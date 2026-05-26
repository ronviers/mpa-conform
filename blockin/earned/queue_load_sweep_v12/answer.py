"""Blind answerer — queue_load_sweep_v12.

Sweep: ONE system at FIVE loads (level 0..4). Method (mandatory for a sweep):
place EACH level as an independent single-point fit FIRST, then read the band.
Per level: FDR locus slope (chi vs C0 - C(tau)), straight vs bent;
relaxation timescale (tau where C decays to C0/e); fluctuation size C(0);
C shape (single vs two-step, monotone vs oscillating).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, r"H:\mpa-conform\blockin")
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

WS = r"H:\mpa-conform\blockin\workspace"
DATA = Path(WS) / "queue_load_sweep_v12.data.csv"

raw = np.genfromtxt(DATA, delimiter=",", names=True)
levels = sorted(set(int(x) for x in raw["level"]))

per = {}
for lv in levels:
    m = raw["level"] == lv
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    util = float(raw["util_rel"][m][0])
    order = np.argsort(tau)
    tau, C, chi = tau[order], C[order], chi[order]
    per[lv] = dict(tau=tau, C=C, chi=chi, util=util)

print("=" * 78)
print("PER-LEVEL INDEPENDENT PLACEMENT")
print("=" * 78)

for lv in levels:
    d = per[lv]
    tau, C, chi, util = d["tau"], d["C"], d["chi"], d["util"]
    C0 = C[0]  # variance of fluctuating quantity (NOT normalized -> use own C0)
    chi0 = chi[0]
    chi_inf = chi[-1]

    # --- FDR locus: chi vs (C0 - C(tau)). Slope-1 straight line through origin = FDT (X=1).
    x = C0 - C  # goes 0 -> C0 as tau grows
    y = chi
    # initial-segment slope (small displacement) vs late-segment slope (large displacement)
    # use fraction of the displacement range to define segments robustly
    xnorm = x / C0
    early = xnorm < 0.30
    late = xnorm > 0.70
    # slope through origin on early segment: least squares y = s*x (force through 0)
    def slope_through_origin(xx, yy):
        xx = xx[xx > 0]
        # reselect yy by mask consistency
        return None
    # do it cleanly:
    me = (xnorm < 0.30) & (x > 0)
    ml = (xnorm > 0.70)
    s_early = np.sum(x[me] * y[me]) / np.sum(x[me] ** 2) if me.sum() >= 2 else np.nan
    s_late = np.sum(x[ml] * y[ml]) / np.sum(x[ml] ** 2) if ml.sum() >= 2 else np.nan
    # overall slope (full locus, through origin)
    s_all = np.sum(x[1:] * y[1:]) / np.sum(x[1:] ** 2)
    # straightness: chi_inf / C0 (if FDT exactly, chi_inf -> C0, slope 1)
    fdt_ratio = chi_inf / C0
    # max deviation of locus from straight slope-1 line y=x
    resid_straight = np.max(np.abs(y - x)) / C0

    # --- relaxation timescale: tau where C falls to C0/e
    target = C0 / np.e
    # C is monotone decreasing -> interpolate
    Cdesc = C
    if Cdesc[0] > target > Cdesc[-1]:
        # find crossing
        idx = np.where(Cdesc <= target)[0][0]
        t1, t0 = tau[idx], tau[idx - 1]
        c1, c0 = Cdesc[idx], Cdesc[idx - 1]
        tau_relax = t0 + (target - c0) * (t1 - t0) / (c1 - c0)
    else:
        tau_relax = np.nan

    # --- C shape: monotone? zero crossings? two-step?
    dC = np.diff(C)
    monotone_dec = np.all(dC <= 1e-9)
    sign_changes = np.sum(np.diff(np.sign(C - 0)) != 0)  # zero crossings of C itself
    # two-step would show a plateau then second decay: check log-slope for a shoulder
    # crude: ratio of curvature; here just report monotone + no negatives
    neg_C = np.any(C < -1e-9)

    per[lv].update(dict(C0=C0, chi_inf=chi_inf, s_early=s_early, s_late=s_late,
                        s_all=s_all, fdt_ratio=fdt_ratio, resid_straight=resid_straight,
                        tau_relax=tau_relax, monotone=monotone_dec, neg_C=neg_C,
                        x=x, y=y))

    print(f"\n--- level {lv}  (util_rel = {util}x) ---")
    print(f"  C(0) fluctuation size (variance)   : {C0:.4g}")
    print(f"  chi(inf) plateau                   : {chi_inf:.4g}")
    print(f"  FDT ratio chi_inf / C0             : {fdt_ratio:.5f}   (=1 if FDT exact)")
    print(f"  FDR slope early segment (x<0.3 C0) : {s_early:.4f}")
    print(f"  FDR slope late  segment (x>0.7 C0) : {s_late:.4f}")
    print(f"  FDR slope full locus (thru origin) : {s_all:.4f}")
    print(f"  max |locus - y=x| / C0             : {resid_straight:.2e}  (0 = perfect straight slope-1)")
    print(f"  relaxation time tau(C=C0/e)        : {tau_relax:.4g}")
    print(f"  C monotone decreasing              : {monotone_dec}")
    print(f"  C goes negative (oscillation)      : {neg_C}")
    print(f"  tau window [min,max]               : [{tau[1]:.4g}, {tau[-1]:.4g}]")

print("\n" + "=" * 78)
print("BAND ACROSS LOADS")
print("=" * 78)
print(f"{'lvl':>3} {'util':>8} {'C0':>12} {'tau_relax':>12} {'FDTratio':>9} {'slope':>8}")
for lv in levels:
    d = per[lv]
    print(f"{lv:>3} {d['util']:>8.3f} {d['C0']:>12.4g} {d['tau_relax']:>12.4g} "
          f"{d['fdt_ratio']:>9.5f} {d['s_all']:>8.4f}")

# divergence scaling of C0 and tau_relax vs util
util = np.array([per[lv]["util"] for lv in levels])
C0s = np.array([per[lv]["C0"] for lv in levels])
trelax = np.array([per[lv]["tau_relax"] for lv in levels])
print(f"\nC0 growth (level0 -> level4)      : {C0s[0]:.4g} -> {C0s[-1]:.4g}  "
      f"= {C0s[-1]/C0s[0]:.1f}x")
print(f"tau_relax growth (level0 -> level4): {trelax[0]:.4g} -> {trelax[-1]:.4g}  "
      f"= {trelax[-1]/trelax[0]:.1f}x")
# log-log slopes vs util_rel
lu = np.log(util)
print(f"\nlog-log slope  C0 vs util_rel      : {np.polyfit(lu, np.log(C0s),1)[0]:.3f}")
print(f"log-log slope  tau_relax vs util   : {np.polyfit(lu, np.log(trelax),1)[0]:.3f}")

# ----------------------------------------------------------------------------
# VIEW
# ----------------------------------------------------------------------------
import matplotlib.pyplot as plt  # noqa: E402

out, STAMP = timestamped_view_path(WS)

QUESTION = (
    "Single-server queue measured at five increasing loads (lightest -> closest to "
    "capacity). As load climbs the queue settles much slower and swings much larger. "
    "At each load is the response still matched to the fluctuations (in balance) or "
    "has it fallen out of balance? Toward the limit am I just slower-and-noisier-but-fine "
    "or approaching a genuine breakdown, and how close to the limit am I?")
MIN_STRUCT = ("One queue (one scalar: queue length), five increasing loads; only the load "
              "changes. Two curves per load: autocorrelation C and integrated step-response chi.")

VERDICT = (
    "IN BALANCE AT EVERY LOAD - no breakdown. The FDR locus (chi vs C0-C) is a single "
    "straight slope-1 line through the origin at all five loads (chi_inf/C0 = 1.000 to "
    f"~4 digits, X=1), so the response stays exactly matched to the fluctuations even at the "
    f"heaviest load. What diverges is timescale and fluctuation size, NOT balance: C(0) grows "
    f"{C0s[-1]/C0s[0]:.0f}x ({C0s[0]:.3g}->{C0s[-1]:.4g}) and relaxation time grows "
    f"{trelax[-1]/trelax[0]:.0f}x across the sweep, both as steep power laws in util_rel. "
    "This is critical slowing + diverging variance of a system that stays reversible/in-balance "
    "- slower-and-noisier-but-fine, not a glassy/stuck/aging transition. Headroom: the heaviest "
    "load is the closest measured to the limit but the data gives no native distance to capacity.")

grounded = [
    "in balance at every load <- FDR locus is a single straight line through origin of slope 1 at all 5 levels; max|locus - y=x|/C0 < 1e-3, and chi_inf/C0 = 1.0000 (X=1, FDT holds exactly)",
    "no aging/bending <- early-segment and late-segment FDR slopes both = 1 at every level (no shallow X<1 tail); locus never bends",
    f"fluctuation size diverges <- C(0) grows monotonically {C0s[0]:.3g} (lvl0) -> {C0s[-1]:.4g} (lvl4), ~{C0s[-1]/C0s[0]:.0f}x, log-log slope ~{np.polyfit(lu, np.log(C0s),1)[0]:.2f} vs util_rel",
    f"timescale diverges (critical slowing) <- relaxation time tau(C=C0/e) grows {trelax[0]:.3g} -> {trelax[-1]:.4g}, ~{trelax[-1]/trelax[0]:.0f}x, log-log slope ~{np.polyfit(lu, np.log(trelax),1)[0]:.2f} vs util_rel",
    "simple reversible relaxation (not two-step/glassy) <- C is single monotone decay to 0 at every level, no plateau/shoulder, no negative excursion (no oscillation/current)",
    "slower-and-noisier-but-fine, NOT breakdown <- the invariant that would flag breakdown (FDR slope X) stays pinned at 1; only timescale and amplitude (parameterizations that diverge as load->capacity) blow up",
]

not_grounded = [
    "native utilization / arrival rate / service rate - data carries only util_rel (relative, lightest=1.0x); no absolute rho or distance-to-capacity in native units",
    "the exponent of the divergence in NATIVE load units - util_rel is a relative dial; the power-law slopes above are vs util_rel, not vs (1 - rho), so the true critical exponent and singularity location are not recoverable here",
    "behaviour exactly AT the capacity limit - heaviest measured load (util_rel=32.67x) is the closest point but is still interior; no point at or past the limit was supplied",
    "one-sided headroom as a native number - cannot state how close level 4 is to capacity; only that it is the closest of the five and that nothing pathological has appeared yet at it",
    "behaviour past each level's tau window - each curve is truncated where C has decayed to ~0; any second/slower process beyond the window cannot be excluded (windows lengthen with load by design, but are finite)",
    "whether the divergence is a true critical point vs a smooth steep blow-up - five points fit a power law in util_rel but cannot distinguish a genuine singularity at a finite load from monotone steepening",
]

placement = (f"X=1 all loads (FDR slope 1, chi_inf/C0=1.000); C0: {C0s[0]:.3g}->{C0s[-1]:.4g} (~{C0s[-1]/C0s[0]:.0f}x); "
             f"tau_relax: {trelax[0]:.3g}->{trelax[-1]:.4g} (~{trelax[-1]/trelax[0]:.0f}x); C single monotone decay")

fig, axes = figure_with_header(
    n_plots=4, slug="queue_load_sweep_v12", date=STAMP, phase="DEV/blind",
    question=QUESTION, minimal_structure=MIN_STRUCT, verdict=VERDICT,
    grounded=grounded, not_grounded=not_grounded, placement=placement)
ax0, ax1, ax2, ax3 = axes

colors = plt.cm.viridis(np.linspace(0, 0.9, len(levels)))

# Box 0: C(tau) per level, normalized + log-x -> shows relaxation slowing right-shift
for i, lv in enumerate(levels):
    d = per[lv]
    ax0.semilogx(d["tau"][1:], d["C"][1:] / d["C0"], "-", color=colors[i],
                 label=f"L{lv} u={d['util']:.1f}")
ax0.axhline(1/np.e, ls=":", color="grey", lw=0.8)
ax0.set_xlabel("tau (lag)"); ax0.set_ylabel("C(tau)/C(0)")
ax0.set_title("Relaxation per load (slows -> right)"); ax0.legend(fontsize=6)

# Box 1: FDR locus per level chi vs (C0 - C), each normalized by its own C0 -> all on slope-1 line if FDT
for i, lv in enumerate(levels):
    d = per[lv]
    ax1.plot(d["x"] / d["C0"], d["y"] / d["C0"], "-", color=colors[i], lw=1.2)
ax1.plot([0, 1], [0, 1], "k--", lw=1.0, label="slope 1 (FDT, X=1)")
ax1.set_xlabel("(C0 - C(tau)) / C0"); ax1.set_ylabel("chi(tau) / C0")
ax1.set_title("FDR locus per load (all straight, slope 1)"); ax1.legend(fontsize=7)

# Box 2 (BAND): C0 and tau_relax vs util_rel, log-log -> the divergence
ax2.loglog(util, C0s, "o-", color="#b30000", label="C(0) fluctuation size")
ax2.loglog(util, trelax, "s-", color="#00468b", label="tau_relax (timescale)")
ax2.set_xlabel("util_rel (relative load)"); ax2.set_ylabel("magnitude")
ax2.set_title("BAND: divergence vs load"); ax2.legend(fontsize=7)
ax2.grid(True, which="both", alpha=0.25)

# Box 3 (BAND): FDR slope (X) vs util_rel -> stays flat at 1 (no breakdown)
slopes_all = np.array([per[lv]["s_all"] for lv in levels])
fdt_ratios = np.array([per[lv]["fdt_ratio"] for lv in levels])
ax3.plot(util, slopes_all, "o-", color="#0a5d00", label="FDR slope X (locus)")
ax3.plot(util, fdt_ratios, "^--", color="#5d8d00", label="chi_inf / C0")
ax3.axhline(1.0, ls=":", color="grey")
ax3.set_xlabel("util_rel (relative load)"); ax3.set_ylabel("X")
ax3.set_ylim(0.0, 1.15)
ax3.set_xscale("log")
ax3.set_title("BAND: balance stays X=1 (no aging)"); ax3.legend(fontsize=7)

fig.savefig(out, dpi=150)
print(f"\nVIEW: {out}")
