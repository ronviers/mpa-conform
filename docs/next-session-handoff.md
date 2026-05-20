# Next-session handoff — mpa-conform

**Disposable. Regenerated each session.** Carries the baton: what just
shipped, what one next move to pick up.

## What's shipped this session (2026-05-19, second pass)

**Cross-substrate diagnostics + chi-convention lock-in.** After the
v0.4 schema landing earlier in the same session, two cross-substrate
diagnostics validated the apparatus:

- **QEC transfer test** (`scripts/test_kww_qec.py`): glass-KWW does
  NOT transfer to QEC at p_base=1e-3 (correct per RULES §7's hierarchy-
  direction inversion). But the framework's 1-param chit fit landing in
  the r-regime DOES correctly read QEC's C ≈ 0 behavior. Framework
  partial-transfer working as designed.
- **Brain transfer test** (`scripts/test_kww_brain.py`): KWW form
  *does* transfer to brain at suspended/velocity with re-tuned
  parameters (C RMS 0.305 → 0.065, factor of 5 reduction). The C-axis
  apparatus is more universal than expected: shape transfers, parameter
  values are substrate-specific.
- **Chi-axis structural finding**: chi/dC ratio varies by 32× across
  brain's cells, factor of ~13 off scale on QEC. No scalar
  normalization brings non-glass substrates onto the FDT line. The
  chi-axis is structurally substrate-conditional in a way the C-axis
  is not.

**Chi-convention lock-in shipped.**
- `observable.metadata.chi_convention` declared per substrate
  (glass=fdr_dimensionless; brain=substrate_emitted_uncalibrated;
  quantum=substrate_emitted_uncalibrated).
- `chi_convention_note` carries paragraph-long rationale per substrate.
- `banach_overlay` reads the convention: full-opacity model curves when
  chi is canonical (glass); pale-gray with yellow callout box when chi
  is uncalibrated (brain, QEC).
- C-panel y-limits clamped to empirical + model curves (the per-window
  fan no longer dominates autoscale on substrates where trail-vector
  observables have a different natural range).
- All 60 cells re-extracted; production PNGs re-rendered.

**Lock-in doc:** [`docs/papers/chi_convention_lock_in.md`](papers/chi_convention_lock_in.md)
— theory, evidence, candidates for per-substrate normalization,
architectural slot, what's owed.

## What's shipped earlier this session (2026-05-19, first pass)

**v0.4 schema landed.** Two coupled changes, both load-bearing:

1. **Lag/display separation.** `observable.data[].tau` is now the
   framework-canonical lag (= `sample.dt` = sample-time minus t_w).
   `observable.data[].display_tau` is the substrate-community display
   convention (= `sample.t` for glass-CK). Model evaluates at lag;
   viewers render the x-axis at display_tau. Decouples the model's
   internal time variable from the plot's x-axis — these were
   conflated under one field name in v0.1–v0.3.
2. **KWW + FDT-violation glass apparatus.** New
   `gfdr_model.generate_kww_glass_locus(chit, q_EA, tau_alpha,
   beta_KWW, tau_beta, X, T)`. Classical Kohlrausch–Williams–Watts
   two-timescale C(τ) plus Cugliandolo–Kurchan FDT-violation X(C). Per
   RULES §10 (inherit substrate vocabulary) and §15 (substrate
   deviation from cdv1 is the API surface). 5-vector substrate-
   thermodynamic refinement of the cdv1 leading-order chit.

**Diagnostic proof.** Hand-tuned KWW on `glass__T0.500__spin-flip`:
C RMS 0.201 → 0.025 (8×), χ RMS 0.287 → 0.073 (4×). Both at SEM-bar
scale. The hairpin in the t-axis display becomes a *predicted* feature
of the model curve, not an unmatched cluster of empirical points.
Receipt: [`output/diagnostics/kww_glass_test__T0.500__spin-flip.png`](../output/diagnostics/kww_glass_test__T0.500__spin-flip.png).

**Production re-extraction.** All 60 mpa-central library cells
re-extracted to v0.4: 22 ck-glassy, 22 surface-code-qec, 16
neural-population. Three driver profiles regenerated. Bundle's
`tau` values now start at sample.dt = 1 (lag) instead of sample.t =
501 (sample-time). All downstream fits recompute.

**Paper for review.** [`docs/papers/lag_display_kww_extension.md`](papers/lag_display_kww_extension.md)
— theory, implementation, results, RULES connections, deferred items,
6 review questions. Outbound review requested.

## Files touched

- `conformer/compute/gfdr_model.py` — `generate_kww_glass_locus` added
- `conformer/curator/walk_library.py` — `_extract_observable` lag/display split + metadata
- `schema/declaration-bundle.v0.4.json` — schema bump (forward-compat over v0.3)
- `conformer/compare/banach_overlay.py` — load/render lag/display split + glass cdv1-prior fallback
- `scripts/test_kww_glass.py` — standalone diagnostic
- 60 bundles re-extracted to `output/seed-corpus/`
- Production comparisons re-rendered to `output/comparisons/`

## Current state of the suite

| Repo | State |
|---|---|
| **mpa-conform** | **v0.4 schema landed (lag/display + KWW glass apparatus). Curator path stable on v0.4. banach_overlay uses cdv1 prior fallback for KWW visualization.** |
| mpa-lens-solver | v1.2 + bootstrap dispatch (2026-05-18). 1-param chit only. **Owes**: 6-vector predictor-corrector. |
| mpa-scale-solver | v1.0.0 (2026-05-16). 1-param BanachSubstrate. **Owes**: vector canonical state for the 6-vector. |
| mpa-central library | 60 cells stable (unchanged this session). Calibration baselines at `H:/mpa-central/library/baselines/` are **stale** (computed against v0.3 bundles). |
| mpa-auditor | Still reads CSV. Bundle ingestion not yet wired; v0.4's `tau` will appear as lag when it lands. |
| mpa-atlas | Unchanged. Thin-RFC discipline preserved. |

## Library-expansion structural lock-in (also this session)

**Two homes for substrate primitives, by design:**

- **External H:\ repo** (existing: mpa-brain, mpc-glass, mpc-quantum) — substrates with non-trivial dependencies, per-repo discipline, citable standalone artifacts. Explicit entry in `grind_library.py::SUBSTRATE_PATHS_EXTERNAL`.
- **In-library primitive** (`H:/mpa-central/library/primitives/<name>/`) — thin adapters that read public datasets. **Auto-discovered** by the grinder; no edit needed to add one. Drop in `__init__.py` + `measurements.py` + `data_loader.py` + `README.md`.

The grinder gained `discover_in_library_substrates()` and `all_substrate_names()`; sys.path injection handles both homes. `LIBRARY_SPEC.md` documents the two-home pattern; `primitives/README.md` documents the per-primitive layout, the promotion-to-own-repo criteria, and the expected workflow for new datasets.

**Why this matters:** new substrates from public datasets won't bloat H:\ root with one repo each. Adding one is "create folder, add 3 files, run grinder, run conform." The outbound-research dataset-acquisition workflow (separate ask, prompt drafted this session) consumes this structure.

## Files touched this session (cross-substrate + chi-convention)

- `scripts/test_kww_qec.py` — QEC cross-substrate diagnostic (standalone)
- `scripts/test_kww_brain.py` — brain cross-substrate diagnostic (standalone)
- `conformer/curator/walk_library.py` — `_chi_convention_for(substrate)`, `_chi_convention_note_for(substrate)`, observable.metadata extensions
- `conformer/compare/banach_overlay.py` — ComparisonData.chi_convention, pale-rendering path, yellow callout, `_y_limits_from` clamping
- 60 bundles re-extracted with the new metadata
- Production PNGs re-rendered (ck-glassy, neural-population, surface-code-qec)
- `docs/papers/chi_convention_lock_in.md` — new lock-in document
- `H:/mpa-central/RULES.md` — Rule 16 added (lag/display separation, earlier in session)
- `output/diagnostics/kww_qec_test__p1e-03__detection-event.png` — QEC diagnostic receipt
- `output/diagnostics/kww_brain_test__suspended__velocity.png` — brain diagnostic receipt
- `H:/mpa-central/library/grind_library.py` — SUBSTRATE_PATHS_EXTERNAL split, in-library primitive auto-discovery
- `H:/mpa-central/library/LIBRARY_SPEC.md` — two-home pattern documented
- `H:/mpa-central/library/primitives/README.md` — per-primitive layout + workflow

## Open: deferred follow-ons

Each is a single session's work. Order is up to the user; they are
mostly independent.

### Brain χ-normalization lookup (NEW, top priority)

Per [`chi_convention_lock_in.md`](papers/chi_convention_lock_in.md) §3.1
and §6: identify what brain's neural-population primitive emits as χ
and the canonical-form mapping. The chi-convention slot is ready to
receive it. Candidates (hypotheses from the data, not declarations):
integrated-response normalization, time-extensive normalization, or
bookkeeping-of-a-different-observable. Resolves brain's chi-axis.

### QEC χ-normalization lookup (NEW, also top priority)

Per [`chi_convention_lock_in.md`](papers/chi_convention_lock_in.md) §3.2
and §6: identify the surface-code chi convention. Most likely
hypothesis is Poisson-statistics normalization
(χ_canonical = χ_emitted / sqrt(p_base · dt) or similar); testable
from existing cell data alone — fit `χ ~ a + b·sqrt(p_base·dt)` across
QEC cells and see if a is small and b is constant. Resolves QEC's
chi-axis.

### 6-param inversion (`inversion.invert` extension)

Fit the substrate-thermodynamic 6-vector (chit + q_EA, τ_α, β_KWW, τ_β, X)
per cell using the v0.4 bundle's lag-anchored data. **Should wait until
at least one non-glass chi-normalization lands** (otherwise X — the
FDT-violation ratio — can't be meaningfully fit on non-glass substrates).
Two viable shapes:

- Analytical two-stage similar to v0.2: anchor chit via cdv1; refine
  the 5 glass params via a numerical inner stage (Levenberg-Marquardt
  or similar) constrained by the cdv1 prior's neighborhood.
- Predictor-corrector vector form (mirror lens-solver's machinery
  extended to 6 dims).

Until this lands, bundles carry the substrate-default cdv1 prior
in banach_overlay's render-time fallback (not in the bundle itself).

### Lens-solver vector extension

`fit_translation_field` extends to fit the 6-vector. The current
predictor-corrector + adaptive bracket + regime-band guard architecture
generalizes naturally; main work is the substrate-conditional
`_BOOTSTRAP_SEED_RANGE_DISPATCH` extension to vector seeds. Cross-path
disagreement becomes |6-vector_two_stage − 6-vector_lens_prior| (norm
in chit-units, or per-component for fine-grained reading).

### Scale-solver BanachSubstrate vector state

`BanachSubstrate(chit_0, gamma_AB_0)` → `BanachSubstrate(vector_state)`.
`state_at(nu)` flows the full 6-vector through nu per the translation
field shape work named in
[`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../mpa-lens-solver/docs/CHARACTER_FRAMING.md).
v2 of mpa-scale-solver was already planned (JAX + differentiability +
N-mode); the vector extension lands cleanly there.

### Calibration baseline refresh

Sweep harness at `conformer/calibration/sweep.py` re-run after the
v0.4 re-extract. Per-substrate-per-path baselines under
`H:/mpa-central/library/baselines/<substrate>.json` regenerate.
Estimated 30 min on the existing hardware.

### mpa-auditor bundle-reader update

Auditor's `data-engine.js` swap from CSV to bundle ingestion. v0.4's
`tau` field reads as lag; `display_tau` (with fallback to `tau`)
drives the x-axis. Existing CSV path continues to work in parallel
until the swap lands.

### QEC and brain substrate-specific apparatus

Glass got KWW + FDT-violation in v0.4. QEC and brain each declare
their own 5-vector (or whatever-vector) substrate-thermodynamic
refinement in their own schema-bump session. Vocabulary lookups owed:
QEC's threshold-and-syndrome literature; brain's scenario-conditional
correlator literature. Each substrate's community has its own canonical
terms; RULES §10 says use them.

### Outbound research / ultrareview on the paper

[`docs/papers/lag_display_kww_extension.md`](papers/lag_display_kww_extension.md)
shipped this session; 6 explicit review questions in §7. Outbound
research channel + ultrareview pass requested.

## Don't

- **Don't try to "fix" the fits being slightly worse on v0.4.** The
  chit shift (e.g., glass T=0.5 two-stage chit 0.30 → 0.25) is the
  intended consequence of lag-anchored extraction; previous v0.3 fits
  were on the wrong tau axis. The new fits are *more honest*, not less.
  Future calibration sweeps will normalize against v0.4 baselines.
- **Don't bypass the 6-param inversion by hand-picking KWW params in
  bundles.** The substrate-default cdv1 prior in `banach_overlay`'s
  fallback is for visualization only. Bundles should carry the actual
  fitted 6-vector once the 6-param inversion ships.
- **Don't promote `display_tau` to a load-bearing fit input.** It is
  display only. The model always evaluates at `tau` (lag). Conflating
  these roles was the v0.3 bug; the v0.4 separation is structural and
  must stay so.
- **Don't rush an `lag`/`display_tau` schema rename.** The v0.4 field
  name `tau` carries lag for historical/backward-compat reasons. A
  v0.5 rename is a viable follow-on (review question 1) but unscoped
  this session.

## Open questions for the next session

- **What does the QEC analogue of (q_EA, τ_α, β_KWW, τ_β, X) look like?**
  Surface-code literature: threshold exponents, syndrome lifetimes,
  logical error rate scaling. The vocabulary is well-named (per Kitaev,
  Fowler, et al.); the 5-vector or so for QEC's substrate-thermodynamic
  refinement should land in a QEC-focused session.
- **Does the brain library yet have enough data shape for an apparatus
  declaration?** mpa-central's brain cells are scenario-table-defined
  per cdv1. The substrate-thermodynamic refinement (whatever the
  neuroscience community names it) may not have a clean cross-cell
  signature yet — worth checking before committing the schema.
- **Should the auditor render plots vs lag or display_tau by default?**
  Currently banach_overlay renders vs display_tau (sample-time, glass-CK
  convention). When the auditor lands bundle ingestion, the same
  choice falls to its `data-engine.js` rendering path. A per-substrate
  display convention field on the driver profile would let the auditor
  pick correctly per substrate.

## Status of ROADMAP.md

[`ROADMAP.md`](ROADMAP.md) §Status section is from 2026-05-18 (v0.3 +
calibration apparatus). Needs refresh to record v0.4 landing. Doing
that as the very next move before handing off; this handoff already
reflects the new state.
