"""Validation harness for the 5-vector inversion (fit_kww5).

Runs the fitter against the control ladder and reports recovered vs prescribed:
  two_temp_ou : pure-exp C -> X-recovery only (q_EA/timescales unidentifiable).
  kww_oracle  : genuine two-timescale C -> FULL 5-vector must round-trip.
  sine_wave   : out-of-domain (cosine, not KWW) -> residual must stay HIGH (domain gate).

Run: python H:/mpa-conform/scripts/test_five_vector_fit.py
"""
from __future__ import annotations
import sys, json, glob
sys.path.insert(0, "H:/mpa-conform")
import numpy as np
from conformer.compute import five_vector

DATA = "H:/mpa-central/library/data"
# kww_oracle/grind.py truth in STEP units: q_EA=0.7, tau_alpha=20, beta=0.6, tau_beta=1.0.
# Rows use dimensionless lag = dt/scale with scale = tau_env = tau_alpha = 20, so the
# fit returns tau in those units: tau_alpha -> 20/20 = 1.0, tau_beta -> 1/20 = 0.05.
KWW_TRUTH = dict(q_EA=0.7, tau_alpha=1.0, beta_KWW=0.6, tau_beta=0.05)


def rows_for(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"]} for e in s]
    return rows, c.get("operating_point", {})


def show(tag, path, want=None, **fit_kw):
    rows, op = rows_for(path)
    try:
        f = five_vector.fit_kww5(rows, **fit_kw)
    except Exception as e:
        print(f"  {tag:<34} FIT FAILED: {type(e).__name__}: {e}")
        return None
    gate = "IN " if f.in_domain else "OUT"
    line = (f"  {tag:<22} [{gate}] X={f.X:5.3f} q_EA={f.q_EA:5.3f} t_a={f.tau_alpha:6.3f} "
            f"b={f.beta_KWW:5.3f} t_b={f.tau_beta:6.3f} | resid={f.residual:.4f}")
    if want:
        errs = {k: abs(getattr(f, k) - v) for k, v in want.items()}
        line += "  | err " + " ".join(f"{k}={errs[k]:.3f}" for k in want)
    print(line)
    return f


def main():
    print("two_temp_ou (X-recovery only; want X=0.5,0.1):")
    for X in ("0.5", "0.1"):
        g = glob.glob(f"{DATA}/two_temp_ou/two_temp_ou__X{X}__velocity.json")
        if g: show(f"X{X}", g[0], want={"X": float(X)}, T=1.0)

    print("\nkww_oracle (FULL 5-vector round-trip; truth q_EA=0.7,t_a=20,b=0.6,t_b=1.0):")
    for X in ("1", "0.5", "0.2"):
        g = glob.glob(f"{DATA}/kww_oracle/kww_oracle__X{X}__velocity.json")
        if g: show(f"X{X}", g[0], want={**KWW_TRUTH, "X": float(X)}, T=1.0)

    print("\nsine_wave (OUT OF DOMAIN; residual should be HIGH):")
    for g in sorted(glob.glob(f"{DATA}/sine_wave/sine_wave__P*__velocity.json"))[:2]:
        show(g.split("__")[1], g, T=1.0)

    print("\ncross-substrate (the session's X-trouble cases; does fit+gate sort them?):")
    # NOTE: aging glass (T<Tc, gt=s) has NULL tau_env in the current library (known gap;
    # camera-scale not placed) -> proper X-recovery there waits on the curator's v0.4
    # lag-anchored extraction + library refresh. T=1.3 (gt=r, above Tc) HAS tau_env.
    g = glob.glob(f"{DATA}/glass/glass__T1.300__spin-flip.json")
    if g: show("glass T=1.3 (r-regime, IN?)", g[0], T=1.0)    # r-regime: expect IN, X~1
    for F in ("1.5", "3.0"):                                  # running NESS: expect OUT (not KWW family)
        g = glob.glob(f"{DATA}/driven_ring/driven_ring__F{F}__velocity.json")
        if g: show(f"driven_ring F{F} (running)", g[0], T=0.5)


if __name__ == "__main__":
    main()
