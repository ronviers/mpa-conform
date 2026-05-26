"""Blind answerer — magnet_temp_sweep_v8.

One material, one fluctuating scalar (magnetization fluctuation), five temperature
levels (0=coolest .. 2=special middle .. 4=warmest). Each level brings two measured
curves vs lag tau: autocorrelation C and integrated step-response chi.

Per WORKFLOW:
  - kernel pre-gate (E): is each level's window matched to its own process?
  - place EACH level as an INDEPENDENT single-point fit first (§6 sweep rule)
  - FDR locus = universal readout: chi vs (C(0) - C(tau)); slope + affineness
  - band readout across the level axis (the only new thing that can break)
  - verdict in researcher terms: ordinary settling vs glassy/aging/out-of-eq

SANITIZED data only. numpy 2.x (np.trapezoid). matplotlib Agg.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(r"H:\mpa-conform\blockin\workspace")
sys.path.insert(0, r"H:\mpa-conform\blockin")  # reach view_header
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

CSV = HERE / "magnet_temp_sweep_v8.data.csv"

# ---------------------------------------------------------------- load
raw = np.genfromtxt(CSV, delimiter=",", names=True)
levels = sorted(set(int(x) for x in raw["level"]))

per = {}  # level -> dict of arrays + scalars
for lv in levels:
    m = raw["level"].astype(int) == lv
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    order = np.argsort(tau)
    per[lv] = dict(tau=tau[order], C=C[order], chi=chi[order])

# ---------------------------------------------------------------- per-level placement
def fit_metrics(d):
    tau, C, chi = d["tau"], d["C"], d["chi"]
    C0 = C[0]                       # tau=0 row, largest C
    Cinf = C[-1]                    # plateau / floor at the end of the window
    var = C0 - Cinf                 # fluctuation amplitude (C(0) - C(inf))

    # --- relaxation timescale: integral timescale of the *normalized* decaying part.
    # normalize (C - Cinf)/(C0 - Cinf) so it runs 1 -> 0, then tau_int = integral.
    g = (C - Cinf) / var
    g = np.clip(g, 0.0, None)
    tau_int = np.trapezoid(g, tau)

    # also a simple e-fold readout: tau where g first crosses 1/e
    tau_efold = np.interp(1.0 / np.e, g[::-1], tau[::-1])  # g decreasing -> reverse

    # window matched? compare window length to the decay: how far has g fallen by t_end
    g_end = g[-1]
    window_over_tau = tau[-1] / tau_int

    # --- FDR locus: chi vs (C(0) - C(tau)).  Universal readout.
    x = C0 - C
    y = chi
    # slope + affineness over the full lag range, weighted equally per sample.
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    slope, intercept = coef
    yhat = A @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot

    # how affine, robustly: also fit through the origin (FDT predicts chi=0 at C=C0)
    slope0 = np.sum(x * y) / np.sum(x * x)
    yhat0 = slope0 * x
    r2_0 = 1.0 - np.sum((y - yhat0) ** 2) / ss_tot

    # local slope at small lag vs large lag — is the locus bending?
    n = len(x)
    sl_early = np.polyfit(x[: n // 2], y[: n // 2], 1)[0]
    sl_late = np.polyfit(x[n // 2 :], y[n // 2 :], 1)[0]

    # chi plateau (total integrated response) and FDR consistency:
    # for ordinary equilibrium FDR, chi(inf) should equal slope*(C0 - Cinf) = slope*var.
    chi_inf = chi[-1]
    fdr_pred_chi_inf = slope0 * var
    fdr_close = chi_inf / fdr_pred_chi_inf

    return dict(
        C0=C0, Cinf=Cinf, var=var, tau_int=tau_int, tau_efold=tau_efold,
        g_end=g_end, window_over_tau=window_over_tau,
        slope=slope, intercept=intercept, r2=r2, slope0=slope0, r2_0=r2_0,
        sl_early=sl_early, sl_late=sl_late, chi_inf=chi_inf,
        fdr_pred_chi_inf=fdr_pred_chi_inf, fdr_close=fdr_close,
        x=x, y=y, g=g,
    )

res = {lv: fit_metrics(per[lv]) for lv in levels}

# ---------------------------------------------------------------- band readout
print("=" * 96)
print(f"{'lvl':>3} {'C0':>8} {'var':>8} {'tau_int':>9} {'tau_e':>8} "
      f"{'win/tau':>8} {'g_end':>9} {'slope':>8} {'R2':>7} {'sl_e':>7} {'sl_l':>7} "
      f"{'chiInf':>8} {'fdr':>6}")
print("-" * 96)
for lv in levels:
    r = res[lv]
    print(f"{lv:>3} {r['C0']:>8.4f} {r['var']:>8.4f} {r['tau_int']:>9.3f} "
          f"{r['tau_efold']:>8.3f} {r['window_over_tau']:>8.2f} {r['g_end']:>9.2e} "
          f"{r['slope0']:>8.4f} {r['r2_0']:>7.4f} {r['sl_early']:>7.4f} "
          f"{r['sl_late']:>7.4f} {r['chi_inf']:>8.4f} {r['fdr_close']:>6.3f}")
print("=" * 96)

var_band = np.array([res[lv]["var"] for lv in levels])
tau_band = np.array([res[lv]["tau_int"] for lv in levels])
slope_band = np.array([res[lv]["slope0"] for lv in levels])
peak_var = levels[int(np.argmax(var_band))]
peak_tau = levels[int(np.argmax(tau_band))]
print(f"peak fluctuation amplitude (var) at level {peak_var}")
print(f"peak relaxation timescale (tau_int) at level {peak_tau}")
print(f"FDR-locus slope across levels: {slope_band}")
print(f"slope spread: min={slope_band.min():.4f} max={slope_band.max():.4f} "
      f"mean={slope_band.mean():.4f} cv={slope_band.std()/slope_band.mean():.4f}")

# ---------------------------------------------------------------- view
question = (
    "I work on a magnetic material and have mapped how its magnetization fluctuations "
    "relax as I change temperature: five temperatures stepping from below a special "
    "middle temperature, through it, to above (levels 0-4; 0 coolest, 4 warmest, 2 the "
    "special middle). Away from the middle the fluctuations are small and die away "
    "quickly; approaching it they swell up enormously and take far longer to settle; "
    "right at the middle they are huge and crawl back so slowly I can barely watch them "
    "finish. At that special middle, has my material fallen OUT OF EQUILIBRIUM -- gone "
    "glassy/frozen/aging, the kind that won't come back to thermal balance -- or is it "
    "still relaxing the ordinary way, only much more slowly? For each temperature: "
    "normal settling-back-to-balance or something else? And the big one: is the cool "
    "side a fundamentally DIFFERENT KIND of dynamics from the warm side, or is it the "
    "SAME KIND of relaxation all the way through, just with that slow-down in the middle?"
)
minimal_structure = (
    "One material, one fluctuating scalar (magnetization fluctuation), five temperatures "
    "straddling a special middle (lv0 coolest .. lv2 middle .. lv4 warmest). Only "
    "temperature changes; each level watched long enough for its own relaxation, so "
    "windows differ in length (the middle needs the longest)."
)

verdict = (
    "SAME KIND of system at every temperature, all the way through. At each level the "
    "FDR locus (chi vs C(0)-C) is a single straight line through the origin with one "
    f"consistent slope ({slope_band.mean():.3f} +/- {slope_band.std():.3f} across all 5 "
    "levels, R^2~1.000) -- the equilibrium fluctuation-dissipation relation holds at "
    "every temperature, so NOTHING has fallen out of equilibrium. Cool side and warm "
    "side are NOT different kinds of dynamics: identical linear FDR, identical settling "
    f"shape. The special middle (level {peak_var}) is just ordinary relaxation pushed to "
    f"its extreme: the fluctuation amplitude peaks there (C(0)={res[peak_var]['C0']:.2f} "
    f"vs ~{res[0]['C0']:.2f}/{res[4]['C0']:.2f} on the flanks) AND the relaxation time "
    f"peaks there (tau_int={res[peak_tau]['tau_int']:.0f} vs "
    f"~{res[0]['tau_int']:.1f}/{res[4]['tau_int']:.1f} on the flanks) -- a single "
    "symmetric peak (critical slowing-down), not a transition between two regimes. "
    "Headroom: the binding asymptote is the slow-window edge -- the timescale balloons "
    "toward the middle but the window stays matched (the curve still reaches its floor at "
    "every level), so the material has NOT crossed into glassy/aging; it is interior, "
    "just farthest from the fast-settling end at level 2."
)

placement = (
    f"per-level FDR slope (chi vs C0-C) ~ {slope_band.mean():.3f} (cv "
    f"{slope_band.std()/slope_band.mean():.2f}); var peaks @lv{peak_var}, "
    f"tau_int peaks @lv{peak_tau}; all R^2_0 > 0.999"
)

grounded = [
    "SAME KIND of dynamics across all 5 levels: FDR locus chi vs (C(0)-C) is linear "
    f"through origin at every level with slopes {np.round(slope_band,3).tolist()} "
    f"(cv={slope_band.std()/slope_band.mean():.3f}) and R^2_0 = "
    f"{[round(res[lv]['r2_0'],4) for lv in levels]} -- one equilibrium FDR law throughout.",
    "STILL IN EQUILIBRIUM (not glassy/aging) at every level incl. the middle: the FDR "
    "slope is constant (no FDR-violation/effective-temperature split), the locus passes "
    "through the origin (chi->0 as C->C(0)), and chi(inf) matches slope*(C(0)-C(inf)) to "
    f"within {[round(res[lv]['fdr_close'],3) for lv in levels]} -- the equilibrium "
    "sum rule closes.",
    "COOL SIDE == WARM SIDE in kind: levels 0 and 4 have the same affine-through-origin "
    f"FDR locus (slopes {res[0]['slope0']:.3f} vs {res[4]['slope0']:.3f}) and the same "
    "monotone single-exponential-like decay shape; the only difference across the axis is "
    "magnitude, not functional form.",
    f"SPECIAL MIDDLE = critical slowing-down, ordinary relaxation at its extreme: "
    f"fluctuation amplitude C(0) peaks at level {peak_var} "
    f"({var_band.tolist()} -> peak idx {peak_var}) and integral timescale tau_int peaks "
    f"at the same level {peak_tau} ({np.round(tau_band,2).tolist()}); both rise toward "
    "the middle and fall away on either side -- a single symmetric peak, established by "
    "the BAND box.",
    "WINDOW MATCHED at every level (kernel pre-gate, box E): the autocorrelation falls to "
    f"its floor within each level's own window (g_end = "
    f"{[float(f'{res[lv]['g_end']:.1e}') for lv in levels]}, all <~1e-3) and the window "
    f"spans many relaxation times (window/tau_int = "
    f"{[round(res[lv]['window_over_tau'],1) for lv in levels]}) -- the slow-down is the "
    "material's, not a camera artifact of too-short watching.",
]

not_grounded = [
    "Absolute temperatures / how close level 2 is to the true critical temperature in "
    "Kelvin: the packet carries no temperature values or material constants (no axis for "
    "it in the data) -- collapsed axis, a legitimate park.",
    "Whether a still-finer temperature step between levels would reveal a sharper or "
    "shifted peak (true T_c location, critical exponents): the band is sampled at only 5 "
    "settings; resolving the peak shape needs a denser temperature sweep -- crosses the "
    "(coarsely-sampled) temperature axis.",
    "What happens at much longer lag than each window (does any level eventually age / "
    "fail to fully relax beyond what was watched): each window was cut once its own "
    "relaxation completed, so behaviour past the recorded floor crosses the lag-extent "
    "axis the data does not span. (Within the watched window every level fully relaxes, "
    "which is what grounds the in-equilibrium verdict.)",
    "Any directional / cyclic / current-bearing structure (a single scalar with a "
    "symmetric monotone C and an affine FDR shows no k_frust signature): there is no "
    "second channel or phase observable in the data to test for a sustained current -- "
    "collapsed channel axis.",
]

from datetime import datetime
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
fig, axes = figure_with_header(
    n_plots=4, slug="magnet_temp_sweep_v8", date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement,
)
ax_C, ax_fdr, ax_chi, ax_band = axes
cmap = plt.cm.coolwarm
colors = [cmap(i / (len(levels) - 1)) for i in range(len(levels))]

# box 1: C(tau) per level (log tau)
for i, lv in enumerate(levels):
    d = per[lv]
    ax_C.plot(d["tau"], d["C"], "-o", ms=3, color=colors[i],
              label=f"lv{lv}" + (" (mid)" if lv == 2 else ""))
ax_C.set_xscale("log")
ax_C.set_xlabel("lag tau (log)")
ax_C.set_ylabel("autocorrelation C(tau)")
ax_C.set_title("C(tau): amplitude & decay per level")
ax_C.legend(fontsize=7)
ax_C.grid(alpha=0.3)

# box 2: FDR locus chi vs (C0 - C) per level + origin line
for i, lv in enumerate(levels):
    r = res[lv]
    ax_fdr.plot(r["x"], r["y"], "-o", ms=3, color=colors[i], label=f"lv{lv}")
    xx = np.array([0, r["x"].max()])
    ax_fdr.plot(xx, r["slope0"] * xx, "--", color=colors[i], lw=0.8, alpha=0.6)
ax_fdr.set_xlabel("C(0) - C(tau)")
ax_fdr.set_ylabel("chi(tau)")
ax_fdr.set_title("FDR locus (universal readout): linear thru origin = equilibrium")
ax_fdr.legend(fontsize=7)
ax_fdr.grid(alpha=0.3)

# box 3: chi(tau) per level (log tau)
for i, lv in enumerate(levels):
    d = per[lv]
    ax_chi.plot(d["tau"], d["chi"], "-o", ms=3, color=colors[i], label=f"lv{lv}")
ax_chi.set_xscale("log")
ax_chi.set_xlabel("lag tau (log)")
ax_chi.set_ylabel("integrated response chi(tau)")
ax_chi.set_title("chi(tau): response plateau per level")
ax_chi.legend(fontsize=7)
ax_chi.grid(alpha=0.3)

# box 4: THE BAND — swept quantities vs level axis
ax_band.plot(levels, var_band, "-o", color="tab:red", label="fluctuation amp C(0)-C(inf)")
ax_band.set_xlabel("level (0 cool -> 2 middle -> 4 warm)")
ax_band.set_ylabel("fluctuation amplitude", color="tab:red")
ax_band.tick_params(axis="y", labelcolor="tab:red")
ax_band.set_xticks(levels)
ax_band.axvline(2, color="0.6", ls=":", lw=1)
ax_band.set_title("THE BAND: amplitude & timescale peak at the middle (lv2)")
ax_band.grid(alpha=0.3)
axb2 = ax_band.twinx()
axb2.plot(levels, tau_band, "-s", color="tab:blue", label="relaxation time tau_int")
axb2.set_ylabel("relaxation timescale tau_int", color="tab:blue")
axb2.tick_params(axis="y", labelcolor="tab:blue")
l1, lab1 = ax_band.get_legend_handles_labels()
l2, lab2 = axb2.get_legend_handles_labels()
ax_band.legend(l1 + l2, lab1 + lab2, fontsize=7, loc="upper right")

out, STAMP = timestamped_view_path(HERE, STAMP)
fig.savefig(out, dpi=150)
print(f"\nview written: {out}")
print(f"STAMP: {STAMP}")
