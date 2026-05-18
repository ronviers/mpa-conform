# Next-session handoff — mpa-lens-solver v0

**Disposable. Regenerated each session.** Carries the baton: what just
shipped, what one next move to pick up.

## What just shipped (this session, 2026-05-17)

**Paired Mode B architecture validated end-to-end.**

Two paired-shot renders ran cleanly for QEC and glass:
- `conformer/shot/library_sequence_shot.py` — new self-contained orchestrator;
  paired (real-substrate + cadence-matched Banach) Mode B EXR sequences at
  1920×1080, 150 frames @ 30fps, c-end calibration to substrate c-end fit.
- `output/shots/paired_qec_detection-event/{real,banach}/` — QEC paired shot.
- `output/shots/paired_glass_spin-flip/{real,banach}/` — glass paired shot.

Architecture is correct (per `project_two_shots_scale_managed`); the
visible delta between real and Banach is genuine substrate fingerprint,
not artifact. See `project_cdv1_pre_hello_world` for the moment-naming.

**Diagnostic outcome — the inversion is the blocker, not the apparatus.**

Both substrates showed structural inversion saturation:
- QEC: 6/11 cells fit chit = -2.0 (grid floor); the substrate-emitted
  `chi/(1-C)` ratio is operating-point-dependent, so the single-scalar
  `scale_q` normalization is insufficient (no choice of scalar collapses
  the whole sweep onto the canonical locus).
- Glass: 9/11 cells fit chit = +0.175 (a centroid); cdv1 predicts
  `chit = Tc - T` should range +0.9 → -0.7 across the T sweep, but the
  inversion can't see the temperature signal at all.

Both diagnostics are the same shape in two modes: **the curator's inversion
treats substrate-native ≡ canonical (identity translation), which is true
only for Banach.** Real substrates need a substrate-class `translation_field`
(RFC-S §4) to map their emitted (C, χ) into canonical coordinates before
the inversion can fit. The mpa-scale-solver runtime to *use* a translation
field exists; the apparatus to *produce* one from substrate observations
does not. That apparatus is the next session's work.

**Architectural block-in landed; new repo scaffolded.**

- `H:/mpa-conform/docs/SOLVERS_BLOCK_IN.md` — three-solver split:
  mpa-solver (substrate physics) / mpa-scale-solver (canonical runtime) /
  mpa-lens-solver (substrate-class ICC profile characterization).
- `H:/mpa-lens-solver/` — new repo, scaffolded this session (its own
  repo to match mpa-solver and mpa-scale-solver patterns). README,
  CLAUDE.md, pyproject.toml, empty package, and the v0 → v0.3+
  block-in at `docs/BLOCK_IN.md` are in place.
- Settings.json updated to add `H:\\mpa-lens-solver` to
  `permissions.additionalDirectories` and `sandbox.filesystem.allowWrite`
  per the new-repo convention.

**Memory residue (this session):**
- `project_two_shots_scale_managed` — paired Mode B architecture + cadence-
  matching role of scale management
- `project_cdv1_pre_hello_world` — first paired QEC shot ran; apparatus
  works; hello-world gated on the mpa-lens-solver landing

## Single next move: mpa-lens-solver v0

**Very simple.** No EXR sequences, no rendering. Just a function in the
new `mpa-lens-solver` repo that takes `(substrate, cells, xdot_kind)` and
returns a `mpa_scale_solver.TranslationField` (lookup_table shape) seeded
with cdv1 priors per substrate class.

**The actual brief lives in
[`H:/mpa-lens-solver/docs/BLOCK_IN.md`](../../mpa-lens-solver/docs/BLOCK_IN.md)
§v0.** Read that first. The summary below is duplicated from there for
hand-off convenience; the BLOCK_IN is authoritative.

### Where it lives

```
H:/mpa-lens-solver/mpa_lens_solver/priors.py   (new — populate this)
H:/mpa-lens-solver/mpa_lens_solver/__init__.py (uncomment the priors re-export)
H:/mpa-lens-solver/tests/test_priors.py        (new — unit tests)
```

Imports types from mpa-scale-solver (`TranslationField`, `TranslationRule`,
`OperatingPoint`, `CanonicalPoint`). No rendering, no IO, no LLM. Pure
function from cells → field.

### v0 scope — cdv1 priors only

| Substrate | Operating point axis | Canonical chit prior | Source |
|---|---|---|---|
| Glass | `T` | `chit = Tc - T` (with Tc = 1.1) | cdv1 §gFDR signatures; resolved per Q-glass-chit-sign |
| QEC | `p_base` | `chit = ln(p_threshold / p_base)` (with p_threshold = 1e-2) | cdv1 §Surface-code identification; ln(G_0/L) chit definition |
| Brain | `scenario` | scenario table: committed=+0.6, suspended=+0.1, conflict=0.0, reset=-0.5 | hand-calibrated from cdv1 regime descriptions; may need user adjudication |

γ_AB held at `-0.3` for all cells (default — phase-locking-r observable
plumbing is a separate move). `k_frust = False` everywhere.

### Output shape

A single `TranslationField` per `(substrate, xdot_kind)` pair, of shape
`lookup_table`:

```python
TranslationField(
    direction="forward",
    shape="lookup_table",
    description="cdv1-prior canonical states per operating point. v0: no fitting.",
    rule=[
        TranslationRule(
            operating_point=OperatingPoint(label=..., axes={...}, gt=...),
            xdot_choice=xdot_kind,
            canonical=CanonicalPoint(
                chit=cdv1_prior_chit(substrate, op),
                gamma_AB=-0.3,
                k_frust=False,
                method="cdv1_prior_v0",
            ),
        )
        for op in cells
    ],
)
```

### Surface

```python
def fit_translation_field(
    substrate: str,
    cells: list[dict],
    xdot_kind: str,
) -> TranslationField:
    """Produce a substrate-class TranslationField from library cells + cdv1 priors.

    v0: no fitting; applies cdv1 substrate-class rule per cell's operating point.
    """
    ...
```

### Wiring into the existing renderer (one-block change)

In `H:/mpa-conform/conformer/shot/library_sequence_shot.py`, replace
the per-cell `_invert_cell` call (which saturates) with:

```python
from mpa_lens_solver import fit_translation_field

field = fit_translation_field(substrate, cells, xdot_kind)
substrate_states = [
    CanonicalState(
        chit=rule.canonical.chit,
        gamma_AB=rule.canonical.gamma_AB,
        k_frust=rule.canonical.k_frust,
    )
    for rule in field.rule
]
```

The cdv1-prior states feed straight into the existing emitter placement.
Banach c-end calibration logic stays as-is — it'll now calibrate to the
cdv1-predicted c-end (e.g., chit_0 = +0.9 for glass T=0.20) instead of
the saturating inversion's +0.175. Banach's analytical decay then has
room to traverse the full s_critical band, and the paired shot can
actually show a c→s→r migration.

### What "done" looks like for v0

1. `mpa-lens-solver/mpa_lens_solver/priors.py` ships with the three
   substrate priors; `tests/test_priors.py` passes.
2. `library_sequence_shot.py` in mpa-conform rewired to import from
   mpa-lens-solver.
3. QEC and glass paired shots re-rendered; canonical trajectories now
   span the cdv1-predicted chit range (not saturated).
4. Look at the PNGs. If the c→s→r migration reads in the real-substrate
   shot with Banach overlay riding alongside — **that's character's hello
   world**.

## Deferred to v0.2 and beyond

- **Round-trip validation per RFC-S §5.** For each cell, project the
  cdv1-prior canonical state forward through the field via
  `apply_translation`, compare to the cell's emitted (C, χ). The residual
  IS the substrate fingerprint quantification.
- **Field-shape upgrades.** When cdv1-prior + residual reveals systematic
  deviation, upgrade to `tangent_flow` (RFC-S Appendix B item 1) or
  `learned` MLP (mpa-scale-solver v3 `LearnedField`); fit parameters by
  minimizing round-trip residual across cells.
- **Phase-locking r plumbing.** Compute or stub `scalar_observables.
  phase_locking_r` per cell to unblock γ_AB variation across the trajectory.
- **driver_profile_builder.py update.** Use the solver's `TranslationField`
  as the profile's `translation_field` block instead of the current
  degenerate canonical-seed lookup.
- **Brain xdot_kinds + scenario adjudication.** The brain prior table is
  hand-calibrated; needs review against cdv1 and possibly empirical
  data.

## Don't

- **Don't add EXR rendering to the solver.** It returns a TranslationField.
  Period.
- **Don't fit against substrate observations in v0.** Priors only. Fitting
  is v0.2+.
- **Don't touch mpa-central/library.** v1.0 is correct; the substrate data
  is the input, not the variable.
- **Don't extend mpa-scale-solver's seven-op surface.** Use the existing
  `TranslationField` type as the output shape; no new ops.
- **Don't bump the EXR Channel Contract.** Library refresh is upstream of
  the EXR producer; this work doesn't touch channel emission.
- **Don't re-litigate the architecture.** `SOLVERS_BLOCK_IN.md` is the
  authority; if a question arises about where something lives, that doc
  answers it.

## Open questions for the next session

- Brain scenario chit priors are stab-in-the-dark; if the user has prior
  thoughts, ask. Otherwise ship with the table above and iterate from
  observation.
- p_threshold = 1e-2 for QEC is approximate (distance-3 surface code
  rotated memory-Z); if the user has a more authoritative value, use
  that. Otherwise the priors will still produce a non-saturated trajectory.
- Whether the renderer should also write `provenance_hash` /
  `validation_flags` data channels reflecting the field's provenance
  (currently both stubbed at `0.0` / `7.0`). Defer until v0.2 makes
  validation meaningful.
