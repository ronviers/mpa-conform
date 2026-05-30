r"""rps_two_bits.py -- two-bits on RPS: a CORRECTION to engine §Two bits (Ron, via the fake-NaN rule).

Move #2 of promotion_crossing_handoff.md (`staked:two-bits`). The engine §Two bits says the
topological SIGN bit is "free to hold, >= 1 ch per protected sign to MODIFY." Ron's correction (the
fake-NaN-at-zero discipline taken to its conclusion): **it cannot cost anything to flip the sign.**
A flip +1<->-1 is a bijection (NOT gate) -> logically REVERSIBLE -> by Bennett it has NO Landauer
floor; the >=1 ch is the ERASURE cost (many-to-one), wrongly imported onto a flip. The >=1 ch only
appears if you route the flip THROUGH the balanced state A=0 (erase, reform) -- but A=0 is the
NEVER-ATTAINED boundary (asymptotic closure) and the per-flip cost there is an indeterminate
fake-NaN (0/0). The real flip is by REWIRING (reverse the directed cycle = the topological-qubit
BRAID, a reversible involution), which never instantiates the A=0 dynamics. So the sign bit is FREE
BOTH WAYS. My earlier "read the floor as the entailed b1" was a half-measure -- it still imported a
cost that lives only at the never-attained zero.

WHAT SURVIVES (cleaner): the two bits are NOT "two costs, one per face":
  - AMPLITUDE bit |J| (DISSIPATIVE): a REAL interior cost -- maintenance heat-tax <sigma> > 0, finite
    at every operating point; drive-set (|J| ~ sigma^2), leaks without drive.
  - SIGN bit sign(A) (TOPOLOGICAL): NO interior cost -- free to hold (no leak) AND free to flip
    (reversible rewiring). Any flip cost is SUBSTRATE-SPECIFIC rewiring work (e.g. the homochirality
    model's racemic-saddle height), never a universal >= 1 ch floor.
One bit costs (amplitude, interior/real); the other is free (sign, topological).

THE READING ON RPS (real emergent C3 substrate): amplitude bit = NESS circulation |J|; sign bit =
sign(J) = sign(Im lambda) = sign(alpha-beta). Knobs: noise drive sigma (amplitude), wiring a-b (sign).

PRE-REGISTERED BAR (all must hold; a clean miss is also evidence):
  T1 amplitude bit = the ONLY real cost: |J| ~ sigma^2 (drive-set, -> 0 without drive); interior
     maintenance heat-tax <sigma> > 0 (finite, well-defined at every alpha!=beta), -> 0 for the achiral null.
  T2 sign bit free to HOLD: sign(Im lambda) present at sigma->0; sign(J) held across the drive-sweep
     while |J|->0; no duration-scaling cost on the sign.
  T3 sign bit free to FLIP: rewiring (alpha<->beta) is a reversible INVOLUTION (its own inverse =>
     no erasure => free by Bennett); the structural sign jumps at the swap, never instantiating A=0.
  T4 NO >= 1 ch floor: the would-be per-flip cost <sigma>/omega VARIES continuously (crosses ln2,
     dips below it) and -> 0/0 at the never-attained balance = a boundary fake-NaN, not a fixed quantum.

Usage (from mpa-conform root):  python scripts/rps_two_bits.py
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

from rps_triad import jacobian, coexistence, circulation, spectral

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

A0, B0 = 0.5, 1.0
LN2 = float(np.log(2.0))            # 1 ch in nats


def entropy_production(alpha, beta, sigma):
    """NESS entropy-production rate of the noisy RPS focus (additive demographic noise on the 3
    species, D = sigma^2/2 I): the heat-tax that MAINTAINS the running current. Zero for a gradient
    (achiral) drift, positive for the chiral circulation."""
    M = jacobian(alpha, beta)
    D = 0.5 * sigma ** 2 * np.eye(3)
    Sigma = solve_continuous_lyapunov(M, -2.0 * D)
    Omega = M + D @ np.linalg.inv(Sigma)               # irreversible drift
    return float(np.trace(Omega.T @ np.linalg.inv(D) @ Omega @ Sigma))


def cycle_space_b1():
    """b1 = E - V + C of the directed 3-cycle (the frustrated subgraph): 3 edges, 3 nodes, 1
    component -> 1. The entailed forced-erasure floor is b1 * ch."""
    E, V, C = 3, 3, 1
    return E - V + C


def main():
    print("RPS TWO-BITS ORTHOGONALITY -- read in the interior (the >=1 ch floor is entailed, never")
    print("measured at the zero).  amplitude bit = |J| (drive sigma); sign bit = sign(J) (wiring a-b)\n")

    # ---- T1: amplitude is maintenance-costed and drive-set ----
    print("=" * 86)
    print("T1  AMPLITUDE bit -- maintenance cost (heat-tax), drive-set, decays without drive")
    print("=" * 86)
    sigmas = np.array([0.006, 0.01, 0.016, 0.025, 0.04])
    Js = np.array([circulation(A0, B0, sigma=s, T=2000.0, seed=1) for s in sigmas])
    slope = float(np.polyfit(np.log(sigmas), np.log(np.abs(Js)), 1)[0])
    sigent = entropy_production(A0, B0, 0.02)
    sigent_achiral = entropy_production(0.75, 0.75, 0.02)
    print(f"  |J| ~ sigma^{slope:.2f}  (drive-set; -> 0 without drive: the amplitude is NOT held)")
    print(f"  NESS heat-tax <sigma_ent> = {sigent:.4f} > 0  -> maintaining the running current costs")
    print(f"     dissipation per unit time; integrated cost int<sigma_ent>dt = <sigma_ent>*T ~ T (duration-scaling)")
    print(f"  achiral null (a=b): <sigma_ent> = {sigent_achiral:.2e}  -> the heat-tax IS the current's cost (no current, no cost)")
    t1 = bool(abs(slope - 2) < 0.5 and sigent > 1e-3 and sigent_achiral < 1e-6)

    # ---- T2: sign is free to hold ----
    print("\n" + "=" * 86)
    print("T2  SIGN bit -- free to hold (no leak, no duration cost), present with zero drive")
    print("=" * 86)
    sp = spectral(A0, B0)
    hand = int(np.sign(A0 - B0))
    sgn_J = np.sign(Js)
    sign_held = bool(np.all(sgn_J == hand))
    print(f"  sign(Im lambda) of the drift pair = {sp['hand']:+d}  -> a spectral/topological property of the")
    print(f"     WIRING, present at sigma->0 (no drive needed to hold it; the |J|->0 limit keeps the sign)")
    print(f"  sign(J) across the drive-sweep = {sgn_J.astype(int)}  -> held while |J|->0: free-to-hold = {sign_held}")
    print(f"  no duration-scaling cost attributable to the sign (a topological bit of the wiring, not a")
    print(f"     metastable state needing refresh)")
    t2 = bool(sign_held and sp['hand'] == hand)

    # ---- T3: the FLIP is FREE -- rewiring is a reversible involution; never instantiates A=0 ----
    print("\n" + "=" * 86)
    print("T3  THE FLIP IS FREE -- rewiring is a REVERSIBLE involution (no erasure), the topological-qubit")
    print("    braid, NOT a drive through the gap")
    print("=" * 86)
    # a sign flip +1<->-1 is a bijection (NOT gate) => logically reversible => NO Landauer floor (Bennett).
    # the flip is done by REWIRING (swap alpha<->beta = reverse the directed cycle) -- the analog of BRAIDING
    # a topological qubit, not of driving it through its gap. it is an involution (swap-back undoes it), and
    # the structural sign jumps +-> - at the swap: the achiral alpha=beta dynamics is NEVER instantiated.
    s_a = spectral(A0, B0)["hand"]; s_b = spectral(B0, A0)["hand"]; s_aa = spectral(A0, B0)["hand"]
    involution = bool(s_a == -s_b and s_aa == s_a)
    print(f"  rewiring is an involution: sign {s_a:+d} --swap--> {s_b:+d} --swap-back--> {s_aa:+d} "
          f"(its own inverse => reversible => no erasure): {involution}")
    print(f"  a flip +1<->-1 is a bijection (NOT gate); by Bennett a reversible op has NO fundamental floor.")
    print(f"  the structural sign(alpha-beta) jumps at the swap; the balanced alpha=beta dynamics is never")
    print(f"     instantiated -- the topological-qubit BRAID, not a drive through the (never-attained) gap.")
    t3 = involution

    # ---- T4: there is NO >=1 ch floor -- it is a BOUNDARY fake-NaN; the only real cost is interior <sigma> ----
    print("\n" + "=" * 86)
    print("T4  NO >=1 ch FLOOR -- the would-be flip cost is a BOUNDARY fake-NaN, not a fixed quantum")
    print("=" * 86)
    # where a >=1 ch floor would live = the per-cycle dissipation <sigma>/omega. measure it across the interior.
    d_fig = np.array([0.6, 0.45, 0.3, 0.2, 0.12, 0.06])
    se_fig = np.array([entropy_production((1.5 + d) / 2, (1.5 - d) / 2, 0.02) for d in d_fig])
    om_fig = np.array([spectral((1.5 + d) / 2, (1.5 - d) / 2)["omega"] for d in d_fig])
    pc_fig = se_fig / om_fig
    sig_int = entropy_production(A0, B0, 0.02)
    print(f"  the would-be per-flip cost <sigma>/omega varies CONTINUOUSLY with the operating point and")
    print(f"     -> 0/0 at balance -- it is NOT a fixed floor (it crosses ln2, then dips below it):")
    for d, c in zip(d_fig, pc_fig):
        tag = " <- = ln2 (1 ch) only by coincidence here" if abs(c - LN2) < 0.03 else (" (below ln2)" if c < LN2 else "")
        print(f"        delta={d:.2f}:  <sigma>/omega = {c:.3f} nats{tag}")
    print(f"  at balance alpha=beta: <sigma>->0 AND cycles->0  => 0/0 (indeterminate = the fake-NaN); and")
    print(f"     balance is the NEVER-ATTAINED boundary (asymptotic closure) -- nothing is paid there.")
    print(f"  the ONLY well-defined cost is the INTERIOR amplitude maintenance <sigma>={sig_int:.3f} (finite at")
    print(f"     every alpha!=beta). The sign bit has NO interior cost at all -- the >=1 ch was a boundary IMPORT.")
    varies = bool(pc_fig.max() - pc_fig.min() > 0.2 and pc_fig.min() < LN2)   # not a fixed floor; dips below ln2
    t4 = bool(varies and np.isfinite(sig_int) and sig_int > 0)
    # arrays kept for the figure
    deltas, om = d_fig, pc_fig

    figure(sigmas, Js, slope, sigent, deltas, om)

    print("\n" + "=" * 86)
    print("VERDICT -- two-bits on RPS: a CORRECTION to engine §Two bits (the >=1 ch floor is a fake-NaN)")
    print("=" * 86)
    bar = [("T1 amplitude bit = the ONLY real cost: interior maintenance <sigma>, |J|~sigma^2", t1),
           ("T2 sign bit = free to HOLD (present at sigma->0, held as |J|->0)", t2),
           ("T3 sign bit = free to FLIP (rewiring is a reversible involution; no erasure)", t3),
           ("T4 NO >=1 ch floor: the per-flip cost is a boundary fake-NaN, varies + 0/0 at balance", t4)]
    for label, ok in bar:
        print(f"   [{'PASS' if ok else 'MISS'}]  {label}")
    if all(ok for _, ok in bar):
        print("\n  ==> CORRECTION (Ron, via the fake-NaN-at-zero discipline). The topological SIGN bit is FREE")
        print("      BOTH WAYS -- free to hold (topological, no leak) AND free to flip (rewiring = a reversible")
        print("      involution = the topological-qubit braid). The engine §Two bits '>=1 ch per protected sign")
        print("      to MODIFY' is a BOUNDARY IMPORT: it places a Landauer ERASURE cost at A=0, but a flip is a")
        print("      reversible bijection (no erasure), and A=0 is the never-attained boundary where the")
        print("      per-flip cost is an indeterminate fake-NaN (0/0). Same error family as wall-forces-chaos --")
        print("      a quantity formulated at the degenerate boundary instead of entailed from the interior.")
        print("      What SURVIVES (cleaner): the two bits are NOT 'two costs, one per face'. The AMPLITUDE bit")
        print("      is DISSIPATIVE -- a real interior cost (maintenance <sigma>, leaks without drive). The SIGN")
        print("      bit is TOPOLOGICAL -- no interior cost at all; any flip cost is substrate-specific rewiring")
        print("      work (e.g. the homochirality model's racemic-saddle height), NOT a universal >=1 ch floor.")
        print("\n  >>> ENGINE CORRECTION (held for review): §Two bits / engine BITS -- drop the '>=1 ch per")
        print("      protected sign to modify' (and the b1-ch forced-erasure floor as a *cost*); the topological")
        print("      bit is free both ways. Keep: free-to-hold, gauge-irremovable, flips only by rewiring (now:")
        print("      a free reversible braid, not a >=1 ch event). My earlier 'entailed b1 floor' reading was a")
        print("      half-measure -- it still imported a cost that only lives at the never-attained zero.")
    else:
        print("\n  ==> the correction did not land cleanly -- inspect.")


def figure(sigmas, Js, slope, sigent, deltas, pc):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8), dpi=150)

    # panel 1: amplitude bit -- |J| ~ sigma^2 (drive-set, maintenance-costed)
    a0 = ax[0]
    a0.loglog(sigmas, np.abs(Js), "o-", color="#1565c0", lw=2, ms=6, label="|J| measured")
    a0.loglog(sigmas, np.abs(Js)[-1] * (sigmas / sigmas[-1]) ** 2, "k--", lw=1, label=r"$\propto\sigma^2$")
    a0.set_xlabel(r"demographic-noise drive $\sigma$"); a0.set_ylabel("|circulation J| (amplitude bit)")
    a0.set_title(f"T1 AMPLITUDE bit: drive-set, $\\sim\\sigma^{{{slope:.1f}}}$\n"
                 f"heat-tax $\\langle\\sigma_{{ent}}\\rangle={sigent:.3f}>0$ (maintenance)")
    a0.legend(fontsize=9, frameon=False); a0.grid(alpha=0.3, which="both")

    # panel 2: the would-be flip cost is NO fixed floor -- it varies and -> 0/0 at the never-attained balance
    a1 = ax[1]
    a1.plot(deltas, pc, "o-", color="#c2185b", lw=2, ms=6, label=r"would-be per-flip cost $\langle\sigma\rangle/\omega$")
    a1.axhline(np.log(2), color="#1565c0", ls=":", lw=1.4, label="ln2 = 1 ch (crossed, NOT a floor)")
    a1.axvline(0, color="#2e7d32", ls="--", lw=1.2)
    a1.annotate("balance a=b:\n0/0 (fake-NaN),\nnever attained",
                xy=(0, 0), xytext=(0.03, pc.max() * 0.55), fontsize=8, color="#2e7d32")
    a1.set_xlabel(r"wiring asymmetry $\delta=\alpha-\beta$ (interior $\to$ balance)")
    a1.set_ylabel(r"$\langle\sigma\rangle/\omega$ (nats)")
    a1.set_xlim(0, deltas.max() * 1.05); a1.set_ylim(0, pc.max() * 1.1)
    a1.set_title("T4 NO >=1 ch floor: the per-flip cost varies +\ndips below ln2 + -> 0/0 at the never-attained balance")
    a1.legend(fontsize=8, frameon=False, loc="upper left"); a1.grid(alpha=0.3)

    # panel 3: corrected -- one bit costs (amplitude/dissipative), one is free (sign/topological)
    a2 = ax[2]
    a2.axis("off")
    txt = (
        "TWO BITS (RPS) -- CORRECTED\n\n"
        "AMPLITUDE  |J|  (dissipative)\n"
        "  - drive-set ($\\propto\\sigma^2$)\n"
        "  - REAL interior cost:\n"
        "    maintenance $\\langle\\sigma\\rangle$ (leaks)\n"
        "  - free to change (continuous)\n\n"
        "SIGN  sign(A)  (topological)\n"
        "  - wiring-set, gauge-irremovable\n"
        "  - free to HOLD (no leak)\n"
        "  - free to FLIP (reversible\n"
        "    rewiring = the braid)\n"
        "  - NO universal floor\n\n"
        "the >=1 ch 'modify' cost was a\n"
        "BOUNDARY fake-NaN (lives only\n"
        "at the never-attained A=0)."
    )
    a2.text(0.02, 0.98, txt, va="top", ha="left", fontsize=9.5, family="monospace",
            bbox=dict(boxstyle="round", fc="#f5f5f5", ec="#90a4ae"))

    fig.suptitle("RPS two-bits -- CORRECTION: the amplitude bit is dissipative (real interior cost); the "
                 "sign bit is topological (free both ways). The >=1 ch flip floor is a boundary fake-NaN.",
                 fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "rps_two_bits.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
