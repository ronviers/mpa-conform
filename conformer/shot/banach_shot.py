"""Fully-connected Banach analytical trajectory as a 3D 3/4-view PNG.

This is the heroic-mode end-to-end pipeline run:
  Taichi -> particle cache (npz) -> EXR -> OIIO -> 3/4 PNG

Subject: BanachSubstrate.state_at(nu) swept across nu, emitting from
each canonical-space point. The trajectory is the framework's analytical
voice -- no real-substrate data, closed-form throughout.

Embedding (canonical -> 3D world):
  world_x = gamma_AB   (cooperative < 0 < competitive; cdv1 sign convention)
  world_y = log10(nu)  (RG-flow depth coordinate)
  world_z = chit       (altitude above bath plane; bath at chit=0)

3/4 camera: elev ~22 deg, azim ~38 deg, looking at trajectory centroid.

Per cdv1, the default Banach trajectory (chit_0=1.5, gamma_AB_0=-0.5)
traces the c -> s migration interior as nu sweeps. Asymptotic-Closure-
compliant: chit -> 0 as nu -> inf but never reaches 0 at any finite nu.
Visually that's a swooping curve toward the bath plane that never lands.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from pathlib import Path
from typing import Optional

import numpy as np

from mpa_scale_solver.banach import BanachSubstrate

from conformer.compute import gfdr_model
from conformer.shot.particle_renderer import channel_to_emitter_params
from conformer.shot.particle_renderer_3d import ParticleField3D
from conformer.shot.exr_io import write_frame
from conformer.shot.png_writer import write_png_from_rgba_linear
from conformer.shot.standards import REGIME_ENCODING


def build_banach_shot(
    *,
    chit_0: float = 1.5,
    gamma_AB_0: float = -0.5,
    nu_range: tuple[float, float] = (0.01, 10.0),
    n_emitters: int = 80,
    width: int = 3840,
    height: int = 2160,
    dt: float = 0.05,
    equilibration_steps: int = 60,
    out_dir: Optional[Path] = None,
) -> dict:
    """One-shot end-to-end Banach 3/4 PNG render.

    Returns dict with artifact paths and basic stats.
    """
    if out_dir is None:
        out_dir = Path(
            "H:/mpa-conform/output/shots/banach/fully_connected"
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. Analytical Banach trajectory (closed form; no observation). ----
    nus = np.logspace(
        np.log10(nu_range[0]), np.log10(nu_range[1]), n_emitters
    )
    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_AB_0)
    states = [banach.state_at(float(nu)) for nu in nus]
    chits = np.array([s.chit for s in states], dtype=np.float32)
    gammas = np.array([s.gamma_AB for s in states], dtype=np.float32)

    # ---- 2. Embed into 3D world space (raw values, no scaling). ----
    world_x = gammas                              # gamma_AB axis
    world_y = np.log10(nus).astype(np.float32)    # log nu axis
    world_z = chits                                # chit (altitude)
    emitter_positions = np.stack([world_x, world_y, world_z], axis=1)

    # ---- 3. Camera (fixed 3/4 view looking at trajectory centroid). ----
    cx = float((world_x.min() + world_x.max()) / 2.0)
    cy = float((world_y.min() + world_y.max()) / 2.0)
    cz = float((world_z.min() + world_z.max()) / 2.0)
    span = float(max(
        world_x.max() - world_x.min(),
        world_y.max() - world_y.min(),
        world_z.max() - world_z.min(),
    ))
    cam_distance = span * 2.2
    elev = np.radians(22.0)
    azim = np.radians(38.0)
    eye = (
        cx + cam_distance * np.cos(elev) * np.cos(azim),
        cy - cam_distance * np.cos(elev) * np.sin(azim),
        cz + cam_distance * np.sin(elev),
    )
    target = (cx, cy, cz)

    print(f"[banach] trajectory span = {span:.3f}, eye = {eye}, target = {target}")

    # ---- 4. Build 3D particle field. ----
    field = ParticleField3D(
        width=width, height=height,
        eye=eye, target=target, up=(0.0, 0.0, 1.0),
        fov_y_deg=35.0, near=0.01, far=cam_distance * 8.0,
        dt=dt,
    )

    # ---- 5. Equilibration loop: emit per channel contract + step. ----
    rng = np.random.default_rng(0)
    # Precompute per-emitter emitter params (constant across steps).
    emitter_params: list[dict] = []
    for state in states:
        regime = gfdr_model.vertex_regime(float(state.chit))
        regime_label_f = REGIME_ENCODING.get(regime, 2.0)
        params = channel_to_emitter_params(
            chit=float(state.chit),
            gamma_AB=float(state.gamma_AB),
            regime_label=regime_label_f,
            in_gamut=1.0,            # Banach is always in gamut
            validation_flags=7.0,    # all 3 validation bits set
        )
        emitter_params.append({
            "params": params,
            "regime": regime,
            "regime_label_f": regime_label_f,
        })

    print(f"[banach] equilibrating: {n_emitters} emitters x "
          f"{equilibration_steps} steps")
    for step_idx in range(equilibration_steps):
        for i, ep in enumerate(emitter_params):
            p = ep["params"]
            color = (p["color_r"], p["color_g"], p["color_b"], p["color_a"])
            field.emit(
                emitter_pos=emitter_positions[i:i + 1],
                rate_per_emitter=p["rate_per_emitter"],
                lifespan_s=p["lifespan_s"],
                mass=p["mass"],
                color=color,
                rng=rng,
            )
        field.step(drag_base=0.5)

    # ---- 6. Render single frame. ----
    field.clear_buf(0.020, 0.020, 0.035, 1.0)  # near-black, faint blue cast
    field.render(base_radius_px=3.0, intensity=0.6)
    rgba_linear = field.snapshot_rgba()

    # ---- 7. Particle cache. ----
    cache_path = out_dir / "particles_cache.npz"
    particles = field.snapshot_particles()
    np.savez_compressed(cache_path, **particles)
    n_particles = int(len(particles["pos"]))
    print(f"[banach] wrote particle cache: {cache_path}  ({n_particles} active)")

    # ---- 8. EXR write (data channels = midpoint canonical state). ----
    # The shot is multi-emitter, so the per-frame data-channel value picks
    # a representative point. The midpoint of the nu sweep is the natural
    # choice; downstream consumers reading the EXR's data layer get a
    # canonical-state fingerprint of where this trajectory passes through.
    mid = n_emitters // 2
    mid_regime = gfdr_model.vertex_regime(float(states[mid].chit))
    data_channels = {
        "chit": float(states[mid].chit),
        "gamma_AB": float(states[mid].gamma_AB),
        "regime_label": REGIME_ENCODING.get(mid_regime, 2.0),
        "in_gamut": 1.0,
        "provenance_hash": 0.0,
        "validation_flags": 7.0,
    }
    exr_path = out_dir / "banach_fully_connected.exr"
    write_frame(
        exr_path,
        rgba_linear=rgba_linear,
        data_channels=data_channels,
        compression="PIZ",
    )
    print(f"[banach] wrote EXR: {exr_path}")

    # ---- 9. PNG via OIIO. ----
    png_path = out_dir / "banach_fully_connected.png"
    png_info = write_png_from_rgba_linear(rgba_linear, png_path)
    print(f"[banach] wrote PNG: {png_path}  ({png_info['backend']})")

    return {
        "particle_cache": str(cache_path),
        "exr": str(exr_path),
        "png": str(png_path),
        "n_particles": n_particles,
        "n_emitters": n_emitters,
        "nu_range": list(nu_range),
        "chit_range": [float(chits.min()), float(chits.max())],
        "gamma_AB_range": [float(gammas.min()), float(gammas.max())],
        "png_backend": png_info["backend"],
    }


if __name__ == "__main__":
    artifacts = build_banach_shot()
    print()
    print("=== artifacts ===")
    for k, v in artifacts.items():
        print(f"  {k}: {v}")
