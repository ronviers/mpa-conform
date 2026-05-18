"""Per-frame matplotlib RGBA renderer.

First-cut frame content (v1) for a substrate measurement: two-panel
C(tau_window) + chi(tau_window) plot showing the substrate's per-window
observations at this sample-time. Static overlay: framework predicted +
Banach reference traces at fitted (chit_0, gamma_AB_0).

The frame-to-frame change is the substrate's measurement aging across
sample-time. That motion is the substrate's character.
"""
from __future__ import annotations

from typing import Optional

import matplotlib
matplotlib.use("Agg")

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


def render_frame_rgba_u8(
    *,
    width: int,
    height: int,
    dpi: int,
    cell_id: str,
    substrate_class: str,
    sample_time_t: float,
    sample_index: int,
    sample_count: int,
    fitted_chit: float,
    fitted_gamma_AB: float,
    regime_label: str,
    tau_windows: list[float],
    C_per_window: list[Optional[float]],
    chi_per_window: list[Optional[float]],
    pred_C_overlay: Optional[tuple[list[float], list[float]]] = None,
    pred_chi_overlay: Optional[tuple[list[float], list[float]]] = None,
    banach_C_overlay: Optional[tuple[list[float], list[float]]] = None,
    banach_chi_overlay: Optional[tuple[list[float], list[float]]] = None,
) -> np.ndarray:
    """Render one frame; return RGBA uint8 of shape (H, W, 4) in sRGB."""
    fig = Figure(figsize=(width / dpi, height / dpi), dpi=dpi, facecolor="white")
    ax_C = fig.add_subplot(2, 1, 1)
    ax_chi = fig.add_subplot(2, 1, 2)

    valid_C = [(tw, c) for tw, c in zip(tau_windows, C_per_window) if c is not None]
    if valid_C:
        tw_v, c_v = zip(*valid_C)
        ax_C.plot(tw_v, c_v, "o", color="black", markersize=5,
                  label=f"empirical @ t={sample_time_t:.0f}")
    if pred_C_overlay is not None:
        ax_C.plot(pred_C_overlay[0], pred_C_overlay[1], color="C0", linewidth=1.3,
                  alpha=0.55, label="predicted")
    if banach_C_overlay is not None:
        ax_C.plot(banach_C_overlay[0], banach_C_overlay[1], color="C3",
                  linewidth=1.3, linestyle="--", alpha=0.55, label="banach")
    ax_C.set_xscale("log")
    ax_C.set_ylabel("C")
    ax_C.set_ylim(-0.05, 1.05)
    ax_C.legend(loc="upper right", fontsize=8, frameon=False)
    ax_C.grid(True, alpha=0.25)

    valid_chi = [(tw, ch) for tw, ch in zip(tau_windows, chi_per_window) if ch is not None]
    if valid_chi:
        tw_v, ch_v = zip(*valid_chi)
        ax_chi.plot(tw_v, ch_v, "o", color="black", markersize=5,
                    label="empirical")
    if pred_chi_overlay is not None:
        ax_chi.plot(pred_chi_overlay[0], pred_chi_overlay[1], color="C0",
                    linewidth=1.3, alpha=0.55, label="predicted")
    if banach_chi_overlay is not None:
        ax_chi.plot(banach_chi_overlay[0], banach_chi_overlay[1], color="C3",
                    linewidth=1.3, linestyle="--", alpha=0.55, label="banach")
    ax_chi.set_xscale("log")
    ax_chi.set_xlabel("tau_window")
    ax_chi.set_ylabel("chi")
    ax_chi.grid(True, alpha=0.25)

    title = (
        f"{cell_id}  ·  {substrate_class}  ·  "
        f"frame {sample_index + 1}/{sample_count}  t={sample_time_t:.0f}\n"
        f"fit chit={fitted_chit:.3f}, gamma_AB={fitted_gamma_AB:.3f}, regime={regime_label}"
    )
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    buf = np.asarray(canvas.buffer_rgba(), dtype=np.uint8).copy()
    fig.clear()
    return buf
