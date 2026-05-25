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
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED** (v2 authored, unrun) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓ — *deep* |
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
has landed** — v1 (Vertex) — with v2 (Vertex) authored-not-run. So all our actual evidence is
one earned record in `earned/laser_ro_nominal_v1/`; everything else on this table is
*authorable*, not done. The next clean branches (unrun, substrate-ready) are **Queueing
(mm1_queue)** and **Non-Reciprocal (banach_frustrated)**. The GAPs (3, 4, 6) need a clean-truth
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

## Pick up here (end of session 2026-05-24)

**State — the four-module restructure and ALL SOP refinements are COMMITTED. The only thing
not committed is v2 (the next pass, untracked). What landed:**

1. **Four-module restructure** (PIPELINE=object / WORKFLOW=pass-SOP / meta-SOP=evolution /
   HANDOFF=baton; `PROTOCOL.md` dissolved into WORKFLOW+meta-SOP).
2. **Process refinements** harvested from the v2 test session and folded into the SOP docs
   — the meta-SOP working as designed (a pass taught the method):
   - WORKFLOW §1: "one operating point" → *smallest data unit that grounds the reading*
     (point for placement, sweep for headroom).
   - meta-SOP §2: the **escalation mechanism** — a `not_grounded[]` item recurring across
     passes promotes itself from "owed" to the default next vector. The SOP learns defaults
     from the ledger.
   - PIPELINE §2 SELECTION + Phase Interface: **I2 (sweep) admitted in dev** when built as
     stitched isolated placements.
   - WORKFLOW §4: blinding boundary extended to the **slug/filename** (token tripwire can't
     catch ambiguous tokens like "Q-band"; human-glance scans the slug) and the **CSV
     columns** (sanitize keeps numeric columns — no stray `r` column).
   - WORKFLOW §6: a **sweep is traversed as N isolated placements + one band readout**
     (isolation preserved; a MISS localizes).
   - WORKFLOW §5/P: **anchor-and-assert** (include an earned point as a sweep sample, assert
     it reproduces) + **confirm-vs-discover** (the sealed value-add must be earned, not
     re-described).
   - PIPELINE §5 READOUT: **regime-zero ≠ boundary-attained** (overdamped ω_RO=0 is not a
     KILL); read the invariant that stays finite near an asymptote (ζ_nat, not ζ_damped).
   - meta-SOP §0 + §6: **parallel-session / single-writer** rule + commit-bundling caution;
     a **backgrounded, auditor-aware commit** procedure (leans on the gitleaks pre-commit
     hook; safe radius = `blockin/`; never crosses the conform→auditor PR seam).
   - HANDOFF: a **substrate coverage map** (which of the 10 categories have a clean-truth
     substrate — the real runway ceiling; **READY ≠ landed**, only Vertex/v1 has landed).
   - meta-SOP §7 + view_header.py: the **result-image standard** (header band = question
     broken down + verdict + placement + grounded/not-grounded, over data-mapped boxes;
     a sweep adds a band box) + **timestamped naming** `view_<YYYYMMDD-HHMMSS>.png`, so
     results accrue into a library (= `earned/**/view_*.png`, no separate gallery).

**v2 is reframed, authored, and answer-key-reviewed — awaiting pose.** It is now
`questions/laser_ro_pump_sweep_v2/` (**untracked**): a 4-point pump sweep
r ∈ {1.01, 1.04, 2.0, 12.0} spanning the sluggish wall → Q-peak (r=2) → roll-off — the move
that *grounds* v1's two-sided-headroom `not_grounded[]` (the escalation above). The old
single-point `laser_ro_threshold_v2` was retired/subsumed (it is now curve 2). Sealed key
is computed from the Jacobian and **independently verified** (Q = 0 / 0.35 / 1.50 / 0.72;
peak at r=2; far wall ≈ r=39); blind packet clean (columns `curve,tau,C,chi`, NO r/pump
column). Reviewer verdict: **GO**.

**Coordination state.** The whole process arc is **committed** (restructure + all
refinements + coverage map + result-image standard; see `git log` for hashes). The **only**
uncommitted thing is **v2** (`questions/laser_ro_pump_sweep_v2/`, untracked) — the next
pass's artifact, committed when v2 runs. A test parallel session validated §0 on-entry
reconcile (cold resume read pending work as expected state, stopped at the human gate).
**One writer at a time.**

**Next move (next round) — v2 is the next pass:**
1. meta-SOP §0 reconcile — the process docs are committed; you'll find only v2 untracked
   (expected, recorded here).
2. `pose.py laser_ro_pump_sweep_v2` → blind answerer. **Brief the answerer** (WORKFLOW §6):
   place each curve independently first, then read the band; curve 1 is legitimately
   overdamped (ω_RO=0 — recognize it, don't force a ring or trip a NaN); assert curve 3
   reproduces v1's r=2 placement (ζ≈0.32, Q≈1.5).
3. Unseal & grade → evolve per meta-SOP (ledger line, accrete contours, pick next vertical)
   → commit per §6 (hook scans; `blockin/**` only).

**The standing finding is in flight.** Two-sided headroom (v1's `not_grounded[]`) is exactly
what v2's sweep grounds. If v2 MATCHes, the READOUT headroom buckle earns its `[EARNED]`
contour and the escalation mechanism is validated end-to-end. (The prod-grade alternative —
inject the analytic Banach Q(χ̂) band as the ROOT-OP reference via
`conformer/compare/banach_overlay.py` — remains; the sweep is the dev-path close.)
