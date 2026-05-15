# Next-session handoff — mpa-conform

**Disposable. Regenerated each session.** Carries the baton: what just
shipped, what to pick up next, the *immediate* next-step detail.

## What just shipped (Session 0, Bootstrap, 2026-05-15)

- Repo created at `H:/mpa-conform`; pushed to
  `github.com/ronviers/mpa-conform`.
- `schema/declaration-bundle.v0.1.json` — auditor-facing contract,
  declares v0.2 signing strata as forward-compat fields.
- `conformer/curator/walk_library.py` — post-processor over the 60
  `mpa-central/library/data/{brain,glass,quantum}/*.json` cells.
  Emits one bundle per cell + one driver profile per substrate-class.
  60/60 cells, 0 failures.
- `conformer/curator/substrate_class_rules.py` — leading-order forward
  translation rules (glass: `Tc - T`; quantum: `ln(p_th / p_base)`;
  brain: scenario table).
- `conformer/curator/driver_profile_builder.py` — RFC-S §4 / driver-profile.v0.2 assembler.
- `tests/test_walk_library.py` — acceptance test (all bundles validate;
  all driver profiles validate; one-per-class projects to contract-05).
- Docs: README, CLAUDE.md, ROADMAP, foundational-questions,
  foundational-answers, research-findings (synthesis of the May 2026
  unified report), this file.

## Outside research that's now load-bearing

[`docs/research-findings.md`](research-findings.md) synthesizes the
unified report (4 parallel briefs) at
[`mpa-auditor/docs/mpa_conform_unified_report.md`](../../mpa-auditor/docs/mpa_conform_unified_report.md).
Read it before scoping the next session — several v0.2 schema decisions
ride on it.

## Recommended next session — three live options

The user chooses. Each is independently scoped; none blocks the others.

### Option A — v0.2 schema (signing strata go live)
Flip `signature.algorithm` from `none` to `ed25519-dsse-intoto`;
switch `manifest_hash_alg` to `blake3`; switch `canonical_form` to
`jcs-rfc8785`; populate `envelope` (DSSE around in-toto Statement);
populate `pubkey_fingerprint`. Add a static `verify.html`. The schema
shape is already declared as forward-compat — this session implements
behind the existing field surface.

**Owns:** `schema/declaration-bundle.v0.2.json`; `conformer/curator/signing.py` (new);
`conformer/curator/walk_library.py` (extend to call signing);
`verify.html` (new static page).

**Time-shape:** small-to-medium. Crypto stack is well-trod; the only
real work is JCS canonicalization (RFC 8785) + DSSE envelope shape.

### Option B — Researcher path first slice (bring-your-own-model)
Build the first end-to-end researcher CLI:
`mpa-conform researcher <upload.csv>` → interactive declaration prompts
→ signed bundle. Adopt `openalex-mcp-server` (DOI), `citecheck`
(citations), and build the thin `pint`-wrapper MCP for units. License →
SPDX is local-deterministic (SPDX JSON + alias table, no LLM).

Bring-your-own-model mode first (API key in env → Anthropic /
OpenAI / Gemini); bundled-LLM mode is a follow-up session.

**Owns:** `conformer/researcher/cli.py` (new); `conformer/researcher/mcps/`
(broker config for the adopted MCPs); `conformer/researcher/spdx_lookup.py`
(local); `conformer/researcher/declaration_prompts.py` (interactive
gap-detection mirroring auditor §Q9).

**Time-shape:** medium-to-large. The interactive declaration loop is
the bulk; MCP brokering is glue.

### Option C — The correlator (Rust → WASM)
Port `multipletau`'s blocking algorithm to a standalone Rust crate;
add t_w / t_obs windowing + n_realizations averaging natively; compile
to WASM; expose canonical (τ, C(τ), χ(τ)) at multiple τ_obs windows.

**Owns:** new sibling repo or `vendor/mpa-correlator/` (architectural
choice — research-findings §3 + §5 argues this is the *first reusable
artifact* worth designing for outside-community use, so a sibling repo
is probably the right home).

**Time-shape:** medium. Bounded engineering — the math is solved; the
work is the port, the windowing logic, the WASM bindings, and the docs.

## Auditor-side ripple

The bundle-import migration row on
[mpa-auditor's ROADMAP](../../mpa-auditor/docs/ROADMAP.md) is now
unblocked (was waiting on "mpa-conform shipping its first signed
`declaration_bundle.json`" — first signed v0.1 bundles are now in
`output/seed-corpus/`). That session can land independently of any of
A/B/C above. Not this repo's session to take.

## Open questions still parked

See [`foundational-questions.md`](foundational-questions.md) for the
full list. Two need user adjudication (not a session-runtime decision):

- **Q-glass-chit-sign** — bootstrap text appears inconsistent with cdv1.
  v0.1 follows cdv1 (`chit = Tc - T`); should the bootstrap text be
  corrected, or is there an alternative reading?
- **Q-brain-class-mapping** — `neural-population` (v0.1 default) vs
  coining `mpa-brain-langevin` as a new class in mpa-auditor's
  `corpus/substrate-classes.json`.

Neither blocks the next session; both should be resolved before v0.2.

## Don't

- **Don't edit `mpa-auditor/contracts/` or `corpus/`.** That's by-design
  (file-import boundary). The exception is `seed-corpus/`, populated by
  PR.
- **Don't edit `mpa-atlas/`.** Spec questions route through
  `mpa-auditor/docs/foundational-questions.md` → mpa-atlas Appendix B
  pipeline.
- **Don't re-litigate the curator-path window-aggregation choice** unless
  a downstream consumer (M-Corpus, per-τ_obs analysis) actively asks
  for per-window slicing. The aggregation is honest and the
  `data_group_id` slice is a future-session refactor.
