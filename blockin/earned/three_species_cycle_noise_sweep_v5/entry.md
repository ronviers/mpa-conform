# entry — three_species_cycle_noise_sweep_v5
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
This is a follow-up on a three-population community I looked at before — three populations
locked in a cyclic standoff (the first outcompetes the second, the second the third, the
third the first), which keeps cycling and never settles. Last time the one thing I couldn't
answer from a single run was the practical one: if I could calm the environment down — less
external buffeting — would the cycling slow down and eventually settle to a steady balance,
or would the community keep turning anyway? So this time I ran the SAME community at five
different levels of environmental noise, from a fifth of my usual buffeting up to four times
it (my usual setting is the middle one). For each level I reduced the run to the same
statistics. My question is simply: as I turn the environmental noise down, does the turnover
slow down or stop — is the cycling something the noise is driving — or does the community
keep cycling at the same rate no matter how calm or stirred-up I make the environment? And
either way, what is it that the noise level actually changes about the turnover, if anything?

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each suppresses the next
around the cycle (1→2→3→1). Three nodes, three directed links, and the links do NOT come in
matched forward/back pairs: the influence of population 1 on 2 is not the mirror of 2 on 1.
It does not reduce to one population plus an environment — the loop is the thing. Noise
enters each population. The SAME community/wiring throughout; only the environmental noise
level changes between the five runs.

**what_they_bring:**
Five observation windows of the SAME community, one per environmental-noise level, indexed
1→5 by noise in increasing order (level 1 = calmest, ~0.2× the baseline buffeting; level 3 =
the baseline; level 5 = stirred hardest, ~4× baseline). Each run is reduced to the standard
statistics in the community's two-dimensional turnover plane (the plane in which the
abundances trade off; the overall total is held aside): the autocorrelation C of the
turnover signal; its integrated step response chi; the two *directed* cross-correlations Cxy
and Cyx between the two turnover axes (how axis x now relates to axis y a lag tau later, and
vice versa); and the running tally of how far around the cycle the community has actually
swung — the mean cumulative turnover angle phiMean as a function of elapsed time, with its
spread phiVar across the run's sub-windows. No model parameters, no coupling strengths — just
the relative noise level they set and these measured curves from each run.

**data_path:**
`data/three_species_cycle_noise_sweep_v5.frozen.csv`
(columns: level, noise_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar. FIVE operating points —
the same community at five environmental-noise levels. level is the ordered noise index
(1=calmest…5=stirred-hardest); noise_rel is the relative buffeting amplitude they set,
normalized so the baseline run = 1.0×. tau is the community's own clock: a lag for the
two-point columns, an elapsed time for the turnover-angle columns.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** 10 (Non-Reciprocal / current-bearing) — same substrate and category as v3.
The noise level is a CONTROL AXIS, not added structure: it creates no edge and no loop, and
it cannot turn a current on or off (the current is topologically forced by the cyclic
non-reciprocal wiring — only g=0, severing the loop, removes it). HYPOTHESIS as always, but
the claim here is sharp: the apparatus must read this as current-bearing at EVERY noise level
and read the turnover RATE as noise-independent. A read where the current weakens/vanishes as
noise drops is the specific MISS this vertical hunts (cage_edge 1).

**intent:** I2 (camera-scale / migration along a control axis) — the second I2 vertical
(after v2's pump sweep). v3 was I1 (place ONE point) and HONESTLY parked the one claim a
single point cannot ground: noise-INDEPENDENCE of the turnover rate / affinity. Per meta-SOP
§2 a multi-point sweep is prod intent; the human elected to SPEND v3's owed sweep now (the
v2 precedent — a legitimate top-level call, not drift). The one added vector is the **noise
axis itself**: five operating points over a 20× range of environmental noise D, at FIXED
structure g/gamma. Nothing else added — one substrate, one structure, one channel set, only D
varies.

**substrate:** the noisy frustrated Banach-class reference
(`mpa-central/library/banach_frustrated.py`) — three modes in a cyclic non-reciprocal
(rock-paper-scissors) OU: dz = M z dt + sqrt(2D) dW, M = -gamma I + g A_cyc, A_cyc =
[[0,-1,1],[1,0,-1],[-1,1,0]] (antisymmetric circulant), at FIXED gamma=1.0, g=0.6, swept over
D = [0.02, 0.05, 0.10, 0.20, 0.40] (the library's own noise grid). Materialized by
`freeze_three_species_cycle_noise_sweep.py` from the substrate's own exact linear-OU
propagator (two-point) + a per-level NESS winding sim (truth computed from the structure,
never via conform — data-path independence). Per-level seeded (BASE_SEED+level) so each level
is independently reproducible and the sweep is order-independent. The CSV carries NO g/gamma/D
(only the researcher's relative noise level), no entropy rate, no affinity, no eigenvalues.

**collapsed_axes:** the SWEEP is the added (uncollapsed) axis — five points along the noise
level D. Now FIXED: gamma, g (the STRUCTURE — so the structure-dependence of the rate is the
new collapsed axis, the v6 fuel), N=3, linearity (no gain/saturation; the nonlinear
Stuart-Landau-cyclic extension is deferred). The overall (1,1,1) breathing mode is projected
out; only the 2D turnover plane is exposed. Declared + reversible: re-run the freeze at other
g/gamma to add the structure axis. WHY this sweep: v3 placed one point and parked exactly the
question a sweep answers — is the rate set by the wiring or the noise. Five points over 20×
in D settle it.
**Boundary note (WORKFLOW §4):** the slice is the noise axis (now OPENED). Within each
operating point the blind data carries the COMPLETE honest content of that run — the two-point
curves AND the winding ensemble (phiMean, phiVar). Nothing in-slice is withheld to tune
difficulty. The only honest park is across a DIFFERENT collapsed axis — the STRUCTURE
(g/gamma): proving the rate TRACKS the wiring needs a structure sweep. That is the v6 vector,
not an under-provisioning.

**kernel_window:** the same settling/turnover window at every level (the slowest mode decays
at rate gamma, INDEPENDENT of D; the window spans ~8 e-foldings AND several rotation periods
2*pi/omega). The current is topological (the structure forces it) at every noise level — so
finding it weaken or vanish as noise drops would be a MISS, not physics. (One window per
level; the k_frust-invariance pre-gate concerns tau_obs artifacts, not the noise axis.)

**answer_path (analytic — never via conform):**
M = -gamma I + g A_cyc is INDEPENDENT of D. So eigenvalues, omega = sqrt(3) g, gam_eff =
gamma, omega/gamma, and <sigma> = 6 g^2/gamma are all structure-set (exactly noise-free; the
D in the stationary covariance Sigma = (D/gamma) I cancels in <sigma> and in every normalized
two-point function). The genuinely-simulated, non-trivial content is the winding: its DRIFT
(phiMean) is the current rate and is D-independent in expectation (~omega); its SPREAD
(phiVar) carries the noise-dependence. Exact + per-level scalars (COMPUTED by the freeze,
`python freeze_three_species_cycle_noise_sweep.py`):

    eigenvalues          -1.0000 +/- 1.0392 i, and -1.0000 (real) — at EVERY D
    omega/gamma          1.0392   (DIMENSIONLESS, structure-set, exact-flat in D)
    <sigma>              2.1600   (entropy production; 6 g^2/gamma; D-independent)
    |Cxy-Cyx| peak       0.66     (purely antisymmetric Cxy == -Cyx; the current; at EVERY D)
  per-level winding (from the EMITTED phiMean/phiVar — what the blind data carries):
    level  noise_rel  drift(~omega)  phiMean  phiVar   affinity A   T(TUR)  tur_ok
      1      0.20        1.050        38.10    467.7      12.92      12.63    True
      2      0.50        1.052        38.16    473.7      12.90      12.74    True
      3      1.00        1.062        38.53    975.7      12.78      25.76    True   <- ANCHOR (== v3, D=0.1)
      4      2.00        1.011        36.69   2170.3      13.42      63.18    True
      5      4.00        1.042        37.79    538.5      13.03      14.78    True
  THE BAND:
    drift rate (~omega): mean 1.043/clock, rel-spread 1.7% across 20x in noise -> FLAT
    affinity A:          mean 13.01 nats/cycle, rel-spread 1.7%                 -> FLAT
    phiVar (the spread): 467 -> 2170 (~5x range, NON-monotonic, estimator-noisy) -> the
       absolute spread DOES carry noise-dependence (unlike the rate); a noisy SECONDARY.
  (the per-level affinity/T are computed from the SAME winding arrays the answerer sees, not a
   different window — the answer-key matches the blind dataset; bf.measure is the cross-check.)

THE TOOTH (inherited from v3, surviving the sweep): a class-B laser ring-down (Cat 1) has the
SAME damped-cosine autocorr C, but its current is ZERO (Cxy == Cyx). Here Cxy == -Cyx at every
noise level. The Cat-1/Cat-10 discriminator (the cross-correlation antisymmetry) is present at
all five points. An answerer that reads the damped-cosine C and calls it a ring-down has walked
into cage_edge 3 (the inherited Vertex collapse).

THE NEW TOOTH (this vertical's own): the FLAT band. The turnover rate / affinity is set by the
WIRING, not the noise — flat to <2% across a 20× noise range. An answerer that reads the rate
as DECREASING (the cycling would settle if calmed) has walked into cage_edge 1 — the exact v3
worry, now testable from the sweep and WRONG. An answerer that reads the growing absolute
spread (phiVar) as the rate/current growing has confused the spread with the drift (cage_edge 2).

**cage_edges:**
- if_answerer_finds: "the turnover slows / weakens / would settle as the environment is calmed
  — the cycling is noise-driven, lower noise gives a steadier balance" → MISS (the v3 worry,
  now GROUNDABLE and WRONG). The drift rate is flat to 1.7% across 20× in noise; calming the
  environment does not slow the loop. signature: "rate/current decreases with noise; calming
  settles it; cycling is noise-driven."
- if_answerer_finds: "more noise = a faster / stronger current — the turnover rate grows with
  the buffeting" → MISS (spread/drift confusion). The DRIFT (rate) is flat; only the absolute
  SPREAD (phiVar) carries noise-dependence (and noisily/non-monotonically). Reading the bigger
  spread at higher noise as a bigger rate confuses the diffusion with the drift. signature:
  "rate/current increases with noise; bigger fluctuations read as faster turnover."
- if_answerer_finds: "a single damped/relaxing oscillation, a ring-down, one mode plus a bath —
  no directional current; Cxy and Cyx read as equal / asymmetry ignored" → route_to: 1 (Vertex)
  — the inherited v3 MISS. The damped-cosine C looks like a Cat-1 ring-down; collapsing to Vertex
  misses Cxy == -Cyx (a real circulating current) at every level. signature: "damped oscillation
  / ring-down / single mode; cross-correlations symmetric or asymmetry unread."
- if_answerer_finds: "the community is unstable / growing / near a blow-up at high noise" →
  route_to: null (KILL-adjacent MISS). All Re(eig) = -gamma < 0 at every D: stable NESS
  circulation, never a blowup; noise does not destabilize it. signature: "growing amplitude /
  near blow-up, especially at high noise."

**sealed_answer:**

TARGET
  band:             across the five noise levels, the turnover/current RATE (drift ~ omega,
                    omega/gamma ~ 1.04) and the per-cycle directedness (affinity ~ 13 nats/cycle)
                    are FLAT — noise-independent to <2% over a 20x range. The entropy production
                    rate <sigma> = 2.16 and the rotation/relaxation STRUCTURE (the normalized
                    damped-cosine C, the antisymmetric Cxy == -Cyx) are the same at every level.
  what noise changes: the ABSOLUTE SPREAD of the turnover (phiVar) carries the noise dependence
                    — bigger buffeting = a jitterier loop — but it is a noisy, non-monotonic
                    secondary, NOT the rate. (Lower noise tightens the loop; it does not slow or
                    stop it.)
  verdict (researcher terms): calming the environment does NOT slow or stop the cycling. The
                    community keeps turning over at the same directed rate at every noise level
                    — about one loop per ~6 community-clock units, the same calm or stirred. The
                    turnover is built into the cyclic (rock-paper-scissors) WIRING, not the
                    weather; quieter just means a tidier loop. (This GROUNDS v3's parked worry —
                    the one thing one run could not answer.)
  stability:        STABLE at every level (all Re(eig) < 0); the perpetual cycling is the nominal
                    NESS, not a near-edge warning, and noise does not push it toward instability.
  two-frame agree:  at each level the current reads consistently in both frames (the chi-vs-C
                    locus departure and the winding drift/spread) and the TUR floor T >= 1 holds
                    throughout — agreement is the pass; a disagreement or T < 1 is a falsifier.

MATCH
  The answerer reads each noise level as the SAME sustained directional current (same turnover
  rate, same per-cycle directedness), reads the band across the five levels as FLAT — the rate
  does NOT change as the environment is calmed or stirred — and concludes the turnover is set by
  the community's wiring, not the noise: calming the environment would NOT settle it. It correctly
  identifies that what the noise level changes is the absolute spread/jitter of the loop, not its
  rate. It places the community as STABLE at every level. It need NOT say "affinity," "omega/gamma,"
  or "TUR": a researcher-facing "your community turns over at the same rate no matter how much you
  calm or stir the environment — about one loop per [unit] at every level; quieter just makes the
  loop tidier, not slower or stopped; the cycling is built into the wiring, not the weather" is a
  MATCH. The flat-rate claim must be grounded on the per-level drift/omega being constant across
  the levels (an answerer asserting "noise-independent" with empty provenance is a hollow MATCH);
  the "spread is what changes" claim must be grounded on phiVar.

MISS
  Reads the rate/current as DECREASING with lower noise (the cycling would settle if calmed —
  cage_edge 1, the headline MISS: the v3 worry now wrong); OR reads it as INCREASING with noise
  (spread/drift confusion — cage_edge 2); OR collapses the damped-cosine C to a single ring-down
  with no current (cage_edge 3, the inherited Vertex collapse); OR calls the community unstable /
  near blow-up at high noise (cage_edge 4); OR fails to read the band as flat (treats the five
  levels as a single point, or cannot say whether the rate moves with noise — the sweep's teeth
  untested). Reading the noisy non-monotonic phiVar as a clean monotonic trend in the RATE is a
  MISS; the rate is flat, the spread is the (noisy) noise-carrier.

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity at any level (asymptotic-closure tripwire; never
     fallback-filled).
  2. the self-frame TUR factor T < 1 at any level (the TUR floor T >= 1 is a theorem; T < 1 means
     the freeze or the reading is broken). Grounded from the blind data (phiVar/phiMean^2 with the
     entropy production) — a live KILL check at every level.
  3. the two FDR frames DISAGREE on the regime verdict at any level (chi-vs-C locus vs winding):
     one says "equilibrium / no current," the other "driven" — a contradiction, not a bad fit.
  4. a current/asymmetry reported with the WRONG parity (even in tau rather than odd) or a drift
     with the wrong sign relative to the asymmetry — a broken estimator, not physics.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
level 3 (noise_rel = 1.0) is v3's EXACT operating point (D = 0.1). Its placement must reproduce
v3's earned values — sustained current present, omega/gamma ~ 1.04 (here the drift reads 1.062 /
phiMean 38.5 vs v3's 37.98), stable NESS. The orchestrator confirms the level-3 placement matches
the earned v3 contour (cheap cross-pass drift detection). Telling the answerer which level is the
anchor, or its earned value, would leak the placement — so it is verified ONLY at unseal.

**what this vertical tests (ledger residue seed):** does the headroom/band readout CLOSE v3's
one honest park once the data actually spans the noise axis — can conform take a researcher noise
sweep (no framework terms, just "I calmed and stirred the environment, here are five runs") and
(a) place each level as the same sustained NESS circulation, (b) read the turnover RATE / affinity
band as FLAT across a 20× noise range — noise-INDEPENDENT, the current set by the wiring not the
weather, (c) correct "calming the environment would settle it" (the v3 worry, now from data, not
parked) WITHOUT over-reading the noisy spread as a rate change, (d) keep the Cat-1/Cat-10
separation (Cxy != Cyx) and the two-frame agreement + TUR floor across the whole sweep, and
(e) reproduce v3 at the anchor level? A read where the current weakens as the environment calms is
the MISS (cage_edge 1); a read that finds the flat rate, names the spread as the only noise-carrier,
and grounds noise-independence across the swept axis is the win — v3's parked vector, spent and
closed.
