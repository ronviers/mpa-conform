# χ-axis Convention Lock-In — What Is Known, What Is Owed

**Status.** Lock-in landed 2026-05-19, immediately after the v0.4 schema
bump. Per-substrate normalization mappings deferred; this document
names the work cleanly so the next session inherits the issue
already-named instead of re-deriving it.

**Companion to** [`lag_display_kww_extension.md`](lag_display_kww_extension.md)
(the v0.4 paper). That paper landed the C-axis apparatus; this paper
addresses the χ-axis question it raised.

---

## 1. The finding

The C-axis KWW form *transfers* across substrates with re-tuned
parameters (Session 8 cross-substrate diagnostic):

| Substrate | C RMS (1-param) | C RMS (KWW) | C RMS reduction |
|---|---|---|---|
| Glass T=0.5 (gt=s) | 0.201 | 0.025 | **8×** |
| Brain suspended velocity (gt=s) | 0.305 | 0.065 | **5×** |
| QEC p=0.001 detection-event (gt=s) | 0.007–0.5 | n/a (1-param already covers r-regime) | (framework r-regime branch sufficient) |

The χ-axis form *does not transfer* under any scalar normalization:

| Substrate | χ range | dC range | χ/dC ratio span |
|---|---|---|---|
| Glass T=0.5 | 0.116–0.42 | 0.06–0.44 | 0.95–1.93 (factor ~2) |
| Brain suspended | 0.006–0.21 | 0.92–0.98 | **0.007–0.22 (factor ~32)** |
| QEC p=0.001 | 12.06–14.02 | 0.996–1.000 | 12–14 (huge but slow variation) |

For glass, χ/dC is in [0.95, 1.93] — consistent with the FDT line
T·χ = dC at T=0.5 (predicting χ/dC = 1/T = 2). For brain, the ratio
varies by **32×** across one cell; for QEC it's an order of magnitude
above any FDT prediction. No single scalar χ_canonical = χ_emitted /
α_substrate brings the non-glass substrates onto the FDT line.

**The χ-axis problem is structural, not scale.** Each substrate's
grinder primitive emits χ in its own substrate-conventional form. Glass
happens to emit FDR-dimensionless χ where the FDT line directly applies;
brain and QEC emit χ in conventions that require functional (not just
scalar) mappings onto canonical χ.

## 2. What is locked in this session

### 2.1. Bundle metadata field

[`walk_library.py`](../../conformer/curator/walk_library.py) emits two
fields in `observable.metadata` per cell:

```json
"chi_convention": "fdr_dimensionless" | "substrate_emitted_uncalibrated",
"chi_convention_note": "<per-substrate human-readable rationale>"
```

Per-substrate values are declared at module level:

```python
_CHI_CONVENTION_BY_SUBSTRATE = {
    "glass":   "fdr_dimensionless",
    "brain":   "substrate_emitted_uncalibrated",
    "quantum": "substrate_emitted_uncalibrated",
}
```

with paragraph-long notes for each substrate documenting the evidence
and what's owed.

### 2.2. Visualization respect

[`banach_overlay.py`](../../conformer/compare/banach_overlay.py) reads
`chi_convention` from the bundle and renders accordingly:

- **`fdr_dimensionless`** (glass): predicted/banach χ traces at full
  opacity, RMS comparison meaningful, no callout.
- **`substrate_emitted_uncalibrated`** (brain, QEC): predicted/banach
  χ traces at 35% alpha (pale gray), labeled "canonical; chi
  uncalibrated for this substrate", with an explicit yellow callout
  box on the χ panel: *"empirical and model curves live in different
  coordinate spaces; normalization owed."*

The C-axis treatment is unchanged. The KWW form (when bundle has the
6-vector or substrate-default prior) renders identically across
substrates; only the χ panel changes.

### 2.3. C-axis y-limit clamping

Side-effect of the per-window trail-vector observables having very
different natural scales on brain and QEC (e.g., 500× the aggregated
C). The y-limits of both panels are now clamped to empirical + model-
curve range, so the per-window fan extends outside the frame on
substrates where it would otherwise dominate the autoscale.

### 2.4. All 60 cells re-extracted

`chi_convention` and `chi_convention_note` now ride on every bundle.
Verified across all three substrates' canonical cells.

## 3. What is owed (per-substrate normalization mappings)

Each substrate with `chi_convention = "substrate_emitted_uncalibrated"`
owes a translation from substrate-emitted χ to FDR-canonical χ. The
translation is **substrate-bespoke** (per RULES §10: inherit substrate
vocabulary, do not invent); it requires substrate-domain expertise to
identify the right mapping.

### 3.1. Brain (neural-population)

What we observed at brain__suspended__velocity:

| dt | C | dC | χ | χ/dC |
|---|---|---|---|---|
| 1 | 0.085 | 0.915 | 0.006 | 0.0066 |
| 8 | 0.072 | 0.928 | 0.043 | 0.046 |
| 38 | 0.045 | 0.955 | 0.131 | 0.137 |
| 174 | 0.025 | 0.975 | 0.203 | 0.208 |
| 794 | 0.025 | 0.976 | 0.212 | 0.217 |
| 3621 | 0.024 | 0.976 | 0.210 | 0.215 |

χ grows roughly logarithmically in dt while dC stays nearly constant
above 0.9. No FDT-line interpretation applies as-emitted.

Candidates worth investigating with brain-substrate domain input:

- **χ_emitted is integrated response** ∫₀^dt R(s) ds where R is the
  neural-population response function. Canonical χ would be the
  FDT-consistent form involving derivatives of C. Translation requires
  knowing what the primitive emits internally — see
  [mpa-brain's primitive module](https://github.com/ronviers/mpa-brain).
- **χ_emitted has time-extensive normalization** that grows with dt;
  canonical χ would be normalized by something like sqrt(dt) or t_w.
- **χ_emitted is bookkeeping for a separate observable** (e.g., the
  number of context-switches accumulated since snapshot) and is not
  the FDT susceptibility at all.

The neuroscience literature for the relevant model class (whatever
specific neural-population dynamics mpa-brain implements) likely names
which it is. Owed: a follow-on session with that lookup.

### 3.2. QEC (surface-code)

What we observed at quantum__p1e-03__detection-event:

- χ range ≈ 12.06–14.02, fluctuating around ~13 with no clear trend
- C range ≈ 0.0002–0.004, essentially zero (r-regime per RULES §7)
- p_base = 0.001, t_obs = 24958, so expected events per realization ≈
  25; χ ≈ 13 is consistent with cumulative-event accumulation modulo
  some normalization

Likely candidates for canonical χ:

- **χ_canonical = χ_emitted / (p_base · dt)**: normalizes by expected
  total events; gives a dimensionless ratio.
- **χ_canonical = χ_emitted / √(p_base · dt)**: variance-scale
  normalization (Poisson statistics); gives a dimensionless deviation.
- **χ_canonical = (χ_emitted - dt·p_base) / dt**: subtract the
  expectation, normalize by time; gives a per-step deviation.

The surface-code literature for FDT-violation in syndrome dynamics
(if such literature exists) would name which is right. Owed: a
follow-on session with that lookup, or with a discussion with someone
who works on surface-code aging.

## 4. The structural architecture

The chi_convention metadata field is the **slot** where per-substrate
χ translations land. The current values
(`fdr_dimensionless`, `substrate_emitted_uncalibrated`) are the
minimum useful taxonomy. When a substrate's translation is identified,
the field can extend to e.g.:

```json
"chi_convention": "fdr_scalar_normalized",
"chi_normalization": {
    "factor": 0.0066,
    "factor_source": "fitted_from_T=0.5_dt_1_anchor",
    "rationale_doc": "https://path/to/brain_chi_normalization_v1.md"
}
```

or

```json
"chi_convention": "fdr_functional_normalized",
"chi_normalization": {
    "form": "translate_function_id",
    "function_id": "qec_poisson_normalization_v1",
    "params": {"p_base": 0.001, "t_obs": 24958}
}
```

The schema's `additionalProperties: true` on `observable.metadata`
already allows these extensions; no v0.5 schema bump needed for the
per-substrate mappings.

**The eventual long-term home, per
[`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../../mpa-lens-solver/docs/CHARACTER_FRAMING.md):**
the TranslationField shape extension. Per-substrate observable
conventions live on the substrate's translation field; canonical
inversions consume the translated form. v0.4 lock-in is the *bundle-
level* declaration; TranslationField is the *inversion-level*
consumption.

## 5. What this lock-in does NOT do

- **Does not assert glass's χ is "right" in any absolute sense.**
  Glass's χ happens to be FDR-dimensionless because of how mpa-central's
  glass grinder primitive normalizes it. A different glass primitive
  with a different convention could emit non-canonical χ; the field
  declares the convention per-cell, not per-substrate-class-globally.
- **Does not produce a 6-param fit yet.** The 6-vector slot in
  `fit_provenance.fitted_params` is defined (v0.4); inversion that
  actually fits the 6-vector remains deferred. For non-glass substrates,
  the χ-axis being uncalibrated means the 6-param inversion couldn't
  meaningfully include X (the FDT-violation ratio) until the substrate's
  χ is canonical.
- **Does not invent normalizations for brain or QEC.** The candidates
  in §3 are *hypotheses* worth checking, not declarations. The
  substrate-domain literature has to settle each one.

## 6. The minimum next-session move

Two viable single moves:

1. **Brain's χ-normalization lookup.** Find what the neural-population
   primitive in mpa-brain actually emits as χ. Identify the canonical
   form. Land the translation as either a scalar normalization (if
   surprisingly scalar) or a functional translation. Update the
   bundle's chi_convention.

2. **QEC's χ-normalization lookup.** Same exercise for surface-code
   detection-events. The Poisson statistics hypothesis (§3.2) is
   testable from the cell data alone — fit `χ ~ a + b·sqrt(p_base·dt)`
   across cells; if the fit is clean, that's the normalization.

Either is a single session's work, both lead toward the
substrate-thermodynamic content for that substrate becoming visible
in the bundle. The v0.4 + chi-convention lock-in is the architectural
scaffolding; these are the load-bearing fills.

## 7. Receipt

| Component | State |
|---|---|
| `chi_convention` field in `observable.metadata` | shipped |
| Per-substrate declarations (glass / brain / QEC) | shipped |
| `chi_convention_note` paragraph per substrate | shipped |
| banach_overlay pale-rendering for uncalibrated χ | shipped |
| C-panel y-limit clamping | shipped |
| All 60 cells re-extracted | done |
| Production comparison PNGs re-rendered | done |
| Brain χ-normalization mapping | **owed** (next session) |
| QEC χ-normalization mapping | **owed** (next session) |
| TranslationField shape extension | **owed** (mpa-lens-solver session) |

---

*Earned at the Session 8 cross-substrate brain + QEC diagnostics
(2026-05-19), immediately after the v0.4 schema bump. The diagnostics
confirmed the C-axis apparatus transfers; the χ-axis structural
mismatch is what required this lock-in.*
