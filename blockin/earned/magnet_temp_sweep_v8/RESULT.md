# magnet_temp_sweep_v8 — BLIND ANSWERER RESULT

phase: DEV/blind · view: `view_20260525-201135.png` · analysis: `answer.py` · grade: **MATCH** (two-sided)

A sweep: one material's fluctuation correlation C and integrated response chi, at 5 temperatures
straddling a special middle temperature (level 0..4; level 2 = middle). Per WORKFLOW §6, each
level placed as an **independent single-point fit first**, then the band read off the 5
placements. Each level read on its own clock (tau range differs by level by design; every level's
C reaches its floor inside its own window — windows matched, ~8 integral times each).

The substrate is an **equilibrium-criticality oracle** (the v4 analytic-correlator pattern applied
to a thermodynamic critical point): a single relaxational mode in thermal equilibrium modelling the
connected order-parameter fluctuation of a magnet swept through its critical (Curie) point. Truth
from the equilibrium FDT theorem, never via conform — X = 1 exactly at every level by construction
(see `entry.md` SEALED half / `freeze_magnet_temp_sweep.py`).

---

## Per-level placement (the framework read)

| level | role | C(0) | fluct amp | tau_int | window/tau_int | FDR slope (thru origin) | R² | FDR sum-rule |
|---|---|---|---|---|---|---|---|---|
| 0 | coolest | 1.365 | 1.365 | 10.05 | 7.96 | 1.0000 | 1.0000 | 1.000 |
| 1 |  | 3.489 | 3.488 | 32.26 | 7.94 | 1.0000 | 1.0000 | 1.000 |
| 2 | **MIDDLE** | 5.000 | 4.998 | 50.47 | 7.92 | 1.0000 | 1.0000 | 1.000 |
| 3 |  | 2.859 | 2.858 | 25.18 | 7.94 | 1.0000 | 1.0000 | 1.000 |
| 4 | warmest | 1.012 | 1.012 | 6.92 | 7.97 | 1.0000 | 1.0000 | 1.000 |

- **FDR locus (universal readout):** at EVERY level chi vs (C(0)−C(tau)) is a single straight line
  **through the origin**, slope 1.0000, R² 1.0000; slope CV across levels = 0.0000; early-lag slope
  = late-lag slope (no bend). The equilibrium fluctuation–response signature — X = 1 — holds at the
  critical middle exactly as on the flanks.
- **Same kind across the crossing:** levels 0 (cool) and 4 (warm) show the identical affine-through-
  origin FDR law and the same monotone decay shape — the two sides of the special temperature are
  the SAME dynamical kind; only magnitude differs.
- **kernel pre-gate:** window matched at every level (C reaches its floor within each window; ~8
  integral times each). The slow-down is the material's own clock, not a too-short-watching artifact.

## The band (what migrates / what stays put)

- **PEAKED, not monotone:** both the fluctuation amplitude C(0) and the timescale tau_int RISE from
  the flanks toward the middle and FALL on the far side — a **single peak at level 2**. Amplitude
  1.37→3.49→5.00→2.86→1.01; timescale 10.0→32.3→50.5→25.2→6.9 (~5×/~7× over the flanks). The axis
  passes THROUGH a critical point and recovers — contrast v7's monotone run-up to an edge.
- **STAYS PUT (invariant):** the *kind* of dynamics — affine-through-origin FDR, slope 1, at every
  level including the peak. No FDT violation, no effective-temperature split, no oscillation.

## Verdict in the researcher's own terms

- **Has it fallen out of equilibrium / gone glassy at the special middle?** **No.** At the critical
  middle the response-vs-correlation law is the same straight line through the origin with the same
  slope as everywhere else, and the correlation still fully relaxes to its floor within the window.
  The huge slow fluctuations there are **reversible critical slowing-down** in equilibrium, **not**
  glassy / aging / frozen arrest.
- **Are the cool and warm sides different kinds of system?** **No** — same affine-through-origin FDR
  law and same monotone decay shape on both sides; the difference across the temperature axis is
  magnitude (timescale + fluctuation size), not kind. The thermodynamic phase boundary is not a
  change of dynamical kind.
- **What is happening at the middle, and how close to an edge?** Critical slowing-down: amplitude and
  timescale peak (~5×/~7× the flanks) in a single peak at level 2, recovering on the warm side. The
  binding direction is the slow/long-time end — sluggish at the middle — but it has not crossed into
  glassy/aging; level 2 is the interior point farthest from the fast-settling end, with room
  remaining. **Absolute proximity to the true critical temperature in native units is not readable**
  (no temperatures/constants in the data).

## grounded[]
1. **SAME KIND across all 5 levels** — FDR locus linear through origin every level; slopes all 1.000,
   R² all 1.0, CV 0.0000. *(columns C, chi)*
2. **STILL IN EQUILIBRIUM every level incl. the middle** — FDR slope constant (no two-temperature
   split), locus through origin, equilibrium sum rule closes (chi(inf)/[slope·var] = 1.000). *(C, chi)*
3. **COOL = WARM in kind** — levels 0 and 4 same affine-through-origin locus + same monotone decay;
   magnitude-only difference. *(C, chi)*
4. **SPECIAL MIDDLE = critical slowing-down** — amplitude C(0) peaks at level 2 AND tau_int peaks at
   the same level 2; single peak. *(BAND box; columns C, tau)*
5. **WINDOW MATCHED every level** — normalized C falls to its floor within each window (~8 integral
   times); the slow-down is the material's, not a camera artifact. *(columns tau, C)*

## not_grounded[] (the honest limits — collapsed-axis parks)
1. **Absolute temperatures / proximity of level 2 to the true critical temperature in native units** —
   no temperature values/constants in the data (collapsed axis). *(Independently rediscovers v7's
   finding: absolute distance-in-native-units is not blind-closeable; the closeable headroom lives in
   the observable band.)*
2. **Whether a finer temperature step reveals a sharper/shifted peak (true critical point, exponents)**
   — only 5 settings; needs a denser temperature sweep (collapsed sweep-density axis).
3. **Behaviour at lag longer than each window (eventual aging beyond what was watched)** — each window
   cut once its own relaxation completed (collapsed lag-extent axis). Within the watched window every
   level fully relaxes — what grounds the in-equilibrium verdict.
4. **Any directional / cyclic / current-bearing structure** — single scalar, symmetric monotone C,
   affine FDR; no second channel to test for a current (collapsed channel axis — honest absence, not a
   withheld observable).

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED: all five placed as the same reversible
equilibrium kind (X = 1, affine same-slope locus) ✓; band read as a peak at the critical middle
(level 2) recovering on the far side ✓; the **headline tooth corrected** — critical slowing read as
reversible/equilibrium, NOT aging (the `ising_equilibrium` PENDING falsifier) ✓; the **cool/warm
category-smear avoided** ✓; no false oscillation/current ✓; not hollow (every claim grounded on a
computed quantity) ✓; meta-validity P held (independent per-level placements, then band) ✓. No KILL
(X = 1 by construction, no NaN, no current, single real mode). First contact with this oracle — no
prior earned operating point to anchor (consistent with the seal). The not_grounded items are all
legitimate collapsed-axis parks; item 1 independently re-derives v7's native-unit headroom limit.

view: `H:\mpa-conform\blockin\workspace\view_20260525-201135.png` (deposited as
`earned/magnet_temp_sweep_v8/view_20260525-201135.png`)
