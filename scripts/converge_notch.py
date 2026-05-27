"""converge_notch.py -- dt-convergence study at the aging notch.

Per mpa_units.md sec 4: a near-threshold value must be REFINEMENT-INVARIANT
(stable under halving dt, to a stated tolerance) before it counts -- curing
NaNs is necessary, not sufficient. Hold chit_ch=0.2 (the notch), gamma=0;
sweep dt; watch X(dt). Does the aging dip converge to a real value, or keep
drifting?

Also reports the unit's dt wall (sec 4): dt_max = 1/(k * lambda_fast), k=10,
from the linearized deterministic fixed point -- where the integrator should
start trusting itself. If X has plateaued by dt_max/2, the value is real; if it
is still moving below dt_max, the clamp (np.maximum(rho,0)) is the suspect.

chit is in ch (character bit) = chit/ln2, per the renamed unit.

Run from repo root:  python scripts/converge_notch.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
for p in (str(REPO_ROOT), str(SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conformer.compute.kernel import from_chit_gamma, integrate_deterministic, linearize
from conformer.compute.observables import gfdr_locus
from one_ball import read_X  # noqa: E402

LN2 = float(np.log(2.0))
CHIT_CH = 0.2
GAMMA = 0.0
CHIT = CHIT_CH * LN2
DTS = [0.02, 0.01, 0.005, 0.0025, 0.00125]
SEEDS = range(8)
TWO_THIRDS, THREE_QUARTERS = 2.0 / 3.0, 3.0 / 4.0


def dt_wall() -> tuple[float, float, float]:
    """dt_max from the linearized deterministic fixed point (mpa_units sec 4)."""
    p = from_chit_gamma(CHIT, GAMMA)
    fp = integrate_deterministic((0.3, 0.7), p, t_max=120.0, dt=0.005)
    state = (float(fp["rho_A"][-1]), float(fp["rho_B"][-1]))
    lin = linearize(state, p)
    mags = [abs(complex(e["re"], e["im"])) for e in lin["eigenvalues"]]
    lam_fast = max(mags) if mags else 0.0
    lam_slow = min(mags) if mags else 0.0
    dtmax = (1.0 / (10.0 * lam_fast)) if lam_fast > 0 else float("inf")
    return dtmax, lam_fast, lam_slow


def x_at(dt: float, seed: int) -> float | None:
    # Hold the PHYSICAL windows fixed while varying dt alone: equilibration and
    # n_tau are in samples, so scale them by 1/dt to keep equilibration TIME and
    # lag window constant. Otherwise refining dt silently shrinks both and the
    # FDR read drifts for a non-numerical reason. t_max is already in time.
    t_equil, tau_max = 3.0, 15.0   # the dt=0.01 reference windows, in time
    equil = max(1, round(t_equil / dt))
    ntau = max(2, round(tau_max / dt))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loc = gfdr_locus(CHIT, GAMMA, seed=seed, dt=dt, equilibration=equil, n_tau=ntau)
    X, _ = read_X(1.0 - loc["C"], loc["chi"])
    return X


def main() -> None:
    dtmax, lam_fast, lam_slow = dt_wall()

    means, stds, ns = [], [], []
    for dt in DTS:
        xs: list[float] = []
        ndiv = 0
        for s in SEEDS:
            try:
                X = x_at(dt, s)
            except RuntimeError:
                ndiv += 1
                continue
            if X is not None and np.isfinite(X):
                xs.append(X)
        means.append(float(np.mean(xs)) if xs else np.nan)
        stds.append(float(np.std(xs)) if xs else np.nan)
        ns.append(len(xs))
        print(f"  dt={dt:<8g} meanX={means[-1]:.3f}  std={stds[-1]:.3f}  n={ns[-1]}  diverged={ndiv}  "
              f"dt*lam_fast={dt*lam_fast:.3f}")

    means_a, stds_a = np.array(means), np.array(stds)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=170)
    ax.axhline(THREE_QUARTERS, ls=":", color="#666", lw=1, label="3/4")
    ax.axhline(TWO_THIRDS, ls=":", color="#999", lw=1, label="2/3")
    ax.axvline(dtmax, ls="--", color="#2b6cb0", lw=1.2, label=f"dt_max={dtmax:.3g} (k=10)")
    ax.axvline(dtmax / 2, ls=":", color="#2b6cb0", lw=1, alpha=0.6, label="dt_max/2 (target)")
    fin = np.isfinite(means_a)
    ax.errorbar(np.array(DTS)[fin], means_a[fin], yerr=stds_a[fin],
                fmt="o-", color="#dd8b1a", ecolor="#888", capsize=3, lw=1.6, ms=5,
                label="single-slope X (biases up)")
    ax.set_xscale("log")
    ax.set_xlabel("dt  (smaller ->)")
    ax.set_ylabel("X  (FDR ratio, single-slope)")
    ax.set_ylim(0.0, 1.0)
    ax.invert_xaxis()
    ax.set_title(f"convergence at the notch: chit_ch={CHIT_CH}, gamma=0 -- X(dt), {len(list(SEEDS))} seeds")
    ax.legend(loc="upper right", fontsize=9, frameon=False)

    out = REPO_ROOT / "output" / "one_ball" / f"converge_notch_chit{CHIT_CH}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    # verdict: change between the two finest dt
    fin_idx = [i for i in range(len(DTS)) if np.isfinite(means[i])]
    print(f"\n  dt wall: lam_fast={lam_fast:.3f}, lam_slow={lam_slow:.3f}, dt_max={dtmax:.4g}")
    if len(fin_idx) >= 2:
        i1, i2 = fin_idx[-2], fin_idx[-1]
        drift = abs(means[i2] - means[i1])
        print(f"  finest two dt ({DTS[i1]} -> {DTS[i2]}): X {means[i1]:.3f} -> {means[i2]:.3f}, drift={drift:.3f}")
        verdict = "CONVERGED (refinement-invariant)" if drift < 0.02 else "STILL DRIFTING (not yet refinement-invariant)"
        print(f"  verdict: {verdict}")
    print(f"\n  plot: {out}")


if __name__ == "__main__":
    main()
