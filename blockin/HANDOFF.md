# HANDOFF — conform block-in (the baton)

Mutable state only. This file carries **what changes pass-to-pass** — the resistance
line, the ledger, the open hypothesis, the substrate reference, and the current
state / next move. The *stable method* lives elsewhere; read those first if new:

- **PIPELINE.md** — the object (conform's data-prep silhouette).
- **WORKFLOW.md** — the pass-SOP (how to run one pass; rules of the game; the A–P box).
- **meta-SOP.md** — the evolution governance (how a verdict evolves the artifacts +
  picks the next question; **start there: §0 on-entry reconcile**).
- **HANDOFF.md** (this file) — the baton.

Full design + why: memory `project_conform_blockin_apparatus`. Repo context:
mpa-conform/CLAUDE.md, mpa-central/SYSTEM_OVERVIEW.md.

---

## Resistance line  [stable]
Reaching for the tau_obs sweep, the bootstrap cost, the full characterization
tensor, or the 10-category protocol as a *plan*? Stop — you're painting scales.
One brittle vertical at a time; the silhouette precipitates, it is not designed.

## Open hypothesis under test  [shrinks as resolved]
- **10-category separability**: do real substrates land in one category cleanly, or
  smear across several? **First aggregation (3 verticals: v1/v2 Vertex, v3 Cat-10).** The
  first CROSS-category test landed CLEAN: Cat-1 (reciprocal ring-down) and Cat-10 (sustained
  circulation) share the same damped-cosine autocorr C(τ), yet a blind answerer separated
  them on the cross-correlation antisymmetry (Cxy≠Cyx) with no smear. So the 1↔10 boundary
  reads SHARP on that observable. Caveat: n=1 cross-category datapoint, both substrates
  analytic/clean; the hypothesis is *encouraged, not confirmed* — needs categories that share
  MORE structure (a reciprocal coupled pair, Cat 2) to find where the boundary actually blurs.

## Vertical ledger  [append 1 line/pass; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. RECLASSIFIED 2026-05-25: verdict-lens inversion is a VIEWER-LAYER concern (researcher utility-lens over the computed band), NOT a teeth-defect → deferred to docs/deferred-for-auditor.md Entry 1, NOT re-posed as v3. earned/.
three_species_cycle_v3| 10 (Non-Recip)   | CLEAN         | sustained NESS current ω/γ≈1.04, ~6 loops/run, far from the ω→0 equilibrium edge; Δ→next: quantitative noise-INDEPENDENCE needs a noise sweep | BLIND MATCH. First contact with the current-gate / two-frame sector (Vertex structurally cannot reach it): a blind answerer read the current in TWO frames (FDR-locus loop + winding/antisymmetry) and they AGREE; placed it STABLE; corrected the naive "noise-driven wobble" worry. CAT-1 vs CAT-10 SEPARATED CLEAN — same damped-cosine C as a ring-down, but the answerer caught Cxy=-Cyx and did NOT collapse to Vertex (separability's first non-Vertex datapoint, no smear). Re-bounded mid-session under the new symmetric-boundary rule (WORKFLOW §4): the in-slice winding ensemble made affinity/TUR/two-frame groundable from ONE point. Note: answerer grounded agreement via locus-vs-winding, NOT the formal affinity/TUR scalars (in-slice but unused → reachable-but-unexercised). Noise-independence parked = a COLLAPSED-AXIS park (legit ADVANCE vector), not under-provisioning. earned/.
```

## Substrate coverage map  [the ceiling — which categories have a clean-truth substrate]

The reserve mapped onto the 10-category taxonomy. **This is what is *authorable*, NOT what
is *done*.** **"Clean truth"** = analytic ground truth computable *without conform* (the
answer-key gate). Status: **READY** (clean substrate in hand → a vertical *could* be
authored) / **PARTIAL** (substrate exists but truth partial/off-category) / **GAP** (no
clean-truth substrate). A separate **⟳ LANDED** tag marks a category with an actually-run,
documented vertical in `earned/` — **only Vertex (v1) so far**; v2 (also Vertex) is
authored, not run. So "READY" means a substrate sits waiting, *not* a test completed.
Two caveats: the taxonomy is itself the open separability **hypothesis** (category
*meanings* are a working reconstruction, provisional); the substrate inventory is grounded
(read from `mpa-central/library/`).

| # · category | reserve status | landed? | clean-truth substrate(s) in hand |
|---|---|---|---|
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED** (v2 run 2026-05-25 — MISS-with-finding, NOT landed) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓ — *deep* |
| 2 · Edge (coupled pair) | PARTIAL | — | two_temp_ou is 2 coupled OU but exposed as single-relax+X; want a clean *reciprocal* 2-node |
| 3 · Subgraph (motif) | **GAP** | — | banach_frustrated is a 3-mode but *non*-reciprocal (→ cat 10); a reciprocal motif / Harary triad has no clean-truth data yet |
| 4 · Meta-Ledger | **GAP** | — | abstract (FDT/entropy accounting); no substrate identified — may be an *instrument* test, not a substrate |
| 5 · Kernel (camera/τ_obs) | PARTIAL | — | no dedicated camera-artifact substrate; probe via kww_oracle's two timescales + a τ_obs sweep |
| 6 · Encoding | **GAP** | — | no dedicated substrate; the `e_i=s_i⊕s_{i-1}` preprocessing needs a spin process with clean truth |
| 7 · Capacity | PARTIAL | — | mm1_queue's ρ→1 saturation *is* a capacity limit — repurpose-able; no dedicated capacity substrate |
| 8 · Phase (glassy/critical) | PARTIAL+ | — | kww_oracle ✓ (glassy relaxation fingerprint), ising/ou equilibrium ✓ (X=1); criticality/aging PARTIAL (sk z≈4, sir R₀, voter — placeholder near Tc) |
| 9 · Queueing | **READY** | — | mm1_queue ✓ (exact stationary ρ/(1−ρ)) |
| 10 · Non-Reciprocal (current/k_frust) | **READY+** | **⟳ v3 LANDED** (BLIND MATCH 2026-05-25; current-gate/two-frame sector reached & agree) | banach_frustrated ✓ (exact 3-mode current, affinity/TUR); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 3 categories are
READY (1, 9, 10), ~4 PARTIAL (2, 5, 7, 8), 3 GAP (3, 4, 6). *Work-wise*, **2 verticals have
landed contours** — v1 (Vertex/Cat 1) and v3 (Cat 10, non-reciprocal); v2 (Vertex sweep) graded
MISS-with-finding (deferred to the viewer layer, landed no contour). So landed evidence is now
TWO records across TWO categories (`earned/laser_ro_nominal_v1/`, `earned/three_species_cycle_v3/`)
plus one documented MISS. v3 closed the Non-Reciprocal branch and reached the current/two-frame
sector. Remaining clean substrate-ready branch off the dots: **Queueing (mm1_queue, Cat 9)**. But
the separability §4 caveat now points elsewhere — the 1↔10 separation was easy (very different
substrates); the informative next probe is a category that shares MORE structure with an existing
dot, i.e. **a reciprocal coupled pair (Cat 2)** to find where the boundary actually blurs. The
GAPs (3, 4, 6) need a clean-truth substrate *built* before they're authorable — the runway limit.

- **Falsifier / out-of-domain probes** (test the tripwires, not a category): logistic_chaos
  (no FDT → KILL-test), sine/square_wave (decorrelate trivially), constant (no dynamics).
- **Pure-stochastic, no analytic handle** (NOT authorable as-is): abp, heston, east,
  levy_flight, fbm (scaling known, C/χ not).
- **HOLD (known-contaminated, do NOT seed from):** unnormalized quantum chi, zero-filled
  brain C/chi, null glass tau_env (mpa-central DEFERRED.md library-refresh), and any
  conform-touched seed-corpus bundle (examinee output).
- **conform pieces to quarry** (as examinee, never answer key): conformer/compute/
  {inversion, gfdr_model, five_vector}.py.

---

## Pick up here (end of session 2026-05-25, 3rd entry)

**State — v3 (`three_species_cycle_v3`, Cat 10) ran BLIND and graded MATCH. Second category
landed; the current-gate / two-frame sector reached and exercised for the first time. Two
apparatus refinements also landed this session (the symmetric boundary + the strict deferral
threshold). Evolve done; pass committed.**

1. **The pass.** v3 jumped category off the two Vertex dots to the first current-bearing
   substrate (`banach_frustrated`, a 3-mode cyclic non-reciprocal OU), posed in researcher
   voice as a three-species rock-paper-scissors ecology ("real persistent turnover, or
   noise-kicked damped wobble?"). A blind answerer read it from the sanitized inputs only and
   returned MATCH-intent; unseal confirmed **MATCH**: it caught the sustained directional
   current (Cxy=-Cyx + linear winding drift), did NOT collapse the damped-cosine autocorr to a
   Vertex ring-down, read the two frames (FDR-locus loop + winding) as AGREEING, placed it
   STABLE, and corrected the naive worry — while honestly parking quantitative
   noise-independence (a collapsed-axis park). No cage_edge, no KILL. `earned/three_species_cycle_v3/`.

2. **Apparatus refinement A — the symmetric data boundary (WORKFLOW §4).** Authoring v3
   surfaced a method gap: the author had TWO dials (the slice AND which in-slice observables to
   hand over), so a `not_grounded` could be manufactured by under-provisioning — a MISS that
   wouldn't isolate conform. Fixed: **the slice is the only dial; within it the blind data is
   the complete honest observable content of the researcher's measurement** (no curation).
   `not_grounded[]` must fall out of the SLICE (a collapsed axis), never out of curation;
   detector = the leak tripwire run in reverse. This *mechanically* re-bounded v3 (the winding
   ensemble is honest content of one run → in; affinity/TUR/two-frame became in-slice
   groundable; only noise-independence stayed parked, across the noise axis). New P-checklist
   bullet too. **Human approved.**

3. **Apparatus refinement B — strict deferral threshold (`docs/deferred-for-auditor.md`).** The
   doc's entry bar was made explicit and STRICT: an item earns an entry **only if it must
   become a STANDING viewport affordance beyond what the per-pass result image already
   delivers** — source-agnostic (a finding, MISS, or park can clear it), watch-list as the
   cheap default, prune non-recurring. Rationale (human): *much current work will be
   off-target* → high bar, entries cheap to drop. v3 surfaced no new dial (its park is
   delivered in the result image; the "healthiest"-style lens didn't recur). **Human approved.**

4. **Residue worth a glance (not yet an action).** The answerer reached two-frame AGREEMENT via
   a locus-area-vs-winding-drift cross-check, NOT via the formal affinity-in-nats / TUR-factor
   (T>=1) scalars — which are now in-slice groundable (the data carries phiMean/phiVar) but went
   unused. So the formal TUR-floor check is *reachable-but-unexercised*. Open question for a
   future pass/human: should the answerer contract (WORKFLOW §6) REQUIRE the formal TUR-floor
   readout where a current is present, or is an equivalent two-frame cross-check enough? Logged,
   not decided. (PIPELINE §4 [CONTACT] note records it.)

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). As of writing: the v3 pass commit covers
`blockin/**` (WORKFLOW §4 boundary, PIPELINE accretion, this baton, `earned/three_species_cycle_v3/`);
the `docs/deferred-for-auditor.md` threshold is a SEPARATE commit (outside `blockin/`). The two
out-of-block-in arcs (consolidation, five-vector WIP) and the riding crumbs remain PENDING rows.
`questions/` is **empty** (v3 moved to `earned/`). **One writer at a time.**

**Next move (next round) — gated authoring; pick the probe, then run the loop:**
1. meta-SOP §0 reconcile — diff `git status` against `PENDING.md` first. `questions/` empty;
   v1+v3 landed in `earned/`, v2 documented-MISS; confirm the v3 pass + threshold commits landed.
2. **Author the next vertical** (gated; `sealed_answer` freeze-computed, never prose-asserted).
   Per meta-SOP §2 a MATCH → ADVANCE one vector to ground v3's `not_grounded` = **noise-
   INDEPENDENCE**; but that needs a noise sweep (multi-point = I2/prod), so it is **logged owed**
   (parked once; escalates to the default if parked again). Dev-legal candidates:
   - **Separability-driven (recommended):** a **reciprocal coupled pair (Cat 2)** — the 1↔10
     separation was easy (very different substrates); the informative probe now is a category
     that shares MORE structure with a dot, to find where the boundary BLURS (HANDOFF §hypothesis).
     Substrate status PARTIAL (`two_temp_ou` is 2 coupled OU but exposed as single-relax+X; want
     a clean *reciprocal* 2-node) — check substrate readiness before authoring.
   - **Breadth:** **Queueing — `mm1_queue`** (Cat 9, exact ρ/(1−ρ)) — the last clean
     substrate-ready branch off the dots.
   - **Spend the owed sweep early:** the human may elect the v3 noise sweep now (v2 precedent —
     a legitimate top-level call), closing noise-independence directly.
3. `pose.py` → blind answerer (sanitized inputs only) → unseal (orchestrator-side; anchor-and-
   assert where geometry allows) → grade → evolve → commit per §6.

**The standing finding (updated).** Two categories now landed clean and blind; the current /
two-frame sector is demonstrated, not just cage. The separability hypothesis is *encouraged*
(1↔10 sharp on the cross-correlation asymmetry) but the easy cross-category test proves little —
the real test is a structurally-adjacent pair (Cat 2). The symmetric-boundary rule (WORKFLOW §4)
is the session's load-bearing method gain: it removes author discretion over difficulty, so a
MISS now means conform broke, not under-provisioning. The answer-key safeguard (freeze-computed
seal) stays in force — it is what kept v3's key honest.
