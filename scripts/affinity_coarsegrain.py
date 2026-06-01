r"""affinity_coarsegrain.py -- STEP 1 (calibration): does sign(A) survive the LEGITIMATE coarse-graining?

The `scale-covariant-circulation` enabling-lemma check (mpa-atlas/framework/character_frontier.md).
The relocation strategy -- move the Central Commitment forbidding (protected circulation =>
triad) to a cheaper-to-test scale -- is licensed ONLY IF the cycle affinity's TOPOLOGICAL BIT
(sign + existence of the complex pair) survives the legitimate RG map:

    adiabatic Pi_slow  under  (A) local detailed balance on the eliminated subspace
                         AND  (B) b1-preservation (do not contract the loop).

Substrate: banach_frustrated -- the in-hand clean-A 3-cycle OU (M = -gamma I + g A_cyc;
complex pair -gamma +- i*sqrt(3) g = the k_frust signature; <sigma> = 6 g^2/gamma).

Procedure: embed a fast 4th mode, adiabatically eliminate it (Schur complement on the drift
+ the projected fast noise), read the affinity invariants before/after, across five maps:

  BARE                      the bare 3-cycle (reference)
  LEGIT off-plane           fast mode reciprocal, coupled to the NON-rotating (1,1,1) axis
                            (off the cycle's rotation plane) -> A_cyc untouched
  LEGIT in-plane recip.     fast mode reciprocal, coupled INTO the rotation plane
                            -> SYMMETRIC dressing: magnitude renormalizes
  A-VIOLATION non-recip.    fast mode carries its OWN current with the slow modes
                            -> ANTISYMMETRIC dressing: A leaks (EXPECTED loss, not a kill)
  B-VIOLATION lump          contract two cycle nodes (3->2): loop deleted, A=0
                            (rewiring per the Central Commitment edge-deletion clause;
                            EXPECTED, not a kill)

Verdict gate: sign(Im lambda) + the complex pair preserved under BOTH legit maps
=> the topological bit is scale-invariant => relocation licensed. The two illegitimate
maps are pre-classified expected-loss, so a sign flip there is not a kill.

Run from mpa-conform root:  python scripts/affinity_coarsegrain.py
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
for p in (str(REPO_ROOT), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from banach_frustrated import A_CYC, P  # the cyclic circulant + rotation-plane projector

GAMMA, G, D = 1.0, 0.6, 0.1     # banach_frustrated base operating point
GAMMA_F = 50.0                  # fast bystander rate (>> gamma  -> adiabatic)
C = 0.8                         # slow<->fast coupling strength
E1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)   # in rotation plane
E2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)   # in rotation plane
N111 = np.array([1.0, 1.0, 1.0]) / np.sqrt(3.0)  # the non-rotating axis (off-plane)


def ou_invariants(M, B):
    """Affinity invariants of a linear OU  dz = M z dt + sqrt(2B) dW  (B = diffusion matrix).

    Returns sign(Im lambda) [the chimeric/topological bit], omega = max|Im eig|,
    <sigma> (EP rate), and the per-cycle affinity A = 2*pi*<sigma>/omega (nats).
    """
    Sigma = solve_continuous_lyapunov(M, -2.0 * B)          # M Sigma + Sigma M^T = -2B
    Omega = M + B @ np.linalg.inv(Sigma)                    # irreversible (circulating) drift
    sigma = float(np.trace(Omega @ Sigma @ Omega.T @ np.linalg.inv(B)))
    ev = np.linalg.eigvals(M)
    k = int(np.argmax(np.abs(ev.imag)))
    omega = float(abs(ev.imag[k]))
    sign = int(np.sign(ev.imag[k])) if omega > 1e-9 else 0
    A = 2.0 * np.pi * sigma / omega if omega > 1e-9 else 0.0
    gam_eff = float(-ev.real[k])
    if not np.all(np.isfinite([sigma, omega, A])):
        raise FloatingPointError("non-finite invariant -- diagnose, do not fill")
    return dict(sign=sign, omega=omega, sigma=sigma, A=A, gam_eff=gam_eff, ev=ev)


def bare():
    return -GAMMA * np.eye(3) + G * A_CYC, D * np.eye(3)


def embed(b_in, b_out, gamma_f=GAMMA_F, c=C):
    """4-mode embedding: slow 3-cycle + one extra mode (rate gamma_f) coupled in via b_out,
    out via b_in. Reciprocal iff b_in == b_out. Adiabatic (legit) iff gamma_f >> GAMMA.
    Each mode carries its own noise D."""
    M = np.zeros((4, 4))
    M[:3, :3] = -GAMMA * np.eye(3) + G * A_CYC
    M[3, 3] = -gamma_f
    M[:3, 3] = c * b_out      # fast -> slow
    M[3, :3] = c * b_in       # slow -> fast
    B = D * np.eye(4)
    return M, B


def eliminate(M, B, n_slow=3):
    """Adiabatic elimination of the fast block: Schur complement on drift + projected noise."""
    Mss, Msf = M[:n_slow, :n_slow], M[:n_slow, n_slow:]
    Mfs, Mff = M[n_slow:, :n_slow], M[n_slow:, n_slow:]
    Mff_inv = np.linalg.inv(Mff)
    M_eff = Mss - Msf @ Mff_inv @ Mfs
    K = Msf @ Mff_inv
    B_eff = B[:n_slow, :n_slow] + K @ B[n_slow:, n_slow:] @ K.T   # ksi_s - K ksi_f
    return M_eff, B_eff


def lump_12():
    """B-VIOLATION: contract nodes 1,2 into one coordinate (3->2). A 2-mode current is
    gauge-removable -> no complex pair -> A=0. Project the bare drift onto {e0, (e1+e2)/sqrt2}."""
    M3, _ = bare()
    Q = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0] ])
    Q[1] /= np.linalg.norm(Q[1])                 # orthonormal lumping rows
    M2 = Q @ M3 @ Q.T
    B2 = D * (Q @ Q.T)
    return M2, B2


def main() -> None:
    print("STEP 1 -- scale-covariant-circulation: does sign(A) survive the legitimate coarse-graining?")
    print(f"banach_frustrated base: gamma={GAMMA}, g={G}, D={D}; fast bystander gamma_f={GAMMA_F}, coupling c={C}\n")

    cases = {}
    Mb, Bb = bare()
    cases["BARE"] = ou_invariants(Mb, Bb)

    # LEGIT off-plane: fast reciprocal coupling to the NON-rotating (1,1,1) axis (b1-preserving, off the loop)
    cases["LEGIT off-plane"] = ou_invariants(*eliminate(*embed(N111, N111)))
    # LEGIT in-plane reciprocal: fast reciprocal but coupled INTO the rotation plane (symmetric dressing)
    cases["LEGIT in-plane"] = ou_invariants(*eliminate(*embed(E1, E1)))
    # FAST non-reciprocal: fast (adiabatic OK) but non-reciprocal -> still 1/gamma_f-suppressed (robustness)
    cases["fast non-recip"] = ou_invariants(*eliminate(*embed(E1, E2)))
    # A-VIOLATION: eliminate a NON-fast (gamma_f ~ gamma) current-carrying mode -> breaks time-scale
    # separation (condition A); hides real EP -> the affinity VALUE leaks (Esposito hidden-EP)
    cases["A-VIOLATION (slow)"] = ou_invariants(*eliminate(*embed(E1, E2, gamma_f=1.0, c=1.6)))
    # B-VIOLATION: lump two cycle nodes (contract the loop)
    cases["B-VIOLATION (lump)"] = ou_invariants(*lump_12())

    ref = cases["BARE"]
    hdr = f"{'map':>20} | {'sign(Im)':>8} {'omega':>8} {'<sigma>':>9} {'A (nats)':>9} {'gam_eff':>8} | {'dA%':>7} {'verdict'}"
    print(hdr); print("-" * len(hdr))
    for name, c in cases.items():
        dA = 100.0 * (c["A"] - ref["A"]) / ref["A"] if ref["A"] else 0.0
        if name == "BARE":
            v = "reference"
        elif c["omega"] <= 1e-9:
            v = "A erased (loop gone)"
        elif c["sign"] != ref["sign"]:
            v = "SIGN FLIP (bit lost)"
        elif abs(dA) < 1.0:
            v = "bit + value preserved"
        elif abs(dA) < 5.0:
            v = "bit held; value renormalized"
        else:
            v = "bit held; VALUE WRONG (illegit map)"
        print(f"{name:>20} | {c['sign']:>+8d} {c['omega']:>8.4f} {c['sigma']:>9.4f} "
              f"{c['A']:>9.4f} {c['gam_eff']:>8.4f} | {dA:>+6.1f}% {v}")

    legit = [cases["LEGIT off-plane"], cases["LEGIT in-plane"], cases["fast non-recip"]]
    bit_held = all(c["sign"] == ref["sign"] and c["omega"] > 1e-9 for c in legit)
    dA_av = 100.0 * (cases["A-VIOLATION (slow)"]["A"] - ref["A"]) / ref["A"]

    print("\n================ VERDICT ================")
    if bit_held:
        print("TOPOLOGICAL BIT SCALE-INVARIANT. sign(Im lambda) + the complex pair survive every")
        print("adiabatic (fast-mode) elimination -- reciprocal off-plane, reciprocal in-plane, AND")
        print("non-reciprocal -- because the correction is 1/gamma_f-suppressed. => Relocation LICENSED:")
        print("the Central Commitment forbidding (protected circulation => triad) can be tested at the")
        print("cheapest scale and stays the same forbidding.")
        print(f"  - VALUE invariance is EXACT for the b1-preserving off-plane map (dA={100*(cases['LEGIT off-plane']['A']-ref['A'])/ref['A']:+.2g}%);")
        print(f"  - in-plane reciprocal renormalizes the value slightly (dA={100*(cases['LEGIT in-plane']['A']-ref['A'])/ref['A']:+.1f}%), sign held;")
        print(f"  - even fast NON-reciprocal holds (dA={100*(cases['fast non-recip']['A']-ref['A'])/ref['A']:+.1f}%) -- the SIGN/EXISTENCE bit is the robust invariant.")
    else:
        print("BIT NOT HELD under a legitimate map -- relocation NOT licensed; diagnose before proceeding.")
    print("\nThe discrimination -- two DIFFERENT illegitimacies, both pre-classified EXPECTED, not kills:")
    print(f"  A-VIOLATION (slow gamma_f~gamma, non-fast) -> affinity VALUE WRONG dA={dA_av:+.0f}% "
          f"[A={cases['A-VIOLATION (slow)']['A']:.2f} vs {ref['A']:.2f} nats]")
    print("    = the adiabatic-elimination formula MISAPPLIED to a non-fast mode (breaks time-scale")
    print("    separation, condition A). Here it spuriously INFLATES the affinity. NOT a kill -- the")
    print("    map is illegitimate (you cannot adiabatically eliminate a mode that isn't fast).")
    print(f"  B-VIOLATION (lump/marginalize 2 nodes) -> A={cases['B-VIOLATION (lump)']['A']:.3g}, omega={cases['B-VIOLATION (lump)']['omega']:.3g} "
          "= the current-LOSING direction")
    print("    (Esposito under-estimate, taken to its extreme: lumping across the loop hides ALL the")
    print("    current -> A=0). = rewiring per the Central Commitment edge-deletion clause. NOT a kill.")
    print("\nHonest nuance: the SIGN/EXISTENCE bit is robust (survives every adiabatic map, even non-")
    print("reciprocal); the affinity VALUE is exactly invariant only under the b1-preserving (off-plane)")
    print("map. The forbidding (protected circulation => triad) needs only sign/existence -> LICENSED.")

    # ---- figure: spectra of the five maps + invariant bars ----
    fig, (axs, axb) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
    colors = {"BARE": "#222", "LEGIT off-plane": "#2f855a", "LEGIT in-plane": "#2b6cb0",
              "fast non-recip": "#38a169", "A-VIOLATION (slow)": "#c53030",
              "B-VIOLATION (lump)": "#dd8b1a"}
    axs.axhline(0, color="gray", lw=0.6); axs.axvline(0, color="gray", lw=0.6)
    for name, c in cases.items():
        ev = c["ev"]
        axs.scatter(ev.real, ev.imag, s=90, color=colors[name], label=name, edgecolor="white", linewidth=0.5, zorder=3)
    axs.set_xlabel("Re(eig)"); axs.set_ylabel("Im(eig)")
    axs.set_title("M spectra: complex pair (Im != 0) = the k_frust bit\nlegit maps keep it; lump kills it")
    axs.legend(fontsize=8, frameon=False); axs.grid(alpha=0.3)

    names = list(cases.keys())
    Avals = [cases[n]["A"] for n in names]
    bars = axb.bar(range(len(names)), Avals, color=[colors[n] for n in names], edgecolor="k", linewidth=0.5)
    axb.axhline(ref["A"], ls="--", color="#222", lw=1, alpha=0.6, label=f"bare A = {ref['A']:.3f} nats")
    axb.set_xticks(range(len(names))); axb.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    axb.set_ylabel("affinity A per cycle (nats)")
    axb.set_title("affinity value across maps\n(off-plane preserves; in-plane renormalizes; A-viol leaks; lump -> 0)")
    axb.legend(fontsize=8, frameon=False); axb.grid(alpha=0.3, axis="y")

    fig.suptitle("STEP 1 -- scale-covariant-circulation: topological bit survives the legitimate coarse-graining",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "step1_affinity_coarsegrain.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
