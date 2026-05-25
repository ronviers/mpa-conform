"""view_header — the self-describing band every block-in view artifact carries.

A view loaded six months from now must explain itself with zero surrounding docs:
what was asked, what the answer was, and — the part that matters most — what the
answerer could NOT ground. That last line is where findings live (pass-1: the
two-sided headroom that one operating point cannot close).

This is a STANDARD, not bespoke: every vertical's view draws the same band, so the
earned/ archive reads uniformly. The plots below the band stay bespoke per substrate.
The authoritative spec for what a result image must contain — and the timestamped
naming that turns earned/ into a browsable library — is **meta-SOP §7**.

Usage (from a bespoke answer script):
    import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[N] ))  # reach blockin/
    from view_header import figure_with_header, timestamped_view_path
    fig, plot_axes = figure_with_header(
        n_plots=3, slug=..., date=STAMP, phase="DEV/blind",
        question=..., minimal_structure=..., verdict=...,
        grounded=[...], not_grounded=[...], placement="zeta=0.32 Q=1.58 ...")
    ax0, ax1, ax2 = plot_axes
    ...
    out, STAMP = timestamped_view_path(HERE)   # earned/<slug>/view_<YYYYMMDD-HHMMSS>.png
    fig.savefig(out, dpi=150)                   # pass the SAME STAMP into date= above
"""
from __future__ import annotations
import textwrap
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

_FONT = 8.5
_LINE_IN = 0.205   # vertical inches per text line at _FONT
_PLOT_H = 4.6      # inches for the bottom plot row


def timestamped_view_path(dirpath, stamp: str | None = None):
    """Return (path, stamp) for a result image — `<dirpath>/view_<YYYYMMDD-HHMMSS>.png`.

    Timestamping the name (not overwriting `view.png`) is what lets re-runs and variants
    accumulate into the results library (meta-SOP §7). Use the returned `stamp` as the
    header's `date=` so the stamp on the image matches its filename."""
    stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(dirpath) / f"view_{stamp}.png", stamp


def figure_with_header(
    *,
    n_plots: int,
    slug: str,
    date: str,
    phase: str,
    question: str,
    minimal_structure: str,
    verdict: str,
    grounded: list[str],
    not_grounded: list[str],
    placement: str,
    plot_w: float = 5.5,
):
    """Return (fig, [plot axes]). Top band = a self-describing header sized to its own
    content (so the provenance lists never overflow into the plots); bottom row =
    n_plots empty axes for the bespoke instrumentation."""
    fig_w = plot_w * n_plots
    wrap_w = max(80, int(fig_w * 9.0))  # chars/inch-ish for monospace at this font

    def wrap(s, width, indent=""):
        body = "\n".join(textwrap.wrap(" ".join(str(s).split()), width=width)) or "(none)"
        return body.replace("\n", "\n" + indent)

    # (text, bold?, color) — build first so we can measure before laying out.
    rows: list[tuple[str, bool, str]] = []
    rows.append((f"{slug}   |   {date}   |   phase: {phase}", True, "#333333"))
    rows.append(("QUESTION (researcher voice):", True, "#1a1a1a"))
    rows.append((wrap(question, wrap_w), False, "#1a1a1a"))
    rows.append(("minimal_structure: " + wrap(minimal_structure, wrap_w - 19, " " * 19), False, "#555555"))
    rows.append(("VERDICT:", True, "#0a5d00"))
    rows.append((wrap(verdict, wrap_w), False, "#0a5d00"))
    rows.append(("placement (framework read): " + placement, False, "#00468b"))
    rows.append(("grounded by:", True, "#00468b"))
    for g in (grounded or ["(none)"]):
        rows.append(("  + " + wrap(g, wrap_w - 4, "    "), False, "#00468b"))
    rows.append(("NOT grounded (the honest limit — read findings here):", True, "#8b0000"))
    for n in (not_grounded or ["(none)"]):
        rows.append(("  - " + wrap(n, wrap_w - 4, "    "), False, "#8b0000"))

    total_lines = sum(t.count("\n") + 1 for t, _, _ in rows) + len(rows) * 0.35  # inter-row gap
    head_h = total_lines * _LINE_IN + 0.3
    fig_h = head_h + _PLOT_H

    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = GridSpec(2, n_plots, height_ratios=[head_h, _PLOT_H],
                  hspace=0.30, wspace=0.28, top=0.985, bottom=0.07, left=0.055, right=0.975)

    head = fig.add_subplot(gs[0, :])
    head.axis("off")
    step = 1.0 / total_lines
    y = 1.0
    for text, bold, color in rows:
        nl = text.count("\n") + 1
        head.text(0.0, y, text, va="top", ha="left", transform=head.transAxes,
                  family="monospace", fontsize=_FONT,
                  fontweight=("bold" if bold else "normal"), color=color)
        y -= step * (nl + 0.35)

    plot_axes = [fig.add_subplot(gs[1, i]) for i in range(n_plots)]
    return fig, plot_axes
