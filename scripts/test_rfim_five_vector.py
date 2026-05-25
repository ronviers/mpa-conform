"""Real-substrate rung on the 5-vector control ladder: driven-critical RFIM.

Feeds the three trajectories from `rfim_fdr_driven.py` (the trusted self-overlap
gFDR apparatus whose equilibrium control reads X=1.00) into `fit_kww5` and renders
the parametric (dC vs T*chi) overlay with recovered X, residual, and the
domain-gate verdict per condition.

Prediction (blockin + FALSIFICATION raw-slope reading):
  equilibrium    -> in-family anchor, X~1, IN
  driven-critical-> T*chi TURNS OVER (rises then falls) -> not in the monotone
                    KWW-FDT family -> should gate OUT (real-substrate analog of
                    the driven_ring NESS). Its raw-slope X=0.12 is a real
                    initial-slope, NOT a KWW-FDT-violation X.
  driven-noncrit -> open; read off the plot.

rfim has no declared tau_env (camera-scale not placed - the substrate-inversion
gap). We use raw sweep-lag as the dimensionless tau; X and the gate are read from
the (dC, T*chi) parametric relation, which is invariant to that scaling (the fit
has free tau_alpha/tau_beta to absorb the lag axis).

Run: python H:/mpa-conform/scripts/test_rfim_five_vector.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, "H:/mpa-conform")
sys.path.insert(0, "H:/mpa-central/library")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from rfim_fdr_driven import run_overlap
from conformer.compute import five_vector, gfdr_model

CACHE = Path("H:/mpa-conform/output/diagnostics/rfim_trajectories.npz")
OUT = Path("H:/mpa-conform/output/diagnostics/rfim_five_vector.png")

N, N_REAL, T_W, N_WINDOW, EPS = 400, 300, 800, 800, 0.05


def conds():
    R_c = float(np.sqrt(2.0 / np.pi))
    half = 0.3
    v = 2.0 * half / N_WINDOW                 # sweep +-half through H_c=0
    H0_drv = -half - T_W * v
    return {
        "equilibrium (control)":  dict(R=0.5,  T=2.0, v_H=0.0, H0=0.0,    seed=11),
        "driven-critical (TEST)": dict(R=R_c,  T=0.3, v_H=v,   H0=H0_drv, seed=21),
        "driven-noncritical":     dict(R=2.0,  T=0.3, v_H=v,   H0=H0_drv, seed=31),
    }


def gather():
    """Run the three rfim conditions once; cache the (x=dC, y=T*chi) trajectories."""
    if CACHE.exists():
        d = np.load(CACHE, allow_pickle=True)
        return [(str(n), np.asarray(x, float), np.asarray(y, float), float(t), float(g))
                for n, x, y, t, g in zip(d["names"], d["xs"], d["ys"], d["Ts"], d["Xgs"])]
    import time
    out, names, xs, ys, Ts, Xgs = [], [], [], [], [], []
    for name, kw in conds().items():
        t0 = time.time()
        x, y, Xg = run_overlap(N=N, N_real=N_REAL, t_w=T_W, n_window=N_WINDOW, eps=EPS, **kw)
        print(f"  {name:>24}: raw-slope X = {Xg:.3f}   ({time.time()-t0:.0f}s)", flush=True)
        out.append((name, x, y, kw["T"], Xg))
        names.append(name); xs.append(x); ys.append(y); Ts.append(kw["T"]); Xgs.append(Xg)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE, names=np.array(names, dtype=object), xs=np.array(xs, dtype=object),
             ys=np.array(ys, dtype=object), Ts=np.array(Ts), Xgs=np.array(Xgs))
    return out


def fit_one(x, y, T):
    """x = C(0)-C(tau) = dC; y = T*chi. Build rows in the fitter's units and fit."""
    C = 1.0 - x
    chi = y / T
    tau = np.arange(len(x), dtype=float)        # raw sweep-lag (no tau_env declared)
    rows = [{"tau": float(t), "C": float(c), "chi": float(ch)}
            for t, c, ch in zip(tau, C, chi)]
    return five_vector.fit_kww5(rows, T=T)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    traj = gather()
    col = {"equilibrium (control)": "C2", "driven-critical (TEST)": "C3",
           "driven-noncritical": "C0"}

    fits = {}
    print("\n===== 5-vector fit on rfim trajectories =====")
    for name, x, y, T, Xg in traj:
        f = fit_one(x, y, T)
        fits[name] = f
        gate = "IN " if f.in_domain else "OUT"
        print(f"  {name:<24} [{gate}] X_raw={Xg:5.2f} X_fit={f.X:5.3f} "
              f"q_EA={f.q_EA:5.3f} b={f.beta_KWW:5.3f} | resid={f.residual:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7.2))
    axL, axR = axes

    # Left: parametric dC vs T*chi (mirrors the trusted rfim_fdr_driven.png axes)
    xm = 0.0
    for name, x, y, T, Xg in traj:
        f = fits[name]
        c = col[name]
        axL.plot(x, y, "o", ms=3, color=c, alpha=0.55)
        loc = gfdr_model.generate_kww_glass_locus(
            f.chit, q_EA=f.q_EA, tau_alpha=f.tau_alpha, beta_KWW=f.beta_KWW,
            tau_beta=f.tau_beta, X=f.X, T=f.T)
        dC_m = 1.0 - loc["C"]; Tchi_m = f.T * loc["chi"]
        order = np.argsort(dC_m)
        gate = "IN" if f.in_domain else "OUT"
        axL.plot(dC_m[order], Tchi_m[order], "-", color=c, lw=2,
                 label=f"{name}: X_raw={Xg:.2f} | fit X={f.X:.2f} resid={f.residual:.3f} [{gate}]")
        xm = max(xm, float(np.nanmax(x)))
    xl = np.linspace(0, xm, 50)
    axL.plot(xl, xl, "k--", lw=1.2, label="FDT line X=1")
    axL.set_xlabel("C(0) - C(tau)   [self-overlap]")
    axL.set_ylabel("T*chi(tau)   [staggered]")
    axL.set_title("rfim trajectories vs fitted KWW-FDT locus")
    axL.legend(loc="upper left", fontsize=8); axL.grid(alpha=0.3)

    # Right: residual vs the domain gate (the in/out story)
    names = [n for n, *_ in traj]
    resids = [fits[n].residual for n in names]
    bars = axR.bar(range(len(names)), resids,
                   color=[col[n] for n in names], alpha=0.8)
    axR.axhline(five_vector.RESIDUAL_GATE, color="k", ls="--", lw=1.5,
                label=f"RESIDUAL_GATE = {five_vector.RESIDUAL_GATE}")
    for i, n in enumerate(names):
        f = fits[n]
        axR.text(i, resids[i] + 0.005, "IN" if f.in_domain else "OUT",
                 ha="center", va="bottom", fontweight="bold")
    axR.set_xticks(range(len(names)))
    axR.set_xticklabels([n.replace(" ", "\n") for n in names], fontsize=8)
    axR.set_ylabel("fit RMS residual")
    axR.set_title("domain-of-validity gate")
    axR.legend(fontsize=9); axR.grid(alpha=0.3, axis="y")

    fig.suptitle("Real-substrate rung: driven-critical RFIM through the 5-vector inversion",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
