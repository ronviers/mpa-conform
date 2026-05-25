"""freeze — three_species_cycle_v3  (bespoke, one substrate, brittle by design)

The FIRST Cat-10 (Non-Reciprocal) vertical, and the first to light the current /
self-frame sector that a single-mode Vertex substrate structurally CANNOT reach.

Substrate: the noisy frustrated Banach-class reference (mpa-central/library/
banach_frustrated.py) — three modes in a cyclic, non-reciprocal (rock-paper-scissors)
coupling, driven by noise:
    dz = M z dt + sqrt(2D) dW,   M = -gamma I + g A_cyc,
    A_cyc = [[0,-1,1],[1,0,-1],[-1,1,0]]  (antisymmetric circulant).
Eigenvalues of M: -gamma (real) and -gamma +/- i*sqrt(3)*g (a COMPLEX PAIR). The
complex pair is the k_frust signature: a *sustained* probability current circulating
in the plane orthogonal to (1,1,1) — a non-equilibrium steady state, never settling to
detailed balance. Topologically forced: no continuous knob (drive, noise) removes it;
only g=0 (severing the cyclic wiring) does.

THE TOOTH (vs the laser, Cat 1): the class-B laser ALSO has a complex eigenvalue pair
(its ring-down). But the laser RELAXES to equilibrium — its probability current is
ZERO, time-reversal symmetry is intact, the cross-correlation matrix is symmetric. The
3-cycle's complex pair is a real circulating current — time-reversal symmetry BROKEN,
the cross-correlation matrix ANTISYMMETRIC. "It oscillates / cycles" does NOT settle
which one it is. The directional asymmetry Cxy(tau) != Cyx(tau) is the discriminator,
and it is the researcher-observable that grounds the Cat-1 vs Cat-10 separation.

Ground truth is exact (linear OU), computed HERE from the structure, never via conform
(data-path independence). For gamma=1.0, g=0.6, D=0.1:
    <sigma> = 6 g^2 / gamma          (entropy production rate; EXACT, noise-independent)
    omega   = sqrt(3) * g            (rotation rate = Im of the complex pair)
    omega/gamma                      (dimensionless spectral ratio; structure-set)
    affinity A (nats/cycle), T (TUR violation factor, floor T>=1) from the winding sim.

BLINDING: the emitted CSV carries ONLY (tau, C, chi, Cxy, Cyx) — the rotation-plane
autocorrelation C, integrated response chi, and the two DIRECTED cross-correlations
Cxy/Cyx (whose inequality is the current). It does NOT carry g, gamma, D, <sigma>,
the affinity, the eigenvalues, or any framework token. The researcher's three population
traces yield exactly these standard observables; the framework reading stays sealed.

Run:  python H:/mpa-conform/blockin/questions/three_species_cycle_v3/freeze_three_species_cycle.py

Emits:  data/three_species_cycle_v3.frozen.csv   (tau,C,chi,Cxy,Cyx — the blind artifact)
        prints the SEALED ground truth (eigenvalues, <sigma>, omega/gamma, affinity,
        T, TUR) for the author to paste / the human to eyeball. The CSV carries NONE of it.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov

# reuse the library substrate as the answer-path (the truth, never via conform)
sys.path.insert(0, "H:/mpa-central/library")
import banach_frustrated as bf  # noqa: E402

# one operating point (a single ecosystem's worth of data — I1 placement, not a sweep)
GAMMA, G, D = 1.0, 0.6, 0.1
SEED = 5

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "three_species_cycle_v3.frozen.csv"

# rotation-plane projector (orthonormal basis perp to (1,1,1)), from the library
P = bf.P            # 2x3
A_CYC = bf.A_CYC


def resolved_winding(M, D, t_grid, rng, n_real=2000, dt=0.01):
    """Tau-resolved ensemble winding in the rotation plane: phi(tau) accumulated over
    elapsed observation time, sampled on t_grid. Returns mean and variance of the
    cumulative net rotation at each grid time. This is the honest content of ONE long
    run read by sub-window / ensemble averaging (stationary, ergodic): its DRIFT gives
    the current rate <J> and its DIFFUSION gives Var(J) — together the affinity and the
    TUR factor. Withholding it would be an under-boundary violation (WORKFLOW §4)."""
    sd = np.sqrt(2.0 * D * dt)
    z = rng.standard_normal((n_real, 3)) * np.sqrt(D)
    for _ in range(3000):                                  # equilibrate to the NESS
        z = z + (z @ M.T) * dt + rng.standard_normal((n_real, 3)) * sd
    steps = np.maximum(1, np.round(t_grid / dt).astype(int))
    n_steps = int(steps[-1])
    u = z @ P.T
    phi = np.zeros(n_real)
    mean = np.empty_like(t_grid)
    var = np.empty_like(t_grid)
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
            mean[k] = phi.mean()
            var[k] = phi.var(ddof=1)
            k += 1
    return bf.finite("phiMean", mean), bf.finite("phiVar", var)


def plane_correlations(M, Sigma, t):
    """Exact OU two-point functions, projected onto the rotation plane.
    c(tau)_ab = <u_a(t+tau) u_b(t)> = (P expm(M tau) Sigma P^T)_ab,  u = P z.
    Returns normalized C (symmetric autocorr), chi (integrated x-response), and the
    two directed cross-correlations Cxy, Cyx (normalized by the same scale)."""
    c0 = P @ Sigma @ P.T
    scale = 0.5 * (c0[0, 0] + c0[1, 1])          # plane variance (normalizer)
    C = np.empty_like(t)
    Cxy = np.empty_like(t)
    Cyx = np.empty_like(t)
    Rxx = np.empty_like(t)                        # x-coordinate impulse response (for chi)
    for i, ti in enumerate(t):
        Pr = expm(M * ti)
        c = P @ Pr @ Sigma @ P.T                  # <u(t+tau) u(t)^T>
        r = P @ Pr @ P.T                          # mean response of u to a u-kick
        C[i] = 0.5 * (c[0, 0] + c[1, 1]) / scale
        Cxy[i] = c[0, 1] / scale
        Cyx[i] = c[1, 0] / scale
        Rxx[i] = r[0, 0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (Rxx[1:] + Rxx[:-1]) * np.diff(t))])
    return C, chi, Cxy, Cyx


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # --- exact structure / spectrum (the sealed truth) ---
    M, sigma, ev, omega, gam_eff = bf.exact(GAMMA, G, D)
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
    ratio = omega / gam_eff
    sigma_formula = 6.0 * G * G / GAMMA          # the closed form, for cross-check

    # --- winding ensemble -> affinity, T, TUR (the self-frame observables) ---
    rng = np.random.default_rng(SEED)
    m = bf.measure(GAMMA, G, D, rng)             # mean/var winding, affinity A, T, tur_ok

    # --- the blind observables: one settling window, rotation-plane two-point functions
    # slowest mode decays at rate gamma; sample ~8 e-foldings, resolve a few rotations.
    slowest = float(-np.max(ev.real))            # = gamma here
    t_settle = 8.0 / slowest
    t_rot = 6.0 * (2.0 * np.pi / omega) if omega > 1e-9 else 0.0
    t_max = max(t_settle, t_rot)
    t = np.linspace(t_max / 400.0, t_max, 120)
    C, chi, Cxy, Cyx = plane_correlations(M, Sigma, t)
    phiMean, phiVar = resolved_winding(M, D, t, rng)       # in-slice winding (WORKFLOW §4)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# three_species_cycle_v3 — one cyclic-community observation window.\n")
        f.write("# columns: tau (community clock — a lag for the two-point columns, an\n")
        f.write("#          elapsed time for the winding columns; same clock either way),\n")
        f.write("#          C (normalized rotation-plane autocorr), chi (integrated\n")
        f.write("#          response), Cxy / Cyx (the two directed cross-correlations\n")
        f.write("#          between the two community-rotation axes), phiMean / phiVar\n")
        f.write("#          (mean and variance of the cumulative net turnover angle swept\n")
        f.write("#          up to elapsed tau, across the run's sub-windows).\n")
        f.write("# All columns dimensionless (angle in radians). One operating point.\n")
        f.write("# Generated by the community's own linear NESS propagator + sim — not via conform.\n")
        f.write("tau,C,chi,Cxy,Cyx,phiMean,phiVar\n")
        for ti, ci, xi, cxy, cyx, pm, pv in zip(t, C, chi, Cxy, Cyx, phiMean, phiVar):
            f.write(f"{ti:.6f},{ci:.6f},{xi:.6f},{cxy:.6f},{cyx:.6f},{pm:.6f},{pv:.6f}\n")

    # the directional asymmetry (the current fingerprint), as the answerer would form it.
    # gauged against C(0)=1 (the autocorr scale): the rotation-plane cross-correlation is
    # purely antisymmetric here (Cxy == -Cyx exactly), so |Cxy-Cyx| IS the current signal.
    asym = Cxy - Cyx
    asym_peak = float(np.max(np.abs(asym)))

    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"substrate: noisy frustrated N=3 cyclic non-reciprocal OU "
          f"(gamma={GAMMA}, g={G}, D={D})")
    print("M eigenvalues (a COMPLEX PAIR = sustained current / k_frust signature):")
    for e in ev:
        print(f"    {e.real:+.4f} {e.imag:+.4f}i")
    print()
    print(f"  <sigma> (entropy production)   = {sigma:.4f}   "
          f"(closed form 6 g^2/gamma = {sigma_formula:.4f})")
    print(f"  omega  (rotation rate, Im pair) = {omega:.4f}   (= sqrt(3) g = {np.sqrt(3)*G:.4f})")
    print(f"  gamma_eff (damping, Re pair)    = {gam_eff:.4f}")
    print(f"  omega/gamma (DIMENSIONLESS)     = {ratio:.4f}  <- structure-set, noise-independent")
    print(f"  winding <J>                     = {m['mean']:.4f}  (nonzero => sustained directional current)")
    print(f"  winding Var(J)                  = {m['var']:.4f}")
    print(f"  affinity A (nats/cycle)         = {m['A']:.4f}")
    print(f"  self-frame T (TUR factor)       = {m['T']:.4f}   (floor T>=1; tur_ok={m['tur_ok']})")
    print()
    print(f"  directional asymmetry |Cxy-Cyx| peak = {asym_peak:.4f}  "
          f"(vs autocorr scale C(0)=1: {100*asym_peak:.0f}%)")
    print("  => the rotation-plane cross-correlation is PURELY ANTISYMMETRIC (Cxy == -Cyx):")
    print("     a real circulating current, NOT reciprocal damped oscillation. A laser")
    print("     ring-down has the SAME damped-cosine autocorr C but Cxy==Cyx (asym=0).")
    print()
    print("PLACEMENT: sustained NESS circulation (Cat 10, non-reciprocal). Stable (all")
    print("  Re(eig) = -gamma < 0): the community circulates forever but does not blow up.")
    print("  The 'edge' the researcher senses is the perpetual turnover, NOT an instability.")
    print("NAIVE-WORRY CORRECTION: the cycling is NOT noise-driven reciprocal oscillation that")
    print("  calming the environment would settle — the directed asymmetry Cxy!=Cyx is a")
    print("  broken-time-reversal current intrinsic to the cyclic wiring; omega/gamma and the")
    print("  per-cycle affinity are set by the STRUCTURE (g/gamma), not by the noise level.")
    # affinity + TUR factor computed FROM THE EMITTED winding arrays (the same data the
    # blind answerer sees) so the sealed key matches the blind dataset, not a different
    # window. bf.measure (printed above) is the canonical cross-check.
    tau_obs = float(t[-1])
    Jbar, Jvar = float(phiMean[-1]), float(phiVar[-1])
    drift_rate = Jbar / tau_obs
    cycles = abs(Jbar) / (2.0 * np.pi)
    A_inslice = sigma * tau_obs / cycles
    T_inslice = sigma * tau_obs * Jvar / (2.0 * Jbar * Jbar)
    print(f"  resolved winding: phiMean(t_max)={Jbar:.2f} (drift rate {drift_rate:.3f}/clock "
          f"~ omega={omega:.3f}), phiVar(t_max)={Jvar:.2f}")
    print(f"  in-slice affinity A = {A_inslice:.2f} nats/cycle (cross-check bf.measure {m['A']:.2f})")
    print(f"  in-slice TUR factor T = {T_inslice:.2f}  (floor T>=1; cross-check {m['T']:.2f})")
    print()
    print("GROUNDED IN-SLICE (one operating point, complete honest content — WORKFLOW §4):")
    print("  current existence + direction (asymmetry Cxy!=Cyx AND nonzero winding drift),")
    print("  spectral ratio omega/gamma, the affinity / entropy production (winding drift +")
    print("  FDR-locus departure), the TUR factor T from phiVar/phiMean^2 (floor T>=1),")
    print("  two-frame AGREEMENT (standard FDR locus vs self-frame affinity, both computable")
    print("  here), and stability. The Cat-10 two-frame teeth are exercised in THIS pass.")
    print("NOT GROUNDED (across a COLLAPSED AXIS only — the legitimate next vector):")
    print("  noise-INDEPENDENCE of omega/gamma and the affinity — that the current is set by")
    print("  the wiring not the noise level needs a NOISE SWEEP (different D = a different")
    print("  operating point = a collapsed axis, I2/prod). This is the only honest park.")

    # self-consistency assertions (author-side; the sealed key must hold together)
    assert np.sum(np.abs(ev.imag) > 1e-9) == 2, "must have a complex eigenvalue PAIR"
    assert np.all(ev.real < 0), "all modes must be damped (stable NESS, not a blowup)"
    assert abs(sigma - sigma_formula) < 1e-6, "<sigma> must match the closed form 6 g^2/gamma"
    assert asym_peak > 0.1, "directional asymmetry must be clearly nonzero vs C(0)=1 (a current)"
    assert T_inslice >= 1.0, "in-slice TUR floor T>=1 must hold (T<1 would be a KILL falsifier)"
    assert abs(Jbar) > 5.0, "winding drift must be resolved clearly nonzero (a sustained current)"
    print("\nself-consistent: complex pair + all-damped + sigma=6g^2/gamma + clear asymmetry "
          "+ in-slice TUR holds + resolved current. OK.")
    print(f"wrote {OUT}  ({len(t)} rows, one operating point)")


if __name__ == "__main__":
    main()
