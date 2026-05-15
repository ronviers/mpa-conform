# `mpa-scale-solver` bootstrap — fork handoff

**You are a fresh Claude Code session. This handoff is self-contained.**

**Your task: create a new sibling repo `H:\mpa-scale-solver`.** Parallel to `mpa-solver`, `mpa-auditor`, `mpa-conform`, `mpa-atlas`. The repo does not exist yet. You are the first session.

**First move:** read this entire document, then [`H:/mpa-central/SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md), then [`H:/mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md`](../../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md). Confirm scope + the name with the user (`mpa-scale-solver` is the proposed default; the user may adjust). Then create the repo.

---

## 1. Why this repo exists

**`mpa-solver` ships the framework's forward-physics kernel.** Universal two-mode kernel + Lamb closure + Caputo memory + DynamicBath + Milstein SDE + gFDR observables + linearization. Given a canonical operating point `(chit, gamma_AB, ...)`, it integrates trajectories, runs ensembles, extracts FDR observables. *Substrate-neutral physics math.*

**`mpa-scale-solver` ships the framework's scale-management kernel.** Universal RG-flow operator + translation-field evaluator + regime classification + gamut + the five intents. Given a substrate observation in substrate-native coordinates plus a τ_obs camera frame, it projects to canonical representation. Given canonical state plus a τ_obs trajectory, it walks the flow. *Substrate-neutral scale-management math.*

The two sit at opposite walls of the compute layer. **Physics solver:** "given a canonical point, what does the trajectory look like?" **Scale solver:** "given an observation and a camera, what canonical point is this *at*, and where does it move if I change the camera?"

### The diagnosis that drove this repo

`mpa-conform` v0.2 development surfaced a load-bearing realization (logged 2026-05-15):

> v9 Foundational Principle #2 — *observer-driven scale management; τ_obs is the camera; canonical representation is observer-relative* — is not a sidecar concern. It's the entire compute scaffolding. Every observation is a sample of an RG-flow trajectory at some camera frame. RFC-S §1: *"The canonical representation at p = τ_obs is the fixed-point set of the Compression Axiom's RG flow at level n. Cross-position structure (auto-remap as τ_obs moves) is the flow trajectory itself."* RFC-S Principle #6: *"MPA scale management is **infinite**. Infinity-machinery is imported directly, not patched on case-by-case."*

The mpa-conform inversion port (Session 1, 2026-05-15) handled τ_obs as bundle *metadata* — declared, not compute-active. Fits saturated at the analytical model's tau range for any substrate whose native scale didn't accidentally match. Per the user's diagnosis: **"if scale management was not intense, it was not going to work."** Intense scale management needs its own kernel. That kernel is this repo.

### Architectural authority

[`H:/mpa-central/SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md) (2026-05-15) — program-wide structural commitment. The compute layer is `mpa-solver` + `mpa-scale-solver` (this repo) + `mpa-conform`. Viewer layer reads what the compute layer produces. This file is downstream of SUITE_BLOCK_IN; if anything here conflicts, SUITE_BLOCK_IN wins.

---

## 2. Read before scoping

Five documents, in order:

1. [`H:/mpa-central/SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md) — the three-layer split (spec / compute / viewer) and what owns what.
2. [`H:/mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md`](../../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md) §§0–5 — the spec authority for everything in this repo. Read in full. (RFC-S §6 onward is compactification + edge cases; useful but not first-session-critical.) **Read [`H:/mpa-atlas/CLAUDE.md`](../../mpa-atlas/CLAUDE.md) (thin-RFC discipline) before opening any mpa-atlas document.** `mpa-scale-solver` does not edit `mpa-atlas`; it reads it.
3. [`H:/mpa-atlas/framework/v9_compressed.md`](../../mpa-atlas/framework/v9_compressed.md) §Foundational principles + §Scale-relativity + §Compression Axiom — the structural anchors. Compression Axiom is the RG-flow source.
4. [`H:/mpa-atlas/framework/cdv1_compressed.md`](../../mpa-atlas/framework/cdv1_compressed.md) §gFDR signatures (especially "*chit reading of the s → r migration is the Apparatus's primary cross-substrate test*") — the named load-bearing prediction the scale solver must service.
5. [`H:/mpa-solver/CLAUDE.md`](../../mpa-solver/CLAUDE.md) + [`H:/mpa-solver/README.md`](../../mpa-solver/README.md) — the **shape** to mirror. mpa-solver is what this repo is parallel-to; its discipline (named family of operations, what-doesn't-live-here boundary, reproducibility commitment, sibling-repo relationships) is the template.

One more for the input shape:

6. [`H:/mpa-atlas/schema/driver-profile.v0.2.json`](../../mpa-atlas/schema/driver-profile.v0.2.json) — `translation_field` + `gamut` + `intents` are this repo's primary inputs.

---

## 3. What lives here (and what doesn't)

**Mirroring mpa-solver's discipline.** The repo is a **numerical / algebraic kernel + one named family of operations**, not a framework, not a substrate model.

### Lives here

- **RG-flow operator** (RFC-S §1). Given canonical state + τ_obs + translation field, evaluate canonical representation at any point along the flow. Vectorized over τ_obs grids.
- **Translation-field evaluator.** Lookup-table form (driver profile carries the table); parametric form (driver profile carries a closed-form rule); learned form (driver profile carries fitted parameters of a chosen functional family). Forward direction only per `mpa-auditor` §Q13 — `canonical → substrate-native`. The backward map (`substrate → canonical`) is forward-sweep search; the solver supplies the sweep machinery.
- **Regime classifier at τ_obs** (v9 §Scale-relativity). `regime(canonical_state, tau_obs) → {c, s, r, k_frust}`. Same trail reads c at narrow τ_obs, s at mid, r at wide.
- **Gamut operations** (RFC-S §2). `in_gamut(canonical_state, tau_obs, gamut_spec) → bool + diagnosis`. Substrate's gamut is the *image* of its RG trajectory in canonical space.
- **Five-intent mapping operators** (RFC-S §3). I1 regime-preserving, I2 drive-faithful, I3 capacity-preserving, I4 persistence-preserving, I5 signature-preserving. The rule per RFC-S §3: *"scale uniformly along the gamut to fit, preserving the named invariant"* — one operation, intent-parameterized.
- **τ_obs sweep — RG-flow trajectory walker.** RFC-S §1: *"Cross-position structure (auto-remap as τ_obs moves) is the flow trajectory itself; the driver supplies the rule that realizes it (form open — Appendix B)."* The solver provides the walker; the driver profile provides the rule.
- **Round-trip validation** (RFC-S §5). Forward + round-trip residuals against reference datasets, per-intent metric. Acceptance gating for driver profiles. Returns residuals; the caller decides accept/reject.
- **Auto-remap rule (leading order).** RFC-S Appendix B item 1 is OPEN; the solver ships a leading-order linear rule (`τ_canonical = τ_substrate / τ_obs`, `γ_canonical = γ_substrate` identity) and the API surface that lets a driver profile override it with substrate-conditional form. Refinement of the leading-order form lives in `mpa-atlas`; the solver exposes the surface, doesn't decide the math.

### Does NOT live here

- **Substrate models.** No laser, no surface-code QEC, no glass, no neural specifics. Substrate-conditional translation fields are carried in driver profiles (consumer-produced); the solver reads them.
- **Forward physics.** ODE integration, ensemble, correlator math — that's `mpa-solver`.
- **Driver profile production.** That's `mpa-conform`'s curator + researcher paths. The solver *consumes* driver profiles; it does not produce them.
- **Data ingestion.** CSV, raw time-series — `mpa-conform`. The solver receives canonical-shaped state + driver profile.
- **Audit classification.** Four-category miss enumeration — `mpa-conform` (porting from `mpa-auditor/engines/audit-engine.js` per `SUITE_BLOCK_IN.md`).
- **LLM / MCP.** Consumer concern.
- **Validation beyond RFC-S §5 round-trip + NaN/Inf gating.** Caller responsibility.

If you find yourself adding any of the above — stop. It belongs in a consumer repo. (Same rule mpa-solver carries.)

---

## 4. The API surface (v0)

Naming is a v0 proposal; refine in the first session if a better convention surfaces. Mirror mpa-solver's idiom: stateless free functions on plain structs, no global state, deterministic.

### Core operations

```
apply_translation(canonical_state, translation_field, tau_obs) -> substrate_state
    // RFC-S §1 forward direction. canonical -> substrate-native projection
    // at the chosen camera frame. Forward-only per mpa-auditor §Q13.

forward_sweep_invert(substrate_state, translation_field, tau_obs,
                     canonical_grid) -> canonical_state + residual
    // RFC-S §1 trajectory + mpa-auditor §Q13 forward-only inversion.
    // Walks canonical_grid, applies apply_translation to each candidate,
    // returns the canonical state with lowest substrate-space residual.
    // Replaces the (ill-posed) substrate -> canonical backward map.

tau_obs_sweep(canonical_state_at_p0, translation_field, tau_obs_grid)
    -> canonical_trajectory
    // RFC-S §1 cross-position structure. Walks the RG flow trajectory
    // through tau_obs_grid; returns canonical state at each frame.

regime_at(canonical_state, tau_obs) -> {c, s, r, k_frust}
    // v9 §Scale-relativity. Vertex label is tau_obs-dependent; this is
    // the function. k_frust is tau_obs-invariant.

gamut_classify(canonical_state, tau_obs, gamut_spec)
    -> {in_gamut: bool, diagnosis: {out_of_range_axis, distance, ...}}
    // RFC-S §2. Image of substrate's RG trajectory in canonical space.

intent_map(out_of_gamut_state, gamut_spec, intent_id)
    -> in_gamut_state + sacrifice_record
    // RFC-S §3. One of {I1, I2, I3, I4, I5}. Per RFC-S §3 the rule is
    // "scale uniformly along the gamut to fit, preserving the named
    // invariant" — one operation, intent-parameterized.

validate_driver_profile(driver_profile, reference_dataset)
    -> {per_intent: {forward_residual, round_trip_residual,
                     within_threshold: bool}}
    // RFC-S §5 protocol. Driver acceptance gating; the caller decides
    // pass/fail based on declared thresholds.
```

### Data shapes

- `canonical_state`: scalar `chit`, `gamma_AB`, and optional N-mode extensions (preserve mpa-solver's N-mode generalization path). Plus `tau_obs` (the camera the state is referenced to).
- `substrate_state`: opaque to the solver — whatever shape the driver profile's translation field consumes / produces. Typed as a sparse record.
- `translation_field`: as carried by the driver profile (RFC-S §4 + `driver-profile.v0.2.json`). Three forms supported: lookup table, parametric, learned. The solver dispatches on the form.
- `gamut_spec`: as carried by the driver profile (RFC-S §2). D-range × τ_obs-range × persistence depth × reachable trail-class structure.
- `intent_id`: enum `{I1, I2, I3, I4, I5}`.

### Bindings (mirror mpa-solver)

- **Native library** (Rust or C++17 — see §6 for the recommended choice). Static, no system deps beyond the toolchain.
- **WebAssembly bindings.** For future viewer-side use (e.g., a static Explore-mode page that walks the τ_obs slider through a precomputed grid).
- **Python bindings.** For `mpa-conform`'s compute pipeline. Same numerical kernel called from both.

---

## 5. First-session deliverable

**Why first.** mpa-solver v0 shipped a tight 2-mode Lamb path that has been preserved bit-for-bit through v2. mpa-scale-solver v0 should ship the equivalent: a tight leading-order RG-flow operator + the API surface that consumers can call today, with the substrate-conditional refinements parked behind a clean extension surface.

**Scope.**

1. **Native library** with the seven operations from §4. Leading-order forms:
   - `apply_translation`: dispatches on translation field form. **Linear rule** as the fallback (`τ_canonical = τ_substrate / τ_obs`, `γ_canonical = γ_substrate`) — this IS the leading-order RFC-S Appendix B item 1 rule, named as such with a debt-marker pointing at the open spec question.
   - `forward_sweep_invert`: generic grid walker; takes `apply_translation` as the projection step.
   - `tau_obs_sweep`: applies `apply_translation` over a τ_obs grid; returns the trajectory.
   - `regime_at`: chit-threshold classifier (deep_c / c_near_s / s_critical / r_near_s / deep_r) — port from `mpa-auditor/math/gfdr-model.js` `vertexRegime`. k_frust input via translation field's discrete extension (substrate-conditional).
   - `gamut_classify`: range checks on declared axes (D-range, τ_obs-range, persistence depth). Out-of-gamut diagnosis names the offending axis + distance.
   - `intent_map`: ship **I5 (signature-preserving)** first — it's the audit's natural intent and the framework's primary load-bearing one per cdv1 §gFDR signatures. I1–I4 stubbed with `not_implemented`.
   - `validate_driver_profile`: per RFC-S §5 protocol; emits forward + round-trip residuals.

2. **WASM bindings** + **Python bindings**. Match mpa-solver's pattern (pybind11 if C++, pyo3 + maturin if Rust; emscripten or wasm-pack accordingly).

3. **Tests.**
   - Round-trip on a synthetic translation field: `apply_translation` then forward-sweep inversion recovers the canonical state.
   - τ_obs-sweep: an RG-invariant quantity (k_frust if carried) stays invariant; a τ_obs-dependent quantity (γ) scales as the leading-order rule predicts.
   - Regime classifier matches `mpa-auditor/math/gfdr-model.js` `vertexRegime` thresholds (parity).
   - Gamut classifier flags out-of-range axes.
   - I5 intent-map preserves regime partition + edge-type partition + k_frust on a synthetic out-of-gamut state.
   - RFC-S §5 round-trip validation runs on a synthetic reference dataset; emits residuals.

4. **One worked example.** A driver profile (synthetic, in-tree fixture) + a reference canonical state; the example walks `apply_translation`, prints substrate-native projection at three τ_obs values, walks `tau_obs_sweep` across a grid, prints the c→s→r migration. Mirrors `mpa-solver/examples/chit_sweep.cpp`.

**What's deliberately deferred (v1+, not first session):**

- N-mode generalization (preserve the extension surface; first session is 2-mode only, paralleling mpa-solver v0).
- Substrate-conditional auto-remap forms beyond the linear leading-order rule. RFC-S Appendix B item 1's exact form is an open spec question in mpa-atlas; the solver's leading-order rule is honest leading-order, refined when mpa-atlas closes Appendix B.
- I1–I4 intent operations beyond stubs.
- Learned translation-field form (the parametric + lookup forms are enough for v0).
- Sensitivity analysis / gradient passes through the flow.
- Driver-profile validation that goes deeper than RFC-S §5 round-trip + NaN/Inf.

**Acceptance test.**

1. Native build succeeds. All seven operations pass their tests.
2. WASM build succeeds; the worked example runs in a browser (open via `npx http-server -c-1` from `examples/web/`).
3. Python bindings build (`pip install ./bindings/python`); the same example runs in Python.
4. `python -m mpa_scale_solver.example` (or equivalent) emits a c→s→r migration trace on the synthetic driver profile — *this is the framework's primary cross-substrate test signature in textual form, surfaced as the solver's "hello world."*
5. Commit + push to `github.com/ronviers/mpa-scale-solver` (public, MIT, parallel to other `mpa-*`). Report SHA.

---

## 6. Repo scaffolding

Mirror mpa-solver's layout. Choose **one** of these two tech stacks for v0:

### Option R — Rust + WASM + Python (recommended for 2026 builds)

```
H:/mpa-scale-solver/
├── Cargo.toml
├── LICENSE
├── README.md
├── CLAUDE.md
├── src/
│   ├── lib.rs                   # public API
│   ├── translation.rs           # apply_translation, forward_sweep_invert
│   ├── flow.rs                  # tau_obs_sweep
│   ├── regime.rs                # regime_at
│   ├── gamut.rs                 # gamut_classify
│   ├── intents.rs               # intent_map (I5 implemented, I1-I4 stubs)
│   ├── validate.rs              # validate_driver_profile (RFC-S §5)
│   └── types.rs                 # canonical_state, substrate_state, etc.
├── tests/                       # per-operation unit tests + round-trip
├── examples/
│   ├── migration_trace.rs       # the c->s->r migration worked example
│   └── web/                     # static page + WASM glue
├── bindings/
│   ├── wasm/                    # wasm-pack manifest
│   └── python/                  # pyo3 + maturin manifest
├── dev_profile.json             # gitignored (matches sibling pattern)
└── .gitignore
```

Why Rust: matches research-findings §3 / §5 recommendation, memory safety, native WASM target, mature pyo3/maturin. (Research synthesis lives at `H:/mpa-auditor/docs/mpa_conform_unified_report.md`.)

### Option C — C++17 + WASM + Python (mirror mpa-solver exactly)

```
H:/mpa-scale-solver/
├── CMakeLists.txt
├── LICENSE
├── README.md
├── CLAUDE.md
├── src/
│   ├── translation.cpp
│   ├── flow.cpp
│   ├── regime.cpp
│   ├── gamut.cpp
│   ├── intents.cpp
│   ├── validate.cpp
│   └── version.cpp
├── include/mpa_scale_solver/
│   └── *.hpp                    # public API + types
├── tests/
├── examples/
├── bindings/
│   ├── wasm/                    # emscripten + embind glue
│   └── python/                  # pybind11 + glue.cpp + pyproject.toml
└── .gitignore
```

Why C++: tight parity with mpa-solver; same toolchain, same idioms, same build flags. Consumers vendoring both repos get one toolchain story.

**Recommended:** Option R (Rust). The user has named "thin and bespoke, 2026 not 2022" as discipline (memory `feedback_thin_modern_engineering.md`); Rust is the 2026-native answer for a new WASM+Python kernel. mpa-solver's C++ is a 2024 sunk-cost legacy that doesn't constrain new sibling repos.

But: **confirm with the user before deciding.**

### Per-machine config

Add `H:\\mpa-scale-solver` to BOTH `permissions.additionalDirectories` AND `sandbox.filesystem.allowWrite` in `~/.claude/settings.json` (mirror the pattern documented in the user's machine-level `CLAUDE.md`).

`.gitignore` excludes `dev_profile.json`, `target/` (Rust) or `build/` (C++), `.claude/`, `__pycache__/`, `*.wasm` build artifacts (if not committed).

`git init` + `gh repo create ronviers/mpa-scale-solver --public --source=H:/mpa-scale-solver --remote=origin --push` (the user's machine CLAUDE.md documents this pattern + the no-prior-origin caveat).

Gitleaks pre-commit hook: `winget install gitleaks` (probably already installed; the user's machine CLAUDE.md documents the pattern). Pre-commit script: `exec gitleaks protect --staged --redact`.

---

## 7. Math caveats — anticipated

Mirror mpa-solver's CLAUDE.md "Math caveats" section. These are the calls the first session will probably need to make:

### 1. The leading-order auto-remap rule is honest leading-order

RFC-S Appendix B item 1 is OPEN. The v0 solver ships:

```
tau_canonical = tau_substrate / tau_obs       // linear rescaling
gamma_canonical = gamma_substrate            // identity at leading order
chit_canonical = chit_substrate              // identity at leading order (debatable)
```

This is the simplest substrate-class-agnostic rule. v9 §Scale-relativity says "γ scales with τ_obs" but doesn't pin the form; the linear rule is the leading-order guess. Substrate-conditional refinements (e.g. dimensional-analysis-derived powers of τ_obs in γ) belong in per-substrate driver profiles, overriding the solver's default.

Document this clearly. The solver's job is to expose the *surface* for the refinement, not to decide the math. mpa-atlas owns the math; the solver consumes whatever mpa-atlas spec'd.

### 2. The five intents share a rule, not five operations

RFC-S §3 names *one* mapping operation per intent: *"scale uniformly along the gamut to fit, preserving the named invariant."* The five intents differ in *which* invariant is preserved, not in the operation's structure. v0 ships I5 (signature-preserving, the audit's primary intent); I1–I4 stubs return `not_implemented`.

This is NOT "I1 first because it's the simplest" — I5 first because it's the load-bearing intent for the framework's primary cross-substrate test (cdv1 §gFDR signatures' "s → r migration"). The order matters for what consumers can do with v0.

### 3. k_frust is RG-invariant; the solver enforces it as a check, not a derivation

v9 §Three typed objects: *"k_frust is a topological invariant of the coupling graph (Mézard–Parisi–Virasoro). Not resolvable by D."* The solver's `tau_obs_sweep` checks that any k_frust carried in canonical state stays invariant across the sweep; a sweep that produces a k_frust delta is a bug, reported as such.

### 4. Driver-profile translation fields are opaque to the solver

The solver dispatches on the *form* (lookup / parametric / learned) but does not inspect the substrate-specific content. A glass driver profile that returns garbage at high τ_obs is the driver's bug, not the solver's. The solver's contract: given a well-formed translation field per `driver-profile.v0.2.json`, produce a numerically stable canonical → substrate-native projection.

---

## 8. Reproducibility commitment

Mirror mpa-solver. Bit-identity across runs is non-negotiable:

- Same `(canonical_state, translation_field, tau_obs, ...)` → byte-identical output.
- WASM and native builds produce numerically-identical outputs for the same inputs (within IEEE-754 determinism limits — single-precision drift between platforms is a bug).
- Python bindings call the same kernel; same input → same output as native.
- `-ffast-math` forbidden.

Any change that alters output requires a patch bump and a fresh captured fixture, documented in the commit.

---

## 9. Acceptance for this bootstrap session

1. `H:/mpa-scale-solver` exists; `git init`d; GitHub repo `ronviers/mpa-scale-solver` created and pushed.
2. Scaffolding from §6 in place (Option R or C — user-confirmed).
3. Machine `~/.claude/CLAUDE.md` settings extended with `H:\\mpa-scale-solver` permissions.
4. **The leading-order v0** from §5 builds (native + WASM + Python), tests pass, the worked example runs in all three contexts.
5. README + CLAUDE.md drafted; CLAUDE.md follows mpa-solver's pattern (what-lives-here, what-doesn't, math caveats, reproducibility, sibling-repo relationships).
6. The c→s→r migration trace from §5 acceptance test 4 prints cleanly — *this is the artifact the framework's primary cross-substrate test runs on*.
7. Append a Session Log row to `mpa-scale-solver/README.md`.
8. Commit + push; report SHA.
9. Update `H:/mpa-central/SUITE_BLOCK_IN.md` compute layer table to add `mpa-scale-solver` between `mpa-solver` and `mpa-conform`.
10. Update `H:/mpa-conform/docs/ROADMAP.md` to note that the scale solver is now vendorable; the v0.2 schema + curator rewrite per the program-wide rebalance can proceed.

**Resist scope creep.** The substrate-conditional refinements, the full intent operations, the N-mode generalization, the learned translation field — none of these are first-session deliverables. The first session ships the leading-order kernel + the API surface + the bindings. Everything else is its own session, sequenced by the user.

---

## 10. Sibling-repo relationships

| Repo | Relationship |
|---|---|
| `mpa-atlas` | Spec authority for everything in this repo. RFC-S §§1–5 + v9 + cdv1 are read-only. Spec questions route via `mpa-conform/docs/foundational-questions.md` → `mpa-auditor/docs/foundational-questions.md` → mpa-atlas Appendix B pipeline; do NOT edit mpa-atlas from here. |
| `mpa-solver` | **Sibling kernel.** Forward physics. Distinct named family of operations. The scale solver does not call the physics solver, and vice versa; both are consumed in parallel by mpa-conform. |
| `mpa-conform` | **Primary consumer.** Vendors this repo's Python bindings into its compute pipeline. The inversion port (mpa-conform/conformer/compute/inversion.py, Session 1 / 2026-05-15) will rewire to call `apply_translation` on entry and fit in canonical space. |
| `mpa-auditor` | **Future consumer.** Once the auditor slim-down lands (per `SUITE_BLOCK_IN.md`), the auditor will vendor this repo's WASM build for any live τ_obs camera operation that survives the slim-down (likely none — the framework grid carries precomputed canonical state per (chit × γ_AB × τ_obs)). |
| `mpa-relaxation` | **Future consumer.** Substrate experiments operate at substrate-native scales; the scale solver projects them to canonical for cross-substrate comparison. |
| `mpa-central` | Methodology + library + program-wide rules. SUITE_BLOCK_IN.md is the structural authority. RULES.md applies. |

---

## 11. References (one-stop list)

- `mpa-central/SUITE_BLOCK_IN.md` — the three-layer split. Structural authority.
- `mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md` §§0–5 — the spec authority for everything in this repo.
- `mpa-atlas/framework/v9_compressed.md` §Foundational principles + §Scale-relativity + §Compression Axiom — structural anchors. Principle #2 (τ_obs is the camera) is the load-bearing reason this repo exists.
- `mpa-atlas/framework/cdv1_compressed.md` §gFDR signatures — names the primary cross-substrate test (s → r migration via τ_obs sweep) the solver must service.
- `mpa-atlas/schema/driver-profile.v0.2.json` — translation_field + gamut + intents input shape.
- `mpa-atlas/CLAUDE.md` — thin-RFC discipline. Read before opening any mpa-atlas document.
- `mpa-solver/CLAUDE.md` + `mpa-solver/README.md` — the **shape** to mirror.
- `mpa-conform/docs/foundational-questions.md` Q-scale-management-as-compute-scaffolding — the conform-side diagnosis that drove this repo.
- `mpa-auditor/docs/foundational-questions.md` §Q16 — the auditor-side spec question (analytical gFDR model parameterization under τ_obs).
- `mpa-conform/conformer/compute/inversion.py` — the consumer code that will rewire to use the scale solver once v0 ships.

**Done. Read §§1–4 once more, then start in §5.**
