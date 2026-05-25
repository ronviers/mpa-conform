# PIPELINE — the object under study (conform's data-prep silhouette)

This is the **pipeline**: MPA's data-prep machinery that takes a researcher's
`(question, data)` and produces a characterization + a view. It is the *object*
we are blocking in — one of four modules (PIPELINE = object · WORKFLOW = pass-SOP ·
meta-SOP = evolution · HANDOFF = baton). It is NOT the workflow: the **pass-SOP**
(how one pass traverses this pipeline; the A–P interrogation box) lives in
`WORKFLOW.md`, and how passes *evolve* this doc lives in `meta-SOP.md`. The pass-SOP
*wraps* this; its single "answerer-session" step **is** one traversal here. Thin seam:
blind packet + data in, view + verdict out.

> **STATUS: THREE CATEGORIES LANDED (3 clean verticals + 1 MISS-with-finding, all blind).**
> `laser_ro_nominal_v1` (Vertex/Cat 1) traversed the spine ADMISSION → FRAME → SELECTION(I1)
> → ROOT OP → READOUT; `three_species_cycle_v3` (Cat 10, non-reciprocal) added the GATES
> current-sector — the two-frame readout reached and agreed, blind; `glass_two_step_v4`
> (Cat 8, Phase/glassy) added the aging-FDR sector — a two-step relaxation read as
> FDT-violated (X<1) from the two-slope χ-vs-C locus, blind. `laser_ro_pump_sweep_v2`
> (Vertex sweep) graded MISS-with-finding (a viewer-layer dial, deferred). Earned contours
> are `[EARNED]`/`[CONTACT]` below; the rest is still cage, not surface. The ROOT OP held exactly (Banach
> damped-oscillator placed at RMS 3e-7). The READOUT headroom is where the silhouette
> buckled (see its note) — and the buckle reproduced under genuine blinding. This doc accretes (earned contours) and contracts
> (as the silhouette firms). The arrow correction is baked in: the root operation is
> inversion conforming Banach **to** the pristine substrate — never the reverse.

(Status, earned contours, and finding/buckle notes live as **blockquotes** or
`[EARNED v=…]` / `[CONTACT v=…]` tags. That is not cosmetic: `pose.py` strips exactly
those forms when it emits the blind answerer's sanitized traversal, then fail-closes if
any substrate/answer token survives. The plain-text steps below are the generic recipe —
keep them substrate-neutral, or the traversal sanitizer will refuse to pose.)

---

## INVARIANTS — hold at every step (one rule each, no branching)
- **The arrow:** substrate pristine and fixed; Banach is conformed *to* it; never the
  reverse. (Topology — kept even in dev.)
- Operate only on Banach (regenerable); never touch the substrate → collapses the
  whole modify-safety / reversibility worry-class.
- **FDR locus = universal readout** (χ vs C₀−C); category-native columns are
  cross-checks, not instruments.
- Data-path independence: the sim makes the data, analytics makes the truth.
- Blinding: the researcher-voice packet leaks no framework.
- Conform is the examinee, never the answer key.
- Falsifier tripwires armed throughout (see Readout).

---

## The traversal (sparsification modules, in order)

### 0 · ADMISSION GATE  `[EARNED v=laser_ro_nominal_v1]`
- Units present per column; C and χ dimensionless?
- Provenance / citation / license present; reproducibility hash?
- Meets the contract — admit or reject?
- "Our data" (clean ground truth) or on the contaminated hold-list?
- **[dev]** loosened — convenience data admitted. **[prod]** full contract-05.

### 1 · FRAME — camera (τ_obs) · *gate, resolve first*  `[EARNED v=laser_ro_nominal_v1]`
- τ_obs declared, or must it be derived?
- Clean intrinsic time, or ambiguous (→0 floor / →∞)?
- Window matched to the process, or is the "failure" a camera artifact?
- τ_obs sweep: labels migrate (expected) while k_frust stays invariant (required)?
- k_frust migrates with τ_obs → detection artifact → preprocess (e_i = s_i ⊕ s_{i−1})?
- Any stable window? If none → the problem *is* the camera (Cat 5).
- tau_scale to dimensionless lag — logged, reversible?
- One operating point, or already a τ_obs / control sweep?
- **[dev]** keep camera-first ordering (topology); relax precision — declare a
  convenient window. **[prod]** derive τ_obs honestly (brain/QEC placement is real work).

### 2 · SELECTION — intent × minimal-structure · *picks the live slice; most stays dark*  `[EARNED v=laser_ro_nominal_v1 — I1/vertex; separability CLEAN]` `[EARNED v=three_species_cycle_v3 — I1/Cat-10 non-reciprocal; first NON-Vertex datapoint, separability 1-vs-10 CLEAN]` `[EARNED v=glass_two_step_v4 — I1/Cat-8 Phase glassy two-step; separability 1-vs-8 CLEAN, no smear]` `[EARNED v=three_species_cycle_noise_sweep_v5 — I2/Cat-10 noise sweep on the v3 dot; noise-INDEPENDENCE of the current rate GROUNDED, blind]`
> **Separability datapoint (three_species_cycle_v3):** the first non-Vertex substrate
> landed CLEAN — a blind answerer separated a sustained directional CIRCULATION (Cat 10)
> from a reciprocal RING-DOWN (Cat 1) even though their autocorrelation C(τ) is the same
> damped cosine. The discriminator that did it is the cross-correlation antisymmetry
> (Cxy != Cyx); the structure did NOT smear into Vertex. n=1 cross-category test so far,
> but the 1↔10 boundary reads sharp on that observable.
> **Separability datapoint (glass_two_step_v4):** a second non-Vertex category landed
> CLEAN. A blind answerer read a two-step relaxation (a fast drop to a frozen-in plateau,
> then a stretched slow tail) as TWO populations — it did NOT collapse the slow tail to a
> single Vertex relaxation time. The discriminators: the plateau/shoulder in C(τ) (a
> separation of timescales, here ~10³×) and the stretched (β_KWW<1) tail. Cat 8 did not
> smear into Cat 1. Three categories now separate clean (1, 8, 10); the three landed
> probes were structurally far apart, so the boundary-BLUR test still wants a
> structurally-adjacent pair (HANDOFF §hypothesis).
- *Question:* researcher's words; nominal-check / placement / comparison / headroom /
  "why"? baseline expectation? one channel or several?
- *Intent:* which of I1–I5? more than one, in what order? supported at this dev stage?
  data shape agrees (point ↔ I1/I5; spanning ↔ I2)?
- *Structure:* minimal structure (the gate); nodes/edges, vertex/edge/cycle; reciprocal
  or non-reciprocal; **current-bearing?** (feeds the current-gate); category (1–10);
  substrate's field (voice/units); native observables, and which one they're watching.
- *Separability (open Wall-test):* does structure land clean or **smear**? — i.e. is this
  axis a valid modular cut at all?
- **[dev]** downstream intents (I1/I5) always; **I2 (sweep/migration) admitted in dev WHEN
  built as stitched isolated placements** — each point an independent I1 fit + one band
  readout, which keeps the fit intent-independent and a MISS localizable (meta-validity P).
  **[prod]** the full I2 migration fit (trajectory machinery reaching into the fit's scope).

### 3 · ROOT OPERATION — inversion conforms Banach to the substrate · *the measurement; subsumption hub*  `[EARNED v=laser_ro_nominal_v1 — 1-param placement EXACT on a vertex]`
- Conform Banach to the (working) substrate — the fit *is* the measurement.
- Placement (chit)? regime? confidence/residual? which observable constrained it?
  γ_AB constrained or free?
- 1-param chit enough for this intent, or the 5-vector refinement?
- *Lens/map:* region of interest; the fitted TranslationField (substrate-native ↔
  canonical); forward-only; round-trip residual (I4); where the asymptotes sit relative
  to the fit (the coordinates that give headroom meaning).
- *The fitted Banach:* which family member, how deformed = **the character**; deviation
  from canonical Banach.
- **[dev]** keep the arrow (winding); relax fit precision/tolerances. **[prod]**
  evidence-grade fit; lens round-trip enforced.

### 4 · GATES — booleans that connect/disconnect whole sub-modules  `[CONTACT v=three_species_cycle_v3 — current-gate OPENED; two-frame sector reached & AGREE, blind]` `[CONTACT v=glass_two_step_v4 — in-family/identifiability gate: two-step 5-vector (q_EA, β_KWW, X) read from ONE (C,χ); aging X<1 separated from equilibrium X=1, blind]` `[CONTACT v=three_species_cycle_noise_sweep_v5 — current-gate "noise-independent?" sub-question CLOSED: current rate flat to <6% over 20× noise, blind]`
> **First-contact finding (glass_two_step_v4):** the **grain/in-family → identifiability**
> gate reached its first genuinely multi-timescale substrate. A blind answerer recovered
> the two-step structure from a single (C, χ) pair: the plateau height q_EA≈0.69, the
> stretched-tail exponent β_KWW≈0.63, and — the teeth — the slow-mode FDT-violation
> X≈0.50 read off the TWO-SLOPE FDR locus (slope ≈1 on the fast branch up to the plateau
> knee, then slope X<1 on the slow branch). C(τ) ALONE is a slow two-step decay either way;
> the response χ read against C is what separates "out-of-equilibrium aging" (X<1) from
> "equilibrated but slow" (X=1). The answerer avoided the equilibrium-collapse trap — the
> clean X<1 counterpart to the parked `mm1_queue` tension (FALSIFICATION.md FINDING 3: there
> the truth was reversible critical-slowing X=1 and the trap was OVER-claiming aging). The
> honest park is across a COLLAPSED AXIS: a stationary window cannot say whether X<1 is
> genuine waiting-time (t_w-dependent) aging or a stationary effective-temperature — and the
> answerer split a second collapsed-axis park the seal under-specified ("not AT arrest" is
> groundable, but distance/direction TO arrest needs a control-axis sweep).
> **First-contact finding (three_species_cycle_v3):** the **current present?** gate fired
> for the first time (a single-mode Vertex substrate structurally cannot reach it). With a
> current present, the self-probe frame IS defined, and a blind answerer read the system in
> TWO independent frames — the fluctuation-response locus (a loop off the equilibrium line)
> and the winding/antisymmetry frame — which AGREED that a sustained directional current
> flows. Agreement = pass (§J); the sector is now demonstrated, not just cage. Note: the
> answerer grounded agreement via locus-area-vs-winding-drift, NOT via the formal affinity/
> TUR-factor scalars — those are now in-slice groundable (the data carries phiMean/phiVar)
> but went unused, so the formal TUR-floor (T>=1) check is reachable-but-unexercised. The
> in-slice winding ensemble that makes this whole sector groundable from ONE operating point
> is a consequence of the symmetric-boundary rule (WORKFLOW §4).
> **Sweep finding (three_species_cycle_noise_sweep_v5):** the current-gate's last sub-question
> — *affinity drive/noise-independent?* — closed. A noise sweep (5 points, 20× in D, fixed
> structure) of the v3 dot showed the winding RATE / per-cycle directedness FLAT to <6% blind,
> while the two-point structure was D-invariant and Cxy=−Cyx survived every level: the current
> is wiring-set, not noise-driven (v3's one honest park, now grounded across the axis it could
> not see). The teeth here are the FIRST moment (drift); the SECOND moment (Var(J)/TUR factor)
> is estimator-noisy/non-monotone, and the blind answerer PARKED it — independently re-deriving
> `docs/deferred-for-auditor.md` Entry 2 (a measurement-quality caveat, not a conform defect:
> expose the spread's uncertainty at the viewport; the source fix lives in mpa-central).
- **grain present?** → *Identifiability:* which params identifiable vs mush (bootstrap);
  trust a param iff in_domain ∧ assessable ∧ identified; X a real FDT-violation or raw-slope?
- **current present?** → *k_frust / two-frame:* self-probe frame defined? where both compute,
  do they agree (disagreement = falsifier)? affinity drive/noise-independent?
- **in-family?** (fit residual / per-channel S/N) → deviation *readable* (within character)
  or out-of-domain?
- C normalizable, or the unnormalized-C pathology?
- **[dev]** gates may be forced (skip bootstrap, ignore out-of-family) **but logged**.
  **[prod]** gates live; n_boot paid; out-of-family honored.

### 5 · READOUT — functions of the fit, not free decisions  `[CONTACT v=laser_ro_nominal_v1 — verdict EARNED; headroom BUCKLED]` `[CONTACT v=three_species_cycle_noise_sweep_v5 — FLAT-band readout: a band whose answer IS its flatness (rate noise-independent), read blind; 2nd-moment channel honestly parked]`
> **First-contact finding (laser_ro_nominal_v1):** the *verdict* (nominal vs marginal)
> and *one-sided* headroom (toward the nearest data-visible asymptote, here ζ→1
> critical/sluggish) are functions of a single fit. The *two-sided* headroom — the part
> that actually corrects the researcher's naive worry — is NOT: it needs the framework
> Q(χ̂) band, which one operating point does not carry. So SELECTION's single-point
> collapse and READOUT's two-sided headroom are in structural tension. Resolve by either
> injecting the analytic Banach band (overlay) as the reference, or posing a sweep vertical.
> **Confirmed under blinding (re-run 2026-05-24):** an isolated answerer with no access to
> the seal independently refused the two-sided claim — the gap is structural, not an
> author artifact. The answerer's `not_grounded[]` is the channel that surfaced it
> (WORKFLOW §6 answerer contract).
> **Graded 2026-05-25 (MISS-with-finding, meta-validity P):** the escalated sweep
> (`laser_ro_pump_sweep_v2`) ran blind. The *mechanical* aim worked — two-sided headroom
> became groundable (the answerer named both walls of the band), a real READOUT capability.
> But the bottom-line verdict inverted: "healthiest" is not Jacobian-computed; it flips on a
> health-metric (response-crispness vs damping-margin) the blind packet never supplied. The
> placements + band shape + the v1 anchor all reproduced — conform did NOT break, and the
> MISS matched no cage_edge. **Reclassified (2026-05-25): the verdict-layer inversion is a
> viewer-layer concern, not a conform teeth-defect to fix by re-posing.** "Healthiest" is a
> researcher *utility lens* over the computed band — a **dial**, not a verdict: conform
> computes and exposes the whole band, the (inert) viewport presents it and exposes the lens
> as a researcher control; the reading lags the researcher's choice, it is not led or
> inferred. A verdict the freeze cannot compute is the tell that the choice is a dial.
> Deferred to `docs/deferred-for-auditor.md` Entry 1 (picked up at the auditor pivot). The *mechanical*
> two-sided-headroom groundability stands as a conform result; whether it promotes to
> `[EARNED]` once carved free of the verdict lens is a gated call parked alongside. See
> `earned/laser_ro_pump_sweep_v2/RESULT.md`.
- *Verdict:* interior of the open interval (nominal) vs departing toward an asymptote;
  headroom = distance to nearest asymptote in native units; which asymptote binds + direction;
  is the naive worry corrected?
- *View:* the intent-selected view; an **artifact (shot/overlay) read by inspection**, not a
  boolean; native / canonical / paired frame; every rendered property maps to data; parallax
  if multichannel.
- *Kill-check:* boundary *attained* at a finite point (NaN tripwire)? X > 1, or X exactly 0/1?
  k_frust where structure forbids it? structure mismatch? — MATCH / MISS / KILL.
  - *Regime-zero ≠ boundary-attained:* a quantity that is zero **by regime** (the model
    degenerating to a simpler regime at some operating points) is NOT a boundary of the
    open interval being attained — it is **not** a KILL. The tripwire fires only when the
    *invariant that should stay interior* reaches 0/1/∞ at a finite point. Read the
    invariant that **stays finite near the asymptote**, not a parameterization that
    diverges as the regime degenerates (a blowing-up parameterization manufactures false
    boundary-attainment).
- **[dev]** view produced as a plumbing check; verdict/kills **not** treated as evidence or
  framework-falsification. **[prod]** a kill means MPA is invalid on this substrate here.

### 6 · ROUTE & DEPOSIT — close the loop
- Result trips a cage_edge → route to the neighbor category, re-pose?
- Did it smear (feed the separability Wall-test)?
- Deposit one residue line (bound + headroom) — into the HANDOFF ledger (meta-SOP §3).
- **[dev/prod]** same — the silhouette accretes regardless of phase.

---

## PHASE INTERFACE — the thin seam that keeps dev/prod modular
The dev/prod cut is a real sparsification only if its interface is explicit: a
**relaxation ledger** — for every constraint off in dev, one line naming *what's off*
and *its revert condition*. Standing entries:
- pristine data-handling — **OFF in dev** (data may be cleaned, **reference-blind only**,
  never toward Banach); revert: prod feeds pristine data, no-touch re-installed.
- evidence-status — **OFF in dev** (dev claims nothing; plumbing only); revert: prod
  outputs are evidence, kills are framework-falsifications.
- blinding rigor — **relaxed in dev** (author==answerer tolerated); revert: prod runs a
  genuinely blind answerer.
- identifiability — **n_boot=0 in dev**; revert: prod pays the bootstrap.
- I2 / migration intent — **admitted in dev WHEN built as stitched isolated placements**
  (each point an independent I1 fit + one band readout, MISS localizable); revert: prod
  runs the full migration fit with trajectory/band machinery in the fit's scope.

Without this ledger, dev debt smears into prod and the phases hit the Wall along the
time axis. Kept across both phases (topology, never relaxed): the arrow, camera-first
ordering, the intent→traversal→view spine, the compute→artifact→view seam, cage adjacency.
