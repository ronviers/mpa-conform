# observation_window_sweep_v13 — BLIND PASS RESULT

phase: DEV/blind · view: `view_20260526-072725.png` · analysis: `answer.py` · verdict: `verdict.md` · grade: **MATCH** (two-sided)

A sweep: one fluctuating signal's autocorrelation C and integrated response chi, at **32 OBSERVATION
DURATIONS** (level 0 shortest watch → level 31 longest, τ_obs log-spaced 3→30000, ~4 decades). The
swept axis is the **CAMERA** (the observation window / τ_obs), NOT a substrate parameter — that is the
distinguishing mark of Cat 5. Per WORKFLOW §6, each window placed as an **independent single-point fit
first**, then the band read off the 32 placements.

The substrate is a two-timescale **equilibrium oracle**: a FIXED two-exponential autocorrelation
C(τ)=a_f·exp(−τ/τ_f)+a_s·exp(−τ/τ_s) (τ_f=1, τ_s=1000, a_f=0.4, a_s=0.6), with the equilibrium FDT
χ=(C(0)−C(τ))/T (T=1 → X=1 at every lag). The CAMERA is τ_obs (window length); sampling is fixed-fine
so the FAST mode is always resolved and only the SLOW mode's resolution is window-controlled. Truth from
the analytic two-exponential + FDT, never via conform (see `entry.md` SEALED half /
`freeze_observation_window.py`).

This LANDS **Cat 5 (Kernel / camera / τ_obs)** — a NEW (fifth) category. Cat 5 is the kernel pre-gate's
own job (WORKFLOW §E; RFC-S §0.2 "τ_obs is the camera"): is an apparent character a property of the
SUBSTRATE or of the OBSERVATION WINDOW? Here the short-window "frozen plateau" mimics a glass q_EA but is
unmasked as a camera artifact.

---

## The band (what migrates / what stays put)
- **Migrates (the camera artifact):** the apparent frozen-shelf height MELTS monotonically from 0.618
  (shortest watch) to ~0 (longest watch) across the 32 windows — the slow mode was simply under-resolved
  by short watches and fully relaxes given enough observation.
- **Stays put (the invariant — the substrate, not the camera):** the FDR slope = 1 (X=1) at every window
  (χ=C(0)−C(τ) to 5e-9 — the FDT sum rule), and the signal's early-curve shape is identical across runs
  (level-0 vs level-31 overlap diff 3.3e-3). The intrinsic two timescales and the equilibrium character
  are window-invariant.

## Verdict in the researcher's own terms
- **Genuinely stuck, or artifact?** A watching-time (camera) artifact — no genuinely frozen component;
  the shelf melts to zero as the watch lengthens.
- **A "right" window?** Long enough to reach the floor (~level 27+); shorter windows under-resolve the
  slow part. No privileged single window, just "watch past the slow timescale."
- **In balance?** In balance (X=1) at every window — the stuck-looking shelf was never a violation, just
  an unfinished relaxation.

## Unseal / grade (orchestrator)
**MATCH (two-sided, blind).** Against `entry.md` SEALED:
- **Camera-artifact signature recovered EXACTLY:** sealed apparent plateau melts 0.618→0; blind shelf
  melts 0.618→5.6e-14 monotonically across the 32 windows ✓.
- **X=1 recovered EXACTLY:** sealed FDR slope 1 at every window; blind 1.00000 at all 32 + the FDT sum
  rule χ=C(0)−C(τ) to 5e-9 ✓.
- **The two teeth landed:** the plateau MELTS (camera, not intrinsic) AND X=1 in-balance (equilibrium,
  not a glass) — exactly the camera-artifact-vs-glass discriminator the design turns on ✓.
- **Headline tooth hit** (cage_edge 1): read as a camera/watching-time artifact, NOT a genuine
  stuck/non-ergodic component ✓. All other cage_edges avoided — including the two subtlest: the answerer
  attributed the change to the CAMERA not the SIGNAL (cage_edge 3 — verified the signal identical across
  runs, overlap 3.3e-3) and read X=1 in-balance not aging (cage_edge 5, the Cat-8 misread); also not
  window-independent (cage_edge 2) and not single-timescale (cage_edge 4) ✓.
- **Not hollow** — every claim grounded on a computed observable (shelf melt, FDR slope, sum rule,
  overlap invariance) ✓. **Meta-validity P held** — independent per-window placements, then band ✓.
- **No KILL:** no NaN, no X>1 (X=1), no current, ground-truth plateau melts + X=1 (freeze-confirmed).
- **Anchor (soft, first contact):** no prior earned camera/τ_obs point. Conceptual FOIL to v4 (kww
  glass): the short-window shelf mimics v4's q_EA, but the melt + X=1 unmask it as a camera artifact —
  the OPPOSITE of v4's intrinsic q_EA with X<1. Consistency by contrast holds; no hard numeric anchor.
- **Boundary symmetry (§4):** every `not_grounded[]` item is a collapsed-axis / honest-limit park (native
  timescales in physical units; behaviour past the longest window; exact slow-mode form; substrate
  identity; exact-vs-measured early-curve agreement). None withheld in-slice; equilibrium scalar has no
  current sector.

**The finding.** **Cat 5 LANDS: the apparent frozen plateau is a CAMERA (observation-window) artifact,
not an intrinsic stuck component** — "the problem is the camera, not the substrate." Conform reads the
τ_obs-migration as the camera/RG-flow trajectory (the substrate's intrinsic content is τ_obs-invariant;
only the apparent non-ergodicity migrates), grounding it on the plateau MELTING across windows + the
slope-1 (X=1) locus. This is the camera-artifact FOIL to v4/v9/v10's intrinsic glass (there the q_EA
plateau is real, X<1, and does NOT melt; here it is a window artifact, X=1, and melts). The kernel
pre-gate's own job — distinguishing a substrate property from a camera artifact — landed blind. Note: the
swept axis being the camera (not a substrate knob) makes this the structural complement to the other
sweeps (v5/v7/v8/v9/v10/v11/v12 all moved a substrate parameter; v13 moves the observer at fixed
substrate).

view: deposited as `earned/observation_window_sweep_v13/view_20260526-072725.png` — a 32-box camera
movie (one C(τ) box per observation window, the shelf melting across the grid) + the melt-band and
flat-X=1 band boxes.
