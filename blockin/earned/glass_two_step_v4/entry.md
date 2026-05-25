# entry — glass_two_step_v4
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I study a disordered material — a supercooled liquid as it approaches structural
arrest. I track one slow structural observable and measure two things about it: its
autocorrelation C (how a fluctuation now persists into a fluctuation a time later) and
its susceptibility chi (how that same observable responds to a small steady applied
field). When I watch C relax, it does NOT come down in one smooth step. It drops quickly
partway, then hangs on a long shoulder for a stretch, and only much later does it
slowly, raggedly finish relaxing the rest of the way — and that final decay is not a
clean exponential, it's drawn-out and stretched. Here is what I cannot tell from the
relaxation curve alone: is my material simply EQUILIBRATED but slow — an ordinary
thermal state that just takes a long time to forget itself — or is it OUT of equilibrium,
with the slow, stuck part of it effectively running "hotter" than the fast part that
relaxes promptly? Those two look the same in the decay curve C by itself. And
practically: is this material sitting in a stable settled state, or is that long stuck
shoulder a sign it is near an arrest it is about to cross?

**minimal_structure:**
A single relaxing structural observable in a disordered medium, with a SEPARATION of
timescales: a population of fast degrees of freedom that relax promptly, and a population
of slow degrees of freedom that are nearly frozen and relax only over a much longer (and
stretched, non-exponential) timescale. It is not one clean relaxation time — it is two
well-separated populations, fast and slow, sharing the one observable. The researcher can
push the observable with a small steady field and watch the integrated response.

**what_they_bring:**
One long observation on a single sample held at a fixed preparation/waiting condition,
reduced to the two standard curves over the material's own lag time: the normalized
autocorrelation C(tau) of the slow observable (C(0)=1), and the integrated step-response
/ susceptibility chi(tau) to a small field conjugate to that observable. That is the
complete content of the one measurement — both curves over the full lag range, from
inside the fast relaxation out past the slow stretched tail. No mode decomposition, no
model parameters, no temperatures — just the measured C and chi.

**data_path:**
`data/glass_two_step_v4.frozen.csv`
(columns: tau, C, chi. One operating point — one sample, one preparation/waiting
condition. tau is the material's own lag time. C is the normalized autocorrelation
(C(0)=1); chi is the integrated step-response to a small applied field.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** 8 (Phase / glassy-critical) — the FIRST vertical in this category, and the
first to light the two-step fluctuation-response sector. The structure is a two-timescale
relaxation with a frozen-in plateau (Edwards-Anderson q_EA) and a stretched slow tail;
its FDR signature is the two-slope Cugliandolo-Kurchan locus (slope 1 then slope X<1)
that a single-mode Vertex substrate (Cat 1) structurally cannot produce. HYPOTHESIS as
always (separability is open) — but here the claim is sharp: the apparatus must read the
SLOW relaxation as FDT-VIOLATED (the slow modes at a higher effective temperature) and
NOT collapse it to either a single relaxing mode (Cat 1, cage_edge 1) or an
equilibrated-slow material (the X=1 read, cage_edge 2 — the headline MISS this vertical
hunts).

**intent:** I1 (place ONE operating point) — same intent grain as v1, deliberately. One
material, one preparation/waiting condition, one operating point. The one added vector
vs the two Vertex dots is the **two-timescale glassy structure** (a plateau + a stretched
slow tail + a slow-mode FDT violation), nothing more. A waiting-time (t_w) sweep — which
would resolve genuine aging non-stationarity — is I2/prod and is explicitly the owed next
vector, NOT this question.

**substrate:** the KWW oracle (`mpa-central/library/primitives/kww_oracle`) — a sum of
independent OU modes realizing a prescribed two-timescale relaxation:
    C(tau)   = (1-q_EA)*exp(-tau/tau_beta) + q_EA*exp(-(tau/tau_alpha)^beta_KWW)
    chi(tau) = (1-q_EA)*(1-exp(-tau/tau_beta))  +  X*q_EA*(1 - alpha_relax(tau))
at a single operating point q_EA=0.70, tau_alpha=5.0, beta_KWW=0.60, tau_beta=0.005,
X=0.50 (~3 decades of timescale separation, so the fast relaxation fully sheds before the
slow one begins — a clean plateau + clean two-slope locus). Materialized by
`freeze_kww_glassy.py` from the substrate's own exact mode-sum correlator (the honest
"red" curve), never via conform (data-path independence). The CSV carries NO q_EA,
tau_alpha, beta_KWW, tau_beta, X, no slopes, no plateau height, no effective temperature,
no framework token — only the researcher's measured (tau, C, chi).

**collapsed_axes:** FIXED at this single point: the 5-vector (q_EA, tau_alpha, beta_KWW,
tau_beta, X), ONE waiting time t_w (a stationary realization — no t_w sweep), one sample.
Declared + reversible: re-run the freeze at other (q_EA, X, ...) or multiple t_w to add
points. WHY one point: the category jump is the move; first contact with a glassy
two-step establishes whether the apparatus reads the plateau + the slow-mode FDT
violation at all.
**Boundary note (WORKFLOW §4):** the slice is the ONLY dial. Within this one operating
point the blind data carries the COMPLETE honest content of the measurement — C(tau) AND
chi(tau) over the full lag range, exactly what a correlation + susceptibility measurement
on one sample yields. The full 5-vector is in-slice groundable from this one (C, chi) pair
(the segmented two-slope read / 5-vector fit). NOTHING in-slice is withheld to tune
difficulty: the response chi is handed over with C precisely because withholding it would
manufacture a non-isolating MISS (an answerer with C alone genuinely could not separate
equilibrated-slow from aging — that is the whole point, and is the researcher's own
dilemma, not an authoring choice). The ONLY honest park is across a COLLAPSED AXIS: whether
the X<1 reflects genuine waiting-time-dependent aging (non-stationary, t_w-dependent) or a
stationary effective-temperature — one stationary window cannot tell them apart (needs a
t_w sweep).

**kernel_window:** one waiting-time window; log-spaced lag from inside the fast
(beta) relaxation (tau ~ tau_beta/5) out past the slow (alpha) stretched tail
(tau ~ 20 tau_alpha), so both relaxations AND the intervening plateau resolve. There is no
tau_obs ambiguity here — the two intrinsic timescales are well-separated (~1000x), so the
camera pre-gate is trivially clean. There is no sustained current (this is an
equilibrium-bath FDT-violation question, not a k_frust / current-sector question), so the
two-frame self-probe sector is not engaged: the single FDR-locus frame is the readout.

**answer_path (analytic — never via conform):**
C and chi from the substrate's own mode spectrum (`kww_oracle.measurements.kww_C_chi`):
    C(tau)   = (1-q_EA) e^{-tau/tau_beta} + q_EA e^{-(tau/tau_alpha)^beta_KWW}
    chi(tau) = (1-q_EA)(1 - e^{-tau/tau_beta})  +  X q_EA (1 - e^{-(tau/tau_alpha)^beta_KWW})
The FDR locus chi vs dC=(1-C) is two straight segments: slope 1 (FDT-respecting) while
dC < 1-q_EA (the fast/beta relaxation), then slope X (FDT-violated) while dC > 1-q_EA (the
slow/alpha relaxation). The knee is the Edwards-Anderson plateau dC = 1-q_EA. Exact
scalars (COMPUTED by the freeze, `python freeze_kww_glassy.py`):

    fast-segment FDR slope (quasi-equilibrium) = 0.978   (-> 1; the FDT segment)
    knee at dC = 1 - q_EA                       = 0.300
    slow-segment FDR slope (aging)             = 0.500   (= X; the violation segment)
    plateau shoulder C(~6 tau_beta)            = 0.672   (the q_EA=0.70 amplitude)
    chi(inf) actual                            = 0.650   (an X=1 equilibrium reaches 1.000)
    effective temperature of the slow modes    = T/X = 2.00 T  (slow modes hotter than bath)
  (the sealed slopes are read off the SAME (tau,C,chi) the answerer sees — the answer-key
   matches the blind dataset.)

THE TOOTH (two ways it can be missed): (a) the autocorrelation C alone is a monotone
two-step decay — it cannot, by itself, separate "equilibrated but slow" (X=1) from
"out-of-equilibrium aging" (X<1); BOTH are slow two-step decays. The discriminator is the
RESPONSE chi read against C: the long-lag slope of chi-vs-(1-C) is X=0.5, not 1. (b) a
single-mode (Cat-1) reading collapses the fast/slow split into one relaxation time and
loses the plateau and the stretched tail. An answerer that reads C as one relaxing mode
walks into cage_edge 1; an answerer that reads the slow relaxation as FDT-respecting
(slope 1 throughout) walks into cage_edge 2 — the headline MISS. (This is the clean X<1
counterpart to the parked `mm1_queue` tension, FALSIFICATION.md FINDING 3: there the truth
was reversible critical slowing X=1 and the trap was OVER-claiming aging; here the truth is
genuine aging X<1 and the trap is reading it as equilibrium.)

**cage_edges:**
- if_answerer_finds: "a single relaxing mode / one relaxation time / a simple exponential
  decay — no plateau, no fast/slow split, no two populations" → route_to: 1 (Vertex). The
  two-step C with a frozen-in plateau and a stretched tail cannot be carried by a single
  Vertex mode; collapsing to one timescale loses q_EA and beta_KWW. signature: "single
  exponential / one timescale / no shoulder / no two populations."
- if_answerer_finds: "the material is equilibrated, just slow — fluctuation-dissipation
  holds throughout, the response tracks the correlation at slope 1 the whole way, no
  effective-temperature split" → MISS (the headline — the equilibrium / X=1 collapse). The
  long-lag chi-vs-(1-C) slope is X=0.5, NOT 1; chi(inf)=0.65, not 1.0. An equilibrated-slow
  material would be slope 1 throughout. (NOTE: proving the violation is genuine WAITING-TIME
  aging needs a t_w sweep — see not_grounded. What IS grounded from one window is that the
  slow-mode response falls below the FDT line — a real effective-temperature split, X<1 —
  not equilibrium.) signature: "equilibrated but slow; FDT intact; response = correlation at
  slope 1; no second slope; chi reaches 1."
- if_answerer_finds: "the material is unstable / diverging / about to cross or is past an
  arrest transition" → route_to: null (KILL-adjacent MISS). It is a STABLE stationary
  glassy state; the long stuck shoulder is its nominal arrested relaxation, not a transition
  being crossed. signature: "diverging / unstable / crossing the transition / runaway."

**sealed_answer:**

TARGET
  placement:        a TWO-STEP glassy relaxation. A fast (beta) relaxation drops C to a
                    frozen-in plateau q_EA ~ 0.70 (the arrested fraction of the
                    observable); then a slow, STRETCHED (beta_KWW ~ 0.6, NOT
                    single-exponential) alpha-relaxation finally relaxes it fully. The slow
                    degrees of freedom are FDT-VIOLATED at ratio X ~ 0.5 -> effective
                    temperature T_eff = T/X ~ 2T (slow modes "hotter" than the bath / the
                    fast modes). Glassy / aging s-regime.
  aging vs slow:    the discriminator is the two-SLOPE fluctuation-response locus (chi vs
                    1-C): slope ~1 (quasi-equilibrium) on the fast part up to the plateau
                    knee at dC = 1-q_EA ~ 0.3, then slope ~X < 1 (aging) on the slow part.
                    The autocorrelation C alone is a slow two-step decay either way; the
                    X<1 SECOND SLOPE (chi(inf) ~ 0.65, not 1) is what proves it is out of
                    equilibrium, not merely slow.
  nominal_verdict:  STABLE stationary glassy state — not crossing/near a transition, not
                    diverging. Its nominal behavior IS the arrested two-step relaxation.
  naive correction: it is NOT "just slow but in equilibrium." The slow degrees of freedom
                    sit at a higher effective temperature than the fast ones; FDT is
                    violated in the slow (alpha) relaxation. (Grounded in-slice from C+chi:
                    the two-step shape, the plateau q_EA, the stretching beta_KWW<1, and the
                    slope-X aging. The ONLY honest park is across a collapsed axis — whether
                    X<1 is genuine waiting-time-dependent aging or a stationary
                    effective-temperature needs a t_w sweep.)

MATCH
  The answerer reads C as TWO-STEP (a fast drop to a plateau/shoulder, then a slow stretched
  tail — NOT one relaxation), AND recognizes — from the response chi read against C — that
  the slow relaxation is FDT-VIOLATED (the response falls below the equilibrium line at long
  lag: the slow modes effectively hotter, an effective-temperature split). It places the
  material as a stable glassy / aging state, gives the plateau a height (the frozen fraction
  ~0.7) and the violation a magnitude (the long-lag slope ~0.5, or equivalently T_eff ~ 2T),
  and corrects the naive worry: it is genuinely out of equilibrium, not merely slow. It need
  NOT say "q_EA," "Edwards-Anderson," "X," "Cugliandolo-Kurchan," or "s-regime": a
  researcher-facing "your material is NOT just slow — it's out of equilibrium; about 70% of
  the structure freezes onto a plateau, then the rest relaxes slowly and raggedly, and the
  stuck slow part behaves as if roughly twice as hot as the fast part; it's a stable
  arrested glass, not about to cross anything" is a MATCH. The aging claim must be grounded
  on the chi-vs-C two-slope structure (an answerer asserting "out of equilibrium" with empty
  provenance is a hollow MATCH); the violation magnitude on the long-lag slope; the plateau
  on the C shoulder.

MISS
  Reads it as a single relaxing mode / one exponential with no plateau (cage_edge 1 — the
  Vertex collapse); OR calls it equilibrated-but-slow with FDT intact / slope 1 throughout /
  chi reaching 1 (cage_edge 2 — the headline equilibrium read); OR calls it unstable /
  crossing a transition (cage_edge 3); OR detects the two-step but cannot read the response
  against C / leaves the violation without a magnitude (a half-reading — the aging teeth
  untested). Over-claiming genuine WAITING-TIME aging (asserting t_w-dependence /
  non-stationarity) from this ONE stationary window is also a MISS — that claim is across a
  collapsed axis and is honestly NOT groundable here.

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never
     fallback-filled).
  2. the FDR violation ratio X > 1 (the slow modes reading COLDER than the bath / a
     super-FDT response) — unphysical for this construction; X in (0,1) is the
     genuine-violation interval, X=1 the equilibrium endpoint. X>1 means a broken reading.
  3. the fast-part FDR slope reading > 1 (response exceeding the FDT bound at short lag) — a
     broken estimator, not physics.
  4. a negative plateau / q_EA outside [0,1], or C(tau) leaving [-1, 1] — a broken correlator.

**what this vertical tests (ledger residue seed):** can conform take a glass researcher's
two-curve data (no framework terms — just "it relaxes in two steps, hangs on a shoulder,
then stretches out; is it equilibrated-slow or out-of-equilibrium, and is it stable?") and
(a) read the TWO-STEP structure (fast drop + plateau + stretched slow tail) and NOT collapse
it to a single relaxing mode (the Cat-1 separation — the separability hypothesis's first
Phase datapoint); (b) read the slow relaxation as FDT-VIOLATED (X<1, an effective-temperature
split) from the two-slope chi-vs-C locus, NOT as equilibrium critical slowing (the X=1 trap —
the clean counterpart to the parked mm1 FINDING-3 tension); (c) place it as a stable
glassy/aging state with a plateau height and a violation magnitude; and (d) correct "it's just
slow" while HONESTLY refusing to over-claim genuine waiting-time aging (the one park, across a
collapsed axis). A read that calls it one relaxing mode is cage_edge 1; a read that calls it
equilibrated-slow (X=1) is cage_edge 2 (the headline MISS); a read that finds the two-step,
reads the slow-mode FDT violation with a magnitude, and bounds it as a stable glassy state is
the win — the first time the apparatus reaches and EXERCISES the two-step / aging-FDR sector
that a single-mode Vertex structurally cannot.
