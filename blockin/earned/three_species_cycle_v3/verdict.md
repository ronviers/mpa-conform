# verdict — three_species_cycle_v3  (DEV/blind)

**date:** 2026-05-25
**phase:** DEV/blind
**view:** `view_20260525-105030.png`
**script:** `three_species_cycle_v3.answer.py`

---

## placement (framework read)

Direct read of the measured curves at the single supplied operating point
(no model parameters given):

| quantity | measured | meaning |
|---|---|---|
| mean angular velocity `omega = d<phi>/dt` | **1.041 rad / time-unit** (linear fit, R² = 0.9997, RMS resid 0.18) | steady one-way drift of the cumulative turnover angle |
| total winding over the run | **37.98 rad ≈ 6.0 full loops** | the community went around the cycle ~6 times, monotonically |
| angular diffusion `D_phi` | **≈ 10.0 rad²/time-unit** (Var(φ) slope 20.05) | how much the noise smears the steady turning rate |
| FDR-locus signed loop area | **−0.103** (eq. = 0) | broken detailed balance — locus is a loop, not a line |
| FDR-locus departure from origin-line | RMS **0.048 ≈ 9%** of χ span | the equilibrium straight-line prediction fails |
| directed cross-corr antisymmetry `max|Cxy+Cyx|` | **0.0** (exact) | pure rotational/circulating coupling |
| peak `|Cxy|` | 0.330 at lag τ = 0.70, fixed sign | a consistent directed loop x → −y |
| relaxation time `tau_relax` (\|C\| < 5%C₀) | **1.61**; window 36.3 → **~23×** | window long enough; cycling is not a windowing artifact |
| χ plateau | 0.402 (stable, σ ≈ 0) | response saturates cleanly |
| NaN tripwire | all finite | no falsifier tripped |

Both current frames compute **and agree**: Frame A (fluctuation-response locus
off the origin-line) and Frame B (steady winding + antisymmetric cross-corr)
each independently say the system carries a sustained directional current. That
agreement is a pass, not a single-frame artifact.

---

## verdict (researcher's terms)

**This is a REAL, persistent, directional turnover — not damped oscillation that
the noise keeps re-kicking.** The community genuinely circulates one way around
the 1→2→3→1 loop: over your run it completed ~6 full loops at a steady rate of
~1.04 rad per time-unit, and the turnover angle drifts linearly (it never turns
around). A merely noise-excited wobble around a stable coexistence point would
show **no** net winding and would put the response/fluctuation readout on a
straight line through the origin; yours does neither.

**Would calming the environment settle it?** Structurally, **no** — the turning is
intrinsic. The directed cross-correlations are exactly antisymmetric (pure
circulation), which is the fingerprint of the non-reciprocal cyclic loop driving
the system, not of the noise. Reducing the buffeting would shrink the *spread*
around the turning rate (the `D_phi` term), making the cycling **cleaner and more
regular**, but it would not stop the community from going around.

**Headroom — "you are here, with this much room":** you sit firmly in the
persistent-cycling interior; the equilibrium / no-net-turnover edge (`omega → 0`)
is **far**, not adjacent — the drive is ~0.27 loops per relaxation time, i.e. the
current survives many relaxation cycles rather than petering out within one. The
perpetual cycling is a stable feature of this community's structure, not a sign
it is poised on a knife-edge.

---

## grounded[]

- **Driven, not equilibrium** — FDR locus χ vs C(0)−C(τ) traces a **loop** (signed
  area −0.103; RMS departure 9% of χ span) instead of a straight line through the
  origin. Detailed balance is broken. *(observable: chi, C columns; FDR-locus computation in answer.py)*
- **Sustained directional current** — `phiMean` drifts **linearly** with elapsed
  time, `omega = 1.041 rad/t`, R² = 0.9997; total winding 6.0 loops. *(observable: phiMean vs tau; linear fit)*
- **Pure rotational coupling** — directed cross-correlations are **exactly**
  antisymmetric, `max|Cxy+Cyx| = 0`; peak `|Cxy| = 0.330` at τ = 0.70 with fixed
  sign → one-way circulation. *(observable: Cxy, Cyx columns)*
- **Two-frame agreement** — Frame A (FDR-locus loop) and Frame B (winding +
  antisymmetry) independently report a current and **agree**; the cross-check passes. *(both computations above)*
- **Camera/window sane** — C relaxes by τ ≈ 1.6, χ plateaus at 0.402, window is
  ~23× the relaxation time; all values finite. The cycling is not a windowing
  artifact and no NaN tripwire fires. *(observable: C, chi tails; finiteness check)*
- **Noise quantified as spread, not cause** — `D_phi ≈ 10.0 rad²/t` from the linear
  growth of Var(φ): the noise smears the steady turning rate, it does not produce it. *(observable: phiVar vs tau)*

## not_grounded[]

- **Magnitude of the external noise / coupling strengths** — not supplied (no model
  parameters), and one operating point cannot separate the deterministic drive from
  the noise level numerically. We read the drive as intrinsic (steady `omega`), but
  cannot quote *how much* `omega` would change if you actually lowered the buffeting.
  **That needs a noise-level sweep** (several operating points at different noise),
  which this single run does not contain.
- **The literal "calm the environment" counterfactual** — answered *structurally* (the
  current comes from the non-reciprocal cyclic loop, so less noise → smaller spread
  `D_phi`, unchanged drift `omega`), but **not directly measured**. Only a controlled
  noise sweep would close it empirically.
- **Distance to a bifurcation / "edge"** — we place the system in the persistent-cycling
  interior, but "near some edge" presumes a control axis along which an asymptote is
  approached; with one operating point there is no axis to measure headroom along
  beyond the equilibrium (`omega → 0`) direction, which is far here.
- **Per-species rates / which population is "healthiest"** — the data is reduced to the
  2D turnover plane (total abundance held aside), so individual-population health is
  not recoverable. The question does not ask for a winner; none is invented.

---

## verdict label (my honest reading)

**MATCH-intent.** The researcher's core ask — "real persistent turnover vs.
noise-kicked damped oscillation" — is answered decisively and from independent,
agreeing observables: the system is **driven / out of equilibrium with a sustained
one-way current**. The practical follow-up ("would calming the environment stop it")
is answered structurally with the honest empirical limit (needs a noise sweep)
parked in not_grounded[]. No falsifier tripped (all finite; frames agree; no bounded
quantity hit an impossible value), so this is not a KILL.
