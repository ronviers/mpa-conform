"""coupling_ramp_v7 — blind answerer analysis + view.

Reads ONLY the sanitized CSV. Per WORKFLOW §6 sweep rule: place each level as an
INDEPENDENT single-point fit first, then read the band off the placements.

Per-level instrumentation:
  - kernel/window sanity: tau range, dt, whether C settles inside the window.
  - C(tau): autocorrelation shape -> single exponential vs oscillatory? fit C ~ exp(-tau/tauC)
    (and check for any zero-crossing / negative lobe = genuine cycling signature).
  - chi(tau): integrated step-response -> plateau chi_inf (static response).
  - FDR locus: chi vs (C0 - C). Universal readout. Slope / linearity = fluctuation-dissipation.
  - Cxy vs Cyx: directed cross-correlations. Equal => reciprocal (no directed current).
  - phiMean(t): net cumulative turnover angle. Does it ramp (rotation/cycling) or wander ~0?
  - phiVar(t): spread, ~ diffusive growth.

Band: tauC (relaxation time) and chi_inf vs level; rotation-rate vs level; FDR slope vs level.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

HERE = Path(r"H:\mpa-conform\blockin\workspace")
sys.path.insert(0, str(Path(r"H:\mpa-conform\blockin")))
from view_header import figure_with_header, timestamped_view_path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = HERE / "coupling_ramp_v7.data.csv"
raw = np.genfromtxt(CSV, delimiter=",", names=True)

levels = sorted(set(int(l) for l in raw["level"]))
per = {}
for lv in levels:
    m = raw["level"] == lv
    d = {k: raw[k][m] for k in raw.dtype.names}
    # sort by tau just in case
    order = np.argsort(d["tau"])
    for k in d:
        d[k] = d[k][order]
    per[lv] = d


def fit_tauC(tau, C):
    """C is normalized autocorr starting near 1. Fit single exp via log-linear on the
    region where C is well above noise (C in [0.02, 0.97])."""
    C0 = C[0]
    Cn = C / C0
    mask = (Cn > 0.02) & (Cn < 0.98) & (Cn > 0)
    t = tau[mask]
    y = np.log(Cn[mask])
    A = np.vstack([t, np.ones_like(t)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    tauC = -1.0 / slope
    # residual: reconstruct over full above-noise region
    fit = np.exp(intercept + slope * tau)
    res_mask = Cn > 0.01
    rms = np.sqrt(np.mean((Cn[res_mask] - fit[res_mask]) ** 2))
    return tauC, rms, C0


summary = {}
print("=== PER-LEVEL PLACEMENT ===")
for lv in levels:
    d = per[lv]
    tau, C, chi = d["tau"], d["C"], d["chi"]
    Cxy, Cyx = d["Cxy"], d["Cyx"]
    phiM, phiV = d["phiMean"], d["phiVar"]

    tau_min, tau_max, dt = tau.min(), tau.max(), tau[1] - tau[0]
    C_end = C[-1] / C[0]
    settled = C_end < 0.01

    # autocorr: any negative lobe / zero crossing?
    min_C = C.min()
    has_neg_lobe = min_C < -0.02  # genuine oscillation signature

    tauC, rms, C0 = fit_tauC(tau, C)
    chi_inf = chi[-1]

    # FDR locus: chi vs (C0 - C)
    x_fdr = C0 - C
    # slope of chi vs (C0 - C) -- universal FDR. Linear fit through full curve.
    Afd = np.vstack([x_fdr, np.ones_like(x_fdr)]).T
    fdr_slope, fdr_int = np.linalg.lstsq(Afd, chi, rcond=None)[0]
    fdr_fit = Afd @ np.array([fdr_slope, fdr_int])
    fdr_rms = np.sqrt(np.mean((chi - fdr_fit) ** 2))

    # directed asymmetry
    cross_asym = np.max(np.abs(Cxy - Cyx))

    # rotation rate: slope of phiMean vs tau (net cumulative angle ramp).
    Aphi = np.vstack([tau, np.ones_like(tau)]).T
    rot_slope, _ = np.linalg.lstsq(Aphi, phiM, rcond=None)[0]
    phiM_range = phiM.max() - phiM.min()
    # is the net angle a sustained ramp (cycling) or a bounded wander?
    # compare |total drift| to its spread
    phiM_abs_max = np.max(np.abs(phiM))

    # phiVar growth (diffusive)
    phiV_slope, _ = np.linalg.lstsq(Aphi, phiV, rcond=None)[0]

    summary[lv] = dict(tauC=tauC, rms=rms, chi_inf=chi_inf, fdr_slope=fdr_slope,
                       fdr_rms=fdr_rms, cross_asym=cross_asym, rot_slope=rot_slope,
                       phiM_abs_max=phiM_abs_max, has_neg_lobe=has_neg_lobe,
                       min_C=min_C, tau_max=tau_max, settled=settled,
                       Cxy0=Cxy[0], phiV_end=phiV[-1], phiV_slope=phiV_slope)

    print(f"\nLEVEL {lv}: tau in [{tau_min:.3f},{tau_max:.3f}] dt={dt:.4f} settled={settled} (C_end/C0={C_end:.2e})")
    print(f"  autocorr: single-exp tauC={tauC:.3f}  fit_rms={rms:.4f}  min_C={min_C:.4f}  neg_lobe(oscillation)? {has_neg_lobe}")
    print(f"  chi plateau chi_inf={chi_inf:.4f}")
    print(f"  FDR locus chi vs (C0-C): slope={fdr_slope:.4f} rms={fdr_rms:.4f} (linear=> equilibrium FDR)")
    print(f"  directed cross-corr: max|Cxy-Cyx|={cross_asym:.2e}  (0 => reciprocal, no current)")
    print(f"  phiMean: |max|={phiM_abs_max:.4f} ramp_slope={rot_slope:.5f}  (ramp => rotation/cycling)")
    print(f"  phiVar: end={phiV[-1]:.2f} slope={phiV_slope:.3f} (diffusive spread of turnover angle)")

print("\n=== BAND (across control level) ===")
print("level :  tauC     chi_inf   fdr_slope  cross_asym  rot_slope  phiM|max|  neg_lobe")
for lv in levels:
    s = summary[lv]
    print(f"  {lv}   : {s['tauC']:7.3f}  {s['chi_inf']:7.3f}   {s['fdr_slope']:7.4f}   "
          f"{s['cross_asym']:.2e}  {s['rot_slope']:8.5f}  {s['phiM_abs_max']:7.4f}   {s['has_neg_lobe']}")

# ---- VIEW ----
tauCs = [summary[lv]["tauC"] for lv in levels]
chiinf = [summary[lv]["chi_inf"] for lv in levels]
fdrsl = [summary[lv]["fdr_slope"] for lv in levels]
rots = [summary[lv]["rot_slope"] for lv in levels]
crossa = [summary[lv]["cross_asym"] for lv in levels]

question = ("Three mutually-interacting populations in a loop, watched at 5 increasing "
            "interaction strengths (level 0..4). As I crank the knob the swings get bigger and "
            "settle slower. Is each setting still just settling back to balance, or has it begun "
            "to genuinely cycle/oscillate? Am I approaching an edge (how close)? And does cranking "
            "the strength change WHAT KIND of system this is, or is it the same kind all the way up?")
minimal_structure = ("one community, 3 populations in a loop, mutual/matched coupling, noise per "
                     "population; 5 settings of overall interaction strength; per level: C, chi, "
                     "Cxy, Cyx, phiMean, phiVar on the 2D turnover plane; each level its own window.")

verdict = ("Same KIND of system at every setting: monotone relaxation back to balance, no cycling. "
           "Each level's autocorrelation C decays as a clean single exponential with NO negative lobe "
           "(a true cycle would dip below zero) and the net turnover angle phiMean stays a bounded "
           "wander around ~0 (no sustained ramp), so nothing is going around the loop. Cranking the "
           "knob makes it MORE SO, not different: relaxation time tauC and the static response chi_inf "
           "both roughly DOUBLE per step (tauC ~1.3->2.4->5.0->10->20, chi_inf ~1.07->1.5->2.7->5.1->10) "
           "from level 0 to 4 (slower, larger excursions) -- exactly the 'bigger swings, "
           "longer settling' you see -- but the system stays in the settling regime the whole way. "
           "You are here: deep interior, still settling, just slower. No edge is attained in the data; "
           "the trend is monotone with no sign of a finite blow-up or onset of rotation across the 5 "
           "points sampled. The two directed cross-correlations are identical (Cxy=Cyx) confirming the "
           "matched/reciprocal wiring -- no hidden directed current.")

placement = ("per-level single-exp relaxation; tauC ~1.3,2.4,5.0,10,20 (doubles/step), "
             "chi_inf ~1.07,1.52,2.69,5.10,9.98 monotone up with level; FDR chi-vs-(C0-C) linear at "
             "every level (slope ~= chi_inf ~= tauC, equilibrium FDR, 3 readings agree); "
             "Cxy=Cyx exactly (reciprocal, no current); phiMean bounded ~0 (no rotation); no negative C lobe")

grounded = [
    "KIND = settling not cycling, every level: C(tau) decays monotonically to ~0 with no negative lobe (min_C>0 at all 5 levels) -- a genuine cycle would show C dipping below zero (autocorrelation columns C).",
    "No directed current / matched reciprocal coupling: Cxy equals Cyx to ~1e-6 at every row and level (columns Cxy, Cyx) -- the two directed cross-correlations agree, so no net circulation around the loop. The two readings that should agree, agree (J/L check).",
    "No sustained rotation: phiMean stays a bounded wander near 0 (|phiMean| < ~1.1 even at level 4 over the whole run) with no monotone ramp; cycling would drive a steadily-accumulating net angle (column phiMean).",
    "tauC (relaxation time) per level from log-linear fit of C: ~1.3, 2.4, 5.0, 10, 20 -- doubles each step, grows monotonically with level (the 'longer to settle' the researcher reports) (columns C, tau).",
    "chi_inf (static integrated response) per level: 1.07, 1.52, 2.69, 5.10, 9.98 -- roughly doubles each step, grows monotonically with level (the 'bigger excursions') (column chi).",
    "Equilibrium FDR holds at every level: chi vs (C0 - C) is linear (rms <0.006) AND its slope equals chi_inf which equals tauC to within ~3% -- three independent readings of the relaxation magnitude agree (the J/L cross-check passes), the signature of relaxation toward balance not driven cycling (columns chi, C).",
    "Window sanity per level: each level's C settles to <1% of C0 inside its own tau window (tau_max grows 11.4 -> 160 with level) -- the deliberately longer windows are matched to the slower settling; the reading is not a camera artifact (column tau, C).",
    "phiVar grows roughly linearly in elapsed time at every level (diffusive spread of the turnover angle), consistent with noise-driven wander about a fixed point, not phase-coherent cycling (column phiVar).",
]

not_grounded = [
    "WHETHER a 6th, stronger setting would finally start cycling or tip unstable: that lives across the control axis BEYOND level 4 (a collapsed axis -- the sweep stops at level 4). The 5 sampled points show a monotone, decelerating-but-not-diverging trend with no rotation onset; extrapolating past the last point is not groundable from this data.",
    "The absolute distance to any instability/Hopf edge in the researcher's native knob units: no interaction-strength magnitudes, noise level, or model parameters are in the data (packet states this explicitly), so headroom can only be stated qualitatively (still interior, monotone trend) not as a number in knob units.",
    "An exact functional law for how tauC and chi_inf scale with the knob: only 5 settings and no knob magnitude are provided, so the band is read as monotone-increasing placements, not fit to a divergence law that could pin a critical knob value (would need the swept control magnitude + more points -- collapsed axis).",
    "Which setting is 'best/healthiest' for the community: that is a researcher preference / viewport dial, not a freeze computation -- surfaced here, not pinned (WORKFLOW §6 value-laden carve-out).",
]

fig, axes = figure_with_header(
    n_plots=4, slug="coupling_ramp_v7", date="PENDING", phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement)

cmap = plt.cm.viridis(np.linspace(0, 0.9, len(levels)))

# Plot 0: autocorrelation C(tau) per level (normalized) -- shows single-exp, no neg lobe
ax = axes[0]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["tau"], d["C"] / d["C"][0], color=cmap[i], lw=1.4, label=f"L{lv}")
ax.axhline(0, color="k", lw=0.6, ls=":")
ax.set_xlabel("tau (own clock per level)"); ax.set_ylabel("C(tau)/C(0)  [autocorr]")
ax.set_title("Relaxation: monotone decay, no negative lobe = no cycling")
ax.legend(fontsize=7, ncol=5); ax.set_xscale("symlog", linthresh=1)

# Plot 1: FDR locus chi vs (C0 - C) per level
ax = axes[1]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["C"][0] - d["C"], d["chi"], color=cmap[i], lw=1.4, label=f"L{lv}")
ax.set_xlabel("C(0) - C(tau)"); ax.set_ylabel("chi (integrated response)")
ax.set_title("Universal FDR locus: linear => equilibrium relaxation")
ax.legend(fontsize=7, ncol=5)

# Plot 2: phiMean(t) per level -- bounded wander (no rotation ramp)
ax = axes[2]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["tau"], d["phiMean"], color=cmap[i], lw=1.0, label=f"L{lv}")
ax.axhline(0, color="k", lw=0.6, ls=":")
ax.set_xlabel("elapsed time tau"); ax.set_ylabel("phiMean (net cumulative turnover angle)")
ax.set_title("Net turnover angle wanders ~0: no sustained cycling")
ax.legend(fontsize=7, ncol=5); ax.set_xscale("symlog", linthresh=1)

# Plot 3: THE BAND -- swept quantities vs control level
ax = axes[3]
ax.plot(levels, tauCs, "o-", color="#c44", label="tauC (relax time)")
ax.plot(levels, chiinf, "s-", color="#48c", label="chi_inf (static resp)")
ax.set_yscale("log")
ax.set_xlabel("control level (interaction strength, 0..4)")
ax.set_ylabel("placement quantity (log)")
ax.set_title("THE BAND: tauC & chi_inf migrate UP monotonically; KIND fixed")
ax.set_xticks(levels)
# annotate the invariants that stay put on a twin axis
ax2 = ax.twinx()
ax2.plot(levels, [max(c, 1e-12) for c in crossa], "^--", color="#7a7", label="max|Cxy-Cyx| (~0, no current)")
ax2.plot(levels, np.abs(rots), "x--", color="#a7a", label="|phiMean ramp| (~0, no rotation)")
ax2.set_ylabel("invariants that STAY PUT")
ax2.set_yscale("log")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=6.5, loc="center right")

out, STAMP = timestamped_view_path(HERE)
# rebuild header with the real stamp now that we have it
plt.close(fig)
fig, axes = figure_with_header(
    n_plots=4, slug="coupling_ramp_v7", date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement)

ax = axes[0]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["tau"], d["C"] / d["C"][0], color=cmap[i], lw=1.4, label=f"L{lv}")
ax.axhline(0, color="k", lw=0.6, ls=":")
ax.set_xlabel("tau (own clock per level)"); ax.set_ylabel("C(tau)/C(0)  [autocorr]")
ax.set_title("Relaxation: monotone decay, no negative lobe = no cycling")
ax.legend(fontsize=7, ncol=5); ax.set_xscale("symlog", linthresh=1)

ax = axes[1]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["C"][0] - d["C"], d["chi"], color=cmap[i], lw=1.4, label=f"L{lv}")
ax.set_xlabel("C(0) - C(tau)"); ax.set_ylabel("chi (integrated response)")
ax.set_title("Universal FDR locus: linear => equilibrium relaxation")
ax.legend(fontsize=7, ncol=5)

ax = axes[2]
for i, lv in enumerate(levels):
    d = per[lv]
    ax.plot(d["tau"], d["phiMean"], color=cmap[i], lw=1.0, label=f"L{lv}")
ax.axhline(0, color="k", lw=0.6, ls=":")
ax.set_xlabel("elapsed time tau"); ax.set_ylabel("phiMean (net cumulative turnover angle)")
ax.set_title("Net turnover angle wanders ~0: no sustained cycling")
ax.legend(fontsize=7, ncol=5); ax.set_xscale("symlog", linthresh=1)

ax = axes[3]
ax.plot(levels, tauCs, "o-", color="#c44", label="tauC (relax time)")
ax.plot(levels, chiinf, "s-", color="#48c", label="chi_inf (static resp)")
ax.set_yscale("log")
ax.set_xlabel("control level (interaction strength, 0..4)")
ax.set_ylabel("placement quantity (log)")
ax.set_title("THE BAND: tauC & chi_inf migrate UP monotonically; KIND fixed")
ax.set_xticks(levels)
ax2 = ax.twinx()
ax2.plot(levels, [max(c, 1e-12) for c in crossa], "^--", color="#7a7", label="max|Cxy-Cyx| (~0)")
ax2.plot(levels, np.abs(rots), "x--", color="#a7a", label="|phiMean ramp| (~0)")
ax2.set_ylabel("invariants that STAY PUT (log)")
ax2.set_yscale("log")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=6.5, loc="center right")

fig.savefig(out, dpi=150)
print(f"\nVIEW: {out}")
print(f"STAMP: {STAMP}")
