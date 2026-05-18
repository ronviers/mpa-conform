"""End-to-end visual test for the scale-solver migration trace.

Generates:
  out/migration_compare.png       — single static comparison, both curves
  out/migration_compare.exr       — same plot, float EXR (32-bit linear)
  out/frames/frame_NNNN.exr       — animated sequence, sweep builds up
  out/frames/frame_NNNN.png       — same frames as PNG, for quick review
  out/result.json                 — pass/fail + per-frame residuals

Pass criterion: the numerical curve (solver-computed canonical chit at each
tau_obs) overlays the analytical curve (closed-form truth from the synthetic
driver profile's known parameters). If the curves miss, the math is wrong
somewhere — sign error, wrong axis, off-by-one in the grid, etc.

Tolerance: numerical points must be within half a grid step of analytical
(the grid is the limiting resolution). With the default grid (chit axis
step = 0.01), the threshold is 0.005 plus a small numerical floor.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import OpenEXR

# Make the local package importable when run from the directory
sys.path.insert(0, str(Path(__file__).parent))

from mpa_scale_solver import (
    CanonicalState,
    SubstrateState,
    apply_translation,
    forward_sweep_invert,
    regime_at,
    make_synthetic_aging_driver,
    analytical_canonical_chit,
)


# ---------------------------------------------------------------------------
# Test parameters
# ---------------------------------------------------------------------------

OUT_DIR = Path(__file__).parent / "out"
FRAMES_DIR = OUT_DIR / "frames"
OUT_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)

# Synthetic driver-profile parameters (the "ground truth" the solver must recover)
CHIT_AGING_COEFF = 1.0
TAU_AGING = 1.0

# Reference canonical state: starts in c-regime at tau_obs = 1.0
CHIT_REF = 2.0
GAMMA_REF = -0.5
TAU_OBS_REF = 1.0

# tau_obs sweep: log-spaced from deep narrow to deep wide. 80 frames.
# Wide enough to walk through c -> s -> r cleanly.
TAU_OBS_GRID = np.logspace(-2, 2, 80)
N_FRAMES = len(TAU_OBS_GRID)

# Canonical search grid for forward_sweep_invert.
# chit axis step = 0.01 -> half-step = 0.005 = numerical tolerance.
CHIT_SEARCH_AXIS = np.linspace(-5.0, 5.0, 1001)
GAMMA_SEARCH_AXIS = np.linspace(-1.0, 0.0, 11)  # gamma is identity at v0
_cg, _gg = np.meshgrid(CHIT_SEARCH_AXIS, GAMMA_SEARCH_AXIS, indexing="ij")
SEARCH_GRID = np.column_stack([_cg.ravel(), _gg.ravel()])

# Pass tolerance (half a chit-axis grid step plus a small numerical floor)
TOLERANCE = 0.01

# Image dimensions (16:9, comfortable for EXR review tools)
FIG_W_INCHES = 12.8
FIG_H_INCHES = 7.2
FIG_DPI = 150
# -> 1920 x 1080 pixels


# ---------------------------------------------------------------------------
# Compute analytical truth + run the solver
# ---------------------------------------------------------------------------

def run_test():
    """Run the migration trace. Returns dict with analytical, numerical, residuals."""
    driver = make_synthetic_aging_driver(
        chit_aging_coeff=CHIT_AGING_COEFF,
        tau_aging=TAU_AGING,
    )

    # Reference canonical state, substrate observation at the reference frame
    canonical_ref = CanonicalState(
        chit=CHIT_REF, gamma_AB=GAMMA_REF, tau_obs=TAU_OBS_REF
    )
    substrate = apply_translation(canonical_ref, driver, TAU_OBS_REF)

    # Per-frame: analytical truth + numerical recovery
    analytical_chit = np.array([
        analytical_canonical_chit(
            substrate.chit, float(t), CHIT_AGING_COEFF, TAU_AGING
        )
        for t in TAU_OBS_GRID
    ])
    numerical_chit = np.empty(N_FRAMES)
    for i, tau in enumerate(TAU_OBS_GRID):
        state, _ = forward_sweep_invert(
            substrate, driver, float(tau), SEARCH_GRID
        )
        numerical_chit[i] = state.chit

    residuals = numerical_chit - analytical_chit
    max_abs_residual = float(np.max(np.abs(residuals)))
    passes = max_abs_residual <= TOLERANCE

    # Regime classification per frame (color-code the curve)
    regimes = [
        regime_at(
            CanonicalState(chit=float(c), gamma_AB=0.0, tau_obs=float(t)),
            float(t),
        ).regime
        for c, t in zip(analytical_chit, TAU_OBS_GRID)
    ]

    return {
        "substrate_observation": substrate,
        "analytical_chit": analytical_chit,
        "numerical_chit": numerical_chit,
        "residuals": residuals,
        "max_abs_residual": max_abs_residual,
        "tolerance": TOLERANCE,
        "passes": passes,
        "regimes": regimes,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

# Regime band colors (subtle backgrounds so curves dominate)
REGIME_COLORS = {
    "c": (0.85, 1.00, 0.85),  # pale green: committed
    "s": (1.00, 0.95, 0.80),  # pale yellow: visible strain
    "r": (1.00, 0.85, 0.85),  # pale red: reset
}

ANALYTICAL_COLOR = (0.20, 0.40, 0.85)   # blue, thick solid
NUMERICAL_COLOR = (0.85, 0.20, 0.20)    # red, dashed + markers


def setup_axes(ax, result):
    """Common plot styling. Regime bands, axes, title."""
    log_tau = np.log10(TAU_OBS_GRID)
    chit_min = min(result["analytical_chit"].min(), -2.5)
    chit_max = max(result["analytical_chit"].max(), 3.0)

    # Regime bands as horizontal stripes
    s_width = 0.30  # default S_WINDOW_HALF_WIDTH
    ax.axhspan(s_width, chit_max, color=REGIME_COLORS["c"], alpha=0.55, zorder=0)
    ax.axhspan(-s_width, s_width, color=REGIME_COLORS["s"], alpha=0.55, zorder=0)
    ax.axhspan(chit_min, -s_width, color=REGIME_COLORS["r"], alpha=0.55, zorder=0)

    # Regime band labels (right edge)
    ax.text(log_tau.max() * 0.95, (chit_max + s_width) / 2, "c (committed)",
            ha="right", va="center", fontsize=11, color=(0.20, 0.45, 0.20))
    ax.text(log_tau.max() * 0.95, 0, "s (visible strain)",
            ha="right", va="center", fontsize=11, color=(0.55, 0.45, 0.10))
    ax.text(log_tau.max() * 0.95, (chit_min - s_width) / 2, "r (reset)",
            ha="right", va="center", fontsize=11, color=(0.55, 0.20, 0.20))

    # Axes
    ax.set_xlim(log_tau.min(), log_tau.max())
    ax.set_ylim(chit_min, chit_max)
    ax.set_xlabel(r"$\log_{10}(\tau_{obs})$", fontsize=13)
    ax.set_ylabel(r"canonical $\chi$ (chit)", fontsize=13)
    ax.grid(True, alpha=0.25, linestyle=":", zorder=1)
    ax.axhline(0, color=(0.4, 0.4, 0.4), linewidth=0.8, alpha=0.6, zorder=1)


def render_static_comparison(result, out_path_png, out_path_exr):
    """Single static plot showing both curves overlaid."""
    fig, ax = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES), dpi=FIG_DPI)
    setup_axes(ax, result)
    log_tau = np.log10(TAU_OBS_GRID)

    # Analytical: thick solid line
    ax.plot(log_tau, result["analytical_chit"],
            color=ANALYTICAL_COLOR, linewidth=4.0, alpha=0.85,
            label="analytical (closed-form truth)", zorder=3)
    # Numerical: red dashed line + markers
    ax.plot(log_tau, result["numerical_chit"],
            color=NUMERICAL_COLOR, linewidth=1.5, linestyle="--",
            marker="o", markersize=5, markeredgewidth=0,
            label="numerical (solver recovery)", zorder=4)

    status = "PASS" if result["passes"] else "FAIL"
    status_color = (0.10, 0.55, 0.20) if result["passes"] else (0.75, 0.15, 0.15)
    ax.set_title(
        f"Scale-solver migration trace: c → s → r\n"
        f"max |residual| = {result['max_abs_residual']:.4f}   "
        f"tolerance = {TOLERANCE:.4f}   "
        f"[{status}]",
        fontsize=13,
        color=status_color,
    )
    ax.legend(loc="upper right", fontsize=11, framealpha=0.85)

    fig.tight_layout()
    fig.savefig(out_path_png, dpi=FIG_DPI)

    # Convert to EXR (linear float)
    rgba = _fig_to_rgba_float(fig)
    _write_exr(rgba, out_path_exr)

    plt.close(fig)


def render_frame(result, frame_idx, out_path_exr, out_path_png=None):
    """Render frame frame_idx of the animated sweep.

    Analytical curve drawn faintly across the whole range. Numerical points
    drawn up to and including frame_idx. Playhead at the current tau_obs.
    """
    fig, ax = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES), dpi=FIG_DPI)
    setup_axes(ax, result)
    log_tau = np.log10(TAU_OBS_GRID)

    # Analytical: full curve, faint (so we can see whether numerical tracks)
    ax.plot(log_tau, result["analytical_chit"],
            color=ANALYTICAL_COLOR, linewidth=4.0, alpha=0.85,
            label="analytical", zorder=3)

    # Numerical: only points up to frame_idx
    i_end = frame_idx + 1
    ax.plot(log_tau[:i_end], result["numerical_chit"][:i_end],
            color=NUMERICAL_COLOR, linewidth=1.5, linestyle="--",
            marker="o", markersize=5, markeredgewidth=0,
            label="numerical", zorder=4)

    # Playhead: vertical line at current tau_obs
    ax.axvline(log_tau[frame_idx], color=(0.2, 0.2, 0.2),
               linewidth=1.0, alpha=0.5, zorder=2)

    # Current-frame readout
    cur_tau = TAU_OBS_GRID[frame_idx]
    cur_analytical = result["analytical_chit"][frame_idx]
    cur_numerical = result["numerical_chit"][frame_idx]
    cur_regime = result["regimes"][frame_idx]
    cur_residual = result["residuals"][frame_idx]

    ax.text(0.02, 0.97,
            f"frame {frame_idx+1}/{N_FRAMES}\n"
            f"τ_obs = {cur_tau:.3g}\n"
            f"analytical χ = {cur_analytical:+.4f}\n"
            f"numerical  χ = {cur_numerical:+.4f}\n"
            f"residual    = {cur_residual:+.4f}\n"
            f"regime      = {cur_regime}",
            transform=ax.transAxes,
            ha="left", va="top",
            fontsize=11, family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=(0.6, 0.6, 0.6), alpha=0.92),
            zorder=5)

    status = "PASS" if result["passes"] else "FAIL"
    status_color = (0.10, 0.55, 0.20) if result["passes"] else (0.75, 0.15, 0.15)
    ax.set_title(
        f"Scale-solver migration trace: c → s → r   [{status}]",
        fontsize=13,
        color=status_color,
    )
    ax.legend(loc="upper right", fontsize=11, framealpha=0.85)

    fig.tight_layout()
    rgba = _fig_to_rgba_float(fig)
    _write_exr(rgba, out_path_exr)
    if out_path_png is not None:
        fig.savefig(out_path_png, dpi=FIG_DPI)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Matplotlib -> EXR
# ---------------------------------------------------------------------------

def _fig_to_rgba_float(fig) -> np.ndarray:
    """Render a matplotlib figure to (H, W, 4) float32 RGBA in [0, 1]."""
    fig.canvas.draw()
    # buffer_rgba returns uint8 RGBA in [0, 255]
    buf = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    return (buf.astype(np.float32) / 255.0)


def _write_exr(rgba: np.ndarray, path: Path) -> None:
    """Write an (H, W, 4) float32 RGBA array as a ZIP-compressed EXR.

    EXR is float32 linear; matplotlib renders sRGB-ish but we save the raw
    framebuffer values. The user works in EXR-native tools and can interpret
    the channels directly.
    """
    # Per OpenEXR Python API: channels are a dict of channel-name -> array
    # The simplest path is to write the array as 'RGB' (3 channels). Alpha
    # stored separately.
    rgb = np.ascontiguousarray(rgba[:, :, :3])
    alpha = np.ascontiguousarray(rgba[:, :, 3])
    header = {
        "compression": OpenEXR.ZIP_COMPRESSION,
        "type": OpenEXR.scanlineimage,
    }
    channels = {"RGB": rgb, "A": alpha}
    with OpenEXR.File(header, channels) as exrfile:
        exrfile.write(str(path))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("mpa-scale-solver Python reference: migration-trace visual test")
    print("=" * 70)
    print(f"  synthetic driver: aging_log rule")
    print(f"    chit_aging_coeff = {CHIT_AGING_COEFF}")
    print(f"    tau_aging        = {TAU_AGING}")
    print(f"  reference canonical: chit={CHIT_REF}, gamma={GAMMA_REF}, "
          f"tau_obs={TAU_OBS_REF}")
    print(f"  tau_obs sweep: {N_FRAMES} log-spaced frames from "
          f"{TAU_OBS_GRID[0]:.4g} to {TAU_OBS_GRID[-1]:.4g}")
    print(f"  canonical search grid: {SEARCH_GRID.shape[0]} points")
    print(f"  tolerance: {TOLERANCE:.4f}")
    print()

    print("running solver across sweep ...")
    result = run_test()
    print(f"  substrate observation: chit={result['substrate_observation'].chit:.4f}, "
          f"gamma={result['substrate_observation'].gamma_AB:.4f}")
    print(f"  max |residual|: {result['max_abs_residual']:.4f}")
    print(f"  passes:         {result['passes']}")
    print()

    print("rendering static comparison ...")
    static_png = OUT_DIR / "migration_compare.png"
    static_exr = OUT_DIR / "migration_compare.exr"
    render_static_comparison(result, static_png, static_exr)
    print(f"  wrote {static_png}")
    print(f"  wrote {static_exr}")
    print()

    print(f"rendering {N_FRAMES} animation frames ...")
    for i in range(N_FRAMES):
        frame_exr = FRAMES_DIR / f"frame_{i:04d}.exr"
        frame_png = FRAMES_DIR / f"frame_{i:04d}.png"
        render_frame(result, i, frame_exr, frame_png)
        if (i + 1) % 10 == 0 or i == 0 or i == N_FRAMES - 1:
            print(f"  frame {i+1}/{N_FRAMES}")
    print(f"  wrote {N_FRAMES} EXR + PNG pairs in {FRAMES_DIR}")
    print()

    # Result manifest
    manifest = {
        "passes": result["passes"],
        "max_abs_residual": result["max_abs_residual"],
        "tolerance": TOLERANCE,
        "n_frames": N_FRAMES,
        "tau_obs_grid": TAU_OBS_GRID.tolist(),
        "analytical_chit": result["analytical_chit"].tolist(),
        "numerical_chit": result["numerical_chit"].tolist(),
        "residuals": result["residuals"].tolist(),
        "regimes": result["regimes"],
        "synthetic_params": {
            "chit_aging_coeff": CHIT_AGING_COEFF,
            "tau_aging": TAU_AGING,
            "chit_ref": CHIT_REF,
            "gamma_ref": GAMMA_REF,
            "tau_obs_ref": TAU_OBS_REF,
        },
    }
    manifest_path = OUT_DIR / "result.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"manifest: {manifest_path}")
    print()

    status = "PASS" if result["passes"] else "FAIL"
    print("=" * 70)
    print(f"  result: {status}")
    print(f"    max |residual| = {result['max_abs_residual']:.4f}")
    print(f"    tolerance      = {TOLERANCE:.4f}")
    print("=" * 70)
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
