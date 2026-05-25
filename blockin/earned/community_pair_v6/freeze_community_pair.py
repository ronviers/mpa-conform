"""freeze — community_pair_v6  (bespoke, two members, brittle by design)

The separability probe at MINIMAL GENERATING DISTANCE: two three-population loop
communities that differ by exactly ONE structural bit — the reciprocity of the
coupling — re-posing the Cat-1 (Vertex / reversible relaxation) vs Cat-10
(Non-Reciprocal / sustained current) separation on the SAME substrate family.

Both members are 3-mode OU on the noisy-frustrated Banach-class machinery
(mpa-central/library/banach_frustrated.py), at the SAME operating point
gamma=1.0, g=0.6, D=0.1:

  member B (the CYCLIC community):  M_B = -gamma I + g A_cyc,
        A_cyc = [[0,-1,1],[1,0,-1],[-1,1,0]]   (antisymmetric circulant).
    => eigenvalues -gamma, -gamma +/- i*sqrt(3) g  (a COMPLEX PAIR).
    This is v3's substrate at v3's exact operating point => member B is an ANCHOR:
    its placement must reproduce three_species_cycle_v3 (asserted at unseal).

  member A (the MATCHED community):  M_A = -gamma I + g S,
        S = P^T [[0,1],[1,0]] P    (symmetric, annihilates the (1,1,1) mode,
        plane eigenvalues +/-1).
    => eigenvalues -gamma, -gamma +/- g  (ALL REAL).  Symmetric coupling =>
    detailed balance => zero probability current => an EQUILIBRIUM (reversible)
    community, NOT a NESS.

The reciprocity flip is the whole vector. It changes the THERMODYNAMIC class:
  B: Omega = M + D Sigma^-1 = g A_cyc != 0  -> entropy production <sigma> = 6 g^2/gamma,
     broken time-reversal, cross-correlation ANTISYMMETRIC (Cxy == -Cyx), winding J != 0.
  A: Omega = 0 exactly                       -> <sigma> = 0, time-reversal symmetric,
     cross-correlation SYMMETRIC (Cxy == Cyx), winding J ~ 0.

THE DISCRIMINATOR (the sealed reading): the SYMMETRY of the cross-correlation matrix.
Cxy == Cyx (reciprocal / reversible / equilibrium, Cat 1) vs Cxy == -Cyx (non-reciprocal
/ irreversible / NESS current, Cat 10). The autocorrelation C also differs (A: monotone
bi-exponential; B: damped cosine) but C-SHAPE alone is not decisive — a reciprocal system
could in principle ring; the time-reversal signature that ISOLATES reciprocity is the
cross-correlation symmetry, not the ringing. Both members are STABLE (all Re(eig) < 0):
the matched community settles to equilibrium, the cyclic community settles to a NESS that
circulates forever — neither blows up.

WHY both stable at the SAME gamma: antisymmetric coupling is purely imaginary in the
plane (rotation; Re(eig) = -gamma regardless of g) -> unconditionally stable. Symmetric
coupling is real in the plane (stretch; Re shifts by +/- g) -> stable only for gamma > g.
At gamma=1, g=0.6 both are comfortably stable. (A matched community at the cyclic one's
*rotation* magnitude sqrt(3) g > gamma would destabilize its plane — itself a feature of
the reciprocity flip, not a flaw: circulation is benign, matched competition is not.)

Ground truth is exact (linear OU), computed HERE from each structure, never via conform
(data-path independence). BLINDING: the emitted CSV carries only
(community, tau, C, chi, Cxy, Cyx, phiMean, phiVar) for each of the two communities — no
gamma/g/D, no coupling matrix, no entropy rate, no eigenvalues, no "reciprocal" /
"non-reciprocal" label. Which community is which thermodynamic class is exactly what
conform must INFER from Cxy vs Cyx.

Run:  python H:/mpa-conform/blockin/questions/community_pair_v6/freeze_community_pair.py
Emits: data/community_pair_v6.frozen.csv  (the blind artifact)
       prints the SEALED ground truth for the author to paste / the human to eyeball.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov

# reuse the library substrate's projector + helpers (the answer-path, never via conform)
sys.path.insert(0, "H:/mpa-central/library")
import banach_frustrated as bf  # noqa: E402

GAMMA, G, D = 1.0, 0.6, 0.1
SEED = 5

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "community_pair_v6.frozen.csv"

P = bf.P            # 2x3 rotation-plane projector (perp to (1,1,1))
A_CYC = bf.A_CYC    # antisymmetric circulant (the cyclic / non-reciprocal coupling)
# symmetric reciprocal coupling: off-diagonal symmetric in the OBSERVABLE plane axes,
# embedded back to 3-mode so it annihilates the (1,1,1) mode (like A_cyc does).
B_SYM_PLANE = np.array([[0.0, 1.0], [1.0, 0.0]])         # symmetric, plane eigenvalues +/-1
S_SYM = P.T @ B_SYM_PLANE @ P                            # 3x3 symmetric, S (1,1,1) = 0


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire). Diagnose, do not fill.")
    return x


def exact(M, D):
    """Exact OU scalars for a given drift M (general — NOT assuming the cyclic form).
    Sigma (stationary cov) from the Lyapunov eq; Omega = M + D Sigma^-1 is the
    irreversible drift; <sigma> = Tr[Omega^T D^-1 Omega Sigma] is the entropy production
    rate (0 iff detailed balance). omega = max |Im(eig)| (rotation rate, 0 if no current)."""
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
    Dmat = D * np.eye(3)
    Omega = M + Dmat @ np.linalg.inv(Sigma)
    sigma = float(np.trace(Omega.T @ np.linalg.inv(Dmat) @ Omega @ Sigma))
    ev = np.linalg.eigvals(M)
    omega = float(np.max(np.abs(ev.imag)))
    gam_eff = float(-np.mean(ev.real[np.abs(ev.imag) > 1e-9])) if omega > 1e-9 else float(-np.max(ev.real))
    return Sigma, Omega, sigma, ev, omega, gam_eff


def plane_correlations(M, Sigma, t):
    """Exact OU two-point functions projected onto the observable plane (u = P z):
    C (normalized autocorr), chi (integrated x-response), Cxy, Cyx (the two directed
    cross-correlations). For a reversible (symmetric-coupled) community Cxy == Cyx; for
    the cyclic (antisymmetric-coupled) community Cxy == -Cyx."""
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


def resolved_winding(M, D, t_grid, rng, n_real=2000, dt=0.01):
    """Tau-resolved ensemble winding in the plane (same estimator as v3). DRIFT gives the
    current rate <J>, DIFFUSION gives Var(J). For the matched (reversible) community the
    drift is ~0 (no current); for the cyclic community it accumulates (sustained current)."""
    sd = np.sqrt(2.0 * D * dt)
    z = rng.standard_normal((n_real, 3)) * np.sqrt(D)
    for _ in range(3000):
        z = z + (z @ M.T) * dt + rng.standard_normal((n_real, 3)) * sd
    steps = np.maximum(1, np.round(t_grid / dt).astype(int))
    n_steps = int(steps[-1])
    u = z @ P.T
    phi = np.zeros(n_real)
    mean = np.empty_like(t_grid); var = np.empty_like(t_grid)
    k = 0
    for s in range(1, n_steps + 1):
        z = z + (z @ M.T) * dt + rng.standard_normal((n_real, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        u = un
        while k < len(steps) and steps[k] == s:
            mean[k] = phi.mean(); var[k] = phi.var(ddof=1); k += 1
    return finite("phiMean", mean), finite("phiVar", var)


def build_member(M, label, rng):
    Sigma, Omega, sigma, ev, omega, gam_eff = exact(M, D)
    # blind observables: one window spanning ~8 e-foldings of the slowest mode AND (if it
    # rotates) several rotation periods, so the directed turnover resolves.
    slowest = float(-np.max(ev.real))
    t_settle = 8.0 / slowest
    t_rot = 6.0 * (2.0 * np.pi / omega) if omega > 1e-9 else 0.0
    t_max = max(t_settle, t_rot)
    t = np.linspace(t_max / 400.0, t_max, 120)
    C, chi, Cxy, Cyx = plane_correlations(M, Sigma, t)
    phiMean, phiVar = resolved_winding(M, D, t, rng)
    asym_peak = float(np.max(np.abs(Cxy - Cyx)))
    sym_peak = float(np.max(np.abs(Cxy + Cyx)))   # |Cxy+Cyx|: large if symmetric, ~0 if antisymmetric
    tau_obs = float(t[-1])
    Jbar, Jvar = float(phiMean[-1]), float(phiVar[-1])
    drift_rate = Jbar / tau_obs
    cycles = abs(Jbar) / (2.0 * np.pi)
    A_aff = sigma * tau_obs / cycles if cycles > 1e-6 else float("nan")
    T_inslice = sigma * tau_obs * Jvar / (2.0 * Jbar * Jbar) if abs(Jbar) > 1e-6 else float("nan")
    return dict(label=label, M=M, Sigma=Sigma, Omega=Omega, sigma=sigma, ev=ev,
                omega=omega, gam_eff=gam_eff, t=t, C=C, chi=chi, Cxy=Cxy, Cyx=Cyx,
                phiMean=phiMean, phiVar=phiVar, asym_peak=asym_peak, sym_peak=sym_peak,
                tau_obs=tau_obs, Jbar=Jbar, Jvar=Jvar, drift_rate=drift_rate,
                A_aff=A_aff, T_inslice=T_inslice)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    M_B = -GAMMA * np.eye(3) + G * A_CYC      # cyclic / non-reciprocal (= v3)
    M_A = -GAMMA * np.eye(3) + G * S_SYM      # matched / reciprocal

    # build B first with seed=5 so its winding stream reproduces v3 exactly (anchor),
    # then A on the next stream.
    B = build_member(M_B, "B", rng)
    A = build_member(M_A, "A", rng)

    # --- emit the blind CSV: two communities stacked, neutral integer label 0/1 ---
    # community 0 == member A (matched), community 1 == member B (cyclic). The mapping is
    # NOT in the file; conform must infer the class from Cxy vs Cyx.
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# community_pair_v6 — two three-population loop communities, one long\n")
        f.write("#   observation window each. Stacked: 'community' is a neutral 0/1 index\n")
        f.write("#   (which is which dynamical class is NOT encoded — that is the question).\n")
        f.write("# columns: community (0 or 1), tau (the community's own clock — a lag for the\n")
        f.write("#   two-point columns, an elapsed time for the winding columns), C (normalized\n")
        f.write("#   rotation-plane autocorr), chi (integrated response), Cxy / Cyx (the two\n")
        f.write("#   directed cross-correlations between the two community-rotation axes),\n")
        f.write("#   phiMean / phiVar (mean and variance of the cumulative net turnover angle\n")
        f.write("#   swept up to elapsed tau, across the run's sub-windows).\n")
        f.write("# All columns dimensionless (angle in radians). Two operating points.\n")
        f.write("# Generated by each community's own exact linear propagator + sim — not via conform.\n")
        f.write("community,tau,C,chi,Cxy,Cyx,phiMean,phiVar\n")
        for cid, m in [(0, A), (1, B)]:
            for ti, ci, xi, cxy, cyx, pm, pv in zip(m["t"], m["C"], m["chi"], m["Cxy"],
                                                    m["Cyx"], m["phiMean"], m["phiVar"]):
                f.write(f"{cid},{ti:.6f},{ci:.6f},{xi:.6f},{cxy:.6f},{cyx:.6f},{pm:.6f},{pv:.6f}\n")

    # --- sealed truth (author + human eyeball only — NEVER in the CSV) ---
    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"shared operating point: gamma={GAMMA}, g={G}, D={D};  seed={SEED}")
    print("community labels in the CSV: 0 == member A (MATCHED), 1 == member B (CYCLIC)\n")

    for tag, m, kind in [("A (MATCHED / community 0)", A, "reciprocal -> equilibrium, Cat 1"),
                         ("B (CYCLIC  / community 1)", B, "non-reciprocal -> NESS current, Cat 10")]:
        print(f"--- member {tag}:  {kind}")
        print("  M eigenvalues:")
        for e in m["ev"]:
            print(f"      {e.real:+.4f} {e.imag:+.4f}i")
        print(f"  <sigma> (entropy production)  = {m['sigma']:.4f}   "
              f"({'EQUILIBRIUM (reversible, detailed balance)' if m['sigma'] < 1e-6 else 'NESS (irreversible)'})")
        print(f"  omega (rotation rate, Im pair) = {m['omega']:.4f}")
        print(f"  omega/gamma_eff               = {m['omega']/m['gam_eff']:.4f}")
        print(f"  |Cxy - Cyx| peak (ANTISYM signal) = {m['asym_peak']:.4f}")
        print(f"  |Cxy + Cyx| peak (SYM signal)     = {m['sym_peak']:.4f}")
        print(f"  winding drift phiMean(t_max)  = {m['Jbar']:+.4f}  (rate {m['drift_rate']:+.4f}/clock)")
        print(f"  winding Var(J)                = {m['Jvar']:.4f}")
        if np.isfinite(m["A_aff"]):
            print(f"  affinity A (nats/cycle)       = {m['A_aff']:.4f}")
            print(f"  self-frame T (TUR factor)     = {m['T_inslice']:.4f}  (floor T>=1)")
        else:
            print(f"  affinity / T                  = N/A (no resolvable current — drift ~ 0)")
        print()

    print("DISCRIMINATOR: the SYMMETRY of the cross-correlation matrix.")
    print(f"  member A: |Cxy-Cyx|={A['asym_peak']:.3f} (~0) and |Cxy+Cyx|={A['sym_peak']:.3f} -> Cxy == Cyx,")
    print("            symmetric, time-reversible, NO current => MATCHED equilibrium (Cat 1).")
    print(f"  member B: |Cxy-Cyx|={B['asym_peak']:.3f} and |Cxy+Cyx|={B['sym_peak']:.3f} (~0) -> Cxy == -Cyx,")
    print("            antisymmetric, time-irreversible, a CURRENT => CYCLIC NESS (Cat 10).")
    print("Both stable (all Re(eig) < 0): A settles to equilibrium, B settles to a")
    print("circulating NESS. Neither blows up; the cyclic one's perpetual turnover is its")
    print("nominal NESS, NOT an instability edge.\n")

    print("SEPARABILITY (the load-bearing read): this pair separates CLEAN on the cross-")
    print("correlation symmetry. The generating distance is MINIMAL (only the coupling's")
    print("reciprocity is flipped), yet the observable distance is large — because reciprocity")
    print("is a DISCRETE structural property: a coupling is symmetric or it is not; there is no")
    print("continuous knob that smears A into B (g->0 deletes the loop, it does not blur the")
    print("class). So the 1<->10 cut is TOPOLOGICALLY sharp, not metrically blurry. This does")
    print("NOT settle whether METRIC boundaries (criticality, coupling-strength continua, Cat 2)")
    print("blur — that needs a different, tunable-axis probe (still GAP).\n")

    # --- anchor: member B must reproduce three_species_cycle_v3 ---
    print("ANCHOR (checked at unseal, not handed to the answerer): member B is v3's substrate")
    print("at v3's exact operating point (gamma=1, g=0.6, D=0.1, seed=5). Its placement must")
    print(f"reproduce v3: omega/gamma~1.039 (here {B['omega']/B['gam_eff']:.4f}), <sigma>=2.16")
    print(f"(here {B['sigma']:.4f}), |Cxy-Cyx|peak~0.66 (here {B['asym_peak']:.4f}), winding drift")
    print(f"~38 (here {B['Jbar']:.2f}), affinity~13 nats (here {B['A_aff']:.2f}), T~19 (here {B['T_inslice']:.2f}).\n")

    # --- self-consistency assertions (the sealed key must hold together) ---
    # member B == v3 character
    assert np.sum(np.abs(B["ev"].imag) > 1e-9) == 2, "B must have a complex eigenvalue PAIR (current)"
    assert np.all(B["ev"].real < 0), "B must be stable (NESS, not a blowup)"
    assert abs(B["sigma"] - 6.0 * G * G / GAMMA) < 1e-6, "B <sigma> must match 6 g^2/gamma = 2.16"
    assert B["asym_peak"] > 0.1, "B cross-corr must be clearly ANTISYMMETRIC (a current)"
    assert B["sym_peak"] < 1e-3, "B cross-corr must be PURELY antisymmetric (Cxy == -Cyx)"
    assert abs(B["Jbar"]) > 5.0, "B winding drift must resolve clearly nonzero (sustained current)"
    assert B["T_inslice"] >= 1.0, "B in-slice TUR floor T>=1 must hold"
    assert abs(B["omega"] / B["gam_eff"] - 1.0392) < 1e-2, "B omega/gamma must reproduce v3 ~1.039"
    # member A == reversible equilibrium character
    assert np.all(np.abs(A["ev"].imag) < 1e-9), "A must have ALL-REAL eigenvalues (no rotation)"
    assert np.all(A["ev"].real < 0), "A must be stable (settles to equilibrium)"
    assert A["sigma"] < 1e-6, "A <sigma> must be ~0 (equilibrium, detailed balance)"
    assert A["sym_peak"] > 0.05, "A cross-corr must be clearly nonzero & SYMMETRIC (coupled, but reversible)"
    assert A["asym_peak"] < 1e-3, "A cross-corr must be PURELY symmetric (Cxy == Cyx, no current)"
    assert abs(A["Jbar"]) < 2.0, "A winding drift must be ~0 (no sustained current)"
    print("self-consistent: B = complex pair + current + antisym + reproduces v3;")
    print("                 A = all-real + equilibrium + symmetric + zero current. OK.")
    print(f"wrote {OUT}  ({len(A['t']) + len(B['t'])} rows, two communities)")


if __name__ == "__main__":
    main()
