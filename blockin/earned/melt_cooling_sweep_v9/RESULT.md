# melt_cooling_sweep_v9 — BLIND PASS RESULT

phase: DEV/blind · view: `view_20260525-210438.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

A sweep: one supercooled melt's fluctuation correlation C and integrated response chi, at 5
temperatures cooled through its glass transition Tg (level 0..4; level 0 warmest, level 4 coldest;
Tg at level 1). Per WORKFLOW §6, each level placed as an **independent single-point fit first**, then
the band read off the 5 placements. Each level on its own clock (windows grow ~15→2250, matched to
each level's own diverging alpha-relaxation).

The substrate is a **glass-transition oracle** (the v8 analytic-correlator construction applied to
the v4 two-step KWW form): a two-timescale connected fluctuation correlator swept across Tg. Truth
from the equilibrium/aging FDT structure, never via conform — X = T/T_eff is encoded directly as the
slow-mode FDT ratio, X DERIVED from the alpha-time fall-out rule (see `entry.md` SEALED half /
`freeze_glass_transition.py`).

---

## Per-level placement (the framework read)

| level | role | X (slow-seg slope) | fast slope | C plateau (obs) | terminal shortfall | tau_max | kind |
|---|---|---|---|---|---|---|---|
| 0 | warmest | 1.00 | 1.00 | — (single decay) | 0.000 | 15 | equilibrium |
| 1 | Tg | 1.00 | 1.00 | — (single decay) | 0.000 | 45 | equilibrium |
| 2 | | 0.83 | 0.98 | 0.50 | 0.094 | 150 | partially aged |
| 3 | | 0.63 | 0.97 | 0.65 | 0.249 | 600 | partially aged |
| 4 | coldest | 0.50 | 0.96 | 0.78 | 0.395 | 2250 | deep aging |

- **FDR locus (universal readout):** levels 0–1 are a single straight line of slope 1 (chi+C=1.000 at
  every lag) → X=1, equilibrium. Levels 2–4 the locus BENDS — fast segment slope ~1, then a shallower
  slow segment of slope X<1 read past the plateau knee → out of equilibrium, aging.
- **Two-step structure:** a fast partial drop to a plateau, then a slow stretched tail; the plateau
  deepens and the slow time lengthens on cooling. (At warm levels the two-step is unresolved — too
  little timescale separation for the plateau to appear as a shelf; correctly read as single-decay.)

## The band (what migrates / what stays put)
- **X crosses SMOOTHLY 1.00 → 1.00 → 0.83 → 0.63 → 0.50** warm→cold — a graded crossover, NOT a jump.
  The fast-segment slope stays ~1 everywhere; the slow segment is what bends down. Middle levels (2–3)
  sit at INTERMEDIATE X (partially aged), not snapped to either extreme.
- **Migrates:** plateau height 0.05→0.78, slow timescale tau_max 15→2250 (~150×). **Stays put:** the
  fast-segment near-equilibrium slope.

## Verdict in the researcher's own terms
- **Just slow, or genuinely out of equilibrium?** Warm (L0–1): in balance, X=1 — an ordinary liquid
  that is merely slow. Cold (L2–4): genuinely fallen out of equilibrium and aging — the response no
  longer keeps up with the fluctuations on the slow part (locus bends, X<1).
- **Abrupt or gradual?** **GRADUAL — a crossover.** X slides monotonically with no single switch;
  the middle settings are partway out of balance (≈¾, then ≈⅔ of the way). The change of KIND
  (equilibrium → aging) is real but SMEARS over the cooling range.
- **How far out, per level?** warm: in balance (X=1); middle: partway (X≈0.83, ≈0.63); cold: well out
  (X≈0.50, response ~half what equilibrium would give on the slow modes).
- **Naive worry corrected, both ways:** "it has just gotten slow" is incomplete (cold settings are
  genuinely aging, not merely slowed); and "it's all glassy" is wrong for the warm levels (X=1 there).

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **Load-bearing X band recovered EXACTLY:** sealed `[1.00, 1.00, 0.827, 0.629, 0.50]` vs blind
  `[1.00, 1.00, 0.83, 0.63, 0.50]` ✓.
- Per-level kind placed correctly: warm = reversible equilibrium (X=1, single-slope locus), cold =
  out-of-equilibrium aging (bent locus, slow slope X<1) ✓.
- **Headline tooth hit** (cage_edge 3, the SMEAR): read as a GRADUAL crossover with intermediate-X
  middle levels — NOT a sharp jump, NOT a binary equilibrium/glass split ✓.
- Both naive readings corrected: under-read "just slow" (cage_edge 1) ✓ and over-read "all glassy"
  (cage_edge 2) ✓.
- Two-step read, not collapsed to a single relaxation (cage_edge 4) ✓; no false oscillation/current
  (cage_edge 5) ✓.
- **Not hollow** — every claim grounded on a computed observable (locus slope, terminal shortfall,
  tau_max, plateau height) ✓. **Meta-validity P held** — independent per-level placements, then band ✓.
- **No KILL:** no NaN, no X>1 (max 1.00), no current, ground-truth X = the freeze-prescribed crossover.
- **Anchor-and-assert (soft):** first sweep on this oracle — no hard anchor. Level 4 is a v4-family
  deep-aging point (X=0.5); v4 read X≈0.50, blind L4 X=0.50 — cross-pass consistency holds (consistent
  with the seal).
- **Boundary symmetry (§4):** every `not_grounded[]` item is a legitimate collapsed-axis park (native
  temperatures = v7/v8's re-derived native-unit limit; waiting-time t_w = v4's owed vector; lag past
  each window; stretched-exponent separate fit; precise switch temperature in ordinal data). None is an
  in-slice observable withheld; the scalar has no current sector by construction.

**The finding.** v9 is the **FIRST axis tested that SMEARS.** A metric axis crossing a genuine
DYNAMICAL-category boundary (equilibrium → aging, X:1→<1 — the glass through Tg) is a smooth KINETIC
crossover: X drops 1→0.5 gradually and the intermediate levels are partially aged. This is distinct
from the topologically-sharp reciprocity cut (v6) and the no-kind-change metric axes (v7/v8), and it
is the X<1 (aging) dynamical-crossing counterpart to v8's X=1 (equilibrium) thermodynamic crossing.
It **closes the separability hypothesis with a positive result**: real dynamical-category crossings,
being kinetic, DO smear — and conform RESOLVES the intermediate-X gradient (places the mid levels as
partially aged) rather than snapping to a binary label.

Minor note: the answerer's warm-level "plateau" column reads min-C (0.05/0.03), not the freeze's q_EA
shelf (0.30/0.40) — correct, because at warm levels the timescale separation is too small for q_EA to
resolve as a shelf; the answerer rightly called L0/L1 "single decay." q_EA only becomes an observable
plateau once the cold levels open the separation (cold plateaus 0.50/0.65/0.78 ≈ sealed q_EA
0.55/0.68/0.80). Not verdict-affecting; a small reminder that q_EA is read-through (not measured) in
the equilibrium regime.

view: deposited as `earned/melt_cooling_sweep_v9/view_20260525-210438.png`.
