# entry — three_species_cycle_v3
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I study a small community of three populations locked in a cyclic standoff — the first
outcompetes the second, the second outcompetes the third, and the third outcompetes the
first, round and round (the textbook rock-paper-scissors arrangement). When I watch them
over a long run they never settle: the abundances keep cycling, one cresting while the
next is rising and the last is crashing, over and over. Here's what I can't tell from
just staring at the wiggles: is this a *real, persistent turnover* — the community
genuinely going around the loop in one direction, never reaching a steady balance — or
is it just damped oscillation around a stable coexistence point that the environmental
noise keeps kicking back into motion? Those look the same in a single abundance trace.
And practically: if I could calm the environment down (less external buffeting), would
the cycling die away and settle, or would the community keep turning anyway? Is this
community stable, or is the perpetual cycling a sign it's near some edge?

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each one suppresses
the next around the cycle (1→2→3→1). Three nodes, three directed links, and the links do
NOT come in matched forward/back pairs: the influence of population 1 on 2 is not the
mirror of 2 on 1. It does not reduce to one population plus an environment — the loop is
the thing. Noise enters each population.

**what_they_bring:**
One long observation window of the three abundances, reduced to the standard statistics in
the community's two-dimensional turnover plane (the plane in which the abundances trade
off; the overall total is held aside). For that plane they bring everything that one run
yields: the autocorrelation C of the turnover signal; its integrated step response chi;
the two *directed* cross-correlations Cxy and Cyx between the two turnover axes (how axis x
now relates to axis y a lag tau later, and vice versa); and the running tally of how far
around the cycle the community has actually swung — the mean cumulative turnover angle
phiMean as a function of elapsed time, together with its spread phiVar across the run's
sub-windows. No model parameters, no coupling strengths, no noise level — just these
measured curves from the one run.

**data_path:**
`data/three_species_cycle_v3.frozen.csv`
(columns: tau, C, chi, Cxy, Cyx, phiMean, phiVar. One operating point — a single
community, a single observation window. tau is the community's own clock: a lag for the
two-point columns, an elapsed time for the turnover-angle columns.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** 10 (Non-Reciprocal / current-bearing) — the FIRST vertical in this
category, and the first to reach the current-gate / self-frame sector at all. The
structure is a 3-node closed loop with antisymmetric (non-reciprocal) coupling; it
carries a *sustained probability current* (a circulating NESS), which a single-mode
Vertex substrate structurally cannot. HYPOTHESIS as always (the separability question is
open) — but here the claim is sharp: the apparatus must read this as current-bearing and
NOT collapse it to a Vertex ring-down (see the first cage_edge — that collapse is the
specific MISS this vertical hunts).

**intent:** I1 (place ONE operating point) — same intent grain as v1, deliberately. This
is a *category jump* off the two Vertex dots, not a sweep; the one added vector is the
**non-reciprocal cyclic structure itself** (3 nodes, a closed loop, a current), nothing
more. One substrate, one window, one operating point. (A noise sweep or a structure
sweep would be I2/prod — those are explicitly the owed next vectors, NOT this question.)

**substrate:** the noisy frustrated Banach-class reference
(`mpa-central/library/banach_frustrated.py`) — three modes in a cyclic non-reciprocal
(rock-paper-scissors) OU: dz = M z dt + sqrt(2D) dW, M = -gamma I + g A_cyc, with
A_cyc = [[0,-1,1],[1,0,-1],[-1,1,0]] (antisymmetric circulant), at a single operating
point gamma=1.0, g=0.6, D=0.1. Materialized by `freeze_three_species_cycle.py` from the
substrate's own exact linear-OU propagator (the truth is computed from the structure,
never via conform — data-path independence). The CSV carries NO g/gamma/D, no entropy
rate, no affinity, no eigenvalues — only the researcher's measured two-point curves
(tau, C, chi, Cxy, Cyx).

**collapsed_axes:** FIXED at this single point: gamma, g, D (no noise sweep, no structure
sweep), N=3 (no larger ring), linearity (no gain/saturation — the deterministic-Banach
nonlinear extension is deferred). The overall (1,1,1) breathing mode is projected out;
only the 2D turnover plane is exposed. Declared + reversible: re-run the freeze at other
(g, D) to add points. WHY one point: the category jump is the move; the first contact
with a current establishes whether the apparatus *detects and places* circulation at all.
**Boundary note (WORKFLOW §4):** the slice is the ONLY dial. Within this one operating
point the blind data carries the COMPLETE honest content of the run — including the
winding ensemble (phiMean, phiVar), which is what one long stationary run yields by
sub-window averaging. It is NOT withheld to keep first-contact "minimal": withholding an
in-slice observable would manufacture a non-isolating MISS. So the affinity and the TUR
factor ARE in-slice (the winding ensemble carries them); the only honest park is across a
COLLAPSED AXIS — the noise level D (proving noise-INDEPENDENCE needs a second operating
point). *(This entry was re-bounded 2026-05-25 when its first draft withheld the winding
ensemble — see WORKFLOW §4's worked instance.)*

**kernel_window:** one settling/turnover window. The slowest mode decays at rate gamma;
the window spans ~8 e-foldings AND several rotation periods 2*pi/omega so the directed
turnover resolves. A circulating current here is REAL physics (the structure forces it),
NOT a detection artifact — so unlike a Vertex substrate, finding a current is the correct
reading, and finding NONE is the MISS. (The kernel pre-gate's k_frust-invariance check is
about artifacts under a tau_obs sweep; with one window we instead rely on the structural
truth that the current is topological.)

**answer_path (analytic — never via conform):**
M = -gamma I + g A_cyc. Eigenvalues: -gamma (real) and -gamma +/- i*sqrt(3)*g (a COMPLEX
PAIR). Stationary covariance Sigma = (D/gamma) I (isotropic). The rotation-plane two-point
function is an exactly-solvable damped rotation:
    C(tau)  = e^{-gamma*tau} cos(sqrt(3) g tau)       (autocorr — a damped cosine)
    Cxy(tau)= -e^{-gamma*tau} sin(sqrt(3) g tau)
    Cyx(tau)= +e^{-gamma*tau} sin(sqrt(3) g tau)      (so Cxy == -Cyx, purely antisymmetric)
The antisymmetric cross-correlation is the time-reversal-breaking signature of the
current. Exact scalars (COMPUTED by the freeze, `python freeze_three_species_cycle.py`):

    eigenvalues       -1.0000 +/- 1.0392 i,  and -1.0000 (real)
    <sigma>           = 2.1600   (entropy production; closed form 6 g^2/gamma)
    omega             = 1.0392   (rotation rate = sqrt(3) g)
    omega/gamma       = 1.0392   (DIMENSIONLESS, structure-set)
    |Cxy-Cyx| peak    = 0.66     (66% of the autocorr scale C(0)=1 — a blatant current)
  in-slice (from the EMITTED phiMean/phiVar — what the blind data actually carries):
    winding drift     = 1.047/clock (~ omega) => phiMean(t_max) = 37.98
    winding Var(J)    = 694.20
    affinity A        = 12.96 nats/cycle  (cross-check bf.measure 13.03)
    self-frame T      = 18.86  (TUR factor; floor T>=1 holds; cross-check 16.35)
  (the sealed affinity/T are computed from the SAME winding arrays the answerer sees, not
   a different window — the answer-key matches the blind dataset.)

THE TOOTH: the class-B laser (v1/v2, Cat 1) has the SAME spectral shape — a complex
eigenvalue pair, a damped-cosine autocorr C(tau) = e^{-g t}cos(w t) ring-down. But the
laser RELAXES to equilibrium: its current is ZERO, time-reversal symmetry is intact,
Cxy == Cyx (symmetric, asym = 0). So C(tau) ALONE cannot separate Cat 1 from Cat 10 —
both ring. The discriminator is the cross-correlation antisymmetry Cxy != Cyx, which is
nonzero ONLY when a current circulates. An answerer that reads the damped-cosine C and
calls it a ring-down / single relaxing mode has walked into cage_edge 1.

**cage_edges:**
- if_answerer_finds: "a single damped/relaxing oscillation, a ring-down, one mode plus a
  bath / environment — no directional current; reads Cxy and Cyx as effectively equal /
  ignores the asymmetry" → route_to: 1 (Vertex) — the SPECIFIC MISS this vertical hunts.
  The damped-cosine C looks exactly like a Cat-1 ring-down; collapsing to Vertex means
  missing that Cxy == -Cyx (a real circulating current), which Vertex structurally cannot
  carry. signature: "damped oscillation / ring-down / single mode; cross-correlations
  symmetric or asymmetry unread; no sustained current."
- if_answerer_finds: "the cycling is noise-driven and calming the environment (lowering
  the noise) would settle it to a steady coexistence" → MISS (the naive worry
  UNCORRECTED). The directed asymmetry is structural, not a noise artifact; the rotation
  rate omega/gamma is set by the wiring (g/gamma), not the noise. (NOTE: proving
  *noise-independence* needs a noise sweep — see not_grounded. What IS grounded from one
  point is that the asymmetry is a robust, oscillating-in-tau current signature, not a
  symmetric reciprocal correlation. A MATCH must identify the *current*; it need not
  prove topological forcing.) signature: "current is a noise/drive artifact; remove the
  forcing and it vanishes."
- if_answerer_finds: "the community is unstable / growing / blowing up / near an
  instability edge" → route_to: null (KILL-adjacent MISS). All Re(eig) = -gamma < 0: the
  community circulates forever but is stable. The "edge" the researcher senses is the
  perpetual NESS turnover, NOT an instability. signature: "growing amplitude / near
  blow-up / marginal-toward-instability."

**sealed_answer:**

TARGET
  placement:        a SUSTAINED, DIRECTIONAL circulating current (a non-equilibrium
                    steady state) in the three-population loop. The community genuinely
                    goes around the cycle in one direction and never settles to a steady
                    balance. Spectrally: a complex eigenvalue pair (a rotation) on top of
                    overall damping — rotation rate comparable to the damping rate
                    (omega/gamma ~ 1).
  current vs ring:  the discriminator is the cross-correlation ASYMMETRY Cxy != Cyx
                    (here Cxy == -Cyx, ~66% of the autocorr scale). The autocorrelation C
                    alone is a damped cosine that would look identical to a reciprocal
                    ring-down; the asymmetry is what proves the turnover is a real
                    directional current, not damped oscillation around a fixed point.
  nominal_verdict:  STABLE. All modes are damped (Re(eig) < 0); the circulation is a
                    persistent NESS, not a growing instability. The perpetual cycling is
                    the community's nominal steady behavior, NOT a near-edge warning.
  two-frame agree:  the current is strong enough to read in TWO independent ways that must
                    agree (§J): the standard fluctuation-response frame (the chi-vs-C locus
                    departs from the equilibrium line by an amount set by the entropy
                    production) and the self/winding frame (the turnover drift phiMean and
                    its spread phiVar give the affinity ~13 nats/cycle and a TUR factor
                    T ~ 19 >= 1). Both frames compute here and agree on "driven,
                    current-bearing, bounded by the TUR floor" — agreement is the pass; a
                    disagreement would be a falsifier (see KILL).
  naive correction: the cycling is NOT reciprocal noise-driven oscillation that calming
                    the environment would settle. It is a broken-time-reversal current
                    intrinsic to the cyclic, non-reciprocal wiring. (Grounded in-slice: the
                    current exists, its magnitude/affinity/TUR, and the two-frame agreement.
                    The ONLY honest park is across a collapsed axis — a quantitative proof
                    of noise-INDEPENDENCE needs a second operating point / noise sweep.)

MATCH
  The answerer reads C as a damped oscillation BUT recognizes — from Cxy != Cyx AND the
  nonzero turnover drift phiMean — that this is a sustained DIRECTIONAL current /
  circulation (a non-equilibrium steady state), not a reciprocal ring-down or a single
  relaxing mode. It reports the community as STABLE (the cycling is its nominal NESS, not
  an instability edge), gives the current a MAGNITUDE (the affinity ~ order-10 nats/cycle,
  or equivalently the turnover rate ~ omega), and confirms the two independent readings
  agree and respect the TUR floor (T >= 1). It corrects the naive worry: the turnover is a
  real directional circulation tied to the cyclic wiring, not noise sloshing a damped
  oscillator. It need NOT say "affinity," "winding," "k_frust," or quote omega/gamma: a
  researcher-facing "your community is genuinely turning over in one direction at about
  one cycle per [unit] — a persistent directed loop, not damped wobble around a balance
  point — it's stable, and the turnover rate is the wiring, not the weather" is a MATCH.
  The current claim must be grounded on Cxy != Cyx and the drift (an answerer asserting
  "current" with empty provenance is a hollow MATCH); the magnitude must be grounded on
  the winding statistics.

MISS
  Reads it as a single damped oscillation / ring-down / one-mode-plus-bath with no
  directional current (cage_edge 1 — the headline MISS: the Vertex collapse); OR calls the
  current a noise/drive artifact that would settle if the environment calmed (cage_edge 2,
  naive worry uncorrected); OR calls the community unstable / near blow-up (cage_edge 3);
  OR detects the current but cannot give it a magnitude / leaves the winding data unread
  (a half-reading — the Cat-10 teeth untested). Over-claiming noise-INDEPENDENCE from this
  ONE point (asserting the rate is noise-set without a sweep) is also a MISS — that claim
  is across a collapsed axis and is honestly NOT groundable here.

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never
     fallback-filled).
  2. the self-frame TUR factor T < 1 (the TUR floor T>=1 is a theorem; T<1 means the
     freeze or the reading is broken). This IS now grounded from the blind data — phiVar /
     phiMean^2 with the entropy production from the locus — so it is a live KILL check.
  3. the two FDR frames DISAGREE on the regime verdict (§J): the chi-vs-C locus and the
     winding/affinity frame both compute here; if one says "equilibrium / no current" and
     the other says "driven," that contradiction is a falsifier, not a bad fit.
  4. a current/asymmetry reported with the WRONG parity (even in tau rather than odd, or a
     drift with the wrong sign relative to the asymmetry) — a broken estimator, not physics.

**what this vertical tests (ledger residue seed):** can conform take a researcher's
three-species cyclic-community data (no framework terms — just "they keep cycling, is it
real turnover or noise-kicked wobble, and is it stable?") and (a) DETECT a sustained
directional current from the cross-correlation asymmetry Cxy != Cyx AND the nonzero
turnover drift, (b) NOT collapse the damped-cosine autocorr to a Vertex ring-down (the
Cat-1/Cat-10 separation — the separability hypothesis's first non-Vertex datapoint),
(c) place it as a stable NESS circulation, give it a MAGNITUDE (affinity / turnover rate)
from the winding statistics, and confirm the TWO frames (chi-vs-C locus and the
winding/affinity self-frame) AGREE and respect the TUR floor — the load-bearing Cat-10
teeth, exercised in-slice — and (d) correct "it's just noise-driven oscillation" while
HONESTLY refusing to over-claim noise-INDEPENDENCE (the one park, across a collapsed axis).
A read that calls it a ring-down / single mode is the MISS (cage_edge 1); a read that finds
the directional current, bounds it as a stable structural NESS with a magnitude, and
checks the two-frame agreement is the win — the first time the apparatus reaches and
EXERCISES the current-bearing / two-frame sector that Vertex structurally cannot.
