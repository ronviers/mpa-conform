"""freeze — coupling_ramp_v7  (bespoke, a metric-axis sweep, brittle by design)

The METRIC-boundary-blur probe. v6 showed the 1<->10 cut is TOPOLOGICALLY sharp
(reciprocity is discrete — no continuous knob smears the class). The open question v6
left: does a category smear along a CONTINUOUS (metric) axis? This sweep takes v6's
MATCHED (reciprocal, symmetric-coupled, Cat-1) community and dials its coupling strength
g_s UP toward the stability threshold g_s -> gamma, asking whether the reversible
relaxation BLURS — toward oscillation, toward a current, or toward glassy aging — or
whether it stays cleanly Cat-1 while the operating point approaches a critical edge.

Substrate: the v6 matched community, M = -gamma I + g_s S, S = P^T [[0,1],[1,0]] P
(symmetric, annihilates the (1,1,1) mode, plane eigenvalues +/-1), gamma=1.0, D=0.1.
Sweep g_s = [0.3, 0.6, 0.8, 0.9, 0.95]. Plane eigenvalues are -gamma +/- g_s (ALWAYS
REAL — symmetric coupling), so:
  - the SLOW mode -gamma + g_s -> 0 as g_s -> gamma: the relaxation time
    tau_slow = 1/(gamma - g_s) DIVERGES (critical slowing), and the stationary slow-mode
    variance D/(gamma - g_s) diverges too (susceptibility divergence). At g_s = gamma the
    stationary state ceases to exist (marginal); above it the slow mode is unstable.
  - the spectrum stays REAL at every g_s -> NO oscillation ever develops.
  - the coupling stays SYMMETRIC at every g_s -> detailed balance, <sigma> = 0, Cxy = Cyx,
    zero current -> the FDR locus stays affine (X = 1) the whole way.

So the sealed truth: dialing g_s up does NOT change the KIND of system (it stays a
reversible Cat-1 relaxation — no oscillation, no current, X = 1), but the operating point
approaches an INSTABILITY/critical edge via critical slowing, and the headroom to that edge
(the spectral gap gamma - g_s) is readable off the sweep band. The metric axis grounds the
two-sided headroom-to-instability that ONE operating point could not (v1's owed vector), and
tests whether Cat-1 smears toward Cat-10 (current), an oscillatory onset, or Cat-8 (aging):
it does not — the only thing that changes is the gap (a within-category headroom), so the
category is sharp along the metric axis, the boundary it approaches is a critical point.

ANCHOR: g_s = 0.6 (level 1) is v6's MATCHED community (community 0) exactly -> its placement
must reproduce v6 (real eigenvalues -0.4/-1.6, <sigma>=0, Cxy=Cyx, |Cxy+Cyx| peak ~1.199).

Ground truth is exact (linear OU), computed HERE from each structure, never via conform.
BLINDING: the emitted CSV carries only (level, tau, C, chi, Cxy, Cyx, phiMean, phiVar) — a
neutral integer 'level' (which way the researcher turned the knob), NO g_s/gamma/D, no
spectral gap, no tau_slow, no "critical"/"reversible"/"X" label. What the cranking DOES
is exactly what conform must read out.

Run:  python H:/mpa-conform/blockin/questions/coupling_ramp_v7/freeze_coupling_ramp.py
Emits: data/coupling_ramp_v7.frozen.csv  (the blind artifact)
       prints the SEALED ground truth for the author / human eyeball.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov

sys.path.insert(0, "H:/mpa-central/library")
import banach_frustrated as bf  # noqa: E402  (for the rotation-plane projector P)

GAMMA, D = 1.0, 0.1
G_SWEEP = [0.3, 0.6, 0.8, 0.9, 0.95]   # level 1 (g_s=0.6) == v6 matched community (anchor)
ANCHOR_LEVEL = 1
SEED = 7
DT = 0.01

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "coupling_ramp_v7.frozen.csv"

P = bf.P
S_SYM = P.T @ np.array([[0.0, 1.0], [1.0, 0.0]]) @ P    # symmetric reciprocal coupling


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire). Diagnose, do not fill.")
    return x


def exact(M, D):
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
    Dmat = D * np.eye(3)
    Omega = M + Dmat @ np.linalg.inv(Sigma)
    sigma = float(np.trace(Omega.T @ np.linalg.inv(Dmat) @ Omega @ Sigma))
    ev = np.linalg.eigvals(M)
    omega = float(np.max(np.abs(ev.imag)))
    return Sigma, sigma, ev, omega


def plane_correlations(M, Sigma, t):
    c0 = P @ Sigma @ P.T
    scale = 0.5 * (c0[0, 0] + c0[1, 1])
    C = np.empty_like(t); Cxy = np.empty_like(t); Cyx = np.empty_like(t); Rxx = np.empty_like(t)
    for i, ti in enumerate(t):
        Pr = expm(M * ti)
        c = P @ Pr @ Sigma @ P.T
        r = P @ Pr @ P.T
        C[i] = 0.5 * (c[0, 0] + c[1, 1]) / scale
        Cxy[i] = c[0, 1] / scale
        Cyx[i] = c[1, 0] / scale
        Rxx[i] = r[0, 0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (Rxx[1:] + Rxx[:-1]) * np.diff(t))])
    return C, chi, Cxy, Cyx


def resolved_winding(M, D, t_grid, rng, tau_slow, n_real=1500):
    """Winding-angle ensemble. For a reversible (symmetric) community the drift is ~0 (no
    current); we confirm that and report phiVar (pure diffusion). Equilibration scales with
    tau_slow so the slow mode is settled even near the critical edge."""
    sd = np.sqrt(2.0 * D * DT)
    n_eq = max(3000, int(8.0 * tau_slow / DT))
    z = rng.standard_normal((n_real, 3)) * np.sqrt(D)
    for _ in range(n_eq):
        z = z + (z @ M.T) * DT + rng.standard_normal((n_real, 3)) * sd
    steps = np.maximum(1, np.round(t_grid / DT).astype(int))
    n_steps = int(steps[-1])
    u = z @ P.T
    phi = np.zeros(n_real)
    mean = np.empty_like(t_grid); var = np.empty_like(t_grid)
    k = 0
    for s in range(1, n_steps + 1):
        z = z + (z @ M.T) * DT + rng.standard_normal((n_real, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        u = un
        while k < len(steps) and steps[k] == s:
            mean[k] = phi.mean(); var[k] = phi.var(ddof=1); k += 1
    return finite("phiMean", mean), finite("phiVar", var)


def fdr_locus_slope(C, chi):
    """Slope + R^2 of chi vs (C(0)-C(tau)) — the universal FDR readout. Affine with a single
    slope (high R^2) == equilibrium / FDT holds (X=1, NOT aging). A two-slope / low-R^2 locus
    would be the aging (X<1) signature. Computed for the SEAL only (the answerer forms its own)."""
    x = C[0] - C
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, intercept), *_ = np.linalg.lstsq(A, chi, rcond=None)
    pred = A @ np.array([slope, intercept])
    ss_res = float(np.sum((chi - pred) ** 2))
    ss_tot = float(np.sum((chi - chi.mean()) ** 2)) + 1e-30
    return float(slope), 1.0 - ss_res / ss_tot


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    rows_meta = []
    csv_lines = []

    for level, g_s in enumerate(G_SWEEP):
        M = -GAMMA * np.eye(3) + g_s * S_SYM
        Sigma, sigma, ev, omega = exact(M, D)
        ev_real = np.sort(ev.real)
        gap = GAMMA - g_s                      # spectral gap = -(slowest plane eigenvalue)
        tau_slow = 1.0 / gap
        # window: ~8 e-foldings of the SLOW mode so the divergence shows honestly per level
        t_max = 8.0 * tau_slow
        t = np.linspace(t_max / 400.0, t_max, 120)
        C, chi, Cxy, Cyx = plane_correlations(M, Sigma, t)
        phiMean, phiVar = resolved_winding(M, D, t, rng, tau_slow)
        slope, r2 = fdr_locus_slope(C, chi)
        asym_peak = float(np.max(np.abs(Cxy - Cyx)))
        sym_peak = float(np.max(np.abs(Cxy + Cyx)))
        drift = float(phiMean[-1]) / float(t[-1])
        var_slow = float(D / gap)              # diverging stationary slow-mode variance
        rows_meta.append(dict(level=level, g_s=g_s, ev=ev_real, sigma=sigma, omega=omega,
                              gap=gap, tau_slow=tau_slow, asym_peak=asym_peak,
                              sym_peak=sym_peak, drift=drift, fdr_slope=slope, fdr_r2=r2,
                              var_slow=var_slow, tmax=float(t[-1]),
                              c_halflife=float(t[np.argmin(np.abs(C - 0.5))]),
                              cmin=float(C.min())))
        for ti, ci, xi, cxy, cyx, pm, pv in zip(t, C, chi, Cxy, Cyx, phiMean, phiVar):
            csv_lines.append(f"{level},{ti:.6f},{ci:.6f},{xi:.6f},{cxy:.6f},{cyx:.6f},{pm:.6f},{pv:.6f}")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# coupling_ramp_v7 — ONE matched (mutual-interaction) three-population\n")
        f.write("#   community observed at FIVE increasing interaction-strength settings.\n")
        f.write("# 'level' is a neutral 0..4 index = how far the strength knob was turned up\n")
        f.write("#   (the strength magnitudes themselves are NOT in the file).\n")
        f.write("# columns: level, tau (the community's own clock — a lag for the two-point\n")
        f.write("#   columns, an elapsed time for the winding columns), C (normalized\n")
        f.write("#   turnover-plane autocorr), chi (integrated response), Cxy / Cyx (the two\n")
        f.write("#   directed cross-correlations), phiMean / phiVar (mean & variance of the\n")
        f.write("#   cumulative net turnover angle). Each level has its OWN settling window.\n")
        f.write("# All columns dimensionless (angle in radians). Five operating points.\n")
        f.write("# Generated by the community's own exact linear propagator + sim — not via conform.\n")
        f.write("level,tau,C,chi,Cxy,Cyx,phiMean,phiVar\n")
        f.write("\n".join(csv_lines) + "\n")

    # ---- sealed truth ----
    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"substrate: v6 MATCHED community (symmetric coupling S), gamma={GAMMA}, D={D};  seed={SEED}")
    print(f"sweep g_s = {G_SWEEP}  (level {ANCHOR_LEVEL}, g_s=0.6, == v6 community 0 = ANCHOR)\n")
    hdr = (f"{'lvl':>3} {'g_s':>5} | {'eig(plane)':>16} {'<sigma>':>8} {'omega':>6} | "
           f"{'gap':>5} {'tau_slow':>8} {'Var_slow':>9} | {'|Cxy-Cyx|':>9} {'|Cxy+Cyx|':>9} "
           f"{'drift':>7} | {'FDRslope':>8} {'FDR_R2':>7}")
    print(hdr); print("-" * len(hdr))
    for m in rows_meta:
        evs = f"{m['ev'][0]:+.3f},{m['ev'][2]:+.3f}"   # slowest & fastest plane (sorted asc: [slow_uniform?])
        print(f"{m['level']:>3} {m['g_s']:>5.2f} | {evs:>16} {m['sigma']:>8.4f} {m['omega']:>6.3f} | "
              f"{m['gap']:>5.2f} {m['tau_slow']:>8.2f} {m['var_slow']:>9.3f} | {m['asym_peak']:>9.4f} "
              f"{m['sym_peak']:>9.4f} {m['drift']:>+7.3f} | {m['fdr_slope']:>8.4f} {m['fdr_r2']:>7.4f}")

    print("\nREAD:")
    print("  - spectrum REAL at every level (omega=0 throughout) -> NO oscillation onset.")
    print("  - <sigma>=0 and Cxy=Cyx (|Cxy-Cyx|~0) and drift~0 at every level -> NO current,")
    print("    detailed balance holds the whole way (the class stays REVERSIBLE / Cat 1).")
    print("  - FDR locus AFFINE (R^2~1) with a single slope at every level -> X=1, NOT aging")
    print("    (Cat-8 aging would bend the locus to a second slope X<1; it does not).")
    print("  - tau_slow DIVERGES (1.43 -> 20) and Var_slow diverges as g_s->gamma: CRITICAL")
    print("    SLOWING toward a stability/critical edge. The headroom to that edge is the")
    print("    spectral gap (gamma - g_s), shrinking 0.70 -> 0.05 across the sweep.")
    print("\nMETRIC-BLUR FINDING: cranking the coupling does NOT change the KIND of system —")
    print("  no oscillation, no current, X=1 throughout — so Cat-1 does NOT smear along this")
    print("  metric axis. What changes is the spectral gap: the operating point approaches a")
    print("  critical/instability edge via critical slowing. The category is SHARP; the sweep")
    print("  grounds the two-sided headroom-to-instability (v1's owed vector, closed here for")
    print("  the reversible Cat-1 case). Reversible critical slowing (X=1) is cleanly distinct")
    print("  from glassy aging (X<1, v4) along the SAME diverging-timescale signature.")

    a = rows_meta[ANCHOR_LEVEL]
    print(f"\nANCHOR (level {ANCHOR_LEVEL}, g_s=0.6 == v6 community 0): eig {a['ev'][0]:+.3f}/{a['ev'][2]:+.3f}")
    print(f"  (v6: -0.4/-1.6), <sigma>={a['sigma']:.4f} (v6: 0), |Cxy+Cyx| peak {a['sym_peak']:.4f}")
    print(f"  (v6: 1.199), |Cxy-Cyx| {a['asym_peak']:.4f} (v6: 0), drift {a['drift']:+.4f} (v6: ~0).")

    # ---- self-consistency assertions ----
    for m in rows_meta:
        assert np.all(np.abs(m["ev"].imag if hasattr(m["ev"], "imag") else 0.0) < 1e-9), "spectrum must be real"
        assert m["omega"] < 1e-9, f"no oscillation allowed (level {m['level']})"
        assert m["sigma"] < 1e-6, f"detailed balance: <sigma>~0 (level {m['level']})"
        assert m["asym_peak"] < 1e-3, f"cross-corr must stay symmetric Cxy=Cyx (level {m['level']})"
        assert abs(m["drift"]) < 0.2, f"no current: winding drift ~0 (level {m['level']}, got {m['drift']})"
        assert m["fdr_r2"] > 0.98, f"FDR locus must stay affine X=1 (level {m['level']}, R2={m['fdr_r2']})"
    gaps = [m["gap"] for m in rows_meta]
    taus = [m["tau_slow"] for m in rows_meta]
    assert gaps == sorted(gaps, reverse=True) and taus == sorted(taus), "gap must shrink / tau_slow must grow monotonically"
    assert taus[-1] / taus[0] > 5.0, "critical slowing: tau_slow must diverge clearly across the sweep"
    anc = rows_meta[ANCHOR_LEVEL]
    assert abs(anc["sym_peak"] - 1.199) < 0.05 and anc["sigma"] < 1e-6, "anchor must reproduce v6 community 0"
    print("\nself-consistent: real spectrum + <sigma>=0 + Cxy=Cyx + X=1 at every level;")
    print("                 tau_slow diverges (critical slowing); anchor reproduces v6. OK.")
    print(f"wrote {OUT}  ({len(csv_lines)} rows, five operating points)")


if __name__ == "__main__":
    main()
