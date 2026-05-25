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
  smear across several? **Third aggregation (6 verticals: v1/v2 Vertex, v3+v5 Cat-10, v4
  Cat-8, v6 the 1⊕10 reciprocity-flip pair).** Every boundary tested still reads SHARP:
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
  **The caveat, now sharpened:** v6 shows a *discrete* (topological) boundary stays sharp at
  minimal distance — but that is the boundary type *expected* to be sharp. The still-open,
  genuinely informative question is whether a **METRIC** boundary blurs: one with a continuous
  tuning knob (criticality T→Tc, a coupling-strength continuum, the **Cat-2 reciprocal coupled
  pair**). Those are where a category could smear into a neighbor along a real axis. The
  hypothesis is *encouraged* for discrete cuts and *untested* for metric cuts. **The Cat-2
  reciprocal 2-node is the informative next probe — but it is GAP (must be built; `two_temp_ou`
  is confirmed NOT reciprocal).**

## Vertical ledger  [append 1 line/pass; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. RECLASSIFIED 2026-05-25: verdict-lens inversion is a VIEWER-LAYER concern (researcher utility-lens over the computed band), NOT a teeth-defect → deferred to docs/deferred-for-auditor.md Entry 1, NOT re-posed as v3. earned/.
three_species_cycle_v3| 10 (Non-Recip)   | CLEAN         | sustained NESS current ω/γ≈1.04, ~6 loops/run, far from the ω→0 equilibrium edge; Δ→next: quantitative noise-INDEPENDENCE needs a noise sweep | BLIND MATCH. First contact with the current-gate / two-frame sector (Vertex structurally cannot reach it): a blind answerer read the current in TWO frames (FDR-locus loop + winding/antisymmetry) and they AGREE; placed it STABLE; corrected the naive "noise-driven wobble" worry. CAT-1 vs CAT-10 SEPARATED CLEAN — same damped-cosine C as a ring-down, but the answerer caught Cxy=-Cyx and did NOT collapse to Vertex (separability's first non-Vertex datapoint, no smear). Re-bounded mid-session under the new symmetric-boundary rule (WORKFLOW §4): the in-slice winding ensemble made affinity/TUR/two-frame groundable from ONE point. Note: answerer grounded agreement via locus-vs-winding, NOT the formal affinity/TUR scalars (in-slice but unused → reachable-but-unexercised). Noise-independence parked = a COLLAPSED-AXIS park (legit ADVANCE vector), not under-provisioning. earned/.
glass_two_step_v4     | 8 (Phase/glassy) | CLEAN         | two-step relaxation: plateau q_EA≈0.69, stretched β_KWW≈0.63, ~10³× timescale separation; slow-mode FDT violation X≈0.50 (T_eff/T=2), interior — headroom 0.5 each side (X→1 re-equilibration, X→0 arrest); Δ→next: genuine waiting-time aging vs stationary eff-T needs a t_w sweep | BLIND MATCH. First Cat-8 vertical; first contact with the aging-FDR / two-step sector (Vertex structurally cannot reach it). The blind answerer read the TWO-step structure (did NOT collapse to a single Vertex relaxation — 1↔8 separated CLEAN, no smear) and read the slow-mode FDT violation X<1 off the TWO-SLOPE χ-vs-C locus (fast slope≈1, slow slope=X) — AVOIDING the equilibrium-collapse trap (cage_edge 2). This is the clean X<1 counterpart to the parked mm1 FINDING-3 tension (there X=1, trap was over-claiming aging; here X<1, trap is reading it as equilibrium). Not hollow (out-of-eq grounded on the locus, not guessed); no KILL. Park = a COLLAPSED-AXIS park (t_w sweep), and the answerer SPLIT a second park the seal under-specified: "not AT arrest" groundable, distance-TO-arrest not. earned/.
3sp_noise_sweep_v5    | 10 (Non-Recip)   | CLEAN         | current rate FLAT to <6% over a 20× noise range (drift~ω/γ=1.04, affinity~13 nats/cyc); 2-point structure D-invariant; Cxy=-Cyx at every level; Δ→next: structure-dependence (rate TRACKS g/γ) needs a STRUCTURE sweep | BLIND MATCH. 2nd I2 sweep. SPENDS v3's owed noise-INDEPENDENCE vector → now GROUNDED across the swept axis (v3 could only answer the "calm the environment" counterfactual structurally; this answers it empirically). Anchor (level 3 = v3's D=0.1) reproduces v3: |Cxy-Cyx|=0.66 exact, rate~ω. Blind read was MORE conservative than the seal on the ONE noisy axis: the answerer PARKED "what noise changes" because the 2nd moment (Var(J)/TUR factor) is estimator-noisy/non-monotone — independently re-deriving deferred-for-auditor Entry 2 (caveat real, not a freeze artifact; a measurement-quality flag, NOT a conform defect or an MPA falsification). No cage_edge, no KILL, not hollow. earned/.
community_pair_v6     | 1⊕10 (recip-flip pair) | CLEAN   | TWO communities one reciprocity-flip apart on ONE substrate family (matched/symmetric ⟨σ⟩=0 vs cyclic/antisymmetric ⟨σ⟩=2.16, same op-point); both placed independently, separated on cross-corr SYMMETRY (Cxy=Cyx vs Cxy=-Cyx); Δ→next: METRIC-boundary blur (Cat 2 coupling continuum) still unprobed | BLIND MATCH (two-sided). The FIRST minimal-GENERATING-distance 1↔10 separation (every prior separation was structurally FAR). Answerer placed community 0 = reversible relaxation/no current (Cat 1) and community 1 = NESS circulation ~6 turns (Cat 10), grounded the split on the cross-correlation symmetry (time-reversal signature) NOT C-shape alone, and avoided BOTH cage_edges (no Vertex-collapse of the cyclic one, no false current in the matched one). Naive worry corrected (turnover≠instability; both stable). ANCHOR: community 1 = v3 exactly, reproduced blind (winding ~6 turns, rate ~ω) — no cross-pass drift; answerer didn't know it was an anchor. FINDING: the 1↔10 cut is TOPOLOGICALLY sharp (reciprocity is discrete — no continuous knob smears the class; g→0 deletes the loop, doesn't blur it), which reframes WHY prior far-separations read clean. Does NOT settle METRIC-boundary blur (criticality/coupling-continua/Cat 2). No KILL, not hollow. earned/.
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
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED**; **⟳ v6** (the matched community = a Cat-1 reversible relaxation, landed as one half of the reciprocity-flip pair) (v2 run 2026-05-25 — MISS-with-finding, NOT landed) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓, banach_frustrated *matched/symmetric control* ✓ — *deep* |
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
READY (1, 8, 9, 10), ~3 PARTIAL (2, 5, 7), 3 GAP (3, 4, 6). *Work-wise*, **5 verticals have
landed contours** — v1 (Vertex/Cat 1), v3 (Cat 10, non-reciprocal), v4 (Cat 8, Phase/glassy),
v5 (Cat 10 noise sweep — the second contour ON Cat 10), v6 (the 1⊕10 reciprocity-flip PAIR —
one packet exercising Cat 1 *and* Cat 10 at minimal generating distance); v2 (Vertex sweep)
graded MISS-with-finding (deferred to the viewer layer, landed no contour). So landed evidence is
now FIVE records across THREE categories (`earned/laser_ro_nominal_v1/`, `earned/three_species_cycle_v3/`,
`earned/glass_two_step_v4/`, `earned/three_species_cycle_noise_sweep_v5/`, `earned/community_pair_v6/`)
plus one documented MISS. v3 reached the current/two-frame sector; v5 closed its noise-independence
sub-question (current rate flat over 20× noise, blind); v4 reached the aging-FDR / two-step sector;
v6 landed the FIRST minimal-distance 1↔10 separation and showed the cut is topologically sharp (not
metric blur). Cat 9 (mm1_queue) was examined earlier and SET ASIDE — its named α_s=½ falsifier is a
category error (FINDING 3), and the conform-side reframe (critical-slowing X=1 vs aging X<1) is now
*partly answered from the other side* by v4 (the X<1 glassy aging case). **The separability caveat,
post-v6, is now precise:** discrete (topological) boundaries stay sharp at minimal distance — proven
for the reciprocity cut — but a **METRIC** boundary (continuous tuning knob) is still untested for
blur. The informative next probe is a **reciprocal coupled pair (Cat 2)**, a tunable coupling-strength
axis where a category *could* smear. The GAPs (2-build, 3, 4, 6) need a clean-truth substrate *built*
before they're authorable — the runway limit.

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

## Pick up here (end of session 2026-05-25, 6th entry)

**State — v6 (`community_pair_v6`, the 1⊕10 reciprocity-flip PAIR) ran BLIND and graded MATCH
(two-sided). The FIRST minimal-GENERATING-distance 1↔10 separation; it answered the load-bearing
separability caveat by REFRAMING it (the cut is topologically sharp, not metric blur). Evolve done.
`questions/` empty; v1/v3/v4/v5/v6 in `earned/`, v2 documented-MISS.**

1. **The pass.** v6 posed TWO three-population loop communities one *reciprocity-flip* apart on
   the SAME substrate family (`banach_frustrated` machinery), same operating point γ=1.0, g=0.6,
   D=0.1: community 0 a MATCHED/symmetric coupling (S = Pᵀ[[0,1],[1,0]]P → detailed balance,
   ⟨σ⟩=0, all-real spectrum) and community 1 the CYCLIC/antisymmetric coupling (= v3 exactly →
   ⟨σ⟩=2.16, complex pair, Cxy=−Cyx). One blind packet, NO per-community class hint; columns
   `community, tau, C, chi, Cxy, Cyx, phiMean, phiVar`. The discriminator — the **cross-correlation
   symmetry** (Cxy=Cyx reversible vs Cxy=−Cyx current) — was sealed. A blind answerer placed each
   independently then related them; unseal confirmed **MATCH (two-sided)**: community 0 = a
   reversible coupled relaxation that SETTLES (no current, symmetric cross-corr, flat winding,
   FDR affine R²=1.00); community 1 = a sustained NESS circulation (~6 turns, antisymmetric
   cross-corr, FDR non-affine). The answerer grounded the split on the cross-corr SYMMETRY (not
   C-shape alone), reported BOTH stable, and avoided BOTH cage_edges (no Vertex-collapse of the
   cyclic one, no false current in the matched one). `earned/community_pair_v6/`.

2. **Anchor held (no cross-pass drift).** Community 1 IS v3 at v3's operating point; the answerer
   (blind to this) independently reproduced v3's contour — winding ~6 turns, rate ~ω, |Cxy−Cyx|
   antisymmetric. Cheap cross-pass drift check, clean.

3. **Finding (logged — the load-bearing one).** The **1↔10 cut is TOPOLOGICALLY sharp, not
   metrically blurry.** Minimal *generating* distance (one reciprocity-flip) still gives large
   *observable* distance, because reciprocity is a DISCRETE structural property — a coupling is
   symmetric or it is not; g→0 deletes the loop rather than blurring the class. This reframes WHY
   the prior far-separations (1↔10 v3, 1↔8 v4) read clean: the reciprocity boundary CANNOT smear.
   It does NOT settle whether a **METRIC** boundary (continuous knob — criticality, a
   coupling-strength continuum, **Cat 2**) blurs. The separability caveat is now precise: discrete
   cuts are sharp (proven); metric-cut blur is still untested.

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). The v6 pass commit covers `blockin/**` only
(PIPELINE accretion, this baton, `earned/community_pair_v6/`). No `docs/` or out-of-block-in
change this pass. The lone PENDING row (the `mpa-central/DEFERRED.md` riding-crumb) is a cross-repo
crumb, NOT in this tree — untouched. `questions/` is **empty**. **One writer at a time.**

**Next move (next round) — gated authoring; pick the probe, then run the loop:**
1. meta-SOP §0 reconcile — diff `git status` against `PENDING.md` first. `questions/` empty;
   v1/v3/v4/v5/v6 landed in `earned/`, v2 documented-MISS. **Then run the §0 readiness gate before
   recommending ANY probe below:** the coverage map is a snapshot — verify the candidate substrate
   at its `mpa-central/library/` source and grep `mpa-central/FALSIFICATION.md` for its name
   (parked / mis-specified teeth?). The gate exists because probe-selection once burned two rounds.
2. **Author the next vertical** (gated; `sealed_answer` freeze-computed, never prose-asserted).
   The separability question now points at ONE specific informative probe:
   - **METRIC-boundary blur (recommended, the now-load-bearing gap):** v6 proved discrete cuts are
     sharp; the untested question is whether a category smears along a CONTINUOUS axis. The natural
     target is the **Cat-2 reciprocal coupled pair** (a tunable coupling-strength axis between two
     reciprocal nodes — does it blur into Cat 1 / Cat 8 as coupling → 0 / → critical?). **BUT Cat 2
     is GAP — the clean-truth substrate must be BUILT first** (`two_temp_ou` is confirmed NOT
     reciprocal). Building it is the runway cost; flag to the human before committing to it.
   - A cheaper metric-blur proxy WITHOUT building Cat 2: sweep the v6 *matched* community's coupling
     g_s toward its plane-stability threshold (γ→g_s) — does the Cat-1 relaxation blur toward an
     oscillatory onset? (A tunable-axis sweep on a READY substrate; tests metric blur on the Cat-1
     side without new substrate work.) Multi-point = I2/prod.
   Other owed/opened ADVANCE vectors (carried, not recommended over the above):
   - v4's **genuine-aging vs stationary-eff-T** (waiting-time t_w sweep on the glass) — owed,
     parked ONCE; parking it again ESCALATES it to the default next vector (meta-SOP §2).
   - v5's **structure-dependence** park: does the Cat-10 current rate / affinity TRACK g/γ? (a
     STRUCTURE sweep at fixed noise.)
   - **Cat-9 reframe:** `mm1_queue` as critical-slowing (reversible X=1) — the X=1 mirror of v4.
     Single-point dev-legal.
3. `pose.py` → blind answerer (sanitized inputs only) → unseal (orchestrator-side; anchor-and-
   assert where geometry allows) → grade → evolve → commit per §6.

**The standing finding (updated).** FIVE contours now landed clean and blind across THREE
categories (Vertex ×2 incl. v6's matched half, non-reciprocal current ×3 incl. v6's cyclic half,
glassy aging); the current/two-frame, noise-independence, aging-FDR/two-step, AND now the
minimal-distance 1↔10 separation sectors are all demonstrated. **v6 is the first vertical to
directly MOVE the separability hypothesis:** it shows the 1↔10 cut is *discrete/topological* and
therefore unconditionally sharp — so the open question sharpens from "do categories smear?" to
"do METRIC (continuously-tunable) boundaries smear?", which discrete-cut evidence cannot answer.
That is the informative frontier, and it needs either a built Cat-2 substrate or a tunable-axis
sweep on a ready one. The answer-key safeguard (freeze-computed seal + human-glance before the
blind pass) stays in force — it ran on v6 (the sealed cross-corr-symmetry discriminator was
freeze-computed, and the blind answerer independently rediscovered v3's anchor values).
