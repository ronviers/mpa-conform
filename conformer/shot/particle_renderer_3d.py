"""3D Taichi particle renderer for trajectory-as-subject shots.

Parallel path to ``particle_renderer.py``'s 2D ``ParticleField``. Same
discipline, same channel->emitter contract (`channel_to_emitter_params`
in the 2D file is reusable as-is). The 3D extension is in HOW particles
are positioned in world space and how they project to the framebuffer,
not in WHAT framework data drives their parameters.

  * Positions are 3D world-space coordinates.
  * A fixed perspective camera (lookAt + perspective projection) projects
    each particle to screen space.
  * Splat is additive (order-independent; HDR-friendly; no depth-sort
    bug to fight at million-particle scale).
  * Splat radius attenuates by 1/clip.w (perspective foreshortening; a
    geometric necessity of 3D rendering, NOT decoration -- documented in
    RENDERING_DISCIPLINE.md as a property of the rendering, not the data).

Per ``RENDERING_DISCIPLINE.md``: particles are a visual medium for
upstream-computed framework data, not their own dynamics. The smoke,
not the air.
"""
from typing import Optional

import numpy as np
import taichi as ti


# Single ti.init guard, shared with the 2D path so importing both does
# not double-init the runtime.
if not getattr(ti, "_mpa_conform_initialized", False):
    try:
        ti.init(arch=ti.cuda, log_level=ti.WARN)
    except Exception:
        ti.init(arch=ti.cpu, log_level=ti.WARN)
    ti._mpa_conform_initialized = True


MAX_PARTICLES_3D = 2_000_000


def _look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Right-handed lookAt view matrix."""
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    view = np.eye(4, dtype=np.float32)
    view[0, :3] = s
    view[1, :3] = u
    view[2, :3] = -f
    view[0, 3] = -np.dot(s, eye)
    view[1, 3] = -np.dot(u, eye)
    view[2, 3] = np.dot(f, eye)
    return view


def _perspective(fov_y_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    """Standard right-handed perspective projection matrix."""
    fov_y = np.radians(fov_y_deg)
    f = 1.0 / np.tan(fov_y / 2.0)
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = (far + near) / (near - far)
    proj[2, 3] = (2 * far * near) / (near - far)
    proj[3, 2] = -1.0
    return proj


@ti.data_oriented
class ParticleField3D:
    """3D particle field with fixed perspective camera.

    World coords ``(x, y, z)``; camera at fixed ``eye`` looking at fixed
    ``target`` with world ``up``. Splat is additive in screen space.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        eye: tuple[float, float, float],
        target: tuple[float, float, float],
        up: tuple[float, float, float] = (0.0, 0.0, 1.0),
        fov_y_deg: float = 35.0,
        near: float = 0.05,
        far: float = 100.0,
        dt: float = 0.05,
    ):
        self.width = width
        self.height = height
        self.dt = dt

        # Particle state (3D positions and velocities).
        self.pos = ti.Vector.field(3, dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.vel = ti.Vector.field(3, dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.life = ti.field(dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.max_life = ti.field(dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.color = ti.Vector.field(4, dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.mass = ti.field(dtype=ti.f32, shape=MAX_PARTICLES_3D)
        self.active = ti.field(dtype=ti.i32, shape=MAX_PARTICLES_3D)

        # Framebuffer (linear, HDR; no clamp in the splat).
        self.buf_r = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_g = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_b = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_a = ti.field(dtype=ti.f32, shape=(height, width))

        self.next_slot = ti.field(dtype=ti.i32, shape=())

        # Camera setup (computed on the Python side; MVP passed to kernel
        # as an ndarray each render call -- reliable across Taichi 1.7).
        # The projection matrix is fixed (fov/aspect/near/far constant);
        # the view matrix is per-frame via update_camera() so Mode B
        # camera-path renders can advance eye/target each frame without
        # rebuilding the field.
        eye_np = np.asarray(eye, dtype=np.float32)
        target_np = np.asarray(target, dtype=np.float32)
        up_np = np.asarray(up, dtype=np.float32)
        self._up = up_np
        self._proj = _perspective(fov_y_deg, width / max(height, 1), near, far)
        view = _look_at(eye_np, target_np, up_np)
        self.mvp = (self._proj @ view).astype(np.float32)
        self.eye = eye_np
        self.target = target_np

        self.reset()

    def update_camera(
        self,
        *,
        eye: tuple[float, float, float],
        target: tuple[float, float, float],
        up: Optional[tuple[float, float, float]] = None,
    ) -> None:
        """Update camera eye/target (optionally up); recompute MVP.

        Used by Mode B camera-path-as-Banach renders: at each frame the
        graphics camera position is the substrate's canonical state at
        the current tau_obs. Projection is unchanged (fov/aspect/near/far
        fixed at construction)."""
        eye_np = np.asarray(eye, dtype=np.float32)
        target_np = np.asarray(target, dtype=np.float32)
        up_np = self._up if up is None else np.asarray(up, dtype=np.float32)
        view = _look_at(eye_np, target_np, up_np)
        self.mvp = (self._proj @ view).astype(np.float32)
        self.eye = eye_np
        self.target = target_np
        self._up = up_np

    @ti.kernel
    def reset(self):
        for i in self.active:
            self.active[i] = 0
            self.life[i] = 0.0
        self.next_slot[None] = 0

    @ti.kernel
    def _emit_batch(
        self,
        n: ti.i32,
        pos_arr: ti.types.ndarray(dtype=ti.f32, ndim=2),
        vel_arr: ti.types.ndarray(dtype=ti.f32, ndim=2),
        life_arr: ti.types.ndarray(dtype=ti.f32, ndim=1),
        color_arr: ti.types.ndarray(dtype=ti.f32, ndim=2),
        mass_arr: ti.types.ndarray(dtype=ti.f32, ndim=1),
    ):
        for k in range(n):
            slot = ti.atomic_add(self.next_slot[None], 1) % MAX_PARTICLES_3D
            self.active[slot] = 1
            self.pos[slot] = ti.Vector(
                [pos_arr[k, 0], pos_arr[k, 1], pos_arr[k, 2]]
            )
            self.vel[slot] = ti.Vector(
                [vel_arr[k, 0], vel_arr[k, 1], vel_arr[k, 2]]
            )
            self.life[slot] = life_arr[k]
            self.max_life[slot] = life_arr[k]
            self.color[slot] = ti.Vector(
                [color_arr[k, 0], color_arr[k, 1],
                 color_arr[k, 2], color_arr[k, 3]]
            )
            self.mass[slot] = mass_arr[k]

    def emit(
        self,
        *,
        emitter_pos: np.ndarray,        # (E, 3) world space
        rate_per_emitter: float,
        lifespan_s: float,
        mass: float,
        color: tuple[float, float, float, float],
        velocity_scale: float = 0.015,
        rng: Optional[np.random.Generator] = None,
    ) -> None:
        """Spawn particles at each 3D emitter position. Initial velocity
        is a small isotropic spread (the emission neighborhood; bounded
        by dt). NOT a random walk -- the only motion is what the channel
        contract prescribes."""
        if rng is None:
            rng = np.random.default_rng(0)
        n_per = int(round(rate_per_emitter))
        if n_per <= 0 or emitter_pos.shape[0] == 0:
            return
        n_total = n_per * emitter_pos.shape[0]
        pos = np.repeat(emitter_pos, n_per, axis=0).astype(np.float32)
        vel = (rng.standard_normal((n_total, 3)) * velocity_scale).astype(np.float32)
        life = np.full(n_total, lifespan_s, dtype=np.float32)
        color_arr = np.tile(np.asarray(color, dtype=np.float32), (n_total, 1))
        mass_arr = np.full(n_total, mass, dtype=np.float32)
        self._emit_batch(n_total, pos, vel, life, color_arr, mass_arr)

    @ti.kernel
    def step(self, drag_base: ti.f32):
        """Integrate motion + decay life. No gravity in 3D -- the only
        motion is the emission spread + drag. Drag scales 1/mass per the
        v1 contract."""
        for i in self.active:
            if self.active[i] == 1:
                self.life[i] -= self.dt
                if self.life[i] <= 0.0:
                    self.active[i] = 0
                else:
                    inv_mass = 1.0 / (self.mass[i] + 0.1)
                    drag = drag_base * self.dt * inv_mass
                    self.vel[i] *= ti.max(0.0, 1.0 - drag)
                    self.pos[i] += self.vel[i] * self.dt

    @ti.kernel
    def clear_buf(self, bg_r: ti.f32, bg_g: ti.f32, bg_b: ti.f32, bg_a: ti.f32):
        for i, j in self.buf_r:
            self.buf_r[i, j] = bg_r
            self.buf_g[i, j] = bg_g
            self.buf_b[i, j] = bg_b
            self.buf_a[i, j] = bg_a

    @ti.kernel
    def render_perspective_additive(
        self,
        mvp: ti.types.ndarray(dtype=ti.f32, ndim=2),
        base_radius_px: ti.f32,
        intensity: ti.f32,
        ref_distance: ti.f32,
    ):
        """Project each active particle through MVP, splat additively.

        Splat radius = base_radius_px * (ref_distance / clip.w), so a
        particle at ref_distance from the eye splats at base_radius_px.
        Closer particles splat larger, farther splat smaller -- the
        geometric foreshortening of any perspective camera.
        """
        for k in range(MAX_PARTICLES_3D):
            if self.active[k] == 1:
                wx = self.pos[k].x
                wy = self.pos[k].y
                wz = self.pos[k].z
                # Manual 4x4 * (x, y, z, 1) -- Taichi prefers explicit.
                cx = mvp[0, 0] * wx + mvp[0, 1] * wy + mvp[0, 2] * wz + mvp[0, 3]
                cy = mvp[1, 0] * wx + mvp[1, 1] * wy + mvp[1, 2] * wz + mvp[1, 3]
                cz = mvp[2, 0] * wx + mvp[2, 1] * wy + mvp[2, 2] * wz + mvp[2, 3]
                cw = mvp[3, 0] * wx + mvp[3, 1] * wy + mvp[3, 2] * wz + mvp[3, 3]
                if cw > 1e-6:
                    ndc_x = cx / cw
                    ndc_y = cy / cw
                    ndc_z = cz / cw
                    if ndc_z > -1.0 and ndc_z < 1.0:
                        sx = (ndc_x + 1.0) * 0.5 * self.width
                        sy = (1.0 - ndc_y) * 0.5 * self.height
                        px = ti.cast(sx, ti.i32)
                        py = ti.cast(sy, ti.i32)
                        # Perspective-attenuated splat radius (pixels).
                        radius_f = base_radius_px * (ref_distance / cw)
                        radius_f = ti.min(radius_f, base_radius_px * 8.0)
                        radius = ti.cast(ti.max(1.0, radius_f), ti.i32)
                        fade = self.life[k] / (self.max_life[k] + 1e-6)
                        a_alpha = self.color[k][3] * fade * intensity
                        cr = self.color[k][0]
                        cg = self.color[k][1]
                        cb = self.color[k][2]
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                x = px + dx
                                y = py + dy
                                d2 = dx * dx + dy * dy
                                in_bx = (x >= 0) and (x < self.width)
                                in_by = (y >= 0) and (y < self.height)
                                in_disk = d2 <= radius * radius
                                if in_bx and in_by and in_disk:
                                    r = ti.sqrt(ti.cast(d2, ti.f32))
                                    falloff = ti.max(
                                        0.0,
                                        1.0 - r / (ti.cast(radius, ti.f32) + 1e-6),
                                    )
                                    contrib = a_alpha * falloff
                                    ti.atomic_add(self.buf_r[y, x], cr * contrib)
                                    ti.atomic_add(self.buf_g[y, x], cg * contrib)
                                    ti.atomic_add(self.buf_b[y, x], cb * contrib)
                                    ti.atomic_add(self.buf_a[y, x], contrib)

    def render(self, base_radius_px: float = 2.5, intensity: float = 0.5) -> None:
        """Project + splat with the configured MVP. Reference distance =
        ||eye - target||, the focal distance."""
        ref_distance = float(np.linalg.norm(self.eye - self.target))
        self.render_perspective_additive(
            self.mvp, float(base_radius_px), float(intensity), ref_distance
        )

    def snapshot_rgba(self) -> np.ndarray:
        """Return current framebuffer as (H, W, 4) float32 linear."""
        r = self.buf_r.to_numpy()
        g = self.buf_g.to_numpy()
        b = self.buf_b.to_numpy()
        a = self.buf_a.to_numpy()
        return np.stack([r, g, b, a], axis=-1)

    def snapshot_particles(self) -> dict[str, np.ndarray]:
        """Snapshot active particles for the on-disk particle cache.

        Returns ndarrays of only the active subset. Caller is responsible
        for npz packing.
        """
        pos_np = self.pos.to_numpy()
        vel_np = self.vel.to_numpy()
        life_np = self.life.to_numpy()
        max_life_np = self.max_life.to_numpy()
        color_np = self.color.to_numpy()
        mass_np = self.mass.to_numpy()
        active_np = self.active.to_numpy()
        mask = active_np == 1
        return {
            "pos": pos_np[mask],
            "vel": vel_np[mask],
            "life": life_np[mask],
            "max_life": max_life_np[mask],
            "color": color_np[mask],
            "mass": mass_np[mask],
        }
