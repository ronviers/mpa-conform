"""Pipeline regression: does the full curator->bundle path leave the fit alone?

Compares the 5-vector fit + per-channel gate on glass T1.3 across three feeds:

  A  reference   : library cell all_samples, tau = dt / tau_env       (what the
                   standalone ladder used)
  B  bundle naive: bundle observable.data, tau as-stored (raw native lag) -- the
                   trap if a consumer feeds bundle tau straight to the fitter
  B' bundle right: bundle observable.data, tau / tau_scale (read from the bundle's
                   preprocessing_log, exactly as banach_overlay does)

"Leaves it alone / does not make it worse" == B' reproduces A (verdict, S/N,
params). Also confirms the grain (C_sem/chi_sem) survives into the bundle.

Run: python H:/mpa-conform/scripts/test_pipeline_regression.py
"""
from __future__ import annotations
import sys, json
sys.path.insert(0, "H:/mpa-conform")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from conformer.compute import five_vector

CELL = "H:/mpa-central/library/data/glass/glass__T1.300__spin-flip.json"
BUNDLE = "H:/mpa-conform/output/seed-corpus/ck-glassy/glass__T1.300__spin-flip.bundle.json"
T = 1.0


def rows_from_cell(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]
    return rows, scale


def bundle_tau_scale(b):
    """Mirror banach_overlay: tau_scale lives in a preprocessing_log entry's parameters."""
    for entry in (b["observable"].get("preprocessing_log") or []):
        ts = (entry.get("parameters") or {}).get("tau_scale")
        if ts:
            return float(ts)
    return None


def rows_from_bundle(path, divide_by_scale):
    b = json.load(open(path))
    data = b["observable"]["data"]
    scale = bundle_tau_scale(b) if divide_by_scale else 1.0
    scale = scale or 1.0
    grain = b["observable"].get("uncertainty_reported")
    rows = [{"tau": float(d["tau"]) / scale, "C": float(d["C"]), "chi": float(d["chi"]),
             "C_sem": float(d.get("C_sem", 0.0)), "chi_sem": float(d.get("chi_sem", 0.0))}
            for d in data]
    return rows, scale, grain


def report(tag, rows):
    f = five_vector.fit_kww5(rows, T=T)
    sX = "inf" if not np.isfinite(f.channel_snr["chi"]) else f"{f.channel_snr['chi']:.2f}"
    gate = "IN " if f.in_domain else "OUT"
    print(f"  {tag:<26} [{gate}]  C S/N={f.channel_snr['C']:6.2f}  chi S/N={sX:>6}  "
          f"X={f.X:.3f} q_EA={f.q_EA:.3f} t_a={f.tau_alpha:.3f} | resid={f.residual:.4f}")
    return f


def main():
    print("===== pipeline regression: glass T1.3 =====\n")
    rA, scaleA = rows_from_cell(CELL)
    rBn, _, grain = rows_from_bundle(BUNDLE, divide_by_scale=False)
    rBc, scaleB, _ = rows_from_bundle(BUNDLE, divide_by_scale=True)

    print(f"grain preserved in bundle (uncertainty_reported): {grain}")
    print(f"cell tau_env scale = {scaleA:.3f}   |   bundle logged tau_scale = {scaleB:.3f}")
    print(f"cell tau[0]={rA[0]['tau']:.5f}  bundle-naive tau[0]={rBn[0]['tau']:.5f}  "
          f"bundle-corrected tau[0]={rBc[0]['tau']:.5f}\n")

    fA = report("A  cell (reference)", rA)
    fBn = report("B  bundle naive (raw tau)", rBn)
    fBc = report("B' bundle corrected (/scale)", rBc)

    print("\n----- verdict -----")
    print(f"  A  reference        : {'IN' if fA.in_domain else 'OUT'}")
    print(f"  B' bundle-corrected : {'IN' if fBc.in_domain else 'OUT'}  "
          f"-> {'LEAVES IT ALONE' if fBc.in_domain == fA.in_domain else '** PIPELINE CHANGED THE VERDICT **'}")
    print(f"  B  bundle-naive     : {'IN' if fBn.in_domain else 'OUT'}  "
          f"-> {'(matches)' if fBn.in_domain == fA.in_domain else '** raw-tau feed diverges (the trap) **'}")
    # numeric closeness A vs B'
    dC = abs(fA.channel_snr["C"] - fBc.channel_snr["C"])
    print(f"\n  |C S/N (A) - C S/N (B')| = {dC:.3f}  "
          f"({'within rounding' if dC < 0.2 else 'DIVERGENT'})")


if __name__ == "__main__":
    main()
