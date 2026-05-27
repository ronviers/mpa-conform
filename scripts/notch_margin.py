"""notch_margin.py -- resolve the notch at adequate margin (mpa_units sec 4).

The corrected convergence study showed the notch (chit_ch=0.2, gamma=0) does not
yield a clean X: most seeds diverge (out-of-sane-bounds response). Diagnosis: the
near-threshold fixed point rho* ~ 0.149 sits at margin m = rho*/noise ~ 1.5
against noise_scale=sqrt(d_noise)=0.1 -- far below the units standard m>=10.

FDR X is a RATIO: in the linear-response regime it is noise-independent. So hold
dt fixed, lower d_noise (raise m past 10), and watch:
  - does the divergence clear as m climbs?
  - does X PLATEAU at a real value (=> that is the true notch X), or keep
    drifting with noise (=> the clamp is breaking linearity, clamp replacement
    is then warranted)?

Physical windows held fixed (t_equil=3, tau_max=15), per the convergence fix.

Run from repo root:  python scripts/notch_margin.py
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

from conformer.compute.kernel import from_chit_gamma, integrate_deterministic
from conformer.compute.observables import gfdr_locus
from one_ball import read_X  # noqa: E402

LN2 = float(np.log(2.0))
CHIT_CH = 0.2
GAMMA = 0.0
CHIT = CHIT_CH * LN2
DT = 0.005
SEEDS = range(8)
D_NOISES = [0.01, 0.003, 0.001, 0.0003, 0.0001]
TWO_THIRDS, THREE_QUARTERS = 2.0 / 3.0, 3.0 / 4.0


def rho_star() -> float:
    p = from_chit_gamma(CHIT, GAMMA)
    fp = integrate_deterministic((0.3, 0.7), p, t_max=120.0, dt=0.005)
    return float(fp["rho_A"][-1])


def x_at(d_noise: float, seed: int) -> float | None:
    equil = max(1, round(3.0 / DT))
    ntau = max(2, round(15.0 / DT))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loc = gfdr_locus(CHIT, GAMMA, seed=seed, dt=DT, equilibration=equil,
                         n_tau=ntau, d_noise=d_noise)
    X, _ = read_X(1.0 - loc["C"], loc["chi"])
    return X


def main() -> None:
    rs = rho_star()
    margins, means, stds, ns = [], [], [], []
    for dn in D_NOISES:
        noise_scale = float(np.sqrt(dn))
        m = rs / noise_scale
        margins.append(m)
        xs: list[float] = []
        ndiv = 0
        for s in SEEDS:
            try:
                X = x_at(dn, s)
            except RuntimeError:
                ndiv += 1
                continue
            if X is not None and np.isfinite(X):
                xs.append(X)
        means.append(float(np.mean(xs)) if xs else np.nan)
        stds.append(float(np.std(xs)) if xs else np.nan)
        ns.append(len(xs))
        print(f"  d_noise={dn:<8g} noise={noise_scale:.4f}  m={m:5.1f}  "
              f"meanX={means[-1]:.3f}  std={stds[-1]:.3f}  n={ns[-1]}  diverged={ndiv}")

    margins_a, means_a, stds_a = np.array(margins), np.array(means), np.array(stds)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=170)
    ax.axhline(THREE_QUARTERS, ls=":", color="#666", lw=1, label="3/4")
    ax.axhline(TWO_THIRDS, ls=":", color="#999", lw=1, label="2/3")
    ax.axvline(10.0, ls="--", color="#2b6cb0", lw=1.2, label="m=10 (units standard)")
    fin = np.isfinite(means_a)
    ax.errorbar(margins_a[fin], means_a[fin], yerr=stds_a[fin],
                fmt="o-", color="#dd8b1a", ecolor="#888", capsize=3, lw=1.6, ms=5,
                label="single-slope X (biases up)")
    ax.set_xscale("log")
    ax.set_xlabel("margin  m = rho* / noise   (higher = better resolved ->)")
    ax.set_ylabel("X  (FDR ratio, single-slope)")
    ax.set_ylim(0.0, 1.0)
    ax.set_title(f"notch at adequate margin: chit_ch={CHIT_CH}, gamma=0, dt={DT}, rho*={rs:.3f}")
    ax.legend(loc="upper left", fontsize=9, frameon=False)

    out = REPO_ROOT / "output" / "one_ball" / f"notch_margin_chit{CHIT_CH}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    print(f"\n  rho* = {rs:.4f}")
    hi = [i for i in range(len(D_NOISES)) if margins[i] >= 10 and np.isfinite(means[i])]
    if len(hi) >= 2:
        drift = abs(means[hi[-1]] - means[hi[-2]])
        print(f"  at m>=10: X drift between the two highest-margin points = {drift:.3f}"
              f"  ({'PLATEAU (real X)' if drift < 0.03 else 'still drifting (clamp suspect)'})")
    elif len(hi) == 1:
        print(f"  only one point at m>=10 (X={means[hi[0]]:.3f}); push noise lower to confirm plateau")
    else:
        print("  no points reached m>=10; extend the noise sweep down")
    print(f"\n  plot: {out}")


if __name__ == "__main__":
    main()
