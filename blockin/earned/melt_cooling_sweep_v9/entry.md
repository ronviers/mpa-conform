# entry — melt_cooling_sweep_v9
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.
#
# STATUS: STAGED, NOT YET POSED. Freeze built + run; seal freeze-computed and
# human-glanced (Ron, 2026-05-25). Next session: §0 reconcile, re-glance, pose, run the
# blind pass. Registered in PENDING.md as expected-float.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I work on a material that flows like a (very viscous) liquid when it's warm but stiffens up
into a solid-ish state when I cool it — it doesn't crystallize, it just gradually stops
flowing. I've measured how its internal fluctuations relax at five temperatures, stepping
from warm down to cold (levels 0 through 4; level 0 is the warmest, level 4 the coldest).
When it's warm the fluctuations relax cleanly and completely. As I cool it they get a lot
slower, and a two-stage character appears: a quick partial drop, then a long slow crawl the
rest of the way down. At the coldest settings that slow crawl takes so long I'm not sure it
ever actually finishes inside my measurement. Here's what worries me: when a material gets
this sluggish on cooling, it can stop being a normal warm liquid that's just slow, and instead
fall *out of thermal equilibrium* — get stuck, "age," stop properly relaxing back to balance,
so that its response to a push no longer matches its own fluctuations the way an
equilibrium material's does. So for each temperature I want to know: is this still an ordinary
liquid that's merely slow (still in thermal balance), or has it genuinely fallen out of
equilibrium and started aging? If it's somewhere in between, *how far* out of balance is it?
And the big one: as I cool from warm to cold, does the change from "ordinary liquid" to "stuck
/ aging" happen ABRUPTLY at one particular temperature — a sharp switch — or GRADUALLY across
a range, with the middle temperatures sitting partway between the two?

**minimal_structure:**
One material; one fluctuating quantity in it (a single scalar), observed at five temperatures
as it is cooled from warm (level 0) to cold (level 4). The only thing that changes from level
to level is the temperature; the material and the measurement are otherwise the same. Each
temperature was watched long enough for its own slow relaxation to (mostly) play out — so the
observation windows differ in length across levels, the cold ones much longer than the warm
ones (deliberate: the cold settings relax far more slowly).

**what_they_bring:**
For each of the five temperatures, one measurement window reduced to two standard curves of
the fluctuating quantity: its autocorrelation C (how the fluctuation stays correlated with
itself a lag later) and its integrated step-response chi (how much the quantity shifts in
response to a small steady push, accumulated over the same lag). No temperature values, no
model parameters, no material constants — just these two measured curves, the same pair at
each of the five settings.

**data_path:**
`data/melt_cooling_sweep_v9.frozen.csv`
(columns: level, tau, C, chi. Five operating points — one material at five temperatures.
level is 0…4 (warmest→coldest); tau is the material's own clock — a lag. Each level has its
own settling window, so tau ranges differ across levels, the cold ones reaching to much
longer lags.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** the DYNAMICAL-category-CROSSING probe — the ONE separability case left open after
v8. The substrate CROSSES a real dynamical-category boundary as it is cooled through its glass
transition Tg: from **category 1 (Vertex / reversible equilibrium relaxation, X=1)** at warm
temperatures to **category 8 (Phase / glassy aging, X<1)** at cold ones. v6 (discrete
reciprocity cut), v7 (metric axis WITHIN a category), and v8 (metric axis crossing a
THERMODYNAMIC critical point in equilibrium) all stayed SHARP — no smear. v8 sharpened the
form: a thermodynamic phase boundary is not a dynamical-category boundary (crossing it in
equilibrium keeps X=1). This vertical tests the genuine kind-crossing v8 was the foil for:
equilibrium → out-of-equilibrium AGING (X:1→<1). **Sealed answer: this crossing SMEARS** — X
crosses 1→0.5 SMOOTHLY across Tg, the intermediate levels sit at intermediate X (partially
aged), because the glass transition is a KINETIC crossover, not a sharp transition. So v9 is the
**first axis tested that smears** — distinct from the topologically-sharp reciprocity cut (v6)
and the no-kind-change metric axes (v7/v8). It is the X<1 (aging) dynamical-crossing counterpart
to v8's X=1 (equilibrium) thermodynamic-crossing, and the swept counterpart to v4's single deep-
aging point.

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched isolated
placements**, PIPELINE §PHASE INTERFACE): place each of the five temperatures as an INDEPENDENT
single-point fit, then read the band (the X crossover 1→0.5, the deepening plateau q_EA, the
growing α-time). The MISS must localize to one module — a single placement, or the band readout.
The ONE added vector over v8 is that the metric axis CROSSES a real DYNAMICAL-category boundary
(equilibrium→aging, X:1→<1), where v8's axis crossed only a thermodynamic one (X=1 throughout).

**substrate:** a GLASS-TRANSITION ORACLE (the v8 analytic-correlator pattern on the v4 two-step
KWW form), materialized by `freeze_glass_transition.py`. Per level the connected fluctuation
correlator is the two-timescale KWW
  C(tau)   = (1 - q_EA)·exp(-tau/tau_beta) + q_EA·exp(-(tau/tau_alpha)^beta_KWW)
  chi(tau) = (1 - q_EA)·(1 - exp(-tau/tau_beta)) + X·q_EA·(1 - exp(-(tau/tau_alpha)^beta_KWW))
A fast beta-relaxation drops C to the plateau q_EA; a slow STRETCHED (beta_KWW=0.55) alpha-
relaxation sheds it. The FDR locus chi vs (1 - C) is TWO-SLOPE: slope 1 on the fast part
(quasi-equilibrium), then slope X on the slow part — X = T/T_eff is the slow-mode FDT violation.
Five temperatures cooled through Tg (level 0 warm … level 4 cold): tau_beta = 0.05 (fixed),
beta_KWW = 0.55 (fixed); tau_alpha = [1, 3, 10, 40, 150] (α-time grows ~150×, VF-like);
q_EA = [0.30, 0.40, 0.55, 0.68, 0.80] (cage/plateau deepens). X is DERIVED from the fall-out
rule (not hand-drawn): X = clamp(1 − 0.33·log10(tau_alpha/tau_alpha_Tg), 0.5, 1), with Tg at
level 1 (tau_alpha_Tg = 3). Truth from the equilibrium/aging FDT structure, never via conform.
**Why the oracle and not the library glass MC cells:** the library glass cells have null
`tau_env_analytic` below Tg (camera-scale unplaced; X read only at raw-slope, not validated —
DEFERRED.md library-refresh), so a blind X(T)-crossover read off them would not isolate conform.
The oracle encodes X(T) directly as the slow-mode FDT ratio of the aging state (X is a correlator
parameter, exactly as v4's kww_oracle prescribed X=0.5). The CSV carries NO temperature, Tg,
tau_alpha, tau_beta, q_EA, beta_KWW, X, T_eff, FDR slope, or framework token — only level, tau,
C, chi and a neutral 0…4 index. Native temperatures withheld (v7/v8: absolute distance-in-native-
units is not blind-closeable).

**collapsed_axes:** FIXED across the sweep: tau_beta, beta_KWW, the single-mode (scalar)
structure. The single dial is the **temperature** (the metric axis). Declared + reversible: re-run
the freeze at other temperatures to add/extend levels. **Boundary note (WORKFLOW §4):** within
each level's window the blind data carries the complete honest content (C and chi, the two curves
a correlation+response measurement yields). The honest parks are across the remaining collapsed
axes: the native temperature magnitudes; the WAITING-TIME (t_w) dependence of the aging (the oracle
encodes the aging state's X directly, it does not resolve t_w — a genuine collapsed axis, the v4
owed t_w vector); behaviour at lag beyond each window. There is no current/two-axis channel to
withhold: a scalar relaxation has no current sector (its absence is honest content, not curation).

**kernel_window:** each level gets its OWN settling window (~15·tau_alpha), long enough that the
slow alpha-relaxation sheds and the slow-segment slope (= X) is readable per level — so the
diverging alpha-time is honestly resolved (windows grow ~15 → 2250 across the sweep). This is the
correct camera per level, not an artifact: the longer settling at cold temperatures is the real
slowing. (No tau_obs sweep within a level; the kernel pre-gate's k_frust-invariance concern does
not bind a scalar, current-free relaxation.)

**answer_path (analytic — never via conform):**
The FDR locus chi vs (1 − C) has a fast segment of slope 1 (the (1−q_EA) part obeys FDT) and a
slow segment of slope X (the q_EA part, FDT-violated by X). Single-line fit R² → 1 when X=1
(equilibrium, single slope), dropping as the X<1 bend appears. Exact scalars (COMPUTED by the
freeze, `python freeze_glass_transition.py`):

  level | tau_alpha | q_EA | X(=T/Teff) | FDR fast slope | FDR slow slope | single-line R² | kind
  ------+-----------+------+------------+----------------+----------------+----------------+--------------------
    0   |     1     | 0.30 |   1.000    |     1.000      |     1.000      |    1.00000     | equilibrium (Cat 1)
    1   |     3     | 0.40 |   1.000    |     1.000      |     1.000      |    1.00000     | equilibrium (Cat 1)   (Tg)
    2   |    10     | 0.55 |   0.827    |     0.985      |     0.828      |    0.99784     | partially aged (crossover)
    3   |    40     | 0.68 |   0.629    |     0.974      |     0.629      |    0.98658     | partially aged (crossover)
    4   |   150     | 0.80 |   0.500    |     0.967      |     0.500      |    0.97949     | deep aging (Cat 8)
  X crossover band: [1.00, 1.00, 0.83, 0.63, 0.50] — SMOOTH 1 → 0.5 (a CROSSOVER, not a jump);
  the mid levels are PARTIALLY aged. q_EA band [0.30, 0.40, 0.55, 0.68, 0.80] (plateau deepens);
  tau_alpha band [1, 3, 10, 40, 150] (α-time grows ~150×). The slow-segment slope recovers X
  EXACTLY (0.83, 0.63, 0.50) — the load-bearing readout.

THE READ: cooling the melt through Tg DOES change the KIND of system — from a reversible
equilibrium relaxation (X=1, single-slope FDR locus, levels 0–1) to a glassy AGING state (X<1,
two-slope FDR locus, level 4). But the change is a CROSSOVER, not a jump: X drops smoothly
1→1→0.83→0.63→0.50, and the intermediate temperatures (levels 2–3) sit at intermediate X
(partially aged) — the two-step C develops a deepening plateau and a stretched slow tail, and the
FDR locus bends progressively. The dynamical-category boundary SMEARS because the glass transition
is kinetic. This is the X<1 aging counterpart to v8's X=1 equilibrium criticality crossing.

**cage_edges:**
- if_answerer_finds: "at the cold/sluggish settings it is STILL an ordinary equilibrium liquid,
  just slow — no aging, FDT intact (X=1) everywhere" → MISS (under-reads aging). The FDR locus
  BENDS at the cold levels: slow-segment slope = 0.83 / 0.63 / 0.50 < 1 at levels 2/3/4 → X<1,
  out of equilibrium. Reading the diverging slow relaxation as merely-slow-but-equilibrium misses
  the FDT violation. signature: "single-slope FDR / X=1 / equilibrium at every level / just slow,
  not aging."
- if_answerer_finds: "the WARM settings are ALREADY aging / glassy / out of equilibrium (X<1)" →
  MISS (over-reads). Levels 0–1 have a single-slope FDR locus (slope 1, R²=1) → X=1 equilibrium;
  the two-step is mild and fully equilibrated there. signature: "aging / X<1 at the warm levels."
- if_answerer_finds: "the change from liquid to stuck/aging is a SHARP SWITCH at one temperature
  — every level is EITHER full equilibrium OR full deep-aging, nothing in between" → MISS (the
  HEADLINE tooth — misses the SMEAR). The intermediate levels 2–3 sit at intermediate X (0.83,
  0.63) — partially aged; the slow-segment slope takes intermediate values, not just 1 or 0.5.
  Snapping each level to a binary equilibrium/glass label, or placing a sharp jump, misses the
  crossover. signature: "sharp transition / abrupt switch / binary equilibrium-or-glass / no
  intermediate / X jumps 1→0.5 at one level."
- if_answerer_finds: "the slow crawl is a SINGLE relaxation time (a Vertex-style single-exponential
  / single mode)" → MISS (collapses the two-step) → route_to: 1 (Vertex). C is TWO-step (a fast
  drop to the plateau q_EA, then a STRETCHED beta_KWW<1 slow tail); collapsing it to one relaxation
  misreads the structure. signature: "single relaxation time / single-exponential / one mode / no
  plateau / no stretching."
- if_answerer_finds: "the material starts to OSCILLATE / ring / develop a current as it cools" →
  MISS (false oscillation/current) → route_to: 10 (Non-Reciprocal). C is monotone (no zero-
  crossing); the observable is a single scalar (no current sector). signature: "oscillatory /
  ringing / cycling / directional current."

**sealed_answer:**

TARGET
  per level:        at the WARM levels (0–1), a reversible EQUILIBRIUM relaxation (the response-vs-
                    correlation locus is a single straight line of slope 1 — FDT holds, X=1, an
                    ordinary liquid that is merely slow). At the COLD levels, a glassy AGING state
                    (the locus BENDS — a fast part of slope 1, then a SLOW part of shallower slope X
                    < 1 — the slow modes respond less than their fluctuations would demand in
                    equilibrium: out of thermal balance). The correlation is TWO-step at every level
                    (a fast drop to a plateau, then a stretched slow tail); the plateau deepens and
                    the slow time lengthens on cooling.
  the band:         X (how far out of balance the slow modes are) crosses SMOOTHLY from 1 (warm,
                    equilibrium) to ~0.5 (cold, deep aging) ACROSS the cooling range; the slow time
                    grows ~150× and the plateau deepens. A CROSSOVER through a range, NOT a switch
                    at one temperature.
  abrupt or gradual? GRADUAL — a crossover. The middle temperatures (levels 2–3) sit PARTWAY between
                    ordinary liquid and stuck glass: partially aged, with X at intermediate values
                    (~0.83, ~0.63), not snapped to either extreme. The change of KIND (equilibrium →
                    aging) is real but it SMEARS over the cooling range rather than jumping at one
                    temperature.
  how far out of balance, per level? warm: in balance (X=1). cold: well out (X≈0.5, response about
                    half what equilibrium would give on the slow modes). middle: partway (X≈0.83,
                    ≈0.63) — the headroom read is the value of X itself, level by level.
  naive correction: the worry "it has just gotten slow" is INCOMPLETE — at the cold settings it has
                    genuinely fallen OUT of equilibrium (the response-vs-correlation locus bends; the
                    slow modes are aging, X<1), not merely slowed. AND the opposite over-reading
                    ("it's all glassy") is wrong for the warm levels (X=1 there). The honest picture
                    is a GRADUAL crossover: ordinary liquid → partially aged → deep aging as it cools.

MATCH
  The answerer places the WARM levels (0–1) as reversible equilibrium relaxation (single-slope
  response-vs-correlation locus, slope 1 → X=1) and the COLD levels as out-of-equilibrium AGING
  (the locus BENDS — a shallower slow-segment slope X<1, read past the plateau knee), reads the
  two-step structure (a plateau + a stretched slow tail, NOT a single relaxation), and — the
  load-bearing part — reads the band as a SMOOTH CROSSOVER of X from ~1 to ~0.5 across the cooling
  range, with the MIDDLE levels at INTERMEDIATE X (partially aged), NOT a sharp jump and NOT a binary
  equilibrium/glass split. It answers "abrupt or gradual?" as GRADUAL (a crossover), and corrects
  both the under-read ("just slow") and the over-read ("all glassy"). It need NOT say "X," "FDT,"
  "effective temperature," or "Edwards-Anderson": a researcher-facing "warm, it's an ordinary liquid
  in balance; cold, it's genuinely fallen out of equilibrium and aging — the response no longer keeps
  up with the fluctuations on the slow part; and it doesn't switch over abruptly at one temperature,
  it changes GRADUALLY, your middle settings are partway out of balance (about three-quarters, then
  about two-thirds of the way to balance), getting worse as you cool" is a MATCH. The equilibrium
  (warm) claim must be grounded on the single-slope locus; the aging (cold) claim on the bent locus
  / shallower slow slope; the crossover/gradual claim on the slow-slope (or its proxy) taking
  INTERMEDIATE values across the middle levels; the two-step claim on the plateau + stretched tail.
  Empty provenance on any → hollow.

MISS
  Reads the cold levels as still-equilibrium / just-slow (cage_edge 1, under-read of aging); OR the
  warm levels as already aging (cage_edge 2, over-read); OR a SHARP jump / binary equilibrium-or-
  glass with no intermediate (cage_edge 3 — the headline tooth, misses the smear); OR collapses the
  two-step slow tail to a single relaxation (cage_edge 4 → route 1); OR reads an oscillation/current
  (cage_edge 5 → route 10). A monolithic migration fit that cannot localize a MISS to one module
  (a single placement vs the band readout) also fails meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. the FDR locus reported with X > 1 at any level (X > 1 is a theorem violation).
  3. a NONZERO entropy production / sustained current reported as GROUND TRUTH (the oracle is a
     scalar relaxation — no current sector by construction) — a freeze check; an ANSWERER reading a
     false current is a MISS (cage_edge 5), not a KILL.
  4. the GROUND-TRUTH X not following the prescribed crossover [1, 1, 0.83, 0.63, 0.50] (a broken
     freeze, not a finding) — a freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
NO EXACT anchor — first sweep on this oracle, and no prior earned operating point is identical to a
level here (v4's deep-aging point was q_EA=0.7, tau_alpha=1, beta_KWW=0.6, X=0.5; level 4 here is
q_EA=0.8, tau_alpha=150, beta_KWW=0.55, X=0.5 — same X, different shape). SOFT consistency check:
level 4 is a v4-FAMILY deep-aging point (X=0.5), so its slow-segment slope should reproduce v4's
X≈0.5 two-slope reading — a qualitative cross-pass check at unseal, not a hard anchor. Cross-pass
drift detection on this oracle resumes when a second sweep is posed.

**what this vertical tests (ledger residue seed):** can conform take a researcher's supercooled melt,
measured at five temperatures cooled through where it stops flowing and described only as "it gets
sluggish and two-stage on cooling — is it just slow or genuinely out of equilibrium/aging, and does
the change happen abruptly or gradually?" — and (a) place the warm levels as reversible equilibrium
(single-slope FDR locus, X=1) and the cold levels as out-of-equilibrium aging (bent locus, slow
slope X<1), (b) read the two-step structure (plateau + stretched tail, not a single relaxation),
(c) read the band as a SMOOTH CROSSOVER of X from 1 to ~0.5 with the MIDDLE levels at INTERMEDIATE X
(partially aged) — NOT a sharp jump, NOT a binary split, (d) correct BOTH the under-read ("just
slow") and the over-read ("all glassy"). This is the DYNAMICAL-category-CROSSING companion to v8's
thermodynamic-crossing: it tests whether a real kind-crossing (equilibrium→aging, X:1→<1) SMEARS —
and the sealed answer is that it DOES (the first axis tested that smears, because the glass
transition is a kinetic crossover), with the teeth being whether conform RESOLVES the intermediate X
gradient rather than snapping to a binary label. The headline MISS is a sharp-jump / binary read
(missing the smear) or an under/over-read of which levels are aging; the win is "ordinary liquid when
warm, genuinely aging when cold, changing GRADUALLY through partially-aged middle settings — here's
how far out of balance each one is."
