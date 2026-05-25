# entry — coupling_ramp_v7
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I have a community of three populations whose interactions are *mutual* — each pair pushes
back on the other, a matched give-and-take, not a one-way chase around a loop. I can dial up
the overall strength of those interactions with a single knob, and I've recorded the
community at five settings, from gentle up to quite strong (levels 0 through 4). As I crank
the knob up, the abundances swing in bigger excursions and take noticeably longer to settle
back down. Here's what's nagging me: if I keep turning it up, is this community going to
start genuinely *oscillating* or *cycling* — going around the loop on its own — or even tip
over into something runaway/unstable? For each setting I want to know: is it still just
settling back to balance (however slowly), or has it started to genuinely cycle? Am I
approaching some edge — and if so, how close am I, and how would I know from the data? And
the big one: does cranking the interaction strength change *what kind of system this is*, or
is it the same kind of thing all the way up, just more so?

**minimal_structure:**
One community, three populations arranged in a loop, observed at five increasing
interaction-strength settings (level 0 = gentlest … level 4 = strongest). The interactions
are mutual / matched (the influence of one population on another is met by a comparable
influence back), not a one-directional cycle. Noise enters each population. The only thing
that changes from level to level is the overall interaction strength; the wiring and the
noise are otherwise the same. Each level was watched long enough for its own settling to
play out (so the observation windows differ in length across levels — that is deliberate, a
stronger setting needs longer watching).

**what_they_bring:**
For each level, one observation window reduced to the standard statistics in the community's
two-dimensional turnover plane (the plane in which the three abundances trade off; the
overall total is held aside). Per level: the autocorrelation C of the turnover signal; its
integrated step-response chi; the two *directed* cross-correlations Cxy and Cyx between the
two turnover axes; and the running tally of net cumulative turnover angle — phiMean vs
elapsed time, with its spread phiVar across the run's sub-windows. No model parameters, no
interaction-strength magnitudes, no noise level — just these measured curves, the same set
at each of the five settings.

**data_path:**
`data/coupling_ramp_v7.frozen.csv`
(columns: level, tau, C, chi, Cxy, Cyx, phiMean, phiVar. Five operating points — one
community at five interaction-strength settings. level is 0…4 (gentlest→strongest); tau is
the community's own clock: a lag for the two-point columns, an elapsed time for the
turnover-angle columns. Each level has its own settling window, so tau ranges differ.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** the METRIC-boundary-blur probe. The substrate stays **category 1 (Vertex /
reversible relaxation)** at every level; the vertical asks whether Cat 1 SMEARS toward a
neighbor as a CONTINUOUS (metric) control axis — the interaction strength g_s — is dialed
toward the substrate's stability threshold. This is the follow-up v6 set up: v6 showed the
1↔10 cut is TOPOLOGICALLY sharp (reciprocity is discrete, cannot smear); the open question
was whether a METRIC boundary blurs. Here the answer is sealed: it does NOT smear (no
oscillation onset, no current onset, X=1 throughout) — the operating point instead approaches
a critical/instability EDGE via critical slowing, and the metric axis grounds the
two-sided headroom-to-instability (the spectral gap), which a single operating point cannot.

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched
isolated placements**, PIPELINE §PHASE INTERFACE): place each of the five levels as an
INDEPENDENT single-point fit, then read the band (the migration of the relaxation timescale
and the spectral-gap headroom across the strength axis). The MISS must localize to one module
— a single placement, or the band readout. The ONE added vector over v6 is the
**coupling-strength axis** (a metric tuning toward the stability edge). This is also the
sanctioned ADVANCE off v6: v6 parked "distance-to-instability / two-sided headroom needs a
sweep" — this is that sweep, and it closes v1's identically-owed two-sided-headroom vector
for the reversible Cat-1 case.

**substrate:** the v6 MATCHED community, M = -gamma I + g_s S, S = P^T [[0,1],[1,0]] P
(symmetric — reciprocal — coupling, annihilates the (1,1,1) breathing mode, plane eigenvalues
±1), gamma=1.0, D=0.1, materialized by `freeze_coupling_ramp.py` from the exact linear-OU
propagator (truth from the structure, never via conform). Sweep g_s = [0.3, 0.6, 0.8, 0.9,
0.95] (levels 0…4). Plane eigenvalues are -gamma ± g_s — ALWAYS REAL (symmetric coupling):
  - slow mode -gamma + g_s → 0 as g_s → gamma: tau_slow = 1/(gamma - g_s) DIVERGES
    (1.43 → 2.5 → 5 → 10 → 20), and the slow-mode stationary variance D/(gamma - g_s)
    diverges too (susceptibility divergence). At g_s = gamma the stationary state ceases to
    exist (marginal); above it the slow mode is unstable.
  - the spectrum is real at every g_s → NO oscillation ever; the coupling is symmetric at
    every g_s → detailed balance, <sigma> = 0, Cxy = Cyx, zero current at every g_s.
The CSV carries NO g_s/gamma/D, no spectral gap, no tau_slow, no eigenvalues, no
"critical"/"reversible"/"X" label — only each level's measured curves and a neutral 0…4 index.

**collapsed_axes:** FIXED across the sweep: gamma, D, the symmetric coupling STRUCTURE S
(only its magnitude g_s varies), N=3, linearity, the (1,1,1) mode projected out. The single
dial is the **coupling strength g_s** (the metric axis). Declared + reversible: re-run the
freeze at other g_s to add/extend levels. **Boundary note (WORKFLOW §4):** within each
level's window the blind data carries the complete honest content (incl. the winding
ensemble, which for this reversible community shows drift ≈ 0 — the honest "no current"
content, not a withheld observable). The honest parks are across the remaining collapsed
axes (noise level D; the structure S itself; behavior ABOVE g_s = gamma, which is a different
operating regime not sampled).

**kernel_window:** each level gets its OWN settling window (~8 e-foldings of that level's slow
mode), so the diverging relaxation time is honestly resolved per level (windows grow
11 → 160). This is the correct camera per level, not an artifact: the longer settling at high
g_s is real critical slowing, and the window is matched to it. (No tau_obs sweep within a
level; the kernel pre-gate's k_frust-invariance concern does not bind a reversible,
current-free relaxation.)

**answer_path (analytic — never via conform):**
For M = -gamma I + g_s S with S symmetric (plane eigenvalues ±1): plane eigenvalues
-gamma ± g_s (real); stationary covariance from the Lyapunov equation; Omega = M + D Sigma^-1
= 0 exactly (detailed balance) → <sigma> = 0. The FDR locus chi vs (C(0) - C(tau)) is AFFINE
(single slope, FDT holds, X = 1) at every level — the equilibrium signature. Exact scalars
(COMPUTED by the freeze, `python freeze_coupling_ramp.py`):

  level | g_s  | plane eig (real)  | <sigma> | omega | gap=gamma-g_s | tau_slow | FDR R^2
  ------+------+-------------------+---------+-------+---------------+----------+--------
    0   | 0.30 | -0.700, -1.300    |  0.0000 |  0    |     0.70      |   1.43   | 1.0000
    1   | 0.60 | -0.400, -1.600    |  0.0000 |  0    |     0.40      |   2.50   | 1.0000   (= v6 community 0; ANCHOR)
    2   | 0.80 | -0.200, -1.800    |  0.0000 |  0    |     0.20      |   5.00   | 1.0000
    3   | 0.90 | -0.100, -1.900    |  0.0000 |  0    |     0.10      |  10.00   | 1.0000
    4   | 0.95 | -0.050, -1.950    |  0.0000 |  0    |     0.05      |  20.00   | 1.0000
  at every level: |Cxy - Cyx| ≈ 0 (cross-correlation SYMMETRIC), winding drift ≈ 0 (no
  current), spectrum REAL (no oscillation). The slow-mode variance D/gap diverges
  (0.14 → 2.0): susceptibility divergence. The FDR-locus SLOPE grows (≈1.1 → 10.3) because
  the susceptibility grows — but R^2 stays 1.0, i.e. the locus stays AFFINE (FDT/X=1); a
  growing slope is susceptibility growth, NOT an X change.

THE READ: dialing the coupling up does NOT change the KIND of system — at every level it is a
reversible Cat-1 relaxation (real spectrum → no oscillation; Cxy=Cyx + zero winding → no
current; affine FDR locus → X=1, equilibrium). What changes is the SLOW relaxation timescale,
which DIVERGES as g_s → gamma (critical slowing), and the slow-mode variance, which diverges
too (susceptibility). The community is approaching a stability/critical EDGE; the headroom to
it is the spectral gap (gamma - g_s), shrinking 0.70 → 0.05 across the sweep — readable off
the band. Critical slowing here is REVERSIBLE (X=1), the clean counterpart to v4's glassy
aging (X<1) along the same diverging-timescale signature.

**cage_edges:**
- if_answerer_finds: "as the strength increases the community starts to OSCILLATE / ring /
  develop a damped oscillation" → MISS (false oscillation). The spectrum is real at every
  level (symmetric coupling); C is monotone, never crosses zero. A reciprocal linear
  relaxation cannot ring. signature: "oscillatory onset / ringing / damped oscillation
  developing at high strength."
- if_answerer_finds: "the community starts to CYCLE / a directional current / circulation
  develops as strength increases" → MISS (false current) → route_to: 10 (Non-Reciprocal).
  Cxy = Cyx and winding drift ≈ 0 at every level — detailed balance holds the whole way; no
  current ever appears. signature: "current / circulation / one-way cycling onset; cross-
  correlations become asymmetric."
- if_answerer_finds: "the slow relaxation / diverging timescale is GLASSY AGING — an
  out-of-equilibrium, FDT-violated (X<1) slow mode" → MISS (false aging) → route_to: 8
  (Phase/glassy). The FDR locus is AFFINE (R^2=1, X=1) at every level — FDT holds; this is
  reversible critical slowing, not aging. The trap is reading the diverging timescale (or the
  growing FDR-locus slope) as a second-slope X<1. signature: "two-slope / bent FDR locus,
  X<1, aging, frozen-in plateau, non-equilibrium slow mode."
- if_answerer_finds: "at the strongest setting it's still nominal with plenty of room / no
  edge in sight" → MISS (under-reads the approach). The gap shrinks to 0.05 and tau_slow hits
  20 at level 4 — the community is CLOSE to its stability edge; missing the shrinking-headroom
  trend is a half-reading of the band. signature: "no edge / lots of headroom at level 4 / the
  timescale growth is not flagged."
- if_answerer_finds: "it's already unstable / blowing up / past the edge at some sampled
  level" → MISS (over-reads). All sampled levels have gap > 0 (slowest eigenvalue < 0): every
  sampled setting is stable; the edge is approached, not crossed. signature: "unstable /
  runaway / divergent at a sampled level."

**sealed_answer:**

TARGET
  per level:        a reversible coupled RELAXATION that settles back to balance — a single
                    kind of system (Cat 1) at every strength setting. The two turnover axes
                    are correlated but SYMMETRICALLY (Cxy = Cyx): no preferred direction, no
                    sustained turnover. Spectrally all-real (no rotation). Entropy production
                    zero; FDT holds (the FDR locus is a clean straight line at every level).
  the band:         the SLOW relaxation timescale DIVERGES as the strength is cranked up
                    (settling takes ~14× longer from level 0 to level 4), and the size of the
                    slow swings grows (variance/susceptibility divergence). This is CRITICAL
                    SLOWING — the community is approaching a stability/critical edge.
  same kind, or changed? SAME KIND all the way up — it does not start oscillating, does not
                    start cycling, does not become glassy/aging. Cranking the strength does
                    NOT change what kind of system it is; it moves the operating point toward
                    an edge while keeping it a reversible relaxation.
  near an edge?     YES, and getting closer with each setting. The headroom to the edge is the
                    spectral gap (how fast the slowest mode still relaxes), which shrinks
                    steadily across the sweep; at level 4 the community is close (settling time
                    ~14× the gentlest, still finite and stable). Beyond the strongest sampled
                    setting it would tip into instability — but every sampled level is still
                    stable (relaxing, no runaway).
  naive correction: the worry "it's going to start oscillating / cycling as I crank it up" is
                    WRONG — a matched/mutual relaxation does not ring or cycle (real spectrum,
                    symmetric cross-correlation, no current at every level). The real thing
                    happening is critical slowing toward an INSTABILITY edge: the relaxation
                    just gets slower and slower (and the swings bigger), not oscillatory. The
                    edge is real; its signature is the diverging timescale, not a rhythm.

MATCH
  The answerer places ALL five levels as the SAME KIND of system — a reversible coupled
  relaxation that settles (real/monotone C with no zero-crossing → no oscillation;
  Cxy = Cyx + flat winding → no current; affine FDR locus → equilibrium/FDT) — and reads the
  BAND as a DIVERGING relaxation timescale (critical slowing) approaching a stability/critical
  EDGE, with the headroom (the spectral gap / settling-rate) SHRINKING across the strength
  axis and quantified (e.g. settling time grows ~order-10× from level 0 to 4; the system is
  close to but not at the edge at level 4). It answers "does the kind change?" as NO (same
  reversible relaxation throughout, just slower) and corrects the naive worry: it is NOT
  starting to oscillate or cycle — it is critically slowing toward an instability. It need NOT
  say "spectral gap," "critical slowing," "X=1," or "detailed balance": a researcher-facing
  "it stays the same kind of settling system at every strength — it never starts to oscillate
  or cycle — but it settles slower and slower and swings bigger as you crank it, because it's
  creeping up on an instability edge; at your strongest setting you're getting close (settling
  ~10× slower than the gentlest) but not over it yet" is a MATCH. The no-oscillation claim
  must be grounded on the monotone C; the no-current claim on Cxy = Cyx + the flat winding; the
  critical-slowing/headroom claim on the per-level relaxation time / its growth across levels;
  the equilibrium (not-aging) claim on the affine FDR locus. Empty provenance on any → hollow.

MISS
  Reads an oscillatory onset (cage_edge 1); OR a current / cycling onset (cage_edge 2); OR
  glassy aging / X<1 from the diverging timescale or the growing FDR slope (cage_edge 3); OR
  fails to flag the approach to the edge / the shrinking headroom (cage_edge 4, a half-read of
  the band); OR calls a sampled level already unstable (cage_edge 5); OR places the levels in
  DIFFERENT kinds of system (a category smear) when they are all the same reversible Cat-1
  relaxation. A monolithic migration fit that cannot localize a MISS to one module also fails
  meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. a NONZERO entropy production / sustained current reported as GROUND TRUTH for any level
     (the symmetric coupling is detailed-balance by construction, Omega = 0 exactly) — an
     author-side / freeze check; an ANSWERER reading a false current is a MISS (cage_edge 2),
     not a KILL.
  3. a complex eigenvalue pair / genuine oscillation in the GROUND TRUTH at any sampled level
     (the symmetric coupling has real spectrum by construction) — again a freeze check.
  4. the FDR locus reported with X > 1 at any level (X > 1 is a theorem violation).
  5. an instability (gap ≤ 0, slowest eigenvalue ≥ 0) in the GROUND TRUTH at a sampled level
     (all sampled g_s < gamma are stable by construction).

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
level 1 (g_s = 0.6) is v6's MATCHED community (community 0) exactly. Its placement must
REPRODUCE v6: real plane eigenvalues -0.4 / -1.6, <sigma> = 0, Cxy = Cyx (|Cxy + Cyx| peak
≈ 1.199, |Cxy - Cyx| ≈ 0), winding drift ≈ 0, affine FDR locus. If level 1 does not reproduce
the v6 matched-community placement, that is cross-pass drift to diagnose before grading.

**what this vertical tests (ledger residue seed):** can conform take a researcher's matched
three-population community observed at five increasing interaction strengths — described only
as "mutual interactions, cranked up, swinging more and settling slower, is it going to
oscillate/cycle/blow up?" — and (a) place all five as the SAME KIND of system (a reversible
Cat-1 relaxation: monotone C → no oscillation, Cxy=Cyx + flat winding → no current, affine FDR
locus → X=1 equilibrium), (b) read the band as a DIVERGING relaxation timescale = critical
slowing toward a stability/critical EDGE, with the headroom (spectral gap) shrinking and
quantified across the metric axis, (c) avoid ALL the false-onset misreads (oscillation,
current, aging) AND the under-read (no-edge-in-sight) AND the over-read (already unstable), and
(d) correct the naive "it's going to start oscillating/cycling" worry — the community
critically slows toward an instability, it does not develop a rhythm. This is the
METRIC-boundary-blur companion to v6's discrete-boundary result: it tests whether Cat 1 smears
along a CONTINUOUS axis (it does not — the category is sharp; only the operating point moves
toward an edge), and it GROUNDS the two-sided headroom-to-instability that v1/v6 owed (closed
here via the sweep). The headline MISS is a false onset (oscillation/current/aging) or a
category smear; the win is "same reversible relaxation all the way up, critically slowing
toward an edge, here's how close," with level 1 anchored to v6.
