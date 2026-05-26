# HANDOFF — conform block-in (the baton)

Mutable state only. This file carries **what changes pass-to-pass** — the resistance
line, the ledger, the open hypothesis, the substrate reference, and the current
state / next move. The *stable method* lives elsewhere; read those first if new:

- **PIPELINE.md** — the object (conform's data-prep silhouette).
- **WORKFLOW.md** — the pass-SOP (how to run one pass; rules of the game; the A–P box).
- **meta-SOP.md** — the evolution governance (how a verdict evolves the artifacts +
  picks the next question; **start there: §0 on-entry reconcile**).
- **HANDOFF.md** (this file) — the baton.

Full design + why: memory `project_conform_blockin_apparatus`. Repo context:
mpa-conform/CLAUDE.md, mpa-central/SYSTEM_OVERVIEW.md.

---

## Resistance line  [stable]
Reaching for the tau_obs sweep, the bootstrap cost, the full characterization
tensor, or the 10-category protocol as a *plan*? Stop — you're painting scales.
One brittle vertical at a time; the silhouette precipitates, it is not designed.

## Open hypothesis under test  →  CLOSED (positive, post v9)
- **10-category separability** — *do real substrates land in one category cleanly, or smear across
  several?* — is **answered.** Nine verticals (v1/v2 Vertex, v3+v5 Cat-10, v4 Cat-8, v6 the 1⊕10
  reciprocity-flip pair, v7 Cat-1 metric-axis sweep, v8 Cat-1 metric-axis CROSSING a thermodynamic
  critical point, v9 the Cat-1→8 DYNAMICAL-category crossing) bound the answer on both sides:
  - **Sharp (no smear) on every boundary that is NOT a dynamical-kind crossing:** the *discrete*
    reciprocity cut 1↔10 is TOPOLOGICALLY sharp (v3/v6 — a coupling is symmetric or it is not; g→0
    deletes the loop, doesn't blur the class); a *metric* axis *within* a category does not smear
    (v7 — coupling strength dialed to the stability edge stays Cat-1, X=1, only the magnitude/timescale
    diverges → critical slowing); a *metric* axis CROSSING a *thermodynamic* critical point in
    equilibrium does not smear (v8 — temperature through Tc stays Cat-1, X=1, the band peaks-and-
    recovers; a phase boundary is **not** an MPA dynamical-category boundary).
  - **Smeared (the one place it smears) — a genuine DYNAMICAL-category crossing (v9):** cooling a melt
    through its glass transition Tg (equilibrium → out-of-equilibrium AGING, X:1→<1) is a SMOOTH
    KINETIC CROSSOVER — X drops 1→1→0.83→0.63→0.50 across the cooling range and the middle levels sit
    at intermediate X (partially aged), not a sharp jump. **v9 is the first axis tested that smears.**
  **The resolution.** Categories are separable as KINDS; the BOUNDARIES between kinds come in two
  flavours — *topological/thermodynamic* boundaries stay sharp, a *kinetic* dynamical-category crossing
  smears — and, the teeth that mattered, **conform RESOLVES the smear** (places the intermediate
  operating points at intermediate X — partially aged — rather than snapping to a binary
  equilibrium/glass label). The separability question that drove the loop for nine passes is closed
  with a positive result. *(The next hypothesis is human-picked — see "Pick up here". Candidate
  frontiers: depth (the escalated t_w genuine-aging vector), the cheap v5 structure-sweep, the Cat-9
  reframe, or breadth into the untouched categories.)*

## Vertical ledger  [append 1 line/pass; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. RECLASSIFIED 2026-05-25: verdict-lens inversion is a VIEWER-LAYER concern (researcher utility-lens over the computed band), NOT a teeth-defect → deferred to docs/deferred-for-auditor.md Entry 1, NOT re-posed as v3. earned/.
three_species_cycle_v3| 10 (Non-Recip)   | CLEAN         | sustained NESS current ω/γ≈1.04, ~6 loops/run, far from the ω→0 equilibrium edge; Δ→next: quantitative noise-INDEPENDENCE needs a noise sweep | BLIND MATCH. First contact with the current-gate / two-frame sector (Vertex structurally cannot reach it): a blind answerer read the current in TWO frames (FDR-locus loop + winding/antisymmetry) and they AGREE; placed it STABLE; corrected the naive "noise-driven wobble" worry. CAT-1 vs CAT-10 SEPARATED CLEAN — same damped-cosine C as a ring-down, but the answerer caught Cxy=-Cyx and did NOT collapse to Vertex (separability's first non-Vertex datapoint, no smear). Re-bounded mid-session under the new symmetric-boundary rule (WORKFLOW §4): the in-slice winding ensemble made affinity/TUR/two-frame groundable from ONE point. Note: answerer grounded agreement via locus-vs-winding, NOT the formal affinity/TUR scalars (in-slice but unused → reachable-but-unexercised). Noise-independence parked = a COLLAPSED-AXIS park (legit ADVANCE vector), not under-provisioning. earned/.
glass_two_step_v4     | 8 (Phase/glassy) | CLEAN         | two-step relaxation: plateau q_EA≈0.69, stretched β_KWW≈0.63, ~10³× timescale separation; slow-mode FDT violation X≈0.50 (T_eff/T=2), interior — headroom 0.5 each side (X→1 re-equilibration, X→0 arrest); Δ→next: genuine waiting-time aging vs stationary eff-T needs a t_w sweep | BLIND MATCH. First Cat-8 vertical; first contact with the aging-FDR / two-step sector (Vertex structurally cannot reach it). The blind answerer read the TWO-step structure (did NOT collapse to a single Vertex relaxation — 1↔8 separated CLEAN, no smear) and read the slow-mode FDT violation X<1 off the TWO-SLOPE χ-vs-C locus (fast slope≈1, slow slope=X) — AVOIDING the equilibrium-collapse trap (cage_edge 2). This is the clean X<1 counterpart to the parked mm1 FINDING-3 tension (there X=1, trap was over-claiming aging; here X<1, trap is reading it as equilibrium). Not hollow (out-of-eq grounded on the locus, not guessed); no KILL. Park = a COLLAPSED-AXIS park (t_w sweep), and the answerer SPLIT a second park the seal under-specified: "not AT arrest" groundable, distance-TO-arrest not. earned/.
3sp_noise_sweep_v5    | 10 (Non-Recip)   | CLEAN         | current rate FLAT to <6% over a 20× noise range (drift~ω/γ=1.04, affinity~13 nats/cyc); 2-point structure D-invariant; Cxy=-Cyx at every level; Δ→next: structure-dependence (rate TRACKS g/γ) needs a STRUCTURE sweep | BLIND MATCH. 2nd I2 sweep. SPENDS v3's owed noise-INDEPENDENCE vector → now GROUNDED across the swept axis (v3 could only answer the "calm the environment" counterfactual structurally; this answers it empirically). Anchor (level 3 = v3's D=0.1) reproduces v3: |Cxy-Cyx|=0.66 exact, rate~ω. Blind read was MORE conservative than the seal on the ONE noisy axis: the answerer PARKED "what noise changes" because the 2nd moment (Var(J)/TUR factor) is estimator-noisy/non-monotone — independently re-deriving deferred-for-auditor Entry 2 (caveat real, not a freeze artifact; a measurement-quality flag, NOT a conform defect or an MPA falsification). No cage_edge, no KILL, not hollow. earned/.
community_pair_v6     | 1⊕10 (recip-flip pair) | CLEAN   | TWO communities one reciprocity-flip apart on ONE substrate family (matched/symmetric ⟨σ⟩=0 vs cyclic/antisymmetric ⟨σ⟩=2.16, same op-point); both placed independently, separated on cross-corr SYMMETRY (Cxy=Cyx vs Cxy=-Cyx); Δ→next: METRIC-boundary blur (Cat 2 coupling continuum) still unprobed | BLIND MATCH (two-sided). The FIRST minimal-GENERATING-distance 1↔10 separation (every prior separation was structurally FAR). Answerer placed community 0 = reversible relaxation/no current (Cat 1) and community 1 = NESS circulation ~6 turns (Cat 10), grounded the split on the cross-correlation symmetry (time-reversal signature) NOT C-shape alone, and avoided BOTH cage_edges (no Vertex-collapse of the cyclic one, no false current in the matched one). Naive worry corrected (turnover≠instability; both stable). ANCHOR: community 1 = v3 exactly, reproduced blind (winding ~6 turns, rate ~ω) — no cross-pass drift; answerer didn't know it was an anchor. FINDING: the 1↔10 cut is TOPOLOGICALLY sharp (reciprocity is discrete — no continuous knob smears the class; g→0 deletes the loop, doesn't blur it), which reframes WHY prior far-separations read clean. Does NOT settle METRIC-boundary blur (criticality/coupling-continua/Cat 2). No KILL, not hollow. earned/.
coupling_ramp_v7      | 1 (Vertex, metric sweep) | CLEAN | v6's MATCHED community with coupling g_s dialed UP across 5 levels toward the stability edge (g_s→γ): all 5 are reversible Cat-1 relaxation (monotone C, Cxy=Cyx, affine FDR X=1); τ_slow DIVERGES 1.43→20 (critical slowing), gap 0.70→0.05; Δ→next: a metric axis that ACTUALLY smears (crosses INTO another class) still wants criticality T→Tc or the Cat-2 pair (GAP) | BLIND MATCH. The METRIC-boundary-blur companion to v6: Cat-1 does NOT smear along a CONTINUOUS axis — cranking coupling changes only MAGNITUDE (timescale + susceptibility diverge), never KIND (no oscillation/current/aging onset; X=1 throughout). The operating point approaches a stability/critical EDGE via critical slowing (reversible, X=1 — the clean counterpart to v4's aging X<1). The answerer avoided ALL false-onset misreads incl. the subtle one: it read the GROWING FDR-locus slope as growing SUSCEPTIBILITY, not as X<1 aging (3-way cross-check slope≈chi_inf≈tau_slow). ANCHOR: level 1 (g_s=0.6) = v6 community 0, reproduced blind (τ≈2.5, FDR slope≈1.56, Cxy=Cyx) — no drift. FINDING (sharpens v1/v2): a sweep grounds the QUALITATIVE/relative two-sided headroom (approach direction + rate = the shrinking spectral gap) but the ABSOLUTE distance-to-edge in NATIVE control units is NOT closeable — it needs the control magnitudes that blinding strips; closeable headroom is in the observable (the gap), not native units. No KILL, not hollow. earned/.
magnet_temp_sweep_v8   | 1 (Vertex, metric sweep CROSSING a critical point) | CLEAN | a magnet's fluctuation C+χ at 5 temperatures straddling its critical (Curie) point (level 2 = critical), on a clean equilibrium-criticality ORACLE; all 5 placed as reversible Cat-1 equilibrium relaxation (X=1, affine FDR locus thru origin, SAME slope every level incl. the critical middle); band PEAKS at the middle (τ_corr 10→32→50→25→6.9, χ_static 1.4→3.5→5.0→2.9→1.0, ~7×/~5×) and RECOVERS on the far side; Δ→next: the genuine DYNAMICAL-category crossing (equilibrium→aging, X:1→<1) = glass through Tg, still GAP (null tau_env) | BLIND MATCH (two-sided). The boundary-CROSSING companion to v7's boundary-APPROACH, and the X=1 reversible counterpart to v4's X<1 aging along the same diverging-timescale surface. CLOSES the ising_equilibrium PENDING falsifier ("critical slowing ≠ aging") on a clean substrate: the huge slow critical fluctuations read blind as reversible critical slowing (X=1, locus stays affine at the critical level), NOT glassy aging. Cool/warm category-smear AVOIDED (both sides same kind → a thermodynamic phase boundary is NOT a dynamical-category boundary). Built the oracle because the library ising_equilibrium MC cells (L=32) don't cleanly exhibit X=1 across the transition (ordered phase plateaus at frozen m², critical cell noisy, intended X-read routes through conform's fit_kww5 = examinee). FIRST CONTACT — no anchor; answerer independently re-derived v7's native-unit headroom limit (absolute distance-to-Tc not blind-closeable). No KILL, not hollow. earned/.
melt_cooling_sweep_v9  | 1→8 (DYNAMICAL-category crossing: equilibrium→aging) | CLEAN (SMEARS) | a supercooled melt's two-step C+χ at 5 temperatures cooled THROUGH its glass transition Tg (level 1 = Tg), on a glass-transition ORACLE (v8 construction on the v4 two-step KWW form); warm levels placed reversible-equilibrium (single-slope FDR locus, X=1), cold levels out-of-equilibrium AGING (locus BENDS, slow-segment slope X<1 past the plateau knee); X band recovered EXACTLY 1.00→1.00→0.83→0.63→0.50 — a SMOOTH CROSSOVER, mid levels at intermediate X (partially aged); plateau deepens 0.05/0.03/0.50/0.65/0.78, τ_α grows ~150×; Δ→next: separability CLOSED — next hypothesis human-picked | BLIND MATCH (two-sided). The FIRST axis tested that SMEARS — closes the separability hypothesis with a POSITIVE result: a genuine dynamical-category crossing, being KINETIC, smears (unlike the topologically-sharp reciprocity cut v6 and the no-kind-change metric axes v7/v8), and conform RESOLVES the intermediate-X gradient rather than snapping to a binary equilibrium/glass label. The X<1 aging dynamical-crossing counterpart to v8's X=1 equilibrium thermodynamic crossing; the swept counterpart to v4's single deep-aging point. Both naive readings corrected (under-read "just slow" AND over-read "all glassy"). FIRST CONTACT on this oracle; soft anchor only (level 4 = v4-family X=0.5 deep-aging point, slow slope reproduced v4's X≈0.5, no drift). Built the oracle (not the library glass MC cells: null tau_env below Tg, X-read routes through conform's fit_kww5 = examinee). No KILL, not hollow. earned/.
```

## Substrate coverage map  [the ceiling — which categories have a clean-truth substrate]

The reserve mapped onto the 10-category taxonomy. **This is what is *authorable*, NOT what
is *done*.** **"Clean truth"** = analytic ground truth computable *without conform* (the
answer-key gate). Status: **READY** (clean substrate in hand → a vertical *could* be
authored) / **PARTIAL** (substrate exists but truth partial/off-category) / **GAP** (no
clean-truth substrate). A separate **⟳ LANDED** tag marks a category with an actually-run,
documented vertical in `earned/` (so far: Cat 1 `v1`, Cat 10 `v3`, Cat 8 `v4`; the Cat 1
sweep `v2` ran but graded MISS-with-finding → no contour). So "READY" means a substrate
sits waiting, *not* a test completed.

**This table is a SNAPSHOT to be verified at the source, not ground truth (meta-SOP §0
readiness gate).** It caches a derived view *across a repo boundary*, so it rots — the
authoritative truth lives in `mpa-central/library/` (does the clean substrate exist, in the
claimed shape?) and `mpa-central/FALSIFICATION.md` (have the substrate's teeth been
adjudicated? — a substrate can be READY yet have parked / mis-specified teeth, as Cat 9
`mm1_queue` does). Before a row's tag is acted on, reverify it there: the map *indexes*, the
source *adjudicates*. Standing caveat beyond that: the taxonomy is itself the open
separability **hypothesis** (category *meanings* are a working reconstruction, provisional).

| # · category | reserve status | landed? | clean-truth substrate(s) in hand |
|---|---|---|---|
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED**; **⟳ v6** (matched community = Cat-1, one half of the reciprocity-flip pair); **⟳ v7** (the matched community swept along its coupling-strength axis — metric-blur: Cat-1 stays sharp, critical slowing toward the edge); **⟳ v8** (metric axis CROSSING a thermodynamic critical point — Cat-1 stays sharp through Tc, X=1, band peaks-and-recovers; a phase boundary is not a dynamical-category boundary) (v2 — MISS-with-finding, NOT landed) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓, banach_frustrated *matched/symmetric control* ✓ (+ its coupling-strength axis, v7), equilibrium-criticality oracle ✓ (v8, an analytic stand-in for ising_equilibrium across Tc) — *deep* |
| 2 · Edge (coupled pair) | PARTIAL | — | two_temp_ou is 2 coupled OU but exposed as single-relax+X; want a clean *reciprocal* 2-node |
| 3 · Subgraph (motif) | **GAP** | — | banach_frustrated is a 3-mode but *non*-reciprocal (→ cat 10); a reciprocal motif / Harary triad has no clean-truth data yet |
| 4 · Meta-Ledger | **GAP** | — | abstract (FDT/entropy accounting); no substrate identified — may be an *instrument* test, not a substrate |
| 5 · Kernel (camera/τ_obs) | PARTIAL | — | no dedicated camera-artifact substrate; probe via kww_oracle's two timescales + a τ_obs sweep |
| 6 · Encoding | **GAP** | — | no dedicated substrate; the `e_i=s_i⊕s_{i-1}` preprocessing needs a spin process with clean truth |
| 7 · Capacity | PARTIAL | — | mm1_queue's ρ→1 saturation *is* a capacity limit — repurpose-able; no dedicated capacity substrate |
| 8 · Phase (glassy/critical) | **READY+** | **⟳ v4 LANDED** (BLIND MATCH 2026-05-25; aging-FDR / two-step sector, X<1); **⟳ v9 LANDED** (BLIND MATCH 2026-05-25 — the Cat-1→Cat-8 DYNAMICAL crossing, equilibrium→aging through Tg, landed on a clean glass-transition oracle: X SMEARS 1→0.5 smoothly, the first axis tested that smears). The **equilibrium-criticality** side is touched from the Cat-1 side by **v8** (X=1 across Tc — a phase boundary is not a dynamical-category boundary; closed the ising_equilibrium PENDING falsifier) | kww_oracle ✓ (full 5-vector glassy fingerprint, rung-5 validated), ising/ou equilibrium ✓ (X=1; across-Tc via the v8 oracle), glass-transition oracle ✓ (v9 — the v8 construction on the v4 two-step form, X(T) crossover encoded directly as the slow-mode FDT ratio); aging-glass-below-Tg in the LIBRARY still PARTIAL (library glass cells have null `tau_env` below Tg — DEFERRED.md refresh; the v9 oracle stands in, exactly as v8 did for ising across Tc) |
| 9 · Queueing | **READY** (named falsifier mis-spec) | — | mm1_queue ✓ (exact stationary ρ/(1−ρ)); BUT its named α_s=½ falsifier is a category error (FALSIFICATION.md FINDING 3) — a conform vertical here needs the **critical-slowing-vs-aging reframe** (reversible X=1 vs the v4 X<1 aging), not the ½ test |
| 10 · Non-Reciprocal (current/k_frust) | **READY+** | **⟳ v3 + v5 + v6 LANDED** (v3 BLIND MATCH — current/two-frame sector; v5 BLIND MATCH — noise sweep, rate noise-INDEPENDENCE grounded; v6 BLIND MATCH 2026-05-25 — the cyclic community = Cat-10 half of the minimal-distance 1↔10 pair, anchored to v3) | banach_frustrated ✓ (exact 3-mode current, affinity/TUR; + its symmetric *reciprocal control* now exists as the Cat-1 contrast, v6); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 4 categories are
READY (1, 8, 9, 10), ~3 PARTIAL (2, 5, 7), 3 GAP (3, 4, 6). *Work-wise*, **8 verticals have
landed contours** — v1 (Vertex/Cat 1), v3 (Cat 10, non-reciprocal), v4 (Cat 8, Phase/glassy),
v5 (Cat 10 noise sweep), v6 (the 1⊕10 reciprocity-flip PAIR — Cat 1 *and* Cat 10 at minimal
generating distance), v7 (Cat 1 metric-axis sweep — coupling strength toward the stability edge),
v8 (Cat 1 metric-axis sweep CROSSING a thermodynamic critical point — X=1 through Tc, band
peaks-and-recovers), v9 (the Cat-1→8 DYNAMICAL crossing — equilibrium→aging through Tg, X smears
1→0.5); v2 (Vertex sweep) graded MISS-with-finding (deferred to the viewer layer, landed no
contour). So landed evidence is now EIGHT records across THREE categories
(`earned/laser_ro_nominal_v1/`, `earned/three_species_cycle_v3/`, `earned/glass_two_step_v4/`,
`earned/three_species_cycle_noise_sweep_v5/`, `earned/community_pair_v6/`, `earned/coupling_ramp_v7/`,
`earned/magnet_temp_sweep_v8/`, `earned/melt_cooling_sweep_v9/`) plus one documented MISS. v3 reached
the current/two-frame sector; v5 closed its noise-independence sub-question; v4 reached the aging-FDR /
two-step sector; v6 landed the first minimal-distance 1↔10 separation (topologically sharp); v7 showed
Cat-1 does not smear along a continuous coupling axis (critical slowing toward an edge); v8 showed
Cat-1 does not smear when the axis CROSSES a thermodynamic critical point (X=1 through Tc) and closed
the `ising_equilibrium` PENDING falsifier on a clean oracle; v9 closed the separability hypothesis —
the genuine DYNAMICAL-category crossing (equilibrium→aging) is the first axis that SMEARS, and conform
resolves the intermediate-X gradient. Cat 9 (mm1_queue) was examined earlier and SET ASIDE — its named
α_s=½ falsifier is a category error (FINDING 3), and the conform-side reframe (critical-slowing X=1 vs
aging X<1) is now answered from BOTH sides — v4/v9 (the X<1 aging cases) and v7/v8 (the X=1 reversible
cases). **Separability is CLOSED (positive):** no axis smears the class EXCEPT a genuine
dynamical-kind crossing — discrete boundaries (reciprocity, v6) and metric axes (within-category v7,
thermodynamic-crossing v8) stay sharp; only the kinetic equilibrium→aging crossing (v9) smears, and
conform places its intermediate operating points at intermediate X rather than a binary label. The
GAPs that remain (2-build, 3, 4, 6) need a clean-truth substrate *built* before they're authorable —
the runway limit — and they are now BREADTH targets, not the closed separability frontier.

- **Falsifier / out-of-domain probes** (test the tripwires, not a category): logistic_chaos
  (no FDT → KILL-test), sine/square_wave (decorrelate trivially), constant (no dynamics).
- **Pure-stochastic, no analytic handle** (NOT authorable as-is): abp, heston, east,
  levy_flight, fbm (scaling known, C/χ not).
- **HOLD (known-contaminated, do NOT seed from):** unnormalized quantum chi, zero-filled
  brain C/chi, null glass tau_env (mpa-central DEFERRED.md library-refresh), and any
  conform-touched seed-corpus bundle (examinee output).
- **conform pieces to quarry** (as examinee, never answer key): conformer/compute/
  {inversion, gfdr_model, five_vector}.py.

---

## Pick up here (end of session 2026-05-25, 9th entry)

**State — v9 (`melt_cooling_sweep_v9`, the Cat-1→8 DYNAMICAL-category crossing) ran BLIND and graded
MATCH (two-sided). It is the genuine kind-crossing v8 was the foil for: cooling a supercooled melt
through its glass transition Tg, equilibrium → out-of-equilibrium AGING (X:1→<1). The blind answerer
recovered the X band EXACTLY (1.00→1.00→0.83→0.63→0.50), placed the warm levels as reversible
equilibrium (single-slope FDR locus, X=1) and the cold levels as aging (bent locus, slow slope X<1),
read the two-step structure, and — load-bearing — read the band as a SMOOTH CROSSOVER with the middle
levels at intermediate X (partially aged), not a sharp jump.** This makes **v9 the FIRST axis tested
that SMEARS**, which **CLOSES the separability hypothesis with a positive result** (a kinetic
dynamical-category crossing smears, unlike the topologically-sharp reciprocity cut v6 and the
no-kind-change metric axes v7/v8 — and conform RESOLVES the intermediate-X gradient rather than
snapping to a binary equilibrium/glass label). Evolve done. v1/v3/v4/v5/v6/v7/v8/v9 in `earned/`, v2
documented-MISS. **`questions/` is now EMPTY** — no staged probe; the next vertical is unauthored.

1. **The pass.** §0 reconcile read clean (disk matched the baton; v9 staged in `questions/` per
   PENDING, not drift). Re-glanced the seal (`freeze_glass_transition.py` reprints it: X band
   `[1, 1, 0.827, 0.629, 0.50]`), then `pose.py melt_cooling_sweep_v9` → fresh blind answerer →
   unseal → MATCH. The blind answerer used the FDR locus (χ vs 1−C) as the universal readout: warm
   levels a single straight line slope 1 (X=1, equilibrium); cold levels a BENT locus (fast slope ~1,
   slow-segment slope X<1) read past the plateau knee. It recovered the slow-segment slope EXACTLY
   (0.83/0.63/0.50), so the smooth crossover is grounded on the data, not guessed. `earned/melt_cooling_sweep_v9/`.

2. **The headline tooth, hit blind.** The trap is reading the cooling as an ABRUPT switch (binary
   equilibrium-or-glass at one temperature) — or under-reading the cold tails as "just slow" (still
   X=1), or over-reading the warm levels as "already glassy." The answerer corrected all three: GRADUAL
   crossover, middle levels genuinely partway out of balance, warm = equilibrium, cold = aging. The
   smear was resolved, not flattened to a label.

3. **Soft anchor (first contact on this oracle).** No exact prior point. Level 4 is a v4-FAMILY
   deep-aging point (X=0.5); its slow-segment slope reproduced v4's X≈0.5 reading — soft cross-pass
   consistency, no drift. (Hard anchoring on this oracle resumes if a second sweep is ever posed.)

4. **Finding (logged).** **A genuine DYNAMICAL-category crossing SMEARS — separability closed.** The
   equilibrium→aging crossing is a SMOOTH KINETIC crossover (X drops 1→0.5 across the cooling range,
   mid levels partially aged), distinct from the topologically-sharp reciprocity cut (v6) and the
   no-kind-change metric axes (v7/v8). The X<1 (aging) dynamical-crossing counterpart to v8's X=1
   (equilibrium) thermodynamic crossing. Categories are separable as KINDS; their boundaries are
   *sharp* when topological/thermodynamic and *smeared* when a kinetic dynamical-kind crossing — and
   conform places intermediate operating points at intermediate X.

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). The v9 pass commit covers `blockin/**` only
(PIPELINE accretion, this baton, PENDING row deletion, `earned/melt_cooling_sweep_v9/`). The
glass-transition oracle was kept INLINE in the freeze (conform-local, brittle-by-design) — not written
as a new `mpa-central` primitive — respecting block-in commit-scope (§6) and avoiding a hook-less
cross-repo write mid-pass; if it earns reuse it can be promoted forward. No `docs/` or out-of-block-in
change this pass. The lone PENDING row (the `mpa-central/DEFERRED.md` riding-crumb) is a cross-repo
crumb, NOT in this tree — untouched. `questions/` is EMPTY. **One writer at a time.**

**Next move (next round) — separability is CLOSED; the next hypothesis is HUMAN-PICKED.** The loop's
nine-pass load-bearing question is answered, so there is no auto-default vertical waiting. **Authoring
is gated (meta-SOP §1/§5): surface the menu to Ron, do not auto-author v10.** §0 reconcile first
(`questions/` will be empty — that is the expected state now, not drift). Candidate frontiers, for Ron
to pick:
   - **Depth — the escalated `t_w` vector (meta-SOP §2 default):** v4's genuine-aging vs
     stationary-eff-T (a waiting-time `t_w` sweep on the glass) has now been parked across passes;
     escalation makes it the standing default. It would sharpen v9's result — is the cold-level aging
     genuine non-stationary `t_w` drift, or a stationary effective temperature? NOTE: needs new
     data / an oracle (library glass cells carry one fixed `t_w` and hit sub-Tg contamination) — a
     build, like v8/v9's oracles.
   - **Cheapest — v5's structure-dependence park (no build):** does the Cat-10 current rate / affinity
     TRACK g/γ? A STRUCTURE sweep at fixed noise; `banach_frustrated` self-simulates. Plug-and-play.
   - **Close Cat-9 on its own substrate:** `mm1_queue` as reversible critical-slowing (X=1) — now
     answered from BOTH sides (v4/v9 X<1 aging, v7/v8 X=1 reversible); a direct single-point
     `mm1_queue` pass would close it. Dev-legal.
   - **Breadth — an untouched category:** the GAPs (Cat 2 reciprocal 2-node, 3 motif/Harary triad, 4
     Meta-Ledger, 5 Kernel/τ_obs, 6 Encoding) need a clean-truth substrate *built* first (the runway
     limit). With separability closed, these are now the frontier for *coverage*, not the hypothesis.
   Whichever Ron picks: author (non-blind subagent) → freeze-compute the seal → human-glance →
   `pose.py` → blind answerer → unseal (anchor-and-assert where geometry allows) → grade → evolve →
   commit per §6. The readiness gate (verify the substrate supports a *blind-readable* clean seal, not
   just that a clean truth exists — v8's lesson) applies to any built oracle.

**The standing finding (updated).** EIGHT contours now landed clean and blind across THREE categories
(Vertex ×4: v1 + v6's matched half + v7's coupling sweep + v8's criticality sweep; non-reciprocal
current ×3: v3 + v5 + v6's cyclic half; Phase/glassy ×2: v4 deep-aging + v9 the equilibrium→aging
crossing). **The separability hypothesis is CLOSED (positive):** across nine passes, no axis smears
the class EXCEPT a genuine dynamical-kind crossing. Discrete boundaries (reciprocity, v6) and metric
axes (within-category v7, thermodynamic-crossing v8) stay SHARP; only the kinetic equilibrium→aging
crossing (v9) SMEARS — X drops 1→0.5 smoothly and conform resolves the intermediate operating points
at intermediate X (partially aged), not a binary label. The teeth held throughout: every MATCH named
the pipeline module that did the work, every park fell out of a collapsed axis. The answer-key
safeguard (freeze-computed seal + human-glance before the blind pass) ran on v9's seal ahead of the
pass and stays in force for any future built oracle.
