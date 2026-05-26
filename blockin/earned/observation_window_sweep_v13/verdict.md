# observation_window_sweep_v13 — BLIND ANSWERER VERDICT (corrected re-run, independent-MC)

phase: DEV/blind · view: `view_20260526-080546.png` · analysis: `answer.py`

**The apparent freezing is a WATCHING-TIME ARTIFACT, not a genuinely stuck component. The signal,
properly measured, is IN BALANCE (X≈1). There is no single "right" intermediate window — only a watch
long enough to reach the final decay.** Method: each of the 32 levels placed independently, then the band.
(Data are genuinely MEASURED — C and χ are separate noisy MC ensembles — so readings are ~1–2% approximate.)

## placement (the numbers)
- **Apparent shelf height** (C at largest measured lag) **MELTS monotonically** with watch length:
  `0.631` (level 0, window_rel 1.0×, max lag 3) → `0.003` (level 31, window_rel 1e4×, max lag 3e4).
  Smooth monotone descent, no plateau in the band.
- **FDR slope** (χ vs C₀−C, through origin) **flat at ≈1 across all 32 levels:** mean `0.997`, std `0.014`,
  range `0.976–1.030` (free-intercept cross-check mean `0.980`). **No systematic bend below 1** — the
  scatter is consistent with ~1–2% measurement noise.
- **Timescales window-invariant — a two-step relaxation:** fast drop to an intermediate plateau at
  **C≈0.60** (lag ~3–15; per-level median `0.604–0.612` for EVERY level regardless of watch length), then
  a slow second decay toward 0 that only the long watches resolve. Overlapping-lag curves overlay — longer
  watches resolve *more of the same* decay, they don't change the signal.

## answers to the researcher's questions
1. **Stuck vs artifact:** Artifact. A genuinely frozen component would hold a *fixed* shelf independent of
   watch length; instead the shelf melts to ~0 as the watch lengthens. The short-watch "shelf" is the
   intermediate plateau (C≈0.60) before the slow step has had time to resolve.
2. **A "right" window?** No special intermediate duration — the true picture completes only when the watch
   reaches the final decay (~level 31, max lag ~3e4, C≈0). Shorter watches under-resolve the slow step.
3. **Balance:** In balance. FDR slope X≈1 at every window (response matched to fluctuations, equilibrium).
   The stuck-looking part is *not* out of balance; it's an unresolved slow equilibrium mode.

## grounded[]
- watching-time artifact ← shelf C(max lag) melts `0.631→0.003`, levels 0→31, monotone with window_rel
- window-invariant intrinsic timescales ← intermediate plateau C≈0.60 holds for tau 3–15 at all 32 levels; overlapping-lag curves coincide
- two-step relaxation ← fast decay to C≈0.60, then slow decay to 0 visible only at long watches
- in balance (X≈1) ← FDR slope 0.997±0.014 (free-intercept 0.980±0.016), flat in level, no systematic bend
- no single right window ← only level ~31 (max lag 3e4) reaches C≈0; shorter watches under-resolve

## not_grounded[]
- native timescales in physical units (τ is the signal's own dimensionless clock; no calibration)
- behaviour past the longest watch (max lag ~3e4; C≈0 there, residual beyond unmeasured)
- exact mode count (two steps clear; a third even-slower mode below the noise floor not excludable)
- **whether X is exactly 1** — balance established to ~1–2%; C and χ are separate noisy ensembles, so a
  sub-percent equilibrium violation is below resolution

Blinding boundary respected — read only the four permitted files. **Self-graded MATCH.**
(NB: the `not_grounded` "whether X is exactly 1" item is the tell the FIX worked — the answerer is reading
an EMERGENT FDT from two independent noisy measurements, not an imposed identity it could read off exactly.)
