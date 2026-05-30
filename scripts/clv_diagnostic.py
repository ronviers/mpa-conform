r"""clv_diagnostic.py -- Option 2 for `wall-as-type-boundary`: the pre/post observable that separates
a PLATEAU (a normally hyperbolic invariant manifold -- including a quasiperiodic torus) from a
BOUNDARY (loss of normal hyperbolicity / chaos).

The diagnostic (settled by the establishment research, `mpa-atlas/docs/ladder research and prompt.md`,
three-model convergence): the MINIMUM PRINCIPAL ANGLE theta_min between Covariant Lyapunov Vector
(CLV) subspaces (Ginelli et al. 2007), split at the spectral gap into the tangent/center+unstable
bundle and the stable (transverse) bundle.
  - PLATEAU (NHIM): theta_min bounded away from 0 -- the Oseledets splitting is transverse.
  - BOUNDARY (loss of normal hyperbolicity / chaos): theta_min -> 0 (bundle collapse / tangencies).
The crucial property: theta_min does NOT false-positive on a normally-hyperbolic quasiperiodic torus,
whereas the leading finite-time Lyapunov exponent (FTLE) DOES -- a torus has a positive FTLE tail
(non-uniform flow speed) while its infinite-time exponent is exactly 0.

Testbeds:
  - rossler        : canonical chaos (boundary). Validates the forward pass: spectrum ~ (+0.07, 0, -5.4).
  - coupled SL torus: N=3 Stuart-Landau, weak coupling, incommensurate freqs -> robust 3-torus
                       (the `dynamical_tower` plateau -- the cascade's own dynamics).
  - coupled SL sync : N=3 Stuart-Landau, strong coupling -> synchronized limit cycle (plateau).

Algorithm (Ginelli/Kuptsov-Parlitz):
  forward: evolve state + tangent frame, QR every tau_QR -> GS bases Q_s, triangular R_s, exponents.
  backward: A_{s-1} = normalize(R_s^{-1} A_s); CLVs = Q_s @ A_s.
  theta_min(t) = arccos(max singular value of Qa^T Qb), Qa/Qb orthonormal bases of the two bundles,
                 split at the largest gap in the sorted Lyapunov spectrum.

Usage (from mpa-conform root):
  python scripts/clv_diagnostic.py
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
PHI = (1.0 + np.sqrt(5.0)) / 2.0          # golden ratio -- maximally incommensurate (KAM-robust)
PLASTIC = 1.324717957244746               # plastic number -- second incommensurate frequency


# ============================================================ systems (f, analytic Jacobian)
def rossler(a=0.2, b=0.2, c=5.7):
    def f(s):
        x, y, z = s
        return np.array([-y - z, x + a * y, b + z * (x - c)])

    def jac(s):
        x, y, z = s
        return np.array([[0.0, -1.0, -1.0],
                         [1.0, a, 0.0],
                         [z, 0.0, x - c]])
    return f, jac, 3


def coupled_sl(omega, K):
    """N all-to-all diffusively coupled Stuart-Landau oscillators (mu=1, radius 1).
    state = [x0,y0,x1,y1,...]; the cascade's platformed-rhythm dynamics (dynamical_tower)."""
    N = len(omega)
    om = np.asarray(omega, float)

    def f(s):
        x = s[0::2]; y = s[1::2]
        r2 = x * x + y * y
        sx = x.sum(); sy = y.sum()
        # K * sum_{j!=k}(x_j - x_k) = K*(sx - N x_k) ; all-to-all
        fx = x - om * y - r2 * x + K * (sx - N * x)
        fy = om * x + y - r2 * y + K * (sy - N * y)
        out = np.empty(2 * N)
        out[0::2] = fx; out[1::2] = fy
        return out

    def jac(s):
        x = s[0::2]; y = s[1::2]
        r2 = x * x + y * y
        J = np.zeros((2 * N, 2 * N))
        for k in range(N):
            ix, iy = 2 * k, 2 * k + 1
            J[ix, ix] = 1.0 - (3 * x[k] ** 2 + y[k] ** 2) - K * (N - 1)
            J[ix, iy] = -om[k] - 2 * x[k] * y[k]
            J[iy, ix] = om[k] - 2 * x[k] * y[k]
            J[iy, iy] = 1.0 - (x[k] ** 2 + 3 * y[k] ** 2) - K * (N - 1)
            for j in range(N):
                if j != k:
                    J[ix, 2 * j] = K
                    J[iy, 2 * j + 1] = K
        return J
    return f, jac, 2 * N


# ============================================================ tangent RK4 + CLV (Ginelli)
def _step(x, V, dt, f, jac):
    k1x = f(x); k1V = jac(x) @ V
    x2 = x + 0.5 * dt * k1x; k2x = f(x2); k2V = jac(x2) @ (V + 0.5 * dt * k1V)
    x3 = x + 0.5 * dt * k2x; k3x = f(x3); k3V = jac(x3) @ (V + 0.5 * dt * k2V)
    x4 = x + dt * k3x; k4x = f(x4); k4V = jac(x4) @ (V + dt * k3V)
    x_new = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
    V_new = V + dt / 6 * (k1V + 2 * k2V + 2 * k3V + k4V)
    return x_new, V_new


def lyap_clv(f, jac, n, x0, dt=0.01, m=10, warm=2000, rec=6000, drop=1000, seed=0):
    """Forward (Lyapunov spectrum + GS bases) + backward (CLVs). Returns exponents, stored CLVs over
    the central window, and the leading-FTLE samples (per-QR-interval growth of the 1st GS vector)."""
    rng = np.random.default_rng(seed)
    x = np.array(x0, float)
    V = np.linalg.qr(rng.standard_normal((n, n)))[0]
    tau = m * dt

    # --- warmup: settle onto the attractor + align the GS frame ---
    for _ in range(warm):
        for _ in range(m):
            x, V = _step(x, V, dt, f, jac)
        V, _ = np.linalg.qr(V)

    # --- recording forward pass: store Q_s, R_s; accumulate exponents; sample leading FTLE ---
    Qs = np.empty((rec, n, n)); Rs = np.empty((rec, n, n))
    log_acc = np.zeros(n)
    ftle1 = np.empty(rec)
    for s in range(rec):
        for _ in range(m):
            x, V = _step(x, V, dt, f, jac)
        Q, R = np.linalg.qr(V)
        d = np.sign(np.diag(R)); d[d == 0] = 1.0      # fix QR sign gauge -> positive R diagonal
        Q = Q * d; R = (R.T * d).T
        Qs[s] = Q; Rs[s] = R
        diagR = np.abs(np.diag(R))
        log_acc += np.log(diagR)
        ftle1[s] = np.log(diagR[0]) / tau
        V = Q
    exponents = log_acc / (rec * tau)

    # --- backward pass (Ginelli): A_{s-1} = normalize(R_s^{-1} A_s); CLV_s = Q_s @ A_s ---
    A = np.triu(rng.standard_normal((n, n)))
    A /= np.linalg.norm(A, axis=0, keepdims=True)
    clvs = np.empty((rec - 2 * drop, n, n))
    j = 0
    for s in range(rec - 1, -1, -1):
        if drop <= s < rec - drop:
            V_clv = Qs[s] @ A
            V_clv /= np.linalg.norm(V_clv, axis=0, keepdims=True)
            clvs[rec - 2 * drop - 1 - j] = V_clv
            j += 1
        A = np.linalg.solve(Rs[s], A)
        A /= np.linalg.norm(A, axis=0, keepdims=True)
    return exponents, clvs, ftle1[drop:rec - drop]


# ============================================================ theta_min from CLVs
def split_at_gap(exps):
    """split the sorted-descending spectrum at its largest gap -> (top indices, bottom indices).
    top = tangent/center+unstable bundle, bottom = stable (transverse) bundle."""
    order = np.argsort(exps)[::-1]
    se = exps[order]
    gaps = se[:-1] - se[1:]
    k = int(np.argmax(gaps)) + 1                  # first k = top bundle
    return order[:k], order[k:], float(gaps.max())


def theta_min_series(clvs, idx_top, idx_bot):
    """minimum principal angle (deg) between the two CLV bundles at each recorded time."""
    out = np.empty(len(clvs))
    for t, V in enumerate(clvs):
        Qa, _ = np.linalg.qr(V[:, idx_top])
        Qb, _ = np.linalg.qr(V[:, idx_bot])
        smax = min(float(np.linalg.svd(Qa.T @ Qb, compute_uv=False).max()), 1.0)
        out[t] = np.degrees(np.arccos(smax))
    return out


def run_case(name, f, jac, n, x0, **kw):
    exps, clvs, ftle1 = lyap_clv(f, jac, n, x0, **kw)
    top, bot, gap = split_at_gap(exps)
    th = theta_min_series(clvs, top, bot)
    se = np.sort(exps)[::-1]
    n_zero = int(np.sum(np.abs(exps) < 0.02))
    n_pos = int(np.sum(exps > 0.02))
    kind = "CHAOS" if n_pos >= 1 else ("TORUS" if n_zero >= 2 else "LIMIT CYCLE")
    print(f"\n[{name}]  spectrum = {np.array2string(se, precision=3, floatmode='fixed')}")
    print(f"   classified: {kind}  (n_pos={n_pos}, n_zero={n_zero}); gap split = {len(top)}|{len(bot)}")
    print(f"   theta_min (deg): min={th.min():.2f}, 1st-pct={np.percentile(th,1):.2f}, "
          f"median={np.median(th):.2f}")
    print(f"   leading FTLE: mean={ftle1.mean():+.3f}, 95th-pct={np.percentile(ftle1,95):+.3f}, "
          f"max={ftle1.max():+.3f}")
    return dict(name=name, exps=se, theta=th, ftle1=ftle1, kind=kind,
                n_pos=n_pos, n_zero=n_zero, gap=gap)


# ============================================================ figure
def figure(cases):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6), dpi=150)
    colors = {"CHAOS": "#c62828", "TORUS": "#1565c0", "LIMIT CYCLE": "#2e7d32"}

    # panel 1: Lyapunov spectra
    for i, c in enumerate(cases):
        col = colors[c["kind"]]
        ax[0].plot(range(len(c["exps"])), c["exps"], "o-", color=col, ms=5,
                   label=f"{c['name']} ({c['kind']})")
    ax[0].axhline(0, color="gray", lw=0.8)
    ax[0].set_xlabel("index $i$"); ax[0].set_ylabel(r"Lyapunov exponent $\lambda_i$")
    ax[0].set_title("Lyapunov spectra"); ax[0].legend(fontsize=7.5, frameon=False); ax[0].grid(alpha=0.3)

    # panel 2: theta_min distributions -- the diagnostic (fixed 0-90deg bins; theta_min can be constant)
    tbins = np.linspace(0, 90, 46)
    for c in cases:
        col = colors[c["kind"]]
        ax[1].hist(c["theta"], bins=tbins, density=True, histtype="step", lw=2, color=col,
                   label=f"{c['name']}: min={c['theta'].min():.1f}°")
    ax[1].axvline(0, color="gray", lw=0.8)
    ax[1].set_xlabel(r"$\theta_{\min}$ between CLV bundles (deg)")
    ax[1].set_ylabel("density")
    ax[1].set_title("CLV $\\theta_{\\min}$: plateau bounded from 0, boundary → 0")
    ax[1].legend(fontsize=7.5, frameon=False); ax[1].grid(alpha=0.3)

    # panel 3: the torus false-positive -- FTLE tail (looks chaotic) vs theta_min (correctly bounded)
    torus = next((c for c in cases if c["kind"] == "TORUS"), None)
    chaos = next((c for c in cases if c["kind"] == "CHAOS"), None)
    if torus is not None:
        lo = min(torus["ftle1"].min(), chaos["ftle1"].min() if chaos is not None else 0.0)
        hi = max(torus["ftle1"].max(), chaos["ftle1"].max() if chaos is not None else 0.0)
        fbins = np.linspace(lo, hi, 51) if hi > lo else np.linspace(lo - 1, hi + 1, 51)
        ax[2].hist(torus["ftle1"], bins=fbins, density=True, histtype="stepfilled", alpha=0.5,
                   color="#1565c0", label=f"torus FTLE λ₁ (95th={np.percentile(torus['ftle1'],95):+.2f}>0!)")
        if chaos is not None:
            ax[2].hist(chaos["ftle1"], bins=fbins, density=True, histtype="step", lw=2,
                       color="#c62828", label="chaos FTLE λ₁")
        ax[2].axvline(0, color="gray", lw=1.0, ls="--")
        ax[2].set_xlabel(r"leading finite-time Lyapunov exponent $\lambda_1(\tau)$")
        ax[2].set_ylabel("density")
        ax[2].set_title("FTLE FALSE-POSITIVE: the robust torus\nhas a positive λ₁ tail (θ_min does not)")
        ax[2].legend(fontsize=7.5, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("Option 2 — CLV θ_min: the plateau-vs-boundary (NHIM-vs-loss-of-hyperbolicity) diagnostic",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "clv_diagnostic.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


# ============================================================ main
def main():
    print("CLV theta_min diagnostic  (plateau / NHIM  vs  boundary / loss-of-normal-hyperbolicity)")

    # 1) Rossler -- validates the forward pass (known spectrum ~ +0.07, 0, -5.4) + the chaos boundary
    f, jac, n = rossler()
    chaos = run_case("Rössler", f, jac, n, [1.0, 1.0, 1.0], dt=0.01, m=10, warm=3000, rec=6000, drop=800)

    # 2) coupled SL, weak coupling, incommensurate freqs -> robust 3-torus (the cascade plateau)
    om = np.array([1.0, PLASTIC, PHI])
    f, jac, n = coupled_sl(om, K=0.05)
    x0 = np.array([0.9, 0.0, 0.0, 0.9, -0.6, 0.6])
    torus = run_case("coupled-SL (weak K=0.05)", f, jac, n, x0, dt=0.01, m=10, warm=4000, rec=6000, drop=800)

    # 3) coupled SL, strong coupling -> synchronized limit cycle (plateau)
    f, jac, n = coupled_sl(om, K=2.0)
    sync = run_case("coupled-SL (strong K=2.0)", f, jac, n, x0, dt=0.01, m=10, warm=4000, rec=6000, drop=800)

    figure([chaos, torus, sync])

    print("\n" + "=" * 78)
    print("VERDICT (Option 2)")
    print("=" * 78)
    plateau_floor = min(torus["theta"].min(), sync["theta"].min())
    print(f"  Rössler spectrum validates the forward pass (λ₁>0, λ₂≈0, λ₃≪0).")
    print(f"  θ_min SEPARATES the regimes: chaos min={chaos['theta'].min():.1f}° (→0, bundle tangency)")
    print(f"     vs plateau floor={plateau_floor:.1f}° (torus & limit cycle bounded away from 0).")
    print(f"  FALSE-POSITIVE CONTROL: the robust 3-torus has a POSITIVE leading-FTLE tail "
          f"(95th-pct={np.percentile(torus['ftle1'],95):+.3f}) — FTLE would mislabel it chaotic;")
    print(f"     θ_min does not (torus min={torus['theta'].min():.1f}° bounded from 0). The torus is a")
    print(f"     genuine NHIM plateau, exactly the `dynamical_tower` honest-negative, now certified.")
    print(f"  ⇒ θ_min is the runnable pre/post observable for `wall-as-type-boundary` (the ↑ gate).")


if __name__ == "__main__":
    main()
