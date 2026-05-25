# Five-vector inversion — block-in

**Status: ARC LANDED 2026-05-25.** Blocked-in 2026-05-19; core closed 2026-05-21;
integration + gate + identifiability + a real-substrate rung + the result-image
library landed and committed 2026-05-25. The full validation sweep (12 scripts under
`scripts/`) is green:
- **X-recovery** clean (≤~0.06 across X=0.1–1.0); **`kww_oracle` full 5-vector
  round-trips** within the resolution floor; `two_temp_ou` X to ≤0.01.
- **Domain gate** (residual + per-channel S/N) sorts the whole library (7 IN / 17 OUT):
  in-family controls IN (~0.01–0.02), oscillatory / running / out-of-family OUT
  (~0.14–0.45+). **Identifiability** (parametric bootstrap) is orthogonal to the gate
  (closes the degenerate-IN hole: `brain` is gate-IN but pins nothing).
- **Integrated into `invert()`** (additive `five_vector_fit`) and the CLI bundle output;
  **pipeline-regression clean** (curator→bundle leaves the fit alone). A real-substrate
  rung (driven-critical RFIM) reads X_raw≈0.12 → fit OUT (correctly out-of-KWW-family).
- **Schema: no bump.** The `five_vector` block sits under `fit_provenance`, whose
  `additionalProperties: true` (only the top-level bundle is strict) — it validates
  against the current **v0.4** schema additively.
- **Result-image library:** `docs/five_vector_views/` — the Core 3 views
  (`x_recovery_roundtrip`, `domain_gate_census`, `identifiability`) as
  `view_<timestamp>.png` (block-in header-band standard), built by
  `scripts/build_five_vector_views.py`; re-runs accumulate.

**Recorded nuance (not a defect):** borderline glass T=1.3 is IN by the scalar residual
gate but OUT by the stricter per-channel S/N gate — the two criteria disagree on that one
boundary cell (`scripts/test_channel_gate_ladder.py`).

**Owed (parked, NOT blocking the close):**
- **#6 production aging-glass X** (T<Tc): blocked on mpa-central's null `tau_env` below
  Tc (camera-scale not placed; see the substrate-inversion finding + `DEFERRED.md`) — owed
  to the library refresh, a cross-repo task.
- **T as a 6th fit param:** deferred by design (T fixed from the operating point).

The original block-in plan + algorithm below are retained for reference.

**Why this vindicates the "X comes along for the ride" intuition.** X read by
hand off a parametric slope is fragile and substrate-bespoke (the running ring's
drift-dominated χ, the laser's magnitude divergence). The 5-vector *fit* recovers
X as a parameter where the KWW-FDT family applies, and its residual *gate* flags
where it does not — so the running ring is correctly read as **out-of-(KWW)-domain**
rather than yielding a garbage X. The gate is the principled X machine.

**Why this is the keystone owed item.** Two independent findings from the
positive-control ladder ([`H:/mpa-central/FALSIFICATION.md`](H:/mpa-central/FALSIFICATION.md))
both resolve to *this one piece of work*:
- **KEY FINDING:** the production inversion (`inversion.invert`) fits only
  the 1-param cdv1 `chit` and **cannot recover FDT-violation X** — a
  dialed-in X=0.5 reads back as ~0.95. So the production pipeline cannot
  recover X on *any* substrate (glass/quantum/brain included).
- **FINDING 2:** there is **no domain-of-validity gate** — the inversion
  confidently regime-classifies a pure oscillation (sine wave). The
  residual is the only domain signal, but it can't separate "out of
  domain" (sine ~0.8) from "valid aging the 1-param can't express"
  (two_temp_ou X=0.1 ~0.25) — *until* the valid-aging residuals are
  absorbed by a fit that can express them. This fitter does that
  (X=0.1 residual drops 0.25 → 0.02), which then unblocks a clean
  residual-threshold domain gate.

So the 5-vector inversion delivers (a) X-recovery and (b) the precondition
for a domain gate. Build it once; both findings close.

## What exists

- `gfdr_model.generate_kww_glass_locus(chit, *, q_EA, tau_alpha, beta_KWW,
  tau_beta, X, T)` — the **generator**. `chit` is carried for traceability
  but does NOT enter the C/χ formulas; the 5 params + T determine the curve:
  ```
  C(τ)  = (1-q_EA)·exp(-τ/tau_beta) + q_EA·exp(-(τ/tau_alpha)^beta_KWW)
  T·χ   = dC                                  for dC ≤ 1-q_EA  (FDT)
        = (1-q_EA) + X·(dC - (1-q_EA))         for dC >  1-q_EA  (FDT-violated)
  ```
- `inversion.fit_chit_analytical(rows)` / `inversion.invert(rows)` — the
  stage-1 cdv1 chit anchor (reuse; do not reimplement).
- `five_vector.fit_kww5(rows, *, chit_prior, T, seed)` — **the scaffold**
  (first cut, this block-in). Returns `FiveVectorFit(chit, q_EA, tau_alpha,
  beta_KWW, tau_beta, X, T, residual, success, n_eval)`.

## Interface (settled)

```python
fit_kww5(
    rows: list[{"tau","C","chi"}],   # dimensionless lag (lag / tau_scale)
    *,
    chit_prior: float | None = None, # cdv1 anchor; None → fit via stage 1
    T: float = 1.0,                  # FDT-slope temperature; FIXED, not fit
    seed: Sequence[float] | None = None,
) -> FiveVectorFit
```

## Algorithm (settled, two-stage — mirrors v0.2)

1. **Stage 1 — cdv1 anchor.** `chit` from `fit_chit_analytical`. Fixed
   through stage 2 (preserves the universality form per RULES §15; the
   5-vector is the substrate's *deviation* from it).
2. **Stage 2 — numerical refine.** `scipy.optimize.least_squares` over
   (q_EA, tau_alpha, beta_KWW, tau_beta, X) with box bounds, residual =
   joint `[C_emp - C_model, χ_emp - χ_model]` evaluated at the cell's
   dimensionless lag (log-interp of the generated locus). T fixed.

## Validation contract (the controls have complementary roles)

| control | C-shape | validates | status |
|---|---|---|---|
| `two_temp_ou` | pure exponential (degenerate KWW corner) | **X-recovery only** — X clean to ~2%; q_EA/timescales unidentifiable (two param sets give the same C) | **PASS (first cut)** |
| `kww_oracle` | genuine two-timescale KWW | **full 5-vector identifiability** (all params non-degenerate) | NOT BUILT — rung 5 |

This split matters: a fitter can pass two_temp_ou (recover X) while still
being unable to identify q_EA/τ_α/β_KWW. Only kww_oracle proves the full
vector round-trips. Build kww_oracle with a genuine two-timescale C so the
5-vector is non-degenerate.

## What's left (punch list for the new session)

1. **Build `kww_oracle` (ladder rung 5).** A substrate whose C is a real
   two-timescale KWW with a prescribed, non-degenerate (q_EA, τ_α, β_KWW,
   τ_β) plus a prescribed X. Two construction options:
   - *Full-pipeline:* multi-mode OU (Prony sum of exponentials
     approximating the stretched exponential) + two-temperature
     FDT-violation. Goes through the grinder's measurement chain. Honest
     but fiddly (mode spectrum → KWW matching).
   - *Fitter-only oracle:* emit the analytic KWW locus + realization noise
     directly as the cell. Tests the fitter, not the grinder. Simpler.
   Recommend full-pipeline if feasible; fitter-only as a fast first check.
   Then: `fit_kww5` must round-trip all five within the resolution floor
   (±0.03–0.09 in dimensionless f; see FALSIFICATION.md).
2. **Seeding / multi-start.** Current fixed seed works on the controls;
   harder/real cells may need a chit-informed seed or multi-start to
   avoid local minima. The degeneracy on pure-exp C (q_EA→0 vs q_EA→1)
   shows the landscape has flat directions.
3. **T handling.** Currently fixed (=1 for the controls). Production
   substrates carry a real operating-point T (glass T, etc.). Decide: set
   T from the operating point, or fit it as a 6th param (the handoff's
   "6-vector"). Fixing from the OP is cleaner if T is known.
4. **Integration into `invert()` + bundle schema.** `audit_delta` carries
   `chit`, `locus_residual`, `regime_label`, `in_gamut`. Add the 5-vector
   + its residual as an optional refinement block (schema bump, deliberate
   — see conform CLAUDE.md). banach_overlay can then render the 5-vector
   curve as a second overlay.
5. **Domain-of-validity gate (closes FINDING 2).** Once valid-aging
   residuals are absorbed (this fitter: X=0.1 → 0.02), calibrate a
   residual threshold that flags out-of-domain inputs. Calibration points:
   accept two_temp_ou/kww_oracle (resid ~0.02); reject sine_wave
   (resid ~0.8 under the 1-param fit — re-measure under the 5-vector fit,
   it should stay high because a cosine is not in the KWW family either).
6. **Production validation.** Run `fit_kww5` on real glass/quantum/brain
   cells. Does X come out physically sane? Glass below Tc should show
   X<1 (aging); quantum/brain per their chi-convention
   (`docs/papers/chi_convention_lock_in.md`).

## Where it lives / how to test

- Scaffold: `conformer/compute/five_vector.py`.
- Test (X-recovery on two_temp_ou):
  ```python
  import sys, json; sys.path.insert(0, "H:/mpa-conform")
  from conformer.compute import five_vector
  cell = json.load(open("H:/mpa-central/library/data/two_temp_ou/two_temp_ou__X0.5__velocity.json"))
  s = cell["results"]["all_samples"]; scale = cell["tau_env_analytic"]["value"]
  rows = [{"tau": e["dt"]/scale, "C": e["C_mean"], "chi": e["chi_mean"]} for e in s]
  print(five_vector.fit_kww5(rows, T=1.0))   # X ≈ 0.49
  ```
- Diagnostic overlay: extend `H:/mpa-central/library/diag_inversion.py`
  to add a second (5-vector) curve alongside the 1-param blue.
