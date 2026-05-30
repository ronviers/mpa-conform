r"""clv_tower.py -- the PLATEAU SIDE of `battery:wall-ladder` on the coupled-oscillator cascade (move #4).

Substrate choice (the "pick the substrate first" call, Ron 2026-05-30): the COUPLED STUART-LANDAU
CASCADE -- the dynamical_tower substrate (an open chain of N platformed-rhythm oscillators, phi-spaced
= maximally incommensurate). Chosen over reaction-diffusion because the apparatus exists (dynamical_tower
+ clv_diagnostic both built and validated on it) and the frontier already frames coupled-SL as "the
cascade's own dynamics"; a reaction-diffusion build would be from-scratch and risk the under-1hr discipline.

battery:wall-ladder ↑ gate (the plateau side, reachable now): a real cascade substrate's LEVELS read
as NHIM PLATEAUS under the CLV minimum angle theta_min (bounded away from 0) -- INCLUDING a robust
quasiperiodic torus, where the leading FTLE false-positives (positive tail) but theta_min does not.
The closure-loss side (a level driven to eps->1 shows theta_min->0) is the DEFERRED delay-driven regime
(delay_tower.py / engine 14, K>gamma_s) -- not run here.

This runs the Ginelli/Kuptsov-Parlitz CLV theta_min diagnostic (reused from clv_diagnostic.py) directly
on the cascade's own ascent levels:
  N=1 : a single platformed rhythm  -> LIMIT CYCLE  (one plateau).
  N=2 : two platformed rhythms       -> 2-TORUS      (structurally stable, a plateau).
  N=3 : three platformed rhythms      -> 3-TORUS      (the dynamical_tower honest-negative: at weak
        coupling it does NOT break to chaos; it is a ROBUST torus -- a genuine NHIM plateau, despite a
        positive leading-FTLE tail).

PRE-REGISTERED BAR (plateau side; a clean miss is also evidence):
  W1 every cascade level is an NHIM PLATEAU: theta_min bounded away from 0 (>~ a few degrees) at N=1,2,3.
  W2 the FTLE FALSE-POSITIVE control: the robust N=3 3-torus carries a positive leading-FTLE tail
     (FTLE would mislabel it chaotic) while theta_min stays bounded -- theta_min is the correct
     discriminator (no false-positive on the NHIM torus).
  W3 the inter-level transitions (N -> N+1) are IGNITION boundaries (a new rhythm turns on), NOT
     closure-loss: theta_min stays bounded across the ascent -- consistent with the honest-negative
     (weak-coupling rhythms add WITHOUT loss of normal hyperbolicity).
  KILL: a genuine cascade-level NHIM reads theta_min -> 0 (the diagnostic fails to certify a plateau),
        OR the cascade chaoses at weak coupling (a level is not an NHIM at all).

SCOPE (honest): the per-level Stuart-Landau form is the Hopf NORMAL FORM of each platformed frustrated
triad (dynamical_tower) -- so this certifies the PLATEAU STRUCTURE of the cascade's reduced dynamics
(calibration-grade for the plateau side). Full real-emergent-substrate vindication + the closure-loss
side remain. theta_min is read on the cascade's own ascent, not a generic coupled-SL pair.

Usage (from mpa-conform root):  python scripts/clv_tower.py
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
for p in (str(REPO_ROOT), str(REPO_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from clv_diagnostic import lyap_clv, split_at_gap, theta_min_series

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

PHI = (1.0 + np.sqrt(5.0)) / 2.0
OMEGA = np.array([1.0, 1.0 / PHI, 1.0 / PHI ** 2])    # phi-spaced (dynamical_tower): incommensurate, slower up the tower
MU = 1.0                                              # Hopf parameter (above threshold)


def sl_chain(omega, K):
    """OPEN CHAIN of N Stuart-Landau oscillators (the dynamical_tower cascade), real coords
    s=[x0,y0,x1,y1,...]; nearest-neighbour diffusive coupling K (the inter-level coupling up the tower)."""
    N = len(omega)
    om = np.asarray(omega, float)
    deg = np.array([1 if (k == 0 or k == N - 1) else 2 for k in range(N)], float)
    if N == 1:
        deg[:] = 0.0

    def nbrs(k):
        out = []
        if k > 0:
            out.append(k - 1)
        if k < N - 1:
            out.append(k + 1)
        return out

    def f(s):
        x = s[0::2]; y = s[1::2]
        r2 = x * x + y * y
        fx = MU * x - om * y - r2 * x - K * deg * x
        fy = om * x + MU * y - r2 * y - K * deg * y
        for k in range(N):
            for j in nbrs(k):
                fx[k] += K * x[j]
                fy[k] += K * y[j]
        out = np.empty(2 * N)
        out[0::2] = fx; out[1::2] = fy
        return out

    def jac(s):
        x = s[0::2]; y = s[1::2]
        J = np.zeros((2 * N, 2 * N))
        for k in range(N):
            ix, iy = 2 * k, 2 * k + 1
            J[ix, ix] = MU - (3 * x[k] ** 2 + y[k] ** 2) - K * deg[k]
            J[ix, iy] = -om[k] - 2 * x[k] * y[k]
            J[iy, ix] = om[k] - 2 * x[k] * y[k]
            J[iy, iy] = MU - (x[k] ** 2 + 3 * y[k] ** 2) - K * deg[k]
            for j in nbrs(k):
                J[ix, 2 * j] = K
                J[iy, 2 * j + 1] = K
        return J
    return f, jac, 2 * N


def run_level(N, K, seed=1):
    f, jac, n = sl_chain(OMEGA[:N], K)
    rng = np.random.default_rng(seed)
    x0 = 0.9 * rng.standard_normal(n)
    exps, clvs, ftle1 = lyap_clv(f, jac, n, x0, dt=0.01, m=10, warm=4000, rec=6000, drop=800, seed=seed)
    top, bot, gap = split_at_gap(exps)
    th = theta_min_series(clvs, top, bot)
    se = np.sort(exps)[::-1]
    n_zero = int(np.sum(np.abs(exps) < 0.02))
    n_pos = int(np.sum(exps > 0.02))
    kind = "CHAOS" if n_pos >= 1 else ("TORUS" if n_zero >= 2 else "LIMIT CYCLE")
    print(f"\n[N={N}, K={K}]  spectrum = {np.array2string(se, precision=3, floatmode='fixed')}")
    print(f"   level dynamics: {kind} (n_pos={n_pos}, n_zero={n_zero}); gap split {len(top)}|{len(bot)}")
    print(f"   theta_min (deg): min={th.min():.2f}, 1st-pct={np.percentile(th,1):.2f}, median={np.median(th):.2f}")
    print(f"   leading FTLE: mean={ftle1.mean():+.3f}, 95th-pct={np.percentile(ftle1,95):+.3f}, max={ftle1.max():+.3f}")
    return dict(N=N, K=K, exps=se, theta=th, ftle1=ftle1, kind=kind, n_pos=n_pos, n_zero=n_zero)


def main():
    print("CLV theta_min on the coupled Stuart-Landau CASCADE -- the plateau side of battery:wall-ladder")
    print(f"phi-spaced frequencies omega={np.round(OMEGA,4)}, mu={MU}; weak inter-level coupling (torus regime)\n")

    K = 0.05                                          # weak coupling: the dynamical_tower torus/plateau regime
    lvl1 = run_level(1, K)
    lvl2 = run_level(2, K)
    lvl3 = run_level(3, K)
    levels = [lvl1, lvl2, lvl3]

    plateau_floor = min(l["theta"].min() for l in levels)
    n3 = lvl3
    ftle_tail = float(np.percentile(n3["ftle1"], 95))
    chaosed = any(l["n_pos"] >= 1 for l in levels)

    W1 = bool(plateau_floor > 2.0 and not chaosed)                 # every level a bounded-theta_min plateau
    W2 = bool(ftle_tail > 0.0 and n3["theta"].min() > 2.0)         # torus FTLE false-positive, theta_min not fooled
    W3 = bool(all(l["kind"] in ("LIMIT CYCLE", "TORUS") for l in levels) and plateau_floor > 2.0)

    figure(levels)

    print("\n" + "=" * 84)
    print("VERDICT -- battery:wall-ladder PLATEAU SIDE on the coupled Stuart-Landau cascade")
    print("=" * 84)
    bar = [(f"W1 every cascade level is an NHIM plateau (theta_min floor={plateau_floor:.1f} deg, no chaos)", W1),
           (f"W2 FTLE false-positive control: N=3 torus FTLE 95th-pct={ftle_tail:+.3f}>0, "
            f"theta_min={n3['theta'].min():.1f} deg bounded", W2),
           ("W3 inter-level transitions are IGNITION (new rhythm on), NOT closure-loss (theta_min bounded across the ascent)", W3)]
    for label, ok in bar:
        print(f"   [{'PASS' if ok else 'MISS'}]  {label}")
    if all(ok for _, ok in bar):
        print("\n  ==> PLATEAU SIDE INSTANCED on the coupled-oscillator cascade. Every ascent level of the")
        print(f"      Stuart-Landau tower reads as an NHIM PLATEAU under theta_min (floor {plateau_floor:.1f} deg):")
        print("      N=1 limit cycle, N=2 2-torus, N=3 3-torus -- all with the Oseledets splitting bounded")
        print("      transverse. The N=3 robust torus (the dynamical_tower honest-negative) carries a")
        print(f"      positive leading-FTLE tail (95th-pct {ftle_tail:+.3f}) that would mislabel it chaotic;")
        print("      theta_min correctly does NOT false-positive -- it is the right discriminator. The")
        print("      inter-level transitions are IGNITION boundaries (a new rhythm turns on), NOT closure-loss:")
        print("      at weak coupling the rhythms ADD without loss of normal hyperbolicity. => the plateau")
        print("      side of battery:wall-ladder holds on the chosen substrate.")
        print("\n  REMAINING (do NOT claim): the CLOSURE-LOSS side (a level driven to eps->1, theta_min->0) is")
        print("  the DEFERRED delay-driven regime (delay_tower.py / engine 14, K>gamma_s). And the SL form is")
        print("  the Hopf normal form of the emergent frustrated triads -- full real-emergent-substrate")
        print("  vindication (both sides on an emergent cascade) is the open frontier. wall-as-type-boundary")
        print("  stays sharpening; battery:wall-ladder's plateau face is now exercised on the cascade.")
    else:
        print("\n  ==> CLEAN MISS -- report exactly which leg held (it sharpens the gate).")


def figure(levels):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6), dpi=150)
    colors = {"CHAOS": "#c62828", "TORUS": "#1565c0", "LIMIT CYCLE": "#2e7d32"}

    # panel 1: Lyapunov spectra per level
    for l in levels:
        col = colors[l["kind"]]
        ax[0].plot(range(len(l["exps"])), l["exps"], "o-", color=col, ms=6,
                   label=f"N={l['N']} ({l['kind']})")
    ax[0].axhline(0, color="gray", lw=0.8)
    ax[0].set_xlabel("index $i$"); ax[0].set_ylabel(r"Lyapunov exponent $\lambda_i$")
    ax[0].set_title("cascade levels: Lyapunov spectra\n(N=1 cycle, N=2 2-torus, N=3 3-torus — no positive exponent)")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    # panel 2: theta_min per level -- all bounded away from 0 (NHIM plateaus)
    tbins = np.linspace(0, 90, 46)
    for l in levels:
        col = colors[l["kind"]]
        ax[1].hist(l["theta"], bins=tbins, density=True, histtype="step", lw=2, color=col,
                   label=f"N={l['N']}: min={l['theta'].min():.1f}°")
    ax[1].axvline(0, color="gray", lw=0.8)
    ax[1].set_xlabel(r"$\theta_{\min}$ between CLV bundles (deg)")
    ax[1].set_ylabel("density")
    ax[1].set_title(r"every level an NHIM PLATEAU: $\theta_{\min}$ bounded from 0")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    # panel 3: the N=3 torus FTLE false-positive (positive tail) vs theta_min (bounded)
    n3 = levels[-1]
    a2 = ax[2]
    a2.hist(n3["ftle1"], bins=40, density=True, histtype="stepfilled", alpha=0.5, color="#1565c0",
            label=f"N=3 torus FTLE λ₁ (95th={np.percentile(n3['ftle1'],95):+.2f}>0!)")
    a2.axvline(0, color="gray", lw=1.0, ls="--")
    a2.set_xlabel(r"leading finite-time Lyapunov exponent $\lambda_1(\tau)$")
    a2.set_ylabel("density")
    a2.set_title(f"FTLE FALSE-POSITIVE on the robust 3-torus\n(positive tail) — but $\\theta_{{\\min}}$={n3['theta'].min():.0f}° bounded (NHIM)")
    a2.legend(fontsize=8, frameon=False); a2.grid(alpha=0.3)

    fig.suptitle("battery:wall-ladder PLATEAU SIDE — the coupled Stuart-Landau cascade's levels are NHIM "
                 "plateaus (θ_min bounded; FTLE false-positive controlled)", fontsize=11, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "clv_tower.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
