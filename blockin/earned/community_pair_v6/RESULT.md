# community_pair_v6 — BLIND ANSWERER verdict

phase: DEV/blind · view: `view_20260525-174923.png`
inputs read: `community_pair_v6.packet.md`, `community_pair_v6.data.csv`,
`community_pair_v6.traversal.md`, WORKFLOW §1/§5/§6, `view_header.py`. Nothing else.

---

## Kernel / observation-window sanity (run first)

Both communities' autocorrelation C(τ) decays essentially to zero inside the supplied
window (C(end)/C(0) = 2.8e-4 for comm0, ~0 for comm1). So each observation window
**covers its process** — the "wiggling never stops" the researcher sees is the
within-window signal, not a window-too-short artifact. All columns finite for both
communities — **no NaN/inf tripwire fired, no boundary attained**.

---

## Per-system placement (each placed independently first)

**Community 0 — settling with noise (no current).**
- Autocorrelation: **monotone exponential decay**, no zero crossing (Cmin = 0.0003),
  τ_relax ≈ 2.43, ω = 0.
- Directed cross-correlation: **symmetric**, Cxy = Cyx exactly (‖Cxy−Cyx‖ = 0) →
  no in-plane directed flow.
- Net turnover angle phiMean(t): essentially **flat**, rate −0.026/clock, total −0.47 rad
  (≈ −0.07 turns over the whole run) — wanders around 0, no net going-around.
- FDR locus χ vs C(0)−C: **clean affine, R² = 1.000** → pure relaxational / FDT settling.
- placement: `monotone-decay, τ_relax=2.43, ω=0, winding≈0, Cxy=Cyx (sym), χ_plateau=1.516, FDR R²=1.000`

**Community 1 — genuine persistent turnover (a circulating current).**
- Autocorrelation: **damped oscillation** — C rings through zero (Cmin = −0.073),
  fit γ ≈ 1.03, ω ≈ 1.11, τ_relax ≈ 0.97.
- Directed cross-correlation: **antisymmetric**, Cxy = −Cyx (‖Cxy+Cyx‖ = 0) → a
  rotation / circulating current in the turnover plane.
- Net turnover angle phiMean(t): **climbs steadily and almost perfectly linearly**, rate
  +1.05/clock, total +37.5 rad ≈ **+6.0 full turns** around the loop (residual about the
  line only 0.15 rad) — really goes around, over and over, never settling.
- FDR locus χ vs C(0)−C: **non-affine, R² = 0.704** — expected, because a ringing C makes
  χ not a simple function of C(0)−C; the locus shape *agrees with* the oscillatory read.
- placement: `damped-osc γ=1.027 ω=1.114 (τ_relax=0.97), winding=+1.053/clk (~6 turns), Cxy=−Cyx (antisym), χ_plateau=0.402, FDR R²=0.704`

---

## Verdict in the researcher's terms

- **Community 0: it is settling with noise.** The swinging is the community relaxing
  toward a steady balance with the noise jiggling it around that balance — it is *not*
  going around its loop. You are at the no-net-turnover balance point.
- **Community 1: it is genuine, persistent turnover.** It really circulates around the
  loop — about six full turns over your window and still going at a steady rate, with a
  clear rotation in the abundance plane. The angle never settles.
- **Same kind, or different? DIFFERENT.** The two look alike by eye, but they are
  genuinely different systems. The observable that carries it: the **net cumulative
  turnover angle** (phiMean climbs for 1, stays flat for 0), corroborated by the
  **cross-correlation symmetry** (antisymmetric Cxy/Cyx for 1 = a current; symmetric for
  0 = none) and the **autocorrelation shape** (rings for 1, monotone for 0). Three
  independent reads agree, so the difference is real, not a fluke of one statistic.
- **Unstable / near an edge? No — both are healthy / interior.** Both autocorrelations
  relax to zero with a finite decay time and nothing goes non-finite, so neither is
  blowing up or sitting on an edge. Community 1's relentless turnover is a **stable
  circulation**, not an instability — persistent cycling and "near a blow-up edge" are
  different things, and the data says circulation, not edge.

You are here: community 0 at a noisy fixed balance; community 1 on a steady, stable
circulation — both well inside the stable interior.

---

## grounded[]

1. **Per-community independent placement** — each community fit on its own columns first
   (C, χ, Cxy, Cyx, phiMean, phiVar), then related; the "different" call is read off the
   placements, not assumed.
2. **Settle vs turnover [autocorrelation C]** — comm0 monotone decay to 0 (Cmin 0.0003,
   no zero crossing); comm1 rings through zero (Cmin −0.073) → damped oscillation.
3. **Directed flow / current [Cxy vs Cyx symmetry]** — comm0 symmetric (‖Cxy−Cyx‖≈0, no
   current); comm1 antisymmetric (‖Cxy+Cyx‖≈0) → a rotation / circulating current.
4. **Persistent turnover [phiMean(t) slope = net winding]** — comm0 rate −0.026/clk,
   total −0.47 rad (no net winding); comm1 rate +1.053/clk, total +37.5 rad (~6 turns)
   → goes round the loop.
5. **FDR locus cross-check [χ vs C(0)−C]** — comm0 clean affine R²=1.000 (pure
   relaxational); comm1 non-affine R²=0.704 (because C rings) — the locus shape agrees
   with the autocorrelation read on both communities; the two independent reads do not
   disagree (no falsifier tripped).
6. **Stability / healthy [C relaxes + finite guard]** — both autocorrelations decay to ~0
   inside the window (C_end/C0 = 2.8e-4, ~0); all columns finite (no NaN/inf, no boundary
   attained) → neither unstable.
7. **Window sanity [kernel pre-gate]** — autocorrelation has died by the end of each
   window → the observation window covers the process for both communities.

---

## not_grounded[] (the honest limit)

1. **Absolute coupling strengths / the interaction-arrangement parameters** — the
   researcher's own loop-coupling magnitudes are not in the data (only measured curves).
   We read *that* there is a difference and *on which observable*, not the underlying
   parameter values that produced it.
2. **Noise amplitudes / environmental drive level** — not a column. The angular-diffusion
   rate (phiVar slope: 10.9/clk comm0, 15.7/clk comm1) is a proxy for jiggle but cannot
   be separated into noise-strength vs coupling **without a second operating point**.
3. **Two-sided headroom / distance-to-instability in native units** — each community is
   **one operating point** (one observation window). A single point *places* the system
   but cannot span the load axis: how far comm1's circulation sits from a bifurcation, or
   how close comm0 is to an oscillatory onset, would need a **sweep** (a second operating
   point / a varied arrangement). This is un-groundable because it lives across a
   **collapsed axis**, not because we failed to compute it.
4. **Effective temperature / FDR slope as a calibrated quantity** — the χ-vs-(C0−C) slope
   is consistent and affine for comm0, but without an independent temperature/units
   channel it is a shape cross-check, not an absolute T_eff.
5. **Researcher *preference* (which community is "better"/"more desirable")** — not
   computable and not a placement; both are healthy/interior. Any "which is preferable"
   is an interpretive **dial** for the (inert) viewport — surfaced here, not decided
   (per §6 value-laden-verdict guard).

---

## view

`H:\mpa-conform\blockin\workspace\view_20260525-174923.png` — header band (question
broken down + verdict + placement + grounded/not_grounded) over four data-mapped plots:
(1) C(τ) settle-vs-ring, (2) FDR locus χ vs C0−C, (3) Cxy/Cyx symmetry,
(4) **the band** — cumulative turnover angle phiMean(t) with ±√phiVar envelopes, the one
box that carries the same/different story (comm0 flat, comm1 climbing ~6 turns).

## meta-validity / slice note

Slice collapsed: each community = one operating point (the load/arrangement axis is NOT
spanned). not_grounded #1–#4 all fall out of that collapsed axis, not out of withheld
in-slice observables — every column the researcher's measurement contains was used.
Verdict: **MATCH-shaped** (two systems placed, related on a grounded observable), with
the two-sided headroom honestly parked as the single-operating-point limit.
