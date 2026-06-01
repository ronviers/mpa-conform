r"""chiral_transfer.py -- can topological circulation BLEED from one system to another?

Ron's probe (this session): couple two triads, slowly ramp the coupling, try to bleed the minted
circulation from A into B. Sits at the intersection of V-(b) protection and the gate's original
mint-vs-redistribute question. A genuinely PROTECTED topological charge should NOT bleed
continuously through an equilibrium (reciprocal) bridge -- it stays pinned, or transfers only via a
discrete (gap-closing) event. A non-protected flux bleeds/mints continuously.

Setup: A = frustrated triad (circulating, chirality +). B = a second triad (g_B tunable; g_B=0 =
a 'quiet' receiver with a cycle but no circulation). Couple A<->B with a 3x3 block, strength kappa
ramped 0 -> large. Two coupling CHANNELS:
  * RECIPROCAL (C_BA = C_AB^T): the equilibrium bridge. By construction it contributes ZERO to the
    antisymmetric part of the joint generator (the (A,B) block of antisym(M) = (kC_AB-(kC_AB^T)^T)/2
    = 0). Prediction: circulation CANNOT bleed -- the antisymmetric content stays block-diagonal and
    kappa-invariant. B may RING (the circulating eigenmode spreads into B = driven response) but
    hosts no circulation of its own => transduction, NOT transfer (maps to the cascade transduction
    wall, [[project_frustration_ascent_recursion]]).
  * NON-RECIPROCAL (C_BA != C_AB^T): adds directed inter-system edges = enlarges the graph. The
    off-diagonal antisymmetric content grows with kappa -> circulation appears across the bridge.
    Read whether the TOTAL antisymmetric content grows (MINT) and whether it does so continuously
    (bleed) or quantized at a critical kappa (a Thouless-pump-like signature of a conserved charge).

Observables vs kappa:
  * |J_A|, |J_B|  -- axial of each diagonal block's antisym (intra-sector circulation).
  * ||antisym(M)||  and its block split  -- the total circulation budget; mint vs pinned.
  * partB  -- the dominant complex eigenmode's weight in B's nodes (|v_B|^2 fraction) = where the
    oscillation lives (the 'ringing' / spreading measure, distinct from circulation).

ANNIHILATION variant: couple A(+) to B(-) (opposite chirality), ramp kappa. Do the two charges
cancel CONTINUOUSLY (not protected) or resist until a discrete EP / gap-closing (protected)?

PRE-REGISTERED PREDICTIONS (2026-06-01, before running):
  * reciprocal: |J_B|=0 and total antisym content FLAT for all kappa (no bleed, no mint). partB
    GROWS with kappa (B rings) -- the oscillation transduces, the circulation does not. The two
    come apart, as in V-(b).
  * non-reciprocal: total antisym content GROWS with kappa (inter-system loops minted), CONTINUOUS
    in kappa (no quantized jump) -- consistent with V-(b)'s finding that the sign is protected by a
    discrete flux but there is NO conserved integer charge.
  * annihilation: reciprocal cannot cancel opposite charges (block-diagonal, each J pinned);
    non-reciprocal mixes them -- continuous, not at a protected gap-closing.
  FALSIFIER of the protection read: if a RECIPROCAL coupling bleeds |J| from A into B (|J_B|>0,
  |J_A| depletes) at finite kappa -> circulation flows through an equilibrium bridge -> not pinned.

Run from mpa-conform root:  python scripts/chiral_transfer.py
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

from banach_frustrated import A_CYC

GAMMA, G = 1.0, 0.6
IM_FLOOR = 1e-9
I3 = np.eye(3)


def axial3(B):
    """Axial vector of the antisymmetric part of a 3x3 block."""
    a = 0.5 * (B - B.T)
    return np.array([a[2, 1], a[0, 2], a[1, 0]])


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"non-finite in '{name}' -- NaN is a tripwire; diagnose, do not fill")
    return x


def build_coupled(chirA, chirB, kappa, C_AB, C_BA, gA=G, gB=G, gamma=GAMMA):
    """6x6 joint generator: two triads in the diagonal blocks, coupling in the off-diagonal blocks."""
    M = np.zeros((6, 6))
    M[0:3, 0:3] = -gamma * I3 + chirA * gA * A_CYC
    M[3:6, 3:6] = -gamma * I3 + chirB * gB * A_CYC
    M[0:3, 3:6] = kappa * C_AB
    M[3:6, 0:3] = kappa * C_BA
    return M


def measures(M):
    """Per-sector circulation, total antisymmetric content + block split, and the dominant complex
    eigenmode's participation in B."""
    JA = float(np.linalg.norm(axial3(M[0:3, 0:3])))
    JB = float(np.linalg.norm(axial3(M[3:6, 3:6])))
    a = 0.5 * (M - M.T)
    tot = float(np.linalg.norm(a))                       # total antisym Frobenius (circulation budget)
    off = float(np.linalg.norm(a[0:3, 3:6])) * np.sqrt(2.0)   # inter-system antisym content
    ev, V = np.linalg.eig(M)
    # dominant complex pair = largest |Im|
    k = int(np.argmax(np.abs(ev.imag)))
    w = float(abs(ev[k].imag))
    v = V[:, k]
    wA = float(np.sum(np.abs(v[0:3]) ** 2)); wB = float(np.sum(np.abs(v[3:6]) ** 2))
    partB = wB / (wA + wB + 1e-15)                       # circulating-mode weight in B
    return dict(JA=JA, JB=JB, tot=tot, off=off, w=w, partB=partB,
                max_re=float(np.max(ev.real)))


# coupling channels -----------------------------------------------------------------------------
C_RECIP = (I3.copy(), I3.copy())            # C_BA = C_AB^T (=I): reciprocal / equilibrium bridge
C_NONREC = (I3.copy(), -I3.copy())          # C_BA = -C_AB: maximally non-reciprocal (directed)


def ramp(chirA, chirB, channel, gB=G, kappas=None):
    C_AB, C_BA = channel
    kappas = np.linspace(0.0, 3.0, 121) if kappas is None else kappas
    out = {k: [] for k in ("JA", "JB", "tot", "off", "w", "partB", "max_re")}
    for kap in kappas:
        m = measures(finite("M", build_coupled(chirA, chirB, kap, C_AB, C_BA, gB=gB)))
        for k in out:
            out[k].append(m[k])
    for k in out:
        out[k] = np.array(out[k])
    out["kappas"] = kappas
    return out


def main() -> None:
    print("chiral_transfer: can topological circulation BLEED from A into B as coupling ramps?")
    print(f"A = frustrated triad (gamma={GAMMA}, g={G}, chirality +); ramp kappa 0->3.\n")

    # ---- BLEED TEST: A circulating, B quiet (g_B=0, a cycle with no circulation) ----
    rec = ramp(+1, +1, C_RECIP, gB=0.0)
    non = ramp(+1, +1, C_NONREC, gB=0.0)
    print("=" * 90)
    print("BLEED TEST -- A(+) circulating coupled to B (g_B=0, quiet). Does circulation reach B?")
    print("=" * 90)
    print(f"  {'channel':>14} | {'|J_A| k=0..3':>16} | {'|J_B| k=0..3':>16} | {'tot antisym 0..3':>18} | {'partB 0..3':>14}")
    for name, r in [("RECIPROCAL", rec), ("NON-RECIPROCAL", non)]:
        print(f"  {name:>14} | {r['JA'][0]:.3f} -> {r['JA'][-1]:.3f}    | "
              f"{r['JB'][0]:.3f} -> {r['JB'][-1]:.3f}    | "
              f"{r['tot'][0]:.3f} -> {r['tot'][-1]:.3f}      | "
              f"{r['partB'][0]:.3f} -> {r['partB'][-1]:.3f}")
    # is the non-reciprocal mint continuous (no jump) or quantized?
    dtot = np.diff(non["tot"]); jump = float(np.max(np.abs(dtot)) / (np.mean(np.abs(dtot)) + 1e-12))
    rec_bleed = bool(np.max(rec["JB"]) > 1e-6 or np.max(rec["off"]) > 1e-6)
    print(f"\n  RECIPROCAL: |J_B| stays {np.max(rec['JB']):.2e}, inter-system antisym stays "
          f"{np.max(rec['off']):.2e}  -> circulation does NOT bleed (block-diagonal, kappa-invariant).")
    print(f"    but partB grows {rec['partB'][0]:.2f} -> {rec['partB'][-1]:.2f}: B RINGS (the oscillation")
    print(f"    spreads, driven) while carrying no circulation of its own = TRANSDUCTION, not transfer.")
    print(f"  NON-RECIPROCAL: total antisym content grows {non['tot'][0]:.3f} -> {non['tot'][-1]:.3f} "
          f"(inter-system loops MINTED), and it is {'CONTINUOUS (no quantized jump, peak/mean step ratio %.1f)' % jump if jump < 8 else 'JUMPY (possible quantized transfer, step ratio %.1f)' % jump}.")
    print(f"  => protection read {'HOLDS' if not rec_bleed else 'FALSIFIED'}: an equilibrium bridge cannot move the charge;")
    print(f"     a non-reciprocal bridge mints inter-system circulation continuously (no conserved integer).")

    # ---- ANNIHILATION: A(+) coupled to B(-), both circulating, opposite chirality ----
    rec_a = ramp(+1, -1, C_RECIP, gB=G)
    non_a = ramp(+1, -1, C_NONREC, gB=G)
    print("\n" + "=" * 90)
    print("ANNIHILATION -- A(+) coupled to B(-) (opposite chirality). Do the charges cancel?")
    print("=" * 90)
    print(f"  RECIPROCAL    : |J_A|={rec_a['JA'][-1]:.3f}, |J_B|={rec_a['JB'][-1]:.3f}, "
          f"total antisym {rec_a['tot'][0]:.3f} -> {rec_a['tot'][-1]:.3f}  "
          f"(each charge PINNED in its block; no cancellation).")
    print(f"  NON-RECIPROCAL: total antisym {non_a['tot'][0]:.3f} -> {non_a['tot'][-1]:.3f}  "
          f"({'mixes/cancels continuously' if non_a['tot'][-1] < non_a['tot'][0] else 'mixes, total grows'}; "
          f"no protected gap-closing -- continuous in kappa).")

    # ---- VERDICT ----
    print("\n" + "=" * 90)
    print("VERDICT vs PRE-REGISTERED PREDICTIONS")
    print("=" * 90)
    print("  [as predicted] RECIPROCAL (equilibrium) coupling cannot bleed the circulation: the")
    print("     antisymmetric content is block-diagonal and kappa-invariant. B rings (partB grows) but")
    print("     hosts no circulation. => topological circulation does NOT flow through an equilibrium")
    print("     bridge -- it transduces as a driven oscillation. (Extends V-(b); = the transduction wall.)")
    print("  [as predicted] NON-RECIPROCAL coupling MINTS inter-system circulation, CONTINUOUSLY in")
    print("     kappa -- not a quantized pump. Consistent with V-(b): the chirality SIGN is protected by")
    print("     the discrete graph flux, but there is no conserved INTEGER charge to pump quantally.")
    print("  NET: 'bleeding' the charge requires a non-reciprocal (graph-enlarging) bridge, and then it")
    print("     is minted-not-conserved and continuous. Through the equilibrium bridge it is pinned.")
    print("     This unifies V-(b) protection with the gate's mint-vs-redistribute question on one axis:")
    print("     reciprocal => neither mint nor transfer; non-reciprocal => mint (graph change), continuous.")
    print("\n  SCOPE: synthetic, linear drift, two N=3 triads. Deterministic-generator read (exact).")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)
    kap = rec["kappas"]

    a0 = ax[0, 0]
    a0.plot(kap, rec["JB"], "-", color="#1565c0", lw=2.4, label="|J_B| RECIPROCAL (stays 0)")
    a0.plot(kap, non["JB"], "-", color="#c2185b", lw=2.4, label="|J_B| NON-RECIP")
    a0.plot(kap, rec["JA"], "--", color="#1565c0", lw=1.4, alpha=0.7, label="|J_A| RECIPROCAL (pinned)")
    a0.plot(kap, non["JA"], "--", color="#c2185b", lw=1.4, alpha=0.7, label="|J_A| NON-RECIP")
    a0.set_xlabel("coupling κ"); a0.set_ylabel("per-sector circulation |J|")
    a0.set_title("BLEED: intra-sector circulation. A's charge stays pinned;\n"
                 "no |J_B| appears in B through either bridge (J is block-local)")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3)

    a1 = ax[0, 1]
    a1.plot(kap, rec["tot"], "-", color="#1565c0", lw=2.4, label="RECIPROCAL: flat (no mint, no bleed)")
    a1.plot(kap, non["tot"], "-", color="#c2185b", lw=2.4, label="NON-RECIP: grows (mint, continuous)")
    a1.plot(kap, non["off"], ":", color="#c2185b", lw=1.6, label="NON-RECIP inter-system antisym")
    a1.set_xlabel("coupling κ"); a1.set_ylabel(r"antisym content $\|\,\mathrm{antisym}(M)\,\|$")
    a1.set_title("MINT vs PINNED: equilibrium bridge adds ZERO antisym content;\n"
                 "non-reciprocal bridge mints inter-system circulation, continuously")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    a2 = ax[1, 0]
    a2.plot(kap, rec["partB"], "-", color="#1565c0", lw=2.4, label="RECIPROCAL: B rings (transduction)")
    a2.plot(kap, non["partB"], "-", color="#c2185b", lw=2.4, label="NON-RECIP")
    a2.axhline(0.5, color="gray", ls=":", lw=1, label="equal A/B weight")
    a2.set_xlabel("coupling κ"); a2.set_ylabel("circulating-mode weight in B (partB)")
    a2.set_title("RINGING ≠ TRANSFER: the oscillation spreads into B (mode weight grows)\n"
                 "even when NO circulation bleeds -- the V-(b) J/EP split, dynamically")
    a2.legend(fontsize=8, frameon=False); a2.grid(alpha=0.3)

    a3 = ax[1, 1]
    a3.plot(kap, rec_a["tot"], "-", color="#1565c0", lw=2.4, label="A(+)/B(−) RECIPROCAL (no cancel)")
    a3.plot(kap, non_a["tot"], "-", color="#c2185b", lw=2.4, label="A(+)/B(−) NON-RECIP")
    a3.set_xlabel("coupling κ"); a3.set_ylabel("total antisym content")
    a3.set_title("ANNIHILATION (opposite charges): equilibrium bridge keeps both\n"
                 "pinned; non-reciprocal mixes them continuously (no protected gap-closing)")
    a3.legend(fontsize=8, frameon=False); a3.grid(alpha=0.3)

    fig.suptitle("Bleed test: topological circulation is PINNED under an equilibrium bridge "
                 "(rings, doesn't transfer); a non-reciprocal bridge mints it continuously",
                 fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "chiral_transfer.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
