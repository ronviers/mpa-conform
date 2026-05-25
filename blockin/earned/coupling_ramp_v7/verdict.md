# verdict — coupling_ramp_v7  (DEV/blind)  →  **MATCH** (metric-blur core clean; honest headroom residue)

Orchestrator grading record (holds the seal). The examinee's reading is in
[`RESULT.md`](RESULT.md); this file is the unseal comparison + the anchor check + the residue.

The probe: v6's MATCHED (reciprocal, symmetric-coupled, Cat-1) community with its coupling
strength g_s dialed UP across five levels toward the stability threshold g_s→γ=1
(g_s=[0.3,0.6,0.8,0.9,0.95]). A **metric-axis** sweep — the companion to v6's discrete-axis
result — asking whether Cat-1 SMEARS along a continuous control axis. Traversed as five
independent single-point placements + a band readout (sweep contract, §6).

---

## unseal: blind reading vs sealed truth

| claim | sealed truth | blind answerer read | |
|---|---|---|---|
| kind, every level | reversible Cat-1 relaxation (real spectrum, ⟨σ⟩=0, X=1) | "settling, single-exp C, no negative lobe, Cxy=Cyx, linear FDR" — all 5 | ✅ |
| oscillation onset? | NONE (symmetric coupling → real spectrum at every g_s) | "no negative C lobe at any level → not oscillation" | ✅ (cage_edge 1 avoided) |
| current onset? | NONE (detailed balance, Cxy=Cyx, drift≈0 every level) | "Cxy=Cyx to 1e-6, phiMean bounded wander → no current" | ✅ (cage_edge 2 avoided) |
| aging (X<1)? | NO — FDR locus affine (X=1) at every level; the slope grows with susceptibility, not X | "FDR linear (rms<0.006); slope≈chi_inf≈tauC, 3 readings agree → equilibrium" — read the growing slope as growing susceptibility, NOT aging | ✅ (cage_edge 3 avoided — the subtle one) |
| the band | tau_slow diverges 1.43→20 (critical slowing) + susceptibility D/gap diverges; KIND invariant | "tauC ~doubles per step 1.3→20; chi_inf ~doubles; kind stays put" | ✅ |
| does the kind change? | NO — same reversible relaxation all the way, only magnitude changes | "No — same kind all the way up, just more so (quantitative not qualitative)" | ✅ |
| near an edge / how close? | YES, approaching a stability/critical edge; headroom = spectral gap, shrinking 0.70→0.05, close-but-not-at-edge at level 4 | "interior at all 5, monotone trend heading toward an instability; **absolute distance in knob units NOT readable** (no magnitudes in data)" | ◑ partial — direction+rate grounded, absolute native-unit distance parked |
| already unstable? | NO — all sampled g_s<γ stable | "no finite-time blow-up; every level settles" | ✅ (cage_edge 5 avoided) |
| category smear? | NONE — Cat-1 sharp along the metric axis | placed all 5 as the same kind | ✅ |

**No hollow MATCH:** every claim carries a column/step. **No KILL:** no NaN, no false
ground-truth current/oscillation, FDR cross-checks agree, no X>1. **Parks are all
collapsed-axis / viewport-dial** (a 6th stronger setting; absolute distance-to-edge in knob
units; the exact scaling law; researcher preference). Slice symmetry (§4) clean — the
no-current content (flat winding) was IN the data, not withheld.

## anchor-and-assert (orchestrator-side; level 1 = v6 community 0, not disclosed)

| quantity | v6 matched community | v7 level-1 blind read | |
|---|---|---|---|
| relaxation time | τ_slow=2.5 (eig -0.4) | tauC=2.44 | ✅ |
| FDR slope | 1.564 (seal) | 1.56 | ✅ |
| cross-corr | Cxy=Cyx (symmetric) | Cxy=Cyx to 1e-6 | ✅ |
| current | none (drift≈0) | bounded wander, no ramp | ✅ |

Level 1 reproduces v6's matched-community placement — no cross-pass drift; the answerer did
not know level 1 was an anchor.

## the finding (metric-blur + the sharpened two-sided-headroom)

1. **Metric-boundary blur — answered for the Cat-1 side: NO smear.** v6 showed the 1↔10
   (reciprocity) cut is *topologically* sharp. v7 shows a CONTINUOUS (metric) axis — coupling
   strength — also does not smear Cat-1: cranking g_s toward the stability edge changes only
   the magnitude (the relaxation timescale diverges, the susceptibility grows), never the KIND
   (no oscillation, no current, X=1 throughout). The category is sharp along the metric axis;
   what moves is the operating point, toward a critical/instability EDGE via **critical
   slowing** (a reversible, X=1 counterpart to v4's glassy aging X<1, along the same
   diverging-timescale signature).
2. **The two-sided-headroom finding, sharpened (advances v1/v2's owed vector).** A sweep DOES
   ground the two-sided headroom — but only its *qualitative / observable* part: the answerer
   grounded the DIRECTION (heading toward an instability) and the RELATIVE rate (tauC ~doubling
   per step → the spectral gap shrinking) from the band. The ABSOLUTE distance-to-edge **in the
   researcher's native control units is NOT closeable even with a sweep** — it needs the
   control-axis magnitudes (g_s), which are exactly the model parameters blinding correctly
   strips. So the closeable headroom lives in the OBSERVABLE (the relaxation rate / spectral
   gap), not in the native control units. The answerer independently surfaced this (parked
   "distance to instability/Hopf edge in knob units" as not-groundable) — the same channel that
   surfaced v1's headroom limit. (Note: the edge here is a real-eigenvalue instability, not a
   Hopf/oscillatory one — the answerer's "Hopf" hedge is immaterial, it was a parked item.)

## residue (→ HANDOFF ledger)
`coupling_ramp_v7 | 1 (Vertex, metric sweep) | CLEAN | 5 levels all reversible Cat-1 relaxation;
tau_slow diverges 1.43→20 (critical slowing), gap 0.70→0.05, X=1 (affine FDR) throughout, no
oscillation/current/aging onset | BLIND MATCH. METRIC-boundary blur answered for Cat-1: NO smear
along a continuous axis — only magnitude changes, the operating point approaches a stability edge
via critical slowing; companion to v6's topological-sharpness result. Anchor: level 1 (g_s=0.6) =
v6 community 0, reproduced blind. FINDING (sharpens v1/v2): a sweep grounds the QUALITATIVE/relative
two-sided headroom (approach direction + rate, spectral gap shrinking) but the ABSOLUTE
distance-to-edge in native control units is NOT closeable — it needs the control magnitudes that
blinding strips; closeable headroom is in the observable (the gap), not native units. Δ→next: a
METRIC blur that ACTUALLY smears still wants a substrate where a tuned axis crosses a category
boundary (criticality T→Tc, or the Cat-2 reciprocal pair, still GAP). earned/.`
