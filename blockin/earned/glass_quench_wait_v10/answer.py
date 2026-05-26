"""Blind ANSWERER for glass_quench_wait_v10.

One material, one temperature, five waiting times (ages) after a single quench.
Method: place EACH level as an independent single-point read FIRST (two-step C
params + FDR locus slow-slope X), then read the band/trend across levels.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

HERE = r"H:\mpa-conform\blockin\workspace"
sys.path.insert(0, r"H:\mpa-conform\blockin")
from view_header import figure_with_header, timestamped_view_path

DATA = Path(HERE) / "glass_quench_wait_v10.data.csv"
raw = np.genfromtxt(DATA, delimiter=",", names=True)

levels = sorted(set(int(l) for l in raw["level"]))
per = {}
for lv in levels:
    m = raw["level"] == lv
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    order = np.argsort(tau)
    per[lv] = dict(tau=tau[order], C=C[order], chi=chi[order])

# ----------------------------------------------------------------------
# Per-level reads
# ----------------------------------------------------------------------
def linfit(x, y):
    A = np.vstack([x, np.ones_like(x)]).T
    sol, *_ = np.linalg.lstsq(A, y, rcond=None)
    return sol[0], sol[1]  # slope, intercept

results = {}
print("=" * 78)
for lv in levels:
    d = per[lv]
    tau, C, chi = d["tau"], d["C"], d["chi"]
    x = 1.0 - C  # 1 - C(tau), with C(0)=1
    y = chi

    # FDR locus: fast segment (small 1-C) vs slow segment (large 1-C).
    # Fast segment = early part of the locus; slow = later part.
    # Split at the "knee": use 1-C threshold. Fast ~ 1-C < 0.25; slow ~ 1-C > 0.30
    fast_mask = (x > 1e-9) & (x < 0.22)
    slow_mask = x > 0.35

    fast_slope, _ = linfit(x[fast_mask], y[fast_mask])
    slow_slope, slow_int = linfit(x[slow_mask], y[slow_mask])

    # Two-step C: plateau height = C at the knee (where locus bends).
    # The fast drop goes from C=1 to a plateau; estimate plateau as C where
    # 1-C crosses ~0.22 (end of fast segment) -> read the C value there.
    # More robust: plateau = C at the local "shoulder" = minimum of |dlogC/dlogtau|
    # in the mid range. Use the C value at the knee in 1-C space.
    # Knee 1-C ~ where fast and slow lines cross.
    fs, fi = linfit(x[fast_mask], y[fast_mask])
    knee_x = (fi - slow_int) / (slow_slope - fs)
    plateau_C = 1.0 - knee_x

    # slow relaxation timescale: tau where C drops to half of the plateau region.
    # Define as tau where C crosses plateau_C/2 ... but better, where C crosses a
    # fixed reference. Use tau at C = 0.4 (well into the slow tail for all levels)
    def tau_at_C(target):
        # interpolate in log-tau vs C (C decreasing)
        # find bracket
        Cd = C.copy()
        for i in range(len(Cd) - 1):
            if Cd[i] >= target >= Cd[i + 1]:
                t0, t1 = tau[i], tau[i + 1]
                c0, c1 = Cd[i], Cd[i + 1]
                if t0 <= 0:
                    t0 = 1e-6
                frac = (c0 - target) / (c0 - c1)
                return np.exp(np.log(t0) + frac * (np.log(t1) - np.log(t0)))
        return np.nan
    tau_half_plateau = tau_at_C(plateau_C * 0.5)
    tau_C04 = tau_at_C(0.4)
    tau_C02 = tau_at_C(0.2)

    results[lv] = dict(
        fast_slope=fast_slope, slow_slope=slow_slope, plateau_C=plateau_C,
        knee_x=knee_x, tau_C04=tau_C04, tau_C02=tau_C02,
        tau_half_plateau=tau_half_plateau,
        tau_max=tau.max(),
    )
    print(f"level {lv}: plateau_C={plateau_C:.3f}  fast_slope={fast_slope:.3f}  "
          f"slow_slope X={slow_slope:.3f}  tau(C=0.4)={tau_C04:.2f}  "
          f"tau(C=0.2)={tau_C02:.1f}  tau_max={tau.max():.0f}")

# ----------------------------------------------------------------------
# Stationarity test: fixed-lag C across ages
# ----------------------------------------------------------------------
print("=" * 78)
print("Fixed-lag C across ages (time-translation-invariance test):")
for fixed_tau in [1.0, 5.0, 20.0, 50.0]:
    vals = []
    for lv in levels:
        d = per[lv]
        c = np.interp(np.log(fixed_tau), np.log(np.maximum(d["tau"], 1e-6)), d["C"])
        vals.append(c)
    print(f"  tau={fixed_tau:6.1f}: " + "  ".join(f"L{lv}={v:.3f}" for lv, v in zip(levels, vals)))

print("=" * 78)
print("Slow-segment slope X across ages:", [f"{results[lv]['slow_slope']:.3f}" for lv in levels])
print("Plateau C across ages:          ", [f"{results[lv]['plateau_C']:.3f}" for lv in levels])
print("tau(C=0.4) across ages:         ", [f"{results[lv]['tau_C04']:.1f}" for lv in levels])

# ----------------------------------------------------------------------
# VIEW
# ----------------------------------------------------------------------
out, STAMP = timestamped_view_path(HERE)

question = ("Glass quenched once, then measured at five increasing ages after the quench. "
            "Does the material KEEP EVOLVING as it ages (relaxes differently at different ages) "
            "or has it reached a FIXED sluggish state that looks the same at every age? And at "
            "each age, is its response in balance with its fluctuations (equilibrium) or out of "
            "balance — and does any imbalance heal as it ages or stay put?")
minimal_structure = ("One material, one scalar, one temperature; five successively longer "
                     "waiting times after a single quench (L0 youngest -> L4 oldest); only the "
                     "wait differs; older windows reach much longer lags.")

Xband = [results[lv]['slow_slope'] for lv in levels]
verdict = (f"KEEPS EVOLVING (aging, non-stationary): the slow relaxation timescale grows "
           f"monotonically with age — tau(C=0.4) climbs ~{results[0]['tau_C04']:.0f} -> "
           f"~{results[4]['tau_C04']:.0f} across L0->L4, and at fixed lag C climbs with age; "
           f"the C(tau) curves SHIFT, they do not collapse. OUT OF BALANCE at every age and the "
           f"imbalance does NOT heal: the FDR locus bends from fast-slope ~1 to a shallow "
           f"slow-segment slope X~{np.mean(Xband):.2f} (<1) at every level, and X stays essentially "
           f"flat across ages (X = {', '.join(f'{x:.2f}' for x in Xband)}). So the sample ages "
           f"(gets slower) but its degree of fluctuation-response imbalance is age-independent.")

grounded = [
    f"keeps-evolving/aging <- slow timescale grows monotonically: tau(C=0.4) = "
    f"{', '.join(f'{results[lv]['tau_C04']:.1f}' for lv in levels)} across L0..L4 (each later age relaxes slower)",
    "non-stationary <- C(tau) curves do NOT collapse; at fixed lag tau, C climbs with age "
    "(e.g. tau=5: " + ", ".join(f"L{lv}={np.interp(np.log(5.0), np.log(np.maximum(per[lv]['tau'],1e-6)), per[lv]['C']):.3f}" for lv in levels) + ")",
    f"two-step relaxation each age <- C shows a fast partial drop to a plateau ~"
    f"{', '.join(f'{results[lv]['plateau_C']:.2f}' for lv in levels)} (rising slightly with age) then a slow tail",
    f"out-of-balance each age <- FDR locus bends: fast-slope ~1 (FDT) then a shallow slow-segment "
    f"slope X<1 (X = {', '.join(f'{results[lv]['slow_slope']:.2f}' for lv in levels)})",
    f"imbalance does NOT heal <- slow-segment slope X is flat across ages (mean {np.mean(Xband):.2f}, "
    f"spread {np.ptp(Xband):.2f}); the FDT-violation amplitude is age-independent",
]
not_grounded = [
    "native waiting times / ages in physical units (tau is the material's own dimensionless clock; no absolute wait or age values given)",
    "the temperature value, the material identity, and how far below any glass transition the sample sits",
    "temperature-dependence of the aging — only ONE temperature was measured, so whether aging rate or X change with T is unknowable here",
    "behaviour past each level's own observation window (older windows reach longer lags; the youngest is not watched out to the oldest's lag, so we cannot confirm L0 would reach the same plateau if waited longer)",
    "whether the slow tail is simple-exponential vs stretched in a fitted sense (curves are consistent with a stretched/slow tail by eye, but no functional form was fitted and the packet gives no parametric model)",
    "an effective temperature value of the slow modes (X<1 implies T_eff>T, but converting X to a numeric T_eff needs the bath temperature, which is withheld)",
    "the microscopic quantity being autocorrelated (single unnamed scalar; no field identity)",
]
placement = (f"5 stitched single-age reads: plateau_C {results[0]['plateau_C']:.2f}->{results[4]['plateau_C']:.2f} (rising); "
             f"fast-slope~1.0 all ages; slow-segment X = {', '.join(f'{results[lv]['slow_slope']:.2f}' for lv in levels)} (flat, <1); "
             f"tau(C=0.4) {results[0]['tau_C04']:.0f}->{results[4]['tau_C04']:.0f} (growing). Band: aging in timescale, age-flat in X.")

fig, axes = figure_with_header(
    n_plots=3, slug="glass_quench_wait_v10", date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement)
ax0, ax1, ax2 = axes

colors = plt.cm.viridis(np.linspace(0, 0.85, len(levels)))

# Box 0: C(tau) overlaid (collapse vs shift)
for lv, c in zip(levels, colors):
    ax0.semilogx(np.maximum(per[lv]["tau"], 1e-3), per[lv]["C"], "-o", ms=2.5,
                 color=c, label=f"age L{lv}")
ax0.set_xlabel("lag tau (material clock)")
ax0.set_ylabel("C(tau)")
ax0.set_title("C(tau) per age — curves SHIFT (no collapse) = aging")
ax0.legend(fontsize=7, loc="upper right")
ax0.grid(alpha=0.3)

# Box 1: FDR locus per level (chi vs 1-C) with bend
for lv, c in zip(levels, colors):
    x = 1.0 - per[lv]["C"]
    ax1.plot(x, per[lv]["chi"], "-o", ms=2.5, color=c, label=f"L{lv}")
xx = np.linspace(0, 1, 50)
ax1.plot(xx, xx, "k--", lw=1, label="FDT slope=1")
ax1.set_xlabel("1 - C(tau)")
ax1.set_ylabel("chi(tau)")
ax1.set_title("FDR locus — bends below slope-1 (out of balance)")
ax1.legend(fontsize=7, loc="upper left")
ax1.grid(alpha=0.3)

# Box 2: BAND — aging trend. Twin axes: timescale (growing) + X (flat).
lv_arr = np.array(levels)
tauC04 = np.array([results[lv]["tau_C04"] for lv in levels])
Xarr = np.array([results[lv]["slow_slope"] for lv in levels])
Cfix = np.array([np.interp(np.log(20.0), np.log(np.maximum(per[lv]["tau"], 1e-6)), per[lv]["C"]) for lv in levels])

ax2.plot(lv_arr, tauC04, "-s", color="#b22222", label="slow timescale tau(C=0.4)")
ax2.set_yscale("log")
ax2.set_xlabel("age (level)")
ax2.set_ylabel("tau(C=0.4)  [grows -> aging]", color="#b22222")
ax2.tick_params(axis="y", labelcolor="#b22222")
ax2.set_xticks(lv_arr)
ax2.set_title("BAND: timescale GROWS with age; X is FLAT")
ax2b = ax2.twinx()
ax2b.plot(lv_arr, Xarr, "-^", color="#00468b", label="slow-segment slope X")
ax2b.plot(lv_arr, Cfix, "-o", color="#0a8000", label="fixed-lag C(tau=20)")
ax2b.axhline(1.0, color="gray", ls=":", lw=1)
ax2b.set_ylabel("X (flat, <1)  /  fixed-lag C (climbs)", color="#00468b")
ax2b.set_ylim(0, 1.05)
ax2b.tick_params(axis="y", labelcolor="#00468b")
lines1, labs1 = ax2.get_legend_handles_labels()
lines2, labs2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labs1 + labs2, fontsize=7, loc="center right")
ax2.grid(alpha=0.3)

fig.savefig(out, dpi=150)
print("=" * 78)
print("VIEW:", out)
