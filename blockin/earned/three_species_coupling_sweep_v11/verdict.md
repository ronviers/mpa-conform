# three_species_coupling_sweep_v11 — BLIND ANSWERER VERDICT (as returned)

phase: DEV/blind · view: `view_20260526-013443.png` · analysis: `answer.py`

**There is a genuine directed cycle at every coupling strength, including the weakest. The turnover
rate tracks the interaction strength almost exactly linearly — strengthen the loop, the community
cycles proportionally faster. The interaction strength is what sets the turnover rate. No onset
threshold, no instability.** Method: five independent single-point placements, then the band.

## placement (the numbers)

| level | coupling_rel | Cxy=−Cyx? (antisym resid) | peak \|Cxy\| | winding rate (cyc/τ) | osc freq (cyc/τ) | C(0) | χ∞ | stable? |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.25× | yes, 0.0 | 0.082 | 0.040 | 0.040 | 0.69 | 0.719 | bounded |
| 2 | 0.5× | yes, 0.0 | 0.181 | 0.083 | 0.081 | 0.83 | 0.649 | bounded |
| 3 | 1.0× | yes, 0.0 | 0.330 | 0.164 | 0.163 | 0.91 | 0.402 | bounded |
| 4 | 2.0× | yes, 0.0 | 0.523 | 0.331 | 0.329 | 0.95 | 0.146 | bounded |
| 5 | 4.0× | yes, 0.0 | 0.705 | 0.661 | 0.660 | 0.97 | 0.033 | bounded |

**Band:** rate normalized to the level-3 baseline matches the coupling ratio to within ~2% at every
point (coupling ×0.25/×0.5/×2/×4 → winding-rate ×0.24/×0.51/×2.02/×4.02). Log-log power-law exponent
**p = 1.008 (winding), 1.013 (autocorr osc)** — exact linear tracking. The two independent rate reads
(autocorr oscillation frequency and winding drift) agree at every level. Current magnitude (peak
\|Cxy\|) rises monotonically with coupling. No amplitude runaway; χ saturates finite everywhere.

## verdict in the researcher's terms
- **Directed cycle at every strength** (including weakest); **turnover rate tracks coupling, near-linear**
  (strengthen the loop → proportionally faster cycling). The interaction strength sets the rate.
- **No onset threshold, no instability.** Rate is graded/continuous, nonzero at every level; stable
  throughout.

## grounded[]
- directed current at every level ← Cxy=−Cyx exactly (max\|Cxy+Cyx\|=0 per level)
- cycle survives the weak end ← level 1 (0.25×): peak\|Cxy\|=0.082, winding climbs monotonically to 37.2 rad
- rate tracks coupling, near-linear ← winding drift 0.040→0.661 cyc/τ across levels 1→5; log-log slope p=1.01
- second independent rate read agrees ← autocorr oscillation frequency 0.040→0.660 cyc/τ, same trend
- no all-or-nothing onset ← rate graded/continuous, nonzero at every level
- stable, no blowup ← autocorr amplitude never exceeds C(0); χ saturates finite at every level
- rate not set by noise (consistent with the cited prior run) ← noise fixed here, yet rate changes 16× → coupling alone

## not_grounded[] (the honest limits — collapsed-axis parks)
- absolute rate / coupling in native units (only relative coupling + each run's own τ-clock given)
- behaviour exactly at zero coupling (weakest sampled = 0.25×; rate→0 is extrapolation)
- behaviour above 4× baseline (past the window — linear vs saturating vs destabilizing unknown)
- exact exponent to high precision (p≈1.01 from 5 points consistent with linear, not tightly pinned)
- which population leads / absolute loop phase (only the 2D turnover-plane projection given)
- cross-check against an independent collective observable (only reduced two-point + winding given)

Blinding held: only the four permitted files read. **Self-graded MATCH.**
