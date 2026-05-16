# Banach substrate — calibration reference

The Banach substrate is the canonical reference instance of the cdv1
universal two-mode kernel with parameters normalized to framework-default
values and identity translation field. It lives as a concrete artifact
in `mpa-conform` for calibration, testing, and round-trip validation
across the MPA suite.

---

## State space and generator

| Component | Form |
|---|---|
| **Canonical state at depth ν** | `(chit_ν, γ_AB^ν, regime_ν, …)` — the universal two-mode kernel's canonical coordinates with ν as iteration depth |
| **Generator (continuous form)** | `C^ν = exp(ν · ln C)`, where `C` is the v9 Compression Axiom contraction operator. Grounded via v9 receipts §RG closure (Markovian scope, `β_mem = 1`, where the Banach substrate sits) |
| **Generator (integer form)** | `C^N` for `N ∈ Z+`. Snapshot of the continuous flow when discrete iterations are preferred |
| **Depth axis** | `ν ∈ R+` (continuous) or `N ∈ Z+` (integer). Also serves as `τ_obs` |
| **Translation field** | Identity. Substrate-native ≡ canonical |
| **Gamut** | Image of the trajectory in canonical space; asymptotic convergence toward `M_2` (v9 §Boolean section) |
| **Initial state** | `(chit_0, γ_AB^0)` — free parameters. The c-band start `chit_0 ≫ 0` is canonical so the trajectory traverses the full `c → s → r` migration interior |

---

## Normalization manifest

Parameter values on the Banach substrate. Real substrates carry non-default
values; the deviation is the substrate's fingerprint.

| Parameter | Value | Justification |
|---|---|---|
| `α_{σ,0}` (heat-tax entropy coupling) | `1` | Dimensionless by homogeneity of `L_{n+1} = L_{n+1}^{(0)} + α_σ ⟨σ_n⟩ + α_Σ ⟨Σ_n⟩` (entropy in nats, `⟨σ_n⟩` rate, `L_{n+1}` rate); canonical normalization to 1 |
| `α_Σ` (heat-tax stress coupling) | `1` | Dimensionless by parallel homogeneity on the stress channel; canonical normalization to 1 |
| `β_mem` (Caputo memory exponent) | `1` | Markovian boundary of the Mittag-Leffler family: `E_1(z) = e^z`. Substrate sits exactly at the boundary by construction |
| `ε_residual` (substrate-conditional compression residual) | `0` | Perfect contraction at the *information* level: no residual substrate-conditional content after compression. Limit of `ε → 0` in v9 §Compression Axiom. **Distinct from the kinetic contraction rate** — see note below. |
| `ρ_sat` (Lamb saturation density) | `1` | Natural-units normalization |
| `τ_c` (memory time) | `1` | Natural-units normalization |
| `D_noise` (stochastic noise scale) | `0` | Deterministic substrate — no stochastic noise channel |

The Banach substrate is the unique instance where every parameter sits at
its canonical-default value. Asymptotic-Closure Principle (see
`asymptotic-closure-proposal.md`) holds for the physical-substrate
population; the Banach substrate is the limit point those substrates
approach.

**Note on the two ε's** (clarified 2026-05-16, Q1 of the v1 scale-solver
build session):

| Symbol | Meaning | Banach value |
|---|---|---|
| `ε_residual` | Substrate-conditional information left after compression | `0` (perfect contraction at the information level; identity translation) |
| `ε_kinetic` | Spectral-gap eigenvalue of `ln C` — sets the per-step canonical-state contraction rate under iteration | `exp(-1)` ≈ 0.368 (equivalent to `λ_chit = λ_gamma = 1` in the closed-form `state_at(ν)`) |

The two are different objects. `ε_residual = 0` says "no substrate-
conditional content survives compression"; `ε_kinetic = exp(-1)` says
"the canonical state contracts by `exp(-1)` per unit `ν` under the RG
flow generator". The v1 `BanachSubstrate.state_at(ν)` implementation
uses `λ = 1`, which corresponds to the second `ε`. Earlier versions of
this doc collapsed the two; the table above keeps them separate.

---

## Operations

Available to consumers:

| Op | Signature | Returns |
|---|---|---|
| `state(ν, chit_0, γ_0)` | `R+ × R × R → CanonicalState` | Canonical state at depth ν |
| `trajectory(ν_max, chit_0, γ_0)` | `R+ × R × R → VectorField` | Continuous flow from `ν=0` to `ν_max` |
| `observables(ν, …)` | `R+ × … → {α_s, P_s, X_c, X_r, N_f, regime}` | Per-regime invariants. Delegates to `mpa-solver.fit_invariants` evaluated at `state(ν)` |
| `regime(ν, …)` | `R+ × … → {c, s, r, k_frust}` | Vertex regime classification |
| `flow_spectrum()` | `→ list[complex]` | Spectrum of `ln C` — natural frequencies of the framework's RG flow in depth coordinates. Continuous form only |

---

## Use cases

- **`mpa-scale-solver` camera test.** Test fixture for
  `tests/test_camera_migration.py`. Residuals measure implementation
  against framework default rather than against a handcrafted synthetic.
- **RFC-S §5 round-trip validation.** Calibrated reference instance
  above the named real-substrate references (surface-code QEC,
  habit-extinction). First link in the validation chain with no
  observational confound.
- **Asymptotic-Closure Principle's primary positive instance.** The
  substrate where the framework's asymptotic-only boundary values are
  attained by construction. Real substrates point at the Banach
  substrate's values; the Banach substrate sits at them.
- **Auto-remap rule canonical form.** RFC-S Appendix B item 1: the
  Banach substrate's `γ`-scaling rule under `ν` is the leading-order
  canonical auto-remap rule. Other substrates carry substrate-conditional
  refinements.

---

## Continuous form

Continuous flow `C^ν = exp(ν · ln C)` is grounded by `v9_receipts.md`
§RG closure — the Wilson–Kadanoff structural equivalence, closed by
composition via cdv1's heat-tax + Mori–Zwanzig + slow-manifold
construction. The conjugating isometry is `φ = Π_slow`.

Proven scope is the Markovian / spectral-gap regime (`β_mem = 1`).
The Banach substrate sits at `β_mem = 1` per the normalization
manifest above — exactly in proven scope. Continuous form is
implementable. Integer-N is available as a discrete snapshot when
preferred.

Non-Markovian Caputo (`β_mem < 1`) uses fractional-RG generalization
per v9 receipts §RG closure substrate-scope note; that regime is not
the Banach substrate's home and does not affect this reference.

---

## Implementation falsifiers

A Banach-substrate implementation is broken if:

- Its trajectory does not converge asymptotically toward `M_2` under
  flow (contradicts v9 Compression Axiom).
- Its gFDR signatures at depth `ν` do not match cdv1's per-regime
  invariants evaluated at `state(ν)` to numerical-precision tolerance
  (contradicts cdv1 §gFDR signatures).
- Its `k_frust(ν)` varies with `ν` (contradicts v9 §Scale-relativity).
- Its three-way identity `α_s = β_mem = anomalous heavy-traffic exponent`
  breaks at any depth.

---

## Scope

- **Lives in `mpa-conform`** (this repo) as a calibration artifact, not
  in `mpa-atlas` (cdv1 / v9) as framework spec.
- **Vendored by `mpa-scale-solver`** for the camera test.
- **Read by `mpa-auditor`** through the round-trip-validation chain.
- **Does not add empirical content to cdv1 or v9.** It is one calibrated
  instance of the framework's existing equations, used as reference.

---

## Provenance

| Source | Section | Imported |
|---|---|---|
| v9 compressed | §Compression Axiom | `C`, `ε < 1`, Banach contraction |
| v9 compressed | §Scale-relativity | `τ_obs` as camera; `γ` scales; `k_frust` invariant |
| v9 compressed | §Boolean section | `M_2` as asymptotic terminal attractor |
| v9 compressed | §Asymptotic closure | Structural identity instanced by the substrate |
| v9 receipts | §RG closure | Wilson–Kadanoff structural equivalence (closed by composition; grounds continuous form in Markovian scope) |
| v9 receipts | §Compression Axiom | `ε < 1` Banach contraction; closure status referencing §RG closure |
| cdv1 compressed | §Universal two-mode kernel | Dynamics at each depth |
| cdv1 compressed | §gFDR signatures | Per-regime invariants |
| cdv1 compressed | §The chit unit | `chit = ln(G_0/L)` |
| cdv1 compressed | §Heat-tax tower | `α_{σ,0}`, `α_Σ` recursion |
| cdv1 compressed | §Caputo fractional memory | Mittag-Leffler family with `β_mem = 1` Markovian boundary |
| mpa-atlas RFC-S | §1, §5 | Canonical representation, round-trip validation |
