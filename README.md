# mpa-conform

**The compute hub of the MPA suite.** It takes a substrate's data and a
researcher's question and produces the characterization that the pure-static
[mpa-auditor](https://github.com/ronviers/mpa-auditor) renders as a verdict.
All computation, all mess, and all judgment live here; the auditor is
deliberately **inert** — offline, no LLM, no live inference — so a skeptic can
open it and trust that nothing was fudged at view time. The two are joined only
at a file boundary: conform writes a signed bundle, the auditor reads it.
(Authority: [mpa-auditor §Q12](https://github.com/ronviers/mpa-auditor/blob/main/docs/foundational-answers.md).)

That is the standing description. The rest of this document is what is *actually
going on* — because a new contributor, human or model, needs the force of it
before touching anything.

---

## What is going on (read this first)

A researcher arrives with **one measurement and one question**: *"is this
nominal?"* Answering that honestly, through MPA, means routing their
`(question, data)` through a pipeline that must decide, in order: which
operation they are really asking for; the smallest structure that could produce
what they see; whether their observation window even points at the process or at
an artifact; where the substrate places in canonical space; how far the
analytical reference must bend to match it; which of that bend is real character
and which is noise; whether the result sits safely in the interior or is
drifting toward a failure mode; and what to *show* them. Write out every
question that traversal raises and you get roughly **eighty**, each one touching
the pipeline. That is the **bounding box** of MPA data prep.

You cannot build that box head-on. Eighty coupled constraints honored at full
precision from the first line do not converge — they are the **Complexity Wall**
in MPA's own vocabulary: ε ≥ 1, a tower that never contracts. Every attempt to
hold the whole thing at once collapses into fiddling with the nearest mechanism
while the structure stays invisible.

MPA's central claim is exactly a claim about this situation: a bounded agent
survives density only when the substrate carries enough **modular structure**
for the compression operator to contract (ε < 1). The Wall *is* failed
sparsification. So the framework tells us how to handle its own data-prep
density — **find the modular cuts, or die.** The project is therefore
self-referential by necessity: MPA is a theory of surviving complexity by
sparsification, and building MPA's data prep *is* a bounded-agent-against-density
problem, so we apply MPA to ourselves. We are **blocking conform in** —
establishing its silhouette at the coarsest resolution that reads, and refusing
the detail until the silhouette holds. (Why a silhouette, why blocking-in: the
work is paced by a three-person-plus-model team, no decade to spend, and a model
that re-orients every session. Sparsify or the work never converges.)

## The cuts (why the box becomes tractable)

The eighty questions collapse onto a handful of sparsification modules:

- **Frame** — the camera (τ_obs). A gate: resolve it first, or every downstream
  answer diagnoses the camera instead of the substrate.
- **Selection** — intent × minimal-structure. The researcher's question teases
  out to an RFC-S **intent** (place / scale / reference / …); the structure says
  what object. Together they light a thin slice and leave most of the box dark.
- **Root operation** — inversion **conforms the Banach reference *to* the
  pristine substrate.** This is the measurement and the hub everything reads
  from. The arrow is load-bearing: the substrate is never touched; only Banach is
  bent; the bend *is* the character. Reverse it — project the substrate onto a
  fixed template — and you manufacture artifacts and corrupt the one pristine
  thing you hold.
- **Gates** — single booleans that connect or sever whole sub-modules: grain
  present? (identifiability), current present? (the k_frust / two-frame sector),
  in-family? (is the deviation even readable).
- **Invariants** — one rule each, everywhere, no branching: the arrow; operate
  only on Banach; the FDR locus as universal readout; data-path independence;
  researcher-voice blinding; **conform is the examinee, never the answer key.**
- **Readouts** — verdict, view, and kill-checks are *functions* of the fit, not
  free decisions. "Nominal" is the interior of the open interval; "headroom" is
  the distance to the nearest asymptote. The deliverable is an artifact the
  researcher *reads*, not a boolean conform emits.
- **The phase cut (dev / prod)** — the strongest cut, along the time axis. The
  **dev path relaxes precision and discipline** (it may even clean the data —
  reference-blind only) to get a traversal working at all; the **prod path
  re-installs them.** What dev keeps is **topology** — the arrow, camera-first
  ordering, the seam. The phase interface is an explicit **relaxation ledger**;
  without it the phases smear and you hit the Wall along time.

## The four modules (do not merge them — the slip recurs)

The block-in is **four modules at three levels**, each its own file. Keeping them
separate is itself an act of the sparsification the project preaches:

- **[`blockin/PIPELINE.md`](blockin/PIPELINE.md)** — the **object** under study: the
  traversal above, conform's data-prep anatomy. Accretes earned contours, contracts as
  it firms. Status: **FIRST CONTACT** — one vertical (blinding-validated) has touched
  the spine; the rest is still cage, not surface.
- **[`blockin/WORKFLOW.md`](blockin/WORKFLOW.md)** — the **pass-SOP**: how to run *one*
  pass (rules of the game, roles, blinding, the ~80-question **A–P interrogation box**,
  the answerer contract). A pass *traverses* the pipeline and emits a graded verdict.
- **[`blockin/meta-SOP.md`](blockin/meta-SOP.md)** — the **evolution governance**: how a
  verdict+residue *refines* the pipeline and workflow and *maintains* the handoff, and
  how the **next question is chosen** (verdict→action). It is a different *level* — it
  acts on the other three. The recursion terminates at the human (refining the meta-SOP
  itself stays human-held).
- **[`blockin/HANDOFF.md`](blockin/HANDOFF.md)** — the **baton**: mutable per-pass state
  (resistance line, ledger, open hypothesis, current state / next move).

Two thin seams keep them from bleeding: **workflow → meta-SOP** = `{verdict, residue,
not_grounded[]}` (a pass produces it, the meta-SOP consumes it); **meta-SOP → handoff** =
state in, next-move + ledger line out. Note both *workflow* and *meta-SOP* are SOPs — one
for running a pass, one for evolving the system; do not re-conflate them.

The pass-SOP **wraps** the pipeline: the loop's single "answerer-session" step **is** one
pipeline traversal. The silhouette is not designed top-down; it **precipitates** as the
invariant across many brittle verticals. You cannot tumble a silhouette you do not have,
so we cut the cheapest real traversal first and let the shape emerge.

A vertical is a **known-answer round-trip**: a question posed in the researcher's
own voice (which blinds the framework by construction), over data generated by a
substrate's *own* honest simulator (so the data-path is independent of conform,
the examinee), checked against an analytic ground truth sealed from the answerer.
Match / miss / kill — and a **kill is a framework falsifier, not a bug.**

## Disciplines (non-negotiable)

> **The substrate is never touched.** mpa-conform conforms the **Banach
> analytical reference *to* the substrate's pristine data** — the bundle stores
> the native (τ, C, χ) unchanged; everything we fit, scale, place, or clamp is
> **Banach**, regenerable from a closed form. `tau_scale` is logged reversible
> metadata, not a data edit. Whenever the operand seems to be the substrate,
> stop — it's Banach.

- **Data-path independence.** The sim makes the data; analytics makes the truth;
  conform is *checked against* the truth, never its source.
- **Brittle and bespoke.** Hardcode, one function, match the tool to the problem.
  No frameworks, no premature abstraction. *It was never brittle if it never
  broke.*
- **Dev relaxes precision; prod re-installs it.** Every relaxation is a logged
  debt with a revert condition.
- **Falsification over coverage.** Pre-register what would break a claim; a clean
  failure beats a weak pass.

## Where to read next

- **[`blockin/HANDOFF.md`](blockin/HANDOFF.md)** — the baton: current state + next move.
  Start here to resume; it points at the rest.
- **[`blockin/PIPELINE.md`](blockin/PIPELINE.md)** — the silhouette (the object).
- **[`blockin/WORKFLOW.md`](blockin/WORKFLOW.md)** — the pass-SOP (the A–P box).
- **[`blockin/meta-SOP.md`](blockin/meta-SOP.md)** — the evolution governance (start at
  §0 on-entry reconcile when resuming).
- **[`blockin/earned/laser_ro_nominal_v1/`](blockin/earned/laser_ro_nominal_v1/)** — the
  first landed vertical (class-B laser ring-down, blinding-validated): `RESULT.md` +
  `view.png` + reproducible `answer.py`.
- Architecture: [`../mpa-central/SUITE_BLOCK_IN.md`](../mpa-central/SUITE_BLOCK_IN.md);
  framework source of truth: `../mpa-atlas/framework/mpav1_compressed.md`.

**Current status:** the loop runs end-to-end and is **automated** (orchestrator + blind
answerer subagent + author subagent), with authoring human-gated. Multiple verticals have
landed blind across several categories and the silhouette is precipitating
contour-by-contour. **For the live count, the last verdict, and the next move, read
[`blockin/HANDOFF.md`](blockin/HANDOFF.md)** — per-vertical block-in status lives there and
in auto-memory, never enumerated here (it would rot in a README).

---

## The metal — the existing compute (the production-path target)

Underneath the block-in is the working compute it will reconnect to. This is the
machinery a finished prod traversal calls; the block-in is deciding *how* a
researcher's question should drive it.

**Two paths through one repo.** *Curator path* (`conformer/curator/`) —
mechanical extraction from committed grind cells → seed-corpus; no LLM; read-only
over `H:/mpa-central/library/data/`. *Researcher path* (`conformer/researcher/`)
— raw upload → signed bundle; agentic, LLM-using, MCP-vendoring; scaffolded only.
Both emit one bundle shape so the auditor sees one contract.

**The compute** (`conformer/compute/`): two-stage `inversion.invert` fits the
mpav1 `chit` anchor and, additively, the KWW+FDT **5-vector** (q_EA, τ_α, β_KWW,
τ_β, **X** — the FDT-violation fingerprint) with a per-channel S/N **domain
gate** ("could Banach adapt to this data?") and a parametric-bootstrap
**identifiability** flag. The 5-vector is emitted by `invert()`; persisting it
into the bundle is the owed v0.5 step. The comparison view
(`conformer/compare/banach_overlay.py`) is the I5 reference overlay.

**The bundle** (`schema/declaration-bundle.v0.4.json`): one
`declaration_bundle.json` per (cell × xdot_choice) — `schema`, `bundle_id`,
`tier`, `signature`, `substrate_class`, `xdot_choice`, `tau_obs`, `provenance`
(license never null), `columns`, `observable` (canonical `(tau, C, chi[, sem])`),
`declaration_trail`. See the schema file for the full shape.

### What lives where

| Subdir | What |
|---|---|
| [`blockin/`](blockin/) | **The block-in.** Four modules — `PIPELINE.md` (object), `WORKFLOW.md` (pass-SOP), `meta-SOP.md` (evolution governance), `HANDOFF.md` (baton) — plus `pose.py`, `view_header.py`, `questions/<slug>/`, `earned/<slug>/`. Start at `HANDOFF.md`. |
| [`conformer/compute/`](conformer/compute/) | Inversion, gfdr model, 5-vector, gates. The metal the pipeline traverses. |
| [`conformer/curator/`](conformer/curator/) | Library → seed-corpus. Pure Python, no LLM. |
| [`conformer/compare/`](conformer/compare/) | Banach overlay (the reference view). |
| [`conformer/researcher/`](conformer/researcher/) | Researcher-path placeholder. |
| [`conformer/shot/`](conformer/shot/) | Rendering pipeline (shots, not booleans). |
| [`schema/`](schema/) | The auditor-facing bundle contract. |
| [`output/`](output/) | Staging (gitignored). |
| [`docs/`](docs/) | Reference the pipeline reads: Banach reference, solver block-in, asymptotic-closure, foundational Q&A, research synthesis; plus [`deferred-for-auditor.md`](docs/deferred-for-auditor.md) (grown conform→viewer design-deferral ledger, picked up at the auditor pivot). The plan lives in `blockin/`, not here. |

### What this repo does *not* do

- **Run substrate simulations.** Substrate-package territory, consumed via
  `mpa-central/library`. We read grind output; we never regenerate it. (The
  block-in's freezers are the exception — bespoke dev-path simulators that
  generate known-answer data for verticals, never production substrate data.)
- **Audit data.** That's `mpa-auditor`. We produce the input.
- **Build the backward map.** Per mpa-auditor §Q13, only the *forward* half
  (canonical → substrate-native) is built; the backward map is replaced by
  forward-sweep search.
- **Edit `mpa-atlas`.** We read mpav1 + RFC-S + receipts. Spec questions route
  through mpa-auditor → mpa-atlas.
- **Treat dev results as evidence.** Nothing on the dev path is a claim; the prod
  path re-installs evidence-grade discipline.

## Session log

Pre-block-in history. The block-in arc and its silhouette live in
[`blockin/HANDOFF.md`](blockin/HANDOFF.md) + auto-memory, not here.

| # | Date | Session | Result |
|---|------|---------|--------|
| 0 | 2026-05-15 | Bootstrap | Repo scaffolding; `declaration-bundle.v0.1`; curator post-processor over 60 library cells; 3 driver profiles + 60 bundles staged; acceptance tests pass. |
| 1 | 2026-05-15 | Inversion relocated | Ported the auditor's inversion + gfdr + ensemble-locus + phase-locking + two-mode kernel to pure-numpy `conformer/compute/`. Two-stage fit, 60/60 invert. |
| 2 | 2026-05-17 | Comparison view | `banach_overlay.py` — empirical / predicted / Banach panels. The PNG-driven single-move iteration discipline. |
| — | 2026-05-22 | 5-vector + gates | KWW+FDT 5-vector into `invert()` (tau_scale guard), per-channel S/N domain gate, parametric-bootstrap identifiability, scope-of-validity census, camera proven scale-invariant. |
| — | 2026-05-24 | Block-in | The bounding box, the sparsification cuts, dev/prod phase cut, first vertical (`laser_ro_nominal_v1`) staged. See `blockin/`. |
| — | 2026-05-24 | Loop automated + 4-module split | Vertical 1 **blinding-validated** (isolated blind answerer reproduces placement + finding). Built the harness: data sanitization in `pose.py`, self-describing `view_header.py`, verdict→action question-evolution policy. Then restructured the block-in into **four modules** (PIPELINE/WORKFLOW/meta-SOP/HANDOFF); dissolved the interim `PROTOCOL.md`. Block-in verticals from here on are tracked in `blockin/HANDOFF.md`, not this log. |

## License

MIT (consistent with mpa-central, mpa-atlas, mpa-auditor).
