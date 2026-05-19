# Next-session handoff — mpa-conform

**Disposable. Regenerated each session.** Carries the baton: what just
shipped across the suite, what one next move to pick up.

## What's shipped since this handoff last refreshed (2026-05-17 → 2026-05-18)

The handoff was last refreshed when lens-solver was only just scaffolded.
Since then, three sessions of work landed across two repos.

**Conform Session 6 — v0.3 schema + calibration apparatus.**
`declaration-bundle.v0.3` ships with `audit_delta` carrying
`fit_diagnostics` + `diagnostic_percentiles` + `cross_path_disagreement`.
Per-substrate baselines ([`conformer/calibration/baselines.py`](../conformer/calibration/baselines.py))
partition per `(substrate, path)` — known-good distributions of
`fit_diagnostics` values across `lens_solver_prior`, `lens_solver_bootstrap`,
`two_stage_inversion` per substrate. Percentile lookup
([`percentile.py`](../conformer/calibration/percentile.py)) returns `None`
for new substrates → raw inspection fallback. Cross-path agreement
([`cross_path.py`](../conformer/calibration/cross_path.py)) gives
`|chit_two_stage − chit_lens_solver_prior|` in chit units, scale-free by
construction. Sweep harness ([`sweep.py`](../conformer/calibration/sweep.py))
re-runnable as the algorithm or library changes.

Self-improving loop: new substrate added → automatic sweep on its cells →
baseline JSON written to `H:/mpa-central/library/baselines/<substrate>.json`
→ all subsequent fits get percentiles automatically. No human picks
thresholds per substrate. The library IS the calibration set.

**The salvage came after five attempts at a single calibration-free
per-fit confidence scalar all failed structurally**: raw thresholds (v1
diagnostic vector), v2 normalized thresholds, statistical bootstrap σ,
Laplace σ, polished Laplace σ. Each attempt hit a different facet of the
same wall — the solvers' robustness mechanisms (regime guard, predictor
bracket, grid search, random-perturbation refinement) intentionally
produce fits that don't expose any single analytical structure to peg
confidence against. The salvage split the requirement into three
calibration-free primitives, each matching what the framework's
structure actually provides (per-substrate baselines absorb scale;
cross-path agreement is independent-paths disagreement in chit units;
raw `fit_diagnostics` ride along for forensics). Full framing at
[`docs/open_fit_confidence_framing.md`](open_fit_confidence_framing.md).

Outbound research dispatched today asking whether a calibration-free
framing exists in principle. **Not returned.** If it returns with a
workable framing, that's a v0.4 migration question — the v0.3 apparatus
is the current operating salvage.

**Lens-solver shipped externally** (history at
[`H:/mpa-lens-solver/README.md`](../../mpa-lens-solver/README.md) §Session Log):

- v1.0 — one-process architecture (predictor-corrector + adaptive
  bracket + regime-band guard). Collapsed BLOCK_IN's v0/v0.2/v0.3+
  ladder into a single shape.
- v1.2 — `FitDiagnostics` container (residual_final, regime_confidence,
  predictor_gap, source, n_passes) emitted per cell; `bootstrap=True`
  masks the cdv1 prior; the v0.3 calibration apparatus consumes this
  shape.
- Bootstrap dispatch (today, 2026-05-18) — `bootstrap=None` auto-
  dispatches per substrate (known substrates → cdv1 prior, unknown →
  bootstrap fallback) with substrate-conditional `_BOOTSTRAP_SEED_RANGE_DISPATCH`
  padded from each substrate's prior envelope. A fourth substrate now
  arrives in lens-solver with **zero code change** in lens or conform —
  the dispatch handles it.
- [`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../mpa-lens-solver/docs/CHARACTER_FRAMING.md)
  (today) — how the three cdv1-foundational substrates' character flows
  through lens-solver. Required reading before reasoning about the
  score function, TranslationField shape, or new-substrate onboarding.
  **Relevant to conform**: it names the QEC chi-scale question's
  long-term home as a TranslationField shape extension declaring
  observable conventions per substrate — NOT preprocessing in
  lens-solver, NOT per-substrate dial in conform's baselines. Until
  that trigger fires, v0.3 per-substrate baseline absorption is the
  correct present shape.

**API impact on conform: none.** All conform call sites
([`bootstrap_validation.py`](../conformer/calibration/bootstrap_validation.py),
[`cross_path.py`](../conformer/calibration/cross_path.py),
[`sweep.py`](../conformer/calibration/sweep.py),
[`library_sequence_shot.py`](../conformer/shot/library_sequence_shot.py))
pass `bootstrap` explicitly, so the default change is non-breaking. The
auto-dispatch only kicks in when a caller doesn't specify, which is the
new-substrate-arrival case the rollout was built for.

## Current state of the suite

| Repo | State |
|---|---|
| mpa-lens-solver | v1.2 + bootstrap dispatch (today); resting. Items 1 (score depth) and 4 (Rust+wasm port) wait on triggers that fire elsewhere. |
| mpa-scale-solver | v1.0.0 shipped (2026-05-16); v2 (JAX + differentiability + N-mode) next planned but independent of conform. |
| **mpa-conform** | **v0.3 schema + calibration apparatus shipped; curator path stable; researcher path scaffolded but not built; comparison display from Session 5 awaits the parallax move below.** |
| mpa-auditor | Bundle-import migration unblocked; not yet done. |
| mpa-central library | Refresh deferred per `H:/mpa-central/DEFERRED.md` (unnormalized quantum chi, zero-filled brain C/χ, null glass tau_env below Tc). |
| mpa-atlas | Thin-RFC framework work; cdv1 + RFC-S stable. |

## Single next move — surface parallax in the comparison display

Read the raw grind cell alongside the bundle in
[`conformer/compare/banach_overlay.py`](../conformer/compare/banach_overlay.py)
and draw the 31 per-window empirical traces as faint gray lines under
the aggregated empirical markers. Render one ck-glassy cell, look at the
PNG, then plan the move after that from what's visible.

This was Session 5's recommended next move and remains correct.
Session 6 (calibration apparatus) intervened because the open
fit-confidence question hit stop-the-line; the salvage is now in stable
v0.3 shape and nothing about Session 6 or the lens-solver work
since superseded the parallax lens (per
`project_mpa_conform_comparison_lens` memory: substrate parallax +
framework channel-richness + adapting-not-overfitting are what the
2-channel display strips; future comparison/sidecar work decides what
channels enter `substrate.observables`).

Per single-move discipline (memory: `feedback_single_move_design`):
one move, render, look at the PNG together, plan the move after that.
The options under "Deferred" below are context, not commitments.

## Deferred

- **Researcher path first slice** — biggest unshipped item per ROADMAP
  §Next up. Bring-your-own-model CLI: `mpa-conform researcher
  <upload.csv>` → interactive declaration prompts → signed bundle.
  Blocked on nothing technical; deferred pending whether parallax
  surfacing reveals a comparison-display priority that wants attention
  first.
- **v0.2 signing** — Ed25519 + BLAKE3 + JCS + DSSE-around-in-toto.
  v0.1 schema declares these as forward-compat. Independent track.
- **Audit classification port** — mirror Session 1's inversion port for
  the auditor's audit-engine; lets bundles carry pre-computed
  `audit_delta`. Independent track.
- **Forward physics + framework-grid generator** — port character +
  discrete engines to Python; emit `framework-grid.v0.1.json` for the
  auditor's Explore/Browse mode. Independent track.
- **The correlator** — port `multipletau` blocking algorithm to Rust →
  WASM. Blocked on researcher path needing raw time-series.
- **Library refresh** — mpa-central territory, not this repo.
- **Outbound research on calibration-free framing** — passive wait. If
  it returns, may inform a v0.4 schema and a salvage migration.
- **Sibling doc pointers to CHARACTER_FRAMING.md** — `mpa-conform/CLAUDE.md`,
  [`docs/SOLVERS_BLOCK_IN.md`](SOLVERS_BLOCK_IN.md), and
  `H:/mpa-central/SYSTEM_OVERVIEW.md` §3 all describe lens-solver and
  could cite the framing doc. Small additive sweep, not stale-fix.
  Worth doing in the same session as the parallax move if cycles allow.

## Don't

- **Don't reintroduce QEC chi normalization as preprocessing** in
  conform's curator or lens-solver. The right long-term home is a
  TranslationField shape extension declaring observable conventions
  per substrate (per
  [`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../mpa-lens-solver/docs/CHARACTER_FRAMING.md)
  §Observable conventions belong in TranslationField). Until that
  trigger fires, the v0.3 per-substrate baseline absorption is correct.
- **Don't try a sixth per-fit confidence metric.** The wall is real;
  five attempts characterized it; the three-primitive salvage is the
  operating shape. If outbound research returns a calibration-free
  framing, that's a v0.4 migration, not an in-place metric swap.
- **Don't refit in viewers.** Per [SUITE_BLOCK_IN](../../mpa-central/SUITE_BLOCK_IN.md):
  conform writes `fit_provenance`; auditor reads it.
- **Don't pre-build a new substrate's downstream apparatus.** The
  v0.3 calibration loop auto-engages when a substrate's cells arrive
  and a sweep runs. The lens-solver dispatch handles the fit. No
  pre-build needed.

## Open questions for the next session

- **Outbound research on calibration-free per-fit confidence framing**
  — sent today. No return yet. If returned, evaluate against the v0.3
  apparatus and decide v0.4 migration cost.
- **Parallax-surfacing aftermath** — Session 5's note said the parallax +
  channel-richness lens "drives next moves" but didn't commit to a
  specific channel decision. After this session's parallax move, the
  decision is: which channels (if any) earn promotion into
  `substrate.observables` schema?
- **ROADMAP.md staleness.** The ROADMAP's §Status section is from
  2026-05-17 and predates v0.3 + the calibration apparatus + the
  lens-solver work above. Not addressed in this handoff regeneration
  (handoff and ROADMAP are separate documents per the parallel-document
  discipline). Refresh as a small in-session task before the next move,
  or carry forward.
