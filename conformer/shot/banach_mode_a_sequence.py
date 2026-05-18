"""Mode A sequence — Banach trajectory drawn over time, fixed camera.

The Mode A counterpart to ``banach_sequence_shot.py`` (Mode B). Same
subject, same canvas, same fps — different camera mode per
RENDERING_DISCIPLINE.md §"τ_obs and the graphics camera":

  - Mode A (this file): τ_obs is laid out as a world axis. Graphics
    camera is a fixed meta-viewer looking at the trajectory.
    Animation = the trajectory itself drawing over time as the
    activation wavefront sweeps through nu. The viewer watches the
    substrate write its RG-flow history from outside.

  - Mode B (banach_sequence_shot.py): τ_obs IS the graphics camera.
    Graphics camera position at frame t = BanachSubstrate.state_at(nu_t).
    The viewer rides the RG flow from inside.

Activation wavefront: linear in log_nu, the same parameterization Mode B
uses for its camera path. At frame t, all emitters with
log_nu_i <= log_nu_at_frame(t) are active. By the last frame, all 80
emitters are emitting — the steady-state matches the Mode A single-still
PNG (banach_shot.py).

Pipeline: Taichi 3D (fixed camera) → particle cache (.npz final frame)
→ per-frame EXR → ffmpeg → mp4. EXR sequence is the master review path
in DJV; mp4 is convenience preview only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import json
import shutil
from pathlib import Path
from typing import Optional

import numpy as np

from mpa_scale_solver.banach import BanachSubstrate

from conformer.compute import gfdr_model
from conformer.shot.encoder import encode_preview_from_exr_sequence
from conformer.shot.exr_io import write_frame
from conformer.shot.particle_renderer import channel_to_emitter_params
from conformer.shot.particle_renderer_3d import ParticleField3D
from conformer.shot.standards import REGIME_ENCODING


def _embed_world(state, log_nu: float) -> np.ndarray:
    return np.array(
        [float(state.gamma_AB), float(log_nu), float(state.chit)],
        dtype=np.float32,
    )


def _exr_to_png_via_oiio(exr_path: Path, png_path: Path) -> None:
    import OpenImageIO as oiio
    src = oiio.ImageBuf(str(exr_path))
    if src.has_error:
        raise RuntimeError(f"OIIO failed to read {exr_path}: {src.geterror()}")
    rgba_buf = oiio.ImageBufAlgo.channels(src, ("R", "G", "B", "A"))
    srgb_buf = oiio.ImageBufAlgo.colorconvert(rgba_buf, "scene_linear", "sRGB")
    if not srgb_buf.write(str(png_path), "uint8"):
        raise RuntimeError(f"OIIO PNG write failed: {srgb_buf.geterror()}")


def build_banach_mode_a_sequence(
    *,
    chit_0: float = 1.5,
    gamma_AB_0: float = -0.5,
    nu_range: tuple[float, float] = (0.01, 10.0),
    n_emitters: int = 80,
    n_frames: int = 150,
    fps: int = 30,
    width: int = 3840,
    height: int = 2160,
    dt: float = 0.05,
    out_dir: Optional[Path] = None,
) -> dict:
    """Mode A sequenced shot. Fixed graphics camera; trajectory draws
    itself over time as the activation wavefront sweeps through nu.

    No pre-equilibration. Each emitter starts emitting from the frame
    its activation crosses its log_nu, so the trajectory grows AND
    equilibrates simultaneously over the sequence -- the viewer sees
    the substrate writing its own history.
    """
    if out_dir is None:
        out_dir = Path(
            "H:/mpa-conform/output/shots/banach/mode_a_sequence"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. Analytical trajectory (same as Mode A still + Mode B). ----
    nus = np.logspace(
        np.log10(nu_range[0]), np.log10(nu_range[1]), n_emitters
    )
    log_nus = np.log10(nus).astype(np.float32)
    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_AB_0)
    states = [banach.state_at(float(nu)) for nu in nus]
    emitter_positions = np.stack(
        [_embed_world(s, ln) for s, ln in zip(states, log_nus)], axis=0
    ).astype(np.float32)

    # ---- 2. Activation wavefront: linear in log_nu (matches Mode B's
    #         camera parameterization, so the two sequences are
    #         narratively dual). ----
    log_nu_min = float(log_nus.min())
    log_nu_max = float(log_nus.max())
    activation_log_nu_at_frame = np.linspace(log_nu_min, log_nu_max, n_frames)

    # ---- 3. Fixed graphics camera: same as Mode A still (banach_shot.py). ----
    world_x = emitter_positions[:, 0]
    world_y = emitter_positions[:, 1]
    world_z = emitter_positions[:, 2]
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

    print(f"[mode_a_seq] span={span:.3f}, fixed eye={eye}, target={target}")
    print(f"[mode_a_seq] activation log_nu sweep: "
          f"[{log_nu_min:.2f}, {log_nu_max:.2f}] over {n_frames} frames "
          f"({n_frames / fps:.1f}s @ {fps}fps)")

    # ---- 4. Build particle field with the fixed Mode A camera. ----
    field = ParticleField3D(
        width=width, height=height,
        eye=eye, target=target, up=(0.0, 0.0, 1.0),
        fov_y_deg=35.0, near=0.01, far=cam_distance * 8.0,
        dt=dt,
    )

    # Per-emitter params (constant; same channel contract as the still).
    rng = np.random.default_rng(0)
    emitter_params: list[dict] = []
    for state in states:
        regime = gfdr_model.vertex_regime(float(state.chit))
        params = channel_to_emitter_params(
            chit=float(state.chit),
            gamma_AB=float(state.gamma_AB),
            regime_label=REGIME_ENCODING.get(regime, 2.0),
            in_gamut=1.0,
            validation_flags=7.0,
        )
        emitter_params.append({"params": params, "regime": regime})

    # ---- 5. Per-frame render loop. ----
    print(f"[mode_a_seq] rendering {n_frames} frames at {width}x{height}")
    for frame_idx in range(n_frames):
        activation_threshold = float(activation_log_nu_at_frame[frame_idx])
        # Activate every emitter whose log_nu <= threshold.
        active_indices = np.where(log_nus <= activation_threshold)[0]
        n_active = int(len(active_indices))

        # Emit from active emitters only. Each starts emitting from the
        # frame its activation crosses, so growth and equilibration
        # happen together.
        for i in active_indices:
            p = emitter_params[i]["params"]
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

        # Render.
        field.clear_buf(0.020, 0.020, 0.035, 1.0)
        field.render(base_radius_px=3.0, intensity=0.6)
        rgba_linear = field.snapshot_rgba()

        # Per-frame data channels: state at the activation wavefront
        # (the framework camera's effective position in Mode A is "where
        # the trajectory currently ends" -- the leading-edge emitter).
        wavefront_nu = float(10.0 ** activation_threshold)
        wavefront_state = banach.state_at(wavefront_nu)
        wavefront_regime = gfdr_model.vertex_regime(float(wavefront_state.chit))
        data_channels = {
            "chit": float(wavefront_state.chit),
            "gamma_AB": float(wavefront_state.gamma_AB),
            "regime_label": REGIME_ENCODING.get(wavefront_regime, 2.0),
            "in_gamut": 1.0,
            "provenance_hash": 0.0,
            "validation_flags": 7.0,
        }
        exr_path = frames_dir / f"frame_{frame_idx:05d}.exr"
        write_frame(exr_path, rgba_linear=rgba_linear,
                    data_channels=data_channels, compression="PIZ")

        if (frame_idx + 1) % 25 == 0 or frame_idx == n_frames - 1:
            print(f"[mode_a_seq]   frame {frame_idx + 1}/{n_frames} "
                  f"({n_active}/{n_emitters} emitters active, "
                  f"wavefront nu={wavefront_nu:.3g}, "
                  f"chit={wavefront_state.chit:.4f}, "
                  f"regime={wavefront_regime})")

    # ---- 6. Encode mp4. ----
    preview_path = out_dir / "preview.mp4"
    enc = encode_preview_from_exr_sequence(
        exr_pattern=frames_dir / "frame_%05d.exr",
        out_mp4=preview_path,
        fps=fps,
        codec="libx264",
        crf=18,
        pix_fmt="yuv420p",
    )
    print(f"[mode_a_seq] mp4: {preview_path}  "
          f"(ffmpeg fallback used: {enc.get('fallback', False)})")

    # ---- 7. Preview PNGs. ----
    preview_indices = {
        "first": 0,
        "early": n_frames // 4,
        "mid": n_frames // 2,
        "last": n_frames - 1,
    }
    preview_pngs: dict[str, str] = {}
    for label, idx in preview_indices.items():
        exr_path = frames_dir / f"frame_{idx:05d}.exr"
        png_path = out_dir / f"preview_{label}.png"
        _exr_to_png_via_oiio(exr_path, png_path)
        preview_pngs[label] = str(png_path)
    print(f"[mode_a_seq] preview PNGs: {list(preview_pngs.keys())}")

    # ---- 8. Particle cache (final frame -- matches the Mode A still). ----
    cache_path = out_dir / "particles_cache_final.npz"
    particles = field.snapshot_particles()
    np.savez_compressed(cache_path, **particles)
    n_particles_final = int(len(particles["pos"]))
    print(f"[mode_a_seq] final particle cache: {cache_path} "
          f"({n_particles_final} active)")

    # ---- 9. Manifest. ----
    manifest = {
        "shot_mode": "A",
        "shot_mode_doc": (
            "Mode A per RENDERING_DISCIPLINE.md: tau_obs as world axis. "
            "Graphics camera is a fixed meta-viewer; the trajectory "
            "itself draws over time as the activation wavefront sweeps "
            "through nu. The viewer watches the substrate write its "
            "RG-flow history from outside. Dual to Mode B "
            "(camera-path-as-Banach) in banach_sequence_shot.py."
        ),
        "subject": "BanachSubstrate analytical trajectory (growing)",
        "chit_0": chit_0,
        "gamma_AB_0": gamma_AB_0,
        "nu_range": list(nu_range),
        "n_emitters": n_emitters,
        "n_frames": n_frames,
        "fps": fps,
        "duration_s": n_frames / fps,
        "width": width,
        "height": height,
        "activation_parameterization": "linear in log_nu",
        "encoder_fallback_path_used": enc.get("fallback", False),
        "n_particles_final_frame": n_particles_final,
        "preview_pngs": preview_pngs,
    }
    (out_dir / "shot_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return {
        "mode": "A",
        "preview_mp4": str(preview_path),
        "frames_dir": str(frames_dir),
        "preview_pngs": preview_pngs,
        "particle_cache": str(cache_path),
        "n_frames": n_frames,
        "manifest": str(out_dir / "shot_manifest.json"),
    }


if __name__ == "__main__":
    artifacts = build_banach_mode_a_sequence()
    print()
    print("=== artifacts (Mode A sequence) ===")
    for k, v in artifacts.items():
        print(f"  {k}: {v}")
