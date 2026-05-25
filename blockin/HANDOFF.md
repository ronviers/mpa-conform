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
  smear across several? (Unanswered — testing by accumulation. Updated by the meta-SOP's
  cross-pass aggregation every ~3 verticals.)

## Vertical ledger  [append 1 line/pass; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. Re-pose v3 disambiguated (SHARPEN). earned/.
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
| 10 · Non-Reciprocal (current/k_frust) | **READY** | — | banach_frustrated ✓ (exact 3-mode current, affinity/TUR); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 3 categories are
READY (1, 9, 10), ~4 PARTIAL (2, 5, 7, 8), 3 GAP (3, 4, 6). *Work-wise*, **exactly 1 vertical
has landed a contour** — v1 (Vertex); v2 (Vertex) ran 2026-05-25 and graded MISS-with-finding
(a question-teeth defect, not a conform failure — see its RESULT), so it is documented in
`earned/laser_ro_pump_sweep_v2/` but landed no contour. So our landed evidence is still one
record (`earned/laser_ro_nominal_v1/`), plus one documented MISS; everything else on this table
is *authorable*, not done. The next clean branches (unrun, substrate-ready) are **Queueing
(mm1_queue)** and **Non-Reciprocal (banach_frustrated)** — though the standing move is v3, the
disambiguated re-pose of the Vertex sweep (see baton). The GAPs (3, 4, 6) need a clean-truth
substrate *built* before they're even authorable — that, not question count, is the runway limit.

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

## Pick up here (end of session 2026-05-25)

**State — v2 is GRADED + DEPOSITED; a blinding-fix to the apparatus landed alongside it.**
(The prior session's four-module restructure + SOP refinements shipped — see `git log`.)

1. **v2 graded MISS-with-finding (meta-validity P)** → moved to
   `earned/laser_ro_pump_sweep_v2/` (entry, freeze, data, packet, the blind answerer's
   `answer_fit.py`/`answer_view.py`/`verdict.md`/`view_*.png`, RESULT). The blind sweep
   reproduced **every placement, the band shape, and the v1 anchor** (curve 3 → ζ≈0.28 ≈
   v1's earned ζ≈0.32) — conform works, no cage_edge, no KILL. But the bottom-line
   "healthiest" verdict **inverted**: that word is not Jacobian-computed; it flips on a
   health-metric (response-crispness → curve 3, the seal; vs damping-margin → curve 2, the
   blind answerer) the packet never supplied. The seal's verdict was prose-asserted beyond
   what the freeze computes (the answer-key-safeguard seam). The question lacks **teeth**;
   the READOUT two-sided-headroom contour did **NOT** earn `[EARNED]` — though the
   *mechanical* groundability of two-sided headroom WAS shown. Full write-up in its
   RESULT.md; the standing finding (below) is updated accordingly.

2. **Blinding-fix landed (apparatus — authorized method change).** Two defects surfaced
   while posing v2:
   - `pose.py` `blind_half` matched `## SEALED` as a raw substring, so the entry's own
     header comment (which names the marker) split the packet **empty**. Fixed to match the
     divider as a section-header *line*.
   - The canonical blind read-path **leaked**: accretion had written the v2 answer +
     substrate names into `PIPELINE.md`, the doc the blind answerer is *required* to read
     (WORKFLOW §3). Fix: `pose.py` now emits a sanitized `workspace/<slug>.traversal.md`
     (strips earned/finding **blockquotes** + `[EARNED]`/`[CONTACT]` tags; fail-closes on a
     **substrate/answer** token set, distinct from the packet's method-vocabulary set).
     WORKFLOW §3 repoints the answerer at the sanitized traversal (raw PIPELINE.md now on
     the never-read list); the §5/P anchor leak ("v2's curve 3 = v1's r=2") scrubbed and the
     assert moved to **unseal-time, orchestrator-side**; meta-SOP §3 records the convention:
     **earned/finding/status notes live ONLY in blockquotes or `[EARNED]` tags**, so the
     sanitizer can strip them and the plain-text recipe stays substrate-neutral.

**Coordination state.** v2 + the blinding-fix are committed (`blockin/**` only; see
`git log`). `questions/` is **empty** (ready for v3). **Out-of-block-in drift, NOT ours:**
an older five-vector-inversion WIP (2026-05-22) sits uncommitted in `conformer/compute/`,
`conformer/cli.py`, `docs/`, `scripts/` — a separate arc; do not touch or bundle it. **One
writer at a time.**

**Next move (next round) — v3 re-author (SHARPEN), gated:**
1. meta-SOP §0 reconcile — `questions/` empty; v2 in `earned/` (graded). Confirm only the
   out-of-block-in conformer/ WIP is uncommitted (expected, recorded above).
2. **Author v3** (author-subagent, non-blind, **gated** — human glance clears the computed
   key). Re-pose the laser pump sweep with the health metric **disambiguated in researcher
   voice**: EITHER supply it ("I want a fast clean settle without overshoot" → damping-margin
   → curve 2; OR "I want the sharpest resonant response" → crispness → curve 3), OR pose a
   value-free verdict the data uniquely determines ("which curve rings most / settles
   slowest"). The `sealed_answer` must be **freeze-computed, not prose-asserted** — that is
   this pass's finding, baked into the next authoring.
3. `pose.py` → blind answerer (now reads the sanitized traversal) → unseal (do the
   anchor-and-assert here, orchestrator-side) → grade → evolve → commit per §6.

**The standing finding (updated).** v1's two-sided-headroom gap is *mechanically* closed by
the sweep — but the verdict it feeds is **metric-ambiguous**. The new owed item is **"pin the
health metric in the question."** If v3 MATCHes with the metric supplied, the READOUT contour
earns `[EARNED]` and the escalation mechanism is validated end-to-end. (The prod-grade
alternative — inject the analytic Banach Q(χ̂) band as the ROOT-OP reference via
`conformer/compare/banach_overlay.py` — remains; the sweep is the dev-path close.)
