"""Taichi-based particle renderer for shot frames.

The renderer's discipline is named at the top so violations become
self-evident. See ./RENDERING_DISCIPLINE.md for the canonical contract.

  * Every visual property maps to framework data. No decorative DOF.
  * Differentiation, not decoration: substrates must look distinguishably
    different. The difference IS the framework's diagnostic.
  * No rotation, jitter, billboards, procedural texture, or random walks
    beyond what the framework data itself prescribes.

The Python Taichi simulation here is the executable spec for the
auditor viewport's eventual WebGL implementation. Per the Python-as-
pseudo-spec discipline -- same physics, same look, different runtime.

Channel -> emitter parameter contract (v1):

  regime_label    -> particle color hue (5 distinct hues)
  chit            -> emit rate + particle lifespan
  gamma_AB        -> particle mass (drag / inertia)
  in_gamut        -> emit activation (rate * in_gamut)
  validation_flags -> particle opacity multiplier
  provenance_hash -> NOT a visual property

mpa-solver channels (X_c, X_r, alpha_s, P_s, N_f, beta_mem, Q,
I_pred, C_mu) are deferred until fit_invariants port lands and will
extend the mapping on a per-emitter basis. See RENDERING_DISCIPLINE.md.

NOTE on imports: this module deliberately does NOT use
`from __future__ import annotations` because Taichi 1.7's @ti.kernel
decorator introspects type annotations at class-definition time and
requires them as runtime objects, not PEP-563 strings. Type hints in
this file are real types.
"""
from typing import Optional

import numpy as np
import taichi as ti


# Taichi's @ti.kernel decorators run at class-definition time and need
# the runtime initialized before they resolve type annotations. Guard so
# this only happens once per process. CUDA on the 4080 SUPER is the
# expected backend; fall back to CPU if CUDA isn't available.
if not getattr(ti, "_mpa_conform_initialized", False):
    try:
        ti.init(arch=ti.cuda, log_level=ti.WARN)
    except Exception:
        ti.init(arch=ti.cpu, log_level=ti.WARN)
    ti._mpa_conform_initialized = True


MAX_PARTICLES = 50_000

# Five-bucket regime palette (linear sRGB, scene-referred).
REGIME_PALETTE: dict[float, tuple[float, float, float]] = {
    0.0: (0.18, 0.35, 0.95),   # deep_c       -- cool blue
    1.0: (0.20, 0.78, 0.95),   # c_near_s     -- cyan
    2.0: (0.30, 0.95, 0.50),   # s_critical   -- green
    3.0: (0.98, 0.62, 0.18),   # r_near_s     -- orange
    4.0: (0.95, 0.28, 0.20),   # deep_r       -- red
}


def regime_color(regime_label: float) -> tuple[float, float, float]:
    """Map regime_label (float-encoded enum) to RGB. Nearest-bucket."""
    key = round(float(regime_label))
    key = max(0, min(4, key))
    return REGIME_PALETTE[float(key)]


def channel_to_emitter_params(
    *,
    chit: float,
    gamma_AB: float,
    regime_label: float,
    in_gamut: float,
    validation_flags: float,
) -> dict[str, float]:
    """Consumer binding for EXR Channel Contract v1.

    Producer authority: mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md.
    Discipline (what gets bound and why): ./RENDERING_DISCIPLINE.md.

    When the producer contract bumps version, this function and the
    discipline doc bump in lockstep in the same change.
    """
    abs_chit = abs(chit)
    # Critical (small |chit|) -> high rate, short life.
    # Extreme (large |chit|) -> low rate, long life.
    # Total particle-seconds stays roughly constant across regimes.
    rate = 20.0 * float(in_gamut) / (1.0 + abs_chit)
    lifespan = 0.4 + 1.5 * abs_chit  # seconds at simulation dt
    mass = 1.0 + abs(float(gamma_AB)) * 2.0
    # validation_flags is a 0..7 bitfield (bits 0..2 set)
    bits_set = bin(int(round(float(validation_flags)))).count("1")
    opacity = max(0.0, min(1.0, bits_set / 3.0))
    r, g, b = regime_color(regime_label)
    return {
        "rate_per_emitter": rate,
        "lifespan_s": lifespan,
        "mass": mass,
        "color_r": r, "color_g": g, "color_b": b, "color_a": opacity,
    }


@ti.data_oriented
class ParticleField:
    """Persistent particle system. One instance per shot."""

    def __init__(self, width: int, height: int, dt: float = 0.05):
        self.width = width
        self.height = height
        self.dt = dt

        self.pos = ti.Vector.field(2, dtype=ti.f32, shape=MAX_PARTICLES)
        self.vel = ti.Vector.field(2, dtype=ti.f32, shape=MAX_PARTICLES)
        self.life = ti.field(dtype=ti.f32, shape=MAX_PARTICLES)
        self.max_life = ti.field(dtype=ti.f32, shape=MAX_PARTICLES)
        self.color = ti.Vector.field(4, dtype=ti.f32, shape=MAX_PARTICLES)
        self.mass = ti.field(dtype=ti.f32, shape=MAX_PARTICLES)
        self.active = ti.field(dtype=ti.i32, shape=MAX_PARTICLES)
        # Scalar fields for framebuffer (cleaner atomic_add than Vector
        # field element indexing in Taichi 1.7's LLVM codegen).
        self.buf_r = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_g = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_b = ti.field(dtype=ti.f32, shape=(height, width))
        self.buf_a = ti.field(dtype=ti.f32, shape=(height, width))
        self.next_slot = ti.field(dtype=ti.i32, shape=())

        self.reset()

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
            slot = ti.atomic_add(self.next_slot[None], 1) % MAX_PARTICLES
            self.active[slot] = 1
            self.pos[slot] = ti.Vector([pos_arr[k, 0], pos_arr[k, 1]])
            self.vel[slot] = ti.Vector([vel_arr[k, 0], vel_arr[k, 1]])
            self.life[slot] = life_arr[k]
            self.max_life[slot] = life_arr[k]
            self.color[slot] = ti.Vector(
                [color_arr[k, 0], color_arr[k, 1], color_arr[k, 2], color_arr[k, 3]]
            )
            self.mass[slot] = mass_arr[k]

    def emit(
        self,
        *,
        emitter_pos: np.ndarray,        # (E, 2) image-normalized [0, 1]
        rate_per_emitter: float,        # particles per emitter per frame
        lifespan_s: float,
        mass: float,
        color: tuple[float, float, float, float],
        velocity_scale: float = 0.04,
        rng: np.random.Generator | None = None,
    ) -> None:
        """Spawn particles at each emitter position. Initial velocity is a
        small isotropic spread (substrate emission); not random walk -- the
        spread is what 'observation samples in the neighborhood of the
        measurement' looks like, bounded by the dt of the simulation."""
        if rng is None:
            rng = np.random.default_rng(0)
        n_per = int(round(rate_per_emitter))
        if n_per <= 0 or emitter_pos.shape[0] == 0:
            return
        n_total = n_per * emitter_pos.shape[0]
        pos = np.repeat(emitter_pos, n_per, axis=0).astype(np.float32)
        vel = rng.standard_normal((n_total, 2)).astype(np.float32) * velocity_scale
        life = np.full(n_total, lifespan_s, dtype=np.float32)
        color_arr = np.tile(np.asarray(color, dtype=np.float32), (n_total, 1))
        mass_arr = np.full(n_total, mass, dtype=np.float32)
        self._emit_batch(n_total, pos, vel, life, color_arr, mass_arr)

    @ti.kernel
    def step(self, drag_base: ti.f32, gravity_y: ti.f32):
        """Integrate motion + decay life. Drag scales 1/mass; gravity-y
        pulls particles downward (image-y) at the framework-substrate
        rate, not as an arbitrary force."""
        for i in self.active:
            if self.active[i] == 1:
                self.life[i] -= self.dt
                if self.life[i] <= 0.0:
                    self.active[i] = 0
                else:
                    inv_mass = 1.0 / (self.mass[i] + 0.1)
                    self.vel[i].y += gravity_y * self.dt
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
    def render_additive(self, splat_radius: ti.i32, intensity: ti.f32):
        """Additive splat. Order-independent; HDR-friendly (no clamp)."""
        for k in range(MAX_PARTICLES):
            if self.active[k] == 1:
                fade = self.life[k] / (self.max_life[k] + 1e-6)
                px = ti.cast(self.pos[k].x * self.width, ti.i32)
                py = ti.cast(self.pos[k].y * self.height, ti.i32)
                a_alpha = self.color[k][3] * fade * intensity
                cr = self.color[k][0]
                cg = self.color[k][1]
                cb = self.color[k][2]
                for dx in range(-splat_radius, splat_radius + 1):
                    for dy in range(-splat_radius, splat_radius + 1):
                        x = px + dx
                        y = py + dy
                        d2 = dx * dx + dy * dy
                        in_bounds_x = (x >= 0) and (x < self.width)
                        in_bounds_y = (y >= 0) and (y < self.height)
                        in_disk = d2 <= splat_radius * splat_radius
                        if in_bounds_x and in_bounds_y and in_disk:
                            r = ti.sqrt(ti.cast(d2, ti.f32))
                            falloff = ti.max(
                                0.0,
                                1.0 - r / (ti.cast(splat_radius, ti.f32) + 1e-6),
                            )
                            contrib = a_alpha * falloff
                            ti.atomic_add(self.buf_r[y, x], cr * contrib)
                            ti.atomic_add(self.buf_g[y, x], cg * contrib)
                            ti.atomic_add(self.buf_b[y, x], cb * contrib)
                            ti.atomic_add(self.buf_a[y, x], contrib)

    @ti.kernel
    def draw_overlay_polyline(
        self,
        n: ti.i32,
        pts: ti.types.ndarray(dtype=ti.f32, ndim=2),
        color_r: ti.f32, color_g: ti.f32, color_b: ti.f32, alpha: ti.f32,
        thickness: ti.i32,
    ):
        """Draw a polyline (predicted / Banach reference) as a faint
        background trace."""
        for s in range(n - 1):
            x0 = ti.cast(pts[s, 0] * self.width, ti.i32)
            y0 = ti.cast(pts[s, 1] * self.height, ti.i32)
            x1 = ti.cast(pts[s + 1, 0] * self.width, ti.i32)
            y1 = ti.cast(pts[s + 1, 1] * self.height, ti.i32)
            steps = ti.max(ti.abs(x1 - x0), ti.abs(y1 - y0)) + 1
            for t in range(steps):
                f = ti.cast(t, ti.f32) / ti.cast(steps, ti.f32)
                x = ti.cast(x0 + (x1 - x0) * f, ti.i32)
                y = ti.cast(y0 + (y1 - y0) * f, ti.i32)
                for dx in range(-thickness, thickness + 1):
                    for dy in range(-thickness, thickness + 1):
                        xi = x + dx
                        yi = y + dy
                        in_bx = (xi >= 0) and (xi < self.width)
                        in_by = (yi >= 0) and (yi < self.height)
                        if in_bx and in_by:
                            ti.atomic_add(self.buf_r[yi, xi], color_r * alpha)
                            ti.atomic_add(self.buf_g[yi, xi], color_g * alpha)
                            ti.atomic_add(self.buf_b[yi, xi], color_b * alpha)
                            ti.atomic_add(self.buf_a[yi, xi], alpha)

    def snapshot_rgba(self) -> np.ndarray:
        """Return the current buffer as (H, W, 4) float32 in linear space."""
        r = self.buf_r.to_numpy()
        g = self.buf_g.to_numpy()
        b = self.buf_b.to_numpy()
        a = self.buf_a.to_numpy()
        return np.stack([r, g, b, a], axis=-1)
