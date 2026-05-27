"""selfsat_check.py -- fork (b) keystone: does the self-saturating kernel HOLD?

The shared kernel depletes mode A's gain only by mode B:
    G0_A_eff = G0 / (1 + rho_B / rho_sat)
so a lone surviving mode (rho_B->0) sees G0_eff->G0>1 and runs away. That is
why nothing held above threshold (winner-take-all -> unbounded).

Self-saturating variant (contained here; shared kernel.py untouched, it has a
bit-preservation gate): gain depleted by TOTAL density,
    G0_A_eff = G0 / (1 + (rho_A + rho_B) / rho_sat)
so a lone mode self-saturates to a bounded fixed point rho = G0 - 1, and the
symmetric coexistence sits at rho = (G0 - 1)/2. Either way: BOUNDED. No runaway.

This script only asks the keystone question -- does it settle to a bounded NESS
above threshold, from an asymmetric IC? -- before any FDR read is built on it.

Run from repo root:  python scripts/selfsat_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

LN2 = float(np.log(2.0))
L = 1.0
RHO_SAT = 1.0


def drift_selfsat(state: np.ndarray, G0: float, gamma: float) -> np.ndarray:
    a, b = state[..., 0], state[..., 1]
    tot = (a + b) / RHO_SAT
    g_eff = G0 / (1.0 + tot)          # SELF + cross: both modes see total density
    cross = gamma * a * b
    da = (g_eff - L) * a - cross
    db = (g_eff - L) * b - cross
    return np.stack([da, db], axis=-1)


def integrate(ic, G0, gamma, t_max=120.0, dt=0.01):
    n = int(round(t_max / dt))
    s = np.array(ic, dtype=np.float64)
    ts, A, B = [], [], []
    for k in range(n + 1):
        ts.append(k * dt); A.append(s[0]); B.append(s[1])
        k1 = drift_selfsat(s, G0, gamma)
        k2 = drift_selfsat(s + 0.5 * dt * k1, G0, gamma)
        k3 = drift_selfsat(s + 0.5 * dt * k2, G0, gamma)
        k4 = drift_selfsat(s + dt * k3, G0, gamma)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.array(ts), np.array(A), np.array(B)


def linearize(state, G0, gamma, eps=1e-6):
    s = np.array(state, float)
    f0 = drift_selfsat(s, G0, gamma)
    J = np.zeros((2, 2))
    for j in range(2):
        sp = s.copy(); sp[j] += eps
        J[:, j] = (drift_selfsat(sp, G0, gamma) - f0) / eps
    return np.linalg.eigvals(J)


def main() -> None:
    gamma = 0.0
    chit_chs = [0.5, 1.0, 2.0]
    ic = (0.3, 0.7)

    fig, axes = plt.subplots(1, len(chit_chs), figsize=(14, 4.5), dpi=170)
    print(f"self-saturating kernel, gamma={gamma}, IC={ic}")
    print(f"{'chit_ch':>7} {'G0':>6} {'rho_A*':>8} {'rho_B*':>8} {'sym FP':>7} {'1mode FP':>8} "
          f"{'max Re(eig)':>11} {'bounded':>7}")

    for ax, cb in zip(axes, chit_chs):
        G0 = 2.0 ** cb  # G0 = exp(chit) = exp(chit_ch*ln2) = 2**chit_ch
        ts, A, B = integrate(ic, G0, gamma)
        fa, fb = A[-1], B[-1]
        sym_fp = (G0 - 1.0) / 2.0
        one_fp = G0 - 1.0
        eig = linearize((fa, fb), G0, gamma)
        max_re = float(np.max(eig.real))
        bounded = np.isfinite(fa) and np.isfinite(fb) and abs(fa) < 1e3 and abs(fb) < 1e3

        ax.plot(ts, A, color="#2b6cb0", lw=1.8, label="rho_A")
        ax.plot(ts, B, color="#dd8b1a", lw=1.8, label="rho_B")
        ax.axhline(sym_fp, ls=":", color="#2f855a", lw=1, label=f"sym FP={sym_fp:.3g}")
        ax.axhline(one_fp, ls="--", color="#c53030", lw=1, alpha=0.6, label=f"1-mode FP={one_fp:.3g}")
        ax.set_xlabel("t"); ax.set_title(f"chit_ch={cb:g}  (G0={G0:.3g})")
        if ax is axes[0]:
            ax.set_ylabel("rho")
        ax.legend(fontsize=8, frameon=False, loc="center right")

        print(f"{cb:7g} {G0:6.3f} {fa:8.4f} {fb:8.4f} {sym_fp:7.3f} {one_fp:8.3f} "
              f"{max_re:11.4f} {str(bounded):>7}")

    fig.suptitle("fork (b): self-saturating kernel -- does it HOLD above threshold? "
                 "(bounded settle = yes)", fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = REPO_ROOT / "output" / "selfsat" / "selfsat_hold_check.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")

    # Does gamma != 0 break the marginal degeneracy into a proper stable FP?
    print("\ngamma sweep at chit_ch=1 (G0=2): is the held state a PROPER stable FP?")
    print(f"{'gamma':>6} {'rho_A*':>8} {'rho_B*':>8} {'max Re(eig)':>11} {'verdict':>22}")
    G0 = 2.0
    for g in (-0.5, -0.3, -0.1, 0.1, 0.3, 0.5):
        _, A, B = integrate(ic, G0, g)
        fa, fb = A[-1], B[-1]
        bounded = np.isfinite(fa) and np.isfinite(fb) and abs(fa) < 1e3 and abs(fb) < 1e3
        if not bounded:
            print(f"{g:6.2f} {'--':>8} {'--':>8} {'--':>11} {'runaway':>22}")
            continue
        max_re = float(np.max(linearize((fa, fb), G0, g).real))
        if max_re < -1e-4:
            verdict = "STABLE (proper hold)"
        elif max_re > 1e-4:
            verdict = "unstable"
        else:
            verdict = "marginal"
        print(f"{g:6.2f} {fa:8.4f} {fb:8.4f} {max_re:11.4f} {verdict:>22}")


if __name__ == "__main__":
    main()
