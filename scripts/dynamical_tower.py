r"""dynamical_tower.py -- the capstone: nesting the nonlinear node into the full dynamical tower.

frustration_ascent.py showed (exactly, on the sign-topological face) that each frustrated ascent
platforms +1 protected cycle. nonlinear_node.py showed each node is a real MPA mode that RINGS at
chit = 1 ch and carries a chit-flowing current. This nests them and reads the DYNAMICS.

The bridge: each platformed level is a Hopf oscillator. In its k_frust LIMIT-CYCLE regime, a
frustrated triad's slow attractor is its perp-plane circulation -- and by the Hopf normal form /
center-manifold reduction (pa:bifurcation-normal-forms, pa:center-manifold) that circulation IS a
Stuart-Landau oscillator at the level's frequency. So:

    one ascent  ==  +1 protected cycle (frustration_ascent)  ==  +1 Hopf rhythm  ==  +1 Stuart-Landau
                    oscillator in the tower.

The tower is therefore a chain of N Stuart-Landau oscillators, one per platformed level, timescale-
separated up the tower (phi-spaced frequencies -> maximally incommensurate, hardest to lock):

    da_n/dt = (mu + i omega_n) a_n - |a_n|^2 a_n + K (a_{n-1}-a_n) + K (a_{n+1}-a_n)   (open chain)

THE ENGINE CLAIM (COMPRESSION: wall-forces-chaos; pa:nrt-chaos Newhouse-Ruelle-Takens):
"N>=3 ascents complete a 3-torus => forced chaos." The threshold is sharp and falsifiable:
  * N=1  -> a limit cycle              (largest Lyapunov exponent LLE ~ 0; one discrete spectral peak)
  * N=2  -> a 2-torus (quasiperiodic)  (LLE ~ 0; two incommensurate peaks; NEVER chaos -- two
            frequencies are structurally stable, Peixoto)
  * N=3  -> a 3-torus that BREAKS to chaos (LLE > 0; broadband spectrum) -- the THIRD ascent forces it.

So chaos is forced by N>=3, not by any single oscillator: it is the tower, not the node. This is
the dynamical face of the b1-growth -- the rhythms the recursion platforms cannot all coexist.

VINDICATE: a coupling window where N=3 gives LLE>0 while N=1 and N=2 stay <= 0 (within tol).
KILL: N=3 never chaoses for any coupling (no positive LLE) -- the 3-torus does not break, wall-
      forces-chaos fails; OR N=2 chaoses (chaos not gated at N>=3, the Ruelle-Takens count is wrong).

Honest scope: the per-level Stuart-Landau form is the Hopf NORMAL FORM of each platformed triad
(rigorous near the bifurcation); the tower is the coupled normal forms. Synthetic -> calibration +
the apparatus a real recursive substrate lands into, NOT vindication of the staked claim.

Run from mpa-conform root:  python scripts/dynamical_tower.py
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
OMEGA = np.array([1.0, 1.0 / PHI, 1.0 / PHI**2])   # phi-spaced: maximally incommensurate + slower up tower
MU, DT = 1.0, 0.01                                  # Hopf parameter (above threshold), integration step


def deriv(a, K, N):
    d = (MU + 1j * OMEGA[:N]) * a - (np.abs(a) ** 2) * a
    if N > 1:
        d[:-1] += K * (a[1:] - a[:-1])
        d[1:] += K * (a[:-1] - a[1:])
    return d


def rk4(a, K, N):
    k1 = deriv(a, K, N)
    k2 = deriv(a + 0.5 * DT * k1, K, N)
    k3 = deriv(a + 0.5 * DT * k2, K, N)
    k4 = deriv(a + DT * k3, K, N)
    return a + (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate(N, K, t_trans, t_meas, seed=0):
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    for _ in range(int(t_trans / DT)):
        a = rk4(a, K, N)
    n = int(t_meas / DT)
    traj = np.empty((n, N), dtype=complex)
    for i in range(n):
        a = rk4(a, K, N)
        traj[i] = a
    return traj


def lyapunov(N, K, t_trans=600, t_meas=1500, renorm_dt=0.5, d0=1e-8, seed=1):
    """Benettin largest Lyapunov exponent: two trajectories, renormalize the separation periodically."""
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    for _ in range(int(t_trans / DT)):
        a = rk4(a, K, N)
    da = np.zeros(N, dtype=complex); da[0] = d0
    b = a + da
    steps = int(renorm_dt / DT)
    nblk = int(t_meas / renorm_dt)
    s = 0.0
    for _ in range(nblk):
        for _ in range(steps):
            a = rk4(a, K, N); b = rk4(b, K, N)
        d = b - a
        dist = np.sqrt(np.sum(np.abs(d) ** 2))
        if dist <= 0 or not np.isfinite(dist):
            break
        s += np.log(dist / d0)
        b = a + (d / dist) * d0
    return s / (nblk * renorm_dt)


def spectrum(sig):
    sig = sig - sig.mean()
    f = np.fft.rfftfreq(len(sig), DT)
    p = np.abs(np.fft.rfft(sig * np.hanning(len(sig)))) ** 2
    return f, p / (p.max() + 1e-30)


def main() -> None:
    print("dynamical tower: do N>=3 platformed rhythms force chaos (wall-forces-chaos)?")
    print(f"phi-spaced frequencies omega = {np.round(OMEGA, 4)}, mu = {MU} (above Hopf)\n")

    Ks = np.linspace(0.0, 0.6, 25)
    lle = {N: np.array([lyapunov(N, K) for K in Ks]) for N in (1, 2, 3)}

    print(f"{'K':>6} | {'LLE N=1':>9} {'LLE N=2':>9} {'LLE N=3':>9}")
    print("-" * 40)
    for i, K in enumerate(Ks):
        if i % 2 == 0:
            print(f"{K:>6.3f} | {lle[1][i]:>9.4f} {lle[2][i]:>9.4f} {lle[3][i]:>9.4f}")

    tol = 0.01
    chaos3 = lle[3] > tol
    k_star = float(Ks[np.argmax(lle[3])])
    max3, max2, max1 = float(lle[3].max()), float(lle[2].max()), float(lle[1].max())
    n3_chaoses = bool(np.any(chaos3))
    n12_clean = (max2 <= tol) and (max1 <= tol)

    print(f"\nmax LLE:  N=1 {max1:+.4f}   N=2 {max2:+.4f}   N=3 {max3:+.4f}")
    print(f"N=3 chaotic window: K in "
          f"[{Ks[chaos3].min():.3f}, {Ks[chaos3].max():.3f}]" if n3_chaoses else "N=3: no chaos found")
    print(f"strongest chaos at K* = {k_star:.3f} (N=3 LLE = {lle[3][np.argmax(lle[3])]:+.4f})")

    print("\n================ VERDICT ================")
    if n3_chaoses and n12_clean:
        print(f"WALL-FORCES-CHAOS INSTANCED. The third ascent forces chaos: N=3 has a positive-LLE")
        print(f"window (max LLE {max3:+.3f} at K*={k_star:.3f}) while N=1 (limit cycle, LLE {max1:+.3f})")
        print(f"and N=2 (2-torus, LLE {max2:+.3f}) never chaos -- exactly the Ruelle-Takens count: two")
        print(f"platformed rhythms make a structurally-stable 2-torus, three break it. Chaos is a")
        print(f"property of the TOWER, not any node. This is the dynamical face of frustration-ascent's")
        print(f"b1-growth: +1 rhythm per ascent, and the 3rd rhythm is the one the tower cannot hold.")
    else:
        print(f"NOT clean: N=3 chaoses={n3_chaoses}, N<3 stay non-chaotic={n12_clean} "
              f"(max LLE N1={max1:+.3f}, N2={max2:+.3f}, N3={max3:+.3f}). Read honestly.")
    print("\nHonest scope: per-level Stuart-Landau = the Hopf normal form of each platformed frustrated")
    print("triad (rigorous near bifurcation). Synthetic -> calibration + apparatus a real recursive")
    print("substrate nests into; NOT vindication of the staked claim (needs a real cross-substrate instance).")

    # ---- figure ----
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=140)

    # (0,0) LLE vs K -- the money plot
    a0 = ax[0, 0]
    for N, col in [(1, "#1565c0"), (2, "#2e7d32"), (3, "#c2185b")]:
        a0.plot(Ks, lle[N], "o-", color=col, ms=4, lw=1.8, label=f"N={N}")
    a0.axhline(0, color="gray", lw=0.8)
    a0.fill_between(Ks, 0, lle[3], where=(lle[3] > tol), color="#c2185b", alpha=0.15)
    a0.set_xlabel("inter-level coupling K"); a0.set_ylabel("largest Lyapunov exponent")
    a0.set_title("N>=3 forces chaos: only the N=3 curve goes positive\n(N=1 limit cycle, N=2 2-torus stay <= 0)")
    a0.legend(fontsize=10, frameon=False); a0.grid(alpha=0.3)

    # detail integrations at K*
    trajs = {N: integrate(N, k_star, t_trans=800, t_meas=400) for N in (1, 2, 3)}

    # (0,1) power spectra: discrete -> broadband
    a1 = ax[0, 1]
    for N, col in [(1, "#1565c0"), (2, "#2e7d32"), (3, "#c2185b")]:
        f, p = spectrum(np.real(trajs[N][:, 0]))
        a1.semilogy(f, p + 1e-6, color=col, lw=1.3, label=f"N={N}")
    a1.set_xlim(0, 1.2); a1.set_ylim(1e-6, 2)
    a1.set_xlabel("frequency"); a1.set_ylabel("power (norm.)")
    a1.set_title(f"spectrum at K*={k_star:.3f}: discrete peaks (N=1,2)\n-> broadband (N=3 = chaos)")
    a1.legend(fontsize=10, frameon=False); a1.grid(alpha=0.3)

    # (1,0) phase portrait N=2 (torus) vs N=3 (strange attractor) -- Re a_1 vs Re a_2
    a2 = ax[1, 0]
    a2.plot(np.real(trajs[2][:, 0]), np.real(trajs[2][:, 1]), color="#2e7d32", lw=0.4, alpha=0.7,
            label="N=2 (2-torus)")
    a2.plot(np.real(trajs[3][:, 0]), np.real(trajs[3][:, 1]), color="#c2185b", lw=0.3, alpha=0.7,
            label="N=3 (strange attractor)")
    a2.set_xlabel(r"Re $a_1$"); a2.set_ylabel(r"Re $a_2$")
    a2.set_title("phase portrait: closed torus (N=2)\nvs space-filling strange attractor (N=3)")
    a2.legend(fontsize=10, frameon=False); a2.grid(alpha=0.3)

    # (1,1) time series at K* -- periodic vs chaotic
    a3 = ax[1, 1]
    t = np.arange(trajs[3].shape[0]) * DT
    a3.plot(t, np.real(trajs[1][:, 0]), color="#1565c0", lw=1.0, alpha=0.9, label="N=1 (periodic)")
    a3.plot(t, np.real(trajs[3][:, 0]), color="#c2185b", lw=0.8, alpha=0.9, label="N=3 (chaotic)")
    a3.set_xlim(0, 200)
    a3.set_xlabel("time"); a3.set_ylabel(r"Re $a_1$")
    a3.set_title("the tower's rhythm: clean period (N=1)\n-> aperiodic (N=3)")
    a3.legend(fontsize=10, frameon=False); a3.grid(alpha=0.3)

    fig.suptitle("dynamical tower: the third platformed rhythm forces chaos (N>=3 -> 3-torus breakdown)",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "dynamical_tower.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
