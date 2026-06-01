r"""emergent_identity_n4.py -- the channel's best concrete lead, instanced through OUR protocol.

The Gate-2 substrate re-screen (docs/emergent_identity_substrate_prompt.md) returned a 3-model
report. Its strongest concrete candidate (model b Cand 1 / model c primary) is the **4-state
bipartite allosteric** network: two GENUINELY INDEPENDENT 2-state subsystems, each provably
acyclic (a 2-node graph has one edge -> no cycle -> A=0 by DIMENSION, not by a modeller's choice),
coupled by allosteric gating into a 4-cycle. This is a less-trivial minting than the path+edge of
emergent_identity.py -- it answers model a's sharp caveat ("is the minting more than the obvious
'adding the third edge creates a cycle'?"): here the cycle is minted by GATING, the mechanism real
molecular machines (motors, allosteric enzymes, information engines) actually use.

TWO jobs, both "check the work" (the report is mid-tier; model c claimed GATE DISCHARGED by running
its OWN reconstruction of emergent_identity.py -- not trusted):

  PART 1  Run the parameterized bipartite model through the three components under OUR code.
  PART 2  Load model c's EXACT numerical 4x4 matrix and verify its specific claims
          (A = 2 ln(beta/alpha) = -0.575; real spectrum; min gap 0.70).

States (0-indexed): 0=(A0,B0) 1=(A1,B0) 2=(A1,B1) 3=(A0,B1); square cycle 0->1->2->3->0.
A flips A0<->A1 (edges 0-1 at B=0, 3-2 at B=1); B flips B0<->B1 (edges 0-3 at A=0, 1-2 at A=1).
Gating: forward A-rate x alpha when B=1; forward B-rate x beta when A=1.  =>  A_cycle = ln(beta/alpha).
Uncoupled (alpha=beta=1) the 4-cycle is a product of two reversible 2-state chains -> A=0 (Kolmogorov).

HONEST NOTE: in this allosteric construction the coupling IS the drive (the gating asymmetry
alpha/beta is what breaks detailed balance and must be powered). So the run-loop test has a single
knob (alpha=beta -> collapse), unlike emergent_identity.py's separable drive+coupling. That fusion
is itself physical -- in a molecular engine the coupling is the powered step.

Usage (from mpa-conform root):  python scripts/emergent_identity_n4.py
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

CYCLE = [(0, 1), (1, 2), (2, 3), (3, 0)]   # cw cycle 0->1->2->3->0


def bipartite_rates(alpha, beta, a_f=1.0, a_r=0.8, b_f=1.0, b_r=0.7, present=("01", "12", "23", "30")):
    """rates {(i,j): rate i->j} for the 4-state allosteric square; `present` selects edges (coupling)."""
    r = {}
    # A-flips: 0<->1 at B=0 ; 3<->2 at B=1 (forward A enhanced x alpha at B=1)
    if "01" in present:
        r[(0, 1)] = a_f;        r[(1, 0)] = a_r
    if "23" in present:                              # the 3<->2 A-flip at B=1
        r[(3, 2)] = a_f * alpha; r[(2, 3)] = a_r
    # B-flips: 0<->3 at A=0 ; 1<->2 at A=1 (forward B enhanced x beta at A=1)
    if "30" in present:
        r[(0, 3)] = b_f;        r[(3, 0)] = b_r
    if "12" in present:                              # the 1<->2 B-flip at A=1
        r[(1, 2)] = b_f * beta; r[(2, 1)] = b_r
    return r


def generator(rates, n=4):
    L = np.zeros((n, n))
    for (i, j), w in rates.items():
        L[j, i] += w
        L[i, i] -= w
    return L


def stationary(L):
    n = L.shape[0]
    A = np.vstack([L, np.ones(n)])
    b = np.zeros(n + 1); b[-1] = 1.0
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    return p


def cycle_affinity(rates):
    """A = ln(prod cw / prod ccw) around 0->1->2->3->0; 0 if the cycle is not closed."""
    cw = [(i, j) for (i, j) in CYCLE]
    ccw = [(j, i) for (i, j) in CYCLE]
    if not all(e in rates for e in cw + ccw):
        return 0.0
    pcw = np.prod([rates[e] for e in cw])
    pccw = np.prod([rates[e] for e in ccw])
    return float(np.log(pcw / pccw))


def cycle_current(rates):
    """net stationary current on edge 0->1."""
    if (0, 1) not in rates or (1, 0) not in rates:
        return 0.0
    p = stationary(generator(rates))
    return float(rates[(0, 1)] * p[0] - rates[(1, 0)] * p[1])


def affinity_from_matrix(L):
    """read rates off a column-generator (L[i,j]=rate j->i) and compute the 4-cycle affinity."""
    rates = {}
    for i in range(4):
        for j in range(4):
            if i != j and abs(L[i, j]) > 1e-12:
                rates[(j, i)] = L[i, j]
    return cycle_affinity(rates), rates


# ---------------------------------------------------------------- PART 1: parameterized model
def part1(alpha=2.0, beta=1.0):
    print("=" * 88)
    print("PART 1 -- parameterized 4-state bipartite allosteric model through OUR protocol")
    print(f"         (alpha={alpha}, beta={beta};  A_cycle should be ln(beta/alpha) = {np.log(beta/alpha):+.4f})")
    print("=" * 88)

    # MINTING: each subsystem alone is a 2-state chain (provably acyclic); coupled -> 4-cycle.
    rA = bipartite_rates(alpha, beta, present=("01",))      # A-subsystem alone (B frozen at 0): 0<->1
    rB = bipartite_rates(alpha, beta, present=("30",))      # B-subsystem alone (A frozen at 0): 0<->3
    r_uncoupled = bipartite_rates(1.0, 1.0)                 # full square, NO gating (alpha=beta=1)
    r_coupled = bipartite_rates(alpha, beta)               # full square WITH gating
    AA, AB = cycle_affinity(rA), cycle_affinity(rB)
    A_un, A_co = cycle_affinity(r_uncoupled), cycle_affinity(r_coupled)
    J_co = cycle_current(r_coupled)
    print("\n  [MINTING]")
    print(f"    subsystem A alone (2-state):        A = {AA:+.3e}  (no cycle, acyclic by dimension)")
    print(f"    subsystem B alone (2-state):        A = {AB:+.3e}")
    print(f"    full square, NO gating (a=b=1):     A = {A_un:+.3e}  (product of reversible chains)")
    print(f"    full square, gated (a={alpha},b={beta}): A = {A_co:+.4f}  current J = {J_co:+.4f}")
    minted = abs(AA) < 1e-9 and abs(AB) < 1e-9 and abs(A_un) < 1e-9 and abs(A_co) > 1e-6 and abs(J_co) > 1e-6
    print(f"    => minted ONLY by the gating coupling (parts AND ungated union carry no affinity): {minted}")

    # PROTECTION: A = ln(beta/alpha) depends only on the gating ratio; base-rate magnitudes cancel.
    print("\n  [PROTECTION]")
    rng = np.random.default_rng(0)
    A0 = cycle_affinity(r_coupled); s0 = np.sign(A0)
    flips = 0; maxdev = 0.0
    for _ in range(400):
        af, ar, bf, br = np.exp(2.0 * rng.standard_normal(4))      # huge symmetric base-rate swings
        Ad = cycle_affinity(bipartite_rates(alpha, beta, a_f=af, a_r=ar, b_f=bf, b_r=br))
        maxdev = max(maxdev, abs(Ad - A0)); flips += int(np.sign(Ad) != s0)
    A_rewire = cycle_affinity(bipartite_rates(beta, alpha))         # swap alpha<->beta = reverse gating
    print(f"    reciprocal base-rate deformations (n=400, amp=2): sign-flips = {flips}/400; "
          f"max|dA| = {maxdev:.2e}")
    print(f"    rewire (swap gating alpha<->beta): A = {A_rewire:+.4f} -> sign flips: {np.sign(A_rewire)!=s0}")
    protected = flips == 0 and maxdev < 1e-9 and (np.sign(A_rewire) != s0)
    print(f"    => sign(A)=sign(beta-alpha), reciprocal-invariant, flips only on rewire: {protected}")

    # SUSTAINED IDENTITY: coupling IS the drive here -> single knob. alpha=beta -> collapse.
    print("\n  [SUSTAINED IDENTITY]  (note: coupling = drive in this allosteric model)")
    J_gated = cycle_current(r_coupled)
    J_ungated = cycle_current(bipartite_rates(1.0, 1.0))
    J_severed = cycle_current(bipartite_rates(alpha, beta, present=("01", "23", "30")))  # drop 1<->2 edge
    print(f"    gated (a={alpha},b={beta}):           J = {J_gated:+.4f}   <- minted identity")
    print(f"    ungated (a=b=1, drive=coupling off):  J = {J_ungated:+.3e}   <- collapses (no latch)")
    print(f"    edge 1<->2 severed (square opened):   J = {J_severed:+.3e}   <- no cycle, bit gone")
    sustained = abs(J_gated) > 1e-6 and abs(J_ungated) < 1e-9 and abs(J_severed) < 1e-9
    print(f"    => run loop, nothing stored: {sustained}")

    return dict(AA=AA, AB=AB, A_un=A_un, A_co=A_co, J_co=J_co, flips=flips, maxdev=maxdev,
                A_rewire=A_rewire, minted=minted, protected=protected, sustained=sustained)


# ---------------------------------------------------------- PART 2: verify model c's exact matrix
def part2():
    print("\n" + "=" * 88)
    print("PART 2 -- verify model c's EXACT numerical matrix (check the work; claims A=-0.575, real, gap 0.70)")
    print("=" * 88)
    W = np.array([
        [-1.3853,  1.6487,  0.0000,  1.2840],
        [ 0.6065, -2.8169,  0.8560,  0.0000],
        [ 0.0000,  1.1682, -2.0691,  0.8244],
        [ 0.7788,  0.0000,  1.2131, -2.1084],
    ])
    colsums = W.sum(axis=0)
    A_mat, _ = affinity_from_matrix(W)
    eig = np.linalg.eigvals(W)
    real_spectrum = np.allclose(eig.imag, 0, atol=1e-9)
    nonzero = sorted(np.abs(eig.real[np.abs(eig.real) > 1e-9]))
    gap = nonzero[0] if nonzero else 0.0
    p = stationary(W)
    J = float(W[1, 0] * p[0] - W[0, 1] * p[1])   # net current on edge 0->1
    print(f"    column sums (should be ~0): {np.round(colsums, 4)}")
    print(f"    cycle affinity from THIS matrix: A = {A_mat:+.4f}   (model c claimed -0.575)")
    print(f"    spectrum real? {real_spectrum}   eigenvalues = {np.round(eig, 3)}")
    print(f"    min nonzero |Re(lambda)| (gap): {gap:.3f}   (model c claimed 0.70)")
    print(f"    stationary current on 0->1: J = {J:+.4f}")
    matches_A = np.isclose(A_mat, -0.575, atol=0.02)
    print(f"\n    => model c's stated A=-0.575 matches its own matrix: {matches_A}")
    if not matches_A:
        print(f"       CAUGHT: model c's explicit matrix gives A={A_mat:+.4f}, NOT its claimed -0.575"
              f" -- its numbers are internally inconsistent (mid-tier; do not trust the self-run verdict).")
    return dict(A_mat=A_mat, real_spectrum=real_spectrum, gap=gap, J=J, matches_A=matches_A)


def figure(p1):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), dpi=150)
    labels = ["A alone\n(2-state)", "B alone\n(2-state)", "union\nNO gating", "union\nGATED"]
    vals = [abs(p1["AA"]), abs(p1["AB"]), abs(p1["A_un"]), abs(p1["A_co"])]
    cols = ["#9e9e9e", "#9e9e9e", "#9e9e9e", "#2e7d32"]
    ax[0].bar(labels, vals, color=cols, edgecolor="black", lw=0.8)
    ax[0].set_ylabel(r"cycle affinity $|\mathcal{A}|$ (nats)")
    ax[0].set_title("MINTING (genuine independent parts)\ntwo acyclic 2-state systems + ungated union: "
                    r"$\mathcal{A}=0$;" "\ngating mints the 4-cycle")
    ax[0].grid(alpha=0.3, axis="y")

    ax[1].axhline(p1["A_co"], color="#1565c0", lw=2.0, label=r"$\mathcal{A}$ under recip. base-rate deform.")
    ax[1].scatter(np.arange(40), np.full(40, p1["A_co"]) + 1e-3 * np.random.default_rng(2).standard_normal(40),
                  s=9, color="#1565c0", alpha=0.5)
    ax[1].axhline(p1["A_rewire"], color="#c62828", lw=2.0, ls="--", label="rewire (swap gating): flips")
    ax[1].axhline(0, color="gray", lw=0.8)
    ax[1].set_ylabel(r"cycle affinity $\mathcal{A}$ (nats)")
    ax[1].set_title(f"PROTECTION\nrecip. deform. n=400: {p1['flips']}/400 flips, "
                    f"max|ΔA|={p1['maxdev']:.0e}\nsign set by gating asymmetry only")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3, axis="y")

    fig.suptitle("4-state bipartite allosteric composite — coupling (gating) mints a protected cycle "
                 "from two acyclic parts", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    path = OUT / "emergent_identity_n4.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


def main():
    print("EMERGENT IDENTITY (N=4) -- the channel's best concrete lead, checked through OUR protocol\n")
    p1 = part1()
    p2 = part2()
    figure(p1)
    print("\n" + "=" * 88)
    print("VERDICT")
    print("=" * 88)
    three = p1["minted"] and p1["protected"] and p1["sustained"]
    print(f"  Three legal components on the 4-state bipartite model: minted={p1['minted']} "
          f"protected={p1['protected']} sustained={p1['sustained']}  -> {'ALL PASS' if three else 'NOT all'}")
    print(f"  This is a STRONGER minting than emergent_identity.py: the two parts are genuinely")
    print(f"  independent 2-state systems (acyclic by dimension), and the cycle is minted by GATING")
    print(f"  -- the mechanism real molecular engines use -- not by a hand-drawn closing edge.")
    print(f"\n  model c's specific matrix: its stated affinity matches its matrix = {p2['matches_A']}.")
    print(f"  ==> 'GATE DISCHARGED' (model c) is REJECTED: this is still a SYNTHETIC construction")
    print(f"      (alpha/beta hand-set); calibration, not a real measured substrate. The real")
    print(f"      discharge needs a measured rate matrix (the DNA strand-displacement / kinetic-")
    print(f"      proofreading / allosteric-enzyme leads), instanced through THIS protocol.")


if __name__ == "__main__":
    main()
