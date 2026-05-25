# verdict — community_pair_v6  (DEV/blind)  →  **MATCH** (clean two-sided separation)

Orchestrator grading record (holds the seal). The examinee's reading is in
[`RESULT.md`](RESULT.md); this file is the unseal comparison + the anchor check.

The probe: two three-population loop communities one **reciprocity-flip** apart on the
SAME substrate family (`mpa-central/library/banach_frustrated.py` machinery), same operating
point γ=1.0, g=0.6, D=0.1 — community 0 a **matched/symmetric** coupling (detailed balance),
community 1 the **cyclic/antisymmetric** coupling (= `three_species_cycle_v3` exactly). Posed
in one blind packet with NO per-community class hint; the discriminator (cross-correlation
symmetry) was sealed. Traversed as two independent single-point placements + a separation
readout (sweep contract, §6).

---

## unseal: blind reading vs sealed truth

| claim | sealed truth | blind answerer read | |
|---|---|---|---|
| community 0 class | Cat 1 — reversible relaxation, detailed balance, **⟨σ⟩=0**, no current | "settling with noise; monotone-decay C; Cxy=Cyx; winding≈0; FDR affine R²=1.00" | ✅ |
| community 1 class | Cat 10 — sustained NESS current, **⟨σ⟩=2.16**, Cxy=−Cyx | "genuine persistent turnover; damped-osc; Cxy=−Cyx; +6 turns; FDR non-affine" | ✅ |
| discriminator | cross-correlation **symmetry** (Cxy=Cyx vs Cxy=−Cyx), the time-reversal signature — NOT C-shape alone | split grounded on cross-corr symmetry, corroborated by winding-angle + C-shape (three agreeing reads) | ✅ |
| same or different? | genuinely DIFFERENT — opposite thermodynamic classes on one loop topology | "genuinely DIFFERENT" | ✅ |
| stability | both stable; cyclic one's turnover is a nominal NESS, not an edge | "both healthy/interior; #1's turnover is stable circulation, not an instability edge" | ✅ |
| cage_edge 1 (Vertex-collapse of community 1) | the MISS to avoid | avoided — caught Cxy=−Cyx + the current | ✅ |
| cage_edge 2 (false current in community 0) | the mirror MISS to avoid | avoided — read winding≈0, symmetric cross-corr, no current | ✅ |
| cage_edge 3 ("they're the same") | the headline separation MISS | avoided — separated cleanly | ✅ |

**No hollow MATCH:** every claim carries provenance (the column / step that established it).
**No KILL:** no NaN, no TUR floor violation, FDR-locus and winding frames agree on community 1,
no false ground-truth current for community 0, correct parity. **Parks are all collapsed-axis /
viewport-dial** (absolute coupling strengths, noise-vs-coupling without a 2nd point, two-sided
headroom / distance-to-instability needs a sweep, calibrated T_eff, researcher preference) — no
in-slice observable withheld. Slice symmetry (§4) clean.

## anchor-and-assert (orchestrator-side; community 1 = v3, not disclosed to the answerer)

Community 1 is v3's substrate at v3's exact operating point. The blind fit reproduced v3's
contour with no cross-pass drift:

| quantity | v3 earned | v6 blind read | |
|---|---|---|---|
| winding total | 37.98 rad (~6.0 turns) | 37.5 rad (~6.0 turns) | ✅ |
| winding rate | ~1.04 / clock (~ rotation rate) | +1.053 / clock | ✅ |
| damping γ_eff | 1.0 | 1.027 (blind fit) | ✅ |
| rotation rate ω | 1.039 | 1.114 (blind fit, +7% — fit-from-data, acceptable) | ≈ |
| cross-corr asymmetry | \|Cxy−Cyx\| peak 0.66 | antisymmetric, Cmin −0.073 (consistent) | ✅ |

The answerer did not know community 1 was an anchor; it independently landed v3's numbers.

## the finding (separability — the load-bearing one)

The **1↔10 cut is TOPOLOGICALLY sharp, not metrically blurry.** This is the first separation
at minimal *generating* distance (one reciprocity-flip apart), yet the *observable* distance is
large — because reciprocity is a **discrete** structural property: a coupling is symmetric or it
is not; g→0 deletes the loop rather than blurring the class. There is no continuous knob that
smears community 0 into community 1. This reframes WHY the prior far-separations (1↔10, 1↔8)
read clean: the reciprocity boundary cannot smear. It does **not** settle whether **metric**
boundaries (criticality, coupling-strength continua, **Cat 2** reciprocal 2-node) blur — that
wants a tunable-axis probe on a substrate that is still GAP.

## residue (→ HANDOFF ledger)
`community_pair_v6 | 1⊕10 (reciprocity-flip pair) | CLEAN | both placed, separated on cross-corr
symmetry; ⟨σ⟩=0 vs 2.16, Cxy=Cyx vs Cxy=−Cyx | BLIND MATCH (two-sided, both cage_edges avoided);
anchor=v3 reproduced; finding: 1↔10 cut is topological/discrete (sharp), not metric blur — metric
blur (Cat 2) still the open informative probe. earned/.`
