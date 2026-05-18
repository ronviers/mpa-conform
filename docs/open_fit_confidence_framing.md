# Open question — fit-confidence framing

**Status:** open architectural question, 2026-05-18. Stop-the-line on the
diagnostic-vector path (see Background below). No salvage decision yet.

## What we need

A per-fit **confidence quantity** for chit (the canonical scalar fitted
per cell by every mpa-solver path). The quantity must:

- Have a **natural scale** (chit units, posterior probability, or other
  self-interpretable quantity).
- Not require **per-substrate, per-path, or per-regime threshold
  calibration**. The number should mean the same thing across glass,
  quantum, brain — and across the three fitting paths.
- Be **computable per cell** by all three production fitting paths
  (two-stage analytical inversion, lens-solver prior, lens-solver
  bootstrap), or propose how it'd map.
- Drive three downstream consumers:
  1. **Auditor badging**: "this fit is trustworthy / suspicious / wrong"
  2. **Researcher path**: "request more data on this cell"
  3. **cdv1 library staleness**: systematic poor-fit on a substrate
     template flags the template for human review.

## What we tried (and why it's the wrong shape)

### Diagnostic vector + threshold classifier

A 3-field vector emitted per fit:

- `residual_final`: raw final residual of the score function (gFDR
  locus distance).
- `regime_confidence`: 1 − (fraction of refinement candidates that
  crossed the regime boundary). Range [0, 1].
- `predictor_gap`: |fit_chit − predicted_chit| in chit units (lens-solver
  paths; None for two-stage).

Classifier: flag if **any** signal exceeds its threshold. Thresholds set
empirically from a calibration sweep.

### Sweep characterization

Two full sweeps run (glass-only, then 3-substrate):

- **3 substrates** (glass, quantum, brain) × **3 paths** × **7 noise
  models** (gaussian, drift, quantization, row_dropout,
  calibration_bias, tau_jitter, multimodal_contamination) × **9 noise
  intensities** (σ/dynamic_range ∈ {0, 0.001, 0.01, 0.05, 0.1, 0.25,
  0.5, 1, 2}) × **5 seeds** × ~20 library cells per substrate.
- Total: **56,880 outcomes**. Zero errors, zero hangs. Reproducible
  (seeded RNG, per-cell deterministic).
- Ground truth: each (substrate, path, cell)'s clean-data fit, with
  bootstrap GT mapped to the prior path's clean fit (asymmetric, on
  purpose).
- Per fit: classified TP/FN/FP/TN against gt_error > 0.3.

### What the sweep showed

The signals **carry real information**:

| Path | FN rate (3-sub aggregated) |
|---|---|
| lens_solver_prior | 0.0% |
| lens_solver_bootstrap | 2.1% |
| two_stage_inversion | 2.9% |

But the thresholds **are not transferable** and the FP cost is high:

| Path | FP rate (3-sub range across noise models) |
|---|---|
| lens_solver_prior | 76–79% |
| lens_solver_bootstrap | 90–94% |
| two_stage_inversion | 64–72% |

The thresholds we picked (regime_confidence > 0.85, residual_final >
0.3, predictor_gap > 0.3) discriminate FN well but mean ~70% of "good"
fits get flagged as suspicious. The dial **does not generalize**:
glass-only thresholds gave FP rates 21–46%; the same thresholds on
quantum + brain pushed those rates to 64–94%.

### Why it can't be fixed by dialing

The deeper issue: **each signal needs an external reference to be
interpretable.**

- `regime_confidence`: path-conditional in semantic. On bootstrap, high
  confidence = score pinned to one regime wrongly = bad fit. On a clean
  prior path, high confidence = score correctly agreeing with the prior
  = good fit. **Same signal, opposite meaning per path.**

- `residual_final`: substrate-conditional in scale. Glass natural
  residuals are O(0.1); quantum's are O(1+); brain's differ. A single
  scalar threshold either over-flags or under-flags depending on
  substrate.

- `predictor_gap`: substrate-conditional in scale (different
  substrates have different natural step sizes between cells).
  Also undefined on two-stage (no predictor).

We can dial thresholds per (path, substrate, regime). But every new
library cell, every refined score function, every new substrate, every
algorithm change re-opens calibration. That's not engineering — it's
hand-tuning a reference table.

**The diagnostic vector works as a classifier on the data we trained
it against. It doesn't generalize, and the framing requires permanent
recalibration.**

## What's wrong with the framing

We're trying to estimate **"is this fit correct"** from signals that
have no natural reference scale. Every signal needs to be interpreted
relative to *something*:

- residual_final → "what's a typical good residual for this path /
  substrate / regime?"
- regime_confidence → "what's the expected confidence distribution
  from a known-good fit?"
- predictor_gap → "what's the natural step size of this substrate's
  trajectory?"

All three references are empirical. All three are
path/substrate/regime-conditional. There is no absolute scale.

We want a quantity that has a **natural reference built in** — a
confidence number that means something absolute without requiring
per-substrate/per-path threshold calibration.

## Candidate framings to evaluate

Not recommendations — starting points for the outside research. Each
should be evaluated against the four constraints in "What we need."

### 1. Bayesian posterior over chit

Assume a noise model on observations. Compute P(chit | data) via
likelihood × prior. Report the posterior's standard deviation as the
confidence interval.

- **Pros:** Natural reference (chit units). Uniform across paths if
  noise model is shared.
- **Cons:** Need a noise model. Our (tau, C, chi) observations have
  unclear noise structure — inferring noise from the same data we're
  inferring chit from. Could use empirical residuals from cdv1 library
  cells as a noise prior, but that re-introduces calibration.
- **Cost estimate:** moderate (MCMC or variational); per-fit
  computation in the seconds range.

### 2. Leave-one-out cross-validation

Per fit: hold out one (tau, C, chi) row, refit chit, predict the
held-out row, measure prediction error. Average over all LOO splits.
Report the LOO error as the confidence.

- **Pros:** No noise model. Confidence in observable units.
  Path-agnostic — works for any fitting algorithm.
- **Cons:** N× expensive per cell (N = number of rows ≈ 20–50). For
  three paths × full library, ~100k+ refits — large but feasible on
  current hardware.
- **Cost estimate:** N× single-fit cost. Sub-second per cell for
  lens-solver paths; ~10s per cell for two-stage with stage 2.

### 3. Statistical bootstrap on observations

Per fit: resample (tau, C, chi) rows with replacement, refit, see how
much chit moves across resamples. Report the chit-distribution
standard deviation as the confidence interval.

- **Pros:** No noise model. Same units as the parameter. Honest about
  non-Gaussian / multi-modal posteriors.
- **Cons:** B× expensive (B = 100–1000 typical). With B=100 and 60
  cells × 3 paths, ~18k refits.
- **Cost estimate:** B× single-fit cost. Parallelizable.

### 4. Likelihood ratio against prior

For paths with a prior, compute the score at the best-fit chit vs the
score at the prior chit. The log-ratio measures how much the data
improved on the prior alone.

- **Pros:** Absolute (log-likelihood ratio is unitless and additive).
  Cheap (no refitting).
- **Cons:** Only applies to paths with priors (excludes bootstrap).
  Requires the score function to be a proper likelihood — ours is a
  residual, not a likelihood. Would need a likelihood model anyway.

### 5. Predictive coverage on next cell

For multi-cell trajectories (lens-solver paths): refine cells 1..i−1,
predict cell i's chit from the trajectory, compare to cell i's actual
refined chit.

- **Pros:** Substrate-agnostic. Trajectory-level meaning. No noise
  model.
- **Cons:** Doesn't apply to per-cell scoring. Only meaningful for
  ordered trajectories. Doesn't help two-stage.

### 6. Conformal prediction

Distribution-free wrapper around any predictor; produces calibrated
confidence intervals. Given a non-conformity score (e.g., refinement
residual), produces intervals guaranteed (under exchangeability) to
contain the truth with chosen probability α.

- **Pros:** No noise model. Coverage guarantee. Theoretically clean.
- **Cons:** Needs a calibration set. The reference question may be
  unavoidable in some form. Worth understanding whether the
  guarantees transfer across substrates.

### 7. Fisher information / Cramér-Rao bound

For a parametric model with a likelihood, the Cramér-Rao bound gives
the minimum variance any unbiased estimator can achieve. Compute the
Fisher information at the fit, take its inverse for the variance lower
bound, report sqrt() as the confidence interval.

- **Pros:** Closed-form (cheap). Natural reference (chit units).
- **Cons:** Lower bound only — could understate actual uncertainty.
  Requires a likelihood model. Asymptotic — may not be tight at small
  N.

## Constraints (for the outside agent)

- Must work for THREE paths (two_stage_inversion, lens_solver_prior,
  lens_solver_bootstrap) — or propose explicit mapping per path.
- Must produce a number with a natural scale (NOT a threshold-flag).
- Should not require recalibration per substrate, per path, or per
  regime.
- Implementable in Python in the existing solver pipeline. No heavy ML
  training step that would change deployment shape.
- Reproducibility: pure functions, seeded RNG, value semantics
  (existing solver discipline).
- Acceptable computational cost: up to 100× single-fit cost per cell
  is fine (sweep already runs 56k fits in 30 min on a 24-core
  workstation).

## What's NOT on the table

- More diagnostic signals + retuned thresholds. Same framing problem
  in a higher-dimensional space.
- Learned classifier (gradient boosting, neural net) over the
  diagnostic vector. Brings ML training infrastructure into a
  deterministic solver pipeline; doesn't address the reference-frame
  question.
- LLM-scored confidence. Non-deterministic; introduces new calibration
  problem in a different shape.

## Sweep apparatus (still usable)

The sweep harness, noise models, and reporter remain useful regardless
of what diagnostic shape we land on. Whatever quantity we adopt, the
sweep can validate it (does it predict gt_error? does it generalize
across substrates?) against the same 56k-outcome ground truth.

Code:

- `H:/mpa-conform/conformer/calibration/sweep.py`
- `H:/mpa-conform/conformer/calibration/noise_models.py`
- `H:/mpa-conform/conformer/calibration/report.py`
- Latest sweep parquet:
  `H:/mpa-conform/output/calibration/20260518-132746-full-3sub/sweep.parquet`

## Question for outside research

> Is there a framing of "fit confidence for a low-dimensional inverse
> problem (chit ∈ [−2, 2] inferred from ~20–50 noisy (tau, C, chi)
> observations via a known forward model) that produces a
> calibration-free per-fit confidence quantity?"

Survey statistics (Bayesian, conformal, cross-validation),
information theory (Fisher / Cramér-Rao), and recent ML uncertainty
quantification. Return:

- Candidate framings ranked by fit to the constraints above.
- Implementation cost estimates per candidate.
- Known pitfalls and failure modes (especially for substrate/regime
  generalization).
- Where the framing has been used at production scale in similar
  inverse problems.
- An opinion on whether the calibration-free requirement is achievable
  in principle, or whether some residual reference choice is
  unavoidable.

## Background (links)

- Diagnostic v1 design conversation: 2026-05-18 session.
- Diagnostic v1 → v2 redesign + sweep characterization:
  `H:/mpa-conform/output/calibration/20260518-081524-glass-only/`
  (v1 — broken classifier),
  `H:/mpa-conform/output/calibration/20260518-123048-glass-only/`
  (v2 — works for glass),
  `H:/mpa-conform/output/calibration/20260518-132746-full-3sub/`
  (v2 — generalizes weakly across substrates).
- FitDiagnostics dataclass:
  `H:/mpa-lens-solver/mpa_lens_solver/diagnostics.py` (v2 lives here;
  candidate-for-deletion pending salvage decision).
- Solver-trio architecture:
  `H:/mpa-conform/docs/SOLVERS_BLOCK_IN.md`.
