# `mpa-scale-solver` — v1 handoff (Python continues)

**You are a fresh Claude Code session. This handoff is self-contained.**

**Your task:** extend the Python `mpa-scale-solver` from v0.1.0 to v1.0.0.
Pure Python, no native build. v1 lands the capabilities that Wilson–
Kadanoff closure + Banach substrate + Asymptotic-Closure Principle now
make shippable: continuous-form flow, tangent-flow translation field,
Banach-substrate camera test, inverse-lookup-table sidecar dispatch,
per-call self-validation, full provenance trail.

**North star:** [`mpa-scale-solver-north-star.md`](mpa-scale-solver-north-star.md).
This handoff is v1 on a v0→v6 trajectory. v2 adds JAX +
differentiability + Bayesian + N-mode + full I1–I5 + non-Markovian
Caputo. v6 is the eventual one-shot native port. Each is its own
session; do not implement v2+ in v1.

**Authority chain:**

- North star: `mpa-scale-solver-north-star.md`.
- Architectural: [`SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md).
- Specs: `mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md` §§0–5;
  `v9_compressed.md` (incl. §Asymptotic closure when landed);
  `cdv1_compressed.md`; `mpa-atlas/schema/driver-profile.v2.0.json`.
- Receipts: `v9_receipts.md` §RG closure (Wilson–Kadanoff closed);
  §Asymptotic closure; §Compression Axiom; §Trail-class metric.
- Order of operations: `mpa-auditor/docs/foundational-answers.md` §Q13.
- Component boundaries: `mpa-solver/CLAUDE.md`.
- Banach substrate: [`banach-substrate-reference.md`](banach-substrate-reference.md).
- v0 reference: `H:/mpa-scale-solver/` v0.1.0 (existing pure Python).

**First moves:**

1. Read this document end-to-end.
2. Read `mpa-scale-solver-north-star.md`.
3. Read `v9_receipts.md` §RG closure (the closure that grounds continuous flow).
4. Read `banach-substrate-reference.md` (the new camera-test fixture).
5. Read `H:/mpa-scale-solver/README.md` and skim
   `H:/mpa-scale-solver/mpa_scale_solver/*.py` (the v0 baseline you extend).
6. Confirm scope with the user. Then build.

---

## What v1 ships (six capabilities + the tighter test)

| # | Capability | What it adds |
|---|---|---|
| 1 | **Continuous form `C^ν`** | `flow(canonical_initial, ν, field) → CanonicalState`. Grounded in Markovian scope per §RG closure. Integer-N becomes a sampling helper. |
| 2 | **Tangent-flow translation field** | `TranslationField` enum gains a `TangentFlow` variant alongside `LookupTable`. Banach γ-scaling rule is the canonical leading-order tangent-flow auto-remap (RFC-S Appendix B item 1). |
| 3 | **Banach camera test** | Replaces hand-crafted `aging_log` synthetic. Residual measures implementation against framework, not against fixture author. |
| 4 | **Inverse-lookup-table sidecar dispatch** | `InverseLookupSidecar` type + table-first / compute-fallback dispatch in `forward_sweep_invert`. Solver works with or without sidecar. |
| 5 | **Per-call self-validation** | Every operation returns `OperationOutput[T]` carrying `value`, `validation: ValidationReport`, `provenance: Provenance`. |
| 6 | **Full provenance trail** | Provenance dataclass populated per call; rides through downstream consumers. |

**Plus:** tighten Banach camera-test acceptance from `max|residual| ≤ 0.05`
(v0 against synthetic) to `max|residual| ≤ 0.001` (Banach carries
analytical truth; tolerance can shrink an order of magnitude).

---

# Section A — structural commitments (locked)

## A.1. Python-only

v1 is pure Python. No Rust, no C++, no WASM, no pyo3, no maturin. The
native port is v6; until then, Python is production. mpa-conform's
curator and researcher paths consume via `import mpa_scale_solver`.

Adopt JAX only at v2. v1 stays on numpy + scipy.

## A.2. Backward-compatible

Every v0.1.0 fixture passes unchanged in v1.0.0. The seven-operation
signatures stay identical to v0; new return fields (validation,
provenance) ride on a wrapped `OperationOutput[T]` that consumers
unwrap when they care.

Migration is opt-in: existing v0 consumers calling
`apply_translation(...)` get the raw `SubstrateState` (back-compat
shim); new consumers calling `apply_translation_wrapped(...)` get the
`OperationOutput[SubstrateState]` with validation + provenance.

Alternative pattern (cleaner): keep the seven operations returning the
raw type; expose validation + provenance through a thread-local
`get_last_call_metadata()` accessor. Pick whichever is simpler to
implement and document.

## A.3. Stateless free functions on plain dataclasses (unchanged)

Same discipline as v0. No classes-with-methods. No global state. No
singletons. New types are plain dataclasses; new operations are free
functions.

## A.4. The seven operations stay the same surface

| Operation | v0 | v1 |
|---|---|---|
| `apply_translation` | lookup + nearest-neighbor | + tangent-flow dispatch on field shape |
| `forward_sweep_invert` | brute-force grid search | + sidecar table-first; brute-force as fallback |
| `tau_obs_sweep` | per-frame fan-out | + continuous `ν` via `flow` underneath |
| `regime_at` | five-bucket classifier | + Asymptotic-Closure verification in validation report |
| `gamut_classify` | range checks | + validation report |
| `intent_map` | I5 only | unchanged (I1–I4 land at v2) |
| `validate_driver_profile` | RFC-S §5 round-trip | + Banach reference as first link |

Plus one new public function:

| `flow(initial, ν, field)` | new | `C^ν = exp(ν · ln C)` — continuous-form |

## A.5. EXR multi-channel artifact

Per-frame channels mpa-scale-solver populates: `chit`, `gamma_AB`,
`regime_label`, `in_gamut`. v1 adds two channels:

- `provenance_hash` (float32-encoded): table-vs-compute dispatch
  fingerprint.
- `validation_flags` (float32-bitfield): Asymptotic-Closure +
  k_frust-invariance + round-trip-residual pass/fail per frame.

EXR encoding stays in mpa-conform.

## A.6. Acceptance is fixture-based regression + Banach round-trip

- Every v0 fixture passes unchanged in v1.
- Banach camera test passes with `max|residual| ≤ 0.001`.

---

# Section B — order of operations and component boundaries (locked)

Unchanged from v0. Restated briefly:

## B.1. Five ordering constraints (per `foundational-answers.md` §Q13)

```
declare (class, columns, units, tau_obs)
  → tau_obs selects canonical frame
  → forward-project (apply_translation at this tau_obs)
  → sweep-fit (forward_sweep_invert: substrate → canonical at tau_obs)
  → audit (compare over validity_range ∩ gamut)
```

Five constraints, not five steps: τ_obs declared before any projection;
translation field applied before inversion; regime classification after
projection; gamut check needs canonical state; intent map only fires
when gamut check fails.

## B.2. Three named inner traversals

Audit (single τ_obs), s→r migration (τ_obs swept; the framework's
primary cross-substrate test), driver-profile validation (RFC-S §5
round-trip). Per-frame fan-out, not pipeline-applied-once.

## B.3. Four-repo component boundary

`mpa-scale-solver` owns the seven operations + `flow`. Does NOT own
observable extraction (`mpa-solver`), bundle orchestration
(`mpa-conform`), display (`mpa-auditor`). The line you will most want
to cross: "I'll just compute α_s here, it's only a few lines." No.
`fit_invariants` lives in mpa-solver. The scale solver consumes
already-extracted observables.

## B.4. TranslationField — add tangent-flow

```python
from typing import Literal, Optional, Union
from dataclasses import dataclass

@dataclass
class LookupTableField:
    direction: Literal["forward"]               # type pin
    shape: Literal["lookup_table"]              # type pin
    description: Optional[str]
    rule: list[TranslationRule]                 # minItems 1

@dataclass
class TangentFlowField:
    direction: Literal["forward"]               # type pin
    shape: Literal["tangent_flow"]              # type pin
    description: Optional[str]
    rule_at_origin: TranslationRule             # canonical reference point
    scaling: ScalingRule                        # γ-scaling, chit-scaling under τ_obs

TranslationField = Union[LookupTableField, TangentFlowField]

@dataclass
class ScalingRule:
    # Banach-canonical leading-order tangent-flow rule:
    #   gamma(tau_obs) = gamma_initial * (tau_obs / tau_obs_ref)^delta_gamma
    #   chit(tau_obs)  = chit_initial + delta_chit * ln(tau_obs / tau_obs_ref)
    tau_obs_ref: float
    delta_gamma: float                          # default: 0.0 (identity scaling)
    delta_chit: float                           # default: 0.0 (identity scaling)
    refinement: Optional[dict]                  # substrate-conditional override
```

`apply_translation` dispatches on `field.shape`:
- `"lookup_table"`: existing v0 behavior (lookup + nearest-neighbor).
- `"tangent_flow"`: evaluate via the scaling rule at the given τ_obs.

Both forms are forward-only per Q13.

---

# Section C — v1-specific deliverables

## C.1. Continuous form `C^ν`

Per `v9_receipts.md` §RG closure (Wilson–Kadanoff closed in Markovian
scope, β_mem = 1, where the Banach substrate sits):

```python
def flow(
    canonical_initial: CanonicalState,
    nu: float,
    field: TranslationField,
) -> CanonicalState:
    """C^nu = exp(nu * ln C) — continuous-form flow.

    For nu = N integer, equivalent to N successive applications.
    For real nu, evaluated via the spectral functional calculus on C.
    """
```

Implementation:

- **For Banach substrate (identity translation):** the canonical state at
  depth ν is computed by integrating the flow vector field on
  (chit, γ_AB) space. Use `scipy.integrate.solve_ivp` or analogous.
  The flow vector field is the leading-order generator from the Banach
  substrate's `ScalingRule` plus the Compression Axiom contraction.

- **For lookup-table profiles:** integer-N is unchanged from v0 (apply
  the lookup N times). Continuous-ν between table grid points is linear
  interpolation along the implicit ν axis. Spectral functional calculus
  on the table is overkill at v1; defer to v2 (JAX) when
  differentiability needs it.

- **For tangent-flow profiles:** the scaling rule is closed-form;
  `flow(initial, ν, tangent_flow_field)` evaluates the scaling formula
  at ν directly.

Per-substrate verification of the Markovian-scope assumption is v2's
responsibility; at v1, document that continuous flow is grounded for
β_mem = 1 (Banach substrate's regime); non-Markovian Caputo profiles
fall back to integer-N or raise NotImplementedError.

## C.2. Tangent-flow translation field

Per RFC-S Appendix B item 1, the auto-remap rule's exact form was open
at v0. Wilson–Kadanoff closure unlocks the canonical leading-order
rule: the Banach substrate's γ-scaling.

**Implementation:**

```python
def apply_translation(
    canonical: CanonicalState,
    field: TranslationField,
    tau_obs: float,
) -> SubstrateState:
    if field.shape == "lookup_table":
        return _apply_lookup(canonical, field, tau_obs)
    elif field.shape == "tangent_flow":
        return _apply_tangent_flow(canonical, field, tau_obs)

def _apply_tangent_flow(
    canonical: CanonicalState,
    field: TangentFlowField,
    tau_obs: float,
) -> SubstrateState:
    rule = field.scaling
    ratio = tau_obs / rule.tau_obs_ref
    scaled = CanonicalPoint(
        chit=canonical.chit + rule.delta_chit * math.log(ratio),
        gamma_AB=canonical.gamma_AB * (ratio ** rule.delta_gamma),
        k_frust=canonical.k_frust,                    # invariant per v9 §Scale-relativity
        method=f"tangent_flow:{field.scaling.refinement or 'banach_canonical'}",
    )
    # Project through the rule_at_origin's substrate-side mapping
    return _project_via_origin(scaled, field.rule_at_origin, tau_obs)
```

Default `ScalingRule` values for the Banach substrate are
`delta_gamma=0`, `delta_chit=0` (identity scaling at leading order;
the substrate's RG flow is computed via the continuous flow rather
than the scaling rule). Real substrates can override via
`scaling.refinement`.

## C.3. Banach camera test

Replace the v0 hand-crafted `aging_log` synthetic.

**Implementation:**

```python
# tests/test_banach_camera.py
from mpa_scale_solver import (
    BanachSubstrate, flow, regime_at, tau_obs_sweep,
)

def test_banach_camera_migration():
    substrate = BanachSubstrate(
        chit_0=1.5,                           # c-band start
        gamma_AB_0=-0.5,                      # cooperative
    )
    tau_obs_grid = np.logspace(-2, 4, 80)    # 80 frames

    trajectory = tau_obs_sweep(
        substrate.canonical_initial(),
        substrate.translation_field(),
        tau_obs_grid,
    )

    for nu, frame in zip(tau_obs_grid, trajectory):
        analytical = substrate.state_at(nu)      # framework truth
        residual_chit = abs(frame.chit - analytical.chit)
        residual_gamma = abs(frame.gamma_AB - analytical.gamma_AB)
        assert residual_chit < 0.001
        assert residual_gamma < 0.001
```

The Banach substrate is the framework's self-reference; its `state_at(ν)`
returns analytical truth. Tolerance tightens from 0.05 (v0 against
fixture) to 0.001 (v1 against framework).

Add a `BanachSubstrate` class (or module) in `mpa_scale_solver/` that
produces:
- The canonical-initial state at ν=0
- The translation field (identity)
- The analytical `state_at(ν)` for test comparison
- The normalization manifest from `banach-substrate-reference.md`

## C.4. Inverse-lookup-table sidecar dispatch

**New type:**

```python
@dataclass
class InverseLookupSidecar:
    version: str
    driver_profile_id: str
    driver_profile_version: str
    tau_obs_grid: list[float]
    substrate_grid: list[SubstrateState]
    canonical_grid: list[CanonicalState]
    forward_lookup: dict                          # (canonical, tau_obs) → substrate
    inverse_lookup: dict                          # (substrate, tau_obs) → canonical (where invertible)
    ambiguity_regions: list[dict]                 # multi-valued inverse zones
```

**Dispatch:**

```python
def forward_sweep_invert(
    substrate: SubstrateState,
    field: TranslationField,
    tau_obs: float,
    candidate_grid: list[CanonicalState],
    sidecar: Optional[InverseLookupSidecar] = None,
) -> InversionResult:
    if sidecar is not None:
        hit = sidecar.lookup(substrate, tau_obs)
        if hit is not None:
            return InversionResult.table_hit(hit, sidecar.version)
    # Compute-fallback: brute-force grid search (unchanged from v0).
    return InversionResult.compute(
        _compute_inversion(substrate, field, tau_obs, candidate_grid)
    )
```

`sidecar` is optional. Solver works without it (v0 behavior); fast with
it (v1 behavior). The sidecar's *production* — running the curator
forward through the full grid to build the inverse table — is
mpa-conform's curator-path responsibility, not v1's. v1 ships the data
type + dispatch logic + a one-shot sidecar builder for the Banach
substrate (`BanachSubstrate.build_sidecar()`) so the Banach camera test
exercises the table-first path.

## C.5. Per-call self-validation

Every operation produces an output AND a validation report.

```python
@dataclass
class ValidationReport:
    asymptotic_closure_compliant: bool           # no exact 0 or 1 at non-asymptotic points
    k_frust_invariant: bool                      # topological invariant preserved (trajectory ops)
    round_trip_residual: Optional[float]         # forward-then-back recovery (when computed)
    notes: list[str]                             # human-readable diagnostics

@dataclass
class OperationOutput(Generic[T]):
    value: T
    validation: ValidationReport
    provenance: Provenance
```

Validation logic per operation:

- `apply_translation`: check output `SubstrateState` for exact 0/1
  values in observable channels (excluding declared normalization
  conventions); report.
- `forward_sweep_invert`: check recovered `CanonicalState` similarly;
  optionally compute round-trip residual (apply_translation on
  recovered, compare to original substrate).
- `tau_obs_sweep`: check k_frust invariance across the trajectory.
- `regime_at`: classify; no validation needed beyond the chit threshold check.
- `gamut_classify`: trivially validates itself.
- `intent_map`: I5 invariance preservation check.
- `validate_driver_profile`: returns its own residual report — wrap in
  the new format.

Failures are flagged in `ValidationReport`, not raised. Consumers
decide whether to trust borderline outputs.

**Back-compat:** keep the raw operations returning the raw types (v0
signatures unchanged). Expose `*_wrapped` variants for v1 consumers
that want validation + provenance:

```python
def apply_translation(canonical, field, tau_obs) -> SubstrateState: ...  # v0 sig
def apply_translation_wrapped(canonical, field, tau_obs) -> OperationOutput[SubstrateState]: ...  # v1 addition
```

## C.6. Full provenance trail

```python
@dataclass
class Provenance:
    solver_version: str                          # mpa_scale_solver.__version__
    operation: str                               # "apply_translation", etc.
    timestamp_ns: int                            # time.monotonic_ns()
    dispatch_path: DispatchPath                  # TableHit | ComputeFallback | DirectCompute
    table_version: Optional[str]                 # sidecar version if applicable
    notes: list[str]                             # operation-specific notes
```

Provenance rides on `OperationOutput`. mpa-conform extracts provenance
into the bundle's audit record; the auditor's display layer reads it
directly.

---

# Section D — what you ship (deliverables)

## D.1. Repository layout

```
H:/mpa-scale-solver/                            # existing repo, additive update
├── README.md                                    # updated for v1
├── CLAUDE.md                                    # updated discipline note
├── pyproject.toml                               # bump to 1.0.0
├── mpa_scale_solver/
│   ├── __init__.py                              # export new types + flow + wrapped ops
│   ├── types.py                                 # add OperationOutput, ValidationReport, Provenance, TangentFlowField, ScalingRule, InverseLookupSidecar
│   ├── operations.py                            # add wrapped variants; tangent-flow dispatch
│   ├── flow.py                                  # NEW — continuous-form C^nu
│   ├── banach.py                                # NEW — BanachSubstrate class + sidecar builder
│   ├── sidecar.py                               # NEW — InverseLookupSidecar dispatch helpers
│   ├── validation.py                            # NEW — per-call validation logic
│   ├── provenance.py                            # NEW — provenance trail
│   ├── gfdr_model.py                            # unchanged
│   ├── substrate_signal.py                      # unchanged (camera-test helper only)
│   └── _test_fixtures.py                        # unchanged (synthetic parametric rules)
├── tests/
│   ├── test_operations.py                       # extend with wrapped variants + tangent-flow tests
│   ├── test_fixtures.py                         # all v0 fixtures pass unchanged
│   ├── test_banach_camera.py                    # NEW — replaces v0's aging_log camera test
│   ├── test_camera_migration.py                 # keep v0's test passing; mark as legacy
│   ├── test_seed_corpus.py                      # extend with Banach as fourth reference
│   ├── test_sidecar.py                          # NEW — sidecar dispatch (with + without; same output)
│   ├── test_validation.py                       # NEW — each flag fires when triggered
│   ├── test_provenance.py                       # NEW — provenance correctly recorded per call
│   └── fixtures/                                # v0 fixtures unchanged; add v1 fixture set
└── docs/
    ├── PREREQUISITES.md                         # unchanged (fit_invariants gap, etc.)
    ├── ORDER_OF_OPERATIONS.md                   # unchanged
    ├── EXR_CHANNEL_MANIFEST.md                  # add provenance_hash + validation_flags channels
    ├── CONTINUOUS_FLOW.md                       # NEW — flow() implementation notes
    ├── TANGENT_FLOW.md                          # NEW — tangent-flow translation field
    ├── SIDECAR_FORMAT.md                        # NEW — inverse-lookup-table sidecar spec
    └── BANACH_SUBSTRATE.md                      # NEW — local pointer to mpa-conform's reference doc + Banach class usage
```

## D.2. Tests

Eight test categories, all run in CI:

1. **`test_operations.py`** — extended with wrapped variants and tangent-flow.
2. **`test_fixtures.py`** — every v0 fixture passes unchanged.
3. **`test_banach_camera.py`** — `max|residual| ≤ 0.001` against Banach.
4. **`test_camera_migration.py`** — v0 test stays passing; keep as legacy
   coverage of the lookup-table dispatch.
5. **`test_seed_corpus.py`** — three real profiles + Banach reference.
6. **`test_sidecar.py`** — dispatch with + without sidecar; same final
   output; provenance correctly records dispatch path.
7. **`test_validation.py`** — synthetic inputs that should trigger each
   flag (Asymptotic-Closure violation, k_frust drift, round-trip
   blowup); verify the flags fire.
8. **`test_provenance.py`** — per-call provenance correctly populated;
   downstream consumers can read it.

## D.3. Documentation updates

- **`README.md`**: v1 capabilities, trajectory toward north star
  (note v2 = JAX + Bayesian + N-mode; v6 = native port).
- **`CLAUDE.md`**: v1-specific discipline notes (back-compat, wrapped
  variants, sidecar dispatch policy).
- **`docs/CONTINUOUS_FLOW.md`**: implementation notes for `flow`,
  Krein–Rutman / Kato references, Markovian-scope caveat (Caputo
  β_mem < 1 = v2).
- **`docs/TANGENT_FLOW.md`**: tangent-flow field shape, scaling rule
  semantics, Banach-canonical default.
- **`docs/SIDECAR_FORMAT.md`**: sidecar JSON schema, dispatch
  semantics, curator-side production responsibility.
- **`docs/BANACH_SUBSTRATE.md`**: pointer to
  `mpa-conform/docs/banach-substrate-reference.md`; usage of the
  `BanachSubstrate` class in tests and sidecar builds.
- **`docs/EXR_CHANNEL_MANIFEST.md`**: add `provenance_hash` and
  `validation_flags` channels.

## D.4. Public API (v1)

```python
# mpa_scale_solver/__init__.py
from .types import (
    # v0 unchanged
    CanonicalState, SubstrateState,
    CanonicalPoint, OperatingPoint, TranslationRule,
    GamutSpec, RegimeReading,
    # v1 additions
    LookupTableField, TangentFlowField, TranslationField, ScalingRule,
    InverseLookupSidecar,
    OperationOutput, ValidationReport, Provenance, DispatchPath,
)
from .operations import (
    # v0 sigs unchanged
    apply_translation,
    forward_sweep_invert,
    tau_obs_sweep,
    regime_at,
    gamut_classify,
    intent_map,
    validate_driver_profile,
    # v1 wrapped variants
    apply_translation_wrapped,
    forward_sweep_invert_wrapped,
    tau_obs_sweep_wrapped,
    regime_at_wrapped,
    gamut_classify_wrapped,
    intent_map_wrapped,
    validate_driver_profile_wrapped,
)
from .flow import flow
from .banach import BanachSubstrate
from .sidecar import build_sidecar_for_banach          # convenience
from .gfdr_model import (
    vertex_regime, alpha_s, plateau_height,
    generate_locus, interp_locus, locus_residual,
)

__version__ = "1.0.0"
```

---

# Section E — acceptance for this build session

1. v0 fixture regression passes unchanged.
2. Banach camera test passes with `max|residual| ≤ 0.001`.
3. v1 camera test (legacy `aging_log`) still passes — back-compat
   intact.
4. Seed-corpus integration passes (three real profiles + Banach).
5. Sidecar dispatch test passes (with + without; same output;
   correct provenance).
6. Validation test passes (each flag fires when triggered).
7. Provenance test passes.
8. `pip install -e .` works in a fresh venv.
9. README, CLAUDE.md, docs/* updated.
10. Tarball at `H:/mpa-scale-solver/dist/mpa_scale_solver-1.0.0.tar.gz`.
11. Commit + push to `github.com/ronviers/mpa-scale-solver` (MIT). Tag
    `v1.0.0`. Report SHA.
12. Append session log row to `mpa-scale-solver/README.md`.

**Resist scope creep.** JAX, differentiability, Bayesian inversion,
N-mode, full I1–I5, non-Markovian Caputo (β_mem < 1), learned
translation fields, cross-substrate ops, active learning, streaming,
MCP server, real-time scrubbing, 3D/VR phase portrait, native port —
none of these are in v1. Each is its own session, sequenced per the
north star.

---

# Section F — sibling-repo handoff updates

After v1 ships:

- **`mpa-conform/docs/ROADMAP.md`**: mark scale-solver v1 shipped; flag
  the curator-side inverse-table production session as the next unlock
  for mpa-conform.
- **`mpa-conform/conformer/compute/inversion.py`**: optionally
  rewire to call `mpa_scale_solver.forward_sweep_invert_wrapped` if
  validation + provenance are wanted in the bundle's audit trail.
  Optional, not required for v1.
- **`mpa-central/SUITE_BLOCK_IN.md`**: scale-solver row updates to
  "Python v1.0.0; native port at v6."
- **`mpa-atlas/`**: no edits — schema unchanged at v2.0; receipts
  unchanged.
- **`mpa-scale-solver-v1-handoff.md`** (this file): move to
  `archive/` after session ships.

---

# Section G — the standing warning

The Python v0 reference passes its tests. v1's additive surface
(continuous flow, tangent flow, Banach test, sidecar, validation,
provenance) does NOT redesign v0 — it extends. If you find yourself
changing v0's seven-operation signatures, the operation semantics, or
the test fixtures — stop. v0 is the established baseline; v1 is the
post-Wilson-Kadanoff-closure capabilities riding on top of it.

If you find yourself reaching for JAX, for Bayesian primitives, for
N-mode, for non-Markovian Caputo — that's v2. Each is well-scoped for
its own session.

Read [`mpa-scale-solver-north-star.md`](mpa-scale-solver-north-star.md)
before scoping any v1 work. The north star is the destination; v1 is
one well-defined step toward it. Five more steps follow (v2–v6).

---

**Done. Begin with §A re-read, then §C item-by-item. Ship when §E
acceptance is met. Update §F handoffs in the same session.**
