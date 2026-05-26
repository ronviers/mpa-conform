# entry — magnet_temp_sweep_v8
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I work on a magnetic material, and I've been mapping how its magnetization fluctuations
relax as I change its temperature. I took five temperatures, stepping from below a particular
middle temperature, right through it, to above it (levels 0 through 4 — level 0 is the
coolest, level 4 the warmest, and level 2 is that special middle temperature). Here's the
thing that has me worried: away from that middle temperature — whether cooler or warmer — the
fluctuations are small and die away quickly. But as I approach the middle temperature they
swell up enormously and take far, far longer to settle. Right *at* that middle temperature
they're huge and crawl back so slowly I can barely watch them finish. So: at that special
middle temperature where everything goes big and sluggish, has my material fallen *out of
equilibrium* — gone glassy, frozen, "aging" on me, the kind of thing that won't come back to
thermal balance? Or is it still just relaxing the ordinary way, only much more slowly? For
each temperature I want to know — is it still a normal settling-back-to-balance, or has it
turned into something else? And the big one: is the cool side a fundamentally *different kind*
of dynamical behaviour from the warm side — two different sorts of system either side of that
middle — or is it the *same kind* of relaxation all the way through, just with that slow-down
in the middle?

**minimal_structure:**
One material; one fluctuating quantity in it (a single scalar — the magnetization
fluctuation), observed at five temperatures that straddle a special middle temperature
(level 0 = coolest … level 2 = the special middle … level 4 = warmest). The only thing that
changes from level to level is the temperature; the material and the measurement are otherwise
the same. Each temperature was watched long enough for its own relaxation to play out — so the
observation windows differ in length across levels (the middle one needs the longest watching,
deliberately).

**what_they_bring:**
For each of the five temperatures, one measurement window reduced to two standard curves of
the fluctuating quantity: its autocorrelation C (how the fluctuation at one moment stays
correlated with itself a lag later) and its integrated step-response chi (how much the
quantity shifts in response to a small steady push, accumulated over the same lag). No
temperature values, no model parameters, no material constants — just these two measured
curves, the same pair at each of the five settings.

**data_path:**
`data/magnet_temp_sweep_v8.frozen.csv`
(columns: level, tau, C, chi. Five operating points — one material at five temperatures.
level is 0…4 (coolest→warmest; level 2 is the special middle temperature); tau is the
material's own clock — a lag. Each level has its own settling window, so tau ranges differ
across levels.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** the METRIC-boundary-CROSSING probe — the one separability case v6 and v7 left
open. The substrate stays **category 1 (Vertex / reversible equilibrium relaxation)** at every
level, INCLUDING the critical middle. The vertical asks whether Cat 1 SMEARS when a CONTINUOUS
(metric) control axis — temperature — is driven THROUGH a thermodynamic critical point (a
phase boundary), as opposed to v7's axis that monotonically APPROACHED a stability edge. v6
showed the discrete 1↔10 cut is topologically sharp; v7 showed Cat 1 does not smear along a
metric axis *within* a category (it critically slows toward an EDGE it never reaches). The open
question was the boundary-CROSSING case: does the dynamical KIND change as the axis passes
through criticality into the far phase? Sealed answer: it does NOT smear. The KIND is invariant
(reversible Cat-1, X = 1) at every level; the critical point shows up ONLY as a PEAK in the
relaxation timescale and the susceptibility at the middle level (critical slowing + diverging
susceptibility), recovering on the far side. A thermodynamic phase boundary is NOT an MPA
dynamical-category boundary. This is the X = 1 (reversible) counterpart to v4's X < 1 (aging)
glass along the same diverging-timescale signature, and it closes the `ising_equilibrium`
PENDING falsifier in FALSIFICATION.md ("critical slowing ≠ aging") on a clean substrate.

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched
isolated placements**, PIPELINE §PHASE INTERFACE): place each of the five temperatures as an
INDEPENDENT single-point fit, then read the band (the PEAK of the relaxation timescale and the
susceptibility at the critical middle, and its recovery on the far side). The MISS must
localize to one module — a single placement, or the band readout. The ONE added vector over v7
is that the metric axis CROSSES a critical point (a non-monotonic, peaked-and-recovering band
through a phase boundary) rather than monotonically approaching an edge — the human-elected
load-bearing separability frontier.

**substrate:** an EQUILIBRIUM-CRITICALITY ORACLE (the v4 analytic-correlator pattern applied to
a thermodynamic critical point), materialized by `freeze_magnet_temp_sweep.py`. A single
relaxational mode in thermal equilibrium modelling the CONNECTED order-parameter fluctuation of
a magnet swept through its critical (Curie) temperature:
  C(tau)   = C0(g) · exp(-lam(g)·tau)            (connected correlator → 0)
  chi(tau) = (C0(g)/T) · (1 - exp(-lam(g)·tau))  (equilibrium FDT)
with T = 1, gap lam(g) = lam_floor + kappa·(g - g_c)², and susceptibility amplitude
C0(g) = chi_peak·(lam_floor/lam(g))^(gamma/(z·nu)), gamma/(z·nu) = 1.75/2.17 = 0.806 (2D-Ising,
model-A critical exponents). Five control offsets delta = g - g_c = [-0.40, -0.15, 0, +0.20,
+0.50] (level 2 = critical, delta = 0). Truth from the equilibrium FDT theorem, never via
conform: a single relaxational equilibrium mode has an EXACTLY affine FDR locus chi vs (C0 - C)
of slope 1/T and X = 1, at every level, independent of lam and C0 — so the critical slowing
(lam dips → tau_corr peaks) and the susceptibility divergence (C0 peaks) leave X = 1 untouched.
**Why the oracle and not the library `ising_equilibrium` MC cells:** the finite-L (L=32) cells
do not cleanly EXHIBIT X = 1 across the transition — the ordered phase plateaus at the frozen
magnetization m² (spin-flip C barely decays; the locus goes degenerate/near-vertical) and the
critical cell is noisy, so a blind X = 1 read off the raw cells would not isolate conform; the
library's intended clean X-read routes through conform's `fit_kww5` (the EXAMINEE), which cannot
seal. The oracle models the connected correlator directly, equilibrium-FDT-exact, exactly as
v4's kww_oracle sealed its X < 1. (Onsager Tc = 2.269 and equilibrium X = 1 are the external
physics this idealizes; the oracle is the clean stand-in until the library refresh places the
glass/ising camera-scale — DEFERRED.md.) The CSV carries NO g, g_c, lam, C0, T, tau_corr,
susceptibility, slope, X, exponents, or framework token — only level, tau, C, chi and a neutral
0…4 index. Native temperatures are withheld (v7: absolute distance-in-native-units is not
blind-closeable; the closeable content is the observable band).

**collapsed_axes:** FIXED across the sweep: the bath T (FDR units), the gap-dip curvature
kappa, the critical exponent, the single-mode (scalar) structure, equilibrium. The single dial
is the **temperature** (the metric axis, expressed as the control offset delta from criticality).
Declared + reversible: re-run the freeze at other delta to add/extend levels. **Boundary note
(WORKFLOW §4):** within each level's window the blind data carries the complete honest content
(C and chi, the full two curves a correlation+response measurement yields). The honest parks are
across the remaining collapsed axes (the native temperature magnitudes; the behaviour of a
second observable / a conserved channel; dynamics actually AT or beyond a true divergence, which
finite-size rounding replaces with a finite peak — not sampled). There is no current/two-axis
channel to withhold: a scalar equilibrium relaxation has no current sector (its absence is
honest content, not a curated omission).

**kernel_window:** each level gets its OWN settling window (~8 e-foldings of that level's slow
mode), so the diverging-then-recovering relaxation time is honestly resolved per level (windows
grow toward the critical middle, then shrink again). This is the correct camera per level, not
an artifact: the longer settling at the critical temperature is real critical slowing, and the
window is matched to it. (No tau_obs sweep within a level; the kernel pre-gate's k_frust-
invariance concern does not bind a reversible, current-free relaxation.)

**answer_path (analytic — never via conform):**
For a single relaxational equilibrium mode the fluctuation-dissipation theorem gives
chi(tau) = (1/T)·(C(0) - C(tau)) EXACTLY → the FDR locus is affine, slope 1/T, R² = 1, X = 1, at
EVERY level. lam(g) and C0(g) set only the timescale and the amplitude, not the slope. Exact
scalars (COMPUTED by the freeze, `python freeze_magnet_temp_sweep.py`):

  level | delta | lam(gap) | tau_corr | C0 = chi_static | FDR slope | R²  | X
  ------+-------+----------+----------+-----------------+-----------+-----+----
    0   | -0.40 |  0.1000  |   10.00  |      1.365      |   1.000   | 1.0 | 1.0
    1   | -0.15 |  0.0312  |   32.00  |      3.489      |   1.000   | 1.0 | 1.0
    2   |  0.00 |  0.0200  |   50.00  |      5.000      |   1.000   | 1.0 | 1.0   (CRITICAL — peak)
    3   | +0.20 |  0.0400  |   25.00  |      2.859      |   1.000   | 1.0 | 1.0
    4   | +0.50 |  0.1450  |    6.90  |      1.012      |   1.000   | 1.0 | 1.0
  band: tau_corr = [10, 32, 50, 25, 6.9] (PEAK at level 2, ~7× range, non-monotonic — rises to
  the middle, recovers on the far side); chi_static = C0 = [1.37, 3.49, 5.00, 2.86, 1.01] (PEAK
  at level 2, tied to tau_corr by the 2D-Ising exponent chi ~ tau_corr^0.806). At every level
  the FDR locus is affine (R² = 1, slope = 1/T): X = 1. C is monotone single-exponential (no
  zero-crossing → no oscillation); scalar equilibrium mode (no current sector).

THE READ: sweeping the temperature THROUGH the critical point does NOT change the KIND of
system — at every temperature it is a reversible equilibrium relaxation (affine FDR locus, same
slope → X = 1; monotone C → no oscillation; scalar equilibrium → no current). What changes is
the relaxation timescale and the fluctuation size, which PEAK at the critical middle level
(critical slowing + diverging susceptibility) and RECOVER on the far side. The huge slow
fluctuations at the critical temperature are EQUILIBRIUM critical fluctuations (X = 1), NOT
out-of-equilibrium glassy aging (X < 1). The cool side and the warm side are the SAME dynamical
kind. This is the boundary-CROSSING (peak-and-recover) counterpart to v7's boundary-APPROACH
(monotone divergence toward an edge), and the X = 1 reversible counterpart to v4's X < 1 aging.

**cage_edges:**
- if_answerer_finds: "at the critical middle temperature the material has fallen OUT OF
  EQUILIBRIUM — it's GLASSY / FROZEN / AGING, an FDT-violated (X<1) slow mode" → MISS
  (false aging) → route_to: 8 (Phase/glassy). The FDR locus is AFFINE (R²=1, slope 1/T, X=1)
  at EVERY level including the critical one — FDT holds; this is reversible critical slowing,
  not aging. The trap is reading the diverging timescale / huge slow fluctuations at the
  critical point as a second-slope X<1. THIS IS THE HEADLINE TOOTH (the ising_equilibrium
  PENDING falsifier). signature: "two-slope / bent FDR locus, X<1, aging, glassy, frozen,
  out-of-equilibrium, non-equilibrium slow mode at the critical temperature."
- if_answerer_finds: "the cool side and the warm side are DIFFERENT KINDS of dynamical system /
  two different regimes either side of the middle / the dynamical class changes across the
  critical point" → MISS (category smear — the separability tooth). All five levels are the SAME
  reversible Cat-1 equilibrium relaxation (same affine locus slope, X=1); the cool/warm
  difference is in MAGNITUDE (timescale, susceptibility), not KIND. A thermodynamic phase
  boundary is not a dynamical-category boundary. signature: "two phases / two regimes / two kinds
  of dynamics / the dynamical class flips across the middle."
- if_answerer_finds: "the material starts to OSCILLATE / ring / develop a current or
  circulation as temperature changes" → MISS (false oscillation/current) → route_to: 10
  (Non-Reciprocal). C is monotone single-exponential (no zero-crossing) at every level; the
  observable is a single scalar in equilibrium (no current sector). signature: "oscillatory /
  ringing / cycling / directional-current onset."
- if_answerer_finds: "nothing special happens at the middle temperature / the band is flat /
  no critical slowing" → MISS (under-read). tau_corr and the fluctuation size PEAK ~7×/~5× at
  level 2 — missing the critical peak is a half-reading of the band. signature: "flat band / no
  peak / nothing critical at the middle."
- if_answerer_finds: "the critical slow-down / the peak is at the coolest (or warmest) setting"
  OR "it's a MONOTONE divergence — getting steadily worse toward one end, approaching an edge"
  → MISS (mislocated peak / wrong band shape). The peak is at the MIDDLE (level 2) and the band
  RECOVERS on the far side — a peak-and-recover through a critical point, NOT a monotone
  approach to an edge (the v7 contrast). signature: "peak at level 0/4 / monotone band /
  approaching an edge at one end without recovery."

**sealed_answer:**

TARGET
  per level:        a reversible EQUILIBRIUM relaxation that settles back to balance — a single
                    kind of system at every temperature, INCLUDING the critical middle. The
                    fluctuation correlation decays smoothly to zero (monotone, no rotation), and
                    the response tracks it so that the response-vs-correlation relation is a
                    clean straight line of the SAME slope at every temperature (FDT holds;
                    entropy production zero).
  the band:         the relaxation TIMESCALE and the SIZE of the fluctuations both PEAK at the
                    critical middle temperature (level 2) — settling ~7× slower and fluctuations
                    ~5× bigger there than at the extremes — and RECOVER (faster, smaller) on the
                    far (warm) side. A PEAK passed THROUGH, not a monotone run-up to an edge.
                    This is CRITICAL SLOWING + a susceptibility peak at the critical point.
  same kind, or changed? SAME KIND all the way through — across the critical point it does not
                    become glassy/aging, does not start oscillating or cycling, and does not
                    split into two different dynamical regimes either side. Sweeping the
                    temperature through the critical point changes the OPERATING POINT (timescale
                    + fluctuation size, peaking at the middle), NOT the kind of system.
  out of equilibrium? NO — at the critical middle it is still in equilibrium (the response-vs-
                    correlation line keeps the same slope there as everywhere else; FDT intact,
                    X=1). The huge slow critical fluctuations are EQUILIBRIUM critical
                    fluctuations, not glassy/aging arrest.
  naive correction: the worry "at the critical temperature it's gone glassy / frozen / fallen
                    out of equilibrium / is aging" is WRONG — it is reversible CRITICAL SLOWING
                    (equilibrium FDT intact). The huge slow fluctuations are the signature of a
                    critical point being PASSED THROUGH in equilibrium, not of arrest. And the
                    cool side is not a different kind of system from the warm side.

MATCH
  The answerer places ALL five levels as the SAME KIND of system — a reversible equilibrium
  relaxation that settles (monotone C with no zero-crossing → no oscillation; a response-vs-
  correlation locus that is a straight line of the SAME slope at every level → equilibrium / FDT
  / X=1, NOT aging) — and reads the BAND as a PEAK in the relaxation timescale AND the
  fluctuation size at the critical MIDDLE level (level 2), RECOVERING on the far side (a peak
  passed through, not a monotone run-up). It answers "does the kind change across the critical
  point?" as NO (same reversible equilibrium relaxation throughout, just dramatically slower and
  bigger at the middle), corrects the naive worry (it is critically slowing in EQUILIBRIUM at
  the critical temperature, NOT going glassy/aging), and does NOT split the cool/warm sides into
  different dynamical kinds. It need NOT say "X=1," "FDT," "spectral gap," "critical exponent,"
  or "susceptibility": a researcher-facing "it's the same kind of equilibrium settling at every
  temperature — it never goes glassy, frozen, or aging, and never starts oscillating or cycling —
  but right at your special middle temperature the fluctuations get about 5× bigger and about 7×
  slower (critical slowing), then ease back off as you go warmer; you're passing THROUGH a
  critical point in equilibrium, not turning into a different kind of system" is a MATCH. The
  no-aging / still-equilibrium claim must be grounded on the affine, same-slope response-vs-
  correlation locus (at the critical level too); the same-kind claim on the locus staying the
  same shape across levels; the critical-slowing / peak claim on the per-level relaxation time
  and fluctuation size and their peak at the middle with recovery beyond. Empty provenance on
  any → hollow.

MISS
  Reads the critical middle as out-of-equilibrium / glassy / aging / X<1 (cage_edge 1, → 8);
  OR splits the cool and warm sides into DIFFERENT dynamical kinds / two regimes (cage_edge 2,
  category smear); OR reads an oscillation / current / cycling onset (cage_edge 3, → 10); OR
  misses the critical peak — calls the band flat / nothing-special (cage_edge 4); OR mislocates
  the peak to an extreme level or reads a monotone divergence toward an edge instead of a
  peak-and-recover through the middle (cage_edge 5). A monolithic migration fit that cannot
  localize a MISS to one module (a single placement vs the band readout) also fails
  meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. a NONZERO entropy production / sustained current reported as GROUND TRUTH for any level
     (the oracle is a scalar equilibrium relaxation — detailed balance by construction) — an
     author-side / freeze check; an ANSWERER reading a false current is a MISS (cage_edge 3),
     not a KILL.
  3. a complex eigenvalue pair / genuine oscillation in the GROUND TRUTH at any level (the
     oracle is a single real relaxational mode by construction) — a freeze check.
  4. the FDR locus reported with X > 1 at any level (X > 1 is a theorem violation).
  5. X reported NOT equal to 1 in the GROUND TRUTH at any level (the oracle is equilibrium FDT
     by construction — X = 1 exactly at every level; a ground-truth X ≠ 1 means a broken
     freeze, not a finding) — a freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
FIRST CONTACT with this oracle — no prior earned operating point on an equilibrium scalar-
relaxation substrate to anchor to. (v7's matched community is the nearest reversible X=1 point
but is a different substrate and a 2-axis observable, so it is not an apt cross-pass anchor.)
No anchor this pass; cross-pass drift detection on this substrate resumes when a second
operating point is posed against it.

**what this vertical tests (ledger residue seed):** can conform take a researcher's magnet,
measured at five temperatures straddling its critical point and described only as "the
fluctuations go huge and sluggish at the middle temperature — has it gone glassy / fallen out
of equilibrium, and are the two sides different kinds of system?" — and (a) place all five as
the SAME KIND (a reversible equilibrium relaxation: monotone C → no oscillation, affine same-
slope response-vs-correlation locus → X=1 equilibrium, scalar → no current), (b) read the band
as a PEAK in relaxation time + fluctuation size at the critical middle, recovering on the far
side (critical slowing + susceptibility peak passed THROUGH, not a monotone run-up to an edge),
(c) avoid the false-aging misread at the critical point (the headline tooth — the
ising_equilibrium PENDING falsifier), the category-smear (cool/warm = two kinds), the false
oscillation/current onset, the under-read (no peak), and the mislocated/monotone band, and
(d) correct the naive "it's gone glassy/aging at the critical temperature" worry — it is
reversible critical slowing in equilibrium. This is the METRIC-boundary-CROSSING companion to
v6 (discrete cut, sharp) and v7 (metric axis within a category, sharp): it tests whether Cat 1
smears when the axis CROSSES a thermodynamic critical point (it does not — the category stays
sharp; only the operating point peaks at criticality and recovers), and it closes the
ising_equilibrium "critical slowing ≠ aging" PENDING falsifier on a clean substrate. The
headline MISS is false aging at the critical point or a cool/warm category smear; the win is
"same reversible equilibrium relaxation all the way through, critically slowing and swelling at
the middle then recovering — passing through a critical point, not changing kind."
