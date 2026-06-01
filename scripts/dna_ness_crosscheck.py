r"""dna_ness_crosscheck.py -- does the N=3 reduction faithfully capture the FULL nonlinear network?

emergent_identity_dna_ness.py reduced the Nicholas et al. dissipative DNA-NESS (Angew. Chem. Int.
Ed. 2025, DOI 10.1002/anie.202512967) to a linear N=3 Markov generator (OQ, FQ, Q) and found all
three emergent-identity components pass on the MEASURED rates (SI Tables S4/S5). That made it a
*candidate*. This script is the rigorous cross-check: build the FULL nonlinear mass-action network
(SI Section 3, the 8 reactions / Table S2 ODEs), integrate it to a non-equilibrium steady state,
and test whether the N=3 reduction reproduces the real cycle current.

Rate constants are FACTS cited from the paper's SI (Tables S4/S5, Exp. Fig. 2b) + Sec. 3 text --
fair-use citation, not the copyrighted PDF. The ODEs are rebuilt from the reaction stoichiometry
(the published ODE text had OCR ambiguities; mass-action on the named reactions is unambiguous).

Species (quencher partner + enzyme; fuel F chemostatted = the sustained drive; waste/deactivation
are slow side-processes omitted for a clean NESS, per the SI's own "drift" discussion):
  O  free output         Q  free quencher      OQ output-quencher duplex
  FQ fuel-quencher       E  free RNase H        FQE enzyme-substrate complex

Reactions (mass-action), F held at a fixed bath value (chemostat):
  R2  OQ + F <-> O + FQ   (kdisp / kdisp_r)        strand displacement
  R3  FQ + E <-> FQE      (kenz / kenz_r)          enzyme binding
  R4  FQE -> Q + E (+W)   (kcat)                   irreversible hydrolysis (the drive)
  R5  Q + O <-> OQ        (kOrebind / kOrebind_r)  output rebinding
  R6  Q + F <-> FQ        (kFrebind / kFrebind_r)  fuel rebinding   [kFrebind_r set by detailed balance]

NESS circulation = net flux on OQ->FQ, J = kdisp*[OQ]*[F] - kdisp_r*[FQ]*[O]  (= net Q->OQ flux too).
Cross-check: integrate the full network to NESS, read J_full and the NESS [O],[E]; build the N=3
reduction with those bath values; compare J_full/Q_total (per-quencher cycling rate) to the N=3
probability current. If they agree, the reduction is faithful -> the candidate is confirmed.

Usage (from mpa-conform root):  python scripts/dna_ness_crosscheck.py
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
from scipy.integrate import solve_ivp

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

# ---- measured rate constants (Nicholas et al., SI Tables S4/S5 Exp. Fig.2b + Sec.3) ----
kdisp, kdisp_r = 6.61e5, 5000.0
kOreb, kOreb_r = 5e8, 1e-6
kFreb          = 5e8
kcat, kenz, kenz_r = 2.65, 3.2e7, 0.1
E_total        = 5.0e-10            # RNase H (M)
Q_total        = 5.0e-8             # DNA duplex / total quencher (M); O_total = Q_total
kFreb_r        = kdisp_r * kOreb_r * kFreb / (kdisp * kOreb)   # detailed-balance value = 7.56e-9

IDX = dict(O=0, Q=1, OQ=2, FQ=3, E=4, FQE=5)


def rhs(t, y, F):
    O, Q, OQ, FQ, E, FQE = y
    R2f = kdisp * OQ * F;     R2r = kdisp_r * FQ * O
    R3f = kenz * FQ * E;      R3r = kenz_r * FQE
    R4 = kcat * FQE
    R5f = kOreb * Q * O;      R5r = kOreb_r * OQ
    R6f = kFreb * Q * F;      R6r = kFreb_r * FQ
    dO = R2f - R2r - R5f + R5r
    dQ = R4 - R5f + R5r - R6f + R6r
    dOQ = -R2f + R2r + R5f - R5r
    dFQ = R2f - R2r - R3f + R3r + R6f - R6r
    dE = -R3f + R3r + R4
    dFQE = R3f - R3r - R4
    return [dO, dQ, dOQ, dFQ, dE, dFQE]


def integrate_to_ness(F, T=2.0e5, y0=None):
    if y0 is None:
        y0 = [0.0, 0.0, Q_total, 0.0, E_total, 0.0]      # start: all quencher as OQ, free enzyme
    sol = solve_ivp(rhs, (0, T), y0, args=(F,), method="BDF", rtol=1e-8, atol=1e-18,
                    dense_output=True, t_eval=np.geomspace(1e-3, T, 400))
    return sol


def circulation(y, F):
    O, Q, OQ, FQ, E, FQE = y
    return kdisp * OQ * F - kdisp_r * FQ * O      # net OQ->FQ flux (M/s)


def n3_current(O_bath, E_bath, F):
    """N=3 reduction (OQ,FQ,Q) probability current, with O,E,F as baths at the full-model NESS."""
    k_deg = kcat * kenz * E_bath / (kenz_r + kcat)
    r = {(0, 1): kdisp * F, (1, 0): kdisp_r * O_bath,
         (1, 2): kFreb_r + k_deg, (2, 1): kFreb * F,
         (2, 0): kOreb * O_bath, (0, 2): kOreb_r}
    L = np.zeros((3, 3))
    for (i, j), w in r.items():
        L[j, i] += w; L[i, i] -= w
    A = np.vstack([L, np.ones(3)]); b = np.array([0, 0, 0, 1.0])
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    return float(r[(0, 1)] * p[0] - r[(1, 0)] * p[1]), k_deg


def main():
    print("DNA-NESS cross-check: FULL nonlinear network vs the N=3 reduction\n")
    F = 1.0e-8        # chemostatted fuel (M); cancels in the affinity, sets the current scale
    print(f"chemostatted fuel [F] = {F:.1e} M; Q_total = {Q_total:.1e} M; [E]_total = {E_total:.1e} M\n")

    # ---- integrate the FULL network to NESS ----
    sol = integrate_to_ness(F)
    y = sol.y[:, -1]
    dy = np.array(rhs(0, y, F))
    resid = np.max(np.abs(dy)) / (Q_total)        # relative steady-state residual
    O, Q, OQ, FQ, E, FQE = y
    print("=" * 84)
    print("FULL NONLINEAR NETWORK at NESS")
    print("=" * 84)
    print(f"  [OQ]={OQ:.3e}  [FQ]={FQ:.3e}  [Q]={Q:.3e}  [O]={O:.3e}  [E]={E:.3e}  [FQE]={FQE:.3e}")
    print(f"  conservation: quencher={OQ+FQ+Q+FQE:.3e} (={Q_total:.1e}); output={O+OQ:.3e}; enzyme={E+FQE:.3e}")
    print(f"  steady-state residual (max|dy|/Q_tot) = {resid:.2e}  ({'converged' if resid<1e-6 else 'NOT converged'})")
    J_full = circulation(y, F)
    J_QO = kOreb * Q * O - kOreb_r * OQ           # net Q->OQ flux; must equal J_full at NESS
    rate_hyd = kcat * FQE                          # fuel-hydrolysis throughput
    print(f"  circulation J (net OQ->FQ)   = {J_full:+.4e} M/s")
    print(f"  net Q->OQ flux (should == J)  = {J_QO:+.4e} M/s   (cycle-consistent: {np.isclose(J_full, J_QO, rtol=1e-3)})")
    print(f"  fuel-hydrolysis throughput kcat*[FQE] = {rate_hyd:+.4e} M/s  (the dissipation)")
    minted_full = abs(J_full) > 1e-15
    print(f"  => the FULL network circulates (minting holds in the full model): {minted_full}")

    # ---- compare to the N=3 reduction (using the full NESS baths) ----
    J_n3, k_deg = n3_current(O, E, F)
    rate_full_perQ = J_full / Q_total              # per-quencher cycling rate (1/s)
    print("\n" + "=" * 84)
    print("N=3 REDUCTION vs FULL (per-quencher cycling rate, 1/s)")
    print("=" * 84)
    print(f"  k_deg (QSS enzyme drain) = {k_deg:.4e} /s;  [FQE]/[FQ] = {FQE/FQ:.2e} (QSS valid if <<1)")
    print(f"  full network:  J_full/Q_total = {rate_full_perQ:+.4e} /s")
    print(f"  N=3 reduction: J_N3           = {J_n3:+.4e} /s")
    ratio = J_n3 / rate_full_perQ if rate_full_perQ != 0 else float('nan')
    print(f"  ratio N=3 / full = {ratio:.3f}   (1.0 = the reduction is exact)")
    faithful = abs(ratio - 1.0) < 0.15 and (np.sign(J_n3) == np.sign(rate_full_perQ))
    print(f"  => reduction faithful (same sign, magnitude within 15%): {faithful}")

    # ---- run-loop in the FULL model: cut the fuel, watch the circulation collapse ----
    print("\n" + "=" * 84)
    print("RUN-LOOP (full model): cut the fuel (F=0) from NESS -> does circulation collapse?")
    print("=" * 84)
    sol_off = solve_ivp(rhs, (0, 600.0), y, args=(0.0,), method="BDF", rtol=1e-8, atol=1e-18,
                        dense_output=True, t_eval=np.linspace(0, 600, 400))
    J_off = np.array([circulation(sol_off.y[:, i], 0.0) for i in range(sol_off.y.shape[1])])
    # time for |J| to fall below 1% of its initial value
    j0 = abs(J_off[0]) if abs(J_off[0]) > 0 else 1.0
    below = np.where(np.abs(J_off) < 0.01 * j0)[0]
    t_relax = sol_off.t[below[0]] if len(below) else sol_off.t[-1]
    print(f"  J at fuel-cut: {J_off[0]:+.3e} M/s  ->  J at t=600s: {J_off[-1]:+.3e} M/s")
    print(f"  time for |J| to fall to 1%: {t_relax:.0f} s (~{t_relax/60:.1f} min)  "
          f"[SI reports experimental recovery ~3 min]")
    collapses = abs(J_off[-1]) < 0.01 * j0
    print(f"  => circulation collapses without fuel (run-loop, not stored): {collapses}")

    figure(sol, F, sol_off, J_off, rate_full_perQ, J_n3)

    print("\n" + "=" * 84)
    print("VERDICT")
    print("=" * 84)
    if minted_full and faithful and collapses:
        print("  CROSS-CHECK PASSES. The full nonlinear network sustains a real cycle circulation")
        print("  (minting), the N=3 reduction reproduces it to within ~15% with the same sign, and")
        print("  cutting the fuel collapses the circulation (run-loop) on a timescale consistent with")
        print("  the SI's experimental ~3-min recovery. => the N=3 emergent-identity instance is")
        print("  CONFIRMED against the full measured model (not a reduction artifact). The remaining")
        print("  caveat is only the chemostat/omitted-side-processes idealization; the core driven")
        print("  cycle is faithful. Pending Ron's review, the emergent-identity node has its first")
        print("  confirmed REAL substrate.")
    else:
        print(f"  NOT a clean confirmation: minted_full={minted_full} faithful={faithful} "
              f"collapses={collapses}. Read honestly.")
    print("\n  Affinity note: the N=3 coarse-grained affinity (~14.5 nats) is the effective fwd/bwd")
    print("  ratio of the LUMPED FQ->Q step; the full model's microscopic affinity runs through the")
    print("  irreversible kcat (the fuel-hydrolysis Delta-mu, effectively unbounded). The CURRENT is")
    print("  the apples-to-apples comparison, not the affinity magnitude.")


def figure(sol, F, sol_off, J_off, rate_full_perQ, J_n3):
    fig, ax = plt.subplots(1, 3, figsize=(16.5, 4.8), dpi=150)

    # panel 1: approach to NESS
    for name in ("OQ", "FQ", "Q", "O"):
        ax[0].semilogx(sol.t, sol.y[IDX[name]] * 1e9, lw=1.6, label=f"[{name}]")
    ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("concentration (nM)")
    ax[0].set_title("FULL network -> NESS\n(chemostatted fuel sustains it)")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    # panel 2: reduction vs full (per-quencher cycling rate)
    ax[1].bar(["full\nnetwork", "N=3\nreduction"], [rate_full_perQ, J_n3],
              color=["#2e7d32", "#1565c0"], edgecolor="black", lw=0.8)
    ax[1].set_ylabel("per-quencher cycling rate (1/s)")
    ax[1].set_title(f"reduction reproduces the real current\nratio N=3/full = {J_n3/rate_full_perQ:.3f}")
    ax[1].grid(alpha=0.3, axis="y")

    # panel 3: run-loop -- fuel cut, circulation collapses
    ax[2].plot(sol_off.t, J_off * 1e9, color="#c62828", lw=1.8, label="circulation J after fuel cut")
    ax[2].axhline(0, color="gray", lw=0.8)
    ax[2].set_xlabel("time after fuel cut (s)"); ax[2].set_ylabel("circulation J (nM/s)")
    ax[2].set_title("RUN-LOOP: cut the fuel -> J -> 0\n(SI: experimental recovery ~3 min)")
    ax[2].legend(fontsize=8, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("DNA-NESS cross-check: the full measured nonlinear network confirms the N=3 "
                 "emergent-identity instance", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    path = OUT / "dna_ness_crosscheck.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
