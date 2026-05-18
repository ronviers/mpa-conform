"""Mode B: camera-path-as-Banach -- sequenced shot of the Banach trajectory.

Per RFC-S §0.2: tau_obs IS the camera. This module renders that literally:
the graphics camera position at frame t IS BanachSubstrate.state_at(nu_t)
embedded in world space. The viewer travels with the substrate through
canonical space along the RG flow.

Distinguished from Mode A (banach_shot.py single-still) where the graphics
camera is a fixed meta-viewer looking at the laid-out trajectory.

Pipeline:
  Taichi (3D particle field, per-frame camera update) ->
  particle cache (.npz per snapshot) ->
  per-frame EXR ->
  ffmpeg (encoder.encode_preview_from_exr_sequence) -> mp4 ->
  DJV review

Both modes share the SAME world embedding so a Mode B frame and a Mode A
still of the same trajectory are directly compositable in post if needed:
  world_x = gamma_AB        (cooperative < 0 < competitive)
  world_y = log10(nu)       (RG-flow depth)
  world_z = chit            (altitude above bath plane)

Camera path: eye and target are both points on the analytical Banach
trajectory, separated by small log_nu offsets so the framework-camera
position (the substrate's current canonical state at tau_obs) is in the
middle of the graphics camera's view. As frames advance, the graphics
camera flies along the curve from the c-end (chit ~ chit_0) toward the
s-asymptote (chit -> 0).
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
from conformer.shot.png_writer import write_png_from_rgba_linear
from conformer.shot.standards import REGIME_ENCODING


def _embed_world(state, log_nu: float) -> np.ndarray:
    """Embed a (chit, gamma_AB) canonical state at log10(nu) into world."""
    return np.array(
        [float(state.gamma_AB), float(log_nu), float(state.chit)],
        dtype=np.float32,
    )


def _state_world_at_log_nu(banach: BanachSubstrate, log_nu: float) -> np.ndarray:
    """Camera helper: world-space position of the analytical Banach
    canonical state at observer position tau_obs ~ 10^log_nu."""
    nu = float(10.0 ** log_nu)
    s = banach.state_at(nu)
    return _embed_world(s, log_nu)


def _exr_to_png_via_oiio(exr_path: Path, png_path: Path) -> None:
    """Read RGBA from a multi-channel EXR, color-convert to sRGB, write PNG.
    OIIO handles the read + the colorconvert + the 8-bit write."""
    import OpenImageIO as oiio
    src = oiio.ImageBuf(str(exr_path))
    if src.has_error:
        raise RuntimeError(f"OIIO failed to read {exr_path}: {src.geterror()}")
    # The EXR has RGBA + 6 data channels; subset to RGBA for PNG.
    rgba_buf = oiio.ImageBufAlgo.channels(src, ("R", "G", "B", "A"))
    srgb_buf = oiio.ImageBufAlgo.colorconvert(rgba_buf, "scene_linear", "sRGB")
    if not srgb_buf.write(str(png_path), "uint8"):
        raise RuntimeError(f"OIIO PNG write failed: {srgb_buf.geterror()}")


def build_banach_sequence_shot(
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
    equilibration_steps: int = 60,
    eye_log_nu_offset: float = -0.30,
    target_log_nu_offset: float = +0.30,
    fov_y_deg: float = 50.0,
    out_dir: Optional[Path] = None,
) -> dict:
    """Mode B sequenced shot. Graphics camera == tau_obs at each frame.

    eye_log_nu_offset / target_log_nu_offset place the eye slightly behind
    the framework-camera position (on the trajectory) and the look-target
    slightly ahead, so the substrate's current canonical state sits in
    the middle of the view as the camera flies along the curve.
    """
    if out_dir is None:
        out_dir = Path(
            "H:/mpa-conform/output/shots/banach/camera_path_mode_b"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. Analytical trajectory (closed form; no observation needed). ----
    nus = np.logspace(
        np.log10(nu_range[0]), np.log10(nu_range[1]), n_emitters
    )
    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_AB_0)
    states = [banach.state_at(float(nu)) for nu in nus]
    emitter_positions = np.stack(
        [_embed_world(s, np.log10(nu)) for s, nu in zip(states, nus)],
        axis=0,
    ).astype(np.float32)

    # ---- 2. Camera path (linear in log_nu = uniform along RG flow). ----
    log_nu_min = float(np.log10(nu_range[0]))
    log_nu_max = float(np.log10(nu_range[1]))
    camera_log_nus = np.linspace(log_nu_min, log_nu_max, n_frames)

    # Initial eye / target for ParticleField3D construction (frame 0).
    eye_0 = _state_world_at_log_nu(banach, camera_log_nus[0] + eye_log_nu_offset)
    tgt_0 = _state_world_at_log_nu(banach, camera_log_nus[0] + target_log_nu_offset)

    print(f"[mode_b] camera path: log_nu in [{log_nu_min:.2f}, {log_nu_max:.2f}], "
          f"{n_frames} frames at {fps}fps -> {n_frames / fps:.1f}s")

    # ---- 3. Build 3D field with frame-0 camera; equilibrate. ----
    field = ParticleField3D(
        width=width, height=height,
        eye=tuple(eye_0), target=tuple(tgt_0), up=(0.0, 0.0, 1.0),
        fov_y_deg=fov_y_deg, near=0.01, far=20.0,
        dt=dt,
    )

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

    def emit_all() -> None:
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

    print(f"[mode_b] equilibrating ({equilibration_steps} steps before frame 0)")
    for _ in range(equilibration_steps):
        emit_all()
        field.step(drag_base=0.5)

    # ---- 4. Per-frame render loop. ----
    print(f"[mode_b] rendering {n_frames} frames at {width}x{height}")
    for frame_idx in range(n_frames):
        cam_log_nu = float(camera_log_nus[frame_idx])
        eye = _state_world_at_log_nu(banach, cam_log_nu + eye_log_nu_offset)
        tgt = _state_world_at_log_nu(banach, cam_log_nu + target_log_nu_offset)
        field.update_camera(eye=tuple(eye), target=tuple(tgt))

        # Mode B: emitters stay placed in canonical space and keep emitting
        # so the trajectory is "alive" throughout the sequence.
        emit_all()
        field.step(drag_base=0.5)

        # Render this frame.
        field.clear_buf(0.020, 0.020, 0.035, 1.0)
        field.render(base_radius_px=3.0, intensity=0.6)
        rgba_linear = field.snapshot_rgba()

        # Per-frame data channels: framework camera's canonical state.
        cam_nu = float(10.0 ** cam_log_nu)
        cam_state = banach.state_at(cam_nu)
        cam_regime = gfdr_model.vertex_regime(float(cam_state.chit))
        data_channels = {
            "chit": float(cam_state.chit),
            "gamma_AB": float(cam_state.gamma_AB),
            "regime_label": REGIME_ENCODING.get(cam_regime, 2.0),
            "in_gamut": 1.0,
            "provenance_hash": 0.0,
            "validation_flags": 7.0,
        }
        exr_path = frames_dir / f"frame_{frame_idx:05d}.exr"
        write_frame(exr_path, rgba_linear=rgba_linear,
                    data_channels=data_channels, compression="PIZ")

        if (frame_idx + 1) % 25 == 0 or frame_idx == n_frames - 1:
            print(f"[mode_b]   frame {frame_idx + 1}/{n_frames} "
                  f"(cam tau_obs nu={cam_nu:.3g}, chit={cam_state.chit:.4f}, "
                  f"regime={cam_regime})")

    # ---- 5. Encode mp4 via the existing pipeline encoder. ----
    preview_path = out_dir / "preview.mp4"
    enc = encode_preview_from_exr_sequence(
        exr_pattern=frames_dir / "frame_%05d.exr",
        out_mp4=preview_path,
        fps=fps,
        codec="libx264",
        crf=18,
        pix_fmt="yuv420p",
    )
    print(f"[mode_b] mp4: {preview_path}  "
          f"(ffmpeg fallback used: {enc.get('fallback', False)})")

    # ---- 6. Convert first/mid/last frames to PNG via OIIO for preview. ----
    preview_indices = {
        "first": 0,
        "mid": n_frames // 2,
        "last": n_frames - 1,
    }
    preview_pngs: dict[str, str] = {}
    for label, idx in preview_indices.items():
        exr_path = frames_dir / f"frame_{idx:05d}.exr"
        png_path = out_dir / f"preview_{label}.png"
        _exr_to_png_via_oiio(exr_path, png_path)
        preview_pngs[label] = str(png_path)
    print(f"[mode_b] preview PNGs: {list(preview_pngs.keys())}")

    # ---- 7. Particle cache (final frame state). ----
    cache_path = out_dir / "particles_cache_final.npz"
    particles = field.snapshot_particles()
    np.savez_compressed(cache_path, **particles)
    n_particles_final = int(len(particles["pos"]))
    print(f"[mode_b] particle cache (final frame): {cache_path} "
          f"({n_particles_final} active)")

    # ---- 8. Manifest. ----
    manifest = {
        "shot_mode": "B",
        "shot_mode_doc": (
            "Mode B per RENDERING_DISCIPLINE.md: tau_obs as graphics camera. "
            "Graphics camera position at frame t = BanachSubstrate.state_at(nu_t) "
            "embedded in world space. Viewer travels with the substrate."
        ),
        "subject": "BanachSubstrate analytical trajectory",
        "chit_0": chit_0,
        "gamma_AB_0": gamma_AB_0,
        "nu_range": list(nu_range),
        "n_emitters": n_emitters,
        "n_frames": n_frames,
        "fps": fps,
        "duration_s": n_frames / fps,
        "width": width,
        "height": height,
        "fov_y_deg": fov_y_deg,
        "eye_log_nu_offset": eye_log_nu_offset,
        "target_log_nu_offset": target_log_nu_offset,
        "equilibration_steps": equilibration_steps,
        "encoder_fallback_path_used": enc.get("fallback", False),
        "n_particles_final_frame": n_particles_final,
        "preview_pngs": preview_pngs,
    }
    (out_dir / "shot_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return {
        "mode": "B",
        "preview_mp4": str(preview_path),
        "frames_dir": str(frames_dir),
        "preview_pngs": preview_pngs,
        "particle_cache": str(cache_path),
        "n_frames": n_frames,
        "manifest": str(out_dir / "shot_manifest.json"),
    }


if __name__ == "__main__":
    artifacts = build_banach_sequence_shot()
    print()
    print("=== artifacts (Mode B) ===")
    for k, v in artifacts.items():
        print(f"  {k}: {v}")
