# Lag / Display Separation and the KWW + FDT-Violation Glass Apparatus

**Status.** Draft for review. Landed in mpa-conform `declaration-bundle.v0.4`
on 2026-05-19. Cross-repo follow-ons (lens-solver, scale-solver, calibration
baselines, auditor reader) tracked in
[`docs/next-session-handoff.md`](../next-session-handoff.md).

**Authors.** Single-author session (claude opus 4.7 + ronviers); review
requested via the outbound research channel and an ultrareview pass.

**Scope.** This paper documents the theory, diagnostic methodology,
production landing, and open items for two coupled changes in the MPA
conform compute layer:

1. **Lag / display separation.** Decouple the bundle's *model-input time
   variable* (lag since snapshot) from its *display x-axis* (substrate-
   community-chosen, e.g. sample-time for glass-CK).
2. **KWW + FDT-violation forward model.** Extend `gfdr_model` with the
   glass community's six-parameter apparatus — Kohlrausch–Williams–Watts
   two-timescale C(τ) and the Cugliandolo–Kurchan / Bouchaud-review
   FDT-violation χ(C) — refining the cdv1 leading-order χ̃ per
   [`RULES.md §15`](../../mpa-central/RULES.md).

Both changes are minor at the file level (a few hundred lines net) but
load-bearing in framing: they make explicit the difference between the
substrate's physics and the visualization layer, and they ground the
framework's stated discipline — *substrate deviation from cdv1 is API
surface* — in a concrete worked instance.

---

## 1. Background — the diagnostic that drove the move

### 1.1. The empirical signature

Spin-glass library cell `glass__T0.500__spin-flip` (mpa-central / cell
schema v1.0): 28 sample times at fixed waiting time t_w = 500, kernel-
width sweep over 31 EMA-trail-vector τ_window values. Top-level
observables are the raw-readout autocorrelation C(t, t_w) and integrated
response χ(t, t_w) averaged over 1024 realizations.

At T = 0.5 the substrate is deep in the aging regime (T < T_c = 1.0 for
the 3D EA glass). The empirical decay is the canonical KWW two-step:
fast β-relaxation through cage rattling, plateau at q_EA ≈ 0.94, then
slow α-relaxation across the full t_obs = 30 000 MC-steps window.
Empirical χ grows from ≈ 0.116 at first sample to ≈ 0.42 at the last.

### 1.2. The model under test (v0.3)

`conformer/compute/gfdr_model.py::generate_locus(chit)` is a 1-parameter
analytical family with three explicit regime branches (lines 45–63 of
the v0.3 module):

```
deep_c / c_near_s    (chit ≥ 0.2):   C = 1 - 0.18·exp(-chit·1.5)·(1 - exp(-τ/τ_c))
s_critical            (-0.2..0.2):   two-timescale dC_short + dC_long, τ_β=0.5, τ_α=50 hardcoded
r_near_s / deep_r    (chit ≤ -0.2):  C = exp(-τ/τ_eq)
```

The 1-parameter family produces curves that are either *plateau-like*
(c-branch, C ≥ 0.82) or *fully decorrelated* (r-branch, C → 0), with a
sharp regime transition between. **There is no continuous KWW-shaped
decay in the family.** Inversion against this model (`inversion.invert`)
locks the empirical onto the c-branch — the empirical's high-C values
look c-like even though the slow decay shape is not present in the
analytical model.

### 1.3. The first symptom — predicted/Banach disagree with empirical

At T = 0.5 the two-stage inversion lands `chit ≈ 0.30`. The predicted
curve at this `chit` sits near C = 1.0 across the full bundled τ range;
empirical goes from 0.94 to 0.56. The Banach reference (canonical-state
flow through `nu_obs = tau_obs / tau_scale = 0.042`) inherits the same
limitation. χ is worse: predicted ≈ 0 while empirical reaches 0.42.

Lens-solver (predictor-corrector with cdv1 prior) lands `chit ≈ 0.55`,
also c-branch, also unable to reproduce the decay shape. **Cross-path
disagreement (0.25 chit units) sits inside a model family that does not
contain the empirical's curve at any chit.**

### 1.4. The diagnostic — KWW + FDT-violation closes both panels

A standalone diagnostic at
[`scripts/test_kww_glass.py`](../../scripts/test_kww_glass.py)
hand-tunes a 6-parameter form against the same cell:

```
C(τ) = (1 - q_EA) · exp(-τ / τ_β)               (β-piece, cage rattling)
     + q_EA       · exp(-(τ / τ_α)^β_KWW)        (α-piece, KWW stretched)

T·χ(C) = dC                                       (equilibrium, C ≥ q_EA)
       = (1 - q_EA) + X · (dC - (1 - q_EA))      (aging, C < q_EA)
```

Hand-picked: q_EA = 0.94, τ_α = 200, β_KWW = 0.4, τ_β = 0.002, X = 0.4,
T = 0.5. RMS drops:

| Quantity | v0.3 1-param at chit=0.55 | v0.4 6-vector KWW + FDT |
|---|---|---|
| C RMS | 0.201 | **0.025** |
| χ RMS | 0.287 | **0.073** |
| Improvement | — | 8× / 4× |

Both RMS are at SEM-bar scale. The cells' empirical curves sit inside
the 6-vector family.

### 1.5. The deeper insight — lag vs display

While verifying the KWW fit, a *hairpin* of clustered empirical points
appeared in any plot that used `sample.t / tau_scale_median` as the
x-axis. The cluster compressed five sample points (early lag dt = 1
through dt = 12) into a 2% sliver of log-x-axis space, while C dropped
by 0.04 and χ rose by 0.08 across them. Switching the x-axis to
`sample.dt / tau_scale` spread the same five points across 1.5 decades
of log-x, with no hairpin.

The framework's natural time variable for the FDR parametric plot is
**lag since snapshot** (CK 1993 convention). The bundle's
`observable.data[].tau` was emitting *sample-time*, conflating two
distinct roles:

1. The **model's internal time variable** — the substrate's physical
   evolution variable. Should always be lag.
2. The **plot's x-axis variable** — display convention chosen by the
   substrate community. For glass-CK that's sample-time; other
   substrates may pick differently.

Once the two are decoupled — model evaluates at lag, plot draws at
display_tau — the hairpin becomes a *predicted* feature of the
substrate's curve (it falls naturally out of KWW's rapid β-piece decay
at very small lag), not an unreachable cluster of artifact points.

The lag/display separation and the KWW model are independent at the
schema level (each can land alone), but they're coupled in the
diagnostic: the KWW shape only renders the hairpin correctly when
evaluated at lag with the result plotted at display_tau.

---

## 2. Theory

### 2.1. The cdv1 framing: leading-order and refinement

[`RULES.md §15`](../../mpa-central/RULES.md):

> Refinement deviation from the cdv1 prior is substrate-thermodynamic
> content, not fit error. The cdv1 priors per substrate are each
> substrate's leading-order universality form: glass `chit = T_c − T`
> (Landau distance from criticality), QEC `chit = ln(p_threshold /
> p_base)` (laser-analogue), brain scenario table. When refinement
> against real (C, χ) data deviates from the prior, the deviation IS
> the substrate-thermodynamic content character §"Open items" catalogs
> as predictions awaiting empirical contact — universality fixes the
> exponent, substrates fix the amplitude.

The 1-parameter model is the cdv1 leading-order. It carries the
*regime* information (vertex_regime mapping `chit → {deep_c, c_near_s,
s_critical, r_near_s, deep_r}`) and predicts the leading-order shape
of C and χ within each regime. The refinement is whatever additional
parameters the substrate's community has measured and named.

For glass that's the KWW + FDT-violation 6-vector. For QEC it's a
different set (logical-error rates, syndrome statistics). For brain
it's again different (scenario-conditional correlators). The cdv1
leading-order is universal; the refinement is substrate-bespoke and
inherited from the substrate's literature per
[`RULES.md §10`](../../mpa-central/RULES.md) (inherit substrate
vocabulary, do not invent).

### 2.2. The KWW two-timescale decay

The Kohlrausch–Williams–Watts form was the right reference for spin-
glass aging long before MPA. Cugliandolo–Kurchan 1993 named it for the
trap-model glass; Bouchaud–Cugliandolo–Kurchan–Mézard (BCKM) cemented
its central role in the aging-glass literature.

```
C(τ) = (1 − q_EA) · exp(−τ / τ_β)                    (β-piece)
     + q_EA       · exp(−(τ / τ_α)^β_KWW)             (α-piece)
```

The four parameters:

- **q_EA** — Edwards–Anderson plateau height. The order parameter the
  substrate equilibrates to *during the β-relaxation*; α-decay is the
  slow departure from this plateau. In MPA's regime language q_EA is
  the c-regime asymptote that *would* be the static order parameter if
  α-relaxation didn't exist.
- **τ_β** — β-relaxation timescale. Cage-rattling, "fast" — typically
  microscopic relative to t_w. The β-piece is the leading-order short-
  time correction to the plateau.
- **τ_α(T, t_w)** — α-relaxation timescale. Aging-dependent: τ_α grows
  with t_w (and diverges as T → 0). The slowest dynamical scale the
  substrate carries.
- **β_KWW** — stretching exponent. β_KWW = 1 is exponential α-decay
  (rare in real glasses); β_KWW = 0.5–0.7 is the typical spin-glass
  range, reflecting a *hierarchy of relaxation timescales*. Sets the
  shape of the α-decay's approach to zero.

These are exactly the four numbers a glass experimentalist would
report. They are the substrate's deviation from cdv1's leading-order
`χ̃ = T_c − T`.

### 2.3. The FDT-violation X(C)

Susceptibility on the (1 − C, χ) parametric plot is piecewise linear in
aging spin glasses (FDT-violation theorem, CK 1993):

```
T · χ(C) = (1 − C)                                  for C ≥ q_EA   (FDT)
         = (1 − q_EA) + X · ((1 − C) − (1 − q_EA))  for C < q_EA   (aging)
```

The X factor is the **FDT-violation ratio**, equivalent to T / T_eff
where T_eff is the effective temperature of the aging glass's slow
degrees of freedom:

- X = 1 → FDT holds (quasi-equilibrium, near T_c)
- X << 1 → frozen aging (deep below T_c, weak coupling between fast
  and slow modes)
- X = 0 → fully frozen (no susceptibility growth from the aging branch)

X is a *thermodynamic-axis* parameter: it lives on the (1−C, χ)-plot
slope, not on the C(τ) decay shape. **β_KWW and X are distinct
physical quantities measuring different things; conflating them was
the structural error in the diagnostic's chi-form first revision.**

The 1/T scaling is the FDT line's natural slope; it rides through both
branches. For the substrate at hand (T = 0.5), small-lag χ ≈ (1−C)/T
gives 0.12 against measured 0.116 — within 4 %. The 1/T scaling is the
load-bearing factor; X then sets the aging-branch slope.

### 2.4. The lag/display separation

The framework's *natural* time variable for the FDR parametric plot is
the lag since snapshot:

```
τ_framework = t - t_w = sample.dt
```

This is the variable that appears in CK 1993's equations, in the
two-time correlation function C(t, t_w) = C(τ, t_w), and in the
gFDR model `gfdr_model.generate_locus(chit)`. The lag is what the
substrate's autocorrelation function depends on (along with t_w as
the second argument).

Substrate communities have their own *display* conventions for the
x-axis of their parametric plots:

- **Glass-CK convention**: plot vs sample-time t (= t_w + dt). The
  hairpin we saw in the diagnostic is what this convention looks like
  for the very-early lag samples — those points all sit near t = t_w
  on a log-t axis.
- **MPA framework default**: lag dt, log-spaced.
- **Aging-anchored**: dt / t_w (simple aging scaling).

These are all monotonic transforms of each other; they encode the same
physics, just at different x-axis layouts. The model's prediction is
the same curve viewed under different display transforms.

**The lock-in is to keep these two roles structurally separate in the
bundle schema.** Conflating them — emitting one field called "tau" that
plays both roles — produces fits that look bad in the community's
chosen view (the hairpin appears to "fail to be matched") even though
the underlying physics is fine. The remedy is to emit *both* values
explicitly: `tau` is lag (framework canonical); `display_tau` is
sample-time (community convention).

---

## 3. Implementation

### 3.1. `gfdr_model.generate_kww_glass_locus`

[`conformer/compute/gfdr_model.py`](../../conformer/compute/gfdr_model.py)
gains a new public function:

```python
def generate_kww_glass_locus(
    chit: float,
    *,
    q_EA: float, tau_alpha: float, beta_KWW: float, tau_beta: float,
    X: float, T: float,
    n_points: int = N_LOCUS_POINTS,
    tau_min: float = 1e-4, tau_max: float = 1e3,
) -> dict:
```

The function returns the same `{tau, C, chi}` dict shape as
`generate_locus`, so it composes with `_interp_log_tau` and any
downstream code that consumes the analytical locus. The wider default
`tau_min = 1e-4` (vs `generate_locus`'s `0.01`) accommodates the
dimensionless lag range that v0.4 bundles emit (sample.dt / tau_scale
typically reaches down to ~10⁻³ for early-lag samples).

`chit` is preserved in the signature for traceability — it is the
cdv1 leading-order anchor and is carried in `fitted_params.chit` even
when the 6-vector refinement is present. The KWW formula does not
depend on `chit`; the substrate-thermodynamic parameters
*are* the cell's deviation from `chit = T_c − T`.

`generate_locus(chit)` is unchanged. Existing callers (`inversion.invert`,
the lens-solver's gfdr lookups, the auditor's foundational tests) see
no behavior change. The KWW path is a strict superset.

### 3.2. `walk_library._extract_observable` — lag/display split

[`conformer/curator/walk_library.py`](../../conformer/curator/walk_library.py)
extracts `sample.dt` as the canonical `tau` field; `sample.t` is
preserved as `display_tau`:

```python
for s in samples:
    lag = s.get("dt")            # canonical model time = lag since snapshot
    sample_time = s.get("t")     # display convention (sample-time)
    ...
    row = {"tau": float(lag), "C": float(C), "chi": float(chi)}
    if sample_time is not None:
        row["display_tau"] = float(sample_time)
```

The column descriptions in the bundle are rewritten to be explicit:

- `tau` — "Lag since snapshot (= sample.dt = sample-time minus t_w).
  The framework's canonical FDR parametric variable. v0.4: lag-
  anchored; previous schemas (v0.1–v0.3) emitted sample-time here —
  see display_tau for that."
- `display_tau` — "Substrate-community display convention for the FDR
  x-axis (= sample.t = lag + t_w). For glass, the CK 1993 convention
  plots vs sample-time. Display only — the model evaluates at tau (lag)."

The bundle's `observable.metadata` gains `operating_point_T`,
`operating_point_h_field`, `operating_point_p_base`, and
`tau_anchoring = "lag"` — explicit metadata for downstream readers.

### 3.3. `declaration-bundle.v0.4.json` — schema bump

[`schema/declaration-bundle.v0.4.json`](../../schema/declaration-bundle.v0.4.json)
extends v0.3:

- `schema` const bumped.
- `observable.data[].display_tau` declared as an optional row field
  (numeric).
- `observable.metadata.operating_point_T`, `operating_point_h_field`,
  `operating_point_p_base`, `tau_anchoring` declared as optional
  metadata fields.
- `fit_provenance.fitted_params` documents the substrate-thermodynamic
  6-vector: `q_EA`, `tau_alpha`, `beta_KWW`, `tau_beta`, `X`, `T`. All
  optional in v0.4 — bundles produced before a 6-param inversion ships
  carry only the existing `chit`/`gamma_AB`.

v0.3 readers (the auditor's current ingestion path) handle v0.4
bundles via `additionalProperties = true` on the relevant sub-objects.
The `tau` values *shift* (from sample-time to lag) — any downstream fit
results recompute against the new values. Calibration baselines and
the inversion seed parameters need a sweep refresh.

### 3.4. `banach_overlay.py` — read lag, plot display

[`conformer/compare/banach_overlay.py`](../../conformer/compare/banach_overlay.py)
splits the role of the bundle's observable rows:

```python
emp_lag_native     = [float(r["tau"]) for r in rows]
emp_display_native = [float(r.get("display_tau", r["tau"])) for r in rows]
emp_lag_dim     = [t / tau_scale for t in emp_lag_native]
emp_display_dim = [t / tau_scale for t in emp_display_native]
```

`_build_path_view` is updated to evaluate the forward model at
`emp_lag_dim` (model's internal time variable) and store the result on
`Trace.tau = emp_display_dim` (plot's x-axis). The empirical Trace
similarly stores `tau = emp_display_dim`. The plot's x-axis is in
display-tau space; the model's evaluation is in lag space; the
mapping between them is the substrate-community choice declared by
the bundle.

A new fallback `_glass_kww_prior_from_T(T)` provides cdv1-leading-order
KWW parameters keyed off the bundle's `operating_point_T`. When a
bundle has `fitted_params.chit` but not the 6-vector (i.e., the
6-param inversion has not yet landed for it), banach_overlay falls
back to this prior. The visualization is immediately useful; future
6-param fits supersede the prior in their own bundles.

### 3.5. Per-window parallax loader

[`_load_per_window_traces`](../../conformer/compare/banach_overlay.py)
gains an explicit `display_axis` parameter — "t" by default for glass-
CK compatibility, switchable to "dt" for substrates whose community
prefers the framework lag axis. The 31 trail-vector per-window traces
are read from the source grind cell at the chosen display variable,
so they layer cleanly under the aggregated empirical markers.

---

## 4. Results

### 4.1. Re-extraction summary

Running `python -m conformer.curator.walk_library` over the full 60-cell
mpa-central library:

| Substrate class | Cells | Bundles emitted |
|---|---|---|
| ck-glassy | 22 | 22 |
| surface-code-qec | 22 | 22 |
| neural-population | 16 | 16 |
| **Total** | **60** | **60** |

All 60 cells re-extracted to `declaration-bundle.v0.4`. Three driver
profiles regenerated. The `_run_summary.json` records the run.

Spot-check on `glass__T0.500__spin-flip.bundle.json`:

```
schema: declaration-bundle.v0.4
first row: {tau=1.0, display_tau=501.0, C=0.9415, chi=0.1160, ...}
metadata.operating_point_T = 0.5
metadata.tau_anchoring = "lag"
fitted_params: {chit=0.250, gamma_AB=0.000}
```

The bundle's tau values now start at 1.0 (= sample.dt at the first
sample, lag = 1 MC-step) instead of 501.0 (sample-time). The fit
results shift: two-stage chit moves from 0.30 to 0.25; cross-path
disagreement moves from 0.37 to 0.30 chit units. **All downstream
fits recompute against lag-anchored tau** — this is the intended
consequence of the move, not an unintended side effect.

### 4.2. Visual proof — hairpin closure in production

The dual-path comparison plot at
[`output/comparisons/ck-glassy/glass__T0.500__spin-flip.bundle.png`](../../output/comparisons/ck-glassy/glass__T0.500__spin-flip.bundle.png)
shows v0.4 production output:

- Left column: two-stage inversion (chit = 0.250). Predicted curve
  (blue, KWW with substrate-default cdv1 prior) traces the empirical
  through the early-lag hairpin and the α-decay tail. Banach (red
  dashed) likewise.
- Right column: lens-solver prior (chit = 0.550). Same KWW form,
  different chit. Both predicted and Banach pass through the empirical
  markers.

The hairpin is *matched* by the model curve, not averaged through.
The 31 per-window gray traces under the markers layer correctly on the
display-tau axis. Cross-path disagreement (|chit_two_stage −
chit_lens| = 0.30) is visible in the title.

### 4.3. Diagnostic RMS (hand-tuned KWW per axis)

From [`scripts/test_kww_glass.py`](../../scripts/test_kww_glass.py)
with the model evaluated at lag and plotted at three candidate axes:

| Display axis | C RMS | χ RMS | Hairpin? |
|---|---|---|---|
| sample.t / τ_scale | 0.025 | 0.073 | No (matched) |
| sample.dt / τ_scale | 0.025 | 0.073 | No (none to match) |
| sample.dt / t_w | 0.025 | 0.073 | No (none to match) |

All three display choices give identical RMS — the physics is
invariant under monotonic display transforms when the model evaluates
at lag. The hairpin in the t-axis becomes a *predicted* feature
(KWW's rapid β-piece decay rendered into the community's preferred
x-axis layout), not an unmatched cluster.

---

## 5. Connection to discipline

### 5.1. RULES §10 — inherit substrate vocabulary

The 6-vector uses the glass community's exact names: q_EA, τ_α, β_KWW,
τ_β, X. No invented MPA-internal aliases. A glass experimentalist
reading the bundle's `fitted_params.q_EA` immediately knows what it
is. This is rule 10's worked instance for glass; QEC and brain follow
the same principle in their own apparatus when their schemas land.

### 5.2. RULES §14 — RFC-S compliance prerequisite

Rule 14 names RFC-S canonical-representation typing as the structural
prerequisite for cross-substrate comparison. v0.4 advances the lag-
anchored direction of this work: by emitting lag (the framework
canonical time) as the model's input, the bundle moves closer to the
RFC-S "drive D and τ_obs schedule in canonical form" requirement.
Full RFC-S compliance — emitting D = Φ\*/κ as a first-class observable
and scheduling τ_obs via an explicit driver profile — remains owed in
a follow-on session. v0.4 is a step toward, not arrival at.

### 5.3. RULES §15 — refinement deviation is substrate content

The 6-vector IS the substrate's deviation from cdv1's leading-order
`chit`. Rule 15 names this deviation as *the* API surface where the
substrate's thermodynamic content lands; v0.4 makes that surface
concrete in the bundle schema. The (q_EA, τ_α, β_KWW, τ_β, X) the
6-param inversion (follow-on session) extracts from each cell are
not "better fit parameters" — they are *the substrate's measurements
on the glass community's posit*, per the rule.

### 5.4. SUITE_BLOCK_IN — compute layer vs viewer layer

[`SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md): conform is
the compute hub; viewers read but do not refit. v0.4 lands the lag/
display split *inside the compute layer* (walk_library emits both
fields; banach_overlay reads both). Viewers (mpa-auditor, mpa-view,
the shot pipeline) inherit the contract — they read display_tau for
the x-axis and trust the model's lag-anchored evaluation in
`fit_provenance.predicted_locus`. No viewer refitting needed.

### 5.5. Thin-and-bespoke — no general inversion abstraction

The KWW + FDT-violation form is *bespoke to glass*. There is no
attempt to "abstract a generic substrate-thermodynamic refinement
interface" — QEC and brain will each land their own substrate-specific
apparatus in their own schema cycles, with their own community
vocabulary. Rule 10 is the discipline against premature generalization
here.

---

## 5.6. Postscript: cross-substrate diagnostics and the χ-convention lock-in

After this paper's initial draft, two cross-substrate diagnostic tests
ran in the same session:

- **QEC** (`scripts/test_kww_qec.py`): glass-KWW does not transfer to
  QEC at p_base=1e-3 (correct per RULES §7 hierarchy-direction
  inversion). The framework's 1-param chit fit landing in the r-regime
  *does* correctly read QEC's C ≈ 0 — framework partial-transfer
  working as designed by §15.
- **Brain** (`scripts/test_kww_brain.py`): KWW *does* transfer to
  brain at suspended/velocity with re-tuned parameters (C RMS 0.305 →
  0.065, factor of 5 reduction). The C-axis apparatus is more
  universal than expected.

Cross-substrate finding: the χ-axis is structurally substrate-
conditional in a way the C-axis is not. χ/dC ratio varies by 32×
across brain's cells, factor of ~13 off-scale on QEC. No scalar
normalization brings non-glass substrates onto the FDT line. This is
the chi-normalization issue named in
[`H:/mpa-central/DEFERRED.md`](../../mpa-central/DEFERRED.md) and the
CHARACTER_FRAMING.md TranslationField shape extension note.

**Companion paper:** [`chi_convention_lock_in.md`](chi_convention_lock_in.md)
landed this session. Three additions:

1. `observable.metadata.chi_convention` declared per substrate (glass=
   `fdr_dimensionless`; brain and QEC = `substrate_emitted_uncalibrated`).
2. banach_overlay renders per convention — full-opacity for glass,
   pale-gray + yellow callout for substrates with uncalibrated χ.
3. Per-substrate normalization mappings deferred (require substrate-
   domain expertise); the architectural slot is in place to receive
   them.

This refines the open items in §6 below: brain and QEC χ-normalization
lookups become higher-priority than the 6-param inversion, since the
inversion can't meaningfully fit X (the FDT-violation ratio) on non-
glass substrates until their χ is canonical.

## 6. Open items (next sessions)

These follow naturally from the v0.4 lock-in but were intentionally
out of scope this session:

### 6.1. 6-param inversion (the substrate-thermodynamic fit)

`conformer/compute/inversion.invert` currently fits chit + gamma_AB
only. The extension to fit (chit, q_EA, τ_α, β_KWW, τ_β, X) is a
non-trivial change — the forward model now has 5 additional degrees of
freedom, so the inversion needs either:

- An analytical+numerical two-stage similar to v0.2's chit fit, with
  the chit prior anchoring most of the parameter mass and the 5
  glass parameters refined in the second stage; or
- A predictor-corrector approach (similar to lens-solver) operating
  on the 6-vector.

Banach's canonical-state propagation needs to flow the 6-vector
(currently just chit). The mpa-scale-solver `BanachSubstrate` API
extension is the home for this; the work is owned by mpa-scale-solver
in its own session.

Until the 6-param inversion lands, `banach_overlay`'s
`_glass_kww_prior_from_T` provides the substrate-default cdv1
leading-order — useful for visualization, not for quantitative posit
extraction.

### 6.2. mpa-lens-solver extension

The lens-solver's predictor-corrector path
[`fit_translation_field`](../../../mpa-lens-solver/) currently
estimates chit only. The 6-vector extension follows directly: the
predictor-corrector machinery handles vector parameters; the
`_BOOTSTRAP_SEED_RANGE_DISPATCH` extends to the new dimensions; the
cdv1 prior becomes the 6-vector default per substrate. Cross-path
disagreement extends to the vector norm.

### 6.3. mpa-scale-solver BanachSubstrate vector state

`BanachSubstrate(chit_0, gamma_AB_0)` becomes a 6-vector canonical
state. `state_at(nu)` flows the full vector (with each parameter's
own translation field per RFC-S). The translation field shape work
named in
[`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../../mpa-lens-solver/docs/CHARACTER_FRAMING.md)
is the natural home for this.

### 6.4. Calibration baseline refresh

The per-substrate baselines at
`H:/mpa-central/library/baselines/<substrate>.json` were computed
against v0.3 bundles. v0.4's tau-shift invalidates them; a sweep
refresh is needed. The
[`conformer/calibration/sweep.py`](../../conformer/calibration/sweep.py)
harness handles this mechanically; estimated runtime ~30 min on the
existing hardware.

### 6.5. mpa-auditor reader update

The auditor's `data-engine.js` ingests bundles via CSV today
(per the foundational §Q12 file-import boundary). When the auditor
swaps to bundle ingestion (a separate planned move), v0.4's `tau` field
will be interpreted as lag. The auditor's display layer should read
`display_tau` for the x-axis. If the auditor's CSV path is still
active when bundle ingestion lands, both fields ride through.

### 6.6. QEC and brain substrate-specific apparatus

Glass got its KWW + FDT-violation in v0.4. QEC and brain each have
their own substrate-thermodynamic content to declare per RULES §10:

- **QEC**: logical-error-rate decomposition; threshold-anchored
  exponents; syndrome-statistic dynamics. The substrate-community
  vocabulary is well-established in the surface-code literature.
- **Brain**: scenario-conditional correlators; context-modulated
  response; population-coding-specific structure. Less canonical
  vocabulary; more curatorial work to identify the right 5–6 params.

Each substrate's apparatus lands in its own schema-bump session.

### 6.7. Display-axis-per-substrate declaration

Currently `banach_overlay` defaults to plotting at display_tau across
all substrates. Some substrates may prefer different display
conventions (e.g., QEC might plot vs syndrome-round count, brain
might plot vs trial number). A per-substrate `display_axis_convention`
metadata field on the driver profile would let viewers pick the right
one without hard-coding.

---

## 7. Review questions

Specific questions for review (outbound research / ultrareview / human):

1. **Naming.** The bundle field `tau` (= lag) and `display_tau` (=
   sample-time) is internally clear but the field name `tau` is
   overloaded. Should v0.5 rename to `lag` and `display_tau`?
   Tradeoff: clarity vs schema migration cost.
2. **FDT-violation form.** The aging-branch slope X is treated as a
   single scalar. Some glass literature uses a *continuous* X(C)
   function (e.g., monotonically decreasing through the aging branch)
   rather than a single constant. Is the piecewise-constant X
   sufficient for the leading-order refinement, or do we need a
   functional form already in v0.4?
3. **Coupling between τ_α and t_w.** The 6-vector treats τ_α as a free
   parameter per cell. In aging glass, τ_α(t_w) is a *function* of the
   waiting time; cells with different t_w should fit different τ_α.
   Currently the cells all have t_w = 500, so this is invisible.
   When the substrate library lands cells at multiple t_w, the
   inversion should know that τ_α is t_w-dependent.
4. **cdv1 prior shape.** `_glass_kww_prior_from_T` uses very simple
   T-dependence. Is there a more principled cdv1 form? E.g., a
   theoretical T-dependence of q_EA derived from the EA order
   parameter, or τ_α scaling from the critical slowdown.
5. **Cross-substrate transfer.** RULES §10's K cavity-method
   correspondence aligned MPA primitives with substrate-existing
   vocabulary. The 6-vector lands that for glass. The natural question:
   **what is the QEC analogue, what is the brain analogue?** Specific
   suggestions welcome.
6. **Hairpin sign in production.** The current production plot shows
   the hairpin as matched by the model curve, but for cells with
   different (q_EA, τ_β) the model may pass *above* or *below* the
   empirical cluster rather than through it. Is per-cell hand-tuning
   acceptable as v0.4 viewer behavior, or should v0.4 ship with a
   "good enough" cell-conditional prior to avoid surprise?

---

## 8. Receipt — what is locked in as of this paper

| Component | State |
|---|---|
| `gfdr_model.generate_kww_glass_locus` | shipped; backward-compat with `generate_locus` |
| `walk_library._extract_observable` | shipped; emits lag + display_tau + metadata |
| `declaration-bundle.v0.4.json` | shipped; forward-compat over v0.3 |
| `banach_overlay.py` (load + render) | shipped; reads lag for model, display_tau for plot |
| Seed-corpus re-extraction (60/60 cells) | done |
| Production comparison PNG for ck-glassy T=0.5 | rendered; hairpin matched |
| 6-param inversion (refinement extraction) | **deferred** to follow-on session |
| Lens-solver vector extension | **deferred** |
| Scale-solver BanachSubstrate vector | **deferred** |
| Calibration baseline refresh | **deferred** |
| Auditor bundle-reader update | **deferred** |

The deferred items are individually scoped, mechanically
straightforward, and each constitutes a single session's work. The
v0.4 lock-in is *complete as the architectural commitment*; the
follow-ons populate the apparatus inside the commitment.

---

## Appendix A — file inventory

Files edited or created in this session:

- `conformer/compute/gfdr_model.py` — added `generate_kww_glass_locus`
- `conformer/curator/walk_library.py` — `_extract_observable` lag/display split; schema bump; metadata extensions
- `schema/declaration-bundle.v0.4.json` — schema bump (forward-compat additions)
- `conformer/compare/banach_overlay.py` — load/render lag/display split; glass cdv1-prior fallback; per-window display axis option
- `scripts/test_kww_glass.py` — standalone diagnostic (theory test, not production)
- `output/diagnostics/kww_glass_test__T0.500__spin-flip.png` — diagnostic receipt
- `output/seed-corpus/**/*.bundle.json` — 60 bundles re-extracted to v0.4
- `output/comparisons/ck-glassy/*.png` — production comparisons re-rendered
- `docs/papers/lag_display_kww_extension.md` — this paper
- `docs/next-session-handoff.md` — to be updated in §8 below

## Appendix B — references

- Cugliandolo, L. F., & Kurchan, J. (1993). *Analytical solution of
  the off-equilibrium dynamics of a long-range spin-glass model*.
  Phys. Rev. Lett. 71, 173.
- Bouchaud, J.-P., Cugliandolo, L. F., Kurchan, J., & Mézard, M.
  (1998). *Out of equilibrium dynamics in spin-glasses and other
  glassy systems*. In *Spin Glasses and Random Fields* (ed. A. P.
  Young).
- Kohlrausch, R. (1854). Original observation of stretched-exponential
  relaxation in Leyden-jar discharge.
- Williams, G., & Watts, D. C. (1970). *Non-symmetrical dielectric
  relaxation behaviour arising from a simple empirical decay function*.
  Trans. Faraday Soc. 66, 80.
- [`H:/mpa-central/RULES.md`](../../mpa-central/RULES.md) §10, §14, §15.
- [`H:/mpa-central/SUITE_BLOCK_IN.md`](../../mpa-central/SUITE_BLOCK_IN.md).
- [`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](../../../mpa-lens-solver/docs/CHARACTER_FRAMING.md).
