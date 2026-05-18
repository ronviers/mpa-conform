# Three-solver block-in

Established 2026-05-17 after the paired Mode B architecture validation
revealed that single-scalar substrate normalization is structurally
insufficient (see conversation residue + `project_cdv1_pre_hello_world`).

## The three solvers — distinct jobs, distinct repos

| Solver | Repo | Consumes | Produces |
|---|---|---|---|
| **mpa-solver** | `H:/mpa-solver` | substrate physics + protocol | substrate observations (the 60 library cells in `mpa-central/library/data/` live downstream of this) |
| **mpa-scale-solver** | `H:/mpa-scale-solver` | a `TranslationField` instance + canonical/substrate states | canonical-space runtime operations (`apply_translation`, `forward_sweep_invert`, `regime_at`, `gamut_classify`, `flow`, `intent_map`). **Runtime, not characterization.** |
| **mpa-lens-solver** *(new, this session, scaffolded as its own repo)* | `H:/mpa-lens-solver` | substrate observations (library cells) + cdv1 priors per substrate class + region of interest | a fitted `TranslationField` — the substrate's ICC profile |

Each solver's responsibility is closed; the boundaries are the load-
bearing distinction. The new solver is what RFC-S §4 names as the
`translation_field` of a `driver_profile`. The runtime apparatus to
*use* that field already exists in mpa-scale-solver; what's missing is
the apparatus that *produces* it from substrate observations.

## What we are explicitly NOT building

- A new substrate physics path. mpa-solver covers it.
- A new canonical-space runtime. mpa-scale-solver covers it.
- Anything in `mpa-central/library/`. Library stays raw, batch-ground,
  v1.0 — per `project_two_shots_scale_managed`. Substrate data is static.
- Extensions to `mpa-scale-solver`'s seven-op surface. The solver
  *consumes* mpa-scale-solver's `TranslationField` type as output shape.
- EXR sequences, particle rendering, anything visual. The solver returns
  a data structure. Rendering is downstream
  (`conformer/shot/library_sequence_shot.py`).

## Why "real-time LUT"

The LUT (the `TranslationField` instance) is **regenerated per shot**
(per camera region of interest in canonical space), not baked into the
library.

- Substrate observations: static, ship with the library.
- Translation field: dynamic, produced for the current shot.
- Camera position / framing: scale management's job
  (`mss.gamut_classify` picks the canonical region; the solver fits the
  field for that region).

Not "real-time" in the per-frame rendering sense. "Real-time" in the
sense of *"produced for the current view, not shipped in advance."*
On-demand-per-shot. Display color management analog: ICC profiles
characterized per display unit at calibration time (not on every refresh,
not at the factory) and applied at every refresh thereafter.

## End-to-end flow with all three solvers in place

```
mpa-solver                            (substrate physics, batch)
     ↓
mpa-central/library/data/             (60 cells, static, v1.0)
     ↓
translation-field-solver              (mpa-conform, on-demand per shot)
   inputs:  substrate cells + cdv1 priors per substrate class
            + region of interest in canonical space
   output:  TranslationField (LUT shape v0; tangent-flow / learned later)
     ↓
mpa-scale-solver runtime              (apply_translation,
   apply_translation, forward_sweep_invert)        forward_sweep_invert)
     ↓
canonical (chit, γ_AB) per cell at any τ_obs
     ↓
conformer/shot/library_sequence_shot.py   (paired Mode B render)
     ↓
EXR sequences (real substrate + cadence-matched Banach)
     ↓
DJV scrub
```

## Where the new solver lives

- **Repo**: [`H:/mpa-lens-solver`](../../mpa-lens-solver) (its own repo,
  matching mpa-solver and mpa-scale-solver). Sibling, not nested.
- **Module entry point**: `mpa_lens_solver.fit_translation_field(substrate,
  cells, xdot_kind) -> mpa_scale_solver.TranslationField`
- **Block-in** (trajectory): [`H:/mpa-lens-solver/docs/BLOCK_IN.md`](../../mpa-lens-solver/docs/BLOCK_IN.md)
  — modeled on mpa-scale-solver's v2→v6 block-in pattern. v0 → v0.2 →
  v0.3+ trajectory.
- **Used by mpa-conform**: `conformer/shot/library_sequence_shot.py`
  replaces the current per-cell `_invert_cell` saturation with a single
  field-driven canonical-state derivation, importing
  `from mpa_lens_solver import fit_translation_field`.
- **Imports from mpa-scale-solver**: `TranslationField`, `TranslationRule`,
  `OperatingPoint`, `CanonicalPoint` (output types). Optionally
  `apply_translation`, `forward_sweep_invert` (when the round-trip
  validation move lands at v0.2).
- **mpa-conform's role**: consumer only. We do not write the solver
  here; we import it. mpa-conform's `driver_profile_builder.py` will be
  updated (later) to consume the solver's `TranslationField` for the
  driver profile's `translation_field` block instead of its current
  degenerate lookup of canonical seeds.

## Versioning

- **v0** (next session): cdv1 priors only, no fitting against substrate
  observations. Output is a `lookup_table`-shape `TranslationField` with
  one rule per (operating_point, xdot_choice) populated by the per-substrate
  cdv1 rule (`chit = Tc - T` for glass; `chit = ln(p_threshold/p_base)`
  for QEC; scenario table for brain). γ_AB held at a default until phase-
  locking observable plumbing lands.
- **v0.2**: round-trip validation per RFC-S §5. For each cell, project
  the canonical state forward through the field via `apply_translation`,
  compare to the cell's emitted (C, χ). The residual quantifies the
  substrate fingerprint relative to cdv1 prior.
- **v0.3+**: field-shape upgrades — `tangent_flow` (RFC-S Appendix B
  item 1) or `learned` MLP (mpa-scale-solver v3 `LearnedField`), with
  parameters fit by minimizing the round-trip residual across cells.
  This is where the solver actually starts *solving* (vs. just stamping
  priors).

## What this block-in commits to

1. Three-solver split is load-bearing. The translation-field solver does
   not creep into substrate physics (mpa-solver) or canonical-space
   runtime (mpa-scale-solver).
2. Library stays static. Re-grind is a separate concern from this work.
3. EXR rendering is downstream of the solver, not part of it.
4. The cdv1 priors are the v0 anchor. The substrate-side characterization
   work (fitting fields against observations) is sized into v0.2+ moves,
   not v0.
