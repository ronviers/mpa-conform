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

## Substrate reference  [evolves as contamination is found]
- seed substrates (clean ground truth, "our data"): class-B laser
  (mpa-central/library/{ro_damping_audit,laser_conform_Q}.py), kww_oracle,
  two_temp_ou, ou_equilibrium, Banach, driven_ring / banach_frustrated.
- HOLD (known-contaminated, do NOT seed from): unnormalized quantum chi, zero-filled
  brain C/chi, null glass tau_env (mpa-central DEFERRED.md library-refresh), and any
  conform-touched seed-corpus bundle (examinee output).
- conform pieces to quarry (as examinee, never answer key): conformer/compute/
  {inversion, gfdr_model, five_vector}.py.

---

## Pick up here (end of session 2026-05-24)

**State — two arcs landed this session, both on `blockin/`; NOTHING committed since c107171:**

1. **Four-module restructure** (PIPELINE=object / WORKFLOW=pass-SOP / meta-SOP=evolution /
   HANDOFF=baton; `PROTOCOL.md` dissolved into WORKFLOW+meta-SOP) — **staged**.
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
   - meta-SOP §0 + §6: **parallel-session / single-writer** rule + commit-bundling caution.

**v2 is reframed, authored, and answer-key-reviewed — awaiting pose.** It is now
`questions/laser_ro_pump_sweep_v2/` (**untracked**): a 4-point pump sweep
r ∈ {1.01, 1.04, 2.0, 12.0} spanning the sluggish wall → Q-peak (r=2) → roll-off — the move
that *grounds* v1's two-sided-headroom `not_grounded[]` (the escalation above). The old
single-point `laser_ro_threshold_v2` was retired/subsumed (it is now curve 2). Sealed key
is computed from the Jacobian and **independently verified** (Q = 0 / 0.35 / 1.50 / 0.72;
peak at r=2; far wall ≈ r=39); blind packet clean (columns `curve,tau,C,chi`, NO r/pump
column). Reviewer verdict: **GO**.

**Coordination state.** Restructure *staged*; v2 sweep *untracked*; no commit since c107171.
A test parallel session validated §0 on-entry reconcile (cold resume read both as expected
state, stopped at the human gate). **One writer at a time.** Before any commit,
`git diff --cached` — don't let `git add blockin/` silently bundle the restructure with the
v2 pass unless that's the intended coherent commit.

**Next move (next round):**
1. meta-SOP §0 reconcile — you'll find the staged restructure + untracked v2 (expected,
   recorded here).
2. **Commit shape (decide):** recommended — commit the restructure + SOP-refinements first
   as a *meta/process* commit (per meta-SOP §6 a restructure is not a pass commit), THEN run
   v2 as its own pass commit. (gitleaks scan, `blockin/**` only, `git diff --cached` first.)
3. `pose.py laser_ro_pump_sweep_v2` → blind answerer. **Brief the answerer** (WORKFLOW §6):
   place each curve independently first, then read the band; curve 1 is legitimately
   overdamped (ω_RO=0 — recognize it, don't force a ring or trip a NaN); assert curve 3
   reproduces v1's r=2 placement (ζ≈0.32, Q≈1.5).
4. Unseal & grade → evolve per meta-SOP (ledger line, accrete contours, pick next vertical)
   → commit.

**The standing finding is in flight.** Two-sided headroom (v1's `not_grounded[]`) is exactly
what v2's sweep grounds. If v2 MATCHes, the READOUT headroom buckle earns its `[EARNED]`
contour and the escalation mechanism is validated end-to-end. (The prod-grade alternative —
inject the analytic Banach Q(χ̂) band as the ROOT-OP reference via
`conformer/compare/banach_overlay.py` — remains; the sweep is the dev-path close.)
