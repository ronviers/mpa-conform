r"""clv_tower_shear.py -- the CLOSURE-LOSS side of `battery:wall-ladder` via SHEAR (non-delay route).

clv_tower.py did the PLATEAU side on the coupled Stuart-Landau cascade (all ascent levels NHIM plateaus,
theta_min bounded) and DEFERRED the closure-loss side (theta_min -> 0) to the delay-driven regime
(delay_tower / engine 14). The drive-characterization research (`mpa-atlas/docs/normal coupling research
and prompt.md`) named a NON-DELAY route: the missing ingredient is SHEAR / non-isochronicity (the reactive
Stuart-Landau cross-term). With shear the coupled-SL / complex-Ginzburg-Landau chain has a
BENJAMIN-FEIR-NEWELL instability (1 + b c < 0): the synchronized plateau loses normal hyperbolicity and
routes to phase turbulence -- a closure-loss boundary reachable WITHOUT delay and WITHOUT N>=3.

clv_tower used ISOCHRONOUS oscillators (no shear) + purely diffusive (real-K) coupling -> it synchronizes
(the dynamical_tower honest-negative). This adds the reactive parts:
    da_k/dt = (mu + i w_k) a_k - (1 + i c) |a_k|^2 a_k + K (1 + i b) * sum_neighbors (a_j - a_k)
  c = shear (amplitude-dependent frequency / non-isochronicity); b = reactive coupling.
Benjamin-Feir-Newell: the in-phase state destabilizes for 1 + b c < 0.

PRE-REGISTERED BAR (a clean miss is also evidence):
  C1 PLATEAU below BF (1 + b c > 0): theta_min bounded away from 0, no positive Lyapunov exponent
     -- reproduces clv_tower's plateau face with shear off / sub-threshold.
  C2 CLOSURE-LOSS above BF (1 + b c < 0): theta_min -> 0 (CLV bundle tangency = loss of normal
     hyperbolicity) AND a positive Lyapunov exponent appears (genuine chaos, not a new torus).
  C3 the transition tracks the BF threshold: theta_min drops / LE turns positive AS 1 + b c crosses 0,
     not at an unrelated c.
  KILL: theta_min stays bounded through the BF instability (the discriminator fails on a shear-driven
        boundary), OR no closure-loss is reachable by shear at all on this substrate.

SCOPE (honest): shear-induced closure-loss is a GENERIC loss-of-NHIM route (Benjamin-Feir), NOT the
engine's specific 14 delay-Hopf mechanism. So this exercises the theta_min DISCRIMINATOR on the boundary
side (which is what the battery:wall-ladder gate literally asks -- "a level driven to closure shows
theta_min->0", mechanism-agnostic); the delay run stays the canonical-mechanism test.

Usage (from mpa-conform root):  python scripts/clv_tower_shear.py
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
MU = 1.0


def sl_chain_shear(omega, K, b, c, ring=False):
    """coupled Stuart-Landau with shear c (non-isochronicity) and reactive coupling b. Real coords
    s=[x0,y0,x1,y1,...]. ring=True -> periodic boundary (the canonical CGLE BF setup)."""
    N = len(omega)
    om = np.asarray(omega, float)
    if ring and N > 2:
        nbrs = [[(k - 1) % N, (k + 1) % N] for k in range(N)]
    else:
        nbrs = [[j for j in (k - 1, k + 1) if 0 <= j < N] for k in range(N)]
    deg = np.array([len(nbrs[k]) for k in range(N)], float)

    def f(s):
        x = s[0::2]; y = s[1::2]
        R = x * x + y * y
        fx = MU * x - om * y - R * x + c * R * y - K * deg * x + K * b * deg * y
        fy = om * x + MU * y - R * y - c * R * x - K * deg * y - K * b * deg * x
        for k in range(N):
            sx = x[nbrs[k]].sum(); sy = y[nbrs[k]].sum()
            fx[k] += K * sx - K * b * sy
            fy[k] += K * sy + K * b * sx
        out = np.empty(2 * N)
        out[0::2] = fx; out[1::2] = fy
        return out

    def jac(s):
        x = s[0::2]; y = s[1::2]
        J = np.zeros((2 * N, 2 * N))
        for k in range(N):
            ix, iy = 2 * k, 2 * k + 1
            xk, yk = x[k], y[k]
            J[ix, ix] = MU - (3 * xk * xk + yk * yk) + 2 * c * xk * yk - K * deg[k]
            J[ix, iy] = -om[k] - 2 * xk * yk + c * (xk * xk + 3 * yk * yk) + K * b * deg[k]
            J[iy, ix] = om[k] - 2 * xk * yk - c * (3 * xk * xk + yk * yk) - K * b * deg[k]
            J[iy, iy] = MU - (xk * xk + 3 * yk * yk) - 2 * c * xk * yk - K * deg[k]
            for j in nbrs[k]:
                J[ix, 2 * j] = K; J[ix, 2 * j + 1] = -K * b
                J[iy, 2 * j] = K * b; J[iy, 2 * j + 1] = K
        return J
    return f, jac, 2 * N


def verify_jacobian(omega, K, b, c, ring=False, seed=0):
    """finite-difference check of the analytic Jacobian -- the CLV/Lyapunov computation is only as
    trustworthy as jac (a Jacobian bug is a fake-NaN-class trap). Returns max|analytic - FD|."""
    f, jac, n = sl_chain_shear(omega, K, b, c, ring)
    rng = np.random.default_rng(seed)
    s = 0.5 * rng.standard_normal(n)
    Ja = jac(s)
    eps = 1e-6
    Jfd = np.zeros((n, n))
    f0 = f(s)
    for i in range(n):
        sp = s.copy(); sp[i] += eps
        Jfd[:, i] = (f(sp) - f0) / eps
    return float(np.max(np.abs(Ja - Jfd)))


def run(omega, K, b, c, ring=False, seed=1, **kw):
    f, jac, n = sl_chain_shear(omega, K, b, c, ring)
    rng = np.random.default_rng(seed)
    x0 = 0.6 * rng.standard_normal(n)
    exps, clvs, ftle1 = lyap_clv(f, jac, n, x0, dt=0.01, m=10,
                                 warm=kw.get("warm", 3000), rec=kw.get("rec", 4000),
                                 drop=kw.get("drop", 600), seed=seed)
    top, bot, gap = split_at_gap(exps)
    th = theta_min_series(clvs, top, bot)
    lam_max = float(np.max(exps))
    n_pos = int(np.sum(exps > 0.02))
    return dict(c=c, bc=1.0 + b * c, lam_max=lam_max, n_pos=n_pos,
                theta_min=float(th.min()), theta_med=float(np.median(th)),
                exps=np.sort(exps)[::-1])


def sweep(label, omega, K, b, cs, ring=False, **kw):
    print(f"\n[{label}]  N={len(omega)}, K={K}, b={b}, ring={ring}; BF threshold 1+bc=0 at c={-1.0/b:.3f}")
    print(f"   {'c':>5} {'1+bc':>7} {'lam_max':>9} {'n_pos':>5} {'theta_min':>10} {'theta_med':>10}  regime")
    rows = []
    for c in cs:
        r = run(omega, K, b, c, ring=ring, **kw)
        regime = "CLOSURE-LOSS" if (r["n_pos"] >= 1 and r["theta_min"] < 5.0) else (
            "chaos?" if r["n_pos"] >= 1 else ("torus/plateau" if r["theta_min"] > 5.0 else "boundary?"))
        rows.append(r)
        print(f"   {c:>5.2f} {r['bc']:>7.2f} {r['lam_max']:>+9.4f} {r['n_pos']:>5d} "
              f"{r['theta_min']:>10.2f} {r['theta_med']:>10.2f}  {regime}")
    return rows


def main():
    print("CLV theta_min under SHEAR -- the closure-loss side of battery:wall-ladder (non-delay route)")
    print("driving the coupled-SL cascade across the Benjamin-Feir-Newell instability (1+bc<0)\n")

    b = -2.0
    cs = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5]

    # Jacobian sanity (fake-NaN guard) at a sub- and super-threshold c
    for c in (0.0, 1.0):
        err = verify_jacobian(np.array([1.0, 1.0 / PHI, 1.0 / PHI ** 2]), 0.3, b, c)
        print(f"  jacobian check (c={c}): max|analytic - finite-diff| = {err:.2e}  "
              f"({'OK' if err < 1e-4 else 'BUG -- do not trust CLV'})")

    # (1) the faithful phi-spaced cascade (N=3 open chain, the clv_tower substrate) + shear
    casc = sweep("cascade N=3 (phi-spaced open chain) + shear",
                 np.array([1.0, 1.0 / PHI, 1.0 / PHI ** 2]), K=0.6, b=b, cs=cs, ring=False)

    # (2) a deeper homogeneous ring (the canonical discrete-CGLE BF setup) -- gives turbulence room
    ring = sweep("ring N=16 (identical, CGLE) + shear",
                 np.ones(16), K=0.6, b=b, cs=cs, ring=True, rec=3000, warm=2500)

    # --- verdict (read the RING as the primary closure-loss demonstration; cascade for reachability) ---
    cbf = -1.0 / b
    below = [r for r in ring if r["bc"] > 0.05]
    above = [r for r in ring if r["bc"] < -0.05]
    c1 = bool(all(r["theta_min"] > 5.0 and r["n_pos"] == 0 for r in below))
    c2 = bool(any(r["theta_min"] < 5.0 and r["n_pos"] >= 1 for r in above))
    # transition tracks BF: first closure-loss row has c just above the threshold
    cl_rows = [r for r in ring if r["theta_min"] < 5.0 and r["n_pos"] >= 1]
    c3 = bool(cl_rows and min(r["c"] for r in cl_rows) >= cbf - 0.2)
    casc_reaches = bool(any(r["theta_min"] < 5.0 and r["n_pos"] >= 1 for r in casc))

    figure(cs, casc, ring, cbf)

    print("\n" + "=" * 84)
    print("VERDICT -- battery:wall-ladder CLOSURE-LOSS side via shear (non-delay)")
    print("=" * 84)
    bar = [(f"C1 plateau below BF (1+bc>0): theta_min bounded, no positive LE", c1),
           (f"C2 closure-loss above BF (1+bc<0): theta_min -> 0 AND a positive LE appears", c2),
           (f"C3 the transition tracks the BF threshold (c >~ {cbf:.2f})", c3)]
    for label, ok in bar:
        print(f"   [{'PASS' if ok else 'MISS'}]  {label}")
    print(f"   [{'YES' if casc_reaches else 'NO'}]   the faithful N=3 cascade also reaches closure-loss under shear")
    if c1 and c2 and c3:
        print("\n  ==> CLOSURE-LOSS SIDE REACHED (non-delay route). Cranking shear past the Benjamin-Feir")
        print("      instability drives the synchronized plateau to loss of normal hyperbolicity: theta_min")
        print("      collapses toward 0 (CLV bundle tangency) and a positive Lyapunov exponent appears,")
        print("      AS 1+bc crosses 0. The theta_min discriminator catches the closure-loss boundary on a")
        print("      coupled-SL cascade WITHOUT the deferred delay machinery. => battery:wall-ladder now has")
        print("      BOTH faces exercised: plateau (clv_tower) + closure-loss (here). The transition is the")
        print("      generic Benjamin-Feir loss-of-NHIM, not the engine-14 delay-Hopf mechanism (that stays")
        print("      the canonical-mechanism test); but the GATE (theta_min->0 at closure) is met.")
        if casc_reaches:
            print("      The faithful N=3 phi-spaced cascade ALSO reaches it under shear.")
        else:
            print("      (The minimal N=3 cascade did NOT reach it -- closure-loss needs tower depth + shear;")
            print("       the deeper ring shows the boundary the discriminator catches.)")
    else:
        print("\n  ==> CLEAN MISS on a leg -- report which held (it sharpens the gate / shear route).")


def figure(cs, casc, ring, cbf):
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), dpi=150)
    cs = np.array(cs)

    # left: theta_min vs shear (plateau bounded -> closure-loss ->0 past BF)
    a0 = ax[0]
    a0.plot(cs, [r["theta_min"] for r in casc], "o-", color="#1565c0", lw=2, label="cascade N=3 (phi)")
    a0.plot(cs, [r["theta_min"] for r in ring], "s-", color="#c2185b", lw=2, label="ring N=16 (CGLE)")
    a0.axvline(cbf, color="#2e7d32", ls="--", lw=1.5, label=f"Benjamin-Feir threshold (c={cbf:.2f})")
    a0.axhline(5.0, color="gray", ls=":", lw=1, label="closure-loss floor (5°)")
    a0.set_xlabel("shear  c (non-isochronicity)"); a0.set_ylabel(r"$\theta_{\min}$ (deg)")
    a0.set_title(r"$\theta_{\min}$: plateau bounded $\to$ closure-loss $\to 0$ past Benjamin-Feir")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3)

    # right: max Lyapunov exponent vs shear (>=0 plateau/torus -> >0 chaos past BF)
    a1 = ax[1]
    a1.plot(cs, [r["lam_max"] for r in casc], "o-", color="#1565c0", lw=2, label="cascade N=3 (phi)")
    a1.plot(cs, [r["lam_max"] for r in ring], "s-", color="#c2185b", lw=2, label="ring N=16 (CGLE)")
    a1.axvline(cbf, color="#2e7d32", ls="--", lw=1.5, label=f"BF threshold (c={cbf:.2f})")
    a1.axhline(0.0, color="gray", lw=0.8)
    a1.set_xlabel("shear  c (non-isochronicity)"); a1.set_ylabel(r"largest Lyapunov exponent $\lambda_{\max}$")
    a1.set_title(r"$\lambda_{\max}$ turns positive past Benjamin-Feir (genuine chaos)")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    fig.suptitle("battery:wall-ladder CLOSURE-LOSS via shear — Benjamin-Feir drives the plateau to "
                 "loss of normal hyperbolicity (θ_min→0, λ_max>0)", fontsize=11, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "clv_tower_shear.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
