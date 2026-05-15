# mpa-conform

**The data-prep porch for the MPA Auditor.** Turns library cells (curator
path) and researcher uploads (researcher path) into signed
[`declaration_bundle.json`](schema/declaration-bundle.v0.1.json) instances
the [mpa-auditor](https://github.com/ronviers/mpa-auditor) ingests.

`mpa-auditor` is a pure-static browser app. It accepts
`declaration_bundle.json` and only `declaration_bundle.json` — there is no
raw-CSV ingestion path. That commitment is what keeps the audit honest:
no runtime LLM calls, no DOI lookups during a fit, no silent inference
into the declaration trail. *Everything* messy lives upstream here, in
mpa-conform.

Architectural authority for this split: [mpa-auditor §Q12 correction note
(2026-05-15)](https://github.com/ronviers/mpa-auditor/blob/main/docs/foundational-answers.md).

## Status

**v0.1 bootstrap (2026-05-15).** Curator path live; researcher path scaffolded
only. 60 library cells from
[`mpa-central`](https://github.com/ronviers/mpa-central) conform cleanly to
3 driver profiles + 60 declaration bundles staged in `output/seed-corpus/`.

## Two paths through one repo

**Curator path** — committed library → seed-corpus. Mechanical extraction
from grind cells. No LLM. Read-only over `H:/mpa-central/library/data/`.
Output: per-cell declaration bundles + per-class driver profiles. Lives at
`conformer/curator/`.

**Researcher path** — raw upload → signed bundle. Agentic, LLM-using,
MCP-server-vendoring. Two deployment modes:
- **(A)** bring-your-own a-list-model via API key; or
- **(B)** bundled tiny model (Gemma-3-4B Q4_K_M + qwen25-3b-openclaw with
  N-of-2 consistency check, per
  [`docs/research-findings.md`](docs/research-findings.md))
  for fully offline operation.

The two paths emit the same bundle shape so the auditor's import logic
sees one contract, not two. Researcher path lives at
`conformer/researcher/` — placeholder for the first session, to be built
once the outside research returns and the bundled-LLM and MCP picks settle.

## Quickstart — curator path

```
python -m conformer.curator.walk_library
```

Walks `H:/mpa-central/library/data/{brain,glass,quantum}/*.json` and emits
to `output/seed-corpus/{class}/`. Idempotent; rerun freely.

Acceptance tests:

```
python tests/test_walk_library.py
```

Validates every bundle against `schema/declaration-bundle.v0.1.json`,
every driver profile against
`H:/mpa-atlas/schema/driver-profile.v0.2.json`, and one bundle per class
projects to a valid contract-05 DataUpload for mpa-auditor.

## Bundle layout

A single `declaration_bundle.json` per (library cell × xdot_choice). See
[`schema/declaration-bundle.v0.1.json`](schema/declaration-bundle.v0.1.json)
for the full shape. Required top-level fields:

- `schema`, `bundle_id`, `tier` (`curated` | `user`)
- `signature` (v0.1: `manifest_hash` + `signed_by`; v0.2+: Ed25519 +
  BLAKE3 + JCS + DSSE-around-in-toto)
- `substrate_class`, `xdot_choice`, `tau_obs`
- `provenance` (citation, license, optional DOI; license NEVER null)
- `columns` (per-column units, coverage_range, validity_range,
  range_source)
- `observable` (canonical `(tau, C, chi[, sem])` rows)
- `declaration_trail` (per-decision provenance: curator | researcher |
  llm_assist | mcp_tool | defaulted)

Optional:
- `scalar_observables` (e.g. `phase_locking_r` for γ_AB constraint)
- `fit_provenance` (curator-path leading-order canonical-parameter
  estimate at the operating point — seeds the driver profile's
  translation_field. The full inversion fit lands at v0.2 in conform per
  [SUITE_BLOCK_IN.md](../mpa-central/SUITE_BLOCK_IN.md).)
- `declaration_assistant` (researcher path only — model id, MCP tools
  used, N-of-2 consistency status)
- `raw_data_archive_ref` (optional pointer to the raw time-series)
- `version_context` (tool / cdv1 / MCP / model versions)

## What lives where

| Subdir | What |
|---|---|
| [`schema/`](schema/) | The auditor-facing contract (`declaration-bundle.v0.1.json`). |
| [`conformer/curator/`](conformer/curator/) | The library → seed-corpus pipeline. Pure Python, no LLM. |
| [`conformer/researcher/`](conformer/researcher/) | Researcher-path placeholder; to be built. |
| [`output/seed-corpus/`](output/) | Staging output. `.gitignore`d. PR into mpa-auditor is a separate manual step. |
| [`tests/`](tests/) | Acceptance tests (run on the staged output). |
| [`docs/`](docs/) | Roadmap, foundational questions/answers, next-session handoff, research-findings synthesis. |

## What this repo does *not* do

- **Run substrate simulations.** That's substrate-package territory
  (`mpa-brain`, `mpc-glass`, `mpc-quantum`) consumed via
  `mpa-central/library`. We read grind output; we never regenerate it.
- **Audit data.** That's `mpa-auditor`. We produce the input.
- **Build the backward map.** Per mpa-auditor §Q13, only the *forward*
  half (canonical → substrate-native) is ever built. The backward map
  is replaced by forward-sweep search in the auditor's Inversion Engine.
- **Edit `mpa-atlas`.** We read cdv1 + RFC-S + receipts. Spec questions
  route through mpa-auditor → mpa-atlas Appendix B, not through here.
- **Edit `mpa-auditor`'s `contracts/` or `corpus/`.** We commit to
  `mpa-auditor/seed-corpus/` via PR; that's the only file we write into
  the auditor's repo.

## Smoke test — load a curated bundle into mpa-auditor

Until the auditor's bundle-import migration lands, the seed-corpus
bundles project to valid contract-05 DataUploads. Manual check:

```
python -c "import json; b=json.load(open('output/seed-corpus/ck-glassy/glass__T0.500__spin-flip.bundle.json')); from tests.test_walk_library import _bundle_to_data_upload; print(json.dumps(_bundle_to_data_upload(b), indent=2)[:2000])"
```

A future session wires the auditor's `data-engine.js` to consume the
bundle directly (bundle-import migration, tracked on the auditor's
ROADMAP).

## Session Log

| # | Date | Session | Result | Notes |
|---|------|---------|--------|-------|
| 0 | 2026-05-15 | Bootstrap | Repo scaffolding; `declaration-bundle.v0.1` schema; curator-path post-processor over 60 library cells (16 brain + 22 glass + 22 quantum); 3 driver profiles + 60 bundles staged; acceptance tests pass (60/60 cells, schema validation, contract-05 projection). | Outside-model research on the agentic-tool landscape returned before bootstrap (`docs/research-findings.md`) — schema declares the Ed25519/BLAKE3/JCS/DSSE signing strata as forward-compat fields so v0.2 bundles land without a schema bump; v0.1 bundles use plain `manifest_hash + signed_by`. Brain → `neural-population` chosen as the closest match in the seeded 12-class roster; alternative `mpa-brain-langevin` is a class-genesis decision deferred. Glass `chit = Tc - T` follows cdv1 convention (chit ≪ 0 ⟹ r); the bootstrap text appeared to carry a sign flip — flagged in `docs/foundational-questions.md`. |

## License

MIT (consistent with mpa-central, mpa-atlas, mpa-auditor).
