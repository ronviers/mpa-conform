# Deferred for the auditor pivot — researcher dials (interpretive DOF → viewport controls)

A **grown** parking doc. It catalogues the **interpretive degrees of freedom** the conform
block-in keeps running into — choices that today the author or orchestrator makes (or brings to
the human), but that **can be honestly pushed to the researcher** as viewport controls (dials
and buttons). When the suite pivots to building out the auditor viewport, this is the pickup
list.

It is **not** the conform→auditor data seam (that is the signed `declaration_bundle.json`
file-import boundary, per [mpa-auditor §Q12](../../mpa-auditor/docs/foundational-answers.md)).
It is the list of *controls the viewport must expose* and the structure the bundle must carry to
support them. One entry per choice; dated; append-only; each names the pass that surfaced it,
what conform must emit to support the dial, what the viewport exposes, and a **provisional
integration proposal** — written while the surfacing session's context is fresh (that context is
the perishable part; the proposal is non-binding).

## The principle — present, expose, lag (do not lead, do not correct)

The viewport does **not** fix, correct, infer, or decide anything — it is **inert by design**
(offline, no LLM, no live inference; that inertness is exactly what lets a skeptic open it and
trust it). Its job is to **present the computed structure** and **expose the legitimate
interpretive choices as controls.** The researcher operates the dials; the reading is *theirs*,
and it **lags** their settings — it is never *led* by a conclusion baked upstream.

So the test, every time the block-in finds itself deciding an interpretive question — which axis
to collapse, what sign to read a quantity with, which metric defines "healthy": **can this be
reasonably and honestly handed to the researcher as a dial?** If yes, that is where it belongs —
catalogue it here; do not pre-commit it in conform or in the author's seal. ("Honestly" is the
gate: a dial is legitimate only when the framework genuinely holds the choice open and exposing
it does not let the researcher fool themselves. A choice the analytic truth *forecloses* is
conform's to make, not a dial.)

**The detector.** A verdict the **freeze cannot compute** is the tell. If the sealed answer has
to be prose-asserted because no analytic quantity determines it, that is not a teeth-defect to
sharpen away — it is the signal that the choice is a **researcher dial**, not conform's call.
(The constructive flip-side of the answer-key safeguard, meta-SOP §2.)

**What conform still owns.** The honest computed structure: the placements, the band, the
analytic ground truth, data-path independence — and *all* the branches a dial selects among.
conform computes and exposes every branch; the dial only chooses which one the researcher looks
through. Leading would be conform (or the author) picking the branch for them.

## UI shape (precipitating — categories and heatmap are NOT known yet)

We are **not** designing the auditor UI here. We are accreting the *inputs* a future UI design
will precipitate from — the same block-in instinct (the silhouette is not designed top-down; it
firms as entries pile up). Two things we explicitly do not have: the **category taxonomy** (does
a dial live under Settings → Advanced, or as a button/dropdown around a viewer, or…?) and the
**usage heatmap** (which dials a researcher actually reaches for often). So:

- **Proposals carry priors, not data.** A proposal's "frequency / prominence" is a hunch from
  the surfacing session, flagged to be validated against real usage. The heatmap is
  future-empirical.
- **Every dial is a presentation toggle.** The viewport is inert — conform precomputes *all* the
  branches a dial selects among, so no dial triggers compute at view time. Placement is therefore
  pure **cognitive ergonomics** (how often, how global, who for), never compute cost.
- **The dimensions that will sort the taxonomy** (record these per proposal; they aggregate into
  the categories):
  - **Scope** — global (a Settings-level mode that reframes the whole view) · per-view (a control
    on one viewer) · per-channel.
  - **Audience** — researcher-domain (their own field language → a *primary* control) ·
    framework-literate (needs MPA fluency to set honestly → Settings → Advanced).
  - **Frequency prior** — every-session vs rarely (hunch + confidence).
  - **Coupling** — conditional on another dial/gate (e.g. a current-sector dial only exists when
    a current is present) → affects grouping.

The dimensions above are *how* placement will be decided; the taxonomy itself **precipitates as
worked entries accrete** — we deliberately do **not** place a candidate ahead of an organic
surfacing. (Scale Intents was the example that taught this: tempting to slot as a "global mode,"
but no vertical has yet exercised it as a dial — and there is a prior question, *is Intent even a
dial or is it lag-derived from the question?*, that a real surfacing should answer, not a guess.
So it stays on the watch-list, unplaced.)

This section starts deliberately sparse and accretes only from entries — never from speculation.

## Two tiers — watch-list vs entry

- An **entry** (below) is *born from a vertical* that hit the choice with real context: full
  account + a proposal. Only organic surfacing earns an entry — no pre-creation, no hurry.
- The **watch-list** is just things we have *noticed might* be dials: a name + a one-line
  suspicion. **No proposal, no placement, no status.** It exists so a suspicion isn't lost — not
  to get ahead of the work. A watch-list item graduates to an entry when a vertical surfaces it.

### Watch-list (suspected dials — NOT yet surfaced by a vertical)
- **Scale Intents (I1–I5)** — and a prior question: is Intent a dial at all, or lag-derived from
  the researcher's question? Await an organic surfacing.
- **Collapse-axis** — author sets `collapsed_axes` in the seal today; *may* be a viewing choice
  where the analytic truth doesn't force it.
- **Sign / interpretation convention** — `xdot_choice`; **X** as FDT-violation vs raw-slope.

---

## Entries

### Entry 1 — the utility lens over a band (the "healthiest" case)

- **Surfaced by:** `laser_ro_pump_sweep_v2` (graded 2026-05-25, MISS-with-finding,
  meta-validity P). See `blockin/earned/laser_ro_pump_sweep_v2/RESULT.md`.

**What happened.** A sweep question asked "across these curves, where is my response
*healthiest*?" conform placed every curve correctly and the band shape reproduced across the
blind run and the seal (anchor to the prior single-point vertical held; data-path independence
held; no KILL). But "healthiest" is **not a computed quantity** — it is a **utility lens** the
researcher lays over the band: response-crispness names one curve, stability-margin names
another, and both are honest. The seal and the blind answerer chose different lenses and so named
different curves. The freeze could not compute "healthiest" (the detector above).

**Why it is a dial, not a fix.** conform did its job — it computed the band. The lens is the
researcher's. Pinning one metric into a blind conform question (the SHARPEN reflex) would
*lead*: it bakes in a purpose conform cannot know.

**What conform must emit (bundle/seam requirement).** The band over candidate metrics per
operating point — every branch the lens could select — not a single "verdict" scalar.

**What the viewport exposes.** The full band, with the lens as a **control**: the researcher
selects the metric matching their purpose and the highlighted curve is then *theirs*, lagging
their choice. No verdict is inferred at view time; the control filters/highlights precomputed
structure.

**Integration proposal (provisional, non-binding — captured 2026-05-25, surfacing context
fresh).**
- *Control:* a "rank / highlight by:" dropdown on the band view; options are the metrics conform
  emits (crispness · stability-margin · settle-time · …). **Default = none** (present the band
  unranked) — a pre-selected default would re-introduce the very leading this dial exists to
  remove.
- *Scope:* per-view (band / sweep view). *Audience:* researcher-domain — phrased as purpose
  ("what do you care about?"), not as ζ/Q. *Frequency prior:* high on any band view; **low
  confidence** (no usage data).
- *Coupling:* only meaningful on a multi-point/band view; absent on a single placement.
- *Why this shape (this session's context):* the dial exists *because* the verdict flipped on a
  metric the data could not pick — so the control's whole job is to let the researcher supply the
  purpose, with the unranked band as the honest default.

**Preserved, NOT deferred.** The *mechanical* two-sided-headroom groundability — that conform
reads **both walls** of a non-monotonic band from a stitched-placement sweep — is a real READOUT
result the pass demonstrated. Only the value-ranking on top is a dial.
