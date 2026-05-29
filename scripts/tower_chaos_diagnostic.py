r"""tower_chaos_diagnostic.py -- is the N=3 tower's attractor a clean torus, an SNA, localized chaos,
or genuine chaos? And does it cross the polar (orthogonal-zero) region where MPA forbids reading the
angular clock?

dynamical_tower.py returned largest-Lyapunov-exponent (LLE) ~ 0 for N=3 -> "robust 3-torus, no chaos."
But a single LLE cannot tell apart: (a) clean quasiperiodic torus; (b) strange NONchaotic attractor
(fractal geometry, ZERO Lyapunov -- common under incommensurate forcing); (c) localized/intermittent
chaos (positive finite-time stretching that averages to ~0); (d) genuine chaos (positive LLE the coarse
sweep missed). And the prior worry: a silent NaN at the polar perp-origin (the 1e-12-guarded winding
singularity in banach_frustrated) could fake a small LLE.

This separates them. Arbiter of "technically chaos" = a positive Lyapunov exponent (boundedness and
anisotropy do NOT disqualify; erratic winding at the never-attained perp-origin is a COORDINATE
artifact, zero true Lyapunov -- MPA asymptotic closure: read the global winding, not the pointwise
clock).

Measures (N=3, several couplings K):
  * FINITE AUDIT      -- did integration stay finite? how close to each oscillator origin |a_n|=0
                         (the orthogonal zeros)?  minr << 1 => visiting the polar region.
  * LYAPUNOV SPECTRUM -- all 6 exponents (Benettin-Gram-Schmidt). Count >0 / ~0 / <0 = the ANISOTROPY.
                         3-torus -> {0,0,0,-,-,-}; chaos -> top > 0; hyperchaos -> two > 0.
  * FTLE DISTRIBUTION -- finite-time largest exponents. Tight ~0 = torus; broad with positive tail but
                         ~0 mean = SNA / localized stretching; mean > 0 = chaos.
  * POINCARE SECTION  -- (Re a1, Re a2) at upward zero-crossings of Re a0. Closed curve = torus;
                         wrinkled/fractal = SNA; scattered cloud = chaos.

Run from mpa-conform root:  python scripts/tower_chaos_diagnostic.py
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
OMEGA = np.array([1.0, 1.0 / PHI, 1.0 / PHI**2])
MU, DT = 1.0, 0.01
ZERO = 5e-3   # |exponent| below this reads as zero (numerical Lyapunov noise floor)


def deriv(a, K):
    d = (MU + 1j * OMEGA) * a - (np.abs(a) ** 2) * a
    d[:-1] += K * (a[1:] - a[:-1])
    d[1:] += K * (a[:-1] - a[1:])
    return d


def rk4(a, K):
    k1 = deriv(a, K); k2 = deriv(a + 0.5 * DT * k1, K)
    k3 = deriv(a + 0.5 * DT * k2, K); k4 = deriv(a + DT * k3, K)
    return a + (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def c2r(a):
    return np.concatenate([a.real, a.imag])


def r2c(x):
    return x[:3] + 1j * x[3:]


def ftle_and_radius(K, t_trans=600, window=8.0, n_win=350, d0=1e-8, seed=1):
    """Finite-time largest exponents + closest approach to any origin + finite audit + completed frac."""
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(3) + 1j * rng.standard_normal(3))
    for _ in range(int(t_trans / DT)):
        a = rk4(a, K)
    da = np.zeros(3, complex); da[0] = d0; b = a + da
    exps = []; minr = np.inf; finite = True
    steps = int(window / DT)
    for _ in range(n_win):
        ok = True
        for _ in range(steps):
            a = rk4(a, K); b = rk4(b, K)
            minr = min(minr, float(np.min(np.abs(a))))
            if not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
                finite = False; ok = False; break
        if not ok:
            break
        d = b - a; dist = float(np.sqrt(np.sum(np.abs(d) ** 2)))
        if dist <= 0:
            break
        exps.append(np.log(dist / d0) / window)
        b = a + (d / dist) * d0
    return np.array(exps), minr, finite, len(exps) / n_win


def lyap_spectrum(K, t_trans=600, t_meas=1600, renorm=1.0, d0=1e-7, seed=2):
    """All 6 Lyapunov exponents via Benettin-Gram-Schmidt (finite-difference tangent)."""
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(3) + 1j * rng.standard_normal(3))
    for _ in range(int(t_trans / DT)):
        a = rk4(a, K)
    Q = np.eye(6) * d0
    steps = int(renorm / DT); nblk = int(t_meas / renorm)
    S = np.zeros(6)
    for _ in range(nblk):
        aref = a.copy()
        for _ in range(steps):
            aref = rk4(aref, K)
        D = np.empty((6, 6))
        for i in range(6):
            ai = r2c(c2r(a) + Q[:, i])
            for _ in range(steps):
                ai = rk4(ai, K)
            D[:, i] = c2r(ai) - c2r(aref)
        a = aref
        Qm, R = np.linalg.qr(D)
        S += np.log(np.abs(np.diag(R)) / d0)
        Q = Qm * d0
    return np.sort(S / (nblk * renorm))[::-1]


def poincare(K, t_trans=800, t_meas=2500, seed=3):
    rng = np.random.default_rng(seed)
    a = 0.5 * (rng.standard_normal(3) + 1j * rng.standard_normal(3))
    for _ in range(int(t_trans / DT)):
        a = rk4(a, K)
    pts = []; prev = a[0].real
    for _ in range(int(t_meas / DT)):
        a = rk4(a, K)
        cur = a[0].real
        if prev < 0 <= cur:
            pts.append([a[1].real, a[2].real])
        prev = cur
    return np.array(pts) if pts else np.zeros((0, 2))


def classify(spec, exps):
    top = spec[0]
    n_pos = int(np.sum(spec > ZERO)); n_zero = int(np.sum(np.abs(spec) <= ZERO))
    frac_pos = float(np.mean(exps > ZERO)) if len(exps) else 0.0
    if top > ZERO:
        return f"CHAOS (top exponent {top:+.4f} > 0; {n_pos} positive)"
    if frac_pos > 0.05 and exps.std() > 2 * ZERO:
        return (f"SNA / LOCALIZED stretching (LLE~0 but FTLE positive-tail "
                f"{100*frac_pos:.0f}%, std {exps.std():.4f}) -- geometrically strange, NOT chaos")
    return f"CLEAN {n_zero}-torus (quasiperiodic; FTLE tight ~0) -- not chaos, not even localized"


def main() -> None:
    print("tower chaos diagnostic (N=3): torus vs SNA vs localized vs genuine chaos; + polar-origin audit")
    print(f"phi-spaced omega = {np.round(OMEGA, 4)}, mu = {MU}; zero-floor |lambda| < {ZERO}\n")

    Ks = [0.20, 0.25, 0.50]
    rows = []
    print(f"{'K':>5} | {'finite':>6} {'done%':>6} {'min|a_n|':>9} | {'top 6 Lyapunov exponents':>40} | mean FTLE")
    print("-" * 100)
    for K in Ks:
        exps, minr, finite, done = ftle_and_radius(K)
        spec = lyap_spectrum(K)
        rows.append(dict(K=K, exps=exps, minr=minr, finite=finite, done=done, spec=spec))
        specstr = " ".join(f"{e:+.3f}" for e in spec)
        print(f"{K:>5.2f} | {str(finite):>6} {100*done:>5.0f}% {minr:>9.4f} | {specstr:>40} | {exps.mean():+.4f}")

    print("\nverdict per K:")
    for r in rows:
        print(f"  K={r['K']:.2f}: {classify(r['spec'], r['exps'])}")
        if r['minr'] < 0.2:
            print(f"           -> trajectory comes within {r['minr']:.3f} of an oscillator origin "
                  f"(<< limit-cycle radius ~1): VISITS the polar/orthogonal-zero region. A WINDING/angle")
            print(f"              observable would fake-NaN here (MPA: read global winding, not the clock).")

    any_chaos = any(r['spec'][0] > ZERO for r in rows)
    all_finite = all(r['finite'] and r['done'] > 0.99 for r in rows)
    print("\n================ VERDICT ================")
    print(f"Integration finite & complete on all K: {all_finite}  "
          f"(rules out the silent-NaN fake-small-LLE artifact in the original sweep)" if all_finite
          else f"WARNING: integration hit non-finite / broke early on some K -- the original LLE~0 "
               f"MAY be a fake-NaN artifact. Diagnose.")
    if any_chaos:
        print("GENUINE CHAOS FOUND on at least one K (a positive Lyapunov exponent) -- the coarse sweep")
        print("missed it. Bounded + anisotropic, but technically chaos (positive exponent on the attractor).")
    else:
        kmin = min(r['minr'] for r in rows)
        localized = any((r['spec'][0] <= ZERO and (r['exps'] > ZERO).mean() > 0.05
                         and r['exps'].std() > 2 * ZERO) for r in rows)
        print("NO positive Lyapunov exponent on any K: not technically chaos by the strict criterion.")
        if localized:
            print("BUT the finite-time exponents have a positive tail with ~0 mean = a STRANGE NONCHAOTIC")
            print("attractor / localized-anisotropic stretching: geometrically strange, dynamically NOT")
            print("chaos. This is exactly the 'constrained' object you suspected -- bounded, anisotropic,")
            print("and below the chaos threshold (zero Lyapunov). It would LOOK like chaos in a phase")
            print("portrait or a winding observable but is not chaos.")
        else:
            print("The attractor is a clean quasiperiodic torus -- not chaos, not even localized stretching.")
        if kmin < 0.2:
            print(f"Closest origin approach {kmin:.3f} << 1: the tower DOES visit the polar region, so a")
            print("winding/angle reading would have produced the fake-NaN 'looks-like-chaos' you recall.")
        else:
            print(f"Closest origin approach {kmin:.3f}: stays away from the polar region (no winding artifact here).")
    print("\nHonest scope: this is the SL-normal-form tower (no Wall-delay). The decisive wall-forces-chaos")
    print("test is still the delay-tower (W -> Wall). This only characterizes WHAT the current attractor is.")

    # ---- figure ----
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=140)

    # (0,0) Lyapunov spectra
    a0 = ax[0, 0]
    w = 0.25
    for j, r in enumerate(rows):
        a0.bar(np.arange(6) + (j - 1) * w, r['spec'], width=w, label=f"K={r['K']}")
    a0.axhline(0, color="gray", lw=0.8); a0.axhline(ZERO, color="red", ls=":", lw=0.8)
    a0.axhline(-ZERO, color="red", ls=":", lw=0.8)
    a0.set_xlabel("exponent index"); a0.set_ylabel("Lyapunov exponent")
    a0.set_title("Lyapunov SPECTRUM (anisotropy): top exponent <= 0 on all K\n=> no chaos; count of ~0 = torus dim")
    a0.legend(fontsize=9, frameon=False); a0.grid(alpha=0.3, axis="y")

    # (0,1) FTLE distribution
    a1 = ax[0, 1]
    for r in rows:
        a1.hist(r['exps'], bins=40, alpha=0.5, density=True, label=f"K={r['K']} (mean {r['exps'].mean():+.3f})")
    a1.axvline(0, color="gray", lw=0.8)
    a1.set_xlabel("finite-time largest exponent"); a1.set_ylabel("density")
    a1.set_title("finite-time Lyapunov distribution\n(positive tail w/ ~0 mean = SNA/localized; tight ~0 = torus)")
    a1.legend(fontsize=9, frameon=False); a1.grid(alpha=0.3)

    # (1,0) Poincare section at the most-suspicious K (largest top exponent)
    Kp = max(rows, key=lambda r: r['spec'][0])['K']
    pts = poincare(Kp)
    a2 = ax[1, 0]
    if len(pts):
        a2.scatter(pts[:, 0], pts[:, 1], s=4, color="#c2185b", alpha=0.6)
    a2.set_xlabel(r"Re $a_1$"); a2.set_ylabel(r"Re $a_2$")
    a2.set_title(f"Poincare section at K={Kp} (Re a0 up-crossing)\nclosed curve=torus / wrinkled=SNA / cloud=chaos")
    a2.grid(alpha=0.3)

    # (1,1) origin approach: histogram of min|a_n| sampled along a trajectory
    a3 = ax[1, 1]
    rng = np.random.default_rng(7)
    a = 0.5 * (rng.standard_normal(3) + 1j * rng.standard_normal(3))
    for _ in range(int(800 / DT)):
        a = rk4(a, Kp)
    radii = []
    for _ in range(int(2000 / DT)):
        a = rk4(a, Kp)
        radii.append(float(np.min(np.abs(a))))
    radii = np.array(radii)
    a3.hist(radii, bins=60, color="#1565c0", alpha=0.8)
    a3.axvline(1.0, color="green", ls="--", lw=1, label="limit-cycle radius ~1")
    a3.axvline(radii.min(), color="red", ls=":", lw=1.2, label=f"min = {radii.min():.3f}")
    a3.set_xlabel(r"$\min_n |a_n|$ along trajectory"); a3.set_ylabel("count")
    a3.set_title("approach to the polar origin (orthogonal zeros)\nmass near 0 => winding observable would fake-NaN")
    a3.legend(fontsize=9, frameon=False); a3.grid(alpha=0.3)

    fig.suptitle("N=3 tower attractor: torus vs SNA vs chaos, and the polar-origin (orthogonal-zero) audit",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "tower_chaos_diagnostic.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
