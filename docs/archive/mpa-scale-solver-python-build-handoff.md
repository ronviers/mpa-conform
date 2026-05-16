# `mpa-scale-solver` — Python build handoff

**SHIPPED 2026-05-15.** Built per this handoff as `H:/mpa-scale-solver/`
Python v0.1.0 →
[github.com/ronviers/mpa-scale-solver](https://github.com/ronviers/mpa-scale-solver)
(commit `71cfb2a`). 59 tests pass; camera test max\|residual\| = 0.012 vs
tolerance 0.05; three seed-corpus profiles close round-trip. Kept here
as the build-time reference; live code is the repo, live spec is
`mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md`.

The native (Rust / C++) port is a future session and reads this handoff
plus the shipped Python.

---

**You are a fresh Claude Code session. This handoff is self-contained.**

**Your task:** build the Python implementation of `mpa-scale-solver` as a
shipping artifact, not as a reference. The Python implementation IS the v0
deliverable. A native (Rust / C++) port comes later, ports byte-identical
to this Python, and is its own session.

**Authority chain:**
- This document is the build authority. If it conflicts with the original
  `mpa-scale-solver-bootstrap.md`, this document wins (the bootstrap was
  the structural sketch; this is the build commitment).
- For specs: `mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md` §§0–5,
  `mpa-atlas/framework/v9_compressed.md`, `mpa-atlas/framework/cdv1_compressed.md`,
  `mpa-atlas/schema/driver-profile.v2.0.json`.
- For order of operations:
  `mpa-auditor/docs/foundational-answers.md` §Q13.
- For component boundaries:
  `mpa-solver/CLAUDE.md` (what observables live where),
  `mpa-central/SUITE_BLOCK_IN.md` (three-layer split).
- For porting sources: `mpa-auditor/math/gfdr-model.js` (canonical analytical
  forward model + regime classifier).

**First moves:**
1. Read this document end-to-end.
2. Read `mpa-auditor/docs/foundational-answers.md` §§Q12, Q13 (the order-
   of-operations + characterization-vs-calibration commitments).
3. Read `mpa-atlas/schema/driver-profile.v2.0.json` (the schema this
   solver consumes).
4. Skim `mpa-auditor/math/gfdr-model.js` (~80 lines; the canonical
   analytical forward model — you will port this to Python).
5. Read `H:/mpa-scale-solver-py-camera/` — the prior session's Python
   reference. It is the *shape* you mirror, with the corrections in §C.
6. Confirm scope with the user. Then build.

---

# Section A — structural commitments (locked)

These are the decisions made in prior sessions. They are not up for redesign.

## A.1. Python-first, native-later

The Python implementation is the v0 *shipping* artifact for the scale
solver, not a throwaway reference. mpa-conform's curator path consumes it
directly via `import mpa_scale_solver`. The native build (Rust + WASM +
Python bindings, mirroring mpa-solver) is a v2-or-later session that ports
this Python byte-identical.

Rationale: the camera test on synthetic substrate runs in 42 seconds on
1 CPU, ~5–10 seconds on the user's 30-worker machine. Performance is not
the bottleneck. Math correctness is. Python-first lets the math be
verified, fixtures be locked, and consumers (mpa-conform) be unblocked
without paying toolchain cost.

**Implication for this build session:** ship a Python package that runs,
passes its tests, and is consumable by mpa-conform. Do not write any
Rust or C++.

## A.2. Sibling-kernel discipline, mirroring mpa-solver

mpa-scale-solver is parallel to mpa-solver, not nested under it. Each is
a named family of operations:

- **mpa-solver:** forward physics + observable extraction. Given a
  canonical operating point, integrate trajectories, run ensembles,
  extract gFDR observables (correlator, response_direct, gfdr_locus,
  fit_invariants).
- **mpa-scale-solver:** τ_obs projection + canonical-frame operations.
  Given canonical state + τ_obs camera + translation field, project to
  substrate-native; given substrate observation + translation field +
  τ_obs, recover canonical state.

The two do not call each other. Both are consumed in parallel by
mpa-conform. See `mpa-solver/CLAUDE.md` for what mpa-solver ships and
where its discipline boundary sits; mirror that discipline here.

## A.3. Stateless free functions on plain dataclasses

No classes-with-methods. No global state. No singletons. Operations are
free functions that take plain dataclasses in and return plain dataclasses
out. Direct-port shape for the eventual Rust/C++ build.

```python
# Yes
def apply_translation(canonical: CanonicalState,
                      field: TranslationField,
                      tau_obs: float) -> SubstrateState: ...

# No
class ScaleSolver:
    def __init__(self, field): ...
    def apply(self, canonical, tau_obs): ...
```

Type hints everywhere (PEP 484). numpy arrays only for vectorized
operations, not for stored state. The Python reference at
`H:/mpa-scale-solver-py-camera/` already follows this discipline; mirror it.

## A.4. The seven operations (bootstrap §4 scope)

The v0 API surface, locked:

| Operation | Role |
|---|---|
| `apply_translation` | canonical state → substrate-native at tau_obs (forward) |
| `forward_sweep_invert` | substrate observation → canonical state at tau_obs |
| `tau_obs_sweep` | walk the RG-flow trajectory across a tau_obs grid |
| `regime_at` | classify vertex regime from chit at this tau_obs |
| `gamut_classify` | in-gamut / out-of-gamut diagnosis at this tau_obs |
| `intent_map` | I5 at v0; I1–I4 raise NotImplementedError |
| `validate_driver_profile` | RFC-S §5 round-trip residuals |

Do not add operations. Do not split operations. If you find yourself
adding an "extract_alpha_s" or "compute_correlator" — stop. That belongs
in mpa-solver. See §B.3 for the boundary.

## A.5. Multi-channel EXR is the per-frame artifact

The output of a camera-frame render is a multi-channel EXR. The RGB+A
channels carry the human-readable render (what your matplotlib produces).
Additional float32 channels carry the framework's observables at this
camera frame. See §D.3 for the channel manifest.

The EXR is *post-orchestration*. mpa-scale-solver populates the
canonical-frame projection channels (chit, gamma_AB, regime, in_gamut).
mpa-solver populates the observable channels (X_c, X_r, alpha_s, P_s, N_f).
mpa-conform orchestrates the EXR build. mpa-scale-solver does not emit
EXRs directly; it returns structured data that the EXR builder consumes.

**Implication for this build session:** ship Python operations that return
structured data with explicit field names. The EXR encoding layer is
mpa-conform's responsibility, not yours. Do *not* import `OpenEXR` in
the solver package. The camera test at
`H:/mpa-scale-solver-py-camera/test_camera_migration.py` does import
OpenEXR because it is a test harness, not a solver operation.

## A.6. Acceptance test is fixture-based regression

The v0 acceptance criterion is:

> Given the same input (substrate signal, translation field, tau_obs grid,
> random seeds), this Python package produces byte-identical per-frame JSON
> fixtures. The native port (future session) must reproduce the same fixtures
> within IEEE-754 platform tolerance.

Fixtures live at `tests/fixtures/`. Each fixture is a JSON file with:
- The inputs (canonical_state, tau_obs, field, seeds)
- The outputs (substrate_state for apply_translation; recovered
  CanonicalPoint for forward_sweep_invert; trajectory for tau_obs_sweep)
- The version (`mpa_scale_solver.__version__`)

CI runs `pytest tests/test_fixtures.py` which loads each fixture, runs the
operation, and asserts byte-identical output. The native port's CI does the
same thing.

---

# Section B — order of operations and component boundaries (locked)

## B.1. The five-step skeleton

From `mpa-auditor/docs/foundational-answers.md` §Q13, the pipeline is:

```
declare (class, columns, units, tau_obs)
  → tau_obs selects the canonical frame
  → forward-project (apply_translation at this tau_obs)
  → sweep-fit (forward_sweep_invert: substrate observation → canonical state)
  → audit (compare to prediction over validity_range ∩ gamut)
```

This is not five separate compute steps — it is five *ordering
constraints*:

| Constraint | Source | What it means |
|---|---|---|
| tau_obs declared before any projection | §Q13 + RFC-S §1 | tau_obs is an observer-fact, not a substrate-unknown. The camera frame is an input to apply_translation, not an output. There is no "infer tau_obs from the data" path. |
| Translation field applied before inversion | §Q13 (forward-only) | The inversion is forward-sweep search through forward projections. You cannot fit without first being able to forward-project. |
| Regime classification after projection | v9 §Scale-relativity | Regime label is tau_obs-conditional. Classifying pre-projection is meaningless. |
| Gamut check needs canonical state | RFC-S §2 | Gamut is the image of the RG trajectory in canonical space. Substrate state must be in canonical coords first. |
| Intent map only fires when gamut check fails | RFC-S §3 | Intents enumerate which invariants are preserved when out-of-gamut. In-gamut states pass through. |

**Critical implication:** the window-average step (taking a time-series
signal and producing a substrate observation by integrating over a
tau_obs-width window) sits *upstream* of `apply_translation` in the
pipeline. But there is one window-average *per tau_obs frame*, not one
window-average for the whole substrate. See §C.1 — this is the bug in the
prior session's Python reference.

## B.2. Three named inner traversals

Within the five-step skeleton, three different traversals share the same
operations but compose them differently:

**Audit traversal (single tau_obs declared):**
```
substrate-native observable
  → window-average at the declared tau_obs
  → apply_translation^(-1) via forward_sweep_invert
  → canonical state (chit, gamma_AB, ...)
  → regime_at
  → gamut_classify
  → in-gamut: pass through; out-of-gamut: intent_map
  → compare to predicted canonical state
```

**s→r migration traversal (tau_obs swept; the framework's primary test):**
```
substrate-native multi-window observables
  → for each tau_obs in the grid:
       window-average at this tau_obs (each window is a distinct camera)
       apply_translation^(-1)
       canonical state at this camera
       regime classification at this camera
  → trajectory of (tau_obs, canonical_state, regime)
  → trajectory shape IS the audit signature (c → s → r migration)
```

**Driver-profile validation traversal (RFC-S §5):**
```
reference canonical state at tau_obs_ref
  → forward-project (apply_translation)
  → predicted substrate-native observation
  → compare to known reference substrate observation (forward residual)
  → invert (forward_sweep_invert)
  → compare to original canonical state (round-trip residual)
  → both residuals must be within intent-specific threshold
```

These three traversals are the only ones in scope at v0. Add no fourth
without a foundational-questions entry.

## B.3. What lives where

The four-repo component boundary, locked. If you are tempted to violate
it, stop and ask.

| Repo | Lives here | Does NOT live here |
|---|---|---|
| `mpa-atlas` | Specs (RFCs), schemas, framework docs. Read-only from all consumers. | Implementation, compute, orchestration. |
| `mpa-solver` | Forward physics: trajectory integration, ensembles. Observable extraction: `correlator`, `response_direct`, `gfdr_locus`, `fit_invariants` (returns `{X_c, X_r, alpha_s, P_s, N_f, regime}`). 2-mode linearization. | tau_obs projection, canonical-frame operations, gamut machinery. |
| `mpa-scale-solver` (this repo) | The seven operations from A.4. tau_obs projection, canonical-frame operations, gamut, intents, round-trip validation. | Observable extraction (that's mpa-solver). Bundle orchestration (that's mpa-conform). Display (that's mpa-auditor). Driver-profile production (that's mpa-conform's curator/researcher path). |
| `mpa-conform` | Orchestration: declare → call mpa-solver for observables → call mpa-scale-solver for projection → assemble bundle → sign. Curator path and researcher path. Bundle schema. | Physics (mpa-solver). Projection (this repo). Spec content (mpa-atlas). |
| `mpa-auditor` | Display. Audit-engine. Read-only consumer of bundles. | Compute (other repos). |

**The line you will most want to cross and must not:** "I'll just compute
alpha_s here, it's only a few lines." No. `fit_invariants` lives in
mpa-solver. The scale-solver consumes already-extracted observables.

## B.4. TranslationField shape (schema-pinned)

Per `mpa-atlas/schema/driver-profile.v2.0.json`:

```python
from typing import Literal, Optional
from dataclasses import dataclass

@dataclass
class CanonicalPoint:
    chit: float                          # required
    gamma_AB: float                      # required (sign: <0 cooperative, >0 competitive)
    k_frust: bool                        # required
    method: str                          # required (provenance string)
    # Additional cdv1 API-slot values ride additionalProperties.
    # Implement as `extras: dict[str, float] = field(default_factory=dict)`.

@dataclass
class OperatingPoint:
    label: str                           # required, matches reference_outputs
    gt: Literal["c", "s", "r", "k"]      # required (ground-truth regime)
    # Substrate-specific axes (T, p_base, h_field, scenario, ...)
    # ride additionalProperties. Implement as
    # `axes: dict[str, float | str | None] = field(default_factory=dict)`.
    # Seed corpus convention: union shape with nulls is valid;
    # omitting irrelevant keys is also valid.

@dataclass
class TranslationRule:
    operating_point: OperatingPoint
    xdot_choice: str                     # must appear in operating_envelope.xdot_choices
    canonical: CanonicalPoint

@dataclass
class TranslationField:
    direction: Literal["forward"]        # architectural pin (Q13). NOT a runtime branch.
    shape: Literal["lookup_table"]       # architectural pin (v2; tangent-flow deferred to v3).
    description: Optional[str]           # free text
    rule: list[TranslationRule]          # minItems=1; cardinality = n_cells x |xdot_choices|
```

**`direction` and `shape` are Literal type pins, not enums with branches.**
The forward-only commitment is Q13 (the backward map is structurally
ill-posed). The lookup-table commitment is RFC-S Appendix B item 1
deferral. Do not write dispatch logic on these fields. They are
architectural constants the type checker enforces.

**`apply_translation` is lookup + interpolation, not parametric dispatch.**
Given a canonical point + tau_obs, look up the nearest rules in
`field.rule` (by operating-point matching), interpolate along the table's
implicit tau_obs axis. The prior session's Python reference uses
parametric rules (`aging_log`, `trivial_baseline`); those are *test
fixtures*, not production. See §C.2.

**Seed-corpus profiles for validation:** `neural-population`, `ck-glassy`,
`surface-code-qec`. All three pass the schema unmodified. Use them as
your integration-test driver profiles.

## B.5. Porting sources

For the analytical forward model and the regime classifier, port from
`mpa-auditor/math/gfdr-model.js`. The file is ~80 lines of pure functions,
no DOM, no event bus, direct port. Specifically:

```javascript
vertexRegime(chit)      // 5-bucket cut: deep_c, c_near_s, s_critical, r_near_s, deep_r
alphaS(chit)            // closed form: 0.5 + 0.3 * exp(-|chit| * 4)
plateauHeight(chit)     // closed form: max(0.05, 1 - exp(-max(0, chit+0.2) * 1.5))
generateLocus(chit, regime)  // analytical chi(tau), C(tau) — 80 points, log-spaced tau
interpLocus(model, tau)      // log-tau interpolation
locusResidual(empirical, chit)  // the inversion's scoring function
```

`vertexRegime` is the regime classifier the auditor uses. Port the
five-bucket version, not the three-bucket version the prior session wrote.

`generateLocus` + `locusResidual` together are the forward model the
inversion scores against. The prior session's `forward_sweep_invert`
is a homemade brute-force search; replace it with `locusResidual`-driven
forward search (sweep over chit candidates, score each, take argmin).

For everything else, the prior session at `H:/mpa-scale-solver-py-camera/`
is your starting point. Mirror its package layout, mirror its discipline,
fix the bugs in §C.

---

# Section C — known gaps, in priority order

These are the corrections needed before the prior session's Python becomes
the canonical shape. Address each in order; do not skip.

## C.1. **BUG**: window-average is upstream of translation in the wrong way

The prior session's `test_camera_migration.py` computes `<K>_tau_obs`
inside the substrate signal module and passes the resulting substrate
observation to `apply_translation`. That's correct for a single-frame
audit traversal.

The bug is in the *language* and would compound:
> "substrate → window-average → translation → invert → regime"

This reads as if window-averaging is a single global step. It is not. The
correct order for the s→r migration traversal is **per-frame**: each
tau_obs in the sweep gets its own window-average, its own translation, its
own inversion. The prior session's code happens to do this correctly (the
test loops over tau_obs and calls window-average once per frame), but the
README and the operation naming suggest a single global window-average.

**Fix:**
1. In `mpa_scale_solver/substrate_signal.py`, rename `window_average` to
   `window_average_at_tau_obs` and document that it produces a
   *single-frame* substrate observation.
2. In any docstring, comment, or README that uses the phrase
   "substrate → window-average → translation", replace with
   "per-frame: (substrate-window-average at tau_obs) → translation at
   tau_obs → invert".
3. The s→r migration test is fundamentally a *fan-out over tau_obs* of
   single-frame operations, not a pipeline applied once.

## C.2. Parametric rules in the prior session are test fixtures

The prior session's `_apply_parametric` dispatches on a `rule` string
inside `field.params` (`trivial_baseline`, `aging_log`). This is not
the v2.0 schema shape. The v2.0 schema has `field.shape = "lookup_table"`
and `field.rule = list[TranslationRule]` — there is no `params.rule`
parametric dispatch.

**Fix:**
1. Move `_apply_parametric` to `mpa_scale_solver/_test_fixtures.py` and
   mark clearly: "synthetic parametric rules, used only by the camera
   test; not the production translation-field shape."
2. Implement `_apply_lookup` in `mpa_scale_solver/operations.py` as the
   production path. Given `canonical_state` + `tau_obs` + a
   `TranslationField` of shape `lookup_table`:
   - Find the `TranslationRule` whose `operating_point` axes match (or
     bracket) the input canonical state.
   - If exact match: return the substrate-side projection at this
     tau_obs from the rule's table.
   - If bracketing match: linearly interpolate along the implicit
     tau_obs axis between the bracketing rules.
   - If no match: raise `ValueError("canonical state outside translation
     field domain")` — this is the curator-path's signal that the
     declared driver profile does not cover this substrate state, which
     is a gamut violation handled upstream.
3. Update the camera test to use lookup-form `TranslationField` constructed
   from a fixture-generated table (sample the analytical `aging_log` rule
   at the test's tau_obs grid → produce `TranslationRule` rows → assemble
   `TranslationField`). The test then exercises the production code path.

## C.3. `fit_invariants` Python binding is a prerequisite, not your scope

The mpa-solver C++/WASM kernel ships `fit_invariants(locus) → {X_c, X_r,
alpha_s, P_s, N_f, regime}`. The Python binding in
`mpa-conform/conformer/compute/observables.py` has `correlator`,
`response_direct`, `gfdr_locus` but not `fit_invariants`.

**Your scope:** do not port `fit_invariants` into this repo. It belongs
in mpa-solver's Python bindings, not here.

**Action:** flag this in `mpa-scale-solver/docs/PREREQUISITES.md` as a
dependency. Suggested wording:

> mpa-solver's Python bindings must expose `fit_invariants` before this
> repo's integration tests against real driver profiles can run. The
> port is a one-shot session in `mpa-solver`. Until that lands,
> integration tests use the synthetic camera test (which does not need
> fit_invariants because the synthetic carries its own analytical
> truth).

## C.4. Regime classifier: five-bucket, not three-bucket

The prior session implements `regime_at` with a three-bucket cut
(`c / s / r`). The auditor's canonical classifier is five-bucket
(`deep_c / c_near_s / s_critical / r_near_s / deep_r`). Port the
five-bucket version from `gfdr-model.js`:

```python
def regime_at(canonical: CanonicalState,
              tau_obs: float) -> RegimeReading:
    chit = canonical.chit
    if chit >= 0.7:    label = "deep_c"
    elif chit >= 0.2:  label = "c_near_s"
    elif chit > -0.2:  label = "s_critical"
    elif chit > -0.7:  label = "r_near_s"
    else:              label = "deep_r"
    return RegimeReading(regime=label, k_frust=canonical.k_frust)
```

The three-bucket cut (`c / s / r`) is a coarse projection used only for
display banding (the green/yellow/red regions in the camera test's plot).
Keep that as a *display* helper, not the canonical classifier:

```python
def regime_display_band(regime: Literal["deep_c", "c_near_s", "s_critical",
                                         "r_near_s", "deep_r"]) -> Literal["c", "s", "r"]:
    if regime in ("deep_c", "c_near_s"): return "c"
    if regime == "s_critical":           return "s"
    return "r"
```

## C.5. v2 feature inventory is sequencing reference, not v0 scope

The prior session drafted a v2 feature inventory (A1–A4 RG-flow content,
B1–B5 intent table, C1–C4 inversion conditioning, D1–D3 N-mode, E1–E4
migration analytics, F1–F3 compactification, G1–G3 cross-substrate,
H1–H3 driver-profile hardening, I1–I2 learned form, J1–J4 infrastructure).
All of this is post-v0.

**v0 ships:**
- The seven operations from A.4, scoped per §7 of the original bootstrap
  (revised to call the leading-order rule "trivial baseline" honestly,
  with non-trivial flow content arriving from driver profiles via the
  lookup table).
- I5 only for `intent_map`.
- 2-mode only (no N-mode).
- Lookup-form TranslationField only.
- The camera test as the canonical visual test.
- Per-frame JSON fixtures as the acceptance basis.

**v1 fills out:** I1–I4, residual-field return from `forward_sweep_invert`,
migration-trajectory analytics (alpha_s extraction from trajectory data
where mpa-solver hasn't already done it), compactification-point detection.

**v2 earns the "RG-flow operator" claim:** non-trivial defaults, tangent-
flow form (RFC-S Appendix B item 1), N-mode, sensitivity, learned form,
cross-substrate gamut operations.

Do not implement v1 or v2 features in this session.

---

# Section D — what you ship (deliverables)

## D.1. Repository layout

```
H:/mpa-scale-solver/
├── README.md
├── CLAUDE.md                            # what-lives-here, what-doesn't, math caveats
├── pyproject.toml
├── mpa_scale_solver/
│   ├── __init__.py                      # public API
│   ├── types.py                         # CanonicalState, SubstrateState, TranslationField,
│   │                                    # CanonicalPoint, OperatingPoint, TranslationRule,
│   │                                    # GamutSpec, RegimeReading
│   ├── operations.py                    # the seven operations
│   ├── gfdr_model.py                    # ported from auditor's gfdr-model.js:
│   │                                    # vertex_regime, alpha_s, plateau_height,
│   │                                    # generate_locus, interp_locus, locus_residual
│   ├── substrate_signal.py              # synthetic K(t) generator (camera test only)
│   └── _test_fixtures.py                # synthetic parametric rules (test only)
├── tests/
│   ├── test_operations.py               # unit tests per operation
│   ├── test_fixtures.py                 # byte-identical regression
│   ├── test_camera_migration.py         # the visual end-to-end test
│   ├── test_seed_corpus.py              # validate against the three seed profiles
│   └── fixtures/
│       ├── apply_translation/           # per-operation fixture sets
│       ├── forward_sweep_invert/
│       ├── tau_obs_sweep/
│       └── camera/                      # per-frame JSON from the camera test
├── docs/
│   ├── PREREQUISITES.md                 # fit_invariants binding gap, etc.
│   ├── ORDER_OF_OPERATIONS.md           # §B of this document, restated as a primer
│   └── EXR_CHANNEL_MANIFEST.md          # §D.3 below, restated for consumers
└── .gitignore
```

Place `H:/mpa-scale-solver/` per the user's machine layout. Mirror
mpa-solver's gitignore + CLAUDE.md patterns.

## D.2. Tests

Four test categories, all run in CI via `pytest`:

**Unit tests (`test_operations.py`):** one test class per operation. For
each, verify type signatures, edge cases (empty grids, single-point grids,
out-of-domain inputs), error handling (informative exceptions, never silent
wrong answers).

**Fixture regression (`test_fixtures.py`):** loads each JSON fixture in
`tests/fixtures/`, runs the operation, asserts byte-identical output.
Format:

```python
def test_apply_translation_fixtures():
    for fixture_path in (FIXTURES / "apply_translation").glob("*.json"):
        fx = json.loads(fixture_path.read_text())
        canonical = CanonicalState(**fx["input"]["canonical_state"])
        field = parse_translation_field(fx["input"]["field"])
        tau_obs = fx["input"]["tau_obs"]
        result = apply_translation(canonical, field, tau_obs)
        expected = SubstrateState(**fx["expected_output"])
        assert result == expected, f"{fixture_path.name} regression"
```

Adding a new feature → adding new fixtures. Changing existing behavior →
patch-bump + new fixtures + commit note explaining the change. Never
regenerate fixtures silently.

**Camera visual test (`test_camera_migration.py`):** port from the prior
session. Three-panel layout, parallel rendering. Pass criterion: max
|residual| ≤ tolerance across all frames. Outputs per-frame PNG + JSON.

**Seed corpus integration (`test_seed_corpus.py`):** load each of the three
seed driver profiles (`neural-population`, `ck-glassy`,
`surface-code-qec`), verify schema validation passes, run
`validate_driver_profile` (RFC-S §5 round-trip) against each, assert all
residuals are within intent-specific thresholds.

## D.3. EXR channel manifest (for consumers, especially mpa-conform)

When mpa-conform assembles a per-camera-frame EXR, the channels are:

| Channel | dtype | Source | Per-frame or trajectory? |
|---|---|---|---|
| RGB, A | uint8 → float32 in [0,1] | matplotlib render | per-frame |
| chit | float32 | mpa-scale-solver (canonical state at this tau_obs) | per-frame |
| gamma_AB | float32 | mpa-scale-solver | per-frame |
| regime_label | float32 (encoded enum) | mpa-scale-solver (`regime_at`, 5-bucket) | per-frame |
| in_gamut | float32 (0 or 1) | mpa-scale-solver (`gamut_classify`) | per-frame |
| X_c | float32 | mpa-solver (`fit_invariants`) | per-frame |
| X_r | float32 | mpa-solver | per-frame |
| alpha_s | float32 | mpa-solver | per-frame |
| P_s | float32 | mpa-solver | per-frame |
| N_f | float32 | mpa-solver | per-frame |
| beta_mem | float32 | mpa-solver (extension; v2 of fit_invariants) | per-frame |
| Q | float32 | mpa-solver (cycles-of-headroom) | per-frame |
| I_pred | float32 | mpa-solver (predictive information) | per-frame |
| C_mu | float32 | mpa-solver (statistical complexity) | per-frame |
| window_mean | float32 | curator (raw substrate-side window-average) | per-frame |
| sem_chit, sem_X_c, sem_alpha_s, ... | float32 | curator (multi-realization SEM) | per-frame |
| trajectory_chit | float32 array | mpa-conform (composition across all frames) | trajectory |
| trajectory_regime | float32 array | mpa-conform | trajectory |
| trajectory_alpha_s | float32 array | mpa-conform | trajectory |

The trajectory channels are arrays packed into the EXR via a 1D image part
(EXR supports multipart files). One channel per per-frame observable;
length = number of frames in the sweep.

**Your scope is the per-frame mpa-scale-solver channels** (chit,
gamma_AB, regime_label, in_gamut). Everything else is upstream
(mpa-solver) or downstream (mpa-conform). Document your channels' units,
ranges, and encoding in `docs/EXR_CHANNEL_MANIFEST.md`.

## D.4. Public API

`mpa_scale_solver/__init__.py` exports:

```python
from .types import (
    CanonicalState, SubstrateState,
    CanonicalPoint, OperatingPoint, TranslationRule, TranslationField,
    GamutSpec, RegimeReading,
)
from .operations import (
    apply_translation,
    forward_sweep_invert,
    tau_obs_sweep,
    regime_at,
    gamut_classify,
    intent_map,
    validate_driver_profile,
)
from .gfdr_model import (
    vertex_regime, alpha_s, plateau_height,
    generate_locus, interp_locus, locus_residual,
)

__version__ = "0.1.0"
__all__ = [...]  # explicit
```

Nothing else exported. Internal helpers stay private (underscore prefix).
The `_test_fixtures` module is not exported.

## D.5. CLAUDE.md content

Mirror `mpa-solver/CLAUDE.md`'s structure. Sections:

1. **What lives here.** The seven operations, the gFDR model port, the
   substrate-signal synthetic. Named family of operations.
2. **What does NOT live here.** Observable extraction (mpa-solver).
   Bundle orchestration (mpa-conform). Display (mpa-auditor). Driver-
   profile production (mpa-conform's curator/researcher paths). Physics
   integration (mpa-solver).
3. **Math caveats.** The five-bucket regime classifier is the canonical
   one; the three-bucket is display-only. Translation field is
   lookup-form at v2; tangent-flow form deferred. apply_translation is
   lookup + interpolation, not parametric dispatch. forward_sweep_invert
   is brute-force grid search at v0; adaptive refinement and Bayesian
   primitives are v1.
4. **Reproducibility.** Stateless free functions on plain dataclasses.
   Same inputs → byte-identical outputs. Fixtures lock behavior.
5. **Sibling-repo relationships.** Table from §B.3.

## D.6. README.md content

For human consumers (researchers, mpa-conform integrators):

1. What this is (the scale-management kernel).
2. The seven operations, one-line each.
3. How to install (`pip install -e .`).
4. How to use (one minimal example: build a `CanonicalState`, build a
   `TranslationField` from a seed driver profile, call
   `apply_translation`).
5. The camera test, with a screenshot of `out_camera/migration.mp4`'s
   final frame.
6. Pointer to `docs/ORDER_OF_OPERATIONS.md` for pipeline integrators.
7. Pointer to `mpa-solver/CLAUDE.md` for upstream observable extraction.
8. Pointer to `mpa-conform/docs/` for orchestration integration.

---

# Section E — acceptance for this build session

When all of these are true, the session is done:

1. `H:/mpa-scale-solver/` exists; `git init`d.
2. The seven operations are implemented per §B and §C.
3. `gfdr_model.py` is ported from the JS, with the five-bucket
   classifier.
4. Unit tests pass. Fixture regression passes. Camera test passes
   (max |residual| ≤ 0.05).
5. Seed corpus integration test passes for all three profiles.
6. README, CLAUDE.md, docs/ORDER_OF_OPERATIONS.md, docs/PREREQUISITES.md,
   docs/EXR_CHANNEL_MANIFEST.md are written.
7. `pip install -e .` works in a fresh venv.
8. Tarball at `H:/mpa-scale-solver/dist/mpa_scale_solver-0.1.0.tar.gz`
   ready to consume.
9. Commit + push to `github.com/<user>/mpa-scale-solver` (public, MIT).
   Report SHA.
10. Append a session log row to `mpa-scale-solver/README.md`.

**Resist scope creep.** Native build, N-mode, I1–I4, residual-field
return, sensitivity, learned-form translation field — none of these are
in scope. Each is its own session, sequenced by the user.

---

# Section F — sibling-repo handoff updates

After this session ships, update:

- **`mpa-conform/docs/ROADMAP.md`:** mark the scale-solver as "vendorable
  via `pip install mpa_scale_solver`"; unblock the v0.2 bundle schema
  bump.
- **`mpa-conform/conformer/compute/inversion.py`:** rewire to call
  `mpa_scale_solver.forward_sweep_invert` on entry; fit in canonical
  space. (This is a follow-up session for mpa-conform, not your scope —
  but flag in this session's commit message that mpa-conform is now
  unblocked.)
- **`mpa-central/SUITE_BLOCK_IN.md`:** the compute layer table now reads
  `mpa-solver` + `mpa-scale-solver` (Python v0) + `mpa-conform`.
- **`mpa-atlas/schema/`:** no edits; the schema is already there at v2.0.
- **`mpa-scale-solver-bootstrap.md`:** archive (move to `archive/` or
  mark superseded). This handoff supersedes it.

---

# Section G — the one warning

The prior session's Python reference passes its camera test. That does not
mean it is correct. The pass shows that:

1. Window-integration → translation → inversion runs end-to-end.
2. The synthetic substrate produces a clean c → s → r migration.
3. The forward search recovers the analytical truth within grid spacing.

The pass does *not* show that:

1. The translation-field shape matches the v2.0 schema. **It does not.**
2. The regime classifier matches the auditor's. **It does not (3-bucket vs 5-bucket).**
3. The order-of-operations language is correct. **It is not (single global
   window-average vs per-frame).**

§C is the work to make the Python reference become the canonical shape.
Do not ship it as-is. Do the C-section work first, *then* call the camera
test the canonical visual test.

If you find yourself thinking "the prior session got it right, I'll just
package it up" — re-read §C. The session got the *shape* right and the
*details* wrong. Both halves matter.

---

**Done. Begin with §A re-read, then §B, then §C item-by-item. Ask the
user if any open question surfaces. Ship when §E acceptance is met.**
