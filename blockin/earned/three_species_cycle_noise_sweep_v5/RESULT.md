# RESULT — three_species_cycle_noise_sweep_v5  (orchestrator's graded record)

**Grade: MATCH** (genuine, richly grounded — no cage_edge, no KILL, not hollow; the blind
read was MORE conservative than the seal on the one noisy axis — no overclaim). Pass run
2026-05-25, DEV/blind. Category 10 (Non-Reciprocal). Intent I2 (noise sweep — five operating
points). Substrate: `mpa-central/library/banach_frustrated.py` (3-mode cyclic non-reciprocal
OU; FIXED γ=1.0, g=0.6; swept D = [0.02, 0.05, 0.10, 0.20, 0.40], a 20× noise range).

This is the **second I2 vertical** (after v2's pump sweep) and the **spend of v3's owed
noise-INDEPENDENCE vector** — the one claim v3 honestly parked (a single operating point
cannot separate "the rate is the wiring" from "the rate is what it happens to be at this
noise"). The sweep grounds it: across the noise axis v3 could not see, the current rate is
flat.

## What the blind answerer returned (verbatim shape — see `verdict.md`)
- **Verdict:** the cycling is INTRINSIC, not noise-driven — turning the environment down will
  NOT slow or stop the turnover. Same rate at every noise level; no headroom toward a
  settling/steady-balance asymptote.
- **Placement (5 independent single-point fits + band):** winding rate d⟨φ⟩/dτ = 1.002…1.059
  rad/clock (R²=1.000 each), band mean 1.042, rel-spread **5.5%** over 20× noise — INVARIANT.
  Two-point block (C, χ, Cxy, Cyx) IDENTICAL across levels (max cross-level dev 0.0e+00).
  Directed current Cxy = −Cyx at every level incl. the calmest, antisymmetric peak ≈0.33/comp
  (⇒ |Cxy−Cyx| ≈ 0.66). Phase-diffusion baseline d(phiVar)/dτ ≈ 12.2, rel-spread 6.7% — also
  flat. Sporadic phiVar jumps only at L3/L4, non-monotone in noise.
- **grounded[]:** cycling intrinsic (phiMean slope flat, R²=1.00); turnover structure
  noise-independent (C/χ/Cxy/Cyx identical); sustained directed cycle at all levels (Cxy=−Cyx);
  baseline diffusion ~noise-invariant (robust median phiVar slope); stationary non-settling
  regime (FDR locus + oscillatory C).
- **not_grounded[]:** WHAT noise changes as a clean law (the sporadic phiVar jumps are
  non-monotone — can't promote to "noise sets a phase-slip rate" without per-point grain);
  behavior below 0.2× noise (collapsed axis floor); individual coupling strengths (not in the
  observables); any "best/healthiest" preference among levels (researcher dial, value-laden).

## Unseal — comparison to `entry.md` sealed_answer
- **MATCH conditions, all met:** read each level as the same sustained directional current;
  read the band as FLAT (rate noise-independent); concluded the turnover is wiring-set and
  calming would NOT settle it (the v3 worry, now from data); placed it STABLE; identified that
  the rate is what does NOT move with noise.
- **cage_edges — none tripped:** rate NOT read as decreasing/settling with calm (edge 1, the
  headline MISS this vertical hunted — AVOIDED); spread NOT read as the rate growing (edge 2 —
  AVOIDED, and the answerer self-corrected a first-draft "diffusion rises with noise" overclaim
  to not_grounded); damped-cosine C NOT collapsed to a Vertex ring-down (edge 3 — AVOIDED,
  Cxy=−Cyx read as a genuine chiral current); NOT called unstable at high noise (edge 4).
- **KILL checks — none fired:** all finite (no NaN); the two frames AGREE (FDR locus +
  winding both read driven/non-settling — no §J disagreement); asymmetry has correct odd-in-τ
  parity with fixed sign. TUR floor not violated (seal: T≥1 at every level).
- **Over-claim guard — passed (notably):** the seal treated "the absolute spread carries the
  noise dependence" as a soft TARGET sub-point; the blind answerer could not even ground THAT
  cleanly and PARKED it (the phiVar jumps are estimator-noisy / non-monotone). So the MATCH is
  the cleanest kind — the examinee was *more* conservative than the answer key on the one axis
  the seal already flagged as noisy. This independently re-derives `docs/deferred-for-auditor.md`
  **Entry 2** (the winding second-moment is under-resolved): a blind reader hits the same wall,
  so the caveat is real, not a freeze artifact.
- **Hollow / value-laden guards — passed:** every claim carries column-level provenance; no
  "healthiest" level invented (respects the §6 carve-out / Entry-1 dial discipline — the
  answerer flagged it as a dial).
- **Anchor-and-assert (level 3 = v3's D=0.1) — REPRODUCES v3:** blind level-3 rate 1.056 ≈ v3's
  ω/γ=1.039; |Cxy−Cyx| ≈ 0.66 = v3's exact sealed peak (0.66); current present; stable NESS.
  Cross-pass drift check passes (the answerer did not know level 3 was the anchor — it placed
  all five independently).
- **Computed values vs seal:** band rate 1.042 vs ω/γ 1.0392; per-level R²=1.00 vs exact linear
  drift; two-point identity across D vs the analytic D-cancellation; Cxy=−Cyx exact vs sealed
  exact. All consistent.

## Residue / finding
- **v3's owed noise-INDEPENDENCE vector is CLOSED (grounded blind).** The current rate /
  per-cycle directedness is flat to <6% across a 20× noise range; the antisymmetric current and
  the FDR-locus/winding two-frame agreement survive the whole sweep. Calming the environment
  tightens the loop (when anything moves at all), it does not slow or stop it. This is the
  empirical answer to the structural-only counterfactual v3 could give from one point.
- **The winding second moment is the honest limit, blind-confirmed.** The answerer parked "what
  noise changes" because phiVar's noise-dependence is estimator-noisy/non-monotone — exactly
  `deferred-for-auditor.md` Entry 2, now re-derived from the blind side. The caveat graduates
  from "single surfacing" to "surfaced by the author AND independently by the blind examinee" —
  still ONE substrate, so it stays provisional, but its validity is strengthened.
- **Separability:** unchanged by this pass (same substrate as v3). v5 was an I2 sweep on an
  existing dot, not a new category — the load-bearing separability gap (a structurally-ADJACENT
  pair) is still open. See HANDOFF §hypothesis.

## Next move (gated, see HANDOFF baton)
MATCH → ADVANCE. v5 closed v3's owed vector; v4's owed t_w aging sweep remains owed (parked
once). The new dev-legal park this pass opened: STRUCTURE dependence — that the rate/affinity
TRACKS g/γ — needs a structure sweep (a different collapsed axis), the natural v6 ADVANCE. The
separability-driven recommendation (a structurally-adjacent pair, e.g. `banach_frustrated`'s
reciprocal control vs the v3 frustrated loop — the cheap 1↔10 adjacency, ready substrate) also
stands. Authoring stays gated; sealed_answer freeze-computed.
