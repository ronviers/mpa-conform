# mpa-conform — session discipline

Read this before touching anything in this repo.

**Program-wide architectural authority:** [`H:/mpa-central/SUITE_BLOCK_IN.md`](../mpa-central/SUITE_BLOCK_IN.md)
is the structural commitment for the MPA suite. mpa-conform is the
**compute hub** in that block-in — it produces every artifact the viewer
layer (mpa-auditor, mpa-view, future viewers) reads. The viewer layer
does not compute. This file is downstream of SUITE_BLOCK_IN; if anything
here conflicts, SUITE_BLOCK_IN wins.

## Architecture commitment (the load-bearing distinction)

This repo is **agentic by design**, sibling to `mpa-auditor`. They are not
the same shape of artifact:

| | mpa-auditor | mpa-conform |
|---|---|---|
| Runtime | Pure-static browser app | CLI / agentic tool |
| LLM | Forbidden at runtime | First-class (researcher path) |
| MCP servers | None | Both broker and vendor |
| Network | Offline-after-download | Online during conform |
| Output | Audit verdicts | Signed `declaration_bundle.json` |

The two are stitched at a **file-import boundary**: mpa-conform writes
the bundle; mpa-auditor reads it. The boundary is the *whole* coupling.
No callbacks, no live links, no inference of one repo's runtime from the
other's.

**Architectural authority:** [mpa-auditor §Q12 correction note
(2026-05-15)](../mpa-auditor/docs/foundational-answers.md). Treat that
note as upstream-binding. Any architectural drift in mpa-conform that
contradicts §Q12 is a bug.

## What this repo writes to

- `mpa-conform/output/seed-corpus/` — staging (gitignored).
- `mpa-auditor/seed-corpus/` — via PR. This is the *only* place we write
  into another repo, by-design (§Q12 file-import boundary).

## What this repo reads from

- `mpa-central/library/data/` — grind cells (curator path input).
- `mpa-auditor/corpus/substrate-classes.json` — class registry.
- `mpa-auditor/contracts/05-data-upload.schema.json` — auditor target shape.
- `mpa-atlas/schema/driver-profile.v0.2.json` — driver profile shape.
- `mpa-atlas/framework/mpav1_compressed.md` (STRUCTURAL + CHARACTER
  readings, one spine), `mpav1_receipts.md` — substrate-conditional
  reading rules; class definitions. Read `mpa-atlas/CLAUDE.md`
  (thin-RFC discipline) *first*.
- `mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md` — driver profile semantics.

## Thin-and-bespoke for LLM-calling code

When the researcher path lands: **hardcode, one function, match model
to problem, cache as log.** Resist 2022-era guardrails (retry storms,
elaborate prompt-template abstractions, "agent frameworks"). Validate
every LLM output with Pydantic at the boundary; retry with the
validation error as feedback. See [unified research
report](../mpa-auditor/docs/mpa_conform_unified_report.md) §5 for the
concrete shape.

## Discipline borrowings from siblings

- **Thin-RFC discipline** (`mpa-atlas/CLAUDE.md`): governs how we touch
  cdv1 / RFC-S. We read them, we do not thicken them.
- **METHODOLOGY four cuts** (`mpa-central/METHODOLOGY.md`): governs what
  counts as MPA testing. The curator path is methodology-shaped
  characterization; the researcher path is methodology-shaped
  ingestion.
- **No declared virtues in user-facing copy** (memory): scrub
  "honest/transparent/sincere/ethical" from CLI strings, READMEs, and
  bundle metadata. Show behavior; don't announce it.
- **Document size by function, not percentage**: this file is short
  because nothing here is load-bearing past the architectural
  commitment.

## Rendering discipline — the water MPA swims in

Every visual property in every shot maps to framework data;
differentiation, not decoration. Canonical doc:
[`conformer/shot/RENDERING_DISCIPLINE.md`](conformer/shot/RENDERING_DISCIPLINE.md).
Established 2026-05-17. This is not a feature — it is the medium every
visualization across the suite operates in. The discipline does not
get re-litigated per session.

Renderer: Taichi-based particle system at
[`conformer/shot/particle_renderer.py`](conformer/shot/particle_renderer.py).
Channel → emitter parameter contract (v1) lives in
`channel_to_emitter_params()` and is documented in the discipline doc.
The Python implementation is the executable spec for the eventual
auditor viewport's WebGL port.

## Verification — character test suite

This repo **owns** the cross-repo character test framework at
[`conformer/tests/character/`](conformer/tests/character/). Canonical
doc: [`conformer/tests/character/README.md`](conformer/tests/character/README.md).

A character test produces a **shot** (EXR sequence + mp4 preview) — not
an assertion boolean. The verification is watching the shot in DJV
(`C:\Program Files\DJV 3.4.2\bin\djv.exe`). Mechanical
assertions ride along as sanity, not certification. *Grabs aren't
story.*

Run from this repo:

```
python -m conformer.tests.character.runner
python -m conformer.cli test-character --filter ck-glassy
```

Output: `output/tests/character/<timestamp>/index.html` (dailies
report) + per-test shot directories.

**Destination**: the mpa-auditor viewport. When auditor gains tumble /
playback (it doesn't yet), the same EXR sequences these tests produce
will play through its viewport. DJV stands in for now.

**Adding a test case**: drop a module under
`conformer/tests/character/cases/` and add it to `cases/__init__.py`.
One move per session — per `feedback_single_move_design`.

## Session handoff

This repo is mid **block-in**, structured as **four modules at three levels** — do not
re-merge them. Read [`README.md`](README.md) first, then start at the baton,
[`blockin/HANDOFF.md`](blockin/HANDOFF.md) (mutable state + next move):
- [`blockin/PIPELINE.md`](blockin/PIPELINE.md) — the **object** (conform's data-prep silhouette).
- [`blockin/WORKFLOW.md`](blockin/WORKFLOW.md) — the **pass-SOP** (how one pass runs; the A–P box).
- [`blockin/meta-SOP.md`](blockin/meta-SOP.md) — the **evolution governance** (how a verdict evolves the artifacts + picks the next question; §0 on-entry reconcile when resuming).
- [`blockin/HANDOFF.md`](blockin/HANDOFF.md) — the **baton** (mutable state).

(There is no `PROTOCOL.md` — it was dissolved into WORKFLOW + meta-SOP.) The pre-block-in roadmap
is archived at `docs/archive/ROADMAP.md` and the old `docs/next-session-handoff.md` is
retired — they describe a superseded plan; don't follow them. Foundational
questions/answers remain at
[`docs/foundational-questions.md`](docs/foundational-questions.md) and
[`docs/foundational-answers.md`](docs/foundational-answers.md).

A session edits its own files only. Schema bumps are deliberate
(v0.1 → v0.2 → ...); do not edit `declaration-bundle.v0.1.json` after
ship — bump and parallel-version instead.
