# observation_window_sweep_v13 — BLIND PASS RESULT (corrected re-run, independent-MC)

phase: DEV/blind · view: `view_20260526-080546.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

**Correction note (2026-05-26).** The first v13 oracle set the response ANALYTICALLY as χ(τ)=C(0)−C(τ)
— it IMPOSED the equilibrium FDT relation. That made χ the algebraic mirror of C, so the FDR locus
χ vs (C₀−C) was the IDENTITY by construction and the "X=1 / FDT holds" reading was **tautological**, not
a tested fact — a data-path-independence violation (WORKFLOW §1: "the sim makes the data, analytics makes
the truth; conform is the examinee, never the answer key"). Ron caught it ("the in's and out's look like
each other w.r.t. time — that doesn't seem possible": two genuinely independent measurements cannot be
exact mirrors). **This re-run fixes it:** C and χ are now TWO INDEPENDENT Monte-Carlo measurements of the
same equilibrium substrate, so FDT/X=1 EMERGES within MC noise rather than being typed in. The blind
answerer's slope-≈1 reading is now genuine. The original (flawed) earned record is superseded by this one;
git history holds the prior version.

A sweep: one fluctuating signal's autocorrelation C and integrated step-response chi, at **32 OBSERVATION
DURATIONS** (level 0 shortest watch → level 31 longest, τ_obs log-spaced 3→30000). The swept axis is the
**CAMERA** (observation window / τ_obs), NOT a substrate knob — the Cat-5 mark.

**Substrate (corrected):** two independent Ornstein-Uhlenbeck modes at ONE temperature T=1 — fast τ_f=1
(var 1), slow τ_s=1000 (var 1000) — observed via y=c_f·x_f+c_s·x_s with weights a_f=0.4, a_s=0.6
(decoupled from the timescales). True C(τ)=0.4·e^(−τ/τ_f)+0.6·e^(−τ/τ_s). **C is measured from a
fluctuation ensemble; χ from a SEPARATE perturbation ensemble** (step field h conjugate to y; OU linear
→ exact-linear response). Independence check: max|χ−(C₀−C)|=0.056, rms 0.016 over the master grid —
NONZERO (the two measurements differ by MC noise; if χ were imposed = C₀−C this would be exactly 0). The
answer-path truth (X=1, equilibrium FDT) is analytic; the data are MC, never via conform.

This LANDS **Cat 5 (Kernel / camera / τ_obs)** — the kernel pre-gate's own job (WORKFLOW §E; RFC-S §0.2
"τ_obs is the camera"): is an apparent character the SUBSTRATE or the OBSERVATION WINDOW?

---

## The band (what migrates / what stays put)
- **Migrates (the camera artifact):** the apparent frozen-shelf height MELTS monotonically from 0.631
  (shortest watch) to ~0 (longest watch) across the 32 windows — the slow mode was under-resolved by short
  watches and fully relaxes given enough observation.
- **Stays put (the invariant — the substrate, not the camera):** the FDR slope ≈1 (X=1) at every window
  (per-window mean 0.997, range 0.976–1.030 — EMERGENT from two independent MC ensembles, within noise),
  and the signal's intrinsic two timescales / early-curve shape (overlapping-lag curves coincide).

## Verdict in the researcher's own terms
- **Genuinely stuck, or artifact?** A watching-time (camera) artifact — no genuinely frozen component; the
  shelf melts to ~0 as the watch lengthens.
- **A "right" window?** Long enough to reach the final decay (~level 31); no privileged intermediate window.
- **In balance?** In balance (X≈1, emergent) — the stuck-looking shelf is an unresolved slow equilibrium
  mode, not an out-of-balance/aging plateau.

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **Camera-artifact signature recovered:** apparent plateau melts 0.631→0.003 across 32 windows ✓.
- **X≈1 recovered as EMERGENT (the fix):** sealed emergent slope ~0.997 (range 0.976–1.030); blind read
  0.997±0.014, "no systematic bend below 1, scatter consistent with ~1–2% measurement noise" ✓. Crucially
  the answerer PARKED "whether X is exactly 1 ... C and χ are separate noisy ensembles, so a sub-percent
  violation is below resolution" — i.e. it read an emergent FDT from independent measurements, NOT an
  imposed identity. **This is the proof the data-path-independence fix worked.**
- Headline tooth hit (cage_edge 1): camera artifact, not a genuine stuck/non-ergodic component ✓. All five
  cage_edges avoided, incl. camera-not-substrate (signal fixed across runs) and X≈1-not-aging.
- **Not hollow** (every claim grounded), **no KILL** (no NaN, no X>1, no current). **Meta-validity P held.**
- **Anchor (soft, first contact):** FOIL to v4 — the short-window shelf mimics v4's intrinsic glass q_EA,
  but the melt + emergent X≈1 unmask it as a camera artifact (vs v4's intrinsic X<1, fixed q_EA).
- **Boundary symmetry (§4):** `not_grounded[]` items all collapsed-axis / honest-limit parks (native
  timescales, past-window, exact mode count, X-to-sub-percent). Clean.

**The finding (unchanged physics, now genuinely tested).** **The apparent frozen plateau is a CAMERA
(observation-window) artifact (Cat 5), not intrinsic non-ergodicity** — "the problem is the camera, not the
substrate." With the corrected oracle the in-balance (X≈1) leg of that finding is now an EMERGENT FDT from
two independent measurements, not an imposed identity. The camera-artifact FOIL to v4/v9/v10's intrinsic
glass stands. **Methodological finding (the reason for the re-run):** an analytic oracle must compute the
response χ INDEPENDENTLY of the correlation C — never χ=C₀−C by fiat — or the FDR/X reading is tautological.
Now a standing WORKFLOW rule.

view: deposited as `earned/observation_window_sweep_v13/view_20260526-080546.png` — 32-box camera movie
(now showing genuinely-measured, noisy C(τ) per window) + the melt-band + emergent-slope-≈1 band.
