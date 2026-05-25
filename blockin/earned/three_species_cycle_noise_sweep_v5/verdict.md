# verdict — three_species_cycle_noise_sweep_v5  (DEV/blind)

A three-population cyclic standoff (1→2→3→1) run as the SAME community at five
environmental-noise levels (0.2× … 4.0× baseline). Traversed as **five independent
single-point placements + one band readout** (sweep contract, §6). Ground truth is the
sealed analytic answer the orchestrator holds; this file is the examinee's reading from
the sanitized data only.

---

## placement (framework read)

| level | noise_rel | winding rate `phiMean/τ` (rad/clock) | fit R² | phase-diffusion baseline `d(phiVar)/dτ` | sporadic phiVar jumps | directed cross-corr peak |
|------:|----------:|------------------:|-------:|----------------:|-----------------:|------------------:|
| 1 | 0.20 | 1.049 | 1.000 | 12.10 | 0 | 0.330 |
| 2 | 0.50 | 1.059 | 1.000 | 11.65 | 0 | 0.330 |
| 3 | 1.00 | 1.056 | 1.000 | 12.43 | 2 (max +406) | 0.330 |
| 4 | 2.00 | 1.002 | 1.000 | 12.19 | 2 (max +1500) | 0.330 |
| 5 | 4.00 | 1.042 | 1.000 | 12.46 | 0 | 0.330 |

**Band across levels:**
- **Winding rate (turnover frequency): INVARIANT.** mean 1.042 rad/clock, relative
  spread **5.5%** across a 20× change in noise. Every per-level fit is linear with
  R² = 1.000.
- **Two-point structure (C, χ, Cxy, Cyx): IDENTICAL across all five levels** — maximum
  cross-level deviation **0.0e+00** (byte-identical on the shared τ grid). The
  autocorrelation oscillates (C₀ = 0.909, first zero-crossing τ ≈ 1.5) and decays to a
  small positive plateau; χ rises to ≈ 0.51 then relaxes to ≈ 0.40 — same at every noise.
- **Directed current present at ALL levels including the calmest:** Cxy = −Cyx exactly
  (|Cxy + Cyx| = 0), nonzero antisymmetric peak ≈ 0.33 at finite lag (τ ≈ 0.70). This is
  the chirality signature of the 1→2→3→1 loop — a sustained circulating current, not a
  relaxing fluctuation.
- **Phase-diffusion baseline: also essentially flat** — robust median d(phiVar)/dτ ≈ 12.2,
  relative spread **6.7%**. No clean monotone diffusion-vs-noise law (linear corr 0.61 is
  carried by tiny variation, and the highest-noise level L5 has the *lowest* jump count).
- **Sporadic phiVar jumps** (large single-step excursions = phase slips / cycle-count
  events) occur only at L3 (1.0×) and L4 (2.0×) and are **non-monotone** in noise.

---

## verdict (researcher terms)

**The cycling is INTRINSIC, not noise-driven. Turning the environment down will NOT slow
or stop the turnover.** The rate at which the community swings around the 1→2→3→1 cycle is
the same at every noise level you tested — 1.04 rad of cumulative turnover angle per unit
of the community's own clock, flat to ~5% from a fifth of your usual buffeting up to four
times it. The two-point statistics of the turnover plane (autocorrelation and the directed
cross-correlations) are not just similar but *identical* across the five runs, and the
directed-cycle signature (Cxy = −Cyx) is fully present even at the calmest setting. So the
cycling is an internal property of the loop — a self-sustained circulating current — that
the environment neither creates nor paces.

**What does the noise level actually change about the turnover? On the evidence here,
strikingly little that is robustly measurable.** The rate is fixed, the correlation
structure is fixed, and even the baseline rate at which the turnover-angle *spread* grows
(phase diffusion ≈ 12 per clock) is essentially flat across noise. The only noise-associated
feature is occasional large jumps in the angle-spread (phase-slip events) at the middle
levels — but these do not scale cleanly with noise (the loudest run is among the cleanest),
so this analysis cannot promote them to "noise sets the phase-slip rate." That second-half
attribution is flagged not-grounded below.

There is **no headroom toward a settling/steady-balance asymptote**: nothing in the band
migrates toward a fixed point as noise is reduced. The community keeps turning at the same
rate no matter how calm you make the environment.

---

## grounded[]

1. **Cycling is intrinsic, not noise-driven** — winding RATE (slope of `phiMean` vs elapsed
   τ) = 1.002 … 1.059 rad/clock across noise 0.2×…4×, relative spread 5.5%, every per-level
   fit R² = 1.000. *Established by:* the `phiMean` column, per-level least-squares slope.
2. **Turnover structure is independent of noise** — `C`, `chi`, `Cxy`, `Cyx` are identical
   across all five levels (max cross-level deviation 0.0e+00). *Established by:* the
   `C`/`chi`/`Cxy`/`Cyx` columns, level-to-level numeric comparison.
3. **A genuine sustained directed cycle exists at every level incl. the calmest** —
   Cxy = −Cyx (antisymmetric, |Cxy + Cyx| = 0), nonzero peak ≈ 0.33 at finite lag τ ≈ 0.70.
   *Established by:* the `Cxy`, `Cyx` columns (the current/k-frust gate).
4. **Baseline phase-diffusion rate is also ~noise-invariant** — robust median d(phiVar)/dτ
   ≈ 12.2, relative spread 6.7%, no clean monotone trend. *Established by:* the `phiVar`
   column, robust pointwise-slope (median of positive d(phiVar)/dτ, immune to jumps).
5. **System sits in a stationary, non-settling regime (no fixed-point approach)** — the FDR
   locus (χ vs C₀−C(τ)) is well-defined and identical at every noise; the autocorrelation is
   oscillatory-decaying, not collapsing toward a frozen state. *Established by:* the `C`,
   `chi` columns (the universal FDR readout).

## not_grounded[]

1. **WHAT the noise changes about the turnover, as a clean law.** The question's second half
   is only weakly answerable from these statistics. Every robustly-measured property (rate,
   two-point block, baseline diffusion) is ~noise-independent; the one noise-associated
   feature is sporadic large `phiVar` jumps at L3/L4 that do **not** scale monotonically with
   noise (L5, the highest, is among the cleanest). The provided columns cannot distinguish
   "noise sets a phase-slip rate" from "cycle-count glitches in the sub-window angle
   accounting." *Un-groundable because:* no per-point grain/uncertainty supplied, and the
   feature is non-monotone in the swept axis.
2. **Whether rate-invariance persists below 0.2× noise** (toward the deterministic / zero-
   buffeting limit). The sweep floor is 0.2×; a transition off the low end cannot be ruled
   out. *Un-groundable because:* collapsed axis — no operating point below level 1.
3. **Individual coupling strengths / which of the three links dominates.** The directed
   cross-correlation gives chirality and a current magnitude, not per-edge weights.
   *Un-groundable because:* not in the provided observables (researcher brought no model
   parameters).
4. **Any researcher PREFERENCE among the noise levels** (which is "best/healthiest"). The
   band is grounded per level; selecting one is an interpretive choice the researcher brings
   — a viewport dial, not a conform call. *Un-groundable because:* value-laden, not computable
   from the freeze (§6 researcher-dial carve-out).

---

## view
`view_20260525-154725.png` — header band (question + verdict + placement +
grounded/not-grounded) over four data-mapped boxes:
- **Box 0 (THE BAND):** winding rate and phase-diffusion baseline vs `noise_rel` (log control
  axis) — both flat lines, the migration (or lack of it) readable by eye.
- **Box 1:** `phiMean(τ)` for all five levels overlaid — slopes coincide (rate invariant).
- **Box 2:** `phiVar(τ)` for all five levels — common baseline fan with the sporadic L3/L4 jumps.
- **Box 3:** `Cxy`, `Cyx` (antisymmetric directed current) and `C` (autocorr), identical at
  every level.

Every rendered property maps to a measured column; the band box carries the answer.
