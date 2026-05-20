# Five-vector inversion — block-in

**Status:** blocked-in 2026-05-19. First-cut scaffold exists and works
(recovers X on the `two_temp_ou` control to ~1–2%). Known-incomplete; the
"What's left" punch list is the new session's entry point.

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
