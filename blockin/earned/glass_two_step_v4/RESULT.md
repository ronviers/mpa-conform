# RESULT — glass_two_step_v4  (orchestrator's graded record)

**Grade: MATCH** (genuine, richly grounded — no cage_edge, no KILL, not hollow).
Pass run 2026-05-25, DEV/blind. Category 8 (Phase / glassy-critical). Intent I1 (single
operating point). Substrate: `mpa-central/library/primitives/kww_oracle` (sum-of-OU
two-timescale glass; q_EA=0.70, τ_α=5.0, β_KWW=0.60, τ_β=0.005, X=0.50).

This is the **first Cat-8 vertical** and the **first to exercise the aging-FDR /
two-step sector** — a two-step relaxation read as FDT-VIOLATED (X<1) from the two-slope
χ-vs-C locus, which a single-mode Vertex substrate (Cat 1) structurally cannot produce.
It is the clean **X<1 counterpart** to the parked `mm1_queue` tension (FALSIFICATION.md
FINDING 3): there the truth was reversible critical-slowing (X=1) and the trap was
OVER-claiming aging; here the truth is genuine aging (X<1) and the trap (cage_edge 2) is
reading it as equilibrium. The answerer avoided the trap blind.

## What the blind answerer returned (verbatim shape — see `verdict.md`)
- **Verdict:** OUT of equilibrium, not merely slow. The fast population is equilibrated
  (FDR slope ≈1); the slow stuck shoulder lies on the shallower slope X=0.50, so the slow
  sector responds half as much as equilibrium demands — effectively hotter, T_eff/T=2.
  Stable; X finite with a still-relaxing tail → **not AT arrest**.
- **Placement:** two-branch FDR locus χ vs (1−C): fast slope X_fast=0.98≈1, slow slope
  X_slow=0.50 (exact) → T_eff/T=2.00; plateau/shoulder q_EA≈0.69 (knee 0.688, confirmed by
  C-shoulder 0.669); τ_fast≈5×10⁻³ vs τ_α≈5.2 → ~10³× separation; stretched tail β_KWW≈0.63.
- **grounded[]:** out-of-equilibrium (two-slope locus); slow sector hotter (X_slow→T_eff/T=2);
  fast equilibrated (X_fast≈1); q_EA≈0.69 (knee + C plateau); ~10³× separation (C(τ));
  stretched tail β≈0.63. Each tied to the χ/C/τ columns + the FDR-locus/READOUT steps.
- **not_grounded[]:** whether it's about to CROSS arrest (proximity is a control-axis
  derivative — collapsed axis; one point only rules out being AT arrest); absolute T_eff
  (only the ratio; no bath T); aging / waiting-time drift (no t_w axis — collapsed axis);
  mode-resolved fast/slow decomposition (one lumped observable); any current/k_frust read
  (no current; gate correctly dark); uncertainty/grain (no C_sem/χ_sem; n_boot=0).

## Unseal — comparison to `entry.md` sealed_answer
- **MATCH conditions, all met:** read the TWO-STEP structure (did NOT collapse to a single
  Vertex relaxation — cage_edge 1 avoided); read the slow relaxation as FDT-VIOLATED X<1
  from the two-slope locus (did NOT read it as equilibrium critical slowing — cage_edge 2,
  the HEADLINE trap, AVOIDED); placed it stable glassy/aging with a plateau height AND a
  violation magnitude; corrected the naive worry ("not just slow — out of equilibrium").
- **cage_edges — none tripped:** not a single mode (edge 1); not equilibrated-slow/X=1
  (edge 2); not unstable/crossing (edge 3).
- **KILL checks — none fired:** all finite (no NaN); X∈(0,1) (no X>1 super-FDT); fast-branch
  slope ≈1, not >1 (no FDT-bound violation at short lag); plateau in [0,1], C in [−1,1].
- **Over-claim guard — passed:** the answerer did NOT over-claim genuine waiting-time aging
  from one stationary window — it explicitly parked t_w-dependence as a collapsed axis. The
  exact honest line the symmetric-boundary rule (WORKFLOW §4) sets up.
- **Hollow / value-laden guards — passed:** every claim carries provenance; the
  out-of-equilibrium verdict is grounded on the two-slope locus, not guessed; no
  researcher-preference ("healthiest") invented.
- **Computed values vs seal:** X_slow 0.50 vs 0.50 (exact); X_fast 0.98 vs 0.978; q_EA 0.69
  vs 0.70; β_KWW 0.63 vs 0.60 (within the ladder's ±0.08); T_eff/T 2.00 vs 2.00; knee 0.688
  vs 0.700; separation ~10³ vs 10³. All consistent. The seal was freeze-computed from the
  SAME (τ, C, χ) the answerer read.

## Residue / finding
- **The aging-FDR teeth were exercised blind, and they held.** C(τ) alone cannot separate
  equilibrated-slow from aging (both are slow two-step decays); the response χ read against
  C — the two-slope locus — is what does it. The answerer used exactly that instrument and
  caught X<1.
- **The X=1 trap (cage_edge 2) is the clean counterpart to the mm1 FINDING-3 tension.** mm1
  (reversible, X=1) was the OVER-claim-aging trap; this (genuine aging, X<1) is the
  read-it-as-equilibrium trap. Both turn on the same discriminator: the long-lag FDR slope.
  Conform read it correctly on the X<1 side, blind.
- **Park refinement:** the answerer SPLIT a second collapsed-axis park the seal lumped into
  one — "not AT arrest" is groundable from one point, but distance/direction TO arrest is
  not (needs a control-axis sweep). A sharper not_grounded line than the seal specified.
- **Separability:** Cat 8 separated CLEAN from Cat 1 — no smear; the answerer read two
  populations, not one mode. Three categories now separate clean (1, 8, 10), but all three
  landed probes are structurally far apart — the boundary-BLUR test still wants a
  structurally-adjacent pair.

## Next move (gated, see HANDOFF baton)
MATCH → ADVANCE. The owed vector is the t_w (waiting-time) sweep that grounds genuine
aging vs stationary effective-temperature — a multi-point I2/prod move, logged owed
(parked once). Dev-legal alternatives carry forward (a structurally-adjacent pair for the
blur test; the still-owed v3 noise sweep). Authoring stays gated; sealed_answer
freeze-computed.

---

**Limitation note (added 2026-05-26 — imposed-FDT / data-path independence).** This kww oracle built the
response χ analytically from C with an IMPOSED slow-mode X=0.5 factor (χ ≠ C0−C on the slow part). The
FDR-locus **two-slope bend (fast≈1, slow≈0.5) is genuinely readable** as a distinct functional form
(better than an X=1 tautology) — but the **X=0.5 was imposed by hand, not produced by independent
dynamics** (a data-path independence gap; WORKFLOW §1). What stands on its own: the two-step structure
(plateau + stretched tail) and the aging DIRECTION (slow part out of balance). What was imposed, not
earned: the X=0.5 magnitude. The corrected method (measure χ from an INDEPENDENT response ensemble so X
emerges) is demonstrated in v13's corrected re-run; see WORKFLOW §1 response-independence rule. Verdict
stands as MATCH on the structure + aging direction; the X=0.5 magnitude is imposed-not-independently-tested.
