"""Blind answerer — melt_cooling_sweep_v9.

Sweep: ONE material at FIVE settings (level 0..4, warm->cold), each (tau, C, chi).
Method: each level placed as an INDEPENDENT single-point fit first, then the band
across levels is read. FDR locus = chi vs (1 - C), with C(0)=1 reference.

  - equilibrium: locus is a single straight line, slope ~1 through origin (FDT).
  - aging: locus BENDS -- a steep fast segment (slope ~1) then a shallow slow
    segment of slope X < 1. X is the slow-mode fluctuation-response ratio.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = r"H:\mpa-conform\blockin\workspace"
sys.path.insert(0, r"H:\mpa-conform\blockin")
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

DATA = Path(HERE) / "melt_cooling_sweep_v9.data.csv"

# ---- load ---------------------------------------------------------------
raw = np.genfromtxt(DATA, delimiter=",", names=True)
levels = sorted(set(int(l) for l in raw["level"]))
per = {}
for lv in levels:
    m = raw["level"] == lv
    tau = raw["tau"][m]; C = raw["C"][m]; chi = raw["chi"][m]
    order = np.argsort(tau)
    per[lv] = dict(tau=tau[order], C=C[order], chi=chi[order])

# ---- FDR locus analysis -------------------------------------------------
# x = 1 - C, y = chi. Equilibrium => y = x (slope 1). Aging => two slopes.
# Fast slope: from small-x region (near origin, short tau).
# Slow slope X: from large-x region (long tau, where C is small / plateau drained).
#
# We split the locus at the "knee". Robust, parameter-light approach:
#   - fast slope = local slope over the first portion of the locus (x small).
#   - slow slope X = slope of a line fit through the LAST third of the locus
#     in (1-C, chi) space (the slow-tail draining to small C).
# Also report the *terminal* FDR violation: 1 - (C+chi) at the longest tau,
# which directly measures how far chi falls short of the equilibrium chi=1-C.

def two_segment_fit(x, y):
    """Fit a continuous two-segment (knee) model y = a*x (x<=k) then slope b after.
    Sweep the knee over interior x; pick the split minimizing total residual with
    a forced-through-origin first segment. Returns (fast, slow, knee_x, y_at_knee).

    The slow-segment slope X is reported SEPARATELY by slow_segment_slope() below,
    fit over the genuine slow tail (large 1-C); the two agree on aging levels and
    that direct read is the instrument."""
    n = len(x)
    best = None
    for i in range(3, n - 3):
        x1, y1 = x[:i + 1], y[:i + 1]
        # fast segment forced through origin
        a = np.sum(x1 * y1) / np.sum(x1 * x1)
        r1 = y1 - a * x1
        x2, y2 = x[i:], y[i:]
        # slow segment free line
        b, c = np.polyfit(x2, y2, 1)
        r2 = y2 - (b * x2 + c)
        sse = np.sum(r1 ** 2) + np.sum(r2 ** 2)
        if best is None or sse < best[0]:
            best = (sse, a, b, x[i], a * x[i])
    return best[1], best[2], best[3], best[4]


def slow_segment_slope(x, y, frac=0.6):
    """X = slope of chi vs (1-C) over the slow tail (1-C >= frac*max). This is the
    slow-mode fluctuation-response ratio; X=1 equilibrium, X<1 out of balance."""
    cut = x.max() * frac
    sel = x >= cut
    if sel.sum() < 3:
        sel = np.argsort(x)[-6:]
    return float(np.polyfit(x[sel], y[sel], 1)[0])

results = {}
for lv in levels:
    d = per[lv]
    x = 1.0 - d["C"]          # 1 - C
    y = d["chi"]
    fast, _knee_slow, knee_x, knee_y = two_segment_fit(x, y)
    slow = slow_segment_slope(x, y)   # X, the instrument
    # terminal FDR shortfall at longest tau: equilibrium wants chi = 1 - C.
    term_short = (1.0 - d["C"][-1]) - d["chi"][-1]   # >0 means chi below equilibrium
    # single-slope check (pure equilibrium signature): overall regression chi vs (1-C)
    slope_all = np.polyfit(x, y, 1)[0]
    # plateau height of C: the value C settles toward between fast drop and slow tail.
    # estimate as C at the knee tau (where locus bends) -- i.e. C where x=knee_x.
    C_plateau = 1.0 - knee_x
    # fast-drop fraction (how much of the unit correlation drained before the plateau)
    fast_drop = knee_x
    results[lv] = dict(fast=fast, slow=slow, knee_x=knee_x, knee_y=knee_y,
                       term_short=term_short, slope_all=slope_all,
                       C_plateau=C_plateau, fast_drop=fast_drop,
                       tau_max=d["tau"][-1], C_min=d["C"][-1], chi_max=d["chi"][-1])

print(f"{'lv':>2} {'fast':>6} {'X_slow':>7} {'knee(1-C)':>9} {'C_plat':>7} "
      f"{'term_short':>10} {'slope_all':>9} {'tau_max':>9}")
for lv in levels:
    r = results[lv]
    print(f"{lv:>2} {r['fast']:6.3f} {r['slow']:7.3f} {r['knee_x']:9.3f} "
          f"{r['C_plateau']:7.3f} {r['term_short']:10.4f} {r['slope_all']:9.3f} "
          f"{r['tau_max']:9.1f}")

# ---- VIEW ---------------------------------------------------------------
slug = "melt_cooling_sweep_v9"
out, STAMP = timestamped_view_path(HERE)

Xband = [results[lv]["slow"] for lv in levels]
fast_band = [results[lv]["fast"] for lv in levels]
short_band = [results[lv]["term_short"] for lv in levels]

verdict = (
    "L0 and L1 are ordinary equilibrium liquids -- merely slow: FDR locus is a "
    "single straight line of slope 1, chi+C=1 at every lag, no two-step. From L2 "
    "on the system falls out of thermal balance and ages: a plateau opens in C "
    "and the FDR locus bends to a shallow slow segment of slope X<1. How far out: "
    "L2 mildly aging (X~0.83), L3 clearly aging (X~0.63), L4 strongly aging / "
    "stuck (X~0.50, terminal chi ~0.40 short of equilibrium, slow tail still "
    "draining at the end of the window). The equilibrium->stuck change is "
    "GRADUAL, not abrupt: X slides monotonically 1.00 -> 1.00 -> 0.83 -> 0.63 -> "
    "0.50 across the five settings; the middle temperatures sit genuinely partway "
    "between, with the onset of imbalance localized to the L1->L2 step (~midpoint "
    "X~0.5 reached only at the coldest setting)."
)
grounded = [
    "L0 & L1 equilibrium <- FDR locus a single straight line, slope_all=1.00, "
    "slow-segment X=1.00, chi+C=1.000 at every tau (e.g. L0 tau=15: C=0.0036, "
    "chi=0.9964, sum=1.000; L1 tau=45: sum=1.000); no knee, no plateau.",
    "Aging onset at L2 <- first level with a bent locus: slow-segment slope "
    "X=0.83<1 and terminal shortfall (1-C)-chi=0.094 (L1 shortfall=0.000).",
    "L4 strongly aging <- slow-segment slope X=0.50; terminal shortfall ~0.40 "
    "at tau=2250 (C=0.0095, chi=0.595, sum=0.60 << 1).",
    "Monotone GRADUAL trend <- slow-segment slope X falls 1.00/1.00/0.83/0.63/"
    "0.50 across levels 0-4 (band box); no single level jumps the gap, X reaches "
    "the ~0.5 'half-out' mark only at L4.",
    "Two-step correlation deepens on cooling <- plateau height C_plateau "
    "(=1-knee) climbs 0.05/0.03/0.50/0.65/0.78; cold levels hold a high plateau "
    "then crawl, warm levels decay clean in one step.",
    "Slow timescale lengthens on cooling <- tau_max grows 15/45/150/600/2250 to "
    "follow each level's own slow relaxation (window deliberately matched to "
    "process; cold windows far longer).",
]
not_grounded = [
    "Native temperatures: levels are ordinal warm->cold only; no T values, so "
    "no temperature spacing or fragility/VFT reading.",
    "Whether the cold-level slow tail EVER finishes: L4 tail still decaying at "
    "tau_max (C=0.0095, chi still rising); behaviour past each window is unobserved.",
    "Waiting-time / age dependence: one curve per setting, no t_w sweep, so "
    "aging cannot be confirmed as genuinely non-stationary vs merely two-time-"
    "scale -- X<1 is read as the FDT shortfall, not as explicit t_w drift.",
    "Stretched vs simple-exponential slow tail: not separately fit here; the "
    "two-step shape and X are extracted, the tail's stretching exponent is not "
    "grounded from these columns.",
    "A precise switch temperature: the trend is graded, so any 'crossover "
    "level' is a soft midpoint (X~0.5 near L3), not a sharp transition the data "
    "locates.",
]
placement = (
    "X_slow band [L0..L4] = "
    + ", ".join(f"{x:.2f}" for x in Xband)
    + "  (fast~1; X falls warm->cold; gradual)"
)

fig, axes = figure_with_header(
    n_plots=3, slug=slug, date=STAMP, phase="DEV/blind",
    question=("Per temperature: ordinary-but-slow equilibrium liquid, or genuinely "
              "out of equilibrium/aging -- and how far out? Headline: as it cools "
              "warm->cold, is the equilibrium->stuck change ABRUPT at one setting or "
              "GRADUAL across a range?"),
    minimal_structure=("one material, one scalar fluctuation, five temperatures "
                       "(level 0 warm -> 4 cold); per level autocorrelation C and "
                       "integrated step-response chi vs lag tau."),
    verdict=verdict, grounded=grounded, not_grounded=not_grounded, placement=placement)
ax0, ax1, ax2 = axes

cmap = plt.cm.coolwarm_r
colors = [cmap(i / (len(levels) - 1)) for i in range(len(levels))]

# Box 0: C(tau) per level (log-x), shows the deepening two-step.
for lv, col in zip(levels, colors):
    d = per[lv]
    ax0.semilogx(d["tau"], d["C"], "-o", ms=2.5, color=col, label=f"L{lv}")
ax0.set_xlabel("tau (lag, log)"); ax0.set_ylabel("C(tau)")
ax0.set_title("correlation C(tau): single decay (warm) -> two-step (cold)")
ax0.legend(fontsize=7, loc="upper right"); ax0.grid(alpha=0.25)

# Box 1: FDR locus chi vs (1-C) per level, with equilibrium reference y=x.
ax1.plot([0, 1], [0, 1], "k--", lw=1, label="equilibrium (slope 1)")
for lv, col in zip(levels, colors):
    d = per[lv]
    ax1.plot(1.0 - d["C"], d["chi"], "-o", ms=2.5, color=col, label=f"L{lv}")
ax1.set_xlabel("1 - C"); ax1.set_ylabel("chi")
ax1.set_title("FDR locus: on-line=equilibrium, bend=aging (slow slope X<1)")
ax1.legend(fontsize=7, loc="lower right"); ax1.grid(alpha=0.25)
ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)

# Box 2 (REQUIRED): the BAND -- slow-segment slope X vs level.
ax2.axhline(1.0, color="k", ls="--", lw=1, label="X=1 (equilibrium)")
ax2.plot(levels, Xband, "-o", color="#8b0000", lw=2, ms=7, label="X (slow-mode FDT ratio)")
for lv, x in zip(levels, Xband):
    ax2.annotate(f"{x:.2f}", (lv, x), textcoords="offset points",
                 xytext=(0, 8), ha="center", fontsize=8, color="#8b0000")
ax2.set_xlabel("level (0 warm -> 4 cold)"); ax2.set_ylabel("slow-segment slope X")
ax2.set_title("BAND: X falls smoothly warm->cold => GRADUAL, not abrupt")
ax2.set_xticks(levels); ax2.set_ylim(0, 1.15)
ax2.legend(fontsize=7, loc="lower left"); ax2.grid(alpha=0.25)

fig.savefig(out, dpi=150)
print("\nWROTE:", out)
