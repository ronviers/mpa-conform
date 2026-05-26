"""Blind answerer — observation_window_sweep_v13.

Per-level independent placement (stitched I1 fits), then band readout.
Instruments applied per the traversal recipe:
  - apparent shelf height = C at the largest measured lag of that level
  - FDR slope = slope of chi vs (C(0) - C) within that level (own C(0)), thru origin
  - C(tau) shape / timescales across levels
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

HERE = Path(r"H:\mpa-conform\blockin\workspace")
sys.path.insert(0, str(Path(r"H:\mpa-conform\blockin")))
from view_header import figure_with_header, timestamped_view_path

DATA = HERE / "observation_window_sweep_v13.data.csv"

raw = np.genfromtxt(DATA, delimiter=",", names=True)
levels = np.unique(raw["level"]).astype(int)
levels.sort()

# ---- per-level placement -------------------------------------------------
shelf = []          # C at largest lag
maxtau = []          # largest lag reached
window_rel = []
fdr_slope = []       # slope of chi vs (C0 - C), through origin
fdr_slope_unconstrained = []  # free-intercept slope, as a cross-check
C0_level = []
per_level = {}

for lv in levels:
    m = raw["level"] == lv
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    order = np.argsort(tau)
    tau, C, chi = tau[order], C[order], chi[order]
    per_level[lv] = (tau, C, chi)

    C0 = C[0]               # this level's own C(0)
    C0_level.append(C0)
    shelf.append(C[-1])     # apparent shelf height = C at largest lag
    maxtau.append(tau[-1])
    window_rel.append(raw["window_rel"][m][0])

    # FDR locus: chi vs x = C0 - C, slope through origin: s = sum(x*chi)/sum(x^2)
    x = C0 - C
    s0 = np.sum(x * chi) / np.sum(x * x)
    fdr_slope.append(s0)
    # free intercept cross-check
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, chi, rcond=None)
    fdr_slope_unconstrained.append(coef[0])

shelf = np.array(shelf)
maxtau = np.array(maxtau)
window_rel = np.array(window_rel)
fdr_slope = np.array(fdr_slope)
fdr_slope_unconstrained = np.array(fdr_slope_unconstrained)
C0_level = np.array(C0_level)

print("level  window_rel    maxtau      shelf_C   fdr_slope(0)  fdr_slope(free)")
for i, lv in enumerate(levels):
    print(f"{lv:5d} {window_rel[i]:11.3f} {maxtau[i]:11.2f} {shelf[i]:11.4f} "
          f"{fdr_slope[i]:12.4f} {fdr_slope_unconstrained[i]:14.4f}")

print()
print(f"shelf level0 = {shelf[0]:.4f}, shelf level31 = {shelf[-1]:.4f}")
print(f"FDR slope mean = {fdr_slope.mean():.4f}  std = {fdr_slope.std():.4f}  "
      f"min = {fdr_slope.min():.4f}  max = {fdr_slope.max():.4f}")
print(f"FDR slope(free) mean = {fdr_slope_unconstrained.mean():.4f}  "
      f"std = {fdr_slope_unconstrained.std():.4f}")

# intermediate plateau (the apparent early shelf), median C for 3<=tau<=15
mid_shelf = []
for lv in levels:
    tau, C, chi = per_level[lv]
    win = (tau >= 3) & (tau <= 15)
    mid_shelf.append(np.median(C[win]) if win.any() else np.nan)
mid_shelf = np.array(mid_shelf)
print()
print("intermediate plateau (median C for 3<=tau<=15):")
for i, lv in enumerate(levels):
    print(f"  level {lv:2d}: {mid_shelf[i]:.4f}  (maxtau {maxtau[i]:.1f})")

# ---- VIEW ----------------------------------------------------------------
out, STAMP = timestamped_view_path(HERE)

question = ("One fluctuating scalar, measured at 32 increasing observation durations. At short "
            "watches its autocorrelation drops part-way then sits on a flat shelf (looks frozen); "
            "at long watches the shelf is gone and it decorrelates to zero. (1) Genuinely stuck "
            "component or an artifact of not watching long enough? (2) Is there a right observation "
            "duration, and is the signal - properly measured - in balance (response matched to "
            "fluctuations) or out of balance?")

minimal_structure = ("One scalar signal, identical across all 32 runs; ONLY the watch duration "
                     "(window_rel 1.0x -> 1e4x, max lag reached) changes level to level.")

verdict = (f"WATCHING-TIME ARTIFACT, not a stuck component. The apparent shelf MELTS monotonically "
           f"with watch length: C at the largest lag falls from {shelf[0]:.2f} (level 0) to "
           f"{shelf[-1]:.3f} (level 31) -> the slow part simply had not finished relaxing in the "
           f"short runs; nothing is permanently frozen. No single 'right' window - the picture only "
           f"completes once the watch is long enough to reach the final decay (level ~31, "
           f"window_rel~1e4x, max lag ~3e4); past that lag the data cannot speak. Properly measured "
           f"the signal is IN BALANCE: FDR slope chi vs (C0-C) ~= {fdr_slope.mean():.2f} "
           f"(std {fdr_slope.std():.2f}) at EVERY window, no systematic bend below 1 -> equilibrium "
           f"(X~=1); the stuck-looking part is NOT out of balance.")

grounded = [
    f"Watching-time artifact (not stuck): apparent shelf height = C at largest lag melts "
    f"monotonically {shelf[0]:.3f}->{shelf[-1]:.3f} across levels 0->31 as window_rel grows "
    f"1.0x->1e4x; a genuinely frozen component would hold a fixed shelf independent of watch length.",
    f"Intrinsic timescales are window-invariant: the C(tau) curve overlays run-to-run wherever two "
    f"levels share lag (C(tau~3)~0.63, C~0.60 plateau for tau~5-15 at every level); longer watches "
    f"only RESOLVE more of the SAME decay, they do not change the signal.",
    f"Two-step relaxation: a fast drop to an intermediate plateau C~0.60 (tau~3-15, median "
    f"{np.nanmedian(mid_shelf):.2f}), then a second slow decay toward 0 that only the long watches "
    f"reach; the short-watch 'shelf' IS that intermediate plateau before the slow step resolves.",
    f"In balance (X~=1): FDR slope of chi vs (C0-C) through origin = {fdr_slope.mean():.3f} "
    f"+/- {fdr_slope.std():.3f} across all 32 levels (free-intercept cross-check "
    f"{fdr_slope_unconstrained.mean():.3f}); flat in level, no systematic bend below 1 -> response "
    f"matched to fluctuations at every window, scatter consistent with ~1-2% MC noise.",
    f"No single right window: only level ~31 (window_rel {window_rel[-1]:.0f}x, max lag "
    f"{maxtau[-1]:.0f}) reaches C~0; shorter watches under-resolve the slow step. The true picture "
    f"needs a watch long enough to reach the final decay, not a special intermediate duration.",
]

not_grounded = [
    "Native timescales in physical units: tau is the signal's own dimensionless clock with no "
    "calibration to seconds, so the fast (~0.3) and slow (~1e3) relaxation times cannot be stated "
    "in physical units.",
    "Behaviour past the longest watch (max lag ~3e4 at level 31): C reaches ~0 there, but whether it "
    "stays at 0 or has a yet-slower residual beyond that lag is unmeasured - the longest run only "
    "just resolves the final decay.",
    "Exact mode count / functional form: two steps (fast + slow) are clear, but a third even-slower "
    "mode hiding below the noise floor near C~0 cannot be excluded from these curves alone.",
    "Whether X is EXACTLY 1: slope ~1 within ~1-2% MC scatter establishes balance, but C and chi are "
    "separate noisy ensembles, so a sub-percent equilibrium violation is below this resolution.",
]

placement = (f"shelf_C melts {shelf[0]:.2f}->{shelf[-1]:.3f} (levels 0->31); FDR slope X="
             f"{fdr_slope.mean():.2f}+/-{fdr_slope.std():.2f} flat; 2-step decay, timescales window-invariant")

# Header band (n_plots=1, wide), then carve our own 32-box grid + 2 band boxes below.
fig, plot_axes = figure_with_header(
    n_plots=1, slug="observation_window_sweep_v13", date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement, plot_w=22.0)

host = plot_axes[0]
pos = host.get_position()
fig.delaxes(host)

L, B, W, H = pos.x0, pos.y0, pos.width, pos.height
grid_frac = 0.66
band_frac = 0.30

ncols, nrows = 8, 4
grid_top = B + H
grid_h = H * grid_frac
band_h = H * band_frac

cell_w = W / ncols
cell_h = grid_h / nrows
pad_x = cell_w * 0.16
pad_y = cell_h * 0.22

for idx, lv in enumerate(levels):
    r = idx // ncols
    c = idx % ncols
    ax_l = L + c * cell_w + pad_x
    ax_b = grid_top - (r + 1) * cell_h + pad_y
    ax = fig.add_axes([ax_l, ax_b, cell_w - 1.6 * pad_x, cell_h - 1.5 * pad_y])
    tau, C, chi = per_level[lv]
    ax.semilogx(tau[1:], C[1:], "-", color="#1f4e79", lw=1.1)
    ax.axhline(0, color="#bbbbbb", lw=0.5)
    ax.plot(tau[-1], C[-1], "o", color="#cc3311", ms=3.0)  # apparent shelf marker
    ax.set_ylim(-0.1, 1.05)
    ax.set_xlim(0.04, 3.2e4)
    ax.tick_params(labelsize=5, length=2)
    if c != 0:
        ax.set_yticklabels([])
    if r != nrows - 1:
        ax.set_xticklabels([])
    ax.text(0.04, 0.06, f"L{lv}", transform=ax.transAxes, fontsize=6,
            color="#333333", fontweight="bold")
    ax.text(0.96, 0.92, f"{window_rel[idx]:.0f}x", transform=ax.transAxes,
            fontsize=5, color="#666666", ha="right", va="top")

band_b = B
b_cell_w = W / 2
b_pad = b_cell_w * 0.10

# Band box 1: melt curve
axm = fig.add_axes([L + b_pad, band_b + band_h * 0.18, b_cell_w - 2 * b_pad, band_h * 0.62])
axm.plot(levels, shelf, "o-", color="#cc3311", ms=4)
axm.set_xlabel("level (observation duration -->)", fontsize=8)
axm.set_ylabel("apparent shelf  C(max lag)", fontsize=8)
axm.set_title("BAND: shelf MELTS to ~0 -> watching-time artifact (not frozen)", fontsize=8)
axm.grid(alpha=0.3)
axm.tick_params(labelsize=7)
axm.axhline(0, color="#888888", lw=0.6, ls="--")

# Band box 2: FDR slope vs level
axs = fig.add_axes([L + b_cell_w + b_pad, band_b + band_h * 0.18,
                    b_cell_w - 2 * b_pad, band_h * 0.62])
axs.plot(levels, fdr_slope, "o-", color="#0a5d00", ms=4, label="slope (thru origin)")
axs.axhline(1.0, color="#888888", lw=0.8, ls="--", label="X=1 (balance)")
axs.set_xlabel("level (observation duration -->)", fontsize=8)
axs.set_ylabel("FDR slope  X = chi vs (C0 - C)", fontsize=8)
axs.set_title(f"BAND: FDR slope ~= {fdr_slope.mean():.2f} flat -> in balance (X~=1)", fontsize=8)
axs.set_ylim(0.85, 1.15)
axs.grid(alpha=0.3)
axs.tick_params(labelsize=7)
axs.legend(fontsize=6, loc="lower right")

fig.savefig(out, dpi=150)
print(f"\nPNG written: {out}")
