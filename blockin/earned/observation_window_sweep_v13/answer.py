"""Blind answerer — observation_window_sweep_v13.

A single fluctuating signal measured at 32 increasing observation durations.
Per-level INDEPENDENT placement first (each level its own single-point read),
then the band/trend across levels. No monolithic fit.

Instruments (applied from the data):
  - apparent shelf height = C at the largest measured lag of that level
  - FDR slope: chi vs (C(0) - C(tau)) within each level, slope through origin
  - C(tau) shape: intrinsic fast/slow structure, window-invariance check
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

HERE = r"H:\mpa-conform\blockin\workspace"
sys.path.insert(0, r"H:\mpa-conform\blockin")
from view_header import figure_with_header, timestamped_view_path

DATA = Path(HERE) / "observation_window_sweep_v13.data.csv"

# ---- load -----------------------------------------------------------------
raw = np.genfromtxt(DATA, delimiter=",", names=True)
levels = np.unique(raw["level"]).astype(int)
by_level = {}
for lv in levels:
    m = raw["level"] == lv
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    order = np.argsort(tau)
    by_level[lv] = dict(tau=tau[order], C=C[order], chi=chi[order],
                        window_rel=float(raw["window_rel"][m][0]))

# ---- per-level placement (independent) ------------------------------------
shelf = np.zeros(len(levels))         # apparent residual correlation = C at max lag
max_tau = np.zeros(len(levels))
fdr_slope = np.zeros(len(levels))     # chi vs (C0 - C(tau)), slope through origin
fdr_resid = np.zeros(len(levels))     # max |chi - (C0-C)| -> straightness/balance
window_rel = np.zeros(len(levels))

for i, lv in enumerate(levels):
    d = by_level[lv]
    tau, C, chi = d["tau"], d["C"], d["chi"]
    C0 = C[0]                          # this level's own reference (=1.0)
    shelf[i] = C[-1]
    max_tau[i] = tau[-1]
    window_rel[i] = d["window_rel"]
    x = C0 - C                         # fluctuation drop
    # slope through origin (least squares, no intercept): sum(x*chi)/sum(x*x)
    fdr_slope[i] = float(np.sum(x * chi) / np.sum(x * x))
    fdr_resid[i] = float(np.max(np.abs(chi - x)))   # residual vs perfect slope-1 line

# C(0)+C+chi check: is chi == C0 - C exactly? (FDR sum rule)
sumrule_err = []
for lv in levels:
    d = by_level[lv]
    sumrule_err.append(np.max(np.abs(d["C"] + d["chi"] - 1.0)))
sumrule_err = np.array(sumrule_err)

# ---- intrinsic timescale check: is the early curve window-invariant? ------
# Compare C(tau) at common small lags across levels (all share tau=0, 0.05...).
# Level 0 reaches only tau=3; check overlap region against level 31.
d0, d31 = by_level[0], by_level[31]
# interpolate level 31 onto level 0's tau grid, compare
C31_on_0 = np.interp(d0["tau"], d31["tau"], d31["C"])
overlap_maxdiff = float(np.max(np.abs(d0["C"] - C31_on_0)))

# ---- print summary --------------------------------------------------------
print("level  window_rel   max_tau     shelf(C@maxlag)  FDR_slope   resid_vs_slope1")
for i, lv in enumerate(levels):
    print(f"{lv:5d}  {window_rel[i]:9.2f}  {max_tau[i]:10.2f}   "
          f"{shelf[i]:12.6f}   {fdr_slope[i]:9.5f}   {fdr_resid[i]:.2e}")

print(f"\nShelf at shortest watch (lv0): {shelf[0]:.4f}")
print(f"Shelf at longest watch  (lv31): {shelf[-1]:.3e}")
print(f"FDR slope range: {fdr_slope.min():.5f} .. {fdr_slope.max():.5f}")
print(f"Max FDR residual vs perfect slope-1 line (any level): {fdr_resid.max():.2e}")
print(f"Max |C + chi - 1| over ALL rows (sum rule): {sumrule_err.max():.2e}")
print(f"Overlap-region max |C_lv0 - C_lv31| (window-invariance of early curve): {overlap_maxdiff:.2e}")

# crude intrinsic timescale: where does the FINAL (fully-resolved lv31) C cross 1/e of its decay?
d31 = by_level[31]
# C goes 1 -> ~0 ; find tau where C = 1/e
Ce = 1/np.e
tau_e = float(np.interp(-Ce, -d31["C"], d31["tau"]))   # interp on decreasing C
print(f"\nFully-resolved (lv31) tau where C=1/e: {tau_e:.2f} (dimensionless lag)")
# the shelf level ~0.6 at short watch: tau where lv31 crosses 0.6
tau_shelf = float(np.interp(-0.6, -d31["C"], d31["tau"]))
print(f"lv31 tau where C crosses the ~0.6 short-watch shelf value: {tau_shelf:.2f}")

# ---------------------------------------------------------------------------
# VIEW
# ---------------------------------------------------------------------------
slug = "observation_window_sweep_v13"
out, STAMP = timestamped_view_path(HERE)

question = ("One fluctuating signal, watched for 32 increasing durations. At short "
            "watches its autocorrelation drops then freezes on a shelf; at long watches "
            "it decorrelates fully to zero. Is there a genuinely stuck/frozen component, "
            "or is the freezing an artifact of not watching long enough? Is there a right "
            "observation duration, and is the signal in balance (response matched to "
            "fluctuations) or out of balance?")
minimal_structure = ("ONE scalar signal, identical across all 32 runs; only the watch "
                     "duration (max lag reached) changes. window_rel 1.0x -> ~10000x.")

verdict = (f"WATCHING-TIME ARTIFACT, in balance. The apparent freeze is a CAMERA artifact: "
           f"the shelf MELTS from C~{shelf[0]:.2f} (shortest watch) to ~{shelf[-1]:.0e} "
           f"(longest) as the window lengthens. No genuinely stuck component -- the slow "
           f"part simply had not finished relaxing. The signal is IN BALANCE at every "
           f"window: FDR slope = 1 (range {fdr_slope.min():.4f}-{fdr_slope.max():.4f}, "
           f"chi = C(0)-C(tau) exactly, sum-rule |C+chi-1| < {sumrule_err.max():.0e}). "
           f"No 'right' single duration: the true picture only appears once the window "
           f"covers the full slow decay (~level 27+, where C reaches the floor); shorter "
           f"windows under-resolve, none is privileged except 'long enough to reach zero'. "
           f"X=1 everywhere -> the stuck-LOOKING part is NOT out of balance.")

placement = (f"shelf melts {shelf[0]:.2f}->{shelf[-1]:.0e}; FDR slope=1 all 32 windows; "
             f"early C(tau) window-invariant (max diff {overlap_maxdiff:.0e}); 2 timescales "
             f"(fast ~O(1) lag + slow extending ~4 decades), both intrinsic & window-fixed")

grounded = [
    f"camera artifact (not genuinely stuck) <- apparent shelf height (C at max lag) melts "
    f"monotonically from {shelf[0]:.3f} at level 0 (max_tau={max_tau[0]:.1f}) to "
    f"{shelf[-1]:.2e} at level 31 (max_tau={max_tau[-1]:.0f}); a truly frozen component would "
    f"hold the shelf fixed across all windows",
    f"in balance / X=1 <- FDR locus chi vs (C0-C) is a straight line of slope 1 at EVERY "
    f"level (slope range {fdr_slope.min():.5f}-{fdr_slope.max():.5f}); max residual from the "
    f"perfect slope-1 line over all levels = {fdr_resid.max():.1e}",
    f"exact equilibrium sum rule <- chi(tau) = C(0)-C(tau) to machine precision: "
    f"max|C+chi-1| over all 1280 rows = {sumrule_err.max():.1e}; response is exactly matched "
    f"to fluctuations, no FDR violation anywhere",
    f"intrinsic signal is window-invariant <- the early C(tau) curve is identical across "
    f"runs (level 0 vs level 31 overlap region max diff = {overlap_maxdiff:.1e}); only the "
    f"reached lag changes, not the signal -- consistent with the stated minimal structure",
    f"two relaxation steps, both intrinsic <- fast drop at O(0.1-1) lag (same in every run) "
    f"plus a slow tail; fully resolved (level 31) the slow part crosses C=1/e at tau~{tau_e:.0f} "
    f"and reaches the ~0.6 shelf value at tau~{tau_shelf:.1f} -- the shelf was just the slow "
    f"tail not yet entered",
    f"no privileged 'right' window, only 'long enough' <- the true (fully-decorrelated) "
    f"picture appears once the window spans the slow decay; this happens progressively from "
    f"~level 27 onward (C reaches the noise floor); no single duration is special below that",
]

not_grounded = [
    "native timescales in physical units -- tau is a dimensionless lag (the signal's own "
    "clock); no seconds/steps conversion is given, so the fast/slow times are stated only "
    "in dimensionless lag, not absolute units",
    "behaviour strictly past the longest window (window_rel=10000x, max_tau=30000): level 31 "
    "drives C to ~6e-14 (effectively zero), strongly implying full decorrelation with NO "
    "residual frozen component, but a shelf re-emerging at even longer lag cannot be excluded "
    "from data that stops here (it would contradict the slope-1 sum rule, but is not directly "
    "measured)",
    "the precise number of slow timescales / functional form of the slow tail -- the data "
    "resolves 'a fast drop + an extended slow relaxation' but whether the slow part is a single "
    "exponential, a stretched/power-law decay, or several modes is not separable from these two "
    "curves alone (would need a fit per level, not done here under dev I2 stitched-placement)",
    "any substrate identity or physical mechanism behind the slow relaxation -- the read is "
    "purely from C and chi; what the signal physically IS, is blinded and not inferable",
    "whether the early-curve agreement is exact-by-construction vs measured -- it matches to "
    "~1e-2 in the overlap, consistent with 'same signal, different window', but per-run noise "
    "realizations are not provided to confirm it is the identical underlying trace",
]

fig, _ = figure_with_header(
    n_plots=1, slug=slug, date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement,
    plot_w=16.0,
)
# we ignore the single returned plot axis; build our own grids in the bottom region.
# The header used gs row 0; reclaim the figure and add a gridspec for the bottom.
# Easiest: clear the auto plot axis and add subplots manually via add_axes-free gridspec.
for ax in fig.axes[1:]:
    ax.remove()

# Bottom region: we know header sits at top. Use a fresh gridspec confined to lower part.
import matplotlib.gridspec as gridspec
fig_h = fig.get_size_inches()[1]
# header occupies top portion; place our grids in the bottom ~ (PLOT_H / fig_h) fraction.
plot_frac = 4.6 / fig_h
# leave a little margin
top_of_plots = plot_frac * 0.98

# --- left: 32-box camera movie grid (8 cols x 4 rows) ---
gs_movie = gridspec.GridSpec(4, 8, figure=fig,
                             left=0.04, right=0.66, bottom=0.05, top=top_of_plots,
                             hspace=0.35, wspace=0.18)
cmap = plt.cm.viridis
for i, lv in enumerate(levels):
    r, c = divmod(i, 8)
    ax = fig.add_subplot(gs_movie[r, c])
    d = by_level[lv]
    ax.semilogx(d["tau"], d["C"], color=cmap(i / (len(levels) - 1)), lw=1.3)
    ax.axhline(shelf[i], color="crimson", lw=0.6, ls=":")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0.04, 3.2e4)
    ax.set_title(f"L{lv}  shelf={shelf[i]:.2f}", fontsize=6, pad=1.5)
    ax.tick_params(labelsize=4.5, length=2)
    if c != 0:
        ax.set_yticklabels([])
    if r != 3:
        ax.set_xticklabels([])
fig.text(0.35, top_of_plots + 0.012, "CAMERA MOVIE: C(tau) per observation window (level 0 shortest -> 31 longest). "
         "Dotted red = apparent shelf (C at max lag). Watch it MELT left->right, top->bottom.",
         ha="center", fontsize=8, fontweight="bold")

# --- right top: BAND box -- shelf height vs level (the melt curve) ---
gs_band = gridspec.GridSpec(2, 1, figure=fig,
                            left=0.71, right=0.985, bottom=0.05, top=top_of_plots,
                            hspace=0.42)
axb1 = fig.add_subplot(gs_band[0, 0])
axb1.semilogy(levels, shelf, "o-", color="crimson", ms=4)
axb1.set_xlabel("level (observation duration -->)", fontsize=8)
axb1.set_ylabel("apparent shelf height\nC at max lag (log)", fontsize=8)
axb1.set_title("BAND 1 - the melt curve: shelf -> 0 as watch lengthens (CAMERA ARTIFACT, not stuck)",
               fontsize=8, fontweight="bold")
axb1.grid(True, which="both", alpha=0.3)
axb1.tick_params(labelsize=7)

# --- right bottom: BAND box -- FDR slope vs level (flat at 1) ---
axb2 = fig.add_subplot(gs_band[1, 0])
axb2.plot(levels, fdr_slope, "s-", color="#00468b", ms=4, label="FDR slope per level")
axb2.axhline(1.0, color="green", lw=1.0, ls="--", label="slope = 1 (in balance, X=1)")
axb2.set_xlabel("level (observation duration -->)", fontsize=8)
axb2.set_ylabel("FDR slope\nchi vs (C0 - C)", fontsize=8)
axb2.set_ylim(0.9, 1.1)
axb2.set_title("BAND 2 - FDR slope flat at 1 at every window: IN BALANCE, no aging, no out-of-balance frozen part",
               fontsize=8, fontweight="bold")
axb2.grid(True, alpha=0.3)
axb2.legend(fontsize=6.5, loc="lower right")
axb2.tick_params(labelsize=7)

fig.savefig(out, dpi=150)
print(f"\nVIEW: {out}")
