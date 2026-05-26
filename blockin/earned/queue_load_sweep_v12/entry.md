# entry — queue_load_sweep_v12
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.
#
# STATUS: STAGED, NOT YET POSED. Freeze built + run; seal freeze-computed. Awaiting
# Ron's human-glance of the answer key before the blind pass (meta-SOP §2 safeguard).

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I run a single-server queue — jobs arrive, wait in line, get served one at a time. I can dial the
LOAD on it: how heavily it's used, i.e. how close the arrival rate is to what the server can handle.
I measured the queue at five increasing loads, from comfortably loaded up to running very near its
capacity (level 0 = lightest load, level 4 = heaviest, closest to the limit). As I push the load up
toward the limit, two things happen and they worry me: the queue length takes much LONGER to settle
back after a wander (the fluctuations get very slow), and the queue length swings get much LARGER
(the line size becomes wildly variable). Here's what I can't tell from the raw curves: is the queue,
near its capacity limit, still a well-behaved system that's merely SLOW and noisy — its response to a
small extra push still in proportion to its own natural fluctuations, the way a normal system in
balance behaves — or has it tipped into some kind of STUCK / pathological state where its response
no longer keeps up with its fluctuations (so that the system has, in effect, fallen out of balance)?
So for each load I want to know: is the response still matched to the fluctuations (in balance), or
has it fallen out of balance? And the practical one: as I push toward the capacity limit, am I just
getting slower-and-noisier-but-fine, or am I approaching a genuine breakdown — and how close to the
limit am I?

**minimal_structure:**
One queue (one fluctuating quantity — the queue length, a single scalar), measured at five increasing
loads. The only thing that changes from level to level is the load (how close to capacity); the queue
and the measurement are otherwise the same. Each load was watched long enough for its own slow
settling to (mostly) play out — so the observation windows differ in length across levels, the
heavily-loaded ones much longer than the lightly-loaded ones (deliberate: near the limit the queue
settles far more slowly).

**what_they_bring:**
For each of the five loads, one measurement window reduced to two standard curves of the queue length:
its autocorrelation C (how a fluctuation in the line length stays correlated with itself a lag later)
and its integrated step-response chi (how much the queue length shifts in response to a small steady
bump in the load, accumulated over the same lag). No load values, no rates, no model parameters — just
these two measured curves, the same pair at each of the five loads.

**data_path:**
`data/queue_load_sweep_v12.frozen.csv`
(columns: level, util_rel, tau, C, chi. Five operating points — one queue at five loads. level is
0…4 (lightest→heaviest, toward the capacity limit); util_rel is the relative load they set, normalized
so the lightest run = 1.0×. tau is the queue's own clock — a lag. Each level has its own settling
window, so tau ranges differ across levels, the heavily-loaded ones reaching to much longer lags.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** Cat 9 (Queueing) — closing it on its own substrate with the meta-SOP §2 / FALSIFICATION
FINDING-3 REFRAME. mm1_queue is the corpus's flagship self-named falsifier, but its named test is a
CATEGORY ERROR (FINDING 3): the README equates "α_s (the FDR effective-temperature slope, χ-vs-C
plane)" with "the heavy-traffic exponent ½ (the reflected-Brownian / Hurst time-scaling, C-vs-lag
plane)." Different objects in different planes — ½ governs how FAST C decays (relaxation time
~(1−ρ)⁻²); α_s is the FDR slope. AND the raw library cells are window-limited near ρ→1 (the slope is
unresolvable), so a blind read off them would not isolate conform. So this vertical does what v8 did
for ising_equilibrium: BUILD A CLEAN ORACLE and pose the reframe. **Sealed answer: the near-capacity
queue is REVERSIBLE CRITICAL SLOWING, X=1** — M/M/1 is a reversible birth-death process (detailed
balance) → equilibrium FDT → X=1 EXACTLY at every load (FINDING 3: "M/M/1 reversibility forces X=1").
What diverges toward the capacity wall ρ=1 is the relaxation TIME and the fluctuation SIZE, NOT the
FDT class. This is the QUEUEING counterpart to v8's thermodynamic-criticality X=1 (and the X=1
reversible counterpart to v4/v9/v10's X<1 aging).

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched isolated
placements**, PIPELINE §PHASE INTERFACE): place each of the five loads as an INDEPENDENT single-point
fit, then read the band (relaxation time + variance diverging toward capacity; FDR slope flat at 1).
The MISS must localize to one module — a single placement, or the band readout. The added vector is a
NEW CATEGORY (Cat 9) reframed: where v8 read X=1 critical slowing across a thermodynamic critical
point, this reads X=1 critical slowing toward a CAPACITY/queueing limit, and separates the ½
heavy-traffic exponent (C-decay plane) from the FDR slope (χ-vs-C plane) the README conflated.

**substrate:** an M/M/1-QUEUE ORACLE (the v8 equilibrium-criticality pattern on the queueing
substrate), materialized by `freeze_mm1_critical_slowing.py`. Per load ρ the queue-length fluctuation
correlator is a single reversible relaxational mode:
  C(τ)   = Var(ρ)·exp(−λ(ρ)·τ)            [C(0) = Var(ρ), the fluctuation size]
  chi(τ) = Var(ρ)·(1 − exp(−λ(ρ)·τ))      [equilibrium FDT, T=1 → X=1]
with the EXACT M/M/1 scalars: spectral gap (relaxation rate) λ(ρ) = μ·(1−√ρ)²; stationary variance
Var(ρ) = ρ/(1−ρ)²; mean ⟨n⟩ = ρ/(1−ρ). So the FDR locus chi vs (C(0)−C(τ)) is the IDENTITY line
(slope 1, R²=1, through the origin) at EVERY ρ — reversible, X=1 by construction (the construction
encodes the M/M/1 reversibility theorem; it is not a free parameter). μ=1; ρ=[0.60,0.80,0.90,0.95,0.98]
(toward the capacity wall). Each load watched on its own clock (~12/λ). Truth from the M/M/1 reversibility
theorem + exact queueing scalars, never via conform. **Why the oracle and not the library mm1_queue
cells:** window-limited near ρ→1 (FINDING 3 — at ρ=0.999 C decorrelates only ~3.5% over the window, the
slope unresolvable), so a blind read off the raw cells would not isolate conform. The oracle sets the
window per-ρ so the relaxation sheds and the FDR slope is blind-readable. The CSV carries NO ρ, μ, λ,
Var, the spectral gap, the FDR slope, the ½ exponent, or any framework token — only level, util_rel, tau,
C, chi and a neutral 0…4 index. Native utilization withheld (v7/v8/v9: absolute distance-in-native-units
is not blind-closeable).

**collapsed_axes:** FIXED across the sweep: the service rate μ, the single-server single-queue
structure, the single-mode (scalar queue-length) observable. The single dial is the **load ρ** (the
utilization axis, toward the ρ=1 capacity wall). Declared + reversible: re-run the freeze at other loads
to add/extend levels. **Boundary note (WORKFLOW §4):** within each load's window the blind data carries
the complete honest content (C and chi, the two curves a fluctuation+response measurement yields). The
honest parks are across the remaining collapsed axes: the native utilization values; the ABSOLUTE
heavy-traffic exponent (½) in native (1−ρ) units — it lives in the C-decay-TIME scaling vs the load, a
plane the data shows the GROWTH of but cannot pin the exponent of without native ρ; behaviour at lag
beyond each window; ρ=1 itself (the wall) approached but not sampled. There is no current/two-axis
channel to withhold: a reversible scalar queue has no current sector (its absence is honest content, not
curation).

**kernel_window:** each load gets its OWN settling window (~12/λ = ~12·(1−√ρ)⁻²), long enough that the
slow relaxation sheds and the FDR slope (=1) is readable per level — so the diverging relaxation time is
honestly resolved (windows grow ~236 → ~119000 across the sweep; this is the correct camera per load, not
an artifact: the longer settling near capacity is the real critical slowing). This per-load window is
exactly the fix FINDING 3 prescribes for the raw cells' window-limitation. (No τ_obs sweep within a level;
the kernel pre-gate's k_frust-invariance concern does not bind a reversible, current-free relaxation.)

**answer_path (analytic — never via conform):**
M/M/1 reversibility (detailed balance, a 1D birth-death chain) → equilibrium FDT → X=1, so the FDR locus
chi vs (C(0)−C(τ)) has slope 1 (R²=1, through origin) at every load. The critical slowing lives in
λ(ρ)=μ(1−√ρ)² → relaxation time 1/λ ~ (1−ρ)⁻²; the growing fluctuations in Var(ρ)=ρ/(1−ρ)². Exact scalars
(COMPUTED by the freeze, `python freeze_mm1_critical_slowing.py`):

  level | util_rel |  ρ   | λ (rate) | relax time 1/λ | ⟨n⟩  | Var   | FDR slope | R² | X
  ------+----------+------+----------+----------------+------+-------+-----------+----+---
    0   |   1.00   | 0.60 | 0.05081  |     19.7       |  1.5 |   3.7 |   1.000   | 1.0| 1
    1   |   2.67   | 0.80 | 0.01115  |     89.7       |  4.0 |  20.0 |   1.000   | 1.0| 1
    2   |   6.00   | 0.90 | 0.00263  |    379.7       |  9.0 |  90.0 |   1.000   | 1.0| 1
    3   |  12.67   | 0.95 | 0.00064  |   1559.7       | 19.0 | 380.0 |   1.000   | 1.0| 1
    4   |  32.67   | 0.98 | 0.00010  |   9899.7       | 49.0 |2450.0 |   1.000   | 1.0| 1
  relaxation-time band: [19.7, 89.7, 379.7, 1559.7, 9899.7]  → DIVERGES toward capacity (~(1−ρ)⁻²);
                    the heavy-traffic ½ exponent lives in THIS C-decay-time scaling, NOT the FDR slope.
  variance band:        [3.7, 20.0, 90.0, 380.0, 2450.0]     → DIVERGES (~(1−ρ)⁻²); fluctuations grow toward the wall.
  FDR slope band:       [1.000, 1.000, 1.000, 1.000, 1.000]  → FLAT at 1 (X=1) — reversible at every load.

THE READ: pushing the load toward capacity makes the queue SLUGGISH (the relaxation time diverges) and
WILDLY VARIABLE (the variance diverges) — but it stays IN BALANCE (the response-vs-fluctuation locus is a
single straight line of slope 1, X=1): REVERSIBLE CRITICAL SLOWING toward the ρ=1 capacity wall, NOT a
stuck/aging regime (X<1). The headroom is one-sided: distance to the capacity wall, read off the
diverging timescale/variance. The ½ heavy-traffic exponent is the relaxation-TIME scaling (C-decay plane),
a DIFFERENT plane from the FDR slope (=1) — closing the FINDING-3 category error. The X=1 reversible
counterpart to v4/v9/v10's X<1 aging; the queueing counterpart to v8's thermodynamic-criticality X=1.

**cage_edges:**
- if_answerer_finds: "near capacity the queue has fallen OUT of balance / is AGING / glassy / stuck
  (its response no longer matches its fluctuations, X<1)" → MISS (the HEADLINE tooth — reads reversible
  critical slowing as aging). The FDR locus is a single straight line of slope 1 (R²=1) at EVERY load →
  X=1, in balance. The sluggishness + huge fluctuations are reversible critical slowing, not aging.
  signature: "aging / glassy / X<1 / out of balance / stuck / response lags fluctuations near capacity."
- if_answerer_finds: "the response-vs-fluctuation (FDR) slope is ½ / the effective-temperature slope is
  the heavy-traffic exponent" → MISS (the FINDING-3 category error — conflates the ½ heavy-traffic /
  relaxation-time exponent with the FDR slope). The FDR slope is 1; the ½ (if anywhere) is the
  relaxation-TIME scaling vs load, a different plane. signature: "FDR slope ½ / α_s=0.5 /
  effective-temperature slope = heavy-traffic exponent / aging-diagonal slope ½."
- if_answerer_finds: "it's NOMINAL / no critical slowing — the loads behave the same, nothing diverges"
  → MISS (under-reads). The relaxation time (19.7→9900) AND the variance (3.7→2450) diverge sharply
  toward capacity. signature: "nominal / flat timescale / no slowing / loads all alike / far from any limit."
- if_answerer_finds: "the relaxation is a TWO-step / glassy plateau / multiple populations" → MISS
  (mis-structures it). C is a SINGLE reversible relaxation (no plateau, no second slow population).
  signature: "two-step / plateau / stretched / multiple populations / glassy structure."
- if_answerer_finds: "the queue OSCILLATES / rings / sustains a directed current as it loads up" → MISS
  (false oscillation/current) → route_to: 10 (Non-Reciprocal). C is monotone (no zero-crossing); a
  reversible queue has no current sector. signature: "oscillatory / ringing / current / cycling."

**sealed_answer:**

TARGET
  per load:         a reversible, in-balance relaxation — the response-vs-fluctuation locus is a single
                    straight line of slope 1 (X=1, the response matches the fluctuations the way an
                    equilibrium/in-balance system does). The autocorrelation is a single relaxation (no
                    plateau, no two-step). This holds at EVERY load, including the heaviest.
  the band:         as the load climbs toward capacity (level 0→4), the relaxation time DIVERGES (the
                    queue settles ever more slowly) and the fluctuation size DIVERGES (the line length
                    swings grow) — both blow up toward the limit. But the response stays matched to the
                    fluctuations (slope 1) the whole way.
  in balance or out? IN BALANCE at every load (slope 1, X=1). The imbalance the researcher worried about
                    does NOT appear — the response keeps pace with the fluctuations even at the heaviest
                    load. The queue is merely slow-and-noisy, not stuck/aging.
  how close to the limit / breakdown? The diverging relaxation time and variance are the approach to the
                    capacity wall (a one-sided headroom: the binding direction is the load→capacity limit).
                    Heavier load = closer to the wall = slower + more variable, but still reversible. It is
                    NOT a breakdown into a different (aging) regime — it is critical slowing toward the limit.
  naive correction: the worry "near capacity it must break / go pathological / fall out of balance" is
                    WRONG — the near-capacity queue is reversible critical slowing (X=1, in balance), just
                    very slow and very variable. The huge slow fluctuations are the approach to the
                    capacity limit, not a stuck/aging regime.

MATCH
  The answerer places EVERY load as a reversible, in-balance relaxation: the response-vs-fluctuation
  (FDR) locus is a single straight line of slope ≈1 (X=1 — NOT a bent locus, NOT a shallow slow slope),
  the autocorrelation a single relaxation (no two-step) — and reads the band as CRITICAL SLOWING toward
  the capacity limit: the relaxation time and the fluctuation size DIVERGE as the load climbs, while the
  response stays matched to the fluctuations (slope 1) throughout. It answers "in balance or out?" as IN
  BALANCE (X=1) at every load, and "how close to breakdown?" as approaching the capacity wall via
  reversible critical slowing — NOT a stuck/aging regime. It corrects the naive "it must break near
  capacity" worry. It need NOT say "X," "FDT," "reversible," "M/M/1," or name the ½ exponent: a
  researcher-facing "at every load the response stays in proportion to the fluctuations — it's in
  balance, just slower and noisier the harder you load it; the slow-down and the wild swings are how it
  approaches the capacity limit, not a breakdown into a stuck regime" is a MATCH. The in-balance claim
  must be grounded on the single-straight-line FDR locus (slope 1); the critical-slowing claim on the
  relaxation time / variance diverging across loads; the single-relaxation claim on the monotone C.
  Empty provenance on any → hollow.

MISS
  Reads the near-capacity queue as out-of-balance / aging / glassy (cage_edge 1 — the headline tooth);
  OR reads the FDR slope as ½ / the heavy-traffic exponent (cage_edge 2 — the FINDING-3 category error);
  OR reads it as nominal with no critical slowing (cage_edge 3, under-read); OR mis-structures it as a
  two-step/glassy relaxation (cage_edge 4); OR reads an oscillation/current (cage_edge 5 → route 10). A
  monolithic migration fit that cannot localize a MISS to one module (a single placement vs the band
  readout) also fails meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. the FDR locus reported with X > 1 at any load (X > 1 is a theorem violation).
  3. a NONZERO entropy production / sustained current reported as GROUND TRUTH (the M/M/1 queue is
     reversible — no current sector by construction) — a freeze check; an ANSWERER reading a false
     current is a MISS (cage_edge 5), not a KILL.
  4. the GROUND-TRUTH FDR slope not = 1 at any load, or the relaxation time / variance not diverging
     toward capacity (a broken freeze, not a finding) — a freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
FIRST CONTACT — no prior earned M/M/1 / queue operating point to anchor to. Conceptual kinship to v8
(same X=1 reversible critical-slowing reading; different substrate — thermodynamic criticality there,
queueing/capacity here) and to v7 (X=1 critical slowing toward a stability edge): a SOFT cross-pass
consistency check only — the heaviest load's reversible critical-slowing read should be the same KIND
as v7/v8's X=1 critical slowing, NOT the v4/v9/v10 X<1 aging. No hard numeric anchor; cross-pass drift
detection on this oracle resumes if a second sweep is posed.

**what this vertical tests (ledger residue seed):** can conform take a researcher's single-server queue,
swept across five loads toward its capacity limit and described only as "near capacity it gets very slow
and very variable — is it still in balance (response matched to fluctuations) or has it fallen out of
balance / broken, and how close am I to the limit?" — and (a) place every load as a reversible in-balance
relaxation (single-straight-line FDR locus, slope 1, X=1 — NOT aging), (b) read the band as critical
slowing toward the capacity wall (relaxation time AND variance diverging), and (c) correct the naive "it
must break near capacity" worry, landing "reversible critical slowing toward the limit, not a stuck/aging
regime." This CLOSES Cat 9 on its own substrate with the FALSIFICATION FINDING-3 reframe (the named
α_s=½ falsifier is a category error: the ½ lives in the relaxation-time/C-decay plane, the FDR slope is
1). It is the X=1 reversible counterpart to v4/v9/v10's X<1 aging, and the queueing counterpart to v8's
thermodynamic-criticality X=1. The headline MISS is an aging read (X<1) of the near-capacity sluggishness,
or the ½-as-FDR-slope category error; the win is "in balance at every load, reversible critical slowing
toward the capacity limit — slower and noisier, not broken."
