# verdict — magnet_temp_sweep_v8  (DEV / blind answerer)

view: `H:\mpa-conform\blockin\workspace\view_20260525-201135.png`
script: `H:\mpa-conform\blockin\workspace\answer.py`

## placement (framework read)

Each level placed as an INDEPENDENT single-point fit first (§6 sweep rule), then the
band read off the placements.

| level | role    | C(0)   | fluct amp C(0)-C(inf) | tau_int (integral time) | tau_efold | window/tau_int | g_end (decay floor) | FDR slope (chi vs C0-C, thru origin) | R^2 | FDR sum-rule chi(inf)/[slope*var] |
|------:|---------|-------:|----------------------:|------------------------:|----------:|---------------:|--------------------:|-------------------------------------:|----:|----------------------------------:|
| 0 | coolest |  1.3655 | 1.3650 |  10.05 |  10.04 | 7.96 | ~0 | 1.0000 | 1.0000 | 1.000 |
| 1 |         |  3.4887 | 3.4875 |  32.26 |  32.09 | 7.94 | ~0 | 1.0000 | 1.0000 | 1.000 |
| 2 | MIDDLE  |  5.0000 | 4.9983 |  50.47 |  50.41 | 7.92 | ~0 | 1.0000 | 1.0000 | 1.000 |
| 3 |         |  2.8589 | 2.8580 |  25.18 |  25.17 | 7.94 | ~0 | 1.0000 | 1.0000 | 1.000 |
| 4 | warmest |  1.0119 | 1.0116 |   6.92 |   6.92 | 7.97 | ~0 | 1.0000 | 1.0000 | 1.000 |

- **FDR locus (universal readout):** at EVERY level `chi` vs `(C(0) - C(tau))` is a
  single straight line through the origin, slope = 1.0000, R^2 = 1.0000. Slope across
  the five levels: `[1.000, 1.000, 1.000, 1.000, 1.000]`, cv = 0.0000. Early-lag slope
  equals late-lag slope at every level (no bending of the locus).
- **band summary:** both the fluctuation amplitude `C(0)` and the relaxation timescale
  `tau_int` rise monotonically from the flanks toward the middle and fall away on the
  other side — a **single symmetric peak at level 2**. Amplitude
  C(0): 1.37 -> 3.49 -> 5.00 -> 2.86 -> 1.01. Timescale tau_int:
  10.0 -> 32.3 -> 50.5 -> 25.2 -> 6.9. Peak of both at level 2.
- **kernel pre-gate (box E):** window matched at every level — the autocorrelation
  reaches its floor (`g_end ~ 0`, normalized decay fallen to <~1e-3) within each level's
  own window, and each window spans ~8 integral times (`window/tau_int ~ 7.9` for all
  five). The slow-down is the material's own clock, not a too-short-watching artifact.

## verdict (researcher terms)

**Same kind of system at every temperature, all the way through — and nothing has
fallen out of equilibrium.** At each of your five temperatures the
fluctuation-dissipation locus (response chi vs the lost correlation C(0)-C) is one
straight line through the origin with the same slope (1.000, R^2 1.000). That is the
signature of ordinary thermal equilibrium relaxation holding at every setting. The
cool side and the warm side are **not** two different kinds of dynamics: levels 0 and 4
show the identical affine-through-origin FDR law and the same monotone decay shape — the
only thing that changes across your temperature axis is *magnitude*, not functional form.

The special middle (level 2) is **ordinary relaxation pushed to its extreme — critical
slowing-down — not a glassy/aging/frozen transition.** Both the fluctuation amplitude and
the relaxation time peak there in a single symmetric peak, exactly as critical slowing-down
predicts: things get big and sluggish as you approach the middle and recover on the far
side. There is no FDR violation (no effective-temperature split, the locus stays linear
through the origin), and the autocorrelation still fully relaxes to its floor within the
window at level 2 — both hallmarks that it is still settling back to balance, just very
slowly. **Headroom:** the binding edge is the slow-window / long-time end — the timescale
balloons toward the middle (longest at level 2, ~5-7x the flanks) but you have not crossed
into glassy/aging behaviour; level 2 is the interior point farthest from the fast-settling
end, with room remaining (the curve still completes its relaxation). You can stop worrying:
it is one ordinary equilibrium relaxation throughout, with a critical slow-down at level 2.

## grounded[]

- **SAME KIND of dynamics across all 5 levels** <- FDR locus chi vs (C(0)-C) is linear
  through the origin at every level; slopes [1.000, 1.000, 1.000, 1.000, 1.000],
  R^2 = [1.0, 1.0, 1.0, 1.0, 1.0], cv 0.0000. One equilibrium FDR law throughout.
- **STILL IN EQUILIBRIUM (not glassy/aging), every level incl. the middle** <- FDR slope
  constant (no FDR-violation / two-temperature split), locus passes through the origin
  (chi -> 0 as C -> C(0)), and the equilibrium sum rule closes: chi(inf) / [slope*(C(0)-C(inf))]
  = [1.000, 1.000, 1.000, 1.000, 1.000].
- **COOL SIDE == WARM SIDE in kind** <- levels 0 and 4 share the same affine-through-origin
  FDR locus (slopes 1.000 vs 1.000) and the same monotone single-relaxation decay shape;
  difference across the axis is magnitude only.
- **SPECIAL MIDDLE = critical slowing-down (ordinary relaxation at its extreme)** <-
  fluctuation amplitude C(0) peaks at level 2 (1.37, 3.49, 5.00, 2.86, 1.01) and integral
  timescale tau_int peaks at the same level 2 (10.0, 32.3, 50.5, 25.2, 6.9); both form a
  single symmetric peak (the BAND box).
- **WINDOW MATCHED at every level (kernel pre-gate, box E)** <- normalized autocorrelation
  falls to its floor within each level's own window (g_end ~ 0, all <~1e-3) and each window
  spans ~8 integral times (window/tau_int ~ 7.9 for all five); the slow-down is the
  material's, not a camera artifact.

## not_grounded[]

- **Absolute temperatures / how close level 2 sits to the true critical temperature (in
  Kelvin)** — the packet carries no temperature values or material constants; no axis for
  it in the data (collapsed axis, legitimate park).
- **Whether a finer temperature step would reveal a sharper or shifted peak (true T_c
  location, critical exponents)** — the band is sampled at only 5 settings; resolving the
  peak shape needs a denser temperature sweep (crosses the coarsely-sampled temperature
  axis).
- **Behaviour at lag longer than each window (does any level eventually age / fail to
  fully relax beyond what was watched)** — each window was cut once its own relaxation
  completed, so anything past the recorded floor crosses the lag-extent axis the data does
  not span. (Within the watched window every level fully relaxes — which is what grounds
  the in-equilibrium verdict.)
- **Any directional / cyclic / current-bearing (k_frust) structure** — a single scalar
  with symmetric monotone C and an affine FDR shows no current signature, and there is no
  second channel or phase observable in the data to test for a sustained current (collapsed
  channel axis).
