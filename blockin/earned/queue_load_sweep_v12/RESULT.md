# queue_load_sweep_v12 — BLIND PASS RESULT

phase: DEV/blind · view: `view_20260526-020751.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

A sweep: one single-server queue's queue-length fluctuation autocorrelation C and integrated response
chi, at 5 LOADS climbing toward the capacity wall (level 0..4; level 0 lightest, level 4 heaviest /
nearest the limit). Per WORKFLOW §6, each load placed as an **independent single-point fit first**, then
the band read off the 5 placements. Each load on its own clock (windows grow ~236→119000, matched to
each load's own diverging relaxation).

The substrate is an **M/M/1-queue oracle** (the v8 equilibrium-criticality pattern on the queueing
substrate): per load ρ a single reversible relaxational mode with the EXACT M/M/1 scalars — spectral gap
λ(ρ)=μ(1−√ρ)², variance Var(ρ)=ρ/(1−ρ)², mean ⟨n⟩=ρ/(1−ρ); χ built from C by the equilibrium FDT so the
FDR locus is the identity (slope 1, X=1) by construction. Truth from the M/M/1 reversibility theorem +
exact queueing scalars, never via conform (see `entry.md` SEALED half / `freeze_mm1_critical_slowing.py`).

This closes **Cat 9 (Queueing)** on its own substrate with the meta-SOP §2 / FALSIFICATION FINDING-3
REFRAME. mm1_queue's named α_s=½ falsifier is a category error: ½ is the heavy-traffic / reflected-BM
time-scaling exponent (C-vs-lag plane, the relaxation-time divergence), α_s is the FDR effective-
temperature slope (χ-vs-C plane) — different planes. AND the raw library cells are window-limited near
ρ→1 (slope unresolvable), so the oracle (v8 precedent) makes X=1 blind-readable.

---

## Per-load placement (the framework read)

| level | util_rel | ρ | FDR slope X | relaxation time | variance C(0) | C shape |
|---|---|---|---|---|---|---|
| 0 | 1.0× | 0.60 | 1.000 | 19.7 | 3.75 | single reversible relaxation |
| 1 | 2.67× | 0.80 | 1.000 | 89.9 | 20 | single reversible relaxation |
| 2 | 6.0× | 0.90 | 1.000 | 380 | 90 | single reversible relaxation |
| 3 | 12.67× | 0.95 | 1.000 | 1562 | 380 | single reversible relaxation |
| 4 | 32.67× | 0.98 | 1.000 | 9915 | 2450 | single reversible relaxation |

- **FDR locus (universal readout):** a single straight line through the origin of slope 1 (X=1) at EVERY
  load — early- and late-segment slopes both 1, never bends. The response stays matched to the
  fluctuations (in balance) at every load, including the heaviest.
- **Single reversible relaxation** (no two-step/plateau, no oscillation/current) at every load.

## The band (what migrates / what stays put)
- **Migrates (critical slowing + growing fluctuations):** the relaxation time DIVERGES 19.7→9915 (~500×)
  and the variance C(0) DIVERGES 3.75→2450 (~650×) as the load climbs toward capacity — steep power laws
  in the relative load. This is the approach to the ρ=1 capacity wall.
- **Stays put:** the FDR slope X=1 (reversible/in-balance) at every load — the KIND does not change.

## Verdict in the researcher's own terms
- **In balance or out?** In balance at every load (X=1, FDT holds). The imbalance the researcher worried
  about does not appear — the response keeps pace with the fluctuations even at the heaviest load.
- **Approaching breakdown, or just slower-and-noisier?** The latter: reversible critical slowing toward
  the capacity wall (timescale + variance diverge), NOT a tip into a stuck/aging state.
- **Naive correction:** "near capacity it must break / go pathological / fall out of balance" is WRONG —
  it is reversible critical slowing (X=1, in balance), just very slow and very variable.

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **X=1 recovered EXACTLY:** sealed FDR slope `[1,1,1,1,1]` vs blind 1.0000 (single straight line, no
  bend, χ∞/C0=1.0000) at every load ✓.
- Critical-slowing band recovered: relaxation time 19.7→9915 (≈503×) and variance 3.75→2450 (≈653×) both
  diverge toward capacity ✓; single reversible relaxation (no two-step) ✓.
- **Headline tooth hit** (cage_edge 1, aging/out-of-balance): read as IN BALANCE (X=1), reversible
  critical slowing, NOT aging ✓.
- **The FINDING-3 category error avoided** (cage_edge 2): the answerer explicitly separated the diverging
  power-law quantities (timescale, amplitude — the plane where the ½ heavy-traffic exponent lives) from
  the FLAT FDR slope (X=1), and noted the divergence exponent is not recoverable in native (1−ρ) units —
  exactly the two-plane distinction the README conflated ✓.
- Other misreads avoided: not nominal/no-slowing (cage_edge 3) ✓; not two-step/glassy (cage_edge 4) ✓;
  no oscillation/current (cage_edge 5) ✓.
- **Not hollow** — every claim grounded on a computed observable (FDR slope, relaxation time, variance,
  C shape) ✓. **Meta-validity P held** — independent per-load placements, then band ✓.
- **No KILL:** no NaN, no X>1 (X=1), no current, ground-truth FDR slope=1 + timescale/variance diverging
  (freeze-confirmed).
- **Anchor (soft, first contact):** no prior earned queue point. The heaviest-load reading is the same
  KIND as v7/v8 (X=1 reversible critical slowing), NOT the v4/v9/v10 X<1 aging — cross-pass consistency
  by kind. No hard numeric anchor.
- **Boundary symmetry (§4):** every `not_grounded[]` item is a collapsed-axis / honest-limit park (native
  utilization/rates; the divergence exponent in native (1−ρ) units — exactly the FINDING-3 C-decay plane;
  behaviour at the limit; native headroom; past-window; critical-point-vs-steepening). None withheld
  in-slice; the reversible queue has no current sector by construction.

**The finding.** **The near-capacity M/M/1 queue is reversible critical slowing (X=1), not aging** — and
conform reads it correctly, separating the heavy-traffic ½ exponent (the diverging relaxation-time/C-decay
plane) from the FDR slope (=1, the χ-vs-C plane) the README's falsifier conflated. This **closes Cat 9 on
its own substrate with the FALSIFICATION FINDING-3 reframe** (the named α_s=½ falsifier is a category
error). It is the X=1 reversible counterpart to v4/v9/v10's X<1 aging, and the QUEUEING counterpart to
v8's thermodynamic-criticality X=1 — the critical-slowing-vs-aging discriminator is now answered from
both sides on a queueing substrate too.

**Parked (NOT adjudicated here — a framework/cdv1 matter for FALSIFICATION, out of scope for the blind
pass):** cdv1 §Load-handling maps heavy-traffic M/M/1 (chit=−ln ρ→0⁺) into the s-regime, whose FDR
signature is aging (X<1); M/M/1 reversibility forces X=1. So either that mapping over-claims, or s admits
X=1 critical slowing. This pass establishes the substrate truth (X=1 reversible); reconciling it with
cdv1's s-regime stays in FALSIFICATION FINDING 3 (the sharp version was the ising_equilibrium test,
closed by v8). Flagged for the cross-repo parking lot.

view: deposited as `earned/queue_load_sweep_v12/view_20260526-020751.png`.
