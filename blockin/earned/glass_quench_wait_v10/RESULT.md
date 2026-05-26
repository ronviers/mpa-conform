# glass_quench_wait_v10 — BLIND PASS RESULT

phase: DEV/blind · view: `view_20260526-010803.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

A sweep: one glass's two-time fluctuation correlation C and integrated response chi, at 5
WAITING TIMES after a single quench (level 0..4; level 0 youngest, level 4 oldest), ONE
temperature deep below Tg. Per WORKFLOW §6, each age placed as an **independent single-point fit
first**, then the band read off the 5 placements. Each age on its own clock (windows grow
~560→9000, matched to each age's own slow relaxation).

The substrate is a **glass-aging oracle** (the v9 glass-transition oracle held at one deep-quench
temperature and swept along t_w instead of T): a two-timescale KWW with an age-dependent
alpha-time τ_α(t_w) = τ_α_ref·(t_w/t_w_ref)^μ, μ=1 (full aging). Truth from the equilibrium/aging
FDT structure, never via conform — the slow-mode FDT ratio X=0.50 is encoded directly and is
age-independent; τ_α grows ∝ t_w (see `entry.md` SEALED half / `freeze_glass_aging.py`).

This is the meta-SOP §2-escalated WAITING-TIME (t_w) vector v4 parked twice and v9 left standing:
v4 (single deep-aging point) and v9 (a T-sweep, each level one implicit age) read X<1 but could not
separate GENUINE AGING (non-stationary, τ_α grows with age, curves not TTI) from a STATIONARY
effective-temperature state (X<1 but time-translation invariant). The t_w axis is the discriminator.

---

## Per-age placement (the framework read)

| level (age) | t_w | plateau | fast slope | slow slope X | slow timescale | window τ_max | kind |
|---|---|---|---|---|---|---|---|
| 0 youngest | 1 | 0.77 | 0.93 | 0.500 | τ(C=0.4)=19 | 562 | aging glass |
| 1 | 2 | 0.78 | 0.95 | 0.500 | 38 | 1125 | aging glass |
| 2 (anchor) | 4 | 0.78 | 0.96 | 0.500 | 77 | 2250 | aging glass |
| 3 | 8 | 0.79 | 0.97 | 0.500 | 154 | 4500 | aging glass |
| 4 oldest | 16 | 0.79 | 0.97 | 0.500 | 308 | 9000 | aging glass |

- **FDR locus (universal readout):** at EVERY age the locus BENDS — fast segment slope ~1 (β-modes
  equilibrated, FDT) then a shallow slow segment of slope X=0.500 (α-modes out of equilibrium). X is
  FLAT across all five ages (spread 0.00) → the imbalance is age-independent, does NOT heal.
- **Two-step structure** read at every age (plateau ~0.78 + slow stretched tail), not collapsed.

## The band (what migrates / what stays put)
- **Migrates (the aging signature):** the slow timescale GROWS geometrically with age — τ(C=0.4)
  doubles per step (19→38→77→154→308 ≈ ∝ t_w), and at a fixed lag C climbs with age (the curves do
  NOT collapse → non-stationary). The material keeps evolving; it never settles.
- **Stays put:** X=0.50 at every age (the slow-mode effective temperature is age-independent), and
  the fast-segment FDT slope ~1.

## Verdict in the researcher's own terms
- **Keeps evolving or fixed state?** KEEPS EVOLVING (genuine aging). An old sample relaxes measurably
  slower than a young one; the relaxation is a function of how long you waited, not a fixed steady state.
- **In balance / does it heal?** Out of balance on the slow modes (X≈0.5) at every age, and that
  imbalance does NOT heal — the glass gets slower with age but not more equilibrated.
- **Naive corrections, both ways:** "it has settled into a fixed sluggish state" is wrong (it keeps
  aging, curves don't collapse); "the imbalance heals as it settles" is wrong (X stays 0.5).

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **Load-bearing aging signature recovered:** the slow timescale grows ∝ t_w (×2/step, the full-aging
  law) and the C(τ) curves do not collapse (fixed-lag C climbs) → non-stationary = GENUINE AGING ✓.
- **X flat at 0.500 every age** (sealed X-band `[0.5,0.5,0.5,0.5,0.5]`) → out of equilibrium,
  age-independent eff-T, NOT re-equilibrating ✓.
- Per-age placement: glassy two-step, bent FDR locus, fast slope ~1, slow slope 0.50 ✓.
- **Headline tooth hit** (cage_edge 1, stationary/TTI): read as KEEPS EVOLVING, not a fixed steady
  state ✓. Both other reads corrected: not re-equilibrating (cage_edge 2) ✓, not equilibrium/just-slow
  (cage_edge 3) ✓.
- Two-step not collapsed (cage_edge 4) ✓; no false oscillation/current (cage_edge 5) ✓; not
  speeding-up-with-age (cage_edge 6) ✓.
- **Not hollow** — every claim grounded on a computed observable (FDR slope, slow timescale, fixed-lag
  C, plateau) ✓. **Meta-validity P held** — independent per-age placements, then band ✓.
- **No KILL:** no NaN, no X>1 (X=0.5), no current, ground-truth X flat 0.5 + τ_α ∝ t_w (freeze-confirmed).
- **Anchor-and-assert (HARD):** level 2 is built identical to v9 level 4 (τ_α=150, q_EA=0.80, β=0.55,
  X=0.50). Blind L2: plateau 0.783, X=0.500, **window τ_max=2250 = 15×150** → τ_α=150 confirmed →
  reproduces v9 L4's reading. No cross-pass drift.
- **Boundary symmetry (§4):** every `not_grounded[]` item is a collapsed-axis park (native times, the
  TEMPERATURE-dependence of the aging — the other axis of the T×t_w map, window-extent, T_eff
  conversion, stretched-exponent fit). None is an in-slice observable withheld; the scalar has no
  current sector by construction.

**The finding.** **The X<1 glassy state is GENUINE WAITING-TIME AGING, not a stationary
effective-temperature state.** Conform reads the t_w-dependence (τ_α grows ∝ t_w, curves non-TTI) as
aging while reading the age-independent X=0.5 as a fixed-imbalance slow manifold — separating the two
signatures cleanly: *timescale grows, imbalance flat*. This **closes the meta-SOP §2-escalated vector
v4 parked twice** (genuine-aging vs stationary-eff-T), and is the WAITING-TIME companion to v9's
TEMPERATURE axis: v9 swept T at fixed age (the equilibrium→aging crossing smears); v10 swept age at
fixed deep-quench T (the cold/aged state is genuinely non-stationary aging). Together v4 (single point),
v9 (T-axis), v10 (t_w-axis) map the Cat-8 aging sector on both of its control axes.

view: deposited as `earned/glass_quench_wait_v10/view_20260526-010803.png`.

---

**Limitation note (added 2026-05-26 — imposed-FDT / data-path independence).** This oracle built the
response χ analytically from C with an IMPOSED slow-mode X=0.5 factor (χ ≠ C0−C on the slow part). The
FDR-locus **bend (slow slope ≈0.5) is genuinely readable** as a distinct functional form (better than the
X=1 tautology of v8/v12) — but the **X=0.5 value was imposed by hand, not produced by independent
dynamics** (a data-path independence gap; WORKFLOW §1). What stands on its own: the AGING signature (the
slow timescale GROWS with the waiting time t_w, the C(τ) curves do NOT collapse — non-stationarity is a
feature of C across the t_w sweep, fully independent of the imposed X), and the two-step structure. What
was imposed, not earned: the X=0.5 magnitude (the "fixed eff-T" value). The corrected method (independent
response ensemble) is demonstrated in v13's re-run; see WORKFLOW §1. Verdict stands as MATCH on the
non-stationary-aging signature; the X=0.5 magnitude is imposed-not-independently-tested.
