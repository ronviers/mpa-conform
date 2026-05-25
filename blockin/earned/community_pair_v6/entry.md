# entry — community_pair_v6
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I monitor two separate small communities, each three populations interacting around a
loop (population 1 acts on 2, 2 acts on 3, 3 acts on 1). In both communities the
abundances never sit still — they swing and wiggle continuously over my whole
observation window, and honestly the two look pretty similar when I just watch the raw
traces. I set the two communities up under different interaction arrangements, but I
can't tell from the wiggles whether that actually produced any real difference in how
they behave. For EACH community I want to know: is the swinging a *genuine, persistent
turnover* — the community really going around its loop, over and over, never settling —
or is it just relaxing toward a steady balance with the environmental noise keeping it
jiggling around that balance? And the bottom line: are these two communities
fundamentally the SAME kind of system, or are they genuinely different in some way I
can't see by eye? Is either one unstable / near some edge, or are both basically
healthy?

**minimal_structure:**
Two communities, labeled 0 and 1 in the data. Each is three populations arranged in a
closed directed loop (1→2→3→1), each population influencing the next around the cycle,
with noise entering each population. Three nodes, three directed links per community. I
arranged the two communities' interactions differently when I built them, but what that
difference *does* — whether it changes the dynamics at all, and if so how — is exactly
what I'm asking you to read out. Don't assume the two are the same; don't assume they're
different.

**what_they_bring:**
For each community, one long observation window reduced to the standard statistics in
that community's two-dimensional turnover plane (the plane in which the three abundances
trade off against each other; the overall total is held aside). For each community they
bring everything one run yields in that plane: the autocorrelation C of the turnover
signal; its integrated step-response chi; the two *directed* cross-correlations Cxy and
Cyx between the two turnover axes (how axis x now relates to axis y a lag tau later, and
vice versa); and the running tally of how far around the cycle the community has actually
swung — the mean cumulative turnover angle phiMean as a function of elapsed time, with its
spread phiVar across the run's sub-windows. No model parameters, no coupling strengths, no
noise levels — just these measured curves, the same set for each of the two communities.

**data_path:**
`data/community_pair_v6.frozen.csv`
(columns: community, tau, C, chi, Cxy, Cyx, phiMean, phiVar. Two operating points — two
communities, one observation window each. community is 0 or 1; tau is each community's own
clock: a lag for the two-point columns, an elapsed time for the turnover-angle columns.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** the SEPARABILITY probe at minimal generating distance — community 0 is
category **1 (Vertex / reversible relaxation to equilibrium)** and community 1 is category
**10 (Non-Reciprocal / sustained NESS current)**. The two communities are the SAME 3-node
loop substrate family at the SAME operating point; they differ by exactly ONE structural
bit — the **reciprocity of the coupling** (community 0 symmetric / matched, community 1
antisymmetric / cyclic). This is the first vertical that re-poses the 1↔10 separation on
ONE substrate family at minimal structural distance (every prior separation — v3's Cat-1
laser vs Cat-10 cycle, v4's Cat-8 glass — was between structurally FAR substrates). HYPOTHESIS
as always (separability is open): the apparatus must read community 0 as a reversible
relaxation with NO current and community 1 as an irreversible NESS current, and must NOT
smear them — the specific claim being tested is that the 1↔10 boundary stays SHARP even
when the two members are one reciprocity-flip apart.

**intent:** I1 (place each operating point) × 2, read as a comparison. The ONE added
vector over v3 is the **reciprocal counterpart** (community 0) set beside the cyclic loop
(community 1) — a paired contrast, not a sweep along a continuous control axis. Per
WORKFLOW §6 each community is placed as an INDEPENDENT single-point fit first; the "band"
the comparison exists to reveal is the SEPARATION (which class each lands in, and whether
they smear). The MISS must localize to one module — a single placement, or the separation
readout. (A noise sweep or a structure sweep would be I2/prod — those are v5's spent and
v5's owed vectors, NOT this question.)

**substrate:** both communities are 3-mode OU on the noisy-frustrated Banach-class
machinery (`mpa-central/library/banach_frustrated.py`), at the SAME operating point
gamma=1.0, g=0.6, D=0.1, materialized by `freeze_community_pair.py` from each structure's
own exact linear-OU propagator (truth from the structure, never via conform — data-path
independence):
- **community 1 (CYCLIC):** M = -gamma I + g A_cyc, A_cyc = [[0,-1,1],[1,0,-1],[-1,1,0]]
  (antisymmetric circulant). = v3's substrate at v3's exact operating point → community 1
  is an **ANCHOR** (see anchor-and-assert below).
- **community 0 (MATCHED):** M = -gamma I + g S, S = P^T [[0,1],[1,0]] P (symmetric,
  annihilates the (1,1,1) breathing mode like A_cyc does, plane eigenvalues ±1). Symmetric
  coupling → detailed balance → zero probability current → an equilibrium community.
The CSV carries NO gamma/g/D, no coupling matrix, no entropy rate, no eigenvalues, and no
reciprocal/non-reciprocal label — only each community's measured two-point + winding curves.
The community index (0/1) is a neutral integer; which class is which is NOT encoded.

**collapsed_axes:** FIXED for BOTH communities: gamma, g, D (no noise sweep, no structure
sweep), N=3 (no larger ring), linearity (no gain/saturation). The (1,1,1) breathing mode is
projected out; only the 2D turnover plane is exposed. The single dial of this vertical is
the **reciprocity of the coupling** (the two members). Declared + reversible: re-run the
freeze with a different coupling symmetry, or at other (g, D), to add members/points.
**Boundary note (WORKFLOW §4):** within each community's one operating point the blind data
carries the COMPLETE honest content of the run — including the winding ensemble
(phiMean, phiVar), which is what one long stationary run yields by sub-window averaging.
Nothing in-slice is withheld to tune difficulty. The only honest parks are across COLLAPSED
AXES (e.g. noise-independence of either class needs a sweep — owed since v3, partly spent
by v5 for the cyclic class).

**kernel_window:** one settling/turnover window per community, set from each community's own
slowest mode (~8 e-foldings) and, where it rotates, several rotation periods. For the cyclic
community a circulating current is REAL physics (the structure forces it); for the matched
community there is no rotation, so the window is pure relaxation. Both windows resolve the
honest content; neither "failure" is a camera artifact. (The kernel pre-gate's
k_frust-invariance check concerns artifacts under a tau_obs sweep; with one window per member
we rely on the structural truth that the cyclic current is topological and the matched
community is reversible.)

**answer_path (analytic — never via conform):**
For a 3-mode OU dz = M z dt + sqrt(2D) dW, the stationary covariance Sigma solves the
Lyapunov equation; the irreversible drift Omega = M + D Sigma^-1 is ZERO iff detailed
balance holds; the entropy production rate is <sigma> = Tr[Omega^T D^-1 Omega Sigma].
The rotation-plane two-point functions are C (normalized autocorr), Cxy, Cyx (the directed
cross-correlations). Exact scalars (COMPUTED by the freeze,
`python freeze_community_pair.py`):

  community 0 (MATCHED / reciprocal):
    eigenvalues       -0.4000, -1.0000, -1.6000   (ALL REAL — no rotation)
    <sigma>           = 0.0000     (EQUILIBRIUM — detailed balance, Omega = 0 exactly)
    omega             = 0.0000     (no rotation, no current)
    |Cxy - Cyx| peak  = 0.0000     (cross-correlation is purely SYMMETRIC)
    |Cxy + Cyx| peak  = 1.1991     (Cxy == Cyx, clearly nonzero — a real, coupled,
                                    but time-REVERSIBLE relaxation)
    winding drift     = -0.46  (rate -0.023/clock ~ 0 — NO sustained current)
    winding Var(J)    = 209.20  (drift swamped by diffusion → consistent with zero)
  community 1 (CYCLIC / non-reciprocal) — = v3:
    eigenvalues       -1.0000 +/- 1.0392 i,  and -1.0000 (real)
    <sigma>           = 2.1600     (NESS — irreversible; closed form 6 g^2/gamma)
    omega             = 1.0392     (rotation rate = sqrt(3) g)
    omega/gamma       = 1.0392     (DIMENSIONLESS, structure-set)
    |Cxy - Cyx| peak  = 0.6603     (cross-correlation is purely ANTISYMMETRIC — a current)
    |Cxy + Cyx| peak  = 0.0000     (Cxy == -Cyx exactly)
    winding drift     = +37.60 (rate +1.036/clock ~ omega) → a sustained directional current
    winding Var(J)    = 548.22
    affinity A        = 13.10 nats/cycle
    self-frame T      = 15.20  (TUR factor; floor T>=1 holds)

THE DISCRIMINATOR: the SYMMETRY of the cross-correlation matrix. Cxy == Cyx (community 0:
symmetric, time-reversible, no current → reciprocal equilibrium, Cat 1) vs Cxy == -Cyx
(community 1: antisymmetric, time-irreversible, a current → non-reciprocal NESS, Cat 10).
The autocorrelation C ALSO differs (community 0 is a monotone bi-exponential decay;
community 1 is a damped cosine), and that difference is a real secondary tell — but it is
NOT the decisive one: a reciprocal system could in principle ring (inertia), so "it
oscillates" does not prove a current. The signature that ISOLATES reciprocity, independent
of C-shape, is the cross-correlation symmetry. An answerer that calls them "the same
because both wiggle," or reads a current into community 0, or collapses community 1 to a
reciprocal ring-down, has missed the cut.

**cage_edges:**
- if_answerer_finds (community 1): "a single damped/relaxing oscillation, a ring-down, one
  mode plus a bath — no directional current; Cxy and Cyx effectively equal / asymmetry
  unread" → route_to: 1 (Vertex) — the Vertex collapse, the SAME MISS v3 hunted. The
  damped-cosine C looks like a Cat-1 ring-down; collapsing means missing Cxy == -Cyx (a
  real current). signature: "ring-down / single mode / cross-correlations symmetric or
  asymmetry unread; no sustained current."
- if_answerer_finds (community 0): "a directional current / circulation / a non-equilibrium
  loop — it keeps cycling one way" → MISS (a FALSE current — the mirror failure). Community
  0 is reversible (Cxy == Cyx, Omega = 0, winding drift ~ 0); reading a current into it
  means over-reading estimator noise in the (symmetric, nonzero) cross-correlation as
  antisymmetry, or mistaking the coupled-relaxation cross-correlation for a current.
  signature: "community 0 circulates / has a sustained current / is a NESS."
- if_answerer_finds: "the two communities are the SAME kind of system" → MISS (the
  separation missed — either both called relaxers, missing community 1's current, or both
  called cyclers, over-reading community 0). signature: "no real dynamical difference / both
  the same class."
- if_answerer_finds: "the cyclic / never-settling community (1) is unstable, growing, or
  near an instability edge" → route_to: null (KILL-adjacent MISS). All Re(eig) < 0 for BOTH
  communities; community 1 circulates forever but is stable. The "edge" is the perpetual NESS
  turnover, not instability. signature: "growing amplitude / near blow-up / marginal."

**sealed_answer:**

TARGET
  community 0 (MATCHED):  a real, COUPLED relaxation that SETTLES toward a steady balance —
                    a reversible equilibrium. The two turnover axes are correlated (the
                    cross-correlation is clearly nonzero), but the correlation is SYMMETRIC
                    (Cxy == Cyx): there is no preferred direction around the loop, no
                    sustained turnover. The wiggling is genuine noise-kicked relaxation
                    around a stable balance point, NOT a persistent cycle. Spectrally: all
                    real eigenvalues (no rotation). Entropy production zero.
  community 1 (CYCLIC):   a SUSTAINED, DIRECTIONAL circulating current (a non-equilibrium
                    steady state) — the community genuinely goes around its loop in one
                    direction and never settles. The cross-correlation is ANTISYMMETRIC
                    (Cxy == -Cyx, ~66% of the autocorr scale); spectrally a complex
                    eigenvalue pair (rotation rate ~ damping rate, omega/gamma ~ 1). This is
                    v3's community.
  same or different: GENUINELY DIFFERENT — opposite thermodynamic classes on the same loop
                    topology. Community 0 reaches detailed-balance equilibrium (time-reversal
                    symmetric, zero entropy production); community 1 sustains an irreversible
                    NESS current (time-reversal broken, finite entropy production). The
                    discriminator is the cross-correlation SYMMETRY: Cxy==Cyx (0) vs
                    Cxy==-Cyx (1). Both look like "wiggling" by eye; the symmetry is what
                    tells them apart.
  nominal_verdict:  BOTH STABLE / healthy. All modes damped in both communities. Community
                    0 settles; community 1's perpetual cycling is its nominal NESS, not a
                    near-edge warning. Neither is unstable.
  two-frame (1 only): community 1's current is strong enough to read in TWO independent ways
                    that must AGREE (§J): the fluctuation-response frame (the chi-vs-C locus
                    departs from the equilibrium line) and the self/winding frame (the
                    turnover drift phiMean + spread phiVar give affinity ~13 nats/cycle and a
                    TUR factor T ~ 15 >= 1). Agreement is the pass; disagreement would be a
                    falsifier. For community 0 the self-frame is not defined (no current) —
                    correctly so; its FDR locus sits on / near the equilibrium line.
  naive correction: the bottom-line difference between the two communities is NOT "one is
                    stable and one isn't," and NOT "one wiggles more" — both are stable and
                    both wiggle. The real difference is REVERSIBILITY: community 0 is a
                    reversible equilibrium (no net turnover), community 1 is an irreversible
                    NESS that circulates. (Grounded in-slice: each placement, the
                    cross-correlation symmetry, community 1's current magnitude / two-frame
                    agreement. The only honest parks are across collapsed axes — e.g. the
                    noise-independence of either class needs a sweep.)

MATCH
  The answerer places the two communities in DIFFERENT classes and grounds the split on the
  cross-correlation SYMMETRY: community 0 read as a reversible, coupled relaxation that
  SETTLES (Cxy == Cyx, no sustained turnover, no current) and community 1 read as a
  sustained DIRECTIONAL current / circulation (Cxy == -Cyx, nonzero turnover drift). It
  reports BOTH as stable (community 1's cycling is a nominal NESS, not an instability edge),
  gives community 1's current a MAGNITUDE (affinity ~ order-10 nats/cycle, or turnover rate
  ~ omega) grounded on the winding statistics, and confirms community 1's two independent
  readings agree and respect the TUR floor (T >= 1). It answers "same or different" as
  GENUINELY DIFFERENT and (best) names the difference as reversible-vs-irreversible /
  settles-vs-circulates. It need NOT say "reciprocal," "detailed balance," "affinity,"
  "k_frust," or quote omega/gamma: a researcher-facing "community 0 is genuinely settling to
  a balance — its two axes move together but with no preferred direction, just noise-kicked
  wobble; community 1 is genuinely turning over in one direction, a persistent directed loop
  at about one cycle per [unit], not wobble — both are stable, they are NOT the same kind of
  system" is a MATCH. The current claim (community 1) must be grounded on Cxy != Cyx + the
  drift; the no-current claim (community 0) on Cxy == Cyx + the flat winding. Asserting
  either with empty provenance is a hollow MATCH.

MISS
  Calls the two communities the SAME kind of system (separation missed); OR collapses
  community 1 to a reciprocal ring-down / single relaxing mode with no current (cage_edge 1,
  the Vertex collapse); OR reads a sustained current / circulation into community 0
  (cage_edge 2, the FALSE current — over-reading the symmetric cross-correlation or the
  estimator noise in its winding); OR calls community 1 (or either) unstable / near blow-up
  (cage_edge 4); OR separates them but on the WRONG ground — e.g. only on "1 oscillates, 0
  doesn't" without reading the cross-correlation symmetry (the C-shape tell alone does not
  isolate reciprocity; a half-reading that leaves the current's direction/magnitude or the
  reversibility unread leaves the 1↔10 teeth untested). Over-claiming noise-INDEPENDENCE of
  either class from this single operating point each is also a MISS (across a collapsed axis).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never
     fallback-filled).
  2. community 1's self-frame TUR factor T < 1 (the TUR floor T>=1 is a theorem; T<1 means
     the freeze or the reading is broken).
  3. the two FDR frames DISAGREE on community 1's verdict (§J): the chi-vs-C locus and the
     winding/affinity frame both compute there; one saying "equilibrium" and the other
     "driven" is a falsifier, not a bad fit.
  4. a NONZERO entropy production / sustained current reported for community 0 as GROUND
     TRUTH (not as an answerer's misread): community 0 is detailed-balance by construction
     (Omega = 0 exactly). A freeze that emits a real current for the symmetric coupling is a
     broken apparatus — but note this is an author-side / freeze check; an ANSWERER reading a
     false current into community 0 is a MISS (cage_edge 2), not a KILL.
  5. a current/asymmetry reported with the WRONG parity (even in tau rather than odd), or a
     winding drift whose sign contradicts the cross-correlation asymmetry — a broken
     estimator, not physics.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
community 1 is v3's substrate at v3's exact operating point (gamma=1, g=0.6, D=0.1, seed=5).
Its placement must REPRODUCE v3's earned contour: omega/gamma = 1.0392 (v3: 1.04), <sigma> =
2.16 (exact match), |Cxy-Cyx| peak = 0.66 (exact match), winding drift = 37.60 (v3: 37.98),
affinity = 13.10 nats/cycle (v3: 12.96/13.03). The winding VARIANCE / TUR factor is a noisy
2nd-moment estimator and need only land in the same ballpark (here Var=548, T=15.2; v3
Var=694, T=18.86 — differ by the stochastic stream, within the documented noisy-2nd-moment
caveat, deferred-for-auditor Entry 2). The exact quantities matching is the drift check; if
they DON'T reproduce, that is cross-pass drift to diagnose before grading.

**what this vertical tests (ledger residue seed):** can conform take two researcher
three-population loop communities — described identically, both "wiggling," with no hint of
which (if either) is cycling — and (a) PLACE each independently, reading community 0 as a
reversible coupled relaxation (Cxy == Cyx, no current) and community 1 as an irreversible
NESS current (Cxy == -Cyx), (b) SEPARATE them cleanly into Cat 1 vs Cat 10 on the
cross-correlation SYMMETRY (the time-reversal signature), NOT smear them and NOT separate
them on the weaker C-shape tell alone, (c) avoid BOTH boundary failures — neither collapsing
community 1 to a Vertex ring-down NOR reading a false current into community 0, (d) report
both as stable and correct the naive "the never-settling one must be unstable / they're the
same" worry, naming the real difference as reversible-vs-irreversible. This is the FIRST
1↔10 separation at MINIMAL generating distance (one reciprocity-flip apart on one substrate
family) — every prior separation was between structurally FAR substrates. The separability
read it lands: the 1↔10 cut is TOPOLOGICALLY sharp (reciprocity is discrete — no continuous
knob smears community 0 into community 1), which reframes WHY the prior far separations were
clean. It does NOT settle whether METRIC boundaries (criticality, coupling-strength continua,
Cat 2) blur — that needs a tunable-axis probe (still GAP). The headline MISS is "they're the
same" or either boundary failure; the win is the clean two-sided separation grounded on the
cross-correlation symmetry, with community 1 anchored to v3.
