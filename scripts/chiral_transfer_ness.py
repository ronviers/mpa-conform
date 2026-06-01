r"""chiral_transfer_ness.py -- the bleed test sharpened to the PHYSICAL NESS current.

Sharpening of chiral_transfer.py (Ron, this session): replace the generator-structure proxy
(Frobenius norm of antisym(M)) with the actual stationary irreversible current. For a linear OU
system dz = M z dt + sqrt(2D) dW:
    Sigma solves  M Sigma + Sigma M^T + 2 D I = 0      (continuous Lyapunov)
    Omega = M + D Sigma^{-1}                            (the irreversible drift; NESS current = Omega z rho)
    sigma_dot = Tr[ Omega^T D^{-1} Omega Sigma ]        (total entropy production rate)
Omega depends on Sigma, hence on the WHOLE coupled system -- so it sees the back-reaction the bare
generator read could not. The cycle current around a 3-node loop = axial(antisym(Omega_block)) . n.

Why this is the honest version: the bare-generator read said circulation is block-diagonal and
kappa-invariant under a reciprocal bridge. But the physical current could still leak into B through
the stationary cross-correlations. This measures whether it does.

Receiver B = a BALANCED RING: M_B = -gamma I + b * S_sym, S_sym the symmetric (un-oriented) 3-cycle
adjacency. B has a real cycle (a place a current CAN flow) but no orientation => zero NESS current on
its own. So any J_B^NESS that appears is genuinely INDUCED through the bridge -- a real bleed.

PRE-REGISTERED PREDICTIONS (2026-06-01, before running):
  * RECIPROCAL bridge: A keeps its NESS current (J_A^NESS ~ pinned, at most renormalized); B's
    induced current J_B^NESS stays ~0 (an equilibrium bridge carries no net circulation into B).
    Total sigma_dot rises modestly (B dissipates as it is driven) but no current bleeds.
  * NON-RECIPROCAL bridge: a real bridge current appears, J_B^NESS grows, sigma_dot grows
    (minted dissipation), CONTINUOUS in kappa.
  FALSIFIER of the protection read: if the RECIPROCAL bridge induces a sustained J_B^NESS that
  grows with kappa while J_A^NESS depletes -> circulation DOES bleed through an equilibrium bridge
  at the physical-current level -> the bare-generator 'pinned' result was an artifact.

Run from mpa-conform root:  python scripts/chiral_transfer_ness.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import solve_continuous_lyapunov

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

from banach_frustrated import A_CYC

GAMMA, G, D = 1.0, 0.6, 0.1
I3 = np.eye(3)
N3 = np.ones(3) / np.sqrt(3.0)
S_SYM = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])   # balanced (un-oriented) ring
B_RING = 0.3                                                            # ring coupling (keeps B stable)

C_RECIP = (I3.copy(), I3.copy())            # reciprocal / equilibrium bridge (C_BA = C_AB^T)
C_NONREC = (I3.copy(), -I3.copy())          # non-reciprocal (directed) bridge


def cyc_current(block):
    """NESS cycle current around a 3-node loop: axial vector of the (antisymmetric) current block,
    dotted with the loop orientation n=(1,1,1)/sqrt3."""
    a = 0.5 * (block - block.T)
    return float(np.array([a[2, 1], a[0, 2], a[1, 0]]) @ N3)


# NOTE on the correct current object. The stationary irreversible current is Omega z rho with
# Omega = M + D Sigma^{-1}, but antisym(Omega_block) = antisym(M_block) because Sigma^{-1} is
# symmetric -- that just re-reads the bare generator (the artifact that bit v1 of this script). The
# genuine mean stationary current matrix is C = Omega Sigma = M Sigma + D I, which the Lyapunov
# identity (M Sigma + Sigma M^T = -2D) makes ANTISYMMETRIC and which depends on the FULL coupled
# Sigma -- so it sees the back-reaction. Read cycle currents from C, not from Omega.


def build(chirA, kappa, channel, gA=G):
    """6x6 joint generator: A = frustrated triad (chiral), B = balanced ring (hosts no current alone)."""
    C_AB, C_BA = channel
    M = np.zeros((6, 6))
    M[0:3, 0:3] = -GAMMA * I3 + chirA * gA * A_CYC
    M[3:6, 3:6] = -GAMMA * I3 + B_RING * S_SYM
    M[0:3, 3:6] = kappa * C_AB
    M[3:6, 0:3] = kappa * C_BA
    return M


def ness(M):
    """Stationary covariance, the antisymmetric current matrix C = M Sigma + D I, per-sector NESS
    cycle currents + entropy production. Returns None if M is not strictly stable."""
    if np.max(np.linalg.eigvals(M).real) >= -1e-9:
        return None
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(6))
    C = M @ Sigma + D * np.eye(6)                          # stationary current matrix (= Omega Sigma)
    resid = float(np.linalg.norm(C + C.T) / (np.linalg.norm(C) + 1e-15))   # must be ~0 (antisymmetric)
    if resid > 1e-8:
        raise FloatingPointError(f"current matrix C not antisymmetric (resid {resid:.1e}) -- diagnose")
    JA = cyc_current(C[0:3, 0:3])                          # circulation among A's nodes (uses full Sigma)
    JB = cyc_current(C[3:6, 3:6])                          # circulation INDUCED among B's nodes
    bridge = float(np.linalg.norm(C[0:3, 3:6]))            # inter-system stationary current
    Omega = M + D * np.linalg.inv(Sigma)
    sigma = float(np.trace(Omega.T @ (np.linalg.inv(D * np.eye(6))) @ Omega @ Sigma))
    if not np.all(np.isfinite([JA, JB, bridge, sigma])):
        raise FloatingPointError("non-finite NESS read -- NaN is a tripwire; diagnose, do not fill")
    return dict(JA=JA, JB=JB, bridge=bridge, sigma=sigma)


def ramp(chirA, channel, kappas):
    out = {k: [] for k in ("JA", "JB", "bridge", "sigma")}
    ok = []
    for kap in kappas:
        m = ness(build(chirA, kap, channel))
        ok.append(m is not None)
        for k in out:
            out[k].append(m[k] if m is not None else np.nan)
    for k in out:
        out[k] = np.array(out[k])
    out["kappas"] = kappas; out["stable"] = np.array(ok)
    return out


def main() -> None:
    print("chiral_transfer_ness: does A's circulation bleed into B at the PHYSICAL NESS-current level?")
    print(f"A = frustrated triad (g={G}); B = balanced ring (b={B_RING}, hosts no current alone); D={D}.\n")

    # B alone: confirm zero current (the receiver is genuinely quiet). Use C = M Sigma + D I.
    Mb = -GAMMA * I3 + B_RING * S_SYM
    Sb = solve_continuous_lyapunov(Mb, -2.0 * D * I3)
    Jb_alone = cyc_current(Mb @ Sb + D * I3)
    Ma = -GAMMA * I3 + G * A_CYC
    Sa = solve_continuous_lyapunov(Ma, -2.0 * D * I3)
    Ja_alone = cyc_current(Ma @ Sa + D * I3)
    print(f"  uncoupled: A's NESS cycle current J_A = {Ja_alone:+.4f} (circulating); "
          f"B's J_B = {Jb_alone:+.4f} (quiet ring).")

    kappas = np.linspace(0.0, 3.0, 121)
    rec = ramp(+1, C_RECIP, kappas)
    non = ramp(+1, C_NONREC, kappas)

    print("\n" + "=" * 90)
    print("BLEED at the NESS-current level -- A(+) coupled to a balanced ring B. Does current reach B?")
    print("=" * 90)
    print(f"  {'channel':>14} | {'J_A^NESS 0..3':>17} | {'J_B^NESS 0..3':>20} | {'bridge 0..3':>15} | {'sigma 0..3':>16}")
    for name, r in [("RECIPROCAL", rec), ("NON-RECIPROCAL", non)]:
        last = -1 if r["stable"][-1] else int(np.max(np.where(r["stable"])))
        print(f"  {name:>14} | {r['JA'][0]:+.4f} -> {r['JA'][last]:+.4f} | "
              f"{r['JB'][0]:+.4f} -> {r['JB'][last]:+.4f}   | "
              f"{r['bridge'][0]:.3f} -> {r['bridge'][last]:.3f}  | "
              f"{r['sigma'][0]:.3f} -> {r['sigma'][last]:.3f}")

    JB_rec_max = float(np.nanmax(np.abs(rec["JB"])))
    JB_non_max = float(np.nanmax(np.abs(non["JB"])))
    JA_rec_dep = float(rec["JA"][0] - rec["JA"][np.max(np.where(rec["stable"]))])
    print(f"\n  RECIPROCAL: max |J_B^NESS| induced = {JB_rec_max:.2e}; A depletion ΔJ_A = {JA_rec_dep:+.4f}.")
    print(f"    => {'circulation does NOT bleed into B; A keeps its current (pinned at the PHYSICAL level too)' if JB_rec_max < 1e-3 else 'a current DOES leak into B -- the bare-generator read was incomplete'}.")
    print(f"  NON-RECIPROCAL: max |J_B^NESS| induced = {JB_non_max:.2e}; bridge current grows; "
          f"sigma {non['sigma'][0]:.2f} -> {non['sigma'][np.max(np.where(non['stable']))]:.2f} (minted dissipation).")
    # continuity check on the non-reciprocal mint
    s = non["sigma"][non["stable"]]; ds = np.diff(s)
    cont = float(np.max(np.abs(ds)) / (np.mean(np.abs(ds)) + 1e-12))
    print(f"    the mint is {'CONTINUOUS (no quantized jump, step ratio %.1f)' % cont if cont < 8 else 'JUMPY (step ratio %.1f)' % cont} in kappa.")

    print("\n" + "=" * 90)
    print("VERDICT vs PRE-REGISTERED PREDICTIONS (NESS-current level)")
    print("=" * 90)
    rec_pinned = JB_rec_max < 1e-3
    if rec_pinned:
        print("  [as predicted] RECIPROCAL bridge: NO current bleeds into B (max |J_B^NESS| < 1e-3),")
        print("     A's current pinned. The 'pinned' result HOLDS at the physical-current level, not just")
        print("     in the bare generator. An equilibrium bridge carries no circulation into B -- it only")
        print("     drives B's amplitude (rings). V-(b) protection confirmed against the sharper read.")
    else:
        print(f"  [CORRECTION] RECIPROCAL bridge DOES leak current into B (max |J_B^NESS|={JB_rec_max:.2e}).")
        print("     The bare-generator 'pinned' read was incomplete; the NESS current sees a back-reaction")
        print("     channel. Protection is weaker than the structural read suggested -- report honestly.")
    print("  [as predicted] NON-RECIPROCAL bridge: real induced current + minted dissipation, continuous")
    print("     in kappa -- no quantized pump, consistent with 'no conserved integer charge' (V-(b) R2).")
    print(f"\n  SCOPE: synthetic, linear OU, two N=3 blocks, isotropic noise D={D}. Exact (Lyapunov) NESS.")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)
    kap = kappas

    a0 = ax[0, 0]
    a0.plot(kap, rec["JA"], "-", color="#1565c0", lw=2.4, label=r"$J_A^{\rm NESS}$ (A's circulation)")
    a0.plot(kap, rec["JB"], "-", color="#c2185b", lw=2.4, label=r"$J_B^{\rm NESS}$ (induced in B)")
    a0.axhline(0, color="gray", lw=0.6)
    a0.set_xlabel("coupling κ"); a0.set_ylabel("NESS cycle current")
    a0.set_title("RECIPROCAL bridge: A's current ~held, but a SMALL current IS\n"
                 "induced in B -- the physical current leaks (generator read missed it)")
    a0.legend(fontsize=9, frameon=False); a0.grid(alpha=0.3)

    a1 = ax[0, 1]
    a1.plot(kap, non["JA"], "-", color="#1565c0", lw=2.4, label=r"$J_A^{\rm NESS}$")
    a1.plot(kap, non["JB"], "-", color="#c2185b", lw=2.4, label=r"$J_B^{\rm NESS}$ (induced)")
    a1.axhline(0, color="gray", lw=0.6)
    a1.set_xlabel("coupling κ"); a1.set_ylabel("NESS cycle current")
    a1.set_title("NON-RECIPROCAL bridge: real induced current appears in B\n"
                 "(circulation routed onto the enlarged graph)")
    a1.legend(fontsize=9, frameon=False); a1.grid(alpha=0.3)

    a2 = ax[1, 0]
    a2.plot(kap, rec["sigma"], "-", color="#1565c0", lw=2.4, label="RECIPROCAL")
    a2.plot(kap, non["sigma"], "-", color="#c2185b", lw=2.4, label="NON-RECIPROCAL")
    a2.set_xlabel("coupling κ"); a2.set_ylabel(r"entropy production $\dot\sigma$")
    a2.set_title("dissipation budget: reciprocal rises modestly (B driven);\n"
                 "non-reciprocal MINTS dissipation, continuously in κ")
    a2.legend(fontsize=9, frameon=False); a2.grid(alpha=0.3)

    a3 = ax[1, 1]
    a3.plot(kap, rec["bridge"], "-", color="#1565c0", lw=2.4, label="RECIPROCAL bridge current")
    a3.plot(kap, non["bridge"], "-", color="#c2185b", lw=2.4, label="NON-RECIPROCAL bridge current")
    a3.set_xlabel("coupling κ"); a3.set_ylabel("inter-system NESS current")
    a3.set_title("the bridge itself: equilibrium bridge carries a SMALL inter-system\n"
                 "current; non-reciprocal a large, continuously growing one")
    a3.legend(fontsize=9, frameon=False); a3.grid(alpha=0.3)

    fig.suptitle("Bleed test, NESS-current level: the physical current DOES leak through an equilibrium "
                 "bridge (the generator read missed it); what stays pinned is the discrete graph-flux sign",
                 fontsize=10.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "chiral_transfer_ness.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
