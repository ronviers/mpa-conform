r"""rps_dimensionless.py -- the dimensionless self-probe T on RPS (REAL emergent substrate).

Move #2 of promotion_crossing_handoff.md (`dimensionless-substrate`, sharpening -> battery). This is
the REAL-EMERGENT version of what banach_frustrated.py does synthetically: it reads the dimensionless
TUR self-probe T and the canonical affinity on a substrate whose chiral structure EMERGES rather than
being drawn in by hand.

  banach_frustrated:  M = -gamma I + g A_CYC      (A_CYC drawn in by hand = synthetic = calibration)
  RPS (this script):  M = jacobian(alpha,beta)    (its antisymmetric part = x*(alpha-beta)/2 * A_CYC
                                                    EMERGES from the May-Leonard rules -> vindication)

THE DIMENSIONLESS SELF-PROBE (engine FRAMES; standard in character_units.md):
  Read at the system's OWN scale (no external probe): T = <sigma> * tau * Var(J) / (2 <J>^2), the
  TUR-tightness ratio, floored at 1 (Barato-Seifert). J = winding (signed area) accumulated over tau
  by the noisy interior dynamics around the coexistence focus; <sigma> = NESS entropy-production rate
  (heat-tax) from the linear-response Lyapunov solution. Both read from the SAME OU (RPS linearized at
  coexistence) so T is self-consistent -- a meaningful test, not an inconsistency artifact.

CANONICAL QUANTITIES (the dimensionless dream, on a real substrate):
  For additive isotropic noise the OU stationary covariance Sigma scales linearly with the noise, so
  Omega = M + D Sigma^-1 and <sigma> = Tr[Omega^T D^-1 Omega Sigma] are NOISE-INDEPENDENT (D cancels).
  => the affinity A = 2 pi <sigma> / omega (nats/cycle) and the spectral ratio omega/gamma_eff are
  DIMENSIONLESS, NOISE-INDEPENDENT canonical quantities set by the ECOLOGICAL STRUCTURE (alpha,beta).
  The self-probe T is the bounded (>=1) violation factor that rides on top.

PRE-REGISTERED BAR (all must hold; a clean miss is also evidence):
  D1 self-probe CLOSES on the real substrate: the empirical affinity from the winding ensemble
     A_emp = <sigma> tau / cycles matches the closed form A_closed = 2 pi <sigma>/omega (forced, not
     fitted) at every operating point.
  D2 canonical = noise-independent: A and omega/gamma_eff are FLAT across the demographic-noise sweep
     (rel-spread < 10% / < 5%) -- a dimensionless quantity set by structure, not by drive.
  D3 TUR floor holds (the fake-NaN tripwire): the EMPIRICAL T (from the measured winding ensemble) is
     >= 1 at every operating point. T < 1 is NOT a finding -- it is a broken estimator (too few
     samples / too short tau); halt and fix the readout, never report it (fake-NaN rule).
  D4 structure-set: across an asymmetry sweep (delta = alpha - beta) the affinity TRACKS the structure
     (changes with delta) while staying noise-flat at each delta -- the fingerprint is ecological.

  KILL: A or omega/gamma_eff is noise-DEPENDENT (no dimensionless canonical quantity on the real
        substrate), OR A_emp diverges from A_closed (the self-probe does not close on RPS).

Usage (from mpa-conform root):  python scripts/rps_dimensionless.py
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
for p in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import solve_continuous_lyapunov

from rps_triad import jacobian, coexistence, spectral

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

# rotation plane perp to the collective (1,1,1) axis (same basis as rps_triad / banach_frustrated)
E1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
E2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
P = np.stack([E1, E2], axis=0)                    # 2x3 projector onto the rotation plane

A0, B0 = 0.5, 1.0                                 # base RPS operating point (alpha+beta<2: stable focus)
DT = 0.01
T_EQ = 2000                                       # equilibration steps
T_OBS = 4000                                      # observation steps (tau = T_OBS * DT)
N_REAL = 4000                                     # ensemble size for the winding statistics
SEED = 5


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}' -- diagnose the readout, do not fill (fake-NaN rule).")
    return x


def sigma_ep(alpha, beta, sigma):
    """NESS entropy-production rate <sigma> of the RPS focus linearized at coexistence (additive
    isotropic demographic noise D = sigma^2/2 I). Noise-independent by construction (D cancels)."""
    M = jacobian(alpha, beta)
    D = 0.5 * sigma ** 2 * np.eye(3)
    Sigma = solve_continuous_lyapunov(M, -2.0 * D)
    Omega = M + D @ np.linalg.inv(Sigma)
    return float(np.trace(Omega.T @ np.linalg.inv(D) @ Omega @ Sigma))


def spectral_pair(alpha, beta):
    """omega = max|Im lambda|, gamma_eff = -mean Re of the complex pair (the rotating mode's damping)."""
    ev = np.linalg.eigvals(jacobian(alpha, beta))
    om = float(np.max(np.abs(ev.imag)))
    gam = float(-np.mean(ev.real[np.abs(ev.imag) > 1e-9])) if om > 1e-9 else float(-np.max(ev.real))
    return om, gam


def winding_ensemble(alpha, beta, sigma, rng):
    """OU winding (signed area in the rotation plane) accumulated over tau across N_REAL trajectories.
    RPS linearized at coexistence: dz = M z dt + sqrt(2D) dW, M = jacobian, D = sigma^2/2 I."""
    M = jacobian(alpha, beta)
    D = 0.5 * sigma ** 2
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(D)
    for _ in range(T_EQ):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ P.T
    phi = np.zeros(N_REAL)
    for _ in range(T_OBS):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2     # signed swept angle increment
        u = un
    return finite("winding", phi)


def measure(alpha, beta, sigma, rng):
    sig = sigma_ep(alpha, beta, sigma)
    om, gam = spectral_pair(alpha, beta)
    tau = T_OBS * DT
    phi = winding_ensemble(alpha, beta, sigma, rng)
    mean, var = float(phi.mean()), float(phi.var(ddof=1))
    cycles = abs(mean) / (2.0 * np.pi)
    A_emp = sig * tau / cycles if cycles > 1e-9 else float("nan")     # empirical affinity (nats/cycle)
    A_closed = 2.0 * np.pi * sig / om if om > 1e-9 else float("nan")  # closed-form affinity
    T = sig * tau * var / (2.0 * mean * mean) if abs(mean) > 1e-12 else float("nan")
    return dict(alpha=alpha, beta=beta, sigma=sigma, sig=sig, om=om, gam=gam, ratio=om / gam,
                mean=mean, var=var, A_emp=A_emp, A_closed=A_closed, T=T,
                cycles=cycles, sign=int(np.sign(mean)))


def main():
    print("RPS DIMENSIONLESS SELF-PROBE -- the real-emergent version of banach_frustrated")
    print(f"base RPS: alpha={A0}, beta={B0}; emergent chiral Jacobian (antisym part = x*(a-b)/2 A_CYC)\n")
    rng = np.random.default_rng(SEED)

    sp = spectral(A0, B0)
    print(f"emergent spectrum: omega={sp['omega']:.4f}, handedness={sp['hand']:+d}, "
          f"complex pair={sp['complex_pair']}")
    print(f"the chirality is FORCED by the ecological asymmetry alpha!=beta (not drawn in)\n")

    # ---- NOISE SWEEP (vary demographic-noise sigma at fixed ecology). Canonical quantities FLAT. ----
    print("NOISE SWEEP (vary sigma at fixed alpha,beta). A & omega/gamma should be NOISE-INDEPENDENT.")
    hdr = (f"{'sigma':>7} | {'<sigma>':>9} {'omega/gam':>10} {'A_closed':>9} {'A_emp':>8} | "
           f"{'T(>=1)':>7} {'cycles':>7}")
    print(hdr); print("-" * len(hdr))
    sigmas = [0.008, 0.013, 0.02, 0.03, 0.045]
    rowsN = []
    for s in sigmas:
        m = measure(A0, B0, s, rng)
        rowsN.append(m)
        print(f"{s:>7.3f} | {m['sig']:>9.4f} {m['ratio']:>10.4f} {m['A_closed']:>9.4f} "
              f"{m['A_emp']:>8.4f} | {m['T']:>7.3f} {m['cycles']:>7.2f}")

    A_emp = np.array([m["A_emp"] for m in rowsN])
    A_cl = np.array([m["A_closed"] for m in rowsN])
    ratio = np.array([m["ratio"] for m in rowsN])
    Ts = np.array([m["T"] for m in rowsN])
    A_spread = float(np.std(A_emp) / np.mean(A_emp))
    ratio_spread = float(np.std(ratio) / np.mean(ratio))
    close = float(np.max(np.abs(A_emp - A_cl) / A_cl))
    print(f"\n  A_emp: mean {A_emp.mean():.3f} nats, rel-spread {100*A_spread:.1f}% across the noise sweep")
    print(f"  omega/gamma_eff: mean {ratio.mean():.3f}, rel-spread {100*ratio_spread:.1f}%")
    print(f"  A_emp vs A_closed: max rel-error {100*close:.1f}% (the self-probe CLOSES if small)")
    print(f"  TUR self-probe T: min {Ts.min():.3f}, max {Ts.max():.3f} (floor 1)")

    # ---- STRUCTURE SWEEP (vary the ecological asymmetry delta = alpha-beta). A TRACKS structure. ----
    print("\nSTRUCTURE SWEEP (vary delta=alpha-beta at fixed sigma). A should TRACK the ecology.")
    print(f"{'delta':>7} | {'<sigma>':>9} {'omega/gam':>10} {'A_closed':>9} | {'T(>=1)':>7}")
    rowsS = []
    for d in [0.2, 0.35, 0.5, 0.65, 0.8]:
        a, b = 0.75 + d / 2, 0.75 - d / 2          # keep alpha+beta = 1.5 (stable focus) fixed
        m = measure(a, b, 0.02, rng)
        rowsS.append(m)
        print(f"{d:>7.2f} | {m['sig']:>9.4f} {m['ratio']:>10.4f} {m['A_closed']:>9.4f} | {m['T']:>7.3f}")
    A_struct = np.array([m["A_closed"] for m in rowsS])
    struct_spread = float((A_struct.max() - A_struct.min()) / A_struct.mean())
    print(f"\n  A_closed across the structure sweep: {A_struct.min():.3f} -> {A_struct.max():.3f} nats "
          f"(spans {100*struct_spread:.0f}% -> structure-set, NOT a universal constant)")

    # ---- verdict ----
    d1 = bool(close < 0.10)
    d2 = bool(A_spread < 0.10 and ratio_spread < 0.05)
    d3 = bool(np.all(Ts >= 1.0 - 1e-6) and np.all(np.isfinite(Ts)))
    d4 = bool(struct_spread > 0.15)

    figure(sigmas, rowsN, rowsS)

    print("\n" + "=" * 82)
    print("VERDICT -- dimensionless-substrate on RPS (the real-emergent self-probe)")
    print("=" * 82)
    bar = [("D1 self-probe CLOSES: A_emp == A_closed (forced, not fitted)", d1),
           ("D2 canonical = noise-independent: A, omega/gamma FLAT across the drive", d2),
           ("D3 TUR floor holds: empirical T >= 1 at every operating point (fake-NaN tripwire clean)", d3),
           ("D4 structure-set: A TRACKS the ecology delta (not a universal constant)", d4)]
    for label, ok in bar:
        print(f"   [{'PASS' if ok else 'MISS'}]  {label}")
    if all(ok for _, ok in bar):
        print("\n  ==> INSTANCED on a REAL emergent substrate. RPS's emergent chiral Jacobian hosts the")
        print("      dimensionless self-probe T at the standard operating points: the affinity A (nats/cycle)")
        print(f"      and omega/gamma_eff are noise-independent canonical quantities (A = {A_emp.mean():.2f} nats,")
        print(f"      spread {100*A_spread:.1f}%), set by the ecology; the self-probe closes (A_emp == A_closed,")
        print(f"      err {100*close:.1f}%); the TUR floor T >= 1 holds. This is banach_frustrated's synthetic")
        print("      dimensionless dream re-read on a substrate whose chirality EMERGES, not drawn in.")
        print("      => dimensionless-substrate sharpening -> battery (runnable falsifier spec of record).")
    else:
        print("\n  ==> CLEAN MISS -- do NOT promote; report the miss (it sharpens the gate).")
        if not d3:
            print("      (D3 failed: T<1 or non-finite => the WINDING ESTIMATOR is broken, not the substrate.")
            print("       Raise N_REAL / T_OBS and re-run -- this is the fake-NaN tripwire, not a TUR violation.)")


def figure(sigmas, rowsN, rowsS):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.7), dpi=150)
    sig = np.array(sigmas)

    # panel 1: noise sweep -- A and omega/gamma flat (canonical); A_emp == A_closed (closes)
    A_emp = np.array([m["A_emp"] for m in rowsN]); A_cl = np.array([m["A_closed"] for m in rowsN])
    ratio = np.array([m["ratio"] for m in rowsN])
    a0 = ax[0]
    a0.plot(sig, A_emp, "o-", color="#6a1b9a", lw=2, label=r"$A_{\rm emp}$ (winding) — CANONICAL")
    a0.plot(sig, A_cl, "k--", lw=1.2, label=r"$A_{\rm closed}=2\pi\langle\sigma\rangle/\omega$ (forced)")
    a0.plot(sig, ratio, "s-", color="#2e7d32", lw=2, label=r"$\omega/\gamma_{\rm eff}$ — CANONICAL")
    a0.set_xlabel(r"demographic-noise drive $\sigma$"); a0.set_ylabel("dimensionless canonical quantities")
    a0.set_title("NOISE SWEEP: affinity & ω/γ FLAT (noise-independent);\nempirical affinity closes onto the forced form")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3); a0.set_ylim(bottom=0)

    # panel 2: the TUR self-probe T >= 1 (the floor), bounded
    Ts = np.array([m["T"] for m in rowsN])
    a1 = ax[1]
    a1.plot(sig, Ts, "^-", color="#1565c0", lw=2, ms=7, label=r"self-probe $T$ (measured)")
    a1.axhline(1.0, color="#c62828", ls="--", lw=1.4, label="TUR floor $T=1$")
    a1.set_xlabel(r"demographic-noise drive $\sigma$"); a1.set_ylabel(r"$T=\langle\sigma\rangle\tau\,\mathrm{Var}(J)/(2\langle J\rangle^2)$")
    a1.set_title("TUR self-probe bounded by 1 (the violation factor);\nT<1 would be a broken estimator, not a result")
    a1.legend(fontsize=9, frameon=False); a1.grid(alpha=0.3); a1.set_ylim(bottom=0)

    # panel 3: structure sweep -- A tracks the ecology (structure-set, not universal)
    deltas = [0.2, 0.35, 0.5, 0.65, 0.8]
    A_struct = np.array([m["A_closed"] for m in rowsS])
    a2 = ax[2]
    a2.plot(deltas, A_struct, "o-", color="#c2185b", lw=2, ms=7)
    a2.set_xlabel(r"ecological asymmetry $\delta=\alpha-\beta$"); a2.set_ylabel("affinity A (nats/cycle)")
    a2.set_title("STRUCTURE SWEEP: A tracks the ecology\n(structure-set fingerprint, not a universal constant)")
    a2.grid(alpha=0.3)

    fig.suptitle("RPS dimensionless self-probe — the real-emergent affinity as a noise-independent "
                 "canonical quantity (dimensionless-substrate)", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "rps_dimensionless.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
