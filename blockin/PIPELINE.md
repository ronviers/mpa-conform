# PIPELINE — the object under study (conform's data-prep silhouette)

This is the **pipeline**: MPA's data-prep machinery that takes a researcher's
`(question, data)` and produces a characterization + a view. It is the *object*
we are blocking in — one of four modules (PIPELINE = object · WORKFLOW = pass-SOP ·
meta-SOP = evolution · HANDOFF = baton). It is NOT the workflow: the **pass-SOP**
(how one pass traverses this pipeline; the A–P interrogation box) lives in
`WORKFLOW.md`, and how passes *evolve* this doc lives in `meta-SOP.md`. The pass-SOP
*wraps* this; its single "answerer-session" step **is** one traversal here. Thin seam:
blind packet + data in, view + verdict out.

> **STATUS: FIVE CATEGORIES LANDED (12 clean verticals + 1 MISS-with-finding, all blind); the
> separability hypothesis is CLOSED (positive).** `laser_ro_nominal_v1` (Vertex/Cat 1) traversed the
> spine ADMISSION → FRAME → SELECTION(I1) → ROOT OP → READOUT; `three_species_cycle_v3` (Cat 10,
> non-reciprocal) added the GATES current-sector — the two-frame readout reached and agreed, blind;
> `glass_two_step_v4` (Cat 8, Phase/glassy) added the aging-FDR sector — a two-step relaxation read as
> FDT-violated (X<1) from the two-slope χ-vs-C locus, blind; `three_species_cycle_noise_sweep_v5`
> (Cat 10 noise sweep) grounded the current's noise-INDEPENDENCE blind; `community_pair_v6`
> (Cat 1 ⊕ Cat 10 in ONE packet) landed the first MINIMAL-DISTANCE 1↔10 separation — a
> reciprocity-flip pair on one substrate family, separated CLEAN on the cross-correlation
> symmetry, blind; `coupling_ramp_v7` (Cat 1, metric-axis sweep) showed Cat-1 does NOT smear
> along a CONTINUOUS coupling-strength axis — critical slowing toward a stability edge, blind;
> `magnet_temp_sweep_v8` (Cat 1, metric axis CROSSING a thermodynamic critical point) showed Cat-1
> stays sharp through Tc (X=1, band peaks-and-recovers) — a phase boundary is not a dynamical-category
> boundary, blind; `melt_cooling_sweep_v9` (the glass through Tg — a metric axis crossing a DYNAMICAL
> boundary, equilibrium→aging) is the FIRST axis that SMEARS — X recovered exactly 1→0.5 with mid
> levels partially aged, blind — closing separability with a positive result (a kinetic crossing
> smears; conform resolves the intermediate-X gradient, not a binary label); `glass_quench_wait_v10`
> (Cat 8, the WAITING-TIME axis) showed the X<1 glassy state is genuine non-stationary AGING (τ_α grows
> ∝ t_w, curves don't collapse), not a stationary effective-temperature state — closing the meta-SOP §2
> escalated t_w vector v4 parked twice, blind; `three_species_coupling_sweep_v11` (Cat 10, the STRUCTURE
> axis) showed the cyclic current TRACKS the wiring (rate ∝ coupling g, recovered via two independent
> channels) — closing v5's parked structure-dependence and pinning the Cat-10 current as the wiring not
> the weather, blind; `queue_load_sweep_v12` (Cat 9, Queueing — a NEW category landed) showed the
> near-capacity queue is reversible critical slowing (X=1, FDR slope 1 while relaxation time + variance
> diverge), NOT aging — closing Cat 9 with the FALSIFICATION FINDING-3 reframe (the named α_s=½ falsifier
> was a category error), blind; `observation_window_sweep_v13` (Cat 5, Kernel/τ_obs — a NEW category)
> swept the CAMERA (observation window) at fixed substrate across 32 windows and read the apparent frozen
> plateau as a camera artifact (it MELTS as the window opens; X=1 throughout) — "the problem is the camera,
> not the substrate," blind. `laser_ro_pump_sweep_v2`
> (Vertex sweep) graded MISS-with-finding (a viewer-layer dial, deferred). Earned contours
> are `[EARNED]`/`[CONTACT]` below; the rest is still cage, not surface. The ROOT OP held exactly (Banach
> damped-oscillator placed at RMS 3e-7). The READOUT headroom is where the silhouette
> buckled (see its note) — and the buckle reproduced under genuine blinding. This doc accretes (earned contours) and contracts
> (as the silhouette firms). The arrow correction is baked in: the root operation is
> inversion conforming Banach **to** the pristine substrate — never the reverse.

(Status, earned contours, and finding/buckle notes live as **blockquotes** or
`[EARNED v=…]` / `[CONTACT v=…]` tags. That is not cosmetic: `pose.py` strips exactly
those forms when it emits the blind answerer's sanitized traversal, then fail-closes if
any substrate/answer token survives. The plain-text steps below are the generic recipe —
keep them substrate-neutral, or the traversal sanitizer will refuse to pose.)

---

## INVARIANTS — hold at every step (one rule each, no branching)
- **The arrow:** substrate pristine and fixed; Banach is conformed *to* it; never the
  reverse. (Topology — kept even in dev.)
- Operate only on Banach (regenerable); never touch the substrate → collapses the
  whole modify-safety / reversibility worry-class.
- **FDR locus = universal readout** (χ vs C₀−C); category-native columns are
  cross-checks, not instruments.
- Data-path independence: the sim makes the data, analytics makes the truth.
- Blinding: the researcher-voice packet leaks no framework.
- Conform is the examinee, never the answer key.
- Falsifier tripwires armed throughout (see Readout).

---

## The traversal (sparsification modules, in order)

### 0 · ADMISSION GATE  `[EARNED v=laser_ro_nominal_v1]`
- Units present per column; C and χ dimensionless?
- Provenance / citation / license present; reproducibility hash?
- Meets the contract — admit or reject?
- "Our data" (clean ground truth) or on the contaminated hold-list?
- **[dev]** loosened — convenience data admitted. **[prod]** full contract-05.

### 1 · FRAME — camera (τ_obs) · *gate, resolve first*  `[EARNED v=laser_ro_nominal_v1]`
- τ_obs declared, or must it be derived?
- Clean intrinsic time, or ambiguous (→0 floor / →∞)?
- Window matched to the process, or is the "failure" a camera artifact?
- τ_obs sweep: labels migrate (expected) while k_frust stays invariant (required)?
- k_frust migrates with τ_obs → detection artifact → preprocess (e_i = s_i ⊕ s_{i−1})?
- Any stable window? If none → the problem *is* the camera (Cat 5).
- tau_scale to dimensionless lag — logged, reversible?
- One operating point, or already a τ_obs / control sweep?
- **[dev]** keep camera-first ordering (topology); relax precision — declare a
  convenient window. **[prod]** derive τ_obs honestly (brain/QEC placement is real work).

### 2 · SELECTION — intent × minimal-structure · *picks the live slice; most stays dark*  `[EARNED v=laser_ro_nominal_v1 — I1/vertex; separability CLEAN]` `[EARNED v=three_species_cycle_v3 — I1/Cat-10 non-reciprocal; first NON-Vertex datapoint, separability 1-vs-10 CLEAN]` `[EARNED v=glass_two_step_v4 — I1/Cat-8 Phase glassy two-step; separability 1-vs-8 CLEAN, no smear]` `[EARNED v=three_species_cycle_noise_sweep_v5 — I2/Cat-10 noise sweep on the v3 dot; noise-INDEPENDENCE of the current rate GROUNDED, blind]` `[EARNED v=community_pair_v6 — I1×2 comparison; first MINIMAL-DISTANCE 1-vs-10 separation (reciprocity-flip pair, same substrate family), CLEAN on cross-corr symmetry]` `[EARNED v=coupling_ramp_v7 — I2/metric-axis sweep; Cat-1 does NOT smear along a CONTINUOUS (coupling-strength) axis — only magnitude changes, the operating point approaches a stability edge via critical slowing, X=1 throughout]` `[EARNED v=magnet_temp_sweep_v8 — I2/metric-axis sweep CROSSING a critical point; Cat-1 does NOT smear when the axis passes THROUGH a thermodynamic critical point — X=1 every level incl. the critical middle, the band PEAKS at the middle and recovers; a phase boundary is not a dynamical-category boundary; closes the ising_equilibrium PENDING falsifier on a clean oracle]`
> **Separability datapoint (three_species_cycle_v3):** the first non-Vertex substrate
> landed CLEAN — a blind answerer separated a sustained directional CIRCULATION (Cat 10)
> from a reciprocal RING-DOWN (Cat 1) even though their autocorrelation C(τ) is the same
> damped cosine. The discriminator that did it is the cross-correlation antisymmetry
> (Cxy != Cyx); the structure did NOT smear into Vertex. n=1 cross-category test so far,
> but the 1↔10 boundary reads sharp on that observable.
> **Separability datapoint (glass_two_step_v4):** a second non-Vertex category landed
> CLEAN. A blind answerer read a two-step relaxation (a fast drop to a frozen-in plateau,
> then a stretched slow tail) as TWO populations — it did NOT collapse the slow tail to a
> single Vertex relaxation time. The discriminators: the plateau/shoulder in C(τ) (a
> separation of timescales, here ~10³×) and the stretched (β_KWW<1) tail. Cat 8 did not
> smear into Cat 1. Three categories now separate clean (1, 8, 10); the three landed
> probes were structurally far apart, so the boundary-BLUR test still wants a
> structurally-adjacent pair (HANDOFF §hypothesis).
> **Separability datapoint (community_pair_v6) — the adjacent-pair test, landed:** two
> communities one reciprocity-flip apart on the SAME 3-loop substrate family (matched/symmetric
> coupling vs cyclic/antisymmetric, same operating point) were posed in ONE blind packet with
> NO per-community class hint. The answerer placed them in DIFFERENT classes — a reversible
> relaxation with no current (Cat 1) and a sustained NESS circulation (Cat 10, ~6 turns) — and
> grounded the split on the cross-correlation SYMMETRY (Cxy=Cyx vs Cxy=-Cyx), the time-reversal
> signature, NOT on the weaker C-shape tell alone; both boundary failures avoided (no
> Vertex-collapse of the cyclic one, no false current in the matched one). **The finding:** the
> 1-vs-10 cut is TOPOLOGICALLY sharp, not metrically blurry — reciprocity is a discrete structural
> property (a coupling is symmetric or it is not; g->0 deletes the loop rather than blurring the
> class), so minimal *generating* distance still gives large *observable* distance. This reframes
> WHY the prior far-separations (1-vs-10, 1-vs-8) read clean: the reciprocity boundary cannot smear.
> It does NOT settle whether METRIC boundaries (criticality, coupling-strength continua, Cat 2)
> blur — that wants a tunable-axis probe (Cat 2 reciprocal 2-node, still GAP). Anchor held: the
> cyclic community reproduced v3's contour blind (winding ~6 turns, rate ~ rotation rate), no drift.
> **Separability datapoint (coupling_ramp_v7) — the METRIC-axis companion:** v6 showed the
> 1↔10 cut is sharp because reciprocity is DISCRETE; v7 asks whether a category smears along a
> CONTINUOUS (metric) axis. It dialed the v6 MATCHED community's coupling strength up across five
> levels toward its stability threshold. A blind answerer placed all five as the SAME kind — a
> reversible relaxation (monotone C → no oscillation; Cxy=Cyx → no current; affine FDR locus →
> equilibrium/X=1) — and read the band as a DIVERGING relaxation timescale (settling ~doubling per
> step). **No smear:** cranking the metric knob changes only the magnitude, never the kind; the
> operating point approaches a stability/critical EDGE via critical slowing. So even a continuous
> axis does not blur Cat-1 here — the category is sharp, what moves is the operating point toward a
> boundary. Reversible critical slowing (X=1) stayed cleanly distinct from glassy aging (X<1, v4)
> along the same diverging-timescale signature; the answerer read the growing FDR-locus slope as
> growing susceptibility, NOT as an X change. **Caveat now precise:** a metric axis that ACTUALLY
> smears (crosses a category boundary) still wants a substrate where the tuned axis passes through a
> critical point INTO a different class (criticality T→Tc, or the Cat-2 reciprocal pair) — still GAP.
> **Separability datapoint (magnet_temp_sweep_v8) — the boundary-CROSSING metric probe, landed:**
> v7 left one case open — a metric axis that CROSSES a critical point (not just approaches an edge).
> v8 closes it on an equilibrium-criticality oracle (the v4 analytic-correlator pattern at a
> thermodynamic critical point): a magnet's fluctuation C+χ at five temperatures straddling its
> critical (Curie) point (level 2 = critical). A blind answerer placed ALL five as the SAME kind — a
> reversible equilibrium relaxation (monotone C → no oscillation; affine FDR locus through the origin,
> SAME slope every level → equilibrium/X=1) — and read the band as a single PEAK in timescale AND
> susceptibility at the critical middle (~7×/~5× the flanks), RECOVERING on the far side. **No smear,
> and it sharpens the form of the finding:** crossing a thermodynamic phase boundary in EQUILIBRIUM
> does NOT change the dynamical KIND — a phase boundary is not an MPA dynamical-category boundary. The
> headline tooth (the ising_equilibrium PENDING falsifier, "critical slowing ≠ aging") was corrected
> blind: the huge slow critical fluctuations read as reversible critical slowing (X=1), NOT glassy
> aging (X<1, v4) — the clean X=1 counterpart along the same diverging-timescale surface. The
> cool/warm category-smear was avoided (both sides the same kind). **The caveat is now its narrowest:**
> the ONE untested case is an axis that crosses a genuine DYNAMICAL-category boundary (equilibrium →
> out-of-equilibrium AGING — the glass through its glass transition Tg, X:1→<1), which needs the
> refreshed glass substrate (null tau_env below Tg — DEFERRED.md library-refresh). First contact with
> this oracle; no anchor. The answerer independently re-derived v7's native-unit headroom limit.
> **Separability datapoint (melt_cooling_sweep_v9) — the DYNAMICAL-category-CROSSING probe; the FIRST
> axis that SMEARS:** v8 left exactly one case open — a metric axis that crosses a genuine DYNAMICAL
> boundary (equilibrium → out-of-equilibrium AGING, X:1→<1), not just a thermodynamic one. v9 closes it
> on a glass-transition oracle (the v8 construction on the v4 two-step KWW form): a supercooled melt's
> fluctuation C+χ at five temperatures cooled through its glass transition Tg (level 1 = Tg). A blind
> answerer placed the WARM levels as reversible equilibrium relaxation (single-slope FDR locus, X=1)
> and the COLD levels as out-of-equilibrium AGING (the locus BENDS — a shallower slow-segment slope
> X<1 past the plateau knee), read the TWO-step structure (plateau + stretched tail, not collapsed to
> one mode), and — load-bearing — read the band as a SMOOTH CROSSOVER of X recovered EXACTLY
> (1.00→1.00→0.83→0.63→0.50) with the MIDDLE levels at INTERMEDIATE X (partially aged), NOT a sharp
> jump and NOT a binary equilibrium/glass split. **This is the first axis tested that SMEARS** — and
> it closes the separability hypothesis with a POSITIVE result: a real dynamical-category crossing,
> being KINETIC, does smear (X drops gradually, the mid levels are partway out of balance), unlike the
> topologically-sharp reciprocity cut (v6) and the no-kind-change metric axes (v7/v8 keep the kind put,
> X=1 throughout). The teeth held: conform RESOLVES the intermediate-X gradient rather than snapping to
> a binary label. Both naive readings corrected (under-read "just slow" AND over-read "all glassy"). The
> X<1 (aging) dynamical-crossing counterpart to v8's X=1 (equilibrium) thermodynamic crossing, and the
> swept counterpart to v4's single deep-aging point. First contact with this oracle; soft anchor only
> (level 4 is a v4-family X=0.5 deep-aging point — its slow slope reproduced v4's X≈0.5, no drift).
> **Aging-sector datapoint (glass_quench_wait_v10) — the WAITING-TIME (t_w) axis; the genuine-aging-vs-
> stationary discriminator:** v4 and v9 both read the slow-mode FDT violation X<1 but neither could
> tell GENUINE AGING (non-stationary — the slow relaxation keeps slowing with the waiting time, curves
> not time-translation-invariant) from a STATIONARY effective-temperature steady state (X<1 but TTI,
> identical at every age). A single-age measurement cannot separate them; the t_w axis is the
> discriminator. v10 holds a glass-aging oracle (the v9 construction at ONE deep-quench temperature,
> swept along t_w instead of T) at five increasing ages after a quench. A blind answerer placed every
> age as a glassy out-of-equilibrium relaxation (two-step C; bent FDR locus, slow slope X=0.500 at all
> five ages — flat, the imbalance does NOT heal), and — load-bearing — read the band as GENUINE AGING:
> the slow timescale GROWS ∝ t_w (≈×2 per age step, full aging) and the C(τ) curves do NOT collapse
> (fixed-lag C climbs with age) → non-stationary → it keeps evolving, never settles. It corrected BOTH
> the "fixed/stationary steady state" read and the "it re-equilibrates with age" read. **Finding: the
> X<1 glassy state is genuine waiting-time AGING, not a stationary eff-T** — conform separates the two
> signatures cleanly (*timescale grows, imbalance flat*), closing the meta-SOP §2-escalated vector v4
> parked twice. The t_w companion to v9's temperature axis (together v4 single-point + v9 T-axis + v10
> t_w-axis map the Cat-8 aging sector on both control axes). HARD anchor: level 2 == v9 level 4 exactly
> (τ_α=150, q_EA=0.80, X=0.5; window τ_max=2250=15×150 reproduced it blind, no drift).
> **Current-sector datapoint (three_species_coupling_sweep_v11) — the STRUCTURE axis; the current is the
> WIRING not the weather:** v5 swept NOISE on the Cat-10 cyclic current and found the turnover rate FLAT
> (noise-independent); it parked the complementary claim — that the rate is SET BY THE WIRING (tracks
> g/γ). v11 opens that axis: the SAME community (the noisy frustrated N=3 cyclic non-reciprocal OU,
> `banach_frustrated`), SAME noise, five COUPLING strengths g (16× span). A blind answerer placed every
> level as a genuine directed current (the turnover-plane cross-correlations ANTISYMMETRIC, Cxy=−Cyx —
> not a reciprocal ring-down), stable at every coupling, and — load-bearing — read the turnover rate
> TRACKING the coupling: rate ∝ g (log-log slope p=1.01, recovered via TWO independent channels — the
> autocorrelation oscillation frequency AND the winding drift rate, which agree because M depends on g),
> current magnitude rising with g, no all-or-nothing onset, no instability. **Finding: the Cat-10 current
> TRACKS the wiring** (rate/affinity ∝ g, dissipation ∝ g²) — closing the meta-SOP §2-escalated
> structure-dependence vector v5 parked. With v5 (rate FLAT across noise) this pins the Cat-10 current on
> both control axes: *the current is the WIRING, not the weather* — noise tidies the loop without slowing
> it, the coupling sets how fast it spins. Secondary (consistent with v6): the current magnitude shrinks
> toward g→0 but the KIND stays Cat-10 (Cxy=−Cyx) at every sampled g>0 — the reciprocity cut is
> topologically sharp; g→0 deletes the loop rather than blurring the class. HARD anchor: level 3 (g=0.6)
> == v3/v5 exactly (rate ≈ omega = 1.04, reproduced blind, no drift).
> **Cat-9 closing (queue_load_sweep_v12) — the FINDING-3 reframe; reversible critical slowing, NOT
> aging:** Cat 9 (Queueing) is closed on its own substrate. `mm1_queue`'s named α_s=½ falsifier is a
> CATEGORY ERROR (FALSIFICATION FINDING 3): ½ is the heavy-traffic / reflected-BM time-scaling exponent
> (the C-vs-lag plane, the relaxation-time divergence), α_s is the FDR effective-temperature slope (the
> χ-vs-C plane) — different planes; and the raw cells are window-limited near ρ→1. So v12 builds an M/M/1
> ORACLE (the v8 pattern) and poses the reframe: a load-sweep toward the capacity wall ρ=1. M/M/1 is a
> reversible birth-death process → equilibrium FDT → X=1 EXACTLY at every load (a theorem). A blind
> answerer placed every load as a reversible in-balance relaxation (FDR locus a single straight line of
> slope 1, X=1 — never bends), read the band as CRITICAL SLOWING toward capacity (relaxation time ~×500
> and variance ~×650 both DIVERGE) while the FDR slope stays pinned at 1, and — the FINDING-3 point —
> explicitly separated the diverging power-law quantities (the plane the ½ exponent lives in) from the
> flat FDR slope (X=1). **Finding: the near-capacity queue is reversible critical slowing (X=1), not
> aging** — closing Cat 9 with the reframe (the α_s=½ test was the wrong plane). The X=1 reversible
> counterpart to v4/v9/v10's X<1 aging; the QUEUEING counterpart to v8's thermodynamic-criticality X=1.
> First contact (soft kinship to v7/v8 by KIND, no hard anchor). PARKED (framework/cdv1 matter, not a
> conform call — stays in FALSIFICATION FINDING 3): cdv1 §Load-handling maps heavy-traffic M/M/1 into the
> s-regime (aging X<1), but reversibility forces X=1 — this pass establishes the X=1 substrate truth; the
> s-regime reconciliation is out of scope for the blind pass.
> **Cat-5 landing (observation_window_sweep_v13) — the camera/τ_obs category; the problem is the CAMERA,
> not the substrate:** Cat 5 (Kernel/τ_obs) lands — the kernel pre-gate's OWN job (WORKFLOW §E; RFC-S
> §0.2 "τ_obs is the camera"): is an apparent character a property of the SUBSTRATE or of the OBSERVATION
> WINDOW? v13 is the structural complement to every prior sweep — where v5/v7/v8/v9/v10/v11/v12 moved a
> SUBSTRATE knob, v13 moves the CAMERA (τ_obs, the observation-window length) at FIXED substrate, across
> 32 windows. The substrate is one fixed two-timescale EQUILIBRIUM relaxation (fast + slow, X=1); at short
> windows the slow mode hasn't decayed → an apparent frozen plateau that MIMICS a glass q_EA. A blind
> answerer read it as a CAMERA artifact, not an intrinsic stuck component, on two grounds: (a) the
> apparent plateau MELTS to zero as the window opens (~0.63→0 across the 32 windows — the slow mode just
> under-resolved), and (b) the FDR locus is slope ≈1 (X≈1) at every window (equilibrium / in balance —
> NOT a glass). It verified the SIGNAL is fixed (the camera changes, not the substrate), found the matched
> window, and corrected the "permanently stuck / non-ergodic" worry. **Finding: the apparent non-ergodicity
> is a CAMERA (observation-window) artifact (Cat 5), not intrinsic** — the camera-artifact FOIL to
> v4/v9/v10's intrinsic glass (there q_EA is real, X<1, does NOT melt; here it is a window artifact, X≈1,
> melts). RFC-S: as τ_obs moves the reading auto-remaps along the RG-flow trajectory while the substrate's
> intrinsic content is RG-invariant — exactly what landed. First contact (foil to v4, no hard anchor). All
> 5 cage_edges avoided.
> **Method break + fix (2026-05-26, Ron caught it):** v13's FIRST oracle set χ=(C0−C)/T analytically (FDT
> IMPOSED) → the FDR locus was the identity by construction → the X=1 reading was TAUTOLOGICAL (data-path
> independence violation). Rebuilt: C and χ are now TWO INDEPENDENT Monte-Carlo measurements (fluctuation
> ensemble vs separate perturbation ensemble), so FDT/X≈1 EMERGES within MC noise (the corrected blind
> answerer read slope 0.997±0.014 and correctly PARKED "whether X is exactly 1 — below resolution," i.e. an
> emergent FDT, not an identity). New standing rule: WORKFLOW §1 **response-independence corollary** —
> never set χ=(C0−C)/T by fiat. v4/v8/v9/v10/v12's analytic oracles carry a limitation note (their X legs
> were imposed-not-tested; their C-only findings — band shape, two-step, melt, aging direction — stand).
- *Question:* researcher's words; nominal-check / placement / comparison / headroom /
  "why"? baseline expectation? one channel or several?
- *Intent:* which of I1–I5? more than one, in what order? supported at this dev stage?
  data shape agrees (point ↔ I1/I5; spanning ↔ I2)?
- *Structure:* minimal structure (the gate); nodes/edges, vertex/edge/cycle; reciprocal
  or non-reciprocal; **current-bearing?** (feeds the current-gate); category (1–10);
  substrate's field (voice/units); native observables, and which one they're watching.
- *Separability (open Wall-test):* does structure land clean or **smear**? — i.e. is this
  axis a valid modular cut at all?
- **[dev]** downstream intents (I1/I5) always; **I2 (sweep/migration) admitted in dev WHEN
  built as stitched isolated placements** — each point an independent I1 fit + one band
  readout, which keeps the fit intent-independent and a MISS localizable (meta-validity P).
  **[prod]** the full I2 migration fit (trajectory machinery reaching into the fit's scope).

### 3 · ROOT OPERATION — inversion conforms Banach to the substrate · *the measurement; subsumption hub*  `[EARNED v=laser_ro_nominal_v1 — 1-param placement EXACT on a vertex]`
- Conform Banach to the (working) substrate — the fit *is* the measurement.
- Placement (chit)? regime? confidence/residual? which observable constrained it?
  γ_AB constrained or free?
- 1-param chit enough for this intent, or the 5-vector refinement?
- *Lens/map:* region of interest; the fitted TranslationField (substrate-native ↔
  canonical); forward-only; round-trip residual (I4); where the asymptotes sit relative
  to the fit (the coordinates that give headroom meaning).
- *The fitted Banach:* which family member, how deformed = **the character**; deviation
  from canonical Banach.
- **[dev]** keep the arrow (winding); relax fit precision/tolerances. **[prod]**
  evidence-grade fit; lens round-trip enforced.

### 4 · GATES — booleans that connect/disconnect whole sub-modules  `[CONTACT v=three_species_cycle_v3 — current-gate OPENED; two-frame sector reached & AGREE, blind]` `[CONTACT v=glass_two_step_v4 — in-family/identifiability gate: two-step 5-vector (q_EA, β_KWW, X) read from ONE (C,χ); aging X<1 separated from equilibrium X=1, blind]` `[CONTACT v=three_species_cycle_noise_sweep_v5 — current-gate "noise-independent?" sub-question CLOSED: current rate flat to <6% over 20× noise, blind]` `[CONTACT v=community_pair_v6 — current-gate exercised on BOTH branches in one pass: PRESENT (cyclic, self-frame defined) vs ABSENT (matched, Cxy=Cyx, no self-frame) — the gate's boolean read correctly both ways, blind]`
> **First-contact finding (glass_two_step_v4):** the **grain/in-family → identifiability**
> gate reached its first genuinely multi-timescale substrate. A blind answerer recovered
> the two-step structure from a single (C, χ) pair: the plateau height q_EA≈0.69, the
> stretched-tail exponent β_KWW≈0.63, and — the teeth — the slow-mode FDT-violation
> X≈0.50 read off the TWO-SLOPE FDR locus (slope ≈1 on the fast branch up to the plateau
> knee, then slope X<1 on the slow branch). C(τ) ALONE is a slow two-step decay either way;
> the response χ read against C is what separates "out-of-equilibrium aging" (X<1) from
> "equilibrated but slow" (X=1). The answerer avoided the equilibrium-collapse trap — the
> clean X<1 counterpart to the parked `mm1_queue` tension (FALSIFICATION.md FINDING 3: there
> the truth was reversible critical-slowing X=1 and the trap was OVER-claiming aging). The
> honest park is across a COLLAPSED AXIS: a stationary window cannot say whether X<1 is
> genuine waiting-time (t_w-dependent) aging or a stationary effective-temperature — and the
> answerer split a second collapsed-axis park the seal under-specified ("not AT arrest" is
> groundable, but distance/direction TO arrest needs a control-axis sweep).
> **First-contact finding (three_species_cycle_v3):** the **current present?** gate fired
> for the first time (a single-mode Vertex substrate structurally cannot reach it). With a
> current present, the self-probe frame IS defined, and a blind answerer read the system in
> TWO independent frames — the fluctuation-response locus (a loop off the equilibrium line)
> and the winding/antisymmetry frame — which AGREED that a sustained directional current
> flows. Agreement = pass (§J); the sector is now demonstrated, not just cage. Note: the
> answerer grounded agreement via locus-area-vs-winding-drift, NOT via the formal affinity/
> TUR-factor scalars — those are now in-slice groundable (the data carries phiMean/phiVar)
> but went unused, so the formal TUR-floor (T>=1) check is reachable-but-unexercised. The
> in-slice winding ensemble that makes this whole sector groundable from ONE operating point
> is a consequence of the symmetric-boundary rule (WORKFLOW §4).
> **Sweep finding (three_species_cycle_noise_sweep_v5):** the current-gate's last sub-question
> — *affinity drive/noise-independent?* — closed. A noise sweep (5 points, 20× in D, fixed
> structure) of the v3 dot showed the winding RATE / per-cycle directedness FLAT to <6% blind,
> while the two-point structure was D-invariant and Cxy=−Cyx survived every level: the current
> is wiring-set, not noise-driven (v3's one honest park, now grounded across the axis it could
> not see). The teeth here are the FIRST moment (drift); the SECOND moment (Var(J)/TUR factor)
> is estimator-noisy/non-monotone, and the blind answerer PARKED it — independently re-deriving
> `docs/deferred-for-auditor.md` Entry 2 (a measurement-quality caveat, not a conform defect:
> expose the spread's uncertainty at the viewport; the source fix lives in mpa-central).
- **grain present?** → *Identifiability:* which params identifiable vs mush (bootstrap);
  trust a param iff in_domain ∧ assessable ∧ identified; X a real FDT-violation or raw-slope?
- **current present?** → *k_frust / two-frame:* self-probe frame defined? where both compute,
  do they agree (disagreement = falsifier)? affinity drive/noise-independent?
- **in-family?** (fit residual / per-channel S/N) → deviation *readable* (within character)
  or out-of-domain?
- C normalizable, or the unnormalized-C pathology?
- **[dev]** gates may be forced (skip bootstrap, ignore out-of-family) **but logged**.
  **[prod]** gates live; n_boot paid; out-of-family honored.

### 5 · READOUT — functions of the fit, not free decisions  `[CONTACT v=laser_ro_nominal_v1 — verdict EARNED; headroom BUCKLED]` `[CONTACT v=three_species_cycle_noise_sweep_v5 — FLAT-band readout: a band whose answer IS its flatness (rate noise-independent), read blind; 2nd-moment channel honestly parked]` `[CONTACT v=coupling_ramp_v7 — DIVERGING-band readout: critical slowing toward a stability edge, read blind; two-sided headroom grounded in DIRECTION+rate (the shrinking spectral gap) but the ABSOLUTE distance in native control units stays parked]`
> **First-contact finding (laser_ro_nominal_v1):** the *verdict* (nominal vs marginal)
> and *one-sided* headroom (toward the nearest data-visible asymptote, here ζ→1
> critical/sluggish) are functions of a single fit. The *two-sided* headroom — the part
> that actually corrects the researcher's naive worry — is NOT: it needs the framework
> Q(χ̂) band, which one operating point does not carry. So SELECTION's single-point
> collapse and READOUT's two-sided headroom are in structural tension. Resolve by either
> injecting the analytic Banach band (overlay) as the reference, or posing a sweep vertical.
> **Confirmed under blinding (re-run 2026-05-24):** an isolated answerer with no access to
> the seal independently refused the two-sided claim — the gap is structural, not an
> author artifact. The answerer's `not_grounded[]` is the channel that surfaced it
> (WORKFLOW §6 answerer contract).
> **Graded 2026-05-25 (MISS-with-finding, meta-validity P):** the escalated sweep
> (`laser_ro_pump_sweep_v2`) ran blind. The *mechanical* aim worked — two-sided headroom
> became groundable (the answerer named both walls of the band), a real READOUT capability.
> But the bottom-line verdict inverted: "healthiest" is not Jacobian-computed; it flips on a
> health-metric (response-crispness vs damping-margin) the blind packet never supplied. The
> placements + band shape + the v1 anchor all reproduced — conform did NOT break, and the
> MISS matched no cage_edge. **Reclassified (2026-05-25): the verdict-layer inversion is a
> viewer-layer concern, not a conform teeth-defect to fix by re-posing.** "Healthiest" is a
> researcher *utility lens* over the computed band — a **dial**, not a verdict: conform
> computes and exposes the whole band, the (inert) viewport presents it and exposes the lens
> as a researcher control; the reading lags the researcher's choice, it is not led or
> inferred. A verdict the freeze cannot compute is the tell that the choice is a dial.
> Deferred to `docs/deferred-for-auditor.md` Entry 1 (picked up at the auditor pivot). The *mechanical*
> two-sided-headroom groundability stands as a conform result; whether it promotes to
> `[EARNED]` once carved free of the verdict lens is a gated call parked alongside. See
> `earned/laser_ro_pump_sweep_v2/RESULT.md`.
> **Two-sided-headroom, sharpened (coupling_ramp_v7):** a metric-axis sweep toward a stability
> edge grounded the two-sided headroom blind — but only its QUALITATIVE / observable part. The
> answerer read the DIRECTION (heading toward an instability) and the RELATIVE rate of approach
> (the relaxation timescale ~doubling per step → the spectral gap shrinking) off the band. The
> ABSOLUTE distance-to-edge **in the researcher's native control units is NOT closeable even with
> a sweep** — it needs the control-axis magnitudes (the model parameters), which blinding correctly
> strips. So the closeable headroom lives in the OBSERVABLE (the spectral gap / relaxation rate),
> not in native control units; the answerer parked the native-unit distance, the same honest channel
> that surfaced v1's limit. This refines the escalated "subdivide into a sweep" fix (meta-SOP §2):
> the sweep DOES close two-sided headroom, but "closed" means relative/observable, not absolute-native.
- *Verdict:* interior of the open interval (nominal) vs departing toward an asymptote;
  headroom = distance to nearest asymptote in native units; which asymptote binds + direction;
  is the naive worry corrected?
- *View:* the intent-selected view; an **artifact (shot/overlay) read by inspection**, not a
  boolean; native / canonical / paired frame; every rendered property maps to data; parallax
  if multichannel.
- *Kill-check:* boundary *attained* at a finite point (NaN tripwire)? X > 1, or X exactly 0/1?
  k_frust where structure forbids it? structure mismatch? — MATCH / MISS / KILL.
  - *Regime-zero ≠ boundary-attained:* a quantity that is zero **by regime** (the model
    degenerating to a simpler regime at some operating points) is NOT a boundary of the
    open interval being attained — it is **not** a KILL. The tripwire fires only when the
    *invariant that should stay interior* reaches 0/1/∞ at a finite point. Read the
    invariant that **stays finite near the asymptote**, not a parameterization that
    diverges as the regime degenerates (a blowing-up parameterization manufactures false
    boundary-attainment).
- **[dev]** view produced as a plumbing check; verdict/kills **not** treated as evidence or
  framework-falsification. **[prod]** a kill means MPA is invalid on this substrate here.

### 6 · ROUTE & DEPOSIT — close the loop
- Result trips a cage_edge → route to the neighbor category, re-pose?
- Did it smear (feed the separability Wall-test)?
- Deposit one residue line (bound + headroom) — into the HANDOFF ledger (meta-SOP §3).
- **[dev/prod]** same — the silhouette accretes regardless of phase.

---

## PHASE INTERFACE — the thin seam that keeps dev/prod modular
The dev/prod cut is a real sparsification only if its interface is explicit: a
**relaxation ledger** — for every constraint off in dev, one line naming *what's off*
and *its revert condition*. Standing entries:
- pristine data-handling — **OFF in dev** (data may be cleaned, **reference-blind only**,
  never toward Banach); revert: prod feeds pristine data, no-touch re-installed.
- evidence-status — **OFF in dev** (dev claims nothing; plumbing only); revert: prod
  outputs are evidence, kills are framework-falsifications.
- blinding rigor — **relaxed in dev** (author==answerer tolerated); revert: prod runs a
  genuinely blind answerer.
- identifiability — **n_boot=0 in dev**; revert: prod pays the bootstrap.
- I2 / migration intent — **admitted in dev WHEN built as stitched isolated placements**
  (each point an independent I1 fit + one band readout, MISS localizable); revert: prod
  runs the full migration fit with trajectory/band machinery in the fit's scope.

Without this ledger, dev debt smears into prod and the phases hit the Wall along the
time axis. Kept across both phases (topology, never relaxed): the arrow, camera-first
ordering, the intent→traversal→view spine, the compute→artifact→view seam, cage adjacency.
