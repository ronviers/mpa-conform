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

## Status (2026-05-16)

**v0.1 bootstrap landed.** Curator path produces 60 declaration bundles +
3 driver profiles from `mpa-central/library` cells. Schema declares the
v0.2 signing strata as forward-compat fields; v0.1 ships with plain
`manifest_hash + signed_by`.

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

**Next unlock for mpa-conform:** the curator-side inverse-lookup-table
sidecar production session. Curator's `walk_library` produces an
`InverseLookupSidecar` per driver profile by sweeping the gamut at a
chosen `tau_obs_grid` and recording every (canonical, substrate) pair;
the bundle then ships the sidecar so consumers get sub-millisecond
inversion. Banach reference producer (`BanachSubstrate.build_sidecar`)
already lives in the solver; real-substrate producers go here. Optional
rewire of `conformer/compute/inversion.py` to call
`mpa_scale_solver.forward_sweep_invert_wrapped` (with validation +
provenance riding into the bundle's audit record) is deferred until the
v0.2 schema bump explicitly carries those fields.

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

---

## Next up

### Bundle-import migration on the auditor side
**Blocked on:** auditor session (not this repo). The auditor's
`data-engine.js` switches from CSV ingestion to bundle ingestion. v0.1
bundles already project to valid contract-05 DataUploads, so a thin
auditor session can land this without waiting on v0.2.

### v0.2 schema bump — embed real fit + predicted_locus + audit_delta
Now that the inversion is in-tree (Session 1), the bundle should carry
the fitted (chit, γ_AB) + predicted locus at the fitted point + the
audit delta — pre-computed at curator time. Schema bump
`declaration-bundle.v0.1` → `v0.2`. Curator's `walk_library` calls
`conformer.compute.inversion.invert` for each cell and embeds the
result; researcher path does the same when it lands.

Adjacent fix: substrate-conditional tau-rescaling for surface-code-qec
and glass cells before fit (today's fits saturate at the analytical
model's tau range — known limit from auditor's M6 session log, not
introduced by the port). Add tau_env rescaling step in
`walk_library._extract_observable`.

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
