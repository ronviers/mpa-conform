r"""delay_tower.py -- the decisive wall-forces-chaos test: the engine's OWN delay mechanism.

dynamical_tower.py coupled the platformed rhythms INSTANTANEOUSLY and they SYNCHRONIZED to a
smooth torus (no chaos). But the engine's wall-forces-chaos (COMPRESSION; receipts section 14) is
NOT instantaneous coupling -- it is a DELAY that DIVERGES at the Wall: each ascent is a delay
equation with delay = the priority-queue wait W_{n+1} = W_0/(1-sigma) (section 22), and as load
sigma -> 1 (the Wall), W -> infinity, "forcing, not merely allowing, a sequence of tower Hopf
bifurcations; N>=3 ascents populate the 3-torus => chaos forced."

This rebuilds the SAME tower (same phi-spaced frequencies, same coupling K at which the instantaneous
version merely synced) but makes the inter-level coupling DELAYED -- a_m(t - tau) instead of a_m(t) --
with tau = W_0/(1-sigma) growing as sigma -> Wall. It isolates the ONE new ingredient (the diverging
Wall-delay) and sweeps sigma -> 1.

    da_n/dt = (mu + i omega_n) a_n - |a_n|^2 a_n
              + K[a_{n-1}(t-tau) - a_n(t)] + K[a_{n+1}(t-tau) - a_n(t)]      (open chain)

THE SHARP QUESTIONS:
  (1) Does the diverging delay BREAK the torus into chaos (largest Lyapunov exponent LLE > 0)
      where instantaneous coupling synchronized it? If yes -> the WALL-DELAY is the chaos driver
      (wall-forces-chaos vindicated as a delay phenomenon).
  (2) Is it gated at N>=3? If N=1 -> limit cycle, N=2 -> non-chaotic, N=3 -> chaos as sigma->Wall,
      the Ruelle-Takens "3-torus" framing holds. If N=2+delay ALREADY chaoses, the gate is wrong:
      the mechanism is delay-Hopf (infinite-dim, chaoses at low N), NOT the 3-frequency count --
      a real correction to the engine's framing (the delay-Hopf vs Ruelle-Takens tension, flagged).

LLE for a delay system uses the FULL state (current value + the history function over [t-tau,t]);
both reference and perturbed carry their own history buffer, and the separation is renormalized over
the whole buffer (standard DDE Benettin). Hard finite-audit (the fake-NaN lesson).

Honest scope: per-level Stuart-Landau = the Hopf normal form of each platformed triad. Synthetic ->
calibration + the mechanism a real recursive substrate would instantiate; NOT vindication.

Run from mpa-conform root:  python scripts/delay_tower.py
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

PHI = (1.0 + np.sqrt(5.0)) / 2.0
OMEGA = np.array([1.0, 1.0 / PHI, 1.0 / PHI**2])   # same phi-spacing as dynamical_tower
MU, DT, K, W0 = 1.0, 0.01, 0.3, 2.0                 # K=0.3: instantaneous version synced to a torus
CHAOS = 0.01                                        # LLE above this = chaos (clears numerical noise)


def deriv(a, ad, N):
    """ad = delayed state a(t-tau) used for the neighbour (transmission-delayed) coupling."""
    d = (MU + 1j * OMEGA[:N]) * a - (np.abs(a) ** 2) * a
    if N > 1:
        d[:-1] += K * (ad[1:] - a[:-1])     # delayed signal from n+1 into n
        d[1:] += K * (ad[:-1] - a[1:])      # delayed signal from n-1 into n
    return d


def rk4(a, ad, N):
    k1 = deriv(a, ad, N); k2 = deriv(a + 0.5 * DT * k1, ad, N)
    k3 = deriv(a + 0.5 * DT * k2, ad, N); k4 = deriv(a + DT * k3, ad, N)
    return a + (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def lle_dde(N, tau, t_trans=250, t_meas=900, renorm=1.0, d0=1e-7, seed=1):
    """Largest Lyapunov exponent of the delay tower (full state = value + history buffer)."""
    L = max(1, int(round(tau / DT)))
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    histA = np.tile(a, (L, 1)).astype(complex)
    pos = 0
    for _ in range(int(t_trans / DT)):           # transient
        ad = histA[pos].copy()
        an = rk4(a, ad, N); histA[pos] = a; pos = (pos + 1) % L; a = an
    b = a.copy(); b[0] += d0                       # perturb current + (flat) history
    histB = histA.copy()
    steps = int(renorm / DT); nblk = int(t_meas / renorm)
    s = 0.0; ok = True; minr = np.inf
    for _ in range(nblk):
        for _ in range(steps):
            adA = histA[pos].copy(); adB = histB[pos].copy()
            an = rk4(a, adA, N); bn = rk4(b, adB, N)
            histA[pos] = a; histB[pos] = b; pos = (pos + 1) % L
            a, b = an, bn
            minr = min(minr, float(np.min(np.abs(a))))
            if not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
                ok = False; break
        if not ok:
            break
        dc = b - a; dh = histB - histA
        dist = float(np.sqrt(np.sum(np.abs(dc) ** 2) + np.sum(np.abs(dh) ** 2)))
        if dist <= 0 or not np.isfinite(dist):
            ok = False; break
        s += np.log(dist / d0)
        f = d0 / dist
        b = a + dc * f; histB = histA + dh * f
    lle = s / (nblk * renorm) if ok else float("nan")
    return lle, ok, minr


def main() -> None:
    print("delay tower: does the diverging Wall-delay break the torus into chaos? is it N>=3-gated?")
    print(f"phi-spaced omega={np.round(OMEGA,4)}, mu={MU}, K={K} (instantaneous version synced here), "
          f"W0={W0}; tau=W0/(1-sigma) -> infinity at the Wall\n")

    sigmas = np.array([0.0, 0.3, 0.5, 0.7, 0.8, 0.88])
    taus = W0 / (1.0 - sigmas)
    lle = {N: [] for N in (1, 2, 3)}
    finite_all = True
    print(f"{'sigma':>6} {'tau':>6} | {'LLE N=1':>9} {'LLE N=2':>9} {'LLE N=3':>9} | {'min|a| N=3':>10}")
    print("-" * 62)
    for sig, tau in zip(sigmas, taus):
        row = {}
        minr3 = np.nan
        for N in (1, 2, 3):
            l, ok, mr = lle_dde(N, tau)
            lle[N].append(l)
            if not ok:
                finite_all = False
            if N == 3:
                minr3 = mr
        print(f"{sig:>6.2f} {tau:>6.2f} | {lle[1][-1]:>9.4f} {lle[2][-1]:>9.4f} {lle[3][-1]:>9.4f} | {minr3:>10.4f}")
    for N in (1, 2, 3):
        lle[N] = np.array(lle[N])

    max1, max2, max3 = np.nanmax(lle[1]), np.nanmax(lle[2]), np.nanmax(lle[3])
    n3_chaos = max3 > CHAOS
    n2_chaos = max2 > CHAOS
    n1_chaos = max1 > CHAOS

    print(f"\nmax LLE over Wall approach:  N=1 {max1:+.4f}   N=2 {max2:+.4f}   N=3 {max3:+.4f}")
    print("\n================ VERDICT ================")
    if not finite_all:
        print("WARNING: some runs hit non-finite -- inspect before trusting (the fake-NaN lesson).")
    if n3_chaos and not n2_chaos and not n1_chaos:
        sig_on = sigmas[np.argmax(lle[3] > CHAOS)]
        print(f"WALL-FORCES-CHAOS VINDICATED, and N>=3-GATED. The diverging delay breaks the torus into")
        print(f"chaos for N=3 (max LLE {max3:+.3f}, onset near sigma={sig_on:.2f}) while N=1 (limit cycle)")
        print(f"and N=2 stay non-chaotic. The WALL-DELAY is the driver instantaneous coupling lacked; the")
        print(f"3-frequency Ruelle-Takens count holds. Same tower, same K, same frequencies as the")
        print(f"diffusive run that merely synced -- only the diverging delay was added.")
    elif n3_chaos and n2_chaos:
        print(f"CHAOS IS DELAY-DRIVEN, NOT N>=3-GATED. Both N=2 (max LLE {max2:+.3f}) and N=3 ({max3:+.3f})")
        print(f"chaos as sigma->Wall; N=1 (no coupling) stays a limit cycle ({max1:+.3f}). So the delay")
        print(f"forces chaos with only TWO coupled levels -- the mechanism is delay-Hopf (infinite-dim),")
        print(f"NOT the 3-frequency Ruelle-Takens count. This CORRECTS the engine's framing: wall-forces-")
        print(f"chaos is real but its threshold is N>=2+delay, not N>=3+3-torus (the tension flagged earlier).")
    elif not n3_chaos:
        print(f"NO CHAOS even as sigma->Wall (tau up to {taus[-1]:.1f}). Max LLE N=3 {max3:+.3f} <= {CHAOS}.")
        print(f"The diverging delay did not break the torus in the swept range -- a STRONGER pushback on")
        print(f"wall-forces-chaos: even the engine's own delay mechanism, at this K, does not force chaos.")
        print(f"(Check: larger K, or push sigma closer to 1 / tau larger, before concluding.)")
    else:
        print(f"Mixed: N=1 chaos={n1_chaos}, N=2={n2_chaos}, N=3={n3_chaos}. Read the table honestly.")
    print("\nHonest scope: per-level Stuart-Landau = Hopf normal form of each platformed triad; synthetic")
    print("calibration of the mechanism, NOT a real-substrate instance. Finite-audited (no fake-NaN).")

    # ---- figure ----
    fig, (axL, axT) = plt.subplots(1, 2, figsize=(14, 5.6), dpi=140)

    for N, col in [(1, "#1565c0"), (2, "#2e7d32"), (3, "#c2185b")]:
        axL.plot(sigmas, lle[N], "o-", color=col, ms=5, lw=1.9, label=f"N={N}")
    axL.axhline(0, color="gray", lw=0.8)
    axL.axhline(CHAOS, color="red", ls=":", lw=0.9, label="chaos threshold")
    axL.set_xlabel(r"load $\sigma$  (Wall approach; $\tau=W_0/(1-\sigma)\to\infty$)")
    axL.set_ylabel("largest Lyapunov exponent")
    axL.set_title("does the diverging Wall-delay force chaos?\n(same tower as the diffusive run, only the delay added)")
    axL.legend(fontsize=10, frameon=False); axL.grid(alpha=0.3)

    ax2 = axL.twiny()
    ax2.set_xlim(axL.get_xlim())
    ax2.set_xticks(sigmas)
    ax2.set_xticklabels([f"{t:.1f}" for t in taus], fontsize=8)
    ax2.set_xlabel(r"delay $\tau$", fontsize=9)

    # right: time series at the largest sigma for N=1 vs N=3
    def run_series(N, tau, t_trans=400, t_meas=300):
        L = max(1, int(round(tau / DT)))
        rng = np.random.default_rng(5)
        a = 0.5 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
        hist = np.tile(a, (L, 1)).astype(complex); pos = 0
        for _ in range(int(t_trans / DT)):
            ad = hist[pos].copy(); an = rk4(a, ad, N); hist[pos] = a; pos = (pos + 1) % L; a = an
        out = []
        for _ in range(int(t_meas / DT)):
            ad = hist[pos].copy(); an = rk4(a, ad, N); hist[pos] = a; pos = (pos + 1) % L; a = an
            out.append(a[0].real)
        return np.array(out)

    tau_max = taus[-1]
    t = np.arange(int(300 / DT)) * DT
    axT.plot(t, run_series(1, tau_max), color="#1565c0", lw=1.0, alpha=0.9, label="N=1")
    axT.plot(t, run_series(3, tau_max), color="#c2185b", lw=0.7, alpha=0.9, label="N=3")
    axT.set_xlim(0, 300)
    axT.set_xlabel("time"); axT.set_ylabel(r"Re $a_0$")
    axT.set_title(f"rhythm at the Wall (sigma={sigmas[-1]:.2f}, tau={tau_max:.1f})\nN=1 vs N=3")
    axT.legend(fontsize=10, frameon=False); axT.grid(alpha=0.3)

    fig.suptitle("delay tower: the diverging Wall-delay as the wall-forces-chaos driver (engine section 14)",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "delay_tower.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
