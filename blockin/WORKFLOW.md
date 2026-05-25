# WORKFLOW — the pass-SOP (how to run ONE block-in pass)

This is the **pass-SOP**: the standard operating procedure for running a single
vertical through the pipeline and producing a graded verdict. One of four modules —
keep the levels distinct (this slip recurs):

- **PIPELINE.md** — the OBJECT (conform's data-prep anatomy). A pass *traverses* it.
- **WORKFLOW.md** (this file) — the PASS-SOP. How to take one measurement.
- **meta-SOP.md** — the META-SOP. How a pass-result *evolves* the three artifacts and
  picks the next question. It **consumes** what a pass emits; it is not how a pass runs.
- **HANDOFF.md** — the BATON. Mutable state carried between passes.

**Thin seam (workflow → meta-SOP):** a pass emits **{verdict (MATCH/MISS/KILL),
residue, `not_grounded[]`, view}**. This file ends at the graded verdict; everything
after — refine, deposit, next-question, commit — is the meta-SOP.

---

## 1. Rules of the game  [stable — do NOT grow]

- **Researcher-voice questions.** One observable, "is it nominal?", in the
  researcher's own field terms. They bring **the smallest data unit that grounds the
  reading**: a single operating point for a *placement*, a small sweep for a *headroom /
  how-far / which-way* question (a single point cannot ground a two-sided headroom — see
  meta-SOP §2 escalation). Either way it is the researcher's own measurements, not a
  systematic characterization sweep. Framework structure (chit / regime / FDR migration)
  lives only in the sealed `answer_path` — never in the blind packet. Researcher-voice
  IS the blinding.
- **nominal = interior of the open interval; headroom to the nearest asymptote is
  the reading.** "You are here, with this much room," not a regime lecture.
- **kernel pre-gate first**: sweep tau_obs; k_frust must NOT migrate (kill if it does).
- **FDR locus = universal readout** (chi vs C(0)-C(tau)); always computable.
- **open-interval / NaN tripwire**: never test "= boundary"; test departure toward it.
- **route-don't-mix**: `cage_edges` are conditional routes kept as structure (the
  Catmull-Clark cage — collapse axes freely, but record where a slice points at a
  neighbor, or it smooths into disconnected islands).
- **data-path independence**: the sim makes the data, analytics makes the truth.
- **conform is the examinee, never the answer key.** Ground truth is always analytic.
- **blind packet** = { question, minimal_structure, data_path }. Nothing else.
- **brittle is the mandate.** Team of ~3, not NASA, not ten years. Bespoke per
  substrate; the common shape precipitates later, it is not built up front.

## 2. Roles for a pass (two contexts, never merged)

| | ORCHESTRATOR | BLIND ANSWERER |
|---|---|---|
| who | this session / the human-driven driver | a fresh subagent, spawned per pass |
| holds the seal? | YES (unseals) | NO — must be unable to see it |
| job | pose → spawn → unseal → compare → (hand to meta-SOP) | traverse the sanitized traversal on the blind inputs, return a verdict + view |

Blinding is **structural, not honor-system**: the answerer runs in its own context and
is handed only sanitized inputs. It *cannot* read the seal because it is never given a
path to it. Pass 1 defeated blinding by reading `entry.md` to "understand the apparatus"
— a fresh agent would do the same. The split below makes that impossible.

(The **author-subagent** is a *meta-SOP* role, not a pass role — it creates the seal
between passes. See `meta-SOP.md`.)

## 3. Read manifests (the deferred-read — obey per role)

**ORCHESTRATOR reads:** `HANDOFF.md`, `PIPELINE.md`, this file, `meta-SOP.md`, the
slug's `entry.md` (incl. the sealed half — the orchestrator legitimately holds it),
prior `earned/` only if needed. **Do NOT read `dev_profile.json`** — it is ~83 KB of
mostly recursive `output/shots/*.exr` filenames; it is a context-bomb and informs
nothing here.

**BLIND ANSWERER reads ONLY:**
- `workspace/<slug>.packet.md`     (the blind packet)
- `workspace/<slug>.data.csv`      (the SANITIZED data — never the raw `.frozen.csv`)
- `workspace/<slug>.traversal.md`  (the SANITIZED traversal — never raw `PIPELINE.md`,
  which accretes earned contours that name the substrate and the answer)
- §1 (rules of the game), §5 (the A–P interrogation box), §6 (answerer contract) of this file
- `view_header.py`                 (the view standard helper)

**BLIND ANSWERER must NEVER read:** `entry.md`, anything under `questions/` or
`earned/`, any `freeze_*.py` (substrate truth), the raw `*.frozen.csv`, the raw
`PIPELINE.md` (read the sanitized `workspace/<slug>.traversal.md` instead), or
`dev_profile.json`. Reading any of these invalidates the pass as a blinding test.

## 4. Blinding boundary covers the DATA, not just the seal

The blind packet is `{question, minimal_structure, data_path}` — but `data_path` must
point at a file that does not name the substrate. `pose.py` sanitizes: it strips every
`#` provenance line from `.frozen.csv`, keeps only the column header + numeric rows,
trips if any prose or framework token survives, and rewrites the packet's `data_path`
to the sanitized copy. (Pass-1 leak: the raw header read `substrate: class-B laser …
r=2.0` — most of the sealed answer, sitting in the "blind" data.)

**The boundary is symmetric — the slice is the only dial.** Blinding has TWO failure
modes, not one. The sanitizer guards *over*-inclusion: framework tokens or the answer
riding in the data → a false MATCH (the slug/column specifics below). The mirror failure
is *under*-inclusion: withholding observables the researcher's stated measurement honestly
contains. A vertical has exactly ONE degree of freedom — the **slice**: which axes are
collapsed (operating points, structure dimensions, channels held aside), declared and
reversible (§P). Within the slice, the blind data is the **complete honest observable
content** of that measurement; the author does NOT curate which in-slice observables to
hand over. Withholding one to tune difficulty is a boundary violation as real as a leak —
it manufactures a MISS that does not *isolate conform* (the miss could mean "the author
under-provisioned," not "conform broke") and lets the author, not the shape, set the
`not_grounded` line.

So **`not_grounded[]` must fall out of the SLICE, never out of observable curation.**
Detector (the leak tripwire run in reverse): for each parked claim, is it un-groundable
because it lives across a *collapsed axis* (another operating point, a sweep → a
legitimate park, the next vector's fuel) — or because an in-slice observable the
researcher's own measurement contains was withheld (→ a mis-bounded vertical: fix the
data, not the question)? You choose *where* to probe the silhouette (the slice); you do
not choose *what the probe reports*. We map the shape; the substrate's specific
observables follow from the shape — they are not an authoring choice. *(Surfaced
2026-05-25: v3's first draft withheld the in-slice winding ensemble to keep first-contact
"minimal," which mislabeled the Cat-10 two-frame teeth as `not_grounded`. The fix was the
boundary, not the vertical — and the per-vertical deliberation it had cost was the tell
the boundary was under-defined.)*

**The boundary also covers the slug / filename.** The packet carries `data_path`, whose
path contains the slug — so a framework token *in the slug* leaks into the blind packet.
The token tripwire deliberately omits ambiguous short tokens (Q, X), so it will **not**
catch a slug like `…qband…` ("Q-band") — the human-glance must scan the slug. (v2 caught
and renamed `…qband…` → `…pump_sweep…` before posing.) Likewise the CSV: `pose.py`
strips `#` comments but **keeps every numeric column**, so a stray `r`/pump column would
leak (r = eᵡ̂ lets conform skip the fit) — the freeze must not emit it, and the
human-glance confirms the column list.

## 5. The interrogation — the A–P box (the heart of a pass)

Write out every question a traversal of the pipeline raises and you get roughly
**eighty** — the bounding box of MPA data prep. They are organized *by* the pipeline
stages (PIPELINE.md is the anatomy; this is the interrogation procedure that walks it).
A pass does not answer all eighty — SELECTION lights a thin slice and most stay dark —
but the answerer holds the whole box so it knows what it is *not* doing.

**A. Reading the ask (question + data → what's actually wanted)**
- What is the question in the researcher's own words?
- Is it a nominal-check, a placement, a comparison, a headroom/"how-far" question, or a "why is this happening"?
- What does the researcher already believe is normal (their baseline expectation)?
- What do they need to *see* to be satisfied — the deliverable view?
- Is the data one operating point, or does it already span a control axis (a sweep)?
- Is it one channel/observable or several?

**B. Intent (which RFC-S operation this teases to)**
- Which intent(s) does the question map to (I1 place / I2 camera-scale / I3 design-constraint / I4 round-trip / I5 reference)?
- Does it map to more than one, and in what order?
- Is that intent *supported* at the current dev stage, or deferred (e.g. I2 camera for brain)?
- Does the data shape agree with the intent (single point ↔ I1/I5; spanning data ↔ I2 migration)?

**C. Structure & category**
- What is the minimal structure that reproduces the phenomenon (the gate)?
- How many nodes/edges; vertex, edge, or cycle?
- Reciprocal or non-reciprocal coupling? Is there a sustained current (k_frust-bearing)?
- Which provisional category (1–10) — and does the data smear across categories (the separability hypothesis)?
- What is the substrate's own field (for native voice and units)?

**D. Contract: units, provenance, grain**
- What are the units of each column? Are C and χ dimensionless?
- How do the researcher's columns map to the canonical (τ, C, χ)?
- Is provenance/citation/license present (mandatory)?
- What's the reproducibility hash of the source?
- Does the data carry grain (C_sem, χ_sem)? How was uncertainty determined?
- What preprocessing was applied, and is it logged + reversible?
- Coverage range vs declared validity range per column?
- Is C even normalizable, or is it the unnormalized-C pathology?

**E. Camera / kernel pre-gate (τ_obs) — run first**
- What is τ_obs (the observation window)? Declared, or must it be derived?
- Does the substrate have a clean intrinsic time, or is τ_obs ambiguous (→0 floor / →∞)?
- Is the window matched to the process, or is the "failure" a camera artifact?
- Under a τ_obs sweep, do regime labels migrate (expected) while k_frust stays invariant (required)?
- If k_frust migrates with τ_obs → detection artifact → apply e_i = s_i ⊕ s_{i−1}?
- Is there *any* τ_obs window with a stable hierarchy? If none → the problem *is* the camera (Cat 5).
- What tau_scale rescales to dimensionless lag, and is it logged + reversible?

**F. Placement (inversion / I1)**
- Where does the operating point sit in canonical space (chit)?
- Which regime (c / s / r / k_frust)?
- How confident is the placement (regime confidence, residual)?
- Which observable constrained it (locus analytical / ensemble / hybrid)?
- Is γ_AB constrained (phase observable present) or carried unconstrained?
- Does this intent need the 5-vector, or is 1-param chit enough?

**G. The map (lens / translation field)**
- What is the region of interest in canonical space (the framing)?
- What TranslationField (substrate-native ↔ canonical) fits that region?
- Forward-only (the backward map is never built)?
- What's the round-trip residual (I4): does the field reproduce the data?
- Where do the asymptotes sit relative to this point — i.e. the coordinates that give "headroom" meaning?

**H. The reference (Banach / I5)**
- Which Banach instance is the reference for this placement — backbone (c→s→r) or companion (k_frust/current)?
- How is Banach conformed *to* the pristine data (never the reverse)?
- What is the data's deviation from Banach (the substrate's character)?
- Is that deviation within-family (nominal character) or out-of-domain?
- What view-transform/gamut shapes how Banach is shown (without touching the data)?

**I. Deviation fingerprint & gates**
- What's the 5-vector (q_EA, τ_α, β_KWW, τ_β, X)?
- Is the cell in-family (per-channel S/N gate)?
- Which parameters are identifiable vs mush (bootstrap)?
- Trust a parameter only if `in_domain ∧ assessable ∧ identified`?
- Is X a meaningful FDT-violation here, or read at raw-slope?

**J. The two FDR frames / k_frust sector** (only where a current exists)
- Is the self-probe (affinity) frame even defined (current present)?
- Where both frames compute, do they give the same regime verdict (agreement = pass, disagreement = falsifier)?
- Is the affinity drive/noise-independent (structure-set), as required?

**K. Verdict: nominal, headroom, asymptotes**
- Interior of the open interval (nominal), or departing toward an asymptote?
- What is the headroom — distance to the nearest asymptote, in native units?
- Which asymptote is the binding (first) one, and in which direction?
- Is the naive worry corrected (e.g. "more ringing ≠ nearer instability")?

**L. Falsifiers / kill conditions**
- Is any boundary *attained* at a finite point (NaN tripwire)?
- X > 1, or X exactly 0/1 at finite operating point?
- k_frust / circulating current where the structure forbids it?
- Structure mismatch (cycle signature in a single-mode trace)?
- What distinguishes MATCH vs MISS vs KILL for this question?

**M. The view (what the researcher sees)**
- Which view does the intent call for (placement / reference overlay / camera sweep)?
- Is the deliverable an artifact (shot/overlay) the researcher *reads*, not a boolean?
- Native frame, canonical frame, or paired (substrate ⊕ Banach)?
- Does every rendered property map to framework data (rendering discipline)?
- Can nominality be read off it by inspection?
- If multiple channels: is the parallax (cross-channel consistency) shown?

**N. Routing / adjacency / separability**
- Does the result trip a cage_edge (route to a neighbor category)?
- Did the substrate smear (and what does that teach about the separability hypothesis)?
- If routed, re-pose against the adjacent category?

**O. Answer provenance / reproducibility / residue**
- By what path was the answer derived (logged, cached)?
- Is the data-path provably independent of the answer-path?
- What is the sealed analytic truth, and how is it derived without conform?
- Is the verdict reproducible (per-seed / order-independent)?
- What one line of residue does this vertical deposit into the silhouette?

**P. Meta-validity of the vertical itself**
- Is the question blind (researcher voice, zero framework leak)?
- Does it *isolate* conform (a miss can only mean "conform broke," not four other things)?
- Does it have teeth (hard-to-vary answer) and reach (constrains the silhouette generally)?
- Is the substrate "our data" (clean ground truth) or on the contaminated hold-list?
- Which axes were collapsed for this slice (the low-poly cage), declared + reversible?
- **Boundary symmetry (§4):** is every `not_grounded[]` claim parked because it crosses a
  *collapsed axis* — not because an in-slice observable the researcher's own measurement
  contains was withheld? Under-provisioning manufactures a MISS that does not isolate
  conform. The slice is the only dial; in-slice observables are entailed, not curated.
- Which cage edges (adjacency) were recorded so it subdivides into coupling later?
- **Anchor-and-assert:** can the vertical include a *previously-earned* operating point
  as one sample and assert its placement reproduces? Cheap cross-pass drift detection —
  do it whenever the geometry allows. (The assertion is checked **at unseal by the
  orchestrator**, not handed to the blind answerer — telling the answerer which sample is
  the anchor, or its earned value, would leak that placement.)
- **Confirm vs discover:** does the researcher's own description already hand over the
  *shape* of the answer? A nominal-check legitimately carries their observation, but make
  sure the **sealed** value-add (the why, the band, the correction of the naive worry) is
  what's being earned — not merely re-described. Blinding hides framework structure, not
  the researcher's honest observation; the leak-check covers prose **and the slug**.

> Where the box touches the meta-SOP: N/O/P each have a pass-level half that stays here
> (does it trip a cage_edge → re-pose / what residue does it deposit / does *this*
> question have teeth) and a meta-level half that the meta-SOP owns (update the
> separability hypothesis / how the silhouette accretes from deposits / how to *generate*
> the next question). This file answers a posed question; the meta-SOP evolves the system.

## 6. Answerer contract (what the blind answerer returns)

A verdict is not a label — it is a set of **claims, each with provenance**. Required:
- **placement** (framework read): the conformed Banach member + deformation (e.g.
  `zeta, Q, gamma, omega`); fit residual.
- **verdict** in researcher terms: nominal vs departing-toward-an-asymptote; the
  headroom sentence ("you are here, with this much room").
- **grounded[]**: for each claim, *which observable / pipeline module* established it.
- **not_grounded[]**: every claim the inputs could **not** support — stated, never
  fabricated. *This list is where findings come from.* (Pass 1: two-sided headroom is
  not closeable from one operating point — that refusal was the whole result.)
- **view**: a PNG built via `view_header.py`, meeting the **result-image standard
  (meta-SOP §7)** — header band (question broken down + verdict + placement +
  grounded/not-grounded) over a grid of data-mapped plot boxes; for a sweep, one box must
  show the band. Named `view_<timestamp>.png` so results accumulate into the library.
  Plots below the band are bespoke. *Grabs aren't story* — the band is the story.

**Guard against the hollow MATCH:** an answerer that emits the researcher-plausible
answer with empty `grounded[]` is a null result wearing a green check. A claim with no
provenance is not a claim. The orchestrator rejects a verdict whose `grounded[]` is
empty for a non-trivial claim.

**Guard against the value-laden verdict (the researcher-dial carve-out):** a verdict in
researcher terms reports *placement + headroom* — where the substrate sits and how far to
the nearest asymptote. It does **not** commit to a researcher *preference*
(best / healthiest / most-acceptable). Those select among the computed band through an
interpretive choice the researcher brings — a **dial** exposed at the (inert) viewport, which
*presents* the band and lets the researcher's setting highlight their reading: lagging, not
led, and nothing inferred at view time. The **detector**: a verdict the freeze cannot compute
is the tell that the choice is a researcher dial, not conform's call. So if a question asks
"which is healthiest/best," ground the band (every candidate branch per point) and surface the
choice as `not_grounded[]` → a dial; do not pin one metric to manufacture a single winner.
(Surfaced by a prior sweep vertical; parked in `docs/deferred-for-auditor.md` — which also
catalogues other candidate dials: collapse-axis, sign/interpretation convention.)

**Traversing a sweep (multi-point):** place each point as an **independent single-point
fit first**, then read the band/migration off the placements. Never a monolithic
migration fit — a sweep's MISS must still localize to *one* module (a placement vs. the
band readout), or it forfeits meta-validity P (*isolate conform*). The build is "N
isolated placements + one new band readout"; the band readout is the only new thing that
can break. If the sweep includes a previously-earned operating point, **assert its
placement reproduces** the earned value (anchor-and-assert — see §5/P).

## 7. The pass loop (pose → answer → unseal → graded verdict)

```
pose (dumb): pick entry, run its freeze, SANITIZE data + traversal, emit blind packet +
   blind data + blind traversal
-> answerer-session = a BLIND SUBAGENT (own context, sanitized inputs only — never the
   seal): (1) kernel pre-gate, (2) FDR locus + bespoke instrumentation, (3) first
   asymptote + headroom; returns verdict + provenance-per-claim + self-describing view
-> unseal (orchestrator holds the seal): compare to entry.sealed_answer
   -> MATCH / MISS / KILL   (a MATCH with empty provenance = hollow MATCH, not a win)
== seam == hand {verdict, residue, not_grounded[], view} to the meta-SOP ==
```

Unseal/compare detail:
- A **MATCH** must name *which pipeline module did the work*; a match the answerer could
  only have guessed (placement in `grounded[]` empty) is a **hollow MATCH**, not a win.
- A **MISS** that matches a `cage_edge` signature → route to the neighbor (meta-SOP ROUTE).
- A **KILL** (boundary attained / structure mismatch) halts and is diagnosed — in prod
  it is a framework falsification; in dev it is a bug in the freeze or the reading.

`pose.py` is built: runs the slug's freeze, sanitizes the data **and the traversal**,
emits ONLY the pre-SEALED half to `workspace/<slug>.packet.md` plus the sanitized
`workspace/<slug>.traversal.md`, and code-side leak tripwires refuse to emit if a
framework token crosses into the blind packet/data or a substrate/answer token survives
in the traversal. Per-substrate freeze stays bespoke (the common shape precipitates at
substrate N, not before — that is design, not a gap).
