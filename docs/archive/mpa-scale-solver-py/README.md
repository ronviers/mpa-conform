# mpa-scale-solver — Python reference (pre-build)

**Status:** v0 Python reference implementation. Not the shipping kernel.

**Purpose:** Validate the seven scale-solver operations against the framework's
primary cross-substrate test (cdv1 §gFDR signatures: chit reading of the s → r
migration) *before* a native (Rust / C++) build is committed. The downstream
build session inherits this code as the math oracle: same fixtures, same
inputs, same outputs.

## Authority chain

- **Spec:** `mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md` §§0–5
- **Framework anchors:** `v9_compressed.md` §Foundational principles, §Scale-relativity, §Compression Axiom
- **Load-bearing prediction:** `cdv1_compressed.md` §gFDR signatures (c → s → r migration)
- **Build bootstrap:** `mpa-scale-solver-bootstrap.md` (this package fills §5)

## What's here

```
mpa_scale_solver/
├── __init__.py        — public API
├── types.py           — dataclasses (CanonicalState, SubstrateState, ...)
├── operations.py      — the seven operations from bootstrap §4
└── synthetic.py       — synthetic driver profile + analytical truth

test_migration_visual.py   — end-to-end visual test (this is the main artifact)
test_sensitivity_check.py  — runs with a deliberate bug to confirm the test
                             catches errors visibly
```

## The seven operations

Per bootstrap §4, all stateless free functions on plain dataclasses:

| Op | Status | Notes |
|---|---|---|
| `apply_translation` | implemented | Trivial baseline + `aging_log` synthetic rule |
| `forward_sweep_invert` | implemented | Brute-force grid; returns residual field on request |
| `tau_obs_sweep` | implemented | Walks the trajectory at fixed substrate observation |
| `regime_at` | implemented | Chit-threshold cut: c / s / r |
| `gamut_classify` | implemented | Per-axis range checks; out-of-axis diagnoses |
| `intent_map` | I5 only | I1–I4 raise NotImplementedError (per §5 scope) |
| `validate_driver_profile` | I5 only | RFC-S §5 round-trip on a reference dataset |

## Running

```bash
cd /path/to/mpa-scale-solver-py
python3 test_migration_visual.py
```

Requires: Python 3.9+, numpy, matplotlib, OpenEXR.

## What the test does

1. Builds a synthetic driver profile (parametric `aging_log` rule):
   `substrate_chit = canonical_chit + a * log(1 + tau_obs / tau_aging)`

2. Picks a reference canonical state in the c-regime (chit = 2.0, gamma = -0.5)
   at tau_obs = 1.0. Computes the substrate observation at that frame.

3. Sweeps tau_obs across 80 log-spaced frames from 0.01 to 100. At each frame:
   - **Analytical** canonical chit: closed-form truth from the driver
     profile's known parameters (computed *without* the solver).
   - **Numerical** canonical chit: `forward_sweep_invert` recovers it from
     the substrate observation at that frame.

4. Compares the two. Tolerance: 0.01 (twice the chit-axis grid step).

## How to read the output

`out/migration_compare.png` (and `.exr`) — single static comparison.

- **Thick blue solid curve:** analytical truth.
- **Red dashed curve with markers:** what the solver computed.
- **Background bands:** c-regime (green), s-regime (yellow), r-regime (red).

**If the curves overlay, the math is right.** The numerical points sit on
top of the analytical line across the full c → s → r migration.

**If the curves miss, the math is wrong.** A diverging or crossing pair is
a sign error, an off-by-one in the grid, a unit confusion, or any of the
other small bugs that would happen during a native port. See
`out/broken_compare.png` for what a sign-flipped solver looks like — the
numerical curve goes up while the analytical goes down, crossing at the
reference point.

`out/frames/frame_NNNN.exr` (and `.png`) — 80-frame animation.

- Analytical curve drawn faintly across the full range.
- Numerical points drawn up to frame NNNN, building up as the sweep proceeds.
- Vertical playhead marks the current tau_obs.
- Info box shows numerical/analytical/residual/regime at the current frame.

Scrub through to see the migration unfold and verify the numerical tracks
the analytical at every step.

`out/result.json` — per-frame data: tau_obs, analytical, numerical, residual,
regime. For programmatic consumers and regression checks.

## Pass criterion

```
max_over_frames( | numerical_chit - analytical_chit | ) <= tolerance
```

The Python reference passes at residual = 0.005 (half a chit-axis grid step).
The native port must reproduce the same per-frame numerical values
(byte-identical, modulo IEEE-754 platform drift). Same fixture, same output.

## What's deliberately NOT in v0

Per bootstrap §5 deferral list:

- N-mode generalization (2-mode parallel with mpa-solver v0)
- I1–I4 intent operations (stubbed)
- Learned translation-field form (parametric + lookup forms enough at v0)
- Substrate-conditional auto-remap forms beyond the synthetic `aging_log`
  (real driver profiles live in `mpa-conform` curator/researcher path output)
- Sensitivity / gradient passes through the flow
- Non-trivial RG flow defaults in the solver (per revised §7.1: the solver
  ships the trivial baseline; driver profiles carry the flow content)

## Handoff to the build session

This Python reference is the math oracle. The build session ports it to
Rust or C++ + WASM + Python bindings; acceptance is "the native build
produces byte-identical (within IEEE-754 platform tolerance) per-frame
numerical values when fed the same synthetic driver profile, reference
canonical state, and tau_obs grid."

Test fixtures live in `out/result.json` and are mechanical to re-run against
any native implementation.
