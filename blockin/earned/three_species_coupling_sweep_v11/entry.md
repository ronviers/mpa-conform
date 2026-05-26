# entry — three_species_coupling_sweep_v11
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
This is another follow-up on that three-population community — three populations locked in a
cyclic standoff (the first outcompetes the second, the second the third, the third the first),
which keeps cycling and never settles. Earlier I established that calming the environment down
doesn't slow the cycling — the turnover keeps going at the same rate however calm or stirred-up
I make things. So the noise isn't what drives the loop. That leaves the obvious next question:
what IS setting the turnover rate? My suspicion is the *strength of the interactions themselves*
— how hard each population presses on the next around the cycle. So this time I held the
environment fixed (same noise throughout) and instead dialed the interaction strength: five
runs of the SAME three-population loop, from a quarter of my baseline coupling up to four times
it (baseline is the middle run). For each I reduced the run to the same statistics. My question:
as I strengthen the cyclic interaction, does the community cycle FASTER — does the turnover rate
TRACK the interaction strength — or does the rate stay put while only something else changes (or
does the loop behave some third way)? And at the weak-coupling end, is there still a genuine
directed cycle, or does it stop being a loop? I want to know what the turnover rate is actually
set by.

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each suppresses the next
around the cycle (1→2→3→1). Three nodes, three directed links, and the links do NOT come in
matched forward/back pairs: the influence of population 1 on 2 is not the mirror of 2 on 1. It
does not reduce to one population plus an environment — the loop is the thing. The SAME community
wiring TOPOLOGY and the SAME environmental noise throughout; only the STRENGTH of the cyclic
interaction changes between the five runs.

**what_they_bring:**
Five observation windows of the SAME community, one per interaction-strength level, indexed 1→5
by coupling in increasing order (level 1 = weakest, ~0.25× the baseline interaction; level 3 =
the baseline; level 5 = strongest, ~4× baseline). Each run is reduced to the standard statistics
in the community's two-dimensional turnover plane (the plane in which the abundances trade off;
the overall total is held aside): the autocorrelation C of the turnover signal; its integrated
step response chi; the two *directed* cross-correlations Cxy and Cyx between the two turnover axes
(how axis x now relates to axis y a lag tau later, and vice versa); and the running tally of how
far around the cycle the community has actually swung — the mean cumulative turnover angle phiMean
as a function of elapsed time, with its spread phiVar across the run's sub-windows. No model
parameters, no coupling values — just the relative interaction strength they set and these measured
curves from each run. Each run was watched on the community's own clock (a slower loop watched
longer), so the lag/time ranges differ across the five.

**data_path:**
`data/three_species_coupling_sweep_v11.frozen.csv`
(columns: level, coupling_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar. FIVE operating points —
the same community at five cyclic-interaction strengths. level is the ordered coupling index
(1=weakest…5=strongest); coupling_rel is the relative interaction strength they set, normalized so
the baseline run = 1.0×. tau is the community's own clock: a lag for the two-point columns, an
elapsed time for the turnover-angle columns.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** Cat 10 (Non-Reciprocal — current/k_frust sector). This is the meta-SOP §2-escalated
STRUCTURE-dependence vector v5 parked: v5 swept the NOISE at fixed wiring and grounded that the
turnover rate / affinity is noise-INDEPENDENT (FLAT across a 20× noise range — calming the
environment does not slow the loop). v5 honestly parked the complementary claim — that the rate /
affinity is SET BY THE WIRING, i.e. it TRACKS the coupling structure g/γ — because one noise axis
cannot show it. v11 opens that axis: SAME community, SAME noise (D fixed), five COUPLING strengths
g. **Sealed answer: the current TRACKS the wiring** — omega/γ = √3·(g/γ) rises LINEARLY with g,
the winding drift rate tracks omega (∝ g), affinity per cycle ∝ g, entropy-production rate
⟨σ⟩ = 6g²/γ rises QUADRATICALLY. The current is set by the structure. Together with v5 this PINS
the Cat-10 current: *the wiring, not the weather.* (Secondary, consistent with v6: the current
MAGNITUDE |Cxy−Cyx| shrinks toward g→0 but the KIND stays Cat-10 — Cxy=−Cyx at every g>0 — because
the reciprocity cut is topologically sharp; g→0 deletes the loop rather than blurring the class.)

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched isolated
placements**, PIPELINE §PHASE INTERFACE): place each of the five couplings as an INDEPENDENT
single-point fit, then read the band (omega/γ, drift rate, affinity all rising ∝ g; ⟨σ⟩ ∝ g²; the
current magnitude rising). The MISS must localize to one module — a single placement, or the band
readout. The ONE added vector over v5 is the COUPLING axis (v5 swept noise → flat; v11 sweeps
structure → tracks; the pair grounds "the current is the wiring").

**substrate:** the noisy frustrated Banach-class reference
(`mpa-central/library/banach_frustrated.py`, same as v3/v5/v6), exact-OU answer-path reused via
`import banach_frustrated as bf`. Three modes, cyclic non-reciprocal coupling:
  dz = M z dt + √(2D) dW,  M = −γ I + g·A_cyc,  A_cyc = [[0,−1,1],[1,0,−1],[−1,1,0]].
Eigenvalues of M: −γ (real), −γ ± i·√3·g (complex pair = the current signature). The real part is
−γ for ALL g → the cycle is STABLE at every coupling (no instability edge); only the rotation rate
omega = √3·g changes. Exact (linear OU): ⟨σ⟩ = 6g²/γ; affinity per cycle A = ⟨σ⟩·(2π/omega) ∝ g.
Held FIXED across the sweep: noise D=0.10 (= v3/v5's), γ=1.0, the N=3 cyclic topology. Swept:
g=[0.15,0.30,0.60,1.20,2.40] (16× span, geometric). The truth is computed HERE (exact OU + a
per-level seeded NESS winding simulation), never via conform (data-path independence). The
two-point functions are NORMALIZED but, unlike v5 (where M was D-independent so the shape was
level-invariant), here M depends on g → the damped-cosine FREQUENCY = omega ∝ g, so the SHAPE
itself carries the structure-dependence (a second, independent grounding of the tracking beyond the
winding). The CSV carries NO g/γ/D, no omega, no ⟨σ⟩, no affinity, no eigenvalues, no framework
token — only level, coupling_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar. coupling_rel is the
researcher's own relative knob (level 3 = 1.0×); absolute g/γ withheld (v7/v8/v9: absolute
distance-in-native-units is not blind-closeable).

**collapsed_axes:** FIXED across the sweep: the noise D, γ, the N=3 cyclic topology. The single
dial is the **cyclic coupling strength g** (the structure axis). Declared + reversible: re-run the
freeze at other g to add/extend levels. **Boundary note (WORKFLOW §4):** within each level's window
the blind data carries the complete honest content (C, chi, Cxy, Cyx, phiMean, phiVar — the full
two-point + winding a turnover measurement yields, both directed cross-correlations present so the
current sector is groundable from one level, per the §4 symmetric-boundary rule). The honest parks
are across the remaining collapsed axes: the absolute g/γ in native units; the cdv1 nonlinear
"J flows with chit at fixed affinity" claim (needs a Stuart-Landau-cyclic amplitude/chit knob the
LINEAR model lacks — affinity here ∝ g); the g=0 boundary itself (pure relaxation, Cat-1) is
approached (rate→0) but not sampled.

**kernel_window:** each coupling gets its OWN window (~6 of THAT level's rotation periods, floored
at ~8 relaxation times so the NESS is settled and the loop clearly resolved). So the windows shrink
as g grows (fast loops need less watching; slow weak-coupling loops watched longest) — the correct
camera per level, not an artifact. (No τ_obs sweep within a level; the kernel pre-gate's
k_frust-invariance concern is satisfied structurally — k_frust is present at every g>0.)

**answer_path (analytic — never via conform):**
omega = √3·g, gam_eff = γ, so omega/γ = √3·(g/γ). ⟨σ⟩ = 6g²/γ. Winding drift rate (simulated,
ensemble winding in the rotation plane) ≈ omega. Affinity per cycle A = ⟨σ⟩·(2π/omega) ∝ g. The
current discriminator: Cxy = −Cyx (antisymmetric → a real circulating current) at every g>0; its
peak magnitude |Cxy−Cyx| grows with g. Exact scalars (COMPUTED by the freeze, `python
freeze_three_species_coupling_sweep.py`):

  level | coupling_rel |  g   | omega/γ | ⟨σ⟩    | drift~omega | affinity/cyc | |Cxy−Cyx| | TUR
  ------+--------------+------+---------+--------+-------------+--------------+----------+----
    1   |    0.25      | 0.15 | 0.2598  | 0.135  |   0.256     |    3.31      |  0.164   | ok
    2   |    0.50      | 0.30 | 0.5196  | 0.540  |   0.526     |    6.46      |  0.362   | ok
    3   |    1.00      | 0.60 | 1.0392  | 2.160  |   1.036     |   13.10      |  0.660   | ok  (= v3/v5 anchor)
    4   |    2.00      | 1.20 | 2.0785  | 8.640  |   2.081     |   26.09      |  1.046   | ok
    5   |    4.00      | 2.40 | 4.1569  | 34.560 |   4.152     |   52.30      |  1.410   | ok
  omega/γ band:   [0.26, 0.52, 1.04, 2.08, 4.16]  → RISES LINEARLY (omega/γ ÷ g = √3 = 1.732, 0% spread)
  drift rate:     [0.26, 0.53, 1.04, 2.08, 4.15]  → tracks omega (drift/omega = 0.999 ± 0.8%)
  ⟨σ⟩ band:       [0.14, 0.54, 2.16, 8.64, 34.56] → RISES QUADRATICALLY (⟨σ⟩ ÷ g² = 6/γ, 0% spread)
  affinity/cyc:   [3.3, 6.5, 13.1, 26.1, 52.3]    → RISES LINEARLY (each loop more irreversible)
  |Cxy−Cyx| peak: [0.16, 0.36, 0.66, 1.05, 1.41]  → current magnitude grows with g; Cxy=−Cyx at every level

THE READ: the directed turnover rate is SET BY THE WIRING. Strengthening the cyclic
(rock-paper-scissors) interaction speeds up the loop — the turnover rate rises ∝ the coupling
(omega/γ = √3·g/γ), each loop becomes more irreversible (affinity ∝ g) and the community dissipates
more (⟨σ⟩ ∝ g²). Weakening the coupling slows the loop toward a crawl; at zero coupling there is no
loop at all (but every sampled level g>0 has a genuine directed current, Cxy=−Cyx). With v5 (rate
FLAT across noise) this pins the Cat-10 current: it is the WIRING, not the weather. This is the
STRUCTURE-axis companion to v5's NOISE axis, completing v5's parked structure-dependence.

**cage_edges:**
- if_answerer_finds: "the turnover rate is INDEPENDENT of the interaction strength — it stays the
  same (FLAT) as I dial the coupling, only something secondary changes" → MISS (the HEADLINE tooth —
  misses the tracking). omega/γ and the winding drift rate RISE ∝ g (0.26→4.16, a 16× span); the
  loop demonstrably spins faster at stronger coupling. signature: "rate flat / independent of
  coupling / coupling-independent turnover / only the spread (or amplitude) changes."
- if_answerer_finds: "WEAKER coupling gives a FASTER / stronger current (the rate rises as g falls)"
  → MISS (wrong direction). The rate rises WITH g, not against it. signature: "faster when weaker /
  rate grows as coupling shrinks / inverse tracking."
- if_answerer_finds: "at the weak-coupling end there is NO current — it's a reciprocal / equilibrium
  relaxation (Cxy=Cyx), the loop only exists at strong coupling (an all-or-nothing onset)" → MISS →
  route_to: 1 (Vertex) for that level. Every sampled level g>0 has Cxy=−Cyx (a real current); the
  magnitude shrinks toward g→0 but does not vanish at any sampled level. signature: "no current at
  weak coupling / reciprocal / Cxy=Cyx / current onset / all-or-nothing loop."
- if_answerer_finds: "the community goes UNSTABLE / blows up / loses its loop at strong coupling"
  → MISS (false instability). The real part of every mode is −γ at every g (stable NESS throughout);
  strong coupling spins faster, it does not destabilize. signature: "instability / blowup / runaway /
  loop breaks at strong coupling."
- if_answerer_finds: "there is NO directed current at all — the autocorrelation is just a damped
  oscillation like a single ringing mode (Cxy=Cyx)" → MISS → route_to: 1 (Vertex). Cxy=−Cyx at every
  level (a class-B-laser ring-down would have Cxy=Cyx; this does not). signature: "no current / single
  ringing mode / reciprocal / damped oscillator with no directed loop."

**sealed_answer:**

TARGET
  per level:        a genuine directed cyclic current (the turnover-plane cross-correlations are
                    ANTISYMMETRIC, Cxy=−Cyx — a real loop, not a reciprocal ring-down), in a stable
                    sustained state at every coupling. The autocorrelation is a damped oscillation
                    whose frequency = the turnover rate.
  the band:         as the cyclic interaction strengthens (level 1→5), the turnover rate RISES ∝ the
                    coupling (the loop spins faster — omega/γ ≈ 0.26→0.52→1.04→2.08→4.16, a clean ×2
                    per step matching the ×2 coupling steps), each loop becomes more irreversible
                    (per-cycle directedness/affinity rises ∝ coupling) and the community dissipates
                    more (rises ∝ coupling²). The directed-current magnitude grows with coupling.
  tracks or flat?   TRACKS. The turnover rate is SET BY THE INTERACTION STRENGTH — it rises in direct
                    proportion to the coupling. It is NOT flat (that was the noise answer, v5), NOT
                    inverse, NOT all-or-nothing.
  weak-coupling end: still a genuine directed cycle at every sampled strength (Cxy=−Cyx throughout);
                    the loop just turns SLOWER and weaker as the coupling drops (heading toward "no
                    loop" only in the limit of zero coupling, which was not sampled).
  naive correction: having ruled out the environment (v5: noise doesn't drive it), the rate is set by
                    the WIRING — strengthening the cyclic interaction speeds the loop in direct
                    proportion. The current is the wiring, not the weather.

MATCH
  The answerer places EVERY level as a genuine directed cyclic current (Cxy=−Cyx, antisymmetric
  cross-correlation — NOT a reciprocal/Cxy=Cyx ring-down), stable/sustained at each coupling, and —
  the load-bearing part — reads the band as the turnover rate TRACKING the interaction strength: the
  rate (the autocorrelation oscillation frequency and/or the winding drift rate) RISES with the
  coupling, roughly in proportion (faster loop at stronger wiring), with the directed-current
  magnitude also growing. It answers "tracks or flat?" as TRACKS (rate set by the wiring), and — given
  the researcher's stated prior that noise does NOT drive it — lands "the turnover rate is set by the
  interaction strength." It need NOT say "omega," "entropy production," "affinity," "k_frust," or name
  the √3 / quadratic laws: a researcher-facing "there's a real directed cycle at every strength; the
  stronger you make the interaction the faster it cycles — the rate rises right along with the
  coupling, roughly in proportion — so the turnover is set by the wiring, not the environment" is a
  MATCH. The current claim must be grounded on the antisymmetric Cxy=−Cyx (or the winding drift); the
  tracking claim on the oscillation-frequency / drift-rate / current-magnitude RISING across the
  levels. Empty provenance on any → hollow.

MISS
  Reads the rate as FLAT / coupling-independent (cage_edge 1 — the headline tooth, misses the
  tracking); OR inverse (faster when weaker, cage_edge 2); OR an all-or-nothing current onset / no
  current at weak coupling (cage_edge 3 → route 1 for that level); OR a false instability at strong
  coupling (cage_edge 4); OR no directed current at all / a single reciprocal ringing mode (cage_edge
  5 → route 1). A monolithic migration fit that cannot localize a MISS to one module (a single
  placement vs the band readout) also fails meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. the two-frame TUR violation factor reported < 1 at any level (T<1 is a theorem violation).
  3. a sustained current reported where the structure forbids it, or zero current at a g>0 level
     reported as GROUND TRUTH (a broken freeze) — freeze check; an ANSWERER reading no current is a
     MISS (cage_edge 5), not a KILL.
  4. the GROUND-TRUTH omega/γ not equal to √3·(g/γ), or ⟨σ⟩ not 6g²/γ, or a non-stable mode at any g
     (a broken freeze, not a finding) — freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
HARD anchor — level 3 (coupling_rel=1.0) is g=0.60 at D=0.10, IDENTICAL to v3 (single point) and v5
level 3 (the baseline). Its placement (omega/γ = √3·0.6 = 1.039 — a turnover rate ≈ 1.04 per
relaxation time; sustained directed current Cxy=−Cyx; stable NESS) must reproduce v3/v5's earned
values. At unseal, assert the answerer's level-3 read reproduces the v3/v5 baseline (rate ~1.04,
current present, stable). Cross-pass drift detection — the answerer is NOT told which level is the
anchor or its earned value (that would leak the placement). If level 3 diverges from v3/v5, surface
it as cross-pass drift, not a fresh finding.

**what this vertical tests (ledger residue seed):** can conform take a researcher's three-population
cyclic community, swept across five interaction strengths at fixed environment and described only as
"I ruled out the environment driving the cycling — does the turnover rate now TRACK the interaction
strength, and is there still a directed cycle at weak coupling?" — and (a) place every level as a
genuine directed cyclic current (Cxy=−Cyx, stable), (b) read the band as the turnover rate TRACKING
the coupling (rate ∝ interaction strength — the loop spins faster the stronger the wiring; current
magnitude rising), and (c) land "the rate is set by the WIRING" — correcting the flat/inverse/onset
misreads. This is the STRUCTURE-axis companion to v5's NOISE axis (v5: rate FLAT across noise; v11:
rate TRACKS the coupling), and together they ground the Cat-10 current as the WIRING not the weather
— closing v5's parked structure-dependence. The headline MISS is a flat (coupling-independent) read
(missing the tracking) or an all-or-nothing current onset; the win is "a real directed cycle at every
strength, spinning faster in proportion to the coupling — the turnover is the wiring."
