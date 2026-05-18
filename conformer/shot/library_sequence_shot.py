"""Real-substrate paired Mode B shot — substrate emitters + cadence-matched Banach.

Two paired EXR sequences:
  output/shots/paired_<substrate>_<xdot>/real/frames/      (real substrate)
  output/shots/paired_<substrate>_<xdot>/banach/frames/    (cadence-matched Banach)

Both share the same nu grid and the same camera path; DJV-scrubbable
side-by-side. Per project_two_shots_scale_managed: data stays canonical,
scale management adjusts the tau_obs camera framing not the data.
Canonical states come from mpa-lens-solver's cdv1-prior TranslationField
(the prism); Banach c-end calibrates to that field's c-end cell.

Mode B per RFC-S §0.2: tau_obs IS the camera. Graphics camera position
at frame t = trajectory_state_at(nu_t) embedded in world space.

First cut: QEC. Iterate from observation per feedback_single_move_design.
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

from mpa_lens_solver import fit_translation_field
from mpa_scale_solver.banach import BanachSubstrate
from mpa_scale_solver.types import CanonicalState

from conformer.compute import gfdr_model
from conformer.shot.encoder import encode_preview_from_exr_sequence
from conformer.shot.exr_io import write_frame
from conformer.shot.particle_renderer import channel_to_emitter_params
from conformer.shot.particle_renderer_3d import ParticleField3D
from conformer.shot.standards import REGIME_ENCODING


LIBRARY_ROOT = Path("H:/mpa-central/library/data")
DEFAULT_OUT_ROOT = Path("H:/mpa-conform/output/shots")


# --- cell loading ------------------------------------------------------

def _load_cells(substrate: str, xdot_kind: str) -> list[dict]:
    """Load all cells of one (substrate, xdot_kind), sorted by control parameter."""
    paths = sorted((LIBRARY_ROOT / substrate).glob(f"*__{xdot_kind}.json"))
    cells = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    if substrate == "quantum":
        cells.sort(key=lambda c: c["operating_point"]["p_base"])
    elif substrate == "glass":
        cells.sort(key=lambda c: c["operating_point"]["T"])
    return cells


# --- world embedding (matches banach_sequence_shot.py) ------------------

def _embed_world(state: CanonicalState, log_nu: float) -> np.ndarray:
    return np.array(
        [float(state.gamma_AB), float(log_nu), float(state.chit)],
        dtype=np.float32,
    )


def _interp_state(states: list[CanonicalState], log_nus: np.ndarray, log_nu: float) -> CanonicalState:
    """Piecewise-linear interpolation of (chit, gamma_AB) across the trajectory."""
    if log_nu <= log_nus[0]:
        return states[0]
    if log_nu >= log_nus[-1]:
        return states[-1]
    for i in range(1, len(log_nus)):
        if log_nus[i] >= log_nu:
            lo, hi = i - 1, i
            f = (log_nu - log_nus[lo]) / max(log_nus[hi] - log_nus[lo], 1e-12)
            return CanonicalState(
                chit=states[lo].chit + f * (states[hi].chit - states[lo].chit),
                gamma_AB=states[lo].gamma_AB + f * (states[hi].gamma_AB - states[lo].gamma_AB),
                k_frust=states[lo].k_frust,
            )
    return states[-1]


# --- one Mode B shot render --------------------------------------------

def _exr_to_png_via_oiio(exr_path: Path, png_path: Path) -> None:
    """Re-uses the same OIIO bridge banach_sequence_shot.py uses."""
    import OpenImageIO as oiio
    src = oiio.ImageBuf(str(exr_path))
    if src.has_error:
        raise RuntimeError(f"OIIO failed to read {exr_path}: {src.geterror()}")
    rgba_buf = oiio.ImageBufAlgo.channels(src, ("R", "G", "B", "A"))
    srgb_buf = oiio.ImageBufAlgo.colorconvert(rgba_buf, "scene_linear", "sRGB")
    if not srgb_buf.write(str(png_path), "uint8"):
        raise RuntimeError(f"OIIO PNG write failed: {srgb_buf.geterror()}")


def _render_one_shot(
    *,
    states: list[CanonicalState],
    log_nus: np.ndarray,
    shot_label: str,
    out_dir: Path,
    width: int,
    height: int,
    n_frames: int,
    fps: int,
    eye_log_nu_offset: float = -0.30,
    target_log_nu_offset: float = +0.30,
    fov_y_deg: float = 50.0,
    dt: float = 0.05,
    equilibration_steps: int = 60,
) -> dict:
    """Render one Mode B shot from an injected (chit, γ_AB) trajectory.

    Mirrors banach_sequence_shot.build_banach_sequence_shot but the
    trajectory is an input, not generated from BanachSubstrate. Same
    world embedding + camera path conventions so paired shots overlay
    cleanly in DJV.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    emitter_positions = np.stack(
        [_embed_world(s, float(log_nu)) for s, log_nu in zip(states, log_nus)],
        axis=0,
    ).astype(np.float32)

    log_nu_min = float(log_nus[0])
    log_nu_max = float(log_nus[-1])
    camera_log_nus = np.linspace(log_nu_min, log_nu_max, n_frames)

    eye_state_0 = _interp_state(states, log_nus, camera_log_nus[0] + eye_log_nu_offset)
    tgt_state_0 = _interp_state(states, log_nus, camera_log_nus[0] + target_log_nu_offset)
    eye_0 = _embed_world(eye_state_0, camera_log_nus[0] + eye_log_nu_offset)
    tgt_0 = _embed_world(tgt_state_0, camera_log_nus[0] + target_log_nu_offset)

    print(f"[{shot_label}] {len(states)} emitters; camera log_nu in "
          f"[{log_nu_min:.3f}, {log_nu_max:.3f}], "
          f"{n_frames} frames @ {fps}fps -> {n_frames / fps:.1f}s")

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

    print(f"[{shot_label}] equilibrating ({equilibration_steps} steps)")
    for _ in range(equilibration_steps):
        emit_all()
        field.step(drag_base=0.5)

    print(f"[{shot_label}] rendering {n_frames} frames @ {width}x{height}")
    for frame_idx in range(n_frames):
        cam_log_nu = float(camera_log_nus[frame_idx])
        eye_state = _interp_state(states, log_nus, cam_log_nu + eye_log_nu_offset)
        tgt_state = _interp_state(states, log_nus, cam_log_nu + target_log_nu_offset)
        eye = _embed_world(eye_state, cam_log_nu + eye_log_nu_offset)
        tgt = _embed_world(tgt_state, cam_log_nu + target_log_nu_offset)
        field.update_camera(eye=tuple(eye), target=tuple(tgt))

        emit_all()
        field.step(drag_base=0.5)

        field.clear_buf(0.020, 0.020, 0.035, 1.0)
        field.render(base_radius_px=3.0, intensity=0.6)
        rgba_linear = field.snapshot_rgba()

        cam_state = _interp_state(states, log_nus, cam_log_nu)
        cam_regime = gfdr_model.vertex_regime(float(cam_state.chit))
        data_channels = {
            "chit": float(cam_state.chit),
            "gamma_AB": float(cam_state.gamma_AB),
            "regime_label": REGIME_ENCODING.get(cam_regime, 2.0),
            "in_gamut": 1.0,
            "provenance_hash": 0.0,
            "validation_flags": 7.0,
        }
        write_frame(
            frames_dir / f"frame_{frame_idx:05d}.exr",
            rgba_linear=rgba_linear,
            data_channels=data_channels,
            compression="PIZ",
        )

        if (frame_idx + 1) % 25 == 0 or frame_idx == n_frames - 1:
            print(f"[{shot_label}]   frame {frame_idx + 1}/{n_frames} "
                  f"(log_nu={cam_log_nu:.3f}, chit={cam_state.chit:+.4f}, "
                  f"regime={cam_regime})")

    preview_path = out_dir / "preview.mp4"
    enc = encode_preview_from_exr_sequence(
        exr_pattern=frames_dir / "frame_%05d.exr",
        out_mp4=preview_path,
        fps=fps,
        codec="libx264",
        crf=18,
        pix_fmt="yuv420p",
    )

    preview_pngs: dict[str, str] = {}
    for label, idx in {"first": 0, "mid": n_frames // 2, "last": n_frames - 1}.items():
        png_path = out_dir / f"preview_{label}.png"
        _exr_to_png_via_oiio(frames_dir / f"frame_{idx:05d}.exr", png_path)
        preview_pngs[label] = str(png_path)
    print(f"[{shot_label}] preview PNGs: {list(preview_pngs.keys())}")

    cache_path = out_dir / "particles_cache_final.npz"
    np.savez_compressed(cache_path, **field.snapshot_particles())

    return {
        "shot_label": shot_label,
        "out_dir": str(out_dir),
        "frames_dir": str(frames_dir),
        "preview_mp4": str(preview_path),
        "preview_pngs": preview_pngs,
        "particle_cache": str(cache_path),
        "n_frames": n_frames,
        "encoder_fallback_path_used": enc.get("fallback", False),
        "trajectory": [
            {"chit": float(s.chit), "gamma_AB": float(s.gamma_AB), "log_nu": float(ln)}
            for s, ln in zip(states, log_nus)
        ],
    }


# --- entry point: paired shot per substrate ---------------------------

_SUBSTRATE_XDOT_DEFAULTS = {
    "quantum": "detection-event",
    "glass": "spin-flip",
}

_SUBSTRATE_SHORTNAME = {
    "quantum": "qec",
    "glass": "glass",
    "brain": "brain",
}


def build_paired_shot(
    *,
    substrate: str = "quantum",
    xdot_kind: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    n_frames: int = 150,
    fps: int = 30,
    log_nu_min: float = -2.0,
    log_nu_max: float = 1.0,
    out_root: Optional[Path] = None,
    max_passes: int = 0,
    tolerance: float = 1e-3,
    n_candidates: int = 32,
) -> dict:
    """Build paired (real-substrate + cadence-matched Banach) Mode B shots.

    Cadence: nu grid spans `log_nu_min..log_nu_max` (Banach Mode B
    default is [-2, 1]). Number of trajectory points = number of cells
    for the chosen (substrate, xdot_kind). Camera flies linearly in
    log_nu over n_frames.
    """
    if xdot_kind is None:
        xdot_kind = _SUBSTRATE_XDOT_DEFAULTS.get(substrate)
        if xdot_kind is None:
            raise ValueError(f"no default xdot_kind for substrate={substrate!r}; pass one explicitly")

    if out_root is None:
        out_root = DEFAULT_OUT_ROOT
    out_root.mkdir(parents=True, exist_ok=True)

    short = _SUBSTRATE_SHORTNAME.get(substrate, substrate)
    shot_root = out_root / f"paired_{short}_{xdot_kind}"
    shot_root.mkdir(parents=True, exist_ok=True)

    # 1. Load cells; lens-solver stamps cdv1-prior canonical states (the prism).
    cells = _load_cells(substrate, xdot_kind)
    if not cells:
        raise SystemExit(f"no {substrate} cells found for xdot_kind={xdot_kind!r}")
    print(f"loaded {len(cells)} {substrate} cells (xdot_kind={xdot_kind})")

    field = fit_translation_field(
        substrate=substrate, cells=cells, xdot_kind=xdot_kind,
        max_passes=max_passes, tolerance=tolerance, n_candidates=n_candidates,
    )
    substrate_states = [
        CanonicalState(
            chit=r.canonical.chit,
            gamma_AB=r.canonical.gamma_AB,
            k_frust=r.canonical.k_frust,
        )
        for r in field.rule
    ]
    print(f"lens-solver: max_passes={max_passes} tolerance={tolerance} n_candidates={n_candidates}")
    for cell, state, rule in zip(cells, substrate_states, field.rule):
        regime = gfdr_model.vertex_regime(float(state.chit))
        passes = rule.canonical.extras.get("passes_used", 0)
        residual = rule.canonical.extras.get("residual")
        prior = rule.canonical.extras.get("prior_chit")
        suffix = ""
        if max_passes > 0:
            suffix = (f"  prior={prior:+.4f}  passes={passes:>3}  "
                      f"residual={residual:.4g}" if prior is not None else "")
        print(f"  {cell['operating_point']['label']:>24}  "
              f"chit={state.chit:+.4f}  gamma_AB={state.gamma_AB:+.4f}  "
              f"regime={regime:>10}{suffix}")

    # 2. Cadence grid (shared by both shots). Use Banach Mode B's log_nu range.
    n_cells = len(cells)
    log_nu_grid = np.linspace(log_nu_min, log_nu_max, n_cells)

    # 4. Cadence-matched Banach: c-end calibrated to the substrate's c-end fit.
    c_end = substrate_states[0]
    banach = BanachSubstrate(chit_0=c_end.chit, gamma_AB_0=c_end.gamma_AB)
    # Banach state_at expects nu, not log_nu. Use nu = 10^log_nu to keep
    # the analytical decay readable across the log_nu range.
    banach_states = [banach.state_at(float(10.0 ** ln)) for ln in log_nu_grid]
    print(f"\nbanach c-end: chit_0={c_end.chit:+.4f}  gamma_AB_0={c_end.gamma_AB:+.4f}")
    print(f"banach at log_nu={log_nu_max}: "
          f"chit={banach_states[-1].chit:+.4f}  "
          f"gamma_AB={banach_states[-1].gamma_AB:+.4f}\n")

    # 5. Render the two shots.
    shot_real = _render_one_shot(
        states=substrate_states,
        log_nus=log_nu_grid,
        shot_label="real_qec",
        out_dir=shot_root / "real",
        width=width, height=height,
        n_frames=n_frames, fps=fps,
    )
    print()
    shot_banach = _render_one_shot(
        states=banach_states,
        log_nus=log_nu_grid,
        shot_label="banach_paired",
        out_dir=shot_root / "banach",
        width=width, height=height,
        n_frames=n_frames, fps=fps,
    )

    # 6. Combined manifest.
    manifest = {
        "shot_mode": "B-paired",
        "shot_mode_doc": (
            "Two paired Mode B EXR sequences per project_two_shots_scale_managed: "
            "real substrate emitters (from mpa-lens-solver cdv1 prior) and "
            "cadence-matched Banach (analytical state_at(nu) at the same log_nu grid, "
            "c-end calibrated to substrate c-end). DJV-scrubbable side-by-side; "
            "visible delta = substrate fingerprint."
        ),
        "substrate": substrate,
        "xdot_kind": xdot_kind,
        "n_cells": n_cells,
        "log_nu_range": [log_nu_min, log_nu_max],
        "n_frames": n_frames,
        "fps": fps,
        "duration_s": n_frames / fps,
        "width": width,
        "height": height,
        "operating_points": [c["operating_point"] for c in cells],
        "canonical_source": "mpa-lens-solver cdv1_prior_v0",
        "translation_field": {
            "direction": field.direction,
            "shape": field.shape,
            "description": field.description,
            "rules": [
                {
                    "label": r.operating_point.label,
                    "gt": r.operating_point.gt,
                    "axes": r.operating_point.axes,
                    "xdot_choice": r.xdot_choice,
                    "chit": r.canonical.chit,
                    "gamma_AB": r.canonical.gamma_AB,
                    "k_frust": r.canonical.k_frust,
                    "method": r.canonical.method,
                }
                for r in field.rule
            ],
        },
        "banach_c_end": {"chit_0": c_end.chit, "gamma_AB_0": c_end.gamma_AB},
        "real_substrate_shot": shot_real,
        "banach_paired_shot": shot_banach,
    }
    manifest_path = shot_root / "paired_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\npaired manifest: {manifest_path}")
    return manifest


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--substrate", choices=["quantum", "glass", "brain"], default="glass")
    ap.add_argument("--xdot", default=None,
                    help="xdot_kind (default per substrate)")
    ap.add_argument("--max-passes", type=int, default=0,
                    help="lens-solver refinement cap per cell (0 = pure cdv1 prior)")
    ap.add_argument("--tolerance", type=float, default=1e-3,
                    help="lens-solver residual tolerance for early-stop")
    ap.add_argument("--n-candidates", type=int, default=32,
                    help="lens-solver K candidates per refinement pass")
    args = ap.parse_args()
    artifacts = build_paired_shot(
        substrate=args.substrate, xdot_kind=args.xdot,
        max_passes=args.max_passes, tolerance=args.tolerance,
        n_candidates=args.n_candidates,
    )
    print()
    print(f"=== paired {artifacts['substrate']} ({artifacts['xdot_kind']}) artifacts ===")
    print(f"  real:   {artifacts['real_substrate_shot']['out_dir']}")
    print(f"  banach: {artifacts['banach_paired_shot']['out_dir']}")
    print(f"  preview PNGs (real):   {list(artifacts['real_substrate_shot']['preview_pngs'].keys())}")
    print(f"  preview PNGs (banach): {list(artifacts['banach_paired_shot']['preview_pngs'].keys())}")
