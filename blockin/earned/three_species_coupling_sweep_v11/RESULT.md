# three_species_coupling_sweep_v11 — BLIND PASS RESULT

phase: DEV/blind · view: `view_20260526-013443.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

A sweep: one three-population cyclic non-reciprocal community's two-point statistics (C, chi, the
directed cross-correlations Cxy/Cyx) + winding (phiMean/phiVar), at 5 CYCLIC-COUPLING strengths
(level 1..5; level 1 weakest, level 5 strongest, level 3 = baseline), FIXED noise. Per WORKFLOW §6,
each coupling placed as an **independent single-point fit first**, then the band read off the 5
placements. Each level on its own clock (window ~6 of its own rotation periods; weak/slow loops
watched longest).

The substrate is the noisy frustrated Banach-class reference (`mpa-central/library/banach_frustrated.py`,
same as v3/v5/v6): M = −γI + g·A_cyc (cyclic antisymmetric), eigenvalues −γ, −γ±i√3g (the complex pair
= the current). Truth computed HERE from the structure (exact OU + per-level seeded NESS winding
simulation), never via conform — omega/γ=√3(g/γ), ⟨σ⟩=6g²/γ, affinity/cycle ∝ g (see `entry.md` SEALED
half / `freeze_three_species_coupling_sweep.py`).

This is the meta-SOP §2-escalated STRUCTURE-dependence vector v5 parked: v5 swept NOISE at fixed wiring
and found the rate FLAT (noise-independent); it parked the complementary claim that the rate is SET BY
THE WIRING (tracks g/γ). The coupling axis is that claim's test.

---

## Per-level placement (the framework read)

| level | coupling_rel | g | directed current (Cxy=−Cyx) | turnover rate (cyc/τ) | \|Cxy−Cyx\| | stable |
|---|---|---|---|---|---|---|
| 1 | 0.25× | 0.15 | yes | 0.040 | 0.16 | yes |
| 2 | 0.50× | 0.30 | yes | 0.083 | 0.36 | yes |
| 3 (anchor) | 1.00× | 0.60 | yes | 0.164 | 0.66 | yes |
| 4 | 2.00× | 1.20 | yes | 0.331 | 1.05 | yes |
| 5 | 4.00× | 2.40 | yes | 0.661 | 1.41 | yes |

- **Directed current at every level:** the turnover-plane cross-correlations are ANTISYMMETRIC
  (Cxy=−Cyx, residual 0.0) — a real circulation, not a reciprocal/Cxy=Cyx ring-down. Survives to the
  weakest coupling (no onset threshold).
- **Two independent rate reads agree:** the autocorrelation oscillation frequency AND the winding drift
  rate give the same turnover rate at every level (the damped-cosine frequency = omega carries the
  structure — a second grounding beyond the winding).

## The band (what migrates / what stays put)
- **Migrates (the tracking signature):** the turnover rate RISES ∝ the coupling — winding rate
  0.040→0.661 cyc/τ (= omega/2π = √3g/2π), log-log slope **p=1.01** (exact linear); ratio-to-baseline
  matches coupling ratio within ~2%. Current magnitude |Cxy−Cyx| rises 0.16→1.41 with g.
- **Stays put:** the KIND — a stable directed cyclic current (Cxy=−Cyx, no instability) at every
  coupling. Strong coupling spins faster, it does not destabilize.

## Verdict in the researcher's own terms
- **Is there a directed cycle, and where?** At every strength, including the weakest — Cxy=−Cyx
  throughout. No all-or-nothing onset.
- **Tracks or flat?** TRACKS — the turnover rate rises in direct proportion to the interaction
  strength (near-linear). Strengthen the loop, it cycles proportionally faster.
- **Rate set by what?** The WIRING. With the noise ruled out (v5), strengthening the cyclic
  interaction is what speeds the loop. The current is the wiring, not the weather.

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **Turnover rate recovered EXACTLY:** sealed omega/2π `[0.041,0.083,0.165,0.331,0.661]` vs blind winding
  rate `[0.040,0.083,0.164,0.331,0.661]` ✓. Tracking law: sealed linear (∝g), blind log-log slope
  p=1.008–1.013 ✓.
- **Both independent rate channels** (winding drift + autocorr oscillation frequency) recovered and agree
  — the dual grounding the design built in (M depends on g, so the damped-cosine frequency carries omega) ✓.
- Directed current Cxy=−Cyx at every g>0 ✓; current magnitude |Cxy−Cyx| `0.16→1.41` reproduced
  (peak|Cxy| ×2) ✓; cycle survives the weak end (cage_edge 3 avoided) ✓.
- **Headline tooth hit** (cage_edge 1, flat/coupling-independent): read as TRACKS, not flat ✓. Other
  misreads avoided: not inverse (cage_edge 2) ✓, no false instability (cage_edge 4) ✓, real current not a
  reciprocal ring-down (cage_edge 5) ✓.
- **Not hollow** — every claim grounded on a computed observable (Cxy=−Cyx, winding rate, osc frequency,
  log-log slope) ✓. **Meta-validity P held** — independent per-level placements, then band ✓.
- **No KILL:** no NaN, current present where required (not forbidden), stable at every level, ground-truth
  omega/γ=√3g + ⟨σ⟩=6g²/γ (freeze-confirmed).
- **Anchor-and-assert (HARD):** level 3 (coupling_rel=1.0, g=0.6) is v3/v5's exact point. Blind L3:
  winding rate 0.164 cyc/τ ×2π = 1.03 rad/τ = omega = √3·0.6 = 1.039 → reproduces v3/v5's baseline (rate
  ~1.04, current present, stable). No cross-pass drift.
- **Boundary symmetry (§4):** every `not_grounded[]` item is a collapsed-axis / honest-limit park (native
  units = v7/v8/v9 limit; behaviour exactly at g=0 — the Cat-10→Cat-1 edge, not sampled; above-4× window;
  exponent precision from 5 points; loop phase = the held-aside total axis). Both directed
  cross-correlations were in-slice, so the current sector was groundable from each level.

**The finding.** **The Cat-10 directed current TRACKS the wiring** (turnover rate ∝ coupling, recovered
linearly via two independent channels; affinity ∝ g, dissipation ∝ g²). This **closes the meta-SOP
§2-escalated structure-dependence vector v5 parked.** Together with v5 (rate FLAT across a 20× noise
range) it pins the Cat-10 current on both of its control axes: **the current is the WIRING, not the
weather** — noise tidies the loop without slowing it; the coupling sets how fast it spins. Secondary
(consistent with v6): the current magnitude shrinks toward g→0 but the KIND stays Cat-10 (Cxy=−Cyx) at
every sampled g>0 — the reciprocity cut is topologically sharp; g→0 deletes the loop rather than blurring
the class. The Cat-10 sector is now mapped on both control axes (v5 noise, v11 structure), with v3 the
single-point anchor and v6 the minimal-distance 1↔10 separation.

view: deposited as `earned/three_species_coupling_sweep_v11/view_20260526-013443.png`.
