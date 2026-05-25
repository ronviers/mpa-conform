"""Independent per-curve fits for laser_ro_pump_sweep_v2 (blind answerer)."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
import numpy as np
from scipy.optimize import curve_fit

CSV = r"H:\mpa-conform\blockin\workspace\laser_ro_pump_sweep_v2.data.csv"

raw = np.genfromtxt(CSV, delimiter=",", names=True)
curves = {}
for c in (1, 2, 3, 4):
    m = raw["curve"] == c
    tau = raw["tau"][m]
    C = raw["C"][m]
    chi = raw["chi"][m]
    order = np.argsort(tau)
    curves[c] = (tau[order], C[order], chi[order])

# Damped second-order settling model for C(tau).
# Underdamped: C(t) = exp(-zeta*wn*t) * (cos(wd*t) + (zeta*wn/wd)*sin(wd*t)), wd=wn*sqrt(1-zeta^2)
# This is the standard step/impulse settling of a single damped mode, C(0)=1.
def C_underdamped(t, zeta, wn):
    zeta = np.clip(zeta, 1e-6, 0.999999)
    wd = wn * np.sqrt(1.0 - zeta**2)
    return np.exp(-zeta * wn * t) * (np.cos(wd * t) + (zeta * wn / wd) * np.sin(wd * t))

# Overdamped / critically damped form (zeta>=1) using two real roots
def C_overdamped(t, zeta, wn):
    zeta = max(zeta, 1.0 + 1e-9)
    s = wn * np.sqrt(zeta**2 - 1.0)
    r1 = -zeta * wn + s
    r2 = -zeta * wn - s
    # C(0)=1, C'(0)=0 -> A*r1+B*r2=0, A+B=1
    A = -r2 / (r1 - r2)
    B = r1 / (r1 - r2)
    return A * np.exp(r1 * t) + B * np.exp(r2 * t)

def C_model(t, zeta, wn):
    if zeta < 1.0:
        return C_underdamped(t, zeta, wn)
    return C_overdamped(t, zeta, wn)

def fit_curve(tau, C):
    # initial wn guess from decay timescale: time to reach 1/e of |C|
    # crude: use first crossing of C below e^-1 for wn scale
    t_e = tau[np.argmax(C < np.exp(-1))] if np.any(C < np.exp(-1)) else tau[-1]
    wn0 = 1.0 / max(t_e, 1e-6)
    best = None
    for zeta0 in (0.1, 0.3, 0.6, 0.9, 1.2, 2.0):
        try:
            def f(t, zeta, wn):
                return np.array([C_model(ti, zeta, wn) for ti in t])
            popt, _ = curve_fit(f, tau, C, p0=[zeta0, wn0],
                                bounds=([1e-4, 1e-6], [10.0, 10.0]), maxfev=20000)
            resid = f(tau, *popt) - C
            rmse = np.sqrt(np.mean(resid**2))
            if best is None or rmse < best[2]:
                best = (popt[0], popt[1], rmse)
        except Exception:
            continue
    return best

print(f"{'curve':>5} {'zeta':>9} {'wn':>10} {'wd(ring)':>10} {'Q':>8} {'rmse':>10} {'overshoot':>10} {'tau_end':>9}")
results = {}
for c in (1, 2, 3, 4):
    tau, C, chi = curves[c]
    zeta, wn, rmse = fit_curve(tau, C)
    # ring frequency wd: 0 if overdamped (regime-zero, not a kill)
    if zeta < 1.0:
        wd = wn * np.sqrt(1.0 - zeta**2)
    else:
        wd = 0.0
    # Q factor = 1/(2 zeta) for underdamped; report only if ringing
    Q = (1.0 / (2.0 * zeta)) if zeta < 1.0 else 0.0
    # overshoot: peak negative excursion of C (first undershoot below 0), as a positive magnitude
    overshoot = max(0.0, -C.min())
    # response-quality measure: we use damping ratio zeta as the crispness/quality axis
    # zeta ~ 0.7 is the classic "fastest clean settle" optimum; far below = ringy/marginal, far above = sluggish
    results[c] = dict(zeta=zeta, wn=wn, wd=wd, Q=Q, rmse=rmse, overshoot=overshoot,
                      tau_end=tau[-1], chi_inf=chi[-1], C0=C[0])
    print(f"{c:>5} {zeta:>9.4f} {wn:>10.5f} {wd:>10.5f} {Q:>8.3f} {rmse:>10.2e} {overshoot:>10.4f} {tau[-1]:>9.1f}")

# FDR locus cross-check: chi vs C(0)-C(tau). For a single FDR-respecting mode chi ~ (C0 - C)*scale.
print("\nFDR locus cross-check (chi vs C0-C(tau)) — slope & linearity R^2:")
for c in (1, 2, 3, 4):
    tau, C, chi = curves[c]
    x = C[0] - C
    # fit chi = k * x through origin
    k = np.sum(x * chi) / np.sum(x * x)
    pred = k * x
    ss_res = np.sum((chi - pred)**2)
    ss_tot = np.sum((chi - chi.mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    print(f"  curve {c}: slope k={k:.4f}  R^2={r2:.5f}")

# band readout: zeta along ordered curve index
print("\nBAND (zeta along drive axis 1->4):", [round(results[c]['zeta'], 4) for c in (1,2,3,4)])
print("BAND (ring wd 1->4):", [round(results[c]['wd'], 5) for c in (1,2,3,4)])
print("settling time tau_end 1->4:", [round(results[c]['tau_end'], 1) for c in (1,2,3,4)])

import json
with open(r"H:\mpa-conform\blockin\workspace\_fit_results.json", "w") as f:
    json.dump({str(c): results[c] for c in (1,2,3,4)}, f, indent=2)
print("\nwrote _fit_results.json")
