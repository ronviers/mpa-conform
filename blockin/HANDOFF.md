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
  smear across several? **Second aggregation (4 verticals: v1/v2 Vertex, v3 Cat-10, v4
  Cat-8).** THREE categories now separate CLEAN, no smear:
  - **1↔10** (v3): Cat-1 ring-down and Cat-10 circulation share the same damped-cosine
    C(τ), yet the blind answerer split them on the cross-correlation antisymmetry (Cxy≠Cyx).
  - **1↔8** (v4): the blind answerer read a glassy two-step relaxation as TWO populations
    (a frozen-in plateau + a stretched slow tail), did NOT collapse it to a single Vertex
    relaxation, and read the slow-mode FDT violation (X<1) off the two-slope FDR locus —
    the discriminators were the plateau/timescale-separation in C(τ) and the second slope.
  So far every boundary reads SHARP. **But the caveat stands and is now the load-bearing
  one:** all three landed probes are structurally FAR apart (a single underdamped mode, a
  3-cycle current, a two-timescale glass) — these are *easy* separations. The hypothesis is
  *encouraged, not confirmed*; the informative test is still a structurally-ADJACENT pair
  (e.g. a reciprocal coupled pair, Cat 2) to find where the boundary actually BLURS. Clean
  separation of distant categories proves little about the modular cut's validity.

## Vertical ledger  [append 1 line/pass; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
laser_ro_pump_sweep_v2| 1 (Vertex), I2   | CLEAN         | non-monotonic ζ band; extremum (crispest/least-damped) at curve 3; over-damping wall at curve 1; no instability | BLIND MISS-with-finding (meta-validity P): placements+band-shape+v1-anchor all reproduced (conform OK, no cage_edge, no KILL), BUT the "healthiest" verdict inverted (seal=curve3 crispness vs blind=curve2 margin) — flips on a health-metric absent from the packet → question lacks teeth; seal's verdict was prose-asserted beyond the Jacobian. 2-sided headroom mechanically groundable (escalation's mechanical aim met). READOUT contour NOT earned. RECLASSIFIED 2026-05-25: verdict-lens inversion is a VIEWER-LAYER concern (researcher utility-lens over the computed band), NOT a teeth-defect → deferred to docs/deferred-for-auditor.md Entry 1, NOT re-posed as v3. earned/.
three_species_cycle_v3| 10 (Non-Recip)   | CLEAN         | sustained NESS current ω/γ≈1.04, ~6 loops/run, far from the ω→0 equilibrium edge; Δ→next: quantitative noise-INDEPENDENCE needs a noise sweep | BLIND MATCH. First contact with the current-gate / two-frame sector (Vertex structurally cannot reach it): a blind answerer read the current in TWO frames (FDR-locus loop + winding/antisymmetry) and they AGREE; placed it STABLE; corrected the naive "noise-driven wobble" worry. CAT-1 vs CAT-10 SEPARATED CLEAN — same damped-cosine C as a ring-down, but the answerer caught Cxy=-Cyx and did NOT collapse to Vertex (separability's first non-Vertex datapoint, no smear). Re-bounded mid-session under the new symmetric-boundary rule (WORKFLOW §4): the in-slice winding ensemble made affinity/TUR/two-frame groundable from ONE point. Note: answerer grounded agreement via locus-vs-winding, NOT the formal affinity/TUR scalars (in-slice but unused → reachable-but-unexercised). Noise-independence parked = a COLLAPSED-AXIS park (legit ADVANCE vector), not under-provisioning. earned/.
glass_two_step_v4     | 8 (Phase/glassy) | CLEAN         | two-step relaxation: plateau q_EA≈0.69, stretched β_KWW≈0.63, ~10³× timescale separation; slow-mode FDT violation X≈0.50 (T_eff/T=2), interior — headroom 0.5 each side (X→1 re-equilibration, X→0 arrest); Δ→next: genuine waiting-time aging vs stationary eff-T needs a t_w sweep | BLIND MATCH. First Cat-8 vertical; first contact with the aging-FDR / two-step sector (Vertex structurally cannot reach it). The blind answerer read the TWO-step structure (did NOT collapse to a single Vertex relaxation — 1↔8 separated CLEAN, no smear) and read the slow-mode FDT violation X<1 off the TWO-SLOPE χ-vs-C locus (fast slope≈1, slow slope=X) — AVOIDING the equilibrium-collapse trap (cage_edge 2). This is the clean X<1 counterpart to the parked mm1 FINDING-3 tension (there X=1, trap was over-claiming aging; here X<1, trap is reading it as equilibrium). Not hollow (out-of-eq grounded on the locus, not guessed); no KILL. Park = a COLLAPSED-AXIS park (t_w sweep), and the answerer SPLIT a second park the seal under-specified: "not AT arrest" groundable, distance-TO-arrest not. earned/.
3sp_noise_sweep_v5    | 10 (Non-Recip)   | CLEAN         | current rate FLAT to <6% over a 20× noise range (drift~ω/γ=1.04, affinity~13 nats/cyc); 2-point structure D-invariant; Cxy=-Cyx at every level; Δ→next: structure-dependence (rate TRACKS g/γ) needs a STRUCTURE sweep | BLIND MATCH. 2nd I2 sweep. SPENDS v3's owed noise-INDEPENDENCE vector → now GROUNDED across the swept axis (v3 could only answer the "calm the environment" counterfactual structurally; this answers it empirically). Anchor (level 3 = v3's D=0.1) reproduces v3: |Cxy-Cyx|=0.66 exact, rate~ω. Blind read was MORE conservative than the seal on the ONE noisy axis: the answerer PARKED "what noise changes" because the 2nd moment (Var(J)/TUR factor) is estimator-noisy/non-monotone — independently re-deriving deferred-for-auditor Entry 2 (caveat real, not a freeze artifact; a measurement-quality flag, NOT a conform defect or an MPA falsification). No cage_edge, no KILL, not hollow. earned/.
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
| 1 · Vertex (single mode) | **READY+** | **⟳ v1 LANDED** (v2 run 2026-05-25 — MISS-with-finding, NOT landed) | class-B laser ✓, ou_equilibrium ✓, two_temp_ou ✓, kww_oracle ✓, white_noise ✓ — *deep* |
| 2 · Edge (coupled pair) | PARTIAL | — | two_temp_ou is 2 coupled OU but exposed as single-relax+X; want a clean *reciprocal* 2-node |
| 3 · Subgraph (motif) | **GAP** | — | banach_frustrated is a 3-mode but *non*-reciprocal (→ cat 10); a reciprocal motif / Harary triad has no clean-truth data yet |
| 4 · Meta-Ledger | **GAP** | — | abstract (FDT/entropy accounting); no substrate identified — may be an *instrument* test, not a substrate |
| 5 · Kernel (camera/τ_obs) | PARTIAL | — | no dedicated camera-artifact substrate; probe via kww_oracle's two timescales + a τ_obs sweep |
| 6 · Encoding | **GAP** | — | no dedicated substrate; the `e_i=s_i⊕s_{i-1}` preprocessing needs a spin process with clean truth |
| 7 · Capacity | PARTIAL | — | mm1_queue's ρ→1 saturation *is* a capacity limit — repurpose-able; no dedicated capacity substrate |
| 8 · Phase (glassy/critical) | **READY+** | **⟳ v4 LANDED** (BLIND MATCH 2026-05-25; aging-FDR / two-step sector reached) | kww_oracle ✓ (full 5-vector glassy fingerprint, rung-5 validated), ising/ou equilibrium ✓ (X=1); criticality/aging PARTIAL (sk z≈4, sir R₀, voter — placeholder near Tc) |
| 9 · Queueing | **READY** (named falsifier mis-spec) | — | mm1_queue ✓ (exact stationary ρ/(1−ρ)); BUT its named α_s=½ falsifier is a category error (FALSIFICATION.md FINDING 3) — a conform vertical here needs the **critical-slowing-vs-aging reframe** (reversible X=1 vs the v4 X<1 aging), not the ½ test |
| 10 · Non-Reciprocal (current/k_frust) | **READY+** | **⟳ v3 + v5 LANDED** (v3 BLIND MATCH — current/two-frame sector; v5 BLIND MATCH 2026-05-25 — noise sweep, rate noise-INDEPENDENCE grounded) | banach_frustrated ✓ (exact 3-mode current, affinity/TUR); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 4 categories are
READY (1, 8, 9, 10), ~3 PARTIAL (2, 5, 7), 3 GAP (3, 4, 6). *Work-wise*, **4 verticals have
landed contours** — v1 (Vertex/Cat 1), v3 (Cat 10, non-reciprocal), v4 (Cat 8, Phase/glassy),
v5 (Cat 10 noise sweep — the second contour ON Cat 10); v2 (Vertex sweep) graded
MISS-with-finding (deferred to the viewer layer, landed no contour). So landed evidence is now
FOUR records across THREE categories (`earned/laser_ro_nominal_v1/`, `earned/three_species_cycle_v3/`,
`earned/glass_two_step_v4/`, `earned/three_species_cycle_noise_sweep_v5/`) plus one documented
MISS. v3 reached the current/two-frame sector; v5 closed its noise-independence sub-question
(current rate flat over 20× noise, blind); v4 reached the aging-FDR / two-step sector. Cat 9
(mm1_queue) was examined this session and SET ASIDE — its named α_s=½ falsifier is a category
error (FINDING 3), and the conform-side reframe (critical-slowing X=1 vs aging X<1) is now
*partly answered from the other side* by v4 (the X<1 glassy aging case). **The separability §4
caveat is the load-bearing pointer:** three categories separated clean, but all three probes were
structurally FAR apart (easy separations); the informative next probe is a structurally-ADJACENT
pair — **a reciprocal coupled pair (Cat 2)** — to find where the boundary BLURS. The GAPs (3, 4,
6) need a clean-truth substrate *built* before they're authorable — the runway limit.

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

## Pick up here (end of session 2026-05-25, 5th entry)

**State — v5 (`three_species_cycle_noise_sweep_v5`, Cat 10 noise sweep) ran BLIND and graded
MATCH. It SPENDS v3's owed noise-INDEPENDENCE vector — now GROUNDED. Second I2 sweep; second
contour ON Cat 10. Evolve done; pass committed. `questions/` empty; v1/v3/v4/v5 in `earned/`,
v2 documented-MISS.**

1. **The pass.** v5 took v3's exact substrate (`banach_frustrated`, the 3-mode cyclic
   non-reciprocal OU) at FIXED structure (γ=1.0, g=0.6) and swept the NOISE level over 5 points,
   a 20× range (D=0.02…0.40). Posed in researcher voice as the SAME three-population community
   re-run at five environmental-noise levels, asking the question v3 could only answer
   structurally: *does calming the environment slow or stop the cycling?* Blind columns:
   `level, noise_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar`. A blind answerer read it from the
   sanitized inputs only (5 independent single-point placements + a band readout, §6 sweep
   contract); unseal confirmed **MATCH**: the turnover RATE / affinity is FLAT (drift~ω/γ=1.04,
   rel-spread <6%) across the whole noise range; the two-point structure is D-invariant;
   Cxy=−Cyx survives every level. Verdict in the researcher's terms: *the cycling is intrinsic
   (wiring-set), not noise-driven — calming the environment will NOT settle it.* No cage_edge,
   no KILL, not hollow. `earned/three_species_cycle_noise_sweep_v5/`.

2. **The session arc (worth knowing).** The human picked v5 (spend v3's owed sweep) from the
   probe menu. After the freeze-computed key cleared the glance, the human flagged the noisy
   winding 2nd moment as a *researcher-awareness / not-conform's-problem* concern → it was first
   PARKED (caveat filed to `docs/deferred-for-auditor.md` Entry 2, PENDING row added), then the
   human reversed and asked to run it to completion. The blind pass then ran clean.

3. **Residue / finding (logged).** The blind answerer was MORE conservative than the seal on
   the one noisy axis: the seal treated "the absolute spread carries the noise dependence" as a
   soft sub-point, but the answerer could not even ground THAT (the 2nd moment Var(J)/TUR factor
   is estimator-noisy/non-monotone) and PARKED it — **independently re-deriving Entry 2**. A
   blind reader hits the same wall, so the caveat is real, not a freeze artifact — but it is a
   measurement-quality flag (source fix lives in mpa-central), NOT a conform defect and NOT an
   MPA falsification (the TUR floor held at every level; the rate verdict is clean). The NEW park
   v5 opened: STRUCTURE-dependence (does the rate TRACK g/γ?) — a different collapsed axis.

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). The v5 pass commit covers `blockin/**`
(PIPELINE accretion, this baton, `earned/three_species_cycle_noise_sweep_v5/`) and the
`docs/deferred-for-auditor.md` Entry-2 graduation. The v5 PENDING float row is DROPPED (it
landed). The two out-of-block-in arcs (consolidation, five-vector WIP) and the riding crumbs
remain PENDING rows — untouched this pass. `questions/` is **empty**. **One writer at a time.**

**Next move (next round) — gated authoring; pick the probe, then run the loop:**
1. meta-SOP §0 reconcile — diff `git status` against `PENDING.md` first. `questions/` empty;
   v1/v3/v4/v5 landed in `earned/`, v2 documented-MISS. **Then run the §0 readiness gate before
   recommending ANY probe below:** the coverage map is a snapshot — verify the candidate
   substrate at its `mpa-central/library/` source and grep `mpa-central/FALSIFICATION.md` for its
   name (parked / mis-specified teeth?). The gate exists because probe-selection once burned two
   rounds without it.
2. **Author the next vertical** (gated; `sealed_answer` freeze-computed, never prose-asserted).
   Owed/opened ADVANCE vectors (multi-point = I2/prod):
   - v4's **genuine-aging vs stationary-eff-T** (a waiting-time t_w sweep on the glass) — still
     owed, parked once (escalates to default if parked again);
   - v5's NEW **structure-dependence** park: does the Cat-10 current rate / affinity TRACK g/γ?
     (a STRUCTURE sweep at fixed noise — the natural v6 ADVANCE off v5).
   Dev-legal single-vector candidates:
   - **Separability-driven (recommended, STILL the load-bearing gap):** a **structurally-ADJACENT
     pair** to find where the boundary BLURS — every landed separation was between
     structurally-FAR substrates (easy). Best READY target: **`banach_frustrated`'s reciprocal
     control** (symmetric γ → detailed balance, no current) vs the v3 frustrated loop — the SAME
     3-mode wiring, only reciprocity flipped → re-poses 1↔10 at MINIMAL structural distance, on a
     ready clean-truth substrate (`mpa-central/library/k_frust_meter.py`/`k_frust_jcheck.py`; 38×
     sign-definite J separation). The Cat-2 reciprocal 2-node remains GAP (must be built first —
     `two_temp_ou` is not reciprocal; confirmed).
   - **Cat-9 reframe:** `mm1_queue` posed as critical-slowing (reversible X=1) — the X=1 mirror
     of v4 — testing whether conform reads reversible slow relaxation WITHOUT over-claiming aging.
     Single-point dev-legal.
3. `pose.py` → blind answerer (sanitized inputs only) → unseal (orchestrator-side; anchor-and-
   assert where geometry allows) → grade → evolve → commit per §6.

**The standing finding (updated).** FOUR contours now landed clean and blind across THREE
categories (Vertex, non-reciprocal current ×2, glassy aging); the current/two-frame, the
noise-independence, AND the aging-FDR/two-step sectors are all demonstrated. v5 deepened Cat 10
(noise-independence grounded) but did NOT touch separability — it was an I2 sweep on an existing
dot, not a new separation. The separability hypothesis is still *encouraged* (1↔10, 1↔8 sharp)
but every landed separation was between structurally-distant substrates. **The informative next
probe is still a structurally-adjacent pair (where the boundary can actually blur) — the
`banach_frustrated` reciprocal control is now the cheap ready way to get one.** The answer-key
safeguard (freeze-computed seal + human-glance before the blind pass) stays in force — it ran on
v5, and the blind answerer's independent honesty on the noisy 2nd moment is the kind of result it
protects.
