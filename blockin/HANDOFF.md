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
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. RECLASSIFIED 2026-05-25: verdict-lens inversion is a VIEWER-LAYER concern (researcher utility-lens over the computed band), NOT a teeth-defect → deferred to docs/deferred-for-auditor.md Entry 1, NOT re-posed as v3. earned/.
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
is *authorable*, not done. With v2's finding deferred to the viewer layer (no v3 re-pose —
see baton), the standing move is a **fresh category** off the two Vertex dots: the next clean
branches (unrun, substrate-ready) are **Queueing (mm1_queue, Cat 9)** and **Non-Reciprocal
(banach_frustrated, Cat 10)** — both also diversify the ledger the separability hypothesis (§4)
needs. The GAPs (3, 4, 6) need a clean-truth substrate *built* before they're even authorable —
that, not question count, is the runway limit.

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

## Pick up here (end of session 2026-05-25, 2nd entry)

**State — v2's finding RECLASSIFIED to the viewer layer; a grown deferral doc scaffolded.
No v3 authored (the SHARPEN re-pose was the wrong move — see below).**

1. **The audible (this session).** The standing move was "author v3 (SHARPEN): re-pose the
   pump sweep with the health metric pinned." The human called it, and broadened it: v2's
   verdict-inversion is **not a conform teeth-defect** to fix by pinning a metric — and it is
   **not the viewport "fixing" anything either** (the viewport is *inert by design* — it
   infers nothing). "Healthiest" is a researcher **interpretive choice** laid over a band
   conform *already computed correctly* (both runs agree on the per-curve reads + band shape).
   The framework's job is to **present** the computed structure and **expose** legitimate
   interpretive choices as researcher **dials/buttons**; the reading **lags** the researcher's
   settings — it is never *led* by a verdict baked upstream. **Generalize:** the interpretive
   questions the apparatus keeps bringing to the human — which axis to collapse, what sign to
   read a quantity with, which lens defines "healthy" — are candidate dials. If a choice can be
   *reasonably and honestly* handed to the researcher, that is where it ends up. **The
   detector:** a verdict the *freeze cannot compute* is the tell that the choice is a dial, not
   conform's call (the answer-key safeguard run in reverse). Agreed: defer as a dial, don't
   re-pose, don't have the viewport infer.

2. **Scaffolded this session (the deferral).** New grown doc
   [`docs/deferred-for-auditor.md`](../docs/deferred-for-auditor.md) — **researcher dials
   (interpretive DOF → viewport controls)**, picked up at the auditor pivot. Its governing
   principle is *present, expose, lag* (the viewport presents structure + exposes dials, never
   leads or infers) + the freeze-cannot-compute **detector**. It carries a growing **candidate
   dials** catalogue (lens/metric = Entry 1; collapse-axis + sign/interpretation convention =
   candidates) and the worked Entry 1 (conform emits the band over candidate metrics, not a
   baked winner; the viewport exposes the lens as a dial that highlights the researcher's
   reading). **New structure (this session, 2nd audible):** each entry now carries a
   **provisional, non-binding integration proposal** (control type · scope · audience ·
   frequency-prior · coupling · this-session's-why) — capturing the surfacing session's
   perishable UI context — plus a **"UI shape (precipitating)"** section that accretes the
   taxonomy by accumulation (categories + heatmap are NOT known yet; proposals carry priors,
   not data; since the viewport is inert all dials are presentation toggles, so placement is
   ergonomics not compute). **Two-tier discipline (this session, 3rd audible):** an *entry* is
   born only from a vertical surfacing the choice with real context (proposal earned); a thin
   *watch-list* (name + one-line suspicion, no proposal/placement/status) just keeps a suspicion
   from being lost — no pre-creation, no getting ahead. Scale Intents, collapse-axis, sign
   convention sit on the watch-list (Intents carries the open prior: dial vs question-derived).
   Threaded through the four block-in modules: **PIPELINE §5** (the [CONTACT] note
   points the verdict-layer at the deferral, keeps the mechanical groundability as conform's),
   **WORKFLOW §6** ("researcher-dial carve-out" guard + the detector), **meta-SOP §2**
   (escalation outcome + detector-in-reverse), and the **v2 ledger line** above (RECLASSIFIED
   tag). README pointer too (see coordination note).

3. **Preserved, NOT deferred.** The *mechanical* two-sided-headroom groundability (conform
   reads both walls of a non-monotonic band from a stitched-placement sweep) is a real
   READOUT result v2 showed. Whether it promotes to `[EARNED]` once carved free of the
   verdict lens is a **gated call parked** (PIPELINE §5) — not taken this session.

**Coordination state.** This session's block-in edits (the deferral doc + the four-module
reclassification touches) are **un-committed as of writing** — commit scope is `blockin/**`
+ the new `docs/deferred-for-auditor.md` (a new untracked file, cleanly stageable on its
own). **README.md is entangled:** it already carried *uncommitted* edits from the
out-of-block-in consolidation arc (cdv1→mpav1; it still says `laser_ro_threshold_v2`,
pre-dating the pump_sweep rename). My one-line README pointer was added on top of that soup
and is **deliberately left unstaged** — do not bundle README into a block-in commit; it
belongs to the consolidation arc's eventual commit. **Out-of-block-in drift, NOT ours:** the
five-vector-inversion WIP (2026-05-22) in `conformer/compute/`, `conformer/cli.py`, `docs/`
(other files), `scripts/`, `CLAUDE.md` — separate arc; do not touch or bundle. `questions/`
is **empty**. **One writer at a time.**

**Next move (next round) — a fresh-category vertical, gated:**
1. meta-SOP §0 reconcile — `questions/` empty; v2 in `earned/` (graded + reclassified);
   confirm the deferral doc + reclassification touches committed; the out-of-block-in WIP
   (incl. README) still uncommitted (expected, recorded above).
2. **Author the next vertical** (author-subagent, non-blind, **gated**). Two Vertex dots are
   on the ledger; the separability hypothesis (§4) needs **category diversity**, so jump
   category to a clean substrate-ready branch: **Queueing — `mm1_queue`** (Cat 9, exact
   stationary ρ/(1−ρ)) or **Non-Reciprocal — `banach_frustrated`** (Cat 10, exact 3-mode
   current / affinity / TUR — this one finally lights the k_frust / two-frame sector that
   Vertex structurally cannot). Either is a clean known-answer round-trip. `sealed_answer`
   **freeze-computed, not prose-asserted** (the standing answer-key rule — meta-SOP §2 — that
   caught v2 and stays in force).
3. `pose.py` → blind answerer (reads the sanitized traversal) → unseal (anchor-and-assert
   orchestrator-side) → grade → evolve → commit per §6.

**The standing finding (updated).** v1's two-sided-headroom gap is *mechanically* closed by
the sweep; the **value-ranking on top of it is a viewer concern** (deferred — Entry 1), not
an owed conform question. The answer-key safeguard (sealed verdict must be freeze-computed)
is what surfaced it and stays a standing conform rule. Net: the "pin the health metric"
owed-item is **retired** (it was pointing at the wrong layer); the conform-side escalation
already met its mechanical aim. Cross-repo follow-up (optional, not done): a one-line dated
pointer in `mpa-central/DEFERRED.md` under the auditor group → `docs/deferred-for-auditor.md`,
for discoverability at the pivot (separate repo, separate commit — surface to the human).
