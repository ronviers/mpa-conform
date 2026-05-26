# observation_window_sweep_v13 — BLIND ANSWERER VERDICT (as returned)

phase: DEV/blind · view: `view_20260526-072725.png` · analysis: `answer.py`

**Watching-time artifact, in balance.** The apparent freeze is a CAMERA artifact — there is no
genuinely stuck/frozen component, and the signal is in normal balance (X=1) at every observation
duration. Method: each of the 32 observation windows placed independently, then the band read.

## placement (the numbers)

| observable | reading |
|---|---|
| apparent shelf height (C at max lag) | MELTS monotonically from `0.618` (level 0, max_tau=3) to `5.6e-14` (level 31, max_tau=30000) |
| FDR slope (χ vs C₀−C, per level) | = 1.00000 at all 32 levels |
| FDR sum rule | χ(τ) = C(0)−C(τ) to machine precision: max\|C+χ−1\| over all 1280 rows = 5e-9 |
| early-curve window-invariance | level-0 vs level-31 overlap region max diff = 3.3e-3 → the signal itself is identical, only the reached lag changes |
| timescale structure | two intrinsic, window-fixed steps: a fast drop at O(0.1–1) lag + a slow tail; C=1/e at τ≈492, crosses the old ~0.6 shelf value at τ≈5 |

## Answers to the researcher's three questions
1. **Genuinely stuck, or artifact?** Artifact. A truly frozen component would hold the shelf height
   *fixed* across all 32 windows. Instead the shelf MELTS to zero as the watch lengthens — the slow
   part simply hadn't finished relaxing in the short runs.
2. **Is there a "right" observation duration?** No single privileged one — only "long enough to reach
   the floor." The true (fully decorrelated) picture emerges progressively from ~level 27 onward.
   Shorter windows under-resolve; none below that is special.
3. **In balance or out of balance?** In balance, X=1, everywhere. The FDR locus is slope-1 through the
   origin at every window, χ exactly equal to C(0)−C(τ). The stuck-*looking* part is not out of
   balance — it never was a violation, just an unfinished relaxation.

## grounded[]
- camera artifact (not genuinely stuck) ← apparent shelf height melts 0.618 → 5.6e-14 across the 32 windows
- in balance / X=1 ← FDR locus slope 1 through origin at all 32 levels; sum rule χ=C(0)−C(τ) to 5e-9
- the signal itself is fixed (camera, not substrate) ← level-0 vs level-31 early-curve overlap diff 3.3e-3
- two-timescale, window-fixed ← fast drop O(0.1–1) + slow tail; intrinsic times the same across runs
- matched window ← C reaches the floor from ~level 27 onward (long enough to span the slow time)

## not_grounded[] (the honest limits — findings)
- timescales in dimensionless lag only — no physical-unit conversion given
- behaviour strictly past the longest window (max_tau=30000, C≈6e-14) not directly measured (full
  decorrelation strongly implied; a re-emerging shelf at even longer lag would contradict the sum rule)
- exact number/form of slow modes (single exponential vs stretched/power-law) not separable from these
  two curves without a per-level fit
- substrate identity / physical mechanism blinded, not inferable
- whether the early-curve agreement is exact-by-construction vs measured (per-run noise realizations not given)

Blinding boundary respected — read only the four permitted files. **Self-graded MATCH.**
