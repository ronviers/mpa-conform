# coupling_ramp_v7 — BLIND ANSWERER RESULT

phase: DEV/blind · view: `view_20260525-180834.png` · analysis: `coupling_ramp_v7.answer.py`

A sweep: one community at 5 settings of a single interaction-strength knob (level 0..4).
Per WORKFLOW §6, each level placed as an **independent single-point fit first**, then the
band read off the 5 placements. Each level read on its own clock (tau range differs by level
by design; every level's C settles to <0.04% of C(0) inside its own window — windows matched).

---

## Per-level placement (the framework read)

| level | tau window | tauC (relax time) | chi_inf (static resp) | FDR slope | C(tau) shape | max\|Cxy−Cyx\| | phiMean ramp | kind |
|---|---|---|---|---|---|---|---|---|
| 0 | [0.03, 11.4] | 1.30 | 1.071 | 1.10 | single-exp, no neg lobe (min_C=+2e-4) | 0 | ≈0 (bounded ±0.45) | settling |
| 1 | [0.05, 20.0] | 2.44 | 1.516 | 1.56 | single-exp, no neg lobe | 0 | ≈0 (±0.43) | settling |
| 2 | [0.10, 40.0] | 4.98 | 2.690 | 2.78 | single-exp, no neg lobe | 0 | ≈0 (±0.56) | settling |
| 3 | [0.20, 80.0] | 9.996 | 5.105 | 5.27 | single-exp, no neg lobe | 0 | ≈0 (±1.09) | settling |
| 4 | [0.40, 160] | 20.0 | 9.980 | 10.27 | single-exp, no neg lobe | 0 | ≈0 (±1.13) | settling |

- **Relaxation kind, every level:** autocorrelation C(τ) decays monotonically to ~0 with **no
  negative lobe** at any level (min_C stays positive). A genuine cycle/oscillation would drive
  C below zero. → single-exponential relaxation, not oscillation.
- **FDR locus (universal readout):** χ vs (C(0)−C(τ)) is **linear** at every level (rms < 0.006),
  and the slope ≈ chi_inf ≈ tauC to within ~3% — three independent readings of the relaxation
  magnitude that agree. Equilibrium fluctuation–response: the system is relaxing to balance, not
  driven around a loop.
- **Directed cross-correlations:** Cxy = Cyx **exactly** (to 1e-6) at every row of every level →
  matched/reciprocal coupling, **no net directed current** around the loop. (The two readings
  that should agree, do — J/L cross-check passes; no falsifier.)
- **Net turnover angle:** phiMean is a **bounded wander near 0** (|phiMean| ≤ ~1.1 even at level 4
  over the entire run, no monotone ramp). phiVar grows ~linearly in elapsed time (diffusive
  spread). Consistent with noise-driven excursions about a fixed point, not phase-coherent cycling.

## The band (what migrates / what stays put / which way)

- **MIGRATES (up, monotonically):** tauC ~1.3→2.4→5.0→10→20 (roughly **doubles per step**) and
  chi_inf ~1.07→1.52→2.69→5.10→9.98 (also ~doubles). The system settles **slower** and responds
  **larger** as the knob increases — exactly the researcher's "bigger swings, longer settling."
- **STAYS PUT (invariant across the sweep):** the *kind* of dynamics. No negative C lobe appears at
  any level; Cxy−Cyx stays 0; phiMean stays a bounded wander with no rotation ramp. The
  fluctuation–response relation stays linear/equilibrium throughout.
- **Direction it heads:** monotone toward slower, larger-amplitude relaxation — deeper into
  "sluggish but still settling," with **no onset of rotation or finite-time blow-up** across the
  5 sampled points.

## Verdict in the researcher's own terms

- **Is each setting still settling, or genuinely cycling?** Every setting is **still just settling
  back to balance** — slower at higher knob settings, but settling. Nothing has started to cycle:
  the autocorrelation never swings negative and the net turnover angle never accumulates.
- **Does cranking the knob change WHAT KIND of system this is?** **No.** It is the same kind of
  thing all the way up — a noise-driven community relaxing to a stable balance — just *more so*
  (slower, bigger excursions). The change across the sweep is quantitative (timescale and response
  amplitude grow), not qualitative (no new regime, no rotation, no instability).
- **Are you approaching an edge, and how close?** Within the 5 settings you sampled, **you are in
  the interior** — still settling, with a smooth monotone trend and no sign of a finite-time
  divergence or a rotation onset. **How close** in your own knob units is *not readable here*: the
  data carries no knob magnitudes / noise level / model parameters (you stated this), so headroom
  can only be reported qualitatively (interior, monotone, no edge attained), not as a number.
- **How would you know from the data if it tipped?** The tell of true cycling would be C(τ) dipping
  **below zero** (a negative lobe), and/or phiMean starting to **ramp steadily** instead of
  wandering, and/or Cxy and Cyx **splitting apart** (a directed current). None of those is present
  at any level. An instability tip would show up as the settling failing to complete inside a
  window — but every level fully settles.

## grounded[]
1. **KIND = settling not cycling, every level** — C(τ) decays monotonically to ~0 with no negative
   lobe (min_C > 0 at all 5 levels); a cycle would dip C below zero. *(column C)*
2. **No directed current / matched reciprocal coupling** — Cxy = Cyx to ~1e-6 at every row and
   level; the two directed cross-correlations agree → no circulation. *(columns Cxy, Cyx)*
3. **No sustained rotation** — phiMean stays a bounded wander near 0 (|phiMean| < ~1.1 at level 4)
   with no monotone ramp. *(column phiMean)*
4. **tauC per level (relaxation time): ~1.3, 2.4, 5.0, 10, 20** — log-linear fit of C; doubles each
   step; the "longer to settle." *(columns C, tau)*
5. **chi_inf per level (static integrated response): 1.07, 1.52, 2.69, 5.10, 9.98** — roughly
   doubles each step; the "bigger excursions." *(column chi)*
6. **Equilibrium FDR holds at every level** — χ vs (C0−C) linear (rms < 0.006), slope ≈ chi_inf ≈
   tauC within ~3%; three independent readings agree (J/L cross-check). *(columns chi, C)*
7. **Window sanity per level** — each level settles to <0.04% of C(0) inside its own (deliberately
   longer) tau window; the reading is not a camera artifact. *(columns tau, C)*
8. **phiVar grows ~linearly in elapsed time** at every level (diffusive spread), consistent with
   noise-driven wander about a fixed point. *(column phiVar)*

## not_grounded[] (the honest limits)
1. **Whether a 6th, stronger setting would finally cycle or tip unstable** — lives across the
   control axis **beyond level 4** (a collapsed axis; the sweep stops at level 4). The 5 points
   show a monotone, decelerating-but-not-diverging trend with no rotation onset; extrapolation past
   the last point is not groundable.
2. **Absolute distance to any instability/Hopf edge in native knob units** — no interaction-strength
   magnitudes, noise level, or model parameters are in the data (packet says so). Headroom is
   qualitative only (interior, monotone), not a number.
3. **An exact scaling law for tauC / chi_inf vs the knob** — only 5 settings and no knob magnitude;
   the band is read as monotone-increasing placements (≈doubling per step), not fit to a divergence
   law that could pin a critical knob value (would need the swept control magnitude + more points —
   collapsed axis).
4. **Which setting is "best/healthiest"** — a researcher preference / **viewport dial**, not a
   freeze computation; surfaced here, not pinned (WORKFLOW §6 value-laden carve-out).

## Falsifier / kill check
No KILL. No boundary attained at a finite point; no NaN; no negative C lobe (regime stays interior);
Cxy=Cyx so no current appears where the reciprocal structure forbids one (no J/L disagreement). The
structure (reciprocal loop, settling) is consistent across all 5 levels. Verdict: **nominal /
settling at every level; the band migrates in magnitude, the kind is invariant.**

view: `H:\mpa-conform\blockin\workspace\view_20260525-180834.png`
