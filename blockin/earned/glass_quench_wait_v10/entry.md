# entry — glass_quench_wait_v10
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
I work on a glass — a material that, when I cool it fast (quench it), doesn't settle into an
ordinary equilibrium liquid; it gets stuck in a sluggish, disordered, solid-ish state. Here's
the thing about freshly-quenched glass: people say it keeps slowly changing for a long time
after the quench — it "settles" — but I want to pin down what that actually means for MY
sample. So I ran this experiment: I quenched the sample once, then at five increasing times
*after* the quench (call them ages — level 0 is the youngest, just after the quench; level 4
is the oldest, after a long wait) I measured how its internal fluctuations relax: the
autocorrelation C of a fluctuating quantity, and the integrated response chi to a small steady
push, both as a function of the lag that follows. The temperature and the material are exactly
the same at all five — the *only* thing different between them is how long I waited after the
quench before measuring. Two things I need to know. **First:** does this material KEEP EVOLVING
as it ages — i.e. does the way it relaxes actually change depending on how long I'd waited (so
that an old sample behaves measurably differently from a young one) — or has it reached a fixed
sluggish state that looks the SAME no matter how long I wait? **Second:** at each age, is its
response to a push still in balance with its own fluctuations (the way an equilibrium material's
is), or is it out of balance — and if it's out of balance, does that imbalance heal as the
sample gets older, or stay put?

**minimal_structure:**
One material; one fluctuating quantity in it (a single scalar); ONE temperature. It is measured
at five successively longer waiting times after a single quench (level 0 youngest → level 4
oldest). The only thing that changes from level to level is the waiting time before the
measurement; the material, the temperature, and the measurement are otherwise identical. Each
age was watched long enough for its own slow relaxation to (mostly) play out — so the
observation windows differ in length across levels, the older ones much longer than the younger
(deliberate: the older settings relax far more slowly).

**what_they_bring:**
For each of the five ages, one measurement window reduced to two standard curves of the
fluctuating quantity: its autocorrelation C (how the fluctuation stays correlated with itself a
lag later) and its integrated step-response chi (how much the quantity shifts in response to a
small steady push, accumulated over the same lag). No times, no temperature values, no model
parameters, no material constants — just these two measured curves, the same pair at each of the
five ages.

**data_path:**
`data/glass_quench_wait_v10.frozen.csv`
(columns: level, tau, C, chi. Five operating points — one material at one temperature, measured
at five waiting times after a quench. level is 0…4 (youngest→oldest); tau is the material's own
clock — a lag. Each level has its own settling window, so tau ranges differ across levels, the
older ones reaching to much longer lags.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** Cat 8 (Phase / glassy) — the genuine NON-STATIONARY AGING sector. This is the
meta-SOP §2-escalated WAITING-TIME (t_w) vector v4 parked twice and v9 left standing. v4 (single
deep-aging point) and v9 (a temperature sweep through Tg, each level at one implicit age) both
read the slow-mode FDT violation X<1, but neither could separate the TWO kinds of out-of-
equilibrium it could be: (A) genuine **aging** — non-stationary, the slow relaxation keeps
slowing with the waiting time t_w, two-time functions depend on t_w not the lag alone (not
time-translation invariant); or (B) a **stationary effective-temperature** steady state — X<1
but time-translation invariant, identical at every age. A single-t_w measurement cannot tell
them apart (both give a bent FDR locus, slow slope X<1, at one age). The discriminator is the
t_w axis. **Sealed answer: GENUINE AGING (case A)** — the alpha-time grows with t_w (full aging,
τ_α ∝ t_w), the curves do NOT collapse, while the slow-mode FDT ratio X = T/T_eff stays flat at
0.5 (out of equilibrium, age-independent eff-T) and the fast β-modes stay equilibrated (slope 1).
The system keeps evolving; it never settles. This is the t_w companion to v9's temperature axis:
v9 swept T at fixed age (the equilibrium→aging CROSSING smears); v10 swaps the axes — fixed deep-
quench T, swept age — and asks what KIND of out-of-equilibrium the cold/aged state is.

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched isolated
placements**, PIPELINE §PHASE INTERFACE): place each of the five ages as an INDEPENDENT single-
point fit, then read the band (τ_α growing with t_w = the aging law; X flat = the age-independent
eff-T; the C(τ) curves NOT collapsing = non-stationarity). The MISS must localize to one module —
a single placement, or the band readout. The ONE added vector over v4/v9 is the WAITING-TIME axis
(v4/v9 were single-age; this resolves whether the X<1 they saw is genuine aging or a stationary
eff-T).

**substrate:** a GLASS-AGING ORACLE (the v9 glass-transition oracle held at ONE deep-quench
temperature and swept along t_w instead of T), materialized by `freeze_glass_aging.py`. Per age
the two-time connected fluctuation correlator is the two-timescale KWW with an age-dependent
alpha-time:
  C(τ; t_w)   = (1 − q_EA)·exp(−τ/τ_β) + q_EA·exp(−(τ/τ_α(t_w))^β_KWW)
  chi(τ; t_w) = (1 − q_EA)·(1 − exp(−τ/τ_β)) + X·q_EA·(1 − exp(−(τ/τ_α(t_w))^β_KWW))
A fast β-relaxation drops C to the plateau q_EA and is EQUILIBRATED at every age (FDT slope 1,
TTI). The slow STRETCHED (β_KWW=0.55) α-relaxation is the aging one: τ_α grows with the waiting
time by the simple-aging law τ_α(t_w) = τ_α_ref·(t_w/t_w_ref)^μ with μ=1 (full aging). The FDR
locus chi vs (1−C) is TWO-SLOPE: slope 1 on the fast part, then slope X on the slow part —
X = T/T_eff is the slow-mode FDT violation. Held FIXED across the t_w sweep (ONE temperature):
q_EA=0.80, β_KWW=0.55, τ_β=0.05, **X=0.50** (the slow-mode eff-T ratio is a property of the frozen
slow manifold, age-INDEPENDENT — not hand-tuned per level). Swept: t_w=[1,2,4,8,16] →
τ_α=[37.5,75,150,300,600] (grows ~16×). Truth from the equilibrium/aging FDT structure, never via
conform. **Why the oracle and not the library glass MC cells:** the library glass cells carry ONE
fixed t_w each and have null `tau_env_analytic` below Tg (camera-scale unplaced; X read only at
raw-slope, not validated — DEFERRED.md library-refresh), so a real t_w ladder is not in the library
and a blind read off it would not isolate conform. The oracle encodes the aging law τ_α(t_w) and
the age-independent X directly (X a correlator parameter, exactly as v4's kww_oracle prescribed
X=0.5). The CSV carries NO time, temperature, t_w, τ_α, τ_β, q_EA, β_KWW, X, T_eff, FDR slope, μ,
or framework token — only level, tau, C, chi and a neutral 0…4 index. Native times withheld
(v7/v8/v9: absolute distance-in-native-units is not blind-closeable).

**collapsed_axes:** FIXED across the sweep: temperature (one deep-quench T), q_EA, β_KWW, τ_β, X,
the single-mode (scalar) structure. The single dial is the **waiting time t_w** (the age axis).
Declared + reversible: re-run the freeze at other waiting times to add/extend levels. **Boundary
note (WORKFLOW §4):** within each age's window the blind data carries the complete honest content
(C and chi, the two curves a correlation+response measurement yields). The honest parks are across
the remaining collapsed axes: the native times/temperature; the TEMPERATURE-dependence of the aging
(v9 swept T, this sweeps t_w — the full T×t_w map is a 2D object, the other axis parked); the aging
EXPONENT μ's tie to fragility; behaviour at lag beyond each window. There is no current/two-axis
channel to withhold: a scalar relaxation has no current sector (its absence is honest content, not
curation).

**kernel_window:** each age gets its OWN settling window (~15·τ_α), long enough that the slow
alpha-relaxation sheds and the slow-segment slope (= X) is readable per level — so the growing
alpha-time is honestly resolved (windows grow ~560 → 9000 across the sweep). This is the correct
camera per age, not an artifact: the longer settling at older ages is the real aging slow-down.
(No τ_obs sweep within a level; the kernel pre-gate's k_frust-invariance concern does not bind a
scalar, current-free relaxation.)

**answer_path (analytic — never via conform):**
The FDR locus chi vs (1−C) has a fast segment of slope 1 (the (1−q_EA) part obeys FDT) and a slow
segment of slope X (the q_EA part, FDT-violated by X). X is the slow-mode FDT violation; here it is
AGE-INDEPENDENT. The aging signature is in the TWO-TIME structure: τ_α grows with t_w, so at a fixed
lag the older sample is MORE correlated (the curves do not collapse — not TTI). Exact scalars
(COMPUTED by the freeze, `python freeze_glass_aging.py`):

  level | t_w | tau_alpha | tau_a/t_w | q_EA |  X   | FDR fast | FDR slow
  ------+-----+-----------+-----------+------+------+----------+---------
    0   |  1  |    37.5   |   37.50   | 0.80 | 0.50 |  0.935   |  0.500
    1   |  2  |    75.0   |   37.50   | 0.80 | 0.50 |  0.953   |  0.500
    2   |  4  |   150.0   |   37.50   | 0.80 | 0.50 |  0.967   |  0.500   (= v9 level 4, the anchor)
    3   |  8  |   300.0   |   37.50   | 0.80 | 0.50 |  0.977   |  0.500
    4   | 16  |   600.0   |   37.50   | 0.80 | 0.50 |  0.984   |  0.500
  t_w band:       [1, 2, 4, 8, 16]            (the swept axis; 16× span)
  tau_alpha band: [37.5, 75, 150, 300, 600]   → GROWS ∝ t_w (full aging, μ=1); ratio τ_α/t_w CONSTANT
  X band:         [0.5, 0.5, 0.5, 0.5, 0.5]   → FLAT (slow-mode eff-T age-INDEPENDENT; X<1 = out of equilibrium)
  C at fixed lag τ=50: [0.249, 0.362, 0.464, 0.552, 0.621] → CLIMBS with t_w (NOT TTI → curves do not
                    collapse → AGING, not a stationary steady state). The load-bearing non-stationarity readout.

THE READ: this glass is GENUINELY AGING (case A), not in a stationary effective-temperature state.
The slow modes are out of equilibrium at EVERY age (two-slope FDR locus, slow slope X=0.5<1) and that
imbalance does NOT heal with age (X flat at 0.5 — not re-equilibrating); the fast modes stay in balance
(slope 1). And — the discriminator — the relaxation keeps SLOWING the longer you wait (τ_α grows ∝ t_w,
the C(τ) curves do not collapse, the older sample is more correlated at a fixed lag), so the material
keeps evolving and never settles into a fixed state. This is the t_w (non-stationarity) companion to
v9's temperature (kind-crossing) axis, and it resolves v4's parked genuine-aging-vs-stationary-eff-T
question: the X<1 is genuine waiting-time aging.

**cage_edges:**
- if_answerer_finds: "it has reached a FIXED / STATIONARY sluggish state — the relaxation looks the SAME
  at every waiting time (the curves are time-translation invariant / collapse onto one master curve), a
  steady out-of-equilibrium state, NO ongoing aging" → MISS (the HEADLINE tooth — misses the non-
  stationarity). The C(τ) curves do NOT collapse: τ_α grows ∝ t_w and at a fixed lag (τ=50) C climbs
  0.249→0.621 across the ages — the older sample relaxes measurably slower. Reading the five ages as one
  stationary state misses the aging. signature: "stationary / time-translation invariant / curves
  collapse / same at every age / fixed steady state / t_w-independent / no aging."
- if_answerer_finds: "the imbalance HEALS as the sample ages — it re-equilibrates, FDT is restored, the
  response comes back into balance (X→1) at the older ages" → MISS (over-reads recovery). The slow-
  segment FDR slope is X=0.50 at EVERY age (flat) — out of equilibrium throughout, not healing.
  signature: "re-equilibrates / FDT restored / X→1 with age / heals / comes back into balance."
- if_answerer_finds: "at every age it is an ORDINARY equilibrium liquid that is merely slow — response in
  balance with fluctuations (X=1), no FDT violation" → MISS (under-reads aging). The FDR locus BENDS at
  every age: slow-segment slope 0.50 < 1 → X<1, out of equilibrium. signature: "equilibrium / X=1 / FDT
  intact / in balance at every age / just slow."
- if_answerer_finds: "the slow relaxation is a SINGLE relaxation time (a Vertex-style single-exponential /
  single mode)" → MISS (collapses the two-step) → route_to: 1 (Vertex). C is TWO-step (a fast drop to the
  plateau q_EA=0.80, then a STRETCHED β_KWW<1 slow tail). signature: "single relaxation time / single-
  exponential / one mode / no plateau / no stretching."
- if_answerer_finds: "the material OSCILLATES / rings / develops a current as it ages" → MISS (false
  oscillation/current) → route_to: 10 (Non-Reciprocal). C is monotone (no zero-crossing); the observable
  is a single scalar (no current sector). signature: "oscillatory / ringing / cycling / directional current."
- if_answerer_finds: "the relaxation SPEEDS UP / the timescale SHRINKS as the sample ages" → MISS (wrong
  direction). τ_α GROWS ∝ t_w — the older sample relaxes SLOWER. signature: "speeds up with age / faster
  when older / timescale shrinks / relaxation accelerates."

**sealed_answer:**

TARGET
  per age (each level):  a glassy, out-of-equilibrium relaxation. The correlation is TWO-step (a fast drop
                    to a plateau ~0.80, then a stretched slow tail). The response-vs-correlation locus BENDS
                    — a fast part of slope 1 (the fast modes are in balance, FDT holds), then a SLOW part of
                    shallower slope X≈0.50 < 1 (the slow modes respond about half what their fluctuations
                    would demand in equilibrium — out of balance). This holds at EVERY age.
  the band (does it keep evolving?):  YES — it AGES. The slow relaxation time GROWS the longer you wait
                    (the older sample relaxes measurably slower); at a fixed lag the older sample is more
                    correlated; the curves do NOT collapse onto one shape. The material keeps evolving with
                    age; it does NOT settle into a fixed/stationary state.
  the band (does the imbalance heal?):  NO. The slow-mode imbalance is the SAME at every age (X≈0.50
                    throughout) — it neither heals (X does not climb back toward 1) nor worsens. The out-of-
                    balance is a stable property of the aging state; what changes with age is the timescale,
                    not the degree of imbalance.
  keeps evolving or fixed state?  KEEPS EVOLVING (genuine aging). The defining signature is that the
                    relaxation is NOT the same at every age — the slow timescale grows with the waiting time,
                    so an old sample behaves measurably differently from a young one. A fixed/stationary state
                    would look identical at every age; this does not.
  naive correction: the worry splits two ways and both naive answers are wrong. (1) "It's settled into a
                    fixed sluggish state" is wrong — it keeps aging (the relaxation slows with every extra
                    wait; the curves do not collapse). (2) "The imbalance must heal as it settles" is also
                    wrong — the response stays out of balance with the fluctuations on the slow modes (X≈0.5)
                    at every age. The honest picture: it is genuinely AGING — perpetually slowing, perpetually
                    out of balance on the slow modes by a fixed amount, never reaching equilibrium or a steady
                    state.

MATCH
  The answerer places EVERY age as a glassy out-of-equilibrium relaxation: a two-step correlation (plateau +
  stretched tail, NOT a single relaxation) and a BENT response-vs-correlation locus whose slow-segment slope
  is X≈0.50 < 1 (read past the plateau knee) — and reads that slow slope as ~CONSTANT across the ages (the
  imbalance does NOT heal). And — the load-bearing part — it reads the band as GENUINE AGING: the slow
  relaxation timescale GROWS with the waiting time (the C(τ) curves do NOT collapse; at a fixed lag the older
  sample is more correlated), so the material keeps evolving and does NOT reach a stationary/fixed state. It
  answers "keeps evolving or fixed?" as KEEPS EVOLVING (aging), and corrects both the "fixed steady state"
  read (cage_edge 1) and the "it heals / re-equilibrates" read (cage_edge 2). It need NOT say "X," "FDT,"
  "effective temperature," "time-translation invariance," or "Edwards-Anderson": a researcher-facing "at
  every age the slow modes are out of balance by about half and that doesn't heal; and it keeps aging — the
  relaxation slows the longer you wait, an old sample is measurably more sluggish than a young one, it never
  settles" is a MATCH. The out-of-equilibrium (X<1) claim must be grounded on the bent locus / shallow slow
  slope; the no-healing claim on the slow slope staying ≈constant across ages; the AGING (keeps-evolving)
  claim on the slow timescale growing with age / the curves not collapsing / fixed-lag C climbing; the two-
  step claim on the plateau + stretched tail. Empty provenance on any → hollow.

MISS
  Reads the ages as a stationary / TTI fixed state with no ongoing aging (cage_edge 1 — the headline tooth,
  misses non-stationarity); OR reads the imbalance as healing / re-equilibrating with age (cage_edge 2,
  over-read); OR reads every age as ordinary equilibrium / just-slow (cage_edge 3, under-read of the FDT
  violation); OR collapses the two-step slow tail to a single relaxation (cage_edge 4 → route 1); OR reads an
  oscillation/current (cage_edge 5 → route 10); OR reads the relaxation speeding up with age (cage_edge 6,
  wrong direction). A monolithic migration fit that cannot localize a MISS to one module (a single placement
  vs the band readout) also fails meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. the FDR locus reported with X > 1 at any age (X > 1 is a theorem violation).
  3. a NONZERO entropy production / sustained current reported as GROUND TRUTH (the oracle is a scalar
     relaxation — no current sector by construction) — a freeze check; an ANSWERER reading a false current is
     a MISS (cage_edge 5), not a KILL.
  4. the GROUND-TRUTH slow-mode X not flat at 0.50, or τ_α not growing ∝ t_w (a broken freeze, not a
     finding) — a freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
HARD anchor — level 2 (t_w=4) is built with τ_α=150, q_EA=0.80, β_KWW=0.55, X=0.50, IDENTICAL to
melt_cooling_sweep_v9 level 4 (the deepest-quench point). Its single-time C(τ), chi(τ) curves are the SAME
data as v9 L4. At unseal, assert that the answerer's level-2 placement reproduces v9 L4's reading: a two-step
correlation with plateau ≈0.80 and a bent FDR locus with slow-segment slope ≈0.50 (X≈0.5). Cross-pass drift
detection — the answerer is NOT told which level is the anchor or its earned value (that would leak the
placement). If level 2's read diverges from v9 L4, surface it as cross-pass drift, not a fresh finding.

**what this vertical tests (ledger residue seed):** can conform take a researcher's freshly-quenched glass,
measured at five increasing ages after the quench and described only as "it's sluggish and two-stage — does
it keep evolving as it ages or has it settled into a fixed state, and is its response in balance or out of
balance (and does that heal)?" — and (a) place every age as a glassy out-of-equilibrium relaxation (bent FDR
locus, slow slope X≈0.5<1, two-step structure), (b) read the slow-mode imbalance as ~CONSTANT across ages
(does NOT heal), and (c) — load-bearing — read the band as GENUINE AGING (the slow timescale grows with the
waiting time; the curves do not collapse; the material keeps evolving and never reaches a stationary state),
correcting BOTH the "fixed steady state" read and the "it re-equilibrates" read. This is the WAITING-TIME
(t_w) companion to v9's temperature axis and the meta-SOP §2-escalated resolution of v4's parked genuine-
aging-vs-stationary-eff-T question. The headline MISS is a stationary/TTI read (missing the non-stationarity)
or a re-equilibration read; the win is "out of balance on the slow modes by a fixed amount at every age, and
genuinely aging — the relaxation keeps slowing the longer you wait, it never settles."
