r"""emergent_identity_dna_ness.py -- the real-instance TEMPLATE (Nicholas DNA-NESS), vetted.

The 3rd channel return's best output (model b) is a discrete-state reduction of the Nicholas et al.
dissipative DNA-NESS (Angew. Chem. Int. Ed. 2025, 10.1002/anie.202512967; open PMC12535392) to a
linear N=3 Markov generator with a GENUINE two-module minting structure:

  States: 0 = OQ (quencher.output)   1 = FQ (quencher.fuel)   2 = Q (free quencher)

  Module A -- reversible DNA/RNA hybridization (a FULL triangle, OQ<->FQ<->Q<->OQ).
    Pure base-pairing; rates set by equilibrium binding free energies => obeys detailed balance
    => its cycle affinity A_A = 0 ON ITS OWN, even though the cycle GRAPH already exists.
  Module B -- RNase H enzymatic hydrolysis: an irreversible drain FQ -> Q (degrades the RNA fuel).
    A single directed edge; acyclic; A_B = 0 on its own.
  Coupling: Module B adds an irreversible FQ->Q pathway PARALLEL to A's reversible FQ<->Q, driving
    the pre-existing balanced cycle out of detailed balance => A != 0. The circulation is MINTED
    by the enzyme drive -- more physical than "add a third edge": the structure pre-exists, the
    *protected current* is what coupling creates.

This is a STRONGER minting reading than emergent_identity.py (path+edge) and emergent_identity_n4.py
(allosteric square): here the cycle graph is present in the passive module and the *affinity* is
minted by a genuinely distinct physical agent (the enzyme).

TWO modes:
  --illustrative (default): run with detailed-balance-respecting PLACEHOLDER rates (clearly NOT the
     measured values) to VET that model b's reduction structurally yields all three components.
     This validates the reduction; it is NOT a gate discharge.
  measured: supply the 7 rate constants from Nicholas SI Tables S4/S5 (see SLOTS below). Then it is
     the real instance -- run it and read the verdict. We do NOT invent these numbers.

Usage (from mpa-conform root):  python scripts/emergent_identity_dna_ness.py
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

CYCLE = [(0, 1), (1, 2), (2, 0)]   # OQ -> FQ -> Q -> OQ


# ---- MEASURED rates: Nicholas et al., Angew. Chem. 2025, SI Tables S4/S5 (Exp. Fig. 2b) + Sec. 3 ----
# The cycle affinity is INDEPENDENT of [F],[O] -- they cancel around OQ->FQ->Q->OQ (each appears once
# forward, once backward). So minting + protection are fixed by the MEASURED constants alone; the bath
# values affect only the absolute current MAGNITUDE, not any of the three component verdicts.
def nicholas_fig2b():
    # raw SI constants (Tables S4 common + S5 Fig.2b; enzyme conc from Sec.3 text)
    kdisp, kdisp_r = 6.61e5, 5000.0      # S5 / S4   strand displacement fwd/rev (M^-1 s^-1)
    kOreb, kOreb_r = 5e8, 1e-6           # S4        output rebinding fwd (M^-1 s^-1) / rev (s^-1)
    kFreb          = 5e8                 # S4        fuel rebinding fwd (M^-1 s^-1)
    kcat, kenz, kenz_r = 2.65, 3.2e7, 0.1  # S5 / S5 / S4   catalysis / enzyme binding fwd-rev
    E_conc         = 5.0e-10             # Sec.3 text  RNase H concentration (M)
    # kFrebind_r is SET BY DETAILED BALANCE on the OQ-F-O-FQ-Q cycle (SI: "adjusted by DB constraints"):
    #   kdisp * kFreb_r * kOreb = kdisp_r * kOreb_r * kFreb
    kFreb_r = kdisp_r * kOreb_r * kFreb / (kdisp * kOreb)   # = 7.56e-9 (SI publishes 7.6e-9 -- matches)
    # enzymatic FQ->Q effective rate (pseudo-first-order, QSS on FQE): kcat*kenz*[E]/(kenz_r+kcat)
    k_deg = kcat * kenz * E_conc / (kenz_r + kcat)         # ~ 0.0154 s^-1  (the DRIVE = Module B)
    k = dict(k_disp=kdisp, k_rev_disp=kdisp_r, k_unbind_F=kFreb_r, k_bind_F=kFreb,
             k_hyb=kOreb, k_unbind_O=kOreb_r, k_deg=k_deg)
    baths = dict(F_conc=1e-8, O_conc=2.5e-8)   # representative NESS (cancel in affinity; magnitude only)
    return k, baths


MEASURED, BATHS = nicholas_fig2b()


def build_rates(k, baths, with_enzyme=True, with_moduleA=True):
    """effective first-order rates {(i,j): rate i->j}. Module A = hybridization; Module B = k_deg."""
    r = {}
    if with_moduleA:
        r[(0, 1)] = k["k_disp"] * baths["F_conc"]       # OQ -> FQ
        r[(1, 0)] = k["k_rev_disp"] * baths["O_conc"]   # FQ -> OQ
        r[(1, 2)] = k["k_unbind_F"]                     # FQ -> Q   (hybridization part)
        r[(2, 1)] = k["k_bind_F"] * baths["F_conc"]     # Q  -> FQ
        r[(2, 0)] = k["k_hyb"] * baths["O_conc"]        # Q  -> OQ
        r[(0, 2)] = k["k_unbind_O"]                     # OQ -> Q
    if with_enzyme:
        r[(1, 2)] = r.get((1, 2), 0.0) + k["k_deg"]     # Module B drain ADDS to FQ -> Q
    return r


def generator(rates, n=3):
    L = np.zeros((n, n))
    for (i, j), w in rates.items():
        L[j, i] += w
        L[i, i] -= w
    return L


def stationary(L):
    n = L.shape[0]
    A = np.vstack([L, np.ones(n)]); b = np.zeros(n + 1); b[-1] = 1.0
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    return p


def affinity(rates):
    cw = CYCLE; ccw = [(j, i) for (i, j) in CYCLE]
    if not all(e in rates for e in cw + ccw):
        return 0.0
    return float(np.log(np.prod([rates[e] for e in cw]) / np.prod([rates[e] for e in ccw])))


def current(rates):
    if (0, 1) not in rates or (1, 0) not in rates:
        return 0.0
    p = stationary(generator(rates))
    return float(rates[(0, 1)] * p[0] - rates[(1, 0)] * p[1])


def run_protocol(k, baths, label):
    print("=" * 88)
    print(f"  {label}")
    print("=" * 88)

    # MINTING: Module A alone (detailed-balanced triangle), Module B alone, coupled.
    rA = build_rates(k, baths, with_enzyme=False, with_moduleA=True)
    rB = build_rates(k, baths, with_enzyme=True, with_moduleA=False)
    rU = build_rates(k, baths, with_enzyme=True, with_moduleA=True)
    AA, AB, AU = affinity(rA), affinity(rB), affinity(rU)
    JU = current(rU)
    print("\n  [MINTING]")
    print(f"    Module A alone (reversible hybridization triangle): A = {AA:+.3e}  "
          f"(detailed balance -- Kolmogorov check)")
    print(f"    Module B alone (enzyme drain FQ->Q, acyclic):       A = {AB:+.3e}")
    print(f"    coupled (A + enzyme):                                A = {AU:+.4f}  J = {JU:+.4e}")
    minted = abs(AA) < 1e-9 and abs(AB) < 1e-9 and abs(AU) > 1e-6 and abs(JU) > 1e-12
    print(f"    => Module A detailed-balanced AND coupling mints the current: {minted}")
    if abs(AA) >= 1e-9:
        print("    !! Module A is NOT detailed-balanced for these rates -- model b's reduction claim")
        print("       fails for this rate set (the hybridization rates violate Kolmogorov).")

    # PROTECTION: sign(A) is set by the (one-way) enzyme drive; reversible-rate deformations cannot flip it.
    print("\n  [PROTECTION]")
    rng = np.random.default_rng(0)
    s0 = np.sign(AU); flips = 0
    for _ in range(400):
        # RECIPROCAL deformation: scale each reversible EDGE's two directions TOGETHER (preserves
        # Module A's detailed balance), holding the enzyme drive k_deg fixed. (Scaling rates
        # independently would inject affinity into Module A -- not a reciprocal/gauge deformation.)
        s1, s2, s3 = np.exp(2.0 * rng.standard_normal(3))
        kk = dict(k)
        kk["k_disp"] *= s1; kk["k_rev_disp"] *= s1        # OQ<->FQ edge
        kk["k_unbind_F"] *= s2; kk["k_bind_F"] *= s2      # FQ<->Q hybridization edge (k_deg fixed)
        kk["k_hyb"] *= s3; kk["k_unbind_O"] *= s3         # Q<->OQ edge
        flips += int(np.sign(affinity(build_rates(kk, baths))) != s0)
    print(f"    reciprocal deformations of the hybridization (Module A) rates (n=400): "
          f"sign-flips = {flips}/400")
    print(f"    the enzyme is irreversible (k_deg>=0), so sign(A) is drive-locked: it cannot be")
    print(f"    flipped by any deformation, only zeroed by removing the drive (stronger than 'rewire').")
    protected = flips == 0

    # SUSTAINED IDENTITY: remove the enzyme/drive (k_deg->0) OR sever a hybridization edge -> collapse.
    print("\n  [SUSTAINED IDENTITY]  (drive = the enzyme; removing it restores detailed balance)")
    k_nodrive = dict(k); k_nodrive["k_deg"] = 0.0
    J_on = current(rU)
    J_nodrive = current(build_rates(k_nodrive, baths))
    J_severed = current(build_rates(k, baths, with_enzyme=True, with_moduleA=True) | {(2, 0): 0.0, (0, 2): 0.0})
    print(f"    enzyme ON  : J = {J_on:+.4e}   <- minted NESS current")
    print(f"    enzyme OFF (k_deg=0): J = {J_nodrive:+.3e}   <- detailed balance restored, collapses")
    print(f"    Q<->OQ edge severed (cycle opened): J = {J_severed:+.3e}   <- no cycle")
    sustained = abs(J_on) > 1e-12 and abs(J_nodrive) < 1e-9 and abs(J_severed) < 1e-9
    print(f"    => run loop, nothing stored: {sustained}")

    return minted, protected, sustained


def illustrative_rates():
    """detailed-balance-respecting PLACEHOLDER rates (NOT measured) -- structure-check only.

    Effective rates chosen so Module A's cycle product fwd/bwd = 1 (Kolmogorov): with concentrations
    folded in, OQ->FQ=2, FQ->OQ=1, FQ->Q(hyb)=3, Q->FQ=1, Q->OQ=1, OQ->Q=6  => 2*3*1 == 1*1*6.
    Then the enzyme adds k_deg to FQ->Q.  k_disp/F_conc etc. are back-solved to those effective rates.
    """
    F, O = 1.0, 1.0
    k = dict(
        k_disp=2.0 / F, k_rev_disp=1.0 / O,
        k_unbind_F=3.0, k_bind_F=1.0 / F,
        k_hyb=1.0 / O, k_unbind_O=6.0,
        k_deg=4.0,                         # the illustrative drive
    )
    return k, dict(F_conc=F, O_conc=O)


def main():
    print("EMERGENT IDENTITY -- DNA-NESS real-instance template (Nicholas et al., Angew. 2025)\n")
    measured_ready = all(v is not None for v in MEASURED.values()) and all(
        v is not None for v in BATHS.values())

    if measured_ready:
        print(">>> MEASURED rates (Nicholas SI S4/S5, Exp. Fig.2b) -- the REAL instance.\n")
        minted, protected, sustained = run_protocol(MEASURED, BATHS,
                                                     "REAL INSTANCE -- Nicholas DNA-NESS (measured rates)")
        print("\n" + "=" * 88)
        print("VERDICT (real instance)")
        print("=" * 88)
        if minted and protected and sustained:
            print("  The first REAL, MEASURED driven network PASSES all three components through the")
            print("  protocol: a detailed-balanced DNA-hybridization cycle (A=0, the SI enforces DB)")
            print("  is driven by RNase-H fuel hydrolysis into a protected, sustained NESS circulation.")
            print("  The minting + protection use ONLY measured rate constants ([F],[O] cancel in the")
            print("  affinity); the rates are experimentally fitted, not hand-set.")
            print("\n  Honest scope (NOT a triumphant discharge -- the caveats are real):")
            print("   - N=3 reduction of a nonlinear 10-species CRN: enzyme folded to a pseudo-first-")
            print("     order drain k_deg (QSS on FQE, [E] chemostatted); output O / fuel F are baths.")
            print("   - [F],[O] cancel in the affinity (the protected quantity) but set the current")
            print("     magnitude; representative NESS values used there.")
            print("   - kFrebind_r taken from the SI's own detailed-balance constraint (matches the")
            print("     published 7.6e-9 to 2 sig figs); the DB of Module A is the SI's, not ours.")
            print("  => a genuine Gate-2 emergent-identity DISCHARGE CANDIDATE, pending an independent")
            print("     cross-check against the full nonlinear COPASI model + review. NOT synthetic.")
        else:
            print(f"  NOT a clean pass: minted={minted} protected={protected} sustained={sustained}.")
            print("  Read honestly -- the real kinetics may not satisfy the minting structure.")
        return

    print(">>> MEASURED rates NOT yet supplied. Running the STRUCTURE-CHECK (illustrative rates).")
    print("    This VETS model b's reduction; it is NOT the real instance and NOT a gate discharge.\n")
    k, baths = illustrative_rates()
    minted, protected, sustained = run_protocol(k, baths,
                                                "STRUCTURE-CHECK -- illustrative DB-respecting rates (NOT measured)")
    print("\n" + "=" * 88)
    print("VERDICT (structure-check)")
    print("=" * 88)
    print(f"  model b's DNA-NESS reduction yields all three components: "
          f"minted={minted} protected={protected} sustained={sustained} -> "
          f"{'STRUCTURE VALID' if (minted and protected and sustained) else 'STRUCTURE PROBLEM'}")
    print("  The reduction is sound: a detailed-balanced hybridization triangle + an irreversible")
    print("  enzyme drain mints a protected, sustained NESS circulation -- the genuine emergent-")
    print("  identity structure (more physical than path+edge: the cycle pre-exists, the enzyme")
    print("  mints the *current*).")
    print("\n  AWAITING (the ONLY remaining gap): 7 rate constants from Nicholas SI Tables S4/S5 --")
    miss = [kk for kk, v in MEASURED.items() if v is None] + [kk for kk, v in BATHS.items() if v is None]
    print(f"    {', '.join(miss)}")
    print("  Fill MEASURED/BATHS above with the SI numbers (do NOT invent them) and re-run for the")
    print("  real instance. Not web-extractable (SI 403 / Zenodo zip); needs the SI PDF or screenshots.")


if __name__ == "__main__":
    main()
