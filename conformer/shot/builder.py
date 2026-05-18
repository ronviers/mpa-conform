"""Build one shot for one bundle: EXR sequence + mp4 preview + manifest.

A shot is one bundle's grinder sample-times rendered as a sequence of
particle-system frames packed into multi-channel EXRs, plus an mp4
preview encoded by ffmpeg from the EXR sequence.

Renderer is **particle** by default (Taichi-based; see
particle_renderer.py and RENDERING_DISCIPLINE.md). The legacy
matplotlib renderer remains available via renderer="matplotlib" for
diagnostic compare workflows; it shows axes and value labels but is
chart-shaped, not shot-shaped.

Per-frame content (v1): per-sample-time per-window (C, chi) observations
read from the raw grind cell (the bundle's aggregated rows can't drive
this -- per-window structure is what carries the substrate's character
over time). Bundle's predicted + Banach reference traces overlaid as
static faint polylines.

Per-frame data channels (v1): chit, gamma_AB, regime_label, in_gamut,
provenance_hash, validation_flags. Constant per bundle in v1; per-frame
inversion is a follow-up move.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import numpy as np

from mpa_scale_solver.banach import BanachSubstrate

from conformer.compute import gfdr_model

from .encoder import encode_preview_from_exr_sequence
from .exr_io import srgb_to_linear, write_frame
from .renderer import render_frame_rgba_u8
from .standards import REGIME_ENCODING, SHOT_STANDARDS, ShotStandards


REPO_ROOT = Path(__file__).resolve().parents[2]
SHOT_OUT_ROOT = REPO_ROOT / "output" / "shots"


def _grind_cell_path_for(bundle: dict, bundle_path: Path) -> Path:
    ref = bundle.get("raw_data_archive_ref") or ""
    if ref.startswith("local://"):
        return Path(ref.removeprefix("local://"))
    sub_class = bundle.get("substrate_class") or ""
    sub_dir = {"ck-glassy": "glass", "surface-code-qec": "quantum",
               "neural-population": "brain"}.get(sub_class, sub_class)
    stem = bundle_path.stem.removesuffix(".bundle")
    return Path(f"H:/mpa-central/library/data/{sub_dir}/{stem}.json")


def _resolve_tau_scale(bundle: dict) -> float:
    obs = bundle.get("observable") or {}
    for entry in obs.get("preprocessing_log") or []:
        if entry.get("operation") == "tau_rescale_for_fit":
            ts = (entry.get("parameters") or {}).get("tau_scale")
            if isinstance(ts, (int, float)) and ts > 0:
                return float(ts)
    rows = obs.get("data") or []
    taus = [float(r["tau"]) for r in rows if "tau" in r]
    return float(np.median(taus)) if taus else 1.0


def build_shot(
    bundle_path: Path,
    *,
    standards: ShotStandards = SHOT_STANDARDS,
    out_dir: Optional[Path] = None,
    renderer: str = "particle",
) -> dict:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_id = bundle.get("bundle_id") or bundle_path.stem
    substrate_class = bundle.get("substrate_class", "unknown")

    fit_prov = bundle.get("fit_provenance") or {}
    fitted = fit_prov.get("fitted_params") or {}
    chit_0 = float(fitted.get("chit", 0.0))
    gamma_0 = float(fitted.get("gamma_AB", 0.0))
    regime_label = gfdr_model.vertex_regime(chit_0)
    audit_delta = fit_prov.get("audit_delta") or {}
    in_gamut = 1.0 if audit_delta.get("in_gamut") else 0.0
    inv_val = fit_prov.get("inversion_validation") or {}
    validation_flags = 0
    if inv_val.get("asymptotic_closure_compliant"):
        validation_flags |= 1 << 0
    if inv_val.get("k_frust_invariant"):
        validation_flags |= 1 << 1
    if inv_val.get("round_trip_residual") is not None:
        validation_flags |= 1 << 2
    provenance_hash = 0.0  # placeholder until per-frame scale-solver call lands

    grind_path = _grind_cell_path_for(bundle, bundle_path)
    if not grind_path.exists():
        raise FileNotFoundError(
            f"raw grind cell not found at {grind_path}; "
            f"bundle.raw_data_archive_ref={bundle.get('raw_data_archive_ref')!r}"
        )
    grind = json.loads(grind_path.read_text(encoding="utf-8"))
    results = grind.get("results") or {}
    all_samples = results.get("all_samples") or []
    if not all_samples:
        raise ValueError(f"grind cell has no all_samples: {grind_path}")

    schedule = grind.get("schedule") or {}
    tau_windows = sorted(float(t) for t in (schedule.get("tau_windows") or []))
    if not tau_windows:
        raise ValueError("grind cell has no tau_windows in schedule")

    target_frames = int(round(standards.fps * standards.duration_s))
    if len(all_samples) >= target_frames:
        idxs = np.linspace(0, len(all_samples) - 1, target_frames).round().astype(int)
        frames_data = [all_samples[i] for i in idxs]
    else:
        frames_data = all_samples
        target_frames = len(all_samples)

    tau_scale = _resolve_tau_scale(bundle)
    tau_obs_val = (bundle.get("tau_obs") or {}).get("value")
    if tau_obs_val is None:
        bundle_rows = bundle["observable"]["data"]
        tau_obs_val = float(np.median([float(r["tau"]) for r in bundle_rows]))
    nu_obs = float(tau_obs_val) / tau_scale
    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_0)
    banach_state = banach.state_at(nu_obs)

    # Static overlay traces in (tau_window) units. We evaluate the
    # framework's analytical gfdr_model in its native tau range, which
    # matches the tau_window range [1, 1000] for the glass library.
    pred_model = gfdr_model.generate_locus(chit_0)
    pred_C = [gfdr_model._interp_log_tau(pred_model, tw)[0] for tw in tau_windows]
    pred_chi = [gfdr_model._interp_log_tau(pred_model, tw)[1] for tw in tau_windows]
    banach_model = gfdr_model.generate_locus(banach_state.chit)
    banach_C = [gfdr_model._interp_log_tau(banach_model, tw)[0] for tw in tau_windows]
    banach_chi = [gfdr_model._interp_log_tau(banach_model, tw)[1] for tw in tau_windows]

    if out_dir is None:
        out_dir = SHOT_OUT_ROOT / substrate_class / bundle_path.stem
    frames_dir = out_dir / "frames"
    # Clean prior frames so frame count changes don't leave stragglers.
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    data_channels = {
        "chit": chit_0,
        "gamma_AB": gamma_0,
        "regime_label": REGIME_ENCODING.get(regime_label, 2.0),
        "in_gamut": in_gamut,
        "provenance_hash": provenance_hash,
        "validation_flags": float(validation_flags),
    }

    if renderer == "particle":
        _render_frames_particle(
            frames_dir, frames_data, target_frames,
            tau_windows, pred_C, pred_chi, banach_C, banach_chi,
            data_channels, standards,
            bundle_id=bundle_id, substrate_class=substrate_class,
            regime_label_str=regime_label,
        )
    elif renderer == "matplotlib":
        _render_frames_matplotlib(
            frames_dir, frames_data, target_frames,
            tau_windows, pred_C, pred_chi, banach_C, banach_chi,
            data_channels, standards,
            bundle_id=bundle_id, substrate_class=substrate_class,
            regime_label_str=regime_label, chit_0=chit_0, gamma_0=gamma_0,
        )
    else:
        raise ValueError(f"unknown renderer: {renderer!r} (expected 'particle' or 'matplotlib')")

    preview = out_dir / "preview.mp4"
    enc = encode_preview_from_exr_sequence(
        exr_pattern=frames_dir / "frame_%05d.exr",
        out_mp4=preview,
        fps=standards.fps,
        codec=standards.preview_codec,
        crf=standards.preview_crf,
        pix_fmt=standards.preview_pix_fmt,
    )

    manifest = {
        "bundle_id": bundle_id,
        "bundle_path": str(bundle_path),
        "substrate_class": substrate_class,
        "frame_count": target_frames,
        "renderer": renderer,
        "standards": asdict(standards),
        "data_channels_const_in_v1": data_channels,
        "tau_obs_native": float(tau_obs_val),
        "banach_nu_obs": nu_obs,
        "banach_chit_nu": banach_state.chit,
        "encoder_fallback_path_used": enc.get("fallback", False),
    }
    (out_dir / "shot_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


# ---------------------------------------------------------------------------
# Per-frame render helpers (one per renderer mode).
# ---------------------------------------------------------------------------

def _aligned_per_window(sample: dict, tau_windows: list[float]) -> tuple[list[Optional[float]], list[Optional[float]]]:
    """Pair the sample's per_window list with the schedule's tau_windows."""
    per_window = sample.get("per_window") or []
    pw_by_tw = {float(pw.get("tau_window", 0.0)): pw for pw in per_window}
    C_aligned: list[Optional[float]] = []
    chi_aligned: list[Optional[float]] = []
    for tw in tau_windows:
        pw = pw_by_tw.get(float(tw))
        if pw is None:
            C_aligned.append(None)
            chi_aligned.append(None)
            continue
        cdm = pw.get("C_d_mean")
        chim = pw.get("chi_d_mean")
        C_aligned.append(float(cdm) if cdm is not None else None)
        chi_aligned.append(float(chim) if chim is not None else None)
    return C_aligned, chi_aligned


def _normalize_log_tau(tau_windows: list[float], margin: float = 0.05) -> np.ndarray:
    """Map log-tau into [margin, 1 - margin] for image x-axis."""
    arr = np.asarray(tau_windows, dtype=np.float64)
    lo, hi = np.log10(arr.min()), np.log10(arr.max())
    if hi <= lo:
        return np.full_like(arr, 0.5, dtype=np.float32)
    return ((np.log10(arr) - lo) / (hi - lo) * (1 - 2 * margin) + margin).astype(np.float32)


def _render_frames_particle(
    frames_dir: Path,
    frames_data: list[dict],
    target_frames: int,
    tau_windows: list[float],
    pred_C: list[float],
    pred_chi: list[float],
    banach_C: list[float],
    banach_chi: list[float],
    data_channels: dict[str, float],
    standards: ShotStandards,
    *,
    bundle_id: str,
    substrate_class: str,
    regime_label_str: str,
) -> None:
    """Particle renderer path: persistent ParticleField, channel-driven
    emitter params, no decorative DOF."""
    # Importing particle_renderer triggers ti.init under a process-level
    # guard (see particle_renderer.py top).
    from .particle_renderer import (
        ParticleField,
        channel_to_emitter_params,
    )

    field = ParticleField(standards.width, standards.height,
                          dt=1.0 / max(standards.fps, 1))
    rng = np.random.default_rng(12345)

    # Static overlay points (predicted, banach) normalized to image coords.
    tw_x = _normalize_log_tau(tau_windows)
    # Top panel: C, y in [0.05, 0.45]. Bottom panel: chi, y in [0.55, 0.95].
    def _clip01(arr: list[float]) -> np.ndarray:
        return np.clip(np.asarray(arr, dtype=np.float32), 0.0, 1.0)

    pred_C_pts = np.stack([tw_x, 0.05 + (1.0 - _clip01(pred_C)) * 0.40], axis=1)
    pred_chi_pts = np.stack([tw_x, 0.55 + (1.0 - _clip01(pred_chi)) * 0.40], axis=1)
    banach_C_pts = np.stack([tw_x, 0.05 + (1.0 - _clip01(banach_C)) * 0.40], axis=1)
    banach_chi_pts = np.stack([tw_x, 0.55 + (1.0 - _clip01(banach_chi)) * 0.40], axis=1)

    params = channel_to_emitter_params(
        chit=data_channels["chit"],
        gamma_AB=data_channels["gamma_AB"],
        regime_label=data_channels["regime_label"],
        in_gamut=data_channels["in_gamut"],
        validation_flags=data_channels["validation_flags"],
    )

    for frame_idx, sample in enumerate(frames_data):
        C_aligned, chi_aligned = _aligned_per_window(sample, tau_windows)
        # Emitter positions for this frame.
        emit_C_xy = []
        emit_chi_xy = []
        for x_norm, c, ch in zip(tw_x, C_aligned, chi_aligned):
            if c is not None and 0.0 <= c <= 1.5:
                emit_C_xy.append((x_norm, 0.05 + (1.0 - min(max(c, 0.0), 1.0)) * 0.40))
            if ch is not None and 0.0 <= ch <= 1.5:
                emit_chi_xy.append((x_norm, 0.55 + (1.0 - min(max(ch, 0.0), 1.0)) * 0.40))

        color = (params["color_r"], params["color_g"], params["color_b"],
                 params["color_a"])
        if emit_C_xy:
            field.emit(
                emitter_pos=np.asarray(emit_C_xy, dtype=np.float32),
                rate_per_emitter=params["rate_per_emitter"],
                lifespan_s=params["lifespan_s"],
                mass=params["mass"],
                color=color,
                rng=rng,
            )
        if emit_chi_xy:
            field.emit(
                emitter_pos=np.asarray(emit_chi_xy, dtype=np.float32),
                rate_per_emitter=params["rate_per_emitter"],
                lifespan_s=params["lifespan_s"],
                mass=params["mass"],
                color=color,
                rng=rng,
            )
        # Sub-step the simulation for smoother integration.
        for _ in range(4):
            field.step(drag_base=1.0, gravity_y=0.0)

        # Compose this frame. Opaque black background -- alpha=1.0
        # because alpha=0 reads as transparent in downstream image
        # renderers and shows whatever's behind it (often white).

        field.clear_buf(0.0, 0.0, 0.0, 1.0)

        # Faint reference traces (predicted = blue, banach = warm). Alpha
        # values are diagnostic-floor, not decorative.
        field.draw_overlay_polyline(
            pred_C_pts.shape[0], pred_C_pts.astype(np.float32),
            0.30, 0.55, 0.95, 0.30, 1,
        )
        field.draw_overlay_polyline(
            pred_chi_pts.shape[0], pred_chi_pts.astype(np.float32),
            0.30, 0.55, 0.95, 0.30, 1,
        )
        field.draw_overlay_polyline(
            banach_C_pts.shape[0], banach_C_pts.astype(np.float32),
            0.95, 0.45, 0.30, 0.30, 1,
        )
        field.draw_overlay_polyline(
            banach_chi_pts.shape[0], banach_chi_pts.astype(np.float32),
            0.95, 0.45, 0.30, 0.30, 1,
        )

        field.render_additive(splat_radius=4, intensity=1.5)
        rgba_linear = field.snapshot_rgba()

        exr_path = frames_dir / f"frame_{frame_idx:05d}.exr"
        write_frame(
            exr_path,
            rgba_linear=rgba_linear,
            data_channels=data_channels,
            compression=standards.exr_compression,
        )


def _render_frames_matplotlib(
    frames_dir: Path,
    frames_data: list[dict],
    target_frames: int,
    tau_windows: list[float],
    pred_C: list[float],
    pred_chi: list[float],
    banach_C: list[float],
    banach_chi: list[float],
    data_channels: dict[str, float],
    standards: ShotStandards,
    *,
    bundle_id: str,
    substrate_class: str,
    regime_label_str: str,
    chit_0: float,
    gamma_0: float,
) -> None:
    """Legacy matplotlib renderer. Chart-shaped, not shot-shaped --
    kept for diagnostic compare workflows."""
    for frame_idx, sample in enumerate(frames_data):
        C_aligned, chi_aligned = _aligned_per_window(sample, tau_windows)
        rgba_u8 = render_frame_rgba_u8(
            width=standards.width, height=standards.height, dpi=standards.dpi,
            cell_id=bundle_id, substrate_class=substrate_class,
            sample_time_t=float(sample.get("t", 0.0)),
            sample_index=frame_idx, sample_count=target_frames,
            fitted_chit=chit_0, fitted_gamma_AB=gamma_0,
            regime_label=regime_label_str,
            tau_windows=tau_windows,
            C_per_window=C_aligned, chi_per_window=chi_aligned,
            pred_C_overlay=(tau_windows, pred_C),
            pred_chi_overlay=(tau_windows, pred_chi),
            banach_C_overlay=(tau_windows, banach_C),
            banach_chi_overlay=(tau_windows, banach_chi),
        )
        rgba_linear = srgb_to_linear(rgba_u8)
        exr_path = frames_dir / f"frame_{frame_idx:05d}.exr"
        write_frame(
            exr_path,
            rgba_linear=rgba_linear,
            data_channels=data_channels,
            compression=standards.exr_compression,
        )
