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

## Open hypothesis under test  [shrinks as resolved]
- **10-category separability**: do real substrates land in one category cleanly, or
  smear across several? **Third aggregation (7 verticals: v1/v2 Vertex, v3+v5 Cat-10, v4
  Cat-8, v6 the 1⊕10 reciprocity-flip pair, v7 Cat-1 metric-axis sweep).** Every boundary and
  axis tested still reads SHARP:
  - **1↔10** (v3): Cat-1 ring-down and Cat-10 circulation share the same damped-cosine
    C(τ), yet the blind answerer split them on the cross-correlation antisymmetry (Cxy≠Cyx).
  - **1↔8** (v4): the blind answerer read a glassy two-step relaxation as TWO populations
    (a frozen-in plateau + a stretched slow tail), did NOT collapse it to a single Vertex
    relaxation, and read the slow-mode FDT violation (X<1) off the two-slope FDR locus.
  - **1↔10 at MINIMAL GENERATING DISTANCE** (v6 — the adjacent-pair test the caveat below
    demanded): two communities one *reciprocity-flip* apart on the SAME substrate family
    (matched/symmetric ⟨σ⟩=0 vs cyclic/antisymmetric ⟨σ⟩=2.16), posed together with no class
    hint, separated CLEAN on the cross-correlation symmetry. **This partly RESOLVES the
    load-bearing caveat — but by reframing it, not by finding a blur:** the 1↔10 cut turns out
    to be TOPOLOGICALLY sharp, not metrically blurry. Reciprocity is a *discrete* structural
    property (a coupling is symmetric or it is not; g→0 deletes the loop rather than blurring
    the class), so even minimal *generating* distance gives large *observable* distance. That
    explains WHY the prior far-separations read clean — the reciprocity boundary **cannot**
    smear.
  - **Cat-1 along a METRIC axis** (v7 — the metric companion to v6): v6's matched community with
    its coupling strength dialed up across five levels toward the stability edge. All five placed
    as the SAME reversible Cat-1 relaxation (no oscillation, no current, X=1); only the magnitude
    changed (timescale + susceptibility diverge → critical slowing toward the edge). **Cat-1 does
    NOT smear along this continuous axis either** — cranking the knob moves the operating point
    toward a boundary, it does not change the class.
  **The caveat, now precise (post v6+v7):** neither a *discrete* boundary (reciprocity, v6) nor a
  *metric* axis *within a category* (coupling strength, v7) smears the class — both stay sharp;
  what a metric axis does is move the operating point toward a category/stability boundary (with
  the headroom readable). The genuinely-still-open question is narrower: does a metric axis that
  CROSSES a category boundary — passes through a critical point INTO a different class — show a
  smeared transition region, or a sharp jump? That needs a substrate where a tunable axis actually
  traverses two categories: **criticality T→Tc** (Cat 8 onset from Cat 1) or the **Cat-2 reciprocal
  coupled pair**. Both are GAP/PARTIAL (must be built or completed; `two_temp_ou` is confirmed NOT
  reciprocal). Until then: separability is *encouraged* (no smear seen on any axis tested — discrete
  or within-category-metric) and *untested* only for the boundary-CROSSING metric case.

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
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED**; **⟳ v6** (matched community = Cat-1, one half of the reciprocity-flip pair); **⟳ v7** (the matched community swept along its coupling-strength axis — metric-blur: Cat-1 stays sharp, critical slowing toward the edge) (v2 — MISS-with-finding, NOT landed) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓, banach_frustrated *matched/symmetric control* ✓ (+ its coupling-strength axis, v7) — *deep* |
| 2 · Edge (coupled pair) | PARTIAL | — | two_temp_ou is 2 coupled OU but exposed as single-relax+X; want a clean *reciprocal* 2-node |
| 3 · Subgraph (motif) | **GAP** | — | banach_frustrated is a 3-mode but *non*-reciprocal (→ cat 10); a reciprocal motif / Harary triad has no clean-truth data yet |
| 4 · Meta-Ledger | **GAP** | — | abstract (FDT/entropy accounting); no substrate identified — may be an *instrument* test, not a substrate |
| 5 · Kernel (camera/τ_obs) | PARTIAL | — | no dedicated camera-artifact substrate; probe via kww_oracle's two timescales + a τ_obs sweep |
| 6 · Encoding | **GAP** | — | no dedicated substrate; the `e_i=s_i⊕s_{i-1}` preprocessing needs a spin process with clean truth |
| 7 · Capacity | PARTIAL | — | mm1_queue's ρ→1 saturation *is* a capacity limit — repurpose-able; no dedicated capacity substrate |
| 8 · Phase (glassy/critical) | **READY+** | **⟳ v4 LANDED** (BLIND MATCH 2026-05-25; aging-FDR / two-step sector reached) | kww_oracle ✓ (full 5-vector glassy fingerprint, rung-5 validated), ising/ou equilibrium ✓ (X=1); criticality/aging PARTIAL (sk z≈4, sir R₀, voter — placeholder near Tc) |
| 9 · Queueing | **READY** (named falsifier mis-spec) | — | mm1_queue ✓ (exact stationary ρ/(1−ρ)); BUT its named α_s=½ falsifier is a category error (FALSIFICATION.md FINDING 3) — a conform vertical here needs the **critical-slowing-vs-aging reframe** (reversible X=1 vs the v4 X<1 aging), not the ½ test |
| 10 · Non-Reciprocal (current/k_frust) | **READY+** | **⟳ v3 + v5 + v6 LANDED** (v3 BLIND MATCH — current/two-frame sector; v5 BLIND MATCH — noise sweep, rate noise-INDEPENDENCE grounded; v6 BLIND MATCH 2026-05-25 — the cyclic community = Cat-10 half of the minimal-distance 1↔10 pair, anchored to v3) | banach_frustrated ✓ (exact 3-mode current, affinity/TUR; + its symmetric *reciprocal control* now exists as the Cat-1 contrast, v6); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 4 categories are
READY (1, 8, 9, 10), ~3 PARTIAL (2, 5, 7), 3 GAP (3, 4, 6). *Work-wise*, **6 verticals have
landed contours** — v1 (Vertex/Cat 1), v3 (Cat 10, non-reciprocal), v4 (Cat 8, Phase/glassy),
v5 (Cat 10 noise sweep), v6 (the 1⊕10 reciprocity-flip PAIR — Cat 1 *and* Cat 10 at minimal
generating distance), v7 (Cat 1 metric-axis sweep — coupling strength toward the stability edge);
v2 (Vertex sweep) graded MISS-with-finding (deferred to the viewer layer, landed no contour). So
landed evidence is now SIX records across THREE categories (`earned/laser_ro_nominal_v1/`,
`earned/three_species_cycle_v3/`, `earned/glass_two_step_v4/`, `earned/three_species_cycle_noise_sweep_v5/`,
`earned/community_pair_v6/`, `earned/coupling_ramp_v7/`) plus one documented MISS. v3 reached the
current/two-frame sector; v5 closed its noise-independence sub-question; v4 reached the aging-FDR /
two-step sector; v6 landed the first minimal-distance 1↔10 separation (topologically sharp); v7
showed Cat-1 does not smear along a continuous coupling axis (critical slowing toward an edge) and
grounded the qualitative two-sided headroom. Cat 9 (mm1_queue) was examined earlier and SET ASIDE —
its named α_s=½ falsifier is a category error (FINDING 3), and the conform-side reframe
(critical-slowing X=1 vs aging X<1) is now answered from BOTH sides — v4 (the X<1 aging case) and v7
(the X=1 reversible critical-slowing case). **The separability caveat, post v6+v7, is now precise:**
neither a discrete boundary (reciprocity, v6) nor a metric axis WITHIN a category (coupling strength,
v7) smears the class — both stay sharp; a metric axis moves the operating point toward a boundary
(headroom readable), it does not change the class. The only untested case left is a metric axis that
CROSSES a category boundary (through a critical point INTO another class): **criticality T→Tc** (Cat 1
→ Cat 8 onset) or the **Cat-2 reciprocal coupled pair**. The GAPs (2-build, 3, 4, 6) need a clean-truth
substrate *built* before they're authorable — the runway limit.

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

## Pick up here (end of session 2026-05-25, 7th entry)

**State — v7 (`coupling_ramp_v7`, the Cat-1 metric-axis sweep) ran BLIND and graded MATCH. It is
the METRIC-boundary-blur companion to v6: v6 showed the 1↔10 cut is topologically sharp; v7 shows
Cat-1 does NOT smear along a CONTINUOUS (coupling-strength) axis either — the operating point
approaches a stability edge via critical slowing, the class stays put. Evolve done. `questions/`
empty; v1/v3/v4/v5/v6/v7 in `earned/`, v2 documented-MISS.**

1. **The pass.** v7 took v6's MATCHED (reciprocal, symmetric-coupled, Cat-1) community and dialed
   its coupling strength g_s UP across five levels toward the stability threshold g_s→γ=1
   (g_s=[0.3,0.6,0.8,0.9,0.95]). Posed in researcher voice as ONE matched community cranked through
   five interaction-strength settings, asking: *is it starting to oscillate/cycle/go unstable? how
   close to an edge? does cranking change the KIND of system?* Columns
   `level, tau, C, chi, Cxy, Cyx, phiMean, phiVar`, per-level adaptive settling windows. The
   sealed discriminator (critical slowing / spectral gap / X=1) was withheld. A blind answerer
   placed each level independently (sweep contract, §6) then read the band; unseal confirmed
   **MATCH**: all five = reversible Cat-1 relaxation (monotone C → no oscillation; Cxy=Cyx + flat
   winding → no current; affine FDR locus → X=1 equilibrium); the band = a DIVERGING relaxation
   timescale (~doubling per step, 1.3→20) = critical slowing toward a stability edge; the KIND is
   invariant. Verdict in researcher terms: *same kind of settling system all the way up, never
   oscillating or cycling, just slower/bigger — creeping up on an instability edge.* No cage_edge,
   no KILL, not hollow. `earned/coupling_ramp_v7/`.

2. **The subtle teeth, handled.** The FDR-locus SLOPE grows across the sweep (the susceptibility
   diverges as g_s→γ). The blind answerer read this as growing SUSCEPTIBILITY (chi_inf), NOT as an
   X<1 aging onset — keeping the locus affine/equilibrium read (3-way cross-check slope≈chi_inf≈
   tauC agree). So reversible critical slowing (X=1) stayed cleanly separated from glassy aging
   (X<1, v4) along the SAME diverging-timescale signature — the Cat-9 reframe answered from the
   X=1 side.

3. **Anchor held (no cross-pass drift).** Level 1 (g_s=0.6) IS v6's matched community; the answerer
   (blind to this) reproduced it — relaxation time ~2.5, FDR slope ~1.56, Cxy=Cyx.

4. **Finding (logged).** (a) **Metric-boundary blur, Cat-1 side: NO smear.** A continuous axis
   does not blur the class — cranking coupling changes only MAGNITUDE (timescale + susceptibility
   diverge), never KIND; the operating point approaches a stability/critical edge via critical
   slowing. Companion to v6's discrete-axis sharpness. (b) **Two-sided headroom, sharpened
   (advances v1/v2's owed vector).** A sweep DOES ground two-sided headroom — but only the
   QUALITATIVE/observable part: the answerer grounded the DIRECTION (heading toward an instability)
   and the RELATIVE rate (the spectral gap shrinking). The ABSOLUTE distance-to-edge **in native
   control units is NOT closeable even with a sweep** — it needs the control magnitudes, which
   blinding correctly strips; the closeable headroom lives in the OBSERVABLE (the gap), not native
   units. The answerer independently parked the native-unit distance.

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). The v7 pass commit covers `blockin/**` only
(PIPELINE accretion, this baton, `earned/coupling_ramp_v7/`). No `docs/` or out-of-block-in change
this pass. The lone PENDING row (the `mpa-central/DEFERRED.md` riding-crumb) is a cross-repo crumb,
NOT in this tree — untouched. `questions/` is **empty**. **One writer at a time.**

**Next move (next round) — gated authoring; pick the probe, then run the loop:**
1. meta-SOP §0 reconcile — diff `git status` against `PENDING.md` first. `questions/` empty;
   v1/v3/v4/v5/v6/v7 landed in `earned/`, v2 documented-MISS. **Then run the §0 readiness gate
   before recommending ANY probe below:** the coverage map is a snapshot — verify the candidate
   substrate at its `mpa-central/library/` source and grep `mpa-central/FALSIFICATION.md` for its
   name (parked / mis-specified teeth?). The gate exists because probe-selection once burned two
   rounds.
2. **Author the next vertical** (gated; `sealed_answer` freeze-computed, never prose-asserted). The
   separability frontier is now narrow and specific: v6 (discrete cut) and v7 (metric axis WITHIN a
   category) both stayed sharp. The ONLY untested case is a metric axis that **CROSSES a category
   boundary** — passes through a critical point INTO another class — does the transition smear or
   jump?
   - **Boundary-CROSSING metric blur (recommended frontier):** a substrate with a tunable axis that
     actually traverses two categories. Best targets: **criticality T→Tc** (Cat 1 → Cat 8 onset —
     does the relaxation cross from reversible-fast into critical/aging smoothly or sharply?), or
     the **Cat-2 reciprocal coupled pair**. **BOTH are GAP/PARTIAL — substrate must be BUILT or
     completed first** (Cat-8 criticality substrates are "placeholder near Tc" per the coverage map;
     `two_temp_ou` is confirmed NOT reciprocal for Cat 2). Building one is the runway cost; flag to
     the human before committing. This is now THE load-bearing separability probe.
   - Owed/opened ADVANCE vectors on READY substrates (cheaper, carried):
     - v4's **genuine-aging vs stationary-eff-T** (waiting-time t_w sweep on the glass) — owed,
       parked ONCE; parking it again ESCALATES it to the default next vector (meta-SOP §2). **This
       is the cheapest ready ADVANCE and is one park away from auto-escalation — strong candidate.**
     - v5's **structure-dependence** park: does the Cat-10 current rate / affinity TRACK g/γ? (a
       STRUCTURE sweep at fixed noise.)
     - **Cat-9 reframe:** `mm1_queue` as critical-slowing (reversible X=1) — now PARTLY answered
       from BOTH sides (v4 X<1 aging, v7 X=1 reversible critical slowing); a direct mm1_queue pass
       would close it on its own substrate. Single-point dev-legal.
3. `pose.py` → blind answerer (sanitized inputs only) → unseal (orchestrator-side; anchor-and-
   assert where geometry allows) → grade → evolve → commit per §6.

**The standing finding (updated).** SIX contours now landed clean and blind across THREE categories
(Vertex ×3 incl. v6's matched half + v7's sweep, non-reciprocal current ×3 incl. v6's cyclic half,
glassy aging). **v6 and v7 together pin the separability hypothesis down to one open case:** no axis
tested smears the class — not the discrete reciprocity cut (v6), not a metric axis within a category
(v7). Both keep the category sharp; a metric axis moves the operating point toward a boundary (with
the headroom readable) rather than blurring the class. The single remaining open question is whether
a metric axis that CROSSES a category boundary (through a critical point into another class) shows a
smeared transition — and that needs a built/completed boundary-crossing substrate (criticality, or
Cat 2). The answer-key safeguard (freeze-computed seal + human-glance before the blind pass) stays in
force — it ran on v7 (the sealed critical-slowing/X=1 discriminator was freeze-computed; the blind
answerer rediscovered v6's anchor values and independently parked the native-unit headroom limit).
