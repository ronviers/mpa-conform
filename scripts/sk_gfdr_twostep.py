r"""sk_gfdr_twostep.py -- real-substrate instance for `staked:gfdr-two-step`.

Sherrington-Kirkpatrick spin glass (an EMERGENT/non-authored substrate -> vindication-grade) read
through the FLUCTUATION-DISSIPATION (FDT) plot at the raw-slope layer (NOT the conform pipeline, NOT
the 1-param inversion; per the falsification ledger).

THE CLAIM (`staked:gfdr-two-step`): the s-regime FDR is TWO-STEP -- quasi-equilibrium X=1 on short
lags, FDR-violated aging (X<1) on long lags. A short-lag X=1 alone does NOT place a substrate in r;
the long-lag aging segment is the c/s/r discriminator.

APPARATUS NOTE (a real finding). The in-library `sk` primitive's generic FDR protocol applies a
UNIFORM field but reads the SELF-OVERLAP C. Those are not FDT-conjugate -- a uniform-field response
pairs with the magnetization autocorrelation, not the self-overlap -- so the paramagnet's T*chi
overshoots 1 and the slopes are wrong. The established spin-glass method is the STAGGERED-FIELD
estimator: a frozen random eps_i = +-1 field with chi projected onto the same pattern; then
T*chi = 1 - C in equilibrium and the two-step is clean. This script reimplements SK with that
estimator (identical physics: N=100 Glauber, J ~ N(0, 1/sqrt(N)), Tc=1; only the FDT geometry fixed).

READOUT (Cugliandolo-Kurchan): the parametric T*chi-vs-C plot at fixed waiting time t_w.
  equilibrium FDT:  T*chi = 1 - C       (slope -1; X = -d(T*chi)/dC = 1)
  aging glass:      slope -1 for C > q_EA (fast, X=1), BREAK at q_EA, shallower slope -X for C < q_EA.

  T=0.4 (c): slow intra-valley decay -> the X=1 branch is resolvable; strong aging.
  T=0.7 (s): the two-step.
  T=1.3 (r): paramagnet -- CALIBRATION (must read X=1 throughout, no break) + the point (short-lag
        X=1 is shared by s and r; only s ages).

Usage:  python scripts/sk_gfdr_twostep.py [quick]
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
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)
TC, N = 1.0, 100
QUICK = len(sys.argv) > 1 and sys.argv[1] == "quick"

BIG = len(sys.argv) > 1 and sys.argv[1] == "big"
DEEP = len(sys.argv) > 1 and sys.argv[1] == "deep"
TEMPS = [(0.4, "c / deep frozen", "c"), (0.7, "s / aging-RSB", "s"), (1.3, "r / paramagnet", "r")]
if QUICK:
    T_W, T_OBS, N_REAL, N_SAMPLES, H = 1000, 2400, 120, 30, 0.02
elif BIG:
    T_W, T_OBS, N_REAL, N_SAMPLES, H = 1000, 2400, 10000, 34, 0.05
elif DEEP:                                  # deep aging: lower T, large t_w (calibrated apparatus)
    TEMPS = [(0.3, "deep frozen", "c"), (0.5, "aging", "s"), (1.3, "r / paramagnet", "r")]
    T_W, T_OBS, N_REAL, N_SAMPLES, H = 6000, 18000, 3000, 44, 0.05
else:
    T_W, T_OBS, N_REAL, N_SAMPLES, H = 2500, 10000, 300, 40, 0.05


def _sweep(s_unp, s_per, J, beta, field_per, idx, u):
    """one Glauber sweep of both branches with COMMON random numbers (idx, u shared)."""
    n_real, Nn = s_unp.shape
    row = np.arange(n_real)
    for step in range(Nn):
        i = idx[step]
        Ji = J[row, i, :]                              # (n_real, N)
        h_unp = np.einsum("rj,rj->r", Ji, s_unp)
        h_per = np.einsum("rj,rj->r", Ji, s_per) + field_per[row, i]
        us = u[step]
        s_unp[row, i] = np.where(us < 1.0 / (1.0 + np.exp(-2.0 * beta * h_unp)), 1.0, -1.0)
        s_per[row, i] = np.where(us < 1.0 / (1.0 + np.exp(-2.0 * beta * h_per)), 1.0, -1.0)


def sk_fdt(T, seed=0):
    """staggered-field FDT: returns dt, C(self-overlap), chi(staggered response) at fixed t_w."""
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    J = rng.normal(0.0, 1.0 / np.sqrt(N), size=(N_REAL, N, N))
    J = 0.5 * (J + np.transpose(J, (0, 2, 1)))
    J[:, np.arange(N), np.arange(N)] = 0.0
    eps = rng.choice(np.array([-1.0, 1.0]), size=(N_REAL, N))     # frozen staggered pattern
    s = rng.choice(np.array([-1.0, 1.0]), size=(N_REAL, N))

    # age/equilibrate for t_w sweeps (single branch, no field)
    zero_field = np.zeros((N_REAL, N))
    for _ in range(T_W):
        idx = rng.integers(0, N, size=(N, N_REAL)); u = rng.random((N, N_REAL))
        _sweep(s, s, J, beta, zero_field, idx, u)     # both args same -> single branch

    snap = s.copy()
    s_unp = s.copy(); s_per = s.copy()
    field_per = eps * H
    dts = sorted(set(int(round(x)) for x in np.geomspace(1, T_OBS, N_SAMPLES)))
    dt, C, chi = [], [], []
    for t in range(1, T_OBS + 1):
        idx = rng.integers(0, N, size=(N, N_REAL)); u = rng.random((N, N_REAL))
        _sweep(s_unp, s_per, J, beta, field_per, idx, u)
        if t in dts:
            C.append(float(np.mean(s_unp * snap)))                          # self-overlap
            chi.append(float(np.mean(eps * (s_per - s_unp)) / H))           # staggered response
            dt.append(t)
    return np.array(dt), np.array(C), np.array(chi)


def line_slope(C, Tchi, mask):
    return float(np.polyfit(C[mask], Tchi[mask], 1)[0]) if mask.sum() >= 3 else float("nan")


def analyze(T, dt, C, chi):
    Tchi = T * chi
    o = np.argsort(C); Cs, Ts = C[o], Tchi[o]
    cmax, cmin = C.max(), C.min(); span = max(cmax - cmin, 1e-9)
    hi = Cs > cmax - 0.30 * span                       # short lag (high C) -> X=1 branch
    lo = (Cs > cmin + 0.05 * span) & (Cs < cmin + 0.45 * span)   # aging branch
    s_hi = line_slope(Cs, Ts, hi); s_lo = line_slope(Cs, Ts, lo)
    X_short, X_aging = -s_hi, -s_lo
    # GLOBAL invariant (robust to local noise): how far T*chi peels BELOW the X=1 line (1-C),
    # over a common mid-C window present for all regimes. Positive = FDR-violated aging.
    win = (Cs > 0.12) & (Cs < 0.42)
    peel = float(np.mean((1.0 - Cs[win]) - Ts[win])) if win.sum() >= 3 else float("nan")
    # q_EA: scan C downward; first C where the line peels to a shallower slope (local X<0.85)
    q_EA = float("nan")
    nb = 7
    for j in range(len(Cs) - nb, nb, -1):
        seg = slice(j - nb, j + nb)
        sl = line_slope(Cs, Ts, np.array([seg.start <= k < seg.stop for k in range(len(Cs))]))
        if np.isfinite(sl) and -sl < 0.85 and Cs[j] < cmax - 0.04 * span:
            q_EA = float(Cs[j]); break
    two_step = bool(np.isfinite(X_short) and np.isfinite(X_aging)
                    and X_short > 0.80 and X_aging < 0.78)
    return dict(T=T, C=C, chi=chi, Tchi=Tchi, Cs=Cs, Ts=Ts, hi=hi, lo=lo, peel=peel,
                X_short=X_short, X_aging=X_aging, q_EA=q_EA, two_step=two_step)


def figure(results):
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2), dpi=150)
    cols = {"s": "#c2185b", "r": "#1565c0", "c": "#2e7d32"}
    gts = {Tv: gt for (Tv, lab, gt) in TEMPS}
    cc = np.linspace(0, 1, 50)
    ax[0].plot(cc, 1 - cc, "k--", lw=1.3, label="equilibrium FDT  $T\\chi=1-C$ (X=1)")
    for r in results:
        col = cols[gts[r["T"]]]
        ax[0].plot(r["C"], r["Tchi"], "o-", ms=4, color=col, lw=1.5,
                   label=f"T={r['T']} ({gts[r['T']]}): X_short={r['X_short']:.2f}, X_aging={r['X_aging']:.2f}" +
                         ("  TWO-STEP" if r["two_step"] else ""))
        if np.isfinite(r["q_EA"]):
            ax[0].axvline(r["q_EA"], color=col, ls=":", lw=1.0, alpha=0.6)
    ax[0].set_xlabel("C  (spin self-overlap)"); ax[0].set_ylabel(r"$T\chi$  (staggered response × T)")
    ax[0].set_title("FDT plot — aging peels BELOW the X=1 line at C<q_EA\n(dotted = q_EA break)")
    ax[0].legend(fontsize=7.5, frameon=False); ax[0].grid(alpha=0.3); ax[0].set_xlim(-0.05, 1.0)

    for r in results:
        col = cols[gts[r["T"]]]
        ax[1].plot(r["Cs"], r["Ts"], "o", ms=3, color=col, alpha=0.5)
        if r["hi"].sum() >= 3:
            ch = r["Cs"][r["hi"]]; ax[1].plot(ch, np.polyval(np.polyfit(ch, r["Ts"][r["hi"]], 1), ch),
                                              "-", color=col, lw=2.5)
        if r["lo"].sum() >= 3:
            cl = r["Cs"][r["lo"]]; ax[1].plot(cl, np.polyval(np.polyfit(cl, r["Ts"][r["lo"]], 1), cl),
                                              "--", color=col, lw=2.5)
    ax[1].plot(cc, 1 - cc, "k:", lw=1.0)
    ax[1].set_xlabel("C"); ax[1].set_ylabel(r"$T\chi$")
    ax[1].set_title("two-segment fit: solid = short-lag (slope→X_short),\ndashed = aging (slope→X_aging)")
    ax[1].grid(alpha=0.3); ax[1].set_xlim(-0.05, 1.0)

    fig.suptitle("sk spin glass — gFDR two-step (staggered-field FDT; real-substrate instance for staked:gfdr-two-step)",
                 fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "sk_gfdr_twostep.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


def main():
    mode = "quick" if QUICK else "big" if BIG else "deep" if DEEP else "full"
    print(f"SK gFDR two-step (staggered-field FDT)  [{mode}]  "
          f"t_w={T_W}, t_obs={T_OBS}, n_real={N_REAL}, h={H}, N={N}, Tc={TC}")
    results = []
    for (T, lab, gt) in TEMPS:
        dt, C, chi = sk_fdt(T)
        r = analyze(T, dt, C, chi); r["gt"] = gt
        results.append(r)
        print(f"\n[T={T}  {lab}]  C∈[{C.min():.3f},{C.max():.3f}]  Tχ∈[{r['Tchi'].min():.3f},{r['Tchi'].max():.3f}]")
        print(f"   PEEL below FDT line (global, C∈[0.12,0.42]) = {r['peel']:+.4f}   "
              f"[>0 ⇒ FDR-violated aging];  X_aging≈{r['X_aging']:.2f}")
    figure(results)

    cal = next((r for r in results if r["gt"] == "r"), None)
    glasses = [r for r in results if r["gt"] in ("s", "c")]
    print("\n" + "=" * 78); print("VERDICT (sk gFDR two-step)"); print("=" * 78)
    cal_peel = cal["peel"] if cal else float("nan")
    print(f"  CALIBRATION (paramagnet): peel={cal_peel:+.4f} (target ≈0, X=1 on the FDT line)")
    for r in glasses:
        delta = r["peel"] - cal_peel
        print(f"  glass T={r['T']} ({r['gt']}): peel={r['peel']:+.4f}  -> aging excess over paramagnet "
              f"= {delta:+.4f}  {'(AGING)' if delta > 0.02 else '(weak/none)'}")
    aging = any((r["peel"] - cal_peel) > 0.02 for r in glasses)
    cal_ok = np.isfinite(cal_peel) and abs(cal_peel) < 0.05
    if aging and cal_ok:
        print("  ⇒ INSTANCE STANDS: paramagnet on the X=1 line; the glass T*chi peels BELOW it (X<1) in")
        print("     the aging window — a real, emergent glass exercises FDR-violated aging while sharing")
        print("     the same short-lag behavior. The aging segment is the discriminator → vindicates")
        print("     staked:gfdr-two-step.")
    elif cal_ok:
        print("  ⇒ CALIBRATED, but the glass aging peel is weak at these params — push deeper (lower T,")
        print("     larger t_w). The apparatus is now sound; the signal needs more aging.")
    else:
        print("  ⇒ paramagnet not on the line yet — raise n_real (off-diagonal averaging) first.")


if __name__ == "__main__":
    main()
