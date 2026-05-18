# Roadmap — mpa-conform

The plan. Edited in place each session.

Parallel-document discipline (mirrors mpa-auditor):

| Document | Role | Lifecycle |
|---|---|---|
| **`docs/ROADMAP.md`** (this file) | The plan — what is built, what is next, in what order. | Stable; edited in place. |
| **`README.md` → `## Session Log`** | The history — one row per session, what shipped. | Append-only; never rewritten. |
| **`docs/foundational-questions.md` + `foundational-answers.md`** | Shape constraints (schema, file locations) + open architectural questions. | Append + correct. |
| **`docs/next-session-handoff.md`** | The baton. Regenerated each session. | Disposable; rewritten every session. |
| **`docs/research-findings.md`** | Synthesis of outside-model research (2026-05-15 unified report). | Append + correct as findings refine. |

---

## Status (2026-05-17)

**Three-way comparison display landed (this session, Session 5).** New
`conformer/compare/banach_overlay.py` + `compare` / `compare-all` CLI
subcommands render two-panel C(τ) + χ(τ) PNGs per bundle showing
empirical (markers + SEM), predicted (framework analytical at fitted
chit, recomputed in dimensionless τ frame), and Banach (protocol-matched:
single canonical state per measurement window, observable swept). All
22 ck-glassy cells render cleanly; output at `output/comparisons/<class>/`
(gitignored). Used to expose the cdv1 character / channel-richness gap
that drives next moves — see [handoff](next-session-handoff.md) for the
**parallax + channel-richness + adapting-not-overfitting** lens.

**v0.2 schema bump landed (Session 4).** `declaration-bundle.v0.2.json`
ships; curator path produces 60 v0.2 bundles validating clean. The bump
makes `fit_provenance` required and tightens its shape:
`fitted_params` + `predicted_locus` + `audit_delta` are required;
`inversion_provenance` + `inversion_validation` ride as optional
mpa-scale-solver v1.0.0 stamps (regime_at, gamut_classify). Per-cell
curator-time inversion fit via `conformer.compute.inversion.invert`
replaces v0.1's leading-order-rule-only fit_provenance. Substrate-
conditional tau rescaling (ROADMAP §v0.2 adjacent fix) applied inside
the fit; bundle's `observable.data` is native-frame.

**Audit signals now flowing (v0.2 doing its job):** ck-glassy fits land
clean (22/22 in_gamut, mean locus_residual 0.10). Two upstream issues
the audit surfaces for the first time:
- *quantum chi unnormalized* — library cells emit chi in [4, 12]; analytical
  gfdr_model assumes [0, 1]. 20/22 surface-code-qec fits rail at chit=-2
  (out_of_gamut). Library-side normalization issue.
- *brain C/chi zero-filled* — library cells emit identically-zero C and
  chi; fits land at substrate-rule defaults with high residual. Library-
  side observable-extraction issue.

These are pre-existing data issues now visible because v0.2's audit_delta
records them honestly. Fixing them is a separate fit-quality session
(library upstream + possibly chi normalization in curator path).

**Signing stays v0.1 posture.** The Ed25519/JCS/BLAKE3/DSSE bump is its
own parallel track (see §"v0.2 signing"); v0.2 schema accepts both v0.1
minimal-sign and forward Ed25519 fields, no gating between the two.

**v0.1 bootstrap (Phase 0, 2026-05-15)** is the prior landmark. Curator
path was producing 60 declaration bundles + 3 driver profiles from
`mpa-central/library` cells.

**mpa-scale-solver Python v1.0.0 shipped (2026-05-16).** v1 extends the
v0.1 seven-operation surface with: continuous-form `flow(canonical_initial,
nu, field) → CanonicalState` in Markovian scope; tangent-flow translation
field (RFC-S Appendix B item 1 leading-order auto-remap); the Banach
calibration substrate with closed-form `state_at(nu) = chit_0 *
exp(-lambda * nu)` as framework analytical truth; inverse-lookup-table
sidecar dispatch (table-first / compute-fallback); per-call
`ValidationReport` + `Provenance` trail on seven new `*_wrapped`
variants. Banach camera test passes max\|residual\| < 0.001; all v0
fixtures unchanged. v0 sigs unchanged. Available at
[github.com/ronviers/mpa-scale-solver](https://github.com/ronviers/mpa-scale-solver)
@ v1.0.0; sdist at `H:/mpa-scale-solver/dist/mpa_scale_solver-1.0.0.tar.gz`.

**Next unlock for mpa-conform:** fit-quality session. v0.2's audit_delta
exposed three upstream issues now in scope for a focused pass: (1)
quantum chi normalization (library or curator-side rescale before fit),
(2) brain C/chi zero-fill (library upstream), (3) glass tau_env null
fallback (substrate-class default instead of median tau). After that:
curator-side inverse-lookup-table sidecar production —
`InverseLookupSidecar` per driver profile, gamut-swept at chosen
`tau_obs_grid`. Banach reference producer (`BanachSubstrate.build_sidecar`)
already lives in the solver; real-substrate producers go here.

**Architectural authority:** `mpa-auditor/docs/foundational-answers.md`
§Q12 correction note (2026-05-15) — file-import boundary, agentic-vs-pure-static
split, two paths through one repo.

---

## Done

| Phase | Session | Result |
|---|---|---|
| 0 | Bootstrap (2026-05-15) | Repo scaffolding; `declaration-bundle.v0.1` schema; curator-path post-processor over 60 grind cells; 3 driver profiles; acceptance tests pass. |
| 1 | Inversion relocated (2026-05-15) | Ported auditor's inversion engine + forward physics + analytical/ensemble gFDR models + phase-locking observable to Python under `conformer/compute/`. Activity-scroll CLI at `conformer/cli.py`. Parity tests + 60/60 library inversions clean. First load-bearing rebalance per [SUITE_BLOCK_IN](../../mpa-central/SUITE_BLOCK_IN.md). |
| 2 | mpa-scale-solver Python v0.1.0 (2026-05-15) | Seven scale-management operations shipped as a sibling repo per the build handoff (now archived). Camera migration test max\|residual\| = 0.012; three seed-corpus profiles close round-trip. Native (Rust / C++) port is a future session reading the shipped Python. |
| 3 | mpa-scale-solver Python v1.0.0 (2026-05-16) | Continuous `flow()` + tangent-flow translation field + `BanachSubstrate` calibration + inverse-lookup-table sidecar dispatch + per-call `ValidationReport` + `Provenance` trail. Seven `*_wrapped` variants. Banach camera test max\|residual\| < 0.001; v0 fixtures unchanged. Handoff at `docs/archive/mpa-scale-solver-v1-handoff.md`. |
| 4 | v0.2 schema bump + curator-fit + scale-solver stamps (2026-05-16) | `declaration-bundle.v0.2.json` shipped. `fit_provenance` required + tightened (fitted_params + predicted_locus + audit_delta + scale-solver inversion_provenance/inversion_validation). `walk_library` calls `inversion.invert` per cell with substrate-conditional tau rescaling; bundle's `observable.data` stays native-frame. mpa-scale-solver v1.0.0 stamps (regime_at, gamut_classify) ride into audit_delta. 60/60 cells validate against v0.2 schema. ck-glassy fits clean (mean locus_residual 0.10, 22/22 in_gamut). Quantum + brain library issues surfaced through audit_delta — separate fit-quality session. |
| 5 | Three-way comparison display (2026-05-17) | New `conformer/compare/banach_overlay.py` + `compare` / `compare-all` CLI subcommands. Two-panel C(τ) + χ(τ) PNG per bundle showing empirical (markers + SEM), predicted (framework analytical at fitted chit, recomputed in dimensionless τ frame), and Banach (protocol-matched: single canonical state per measurement window, observable swept). 22/22 ck-glassy rendered. Two within-session iterations (RG-flow-sweep → protocol-matched after user spotted axis-conflation); resulting plot surfaced the **parallax + channel-richness + adapting** lens that drives the next single move (see handoff). |

---

## Next up

### Single next move — surface parallax in the comparison display
Read the raw grind cell alongside the bundle in
[`conformer/compare/banach_overlay.py`](../conformer/compare/banach_overlay.py)
and draw the 31 per-window empirical traces as faint gray lines under
the aggregated empirical markers. Render one ck-glassy cell, look at the
PNG, then plan the move after that from what's visible. Per the
single-move discipline (see `feedback_single_move_design` in user
memory): one move, render, look, decide. Resist option menus — the rows
below are context, not commitments.

### Bundle-import migration on the auditor side
**Blocked on:** auditor session (not this repo). The auditor's
`data-engine.js` switches from CSV ingestion to bundle ingestion. v0.1
bundles already project to valid contract-05 DataUploads, so a thin
auditor session can land this without waiting on v0.2.

### ~~v0.2 schema bump — embed real fit + predicted_locus + audit_delta~~ **LANDED 2026-05-16**
See Done table phase 4. Schema at
[`schema/declaration-bundle.v0.2.json`](../schema/declaration-bundle.v0.2.json).
Researcher path will populate the same `fit_provenance` shape when it
lands. Adjacent tau-rescaling fix lives in
[`conformer/curator/walk_library.py`](../conformer/curator/walk_library.py)
`_resolve_tau_scale` + `_rows_for_fit` (not `_extract_observable` per
the ROADMAP's original sketch — see §"Fit-quality session" above for
the open glass tau_env fallback question).

### v0.2 signing — Ed25519 + BLAKE3 + JCS + DSSE-around-in-toto
The v0.1 schema declares these fields as forward-compat. v0.2:

- Switch `manifest_hash_alg` from `sha256` to `blake3` (`pip install blake3`).
- Switch `canonical_form` from `json-stable-keys` to `jcs-rfc8785`
  (RFC 8785 canonicalization).
- Switch `algorithm` from `none` to `ed25519-dsse-intoto`.
- Add `pubkey_fingerprint` (curator's Ed25519 public key).
- Add `envelope` (DSSE envelope around an in-toto Statement).
- Bundle a static `verify.html` that uses WebCrypto to validate offline.

Reference: `docs/research-findings.md` §4 (Lightweight Provenance Signing).

### Researcher path — first slice
**Blocked on:** v0.2 schema landing, MCP picks settling. The first slice:

1. Adopt `cyanheads/openalex-mcp-server` for DOI/citation lookup.
2. Adopt `jhlee0619/citecheck` for citation parsing.
3. Build a thin `pint`-wrapper MCP for unit conversion.
4. Use SPDX-list JSON + alias table for license normalization (local,
   no LLM).
5. Build the first end-to-end researcher CLI:
   `mpa-conform researcher <upload.csv>` → interactive declaration
   prompts → signed bundle.

Bring-your-own-model first (Claude / GPT-5 / Gemini); bundled-LLM mode
comes after.

### Bundled-LLM mode (offline researcher path)
**Blocked on:** researcher path bring-your-own-model mode shipping.

Per research-findings §2:
- **Primary:** Gemma-3-4B at Q4_K_M (~2.3 GB) — best measured schema
  compliance (87%). Caveat: tends to wrap valid JSON in chatter; regex
  extract.
- **Secondary:** `qwen25-3b-openclaw` (March 2026 fine-tune) — best
  measured tool-use (0.989).
- **N-of-2 consistency check** — run both; accept on agreement;
  escalate to curator review on disagreement.
- **Pydantic at the boundary** — validate every LLM emission; retry
  with the validation error as feedback.

### The correlator (the "mpa-conform-solver")
**Blocked on:** researcher path needing it (real raw-time-series upload).

Per research-findings §3: port `multipletau`'s blocking algorithm to
Rust → WASM, alongside `mpa-solver`. Add t_w / t_obs windowing and
n_realizations averaging natively. Emit canonical (τ, C(τ), χ(τ)) at
multiple τ_obs windows.

This is the first reusable artifact the wider statistical-physics
community will likely care about. Design the API and docs accordingly.

### Audit classification port
Mirror Session 1's inversion port: bring the auditor's
`engines/audit-engine.js` (four-category classifier, slot-aware
reading, audit domain + silenced_regions) into `conformer/compute/`.
Bundle then carries `audit_delta` pre-computed; auditor reads, doesn't
classify.

### Forward physics + framework-grid generator
Mirror Session 1's port: bring the auditor's character + discrete
engines into Python (regime manifold, invariants, patterns, cobham
stack, synchroscope, trajectory). Generate `framework-grid.v0.1.json`
— a dense precomputed grid over (chit × γ_AB) — committed to
`mpa-auditor` as a static asset. Drives the auditor's Explore /
Browse mode without live numerics.

### Sidecars — RO-Crate + Data Package
**Blocked on:** researcher path landing.

Emit RO-Crate and Data Package manifests alongside the bundle so
Zenodo / Dataverse / institutional repositories can ingest without
bespoke connectors. Costs little; broadens audience meaningfully.

### Per-tau_obs DataUpload slicing
**Blocked on:** demand from M-Corpus or per-slice analysis in the
auditor. Today the curator path emits one bundle per cell with
window-aggregated `(t, C_mean, chi_mean)`. Per-`tau_window` slicing
(31 bundles per cell, linked by `data_group_id`) is a simple refactor of
`walk_library._extract_observable`. Defer until a consumer asks.

---

## mpa-scale-solver track

The scale-solver's v2 → v6 trajectory has its own self-evolving handoff
at [`H:/mpa-scale-solver/docs/BLOCK_IN.md`](../../mpa-scale-solver/docs/BLOCK_IN.md).
That doc is the single brief each scale-solver session reads cold; each
shipped version deletes its §vN section and refines the remaining ones.
Historical record lives in
[`mpa-scale-solver/README.md`](https://github.com/ronviers/mpa-scale-solver/blob/main/README.md)
§ Session Log.

Sequencing is up to the user. Scale-solver and conform sessions are
independent — v2 of the scale-solver doesn't gate conform's fit-quality
session (above), and vice versa.

| Version | Status | Theme |
|---|---|---|
| v1 | shipped 2026-05-16 | Continuous flow + Banach + sidecar + per-call validation |
| v2 | next | JAX + differentiability + Bayesian + N-mode + full I1–I5 + non-Markovian Caputo |
| v3 | queued | Cross-substrate ops + active learning + MCP server + learned field |
| v4 | queued | Streaming + symbolic query + notebook ergonomics |
| v5 | queued | Continuous self-test + sensitivity backprop + gradient-based inversion |
| v6 | queued | One-shot native port (Rust or C++); zero new features |

v5 is the last functional version; v6 is the port. v5 requires v2 only
(v3/v4 are content sessions, deferrable per block-in §Trajectory).

---

## Cross-repo seams

- **mpa-auditor** consumes bundles. Bundle-import migration row on its
  ROADMAP unblocks once v0.1 ships (now).
- **mpa-central** supplies library cells. Read-only. If `LIBRARY_SPEC.md`
  bumps (e.g. v1.0 → v2.0), the curator path may need a parallel reader.
- **mpa-atlas** supplies cdv1 / RFC-S / receipts and the driver-profile
  schema. Read-only. Schema bumps land here mechanically; spec questions
  route through mpa-auditor's foundational-questions.

---

## Later

- Web UI for the researcher path (a static page calling the bundled-LLM
  stack via WASM, mirroring the auditor's pure-static philosophy).
- The full MCP security posture (pin by hash, sandbox FS access,
  treat-user-text-as-untrusted) per research-findings §5.
- Reproducible-env packaging (`pixi` / `conda-pack`) per research-findings §5.
