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
| 10 · Non-Reciprocal (current/k_frust) | **READY+** | **⟳ v3 LANDED** (BLIND MATCH 2026-05-25; current-gate/two-frame sector reached & agree) | banach_frustrated ✓ (exact 3-mode current, affinity/TUR); driven_ring PARTIAL, banach_active_ring PARTIAL (nonlinear Hopf) |

**Ceiling (two different counts — don't conflate them):** *substrate-wise*, 4 categories are
READY (1, 8, 9, 10), ~3 PARTIAL (2, 5, 7), 3 GAP (3, 4, 6). *Work-wise*, **3 verticals have
landed contours** — v1 (Vertex/Cat 1), v3 (Cat 10, non-reciprocal), v4 (Cat 8, Phase/glassy);
v2 (Vertex sweep) graded MISS-with-finding (deferred to the viewer layer, landed no contour). So
landed evidence is now THREE records across THREE categories (`earned/laser_ro_nominal_v1/`,
`earned/three_species_cycle_v3/`, `earned/glass_two_step_v4/`) plus one documented MISS. v3
reached the current/two-frame sector; v4 reached the aging-FDR / two-step sector. Cat 9
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

## Pick up here (end of session 2026-05-25, 4th entry)

**State — v4 (`glass_two_step_v4`, Cat 8 Phase/glassy) ran BLIND and graded MATCH. THIRD
category landed; the aging-FDR / two-step sector reached and exercised for the first time.
Evolve done; pass committed. `questions/` empty; v1/v3/v4 in `earned/`, v2 documented-MISS.**

1. **The pass.** v4 jumped category off the prior dots to a glassy two-timescale substrate
   (the KWW oracle, `mpa-central/library/primitives/kww_oracle`), posed in researcher voice as
   a supercooled liquid near arrest ("two-step relaxation — equilibrated-but-slow, or
   out-of-equilibrium with the slow part effectively hotter?"). Blind columns: `tau, C, chi`.
   A blind answerer read it from the sanitized inputs only; unseal confirmed **MATCH**: it read
   the TWO-step structure (plateau q_EA≈0.69, stretched β_KWW≈0.63, ~10³× separation), read the
   slow-mode FDT violation X≈0.50 (T_eff/T=2) off the TWO-SLOPE χ-vs-C locus, placed it STABLE
   (not AT arrest), and corrected the naive worry — AVOIDING the equilibrium-collapse trap
   (cage_edge 2). No cage_edge, no KILL, not hollow. `earned/glass_two_step_v4/`.

2. **Why this probe (the mm1 detour — worth knowing).** The session first picked **Cat 9
   `mm1_queue`** (the corpus's named falsifier). On reading FALSIFICATION.md it surfaced that
   the named α_s=½ falsifier is a **category error** (FINDING 3, parked 2026-05-20): ½ is the
   heavy-traffic Hurst exponent (C-vs-lag plane), α_s is the FDR effective-temperature slope
   (χ-vs-C plane). The human SET mm1 ASIDE. The live tension FINDING 3 left open — does the
   heavy-traffic→s mapping over-claim aging, or does s admit X=1 critical slowing? — has a clean
   X<1 counterpart, which became v4: kww is genuine aging (X<1), the mirror of mm1's reversible
   X=1. v4 answered the X<1 side: conform reads aging correctly, blind. (The mm1 X=1 side — a
   critical-slowing-vs-aging reframe — remains a dev-legal candidate; see coverage map Cat 9.)

3. **Residue (logged, not an action).** The answerer SPLIT a collapsed-axis park the seal
   under-specified: "not AT arrest" is groundable from one stationary window, but distance/
   direction TO arrest is not (needs a control-axis sweep). A sharper `not_grounded` line than
   authored. (PIPELINE §4 [CONTACT] records the sector; RESULT.md records the split.)

**Coordination state.** Open-state register is **[`PENDING.md`](PENDING.md)** (§0 reconcile:
in-register = expected-float, not-there = drift). The v4 pass commit covers `blockin/**`
(PIPELINE accretion, this baton, `earned/glass_two_step_v4/`). The two out-of-block-in arcs
(consolidation, five-vector WIP) and the riding crumbs remain PENDING rows — untouched this pass.
`questions/` is **empty** (v4 moved to `earned/`). **One writer at a time.**

**Next move (next round) — gated authoring; pick the probe, then run the loop:**
1. meta-SOP §0 reconcile — diff `git status` against `PENDING.md` first. `questions/` empty;
   v1/v3/v4 landed in `earned/`, v2 documented-MISS; confirm the v4 pass commit landed. **Then
   run the §0 readiness gate before recommending ANY probe below:** the coverage map is a
   snapshot — verify the candidate substrate at its `mpa-central/library/` source and grep
   `mpa-central/FALSIFICATION.md` for its name (parked / mis-specified teeth?). This pass added
   the gate precisely because probe-selection burned two rounds without it.
2. **Author the next vertical** (gated; `sealed_answer` freeze-computed, never prose-asserted).
   The §2 ADVANCE owed-vectors now NUMBER TWO (both multi-point = I2/prod, both logged owed,
   each parked once — escalates to the default if parked again):
   - v3's **noise-INDEPENDENCE** (a noise sweep on the Cat-10 current);
   - v4's **genuine-aging vs stationary-eff-T** (a waiting-time t_w sweep on the glass).
   Dev-legal single-vector candidates:
   - **Separability-driven (recommended, now the load-bearing gap):** a **structurally-ADJACENT
     pair** to find where the boundary BLURS — three categories separated clean but all probes
     were structurally FAR apart (easy separations). Best target: a **reciprocal coupled pair
     (Cat 2)**, substrate status PARTIAL (`two_temp_ou` is a single relax mode + X, NOT a
     reciprocal 2-node — confirmed this session; a clean reciprocal 2-node must be BUILT first,
     runway work outside the loop). A cheaper adjacency: pose a NEAR-glass / near-current variant
     that shares structure with an existing dot.
   - **Cat-9 reframe:** `mm1_queue` posed as critical-slowing (reversible X=1) — the X=1 mirror
     of v4 — testing whether conform reads reversible slow relaxation WITHOUT over-claiming aging
     (the FINDING-3 tension from the other side). Single-point dev-legal.
   - **Spend an owed sweep early:** the human may elect v3's noise sweep or v4's t_w sweep now
     (v2 precedent — a legitimate top-level call), closing a park directly.
3. `pose.py` → blind answerer (sanitized inputs only) → unseal (orchestrator-side; anchor-and-
   assert where geometry allows) → grade → evolve → commit per §6.

**The standing finding (updated).** THREE categories now landed clean and blind (Vertex,
non-reciprocal current, glassy aging); the current/two-frame AND the aging-FDR/two-step sectors
are both demonstrated, not just cage. The separability hypothesis is *encouraged* (1↔10 and 1↔8
both sharp) but every landed separation was between structurally-distant substrates — proving
little about the modular cut's validity. **The informative next probe is a structurally-adjacent
pair (where the boundary can actually blur), not another distant category.** The answer-key
safeguard (freeze-computed seal) stays in force — it is what kept v4's key honest, and the
human-glance on the computed key ran before the blind pass.
