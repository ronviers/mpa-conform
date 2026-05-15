# Research findings — agentic-tool landscape

**Synthesis of outside-model research, May 2026.** The canonical source
document is the unified report at
[`mpa-auditor/docs/mpa_conform_unified_report.md`](../../mpa-auditor/docs/mpa_conform_unified_report.md)
(consolidated from four parallel research briefs). This file extracts
the decisions that ride into this repo's roadmap and schema.

When the findings refine (next research dispatch, vendor updates,
benchmarks moving), edit this file and update the matching ROADMAP /
schema. The unified report itself stays as the source-time snapshot.

---

## Decisions extracted into v0.1

### Schema — forward-compat signing strata
The v0.1 `declaration-bundle.v0.1.json` carries:

- `signature.manifest_hash_alg ∈ {sha256, blake3}` — v0.1 uses `sha256`;
  v0.2 switches to `blake3`.
- `signature.canonical_form ∈ {json-stable-keys, jcs-rfc8785}` — v0.1
  uses `json-stable-keys` (sorted keys, no whitespace); v0.2 switches
  to JCS (RFC 8785).
- `signature.algorithm ∈ {none, ed25519, ed25519-dsse-intoto}` — v0.1
  uses `none` (manifest hash + signer name only); v0.2 switches to
  `ed25519-dsse-intoto`.
- `signature.envelope` — null in v0.1; DSSE envelope wrapping an
  in-toto Statement in v0.2.
- `signature.pubkey_fingerprint` — null in v0.1; required in v0.2.

This means v0.2 bundles can land in production code without a schema
bump for the field shapes; only the version constant flips.

### Schema — declaration_assistant N-of-2 placeholder
`declaration_assistant.consistency_check` carries the N-of-2 status
(per unified report §5). v0.1 leaves the shape minimal; v0.2 will lock
it once the researcher path's bundled-LLM stack settles.

### Schema — version_context for tool/MCP/model staleness
Mirrors mpa-auditor's `AuditDelta.version_context` (Q11 tidy). The
auditor surfaces conform-side staleness symmetrically.

---

## Decisions for the researcher-path session

### MCP picks

| Surface | Pick | Notes |
|---|---|---|
| DOI / scholarly metadata | `cyanheads/openalex-mcp-server` (MIT) | DOI/ORCID/PMID normalization; stdio + HTTP. |
| Citation parsing / BibTeX | `jhlee0619/citecheck` (TypeScript, MIT) | Policy-gated rewrite planning — flags ambiguous entries for human curation rather than silent rewrite. Aligns with the auditor's safety posture. |
| License → SPDX | **Build local, no MCP** | SPDX license-list JSON + alias table; optionally `license-expression` (nexB). |
| Unit conversion | **Build thin MCP** wrapping `pint` (BSD) | The `zazencodes/unit-converter-mcp` does hard-coded conversion; we want dimensional analysis. |
| CSV repair / parsing | Evaluate `anyrepair` (Rust crate, MCP-exposing) + `csvql` (Zig SIMD + SQL) | If they hold up, they save a build. Fallback: `charset-normalizer` + `clevercsv` + `frictionless` + `ftfy`. |
| Multi-τ_obs correlator | **Build** — port `multipletau` to Rust → WASM | Vendor alongside `mpa-solver`. See §3 below. |
| Provenance signing | `cryptography` (Python) + `minisign` (Frank Denis) | See §4 below. |

### Bundled-LLM stack (offline researcher path)

| Role | Model | Footprint | Why |
|---|---|---|---|
| Primary | **Gemma-3-4B at Q4_K_M** | ~2.3 GB | 87% schema compliance (AscentCore benchmark, April 2026 — strongest sub-7B). Caveat: wraps valid JSON in chatter — regex extract downstream. |
| Secondary | **`qwen25-3b-openclaw`** (March 2026 fine-tune) | ~2 GB | 0.989 tool score, 1.000 name accuracy, 0.983 argument F1 (MikeVeerman benchmarks). |
| Avoid | Llama-3.2-3B | — | 0.000 tool restraint; 34–52% schema compliance. Disqualifying for autonomous use. |
| Avoid for header mapping | Phi-4-mini | — | Documented repetition bug (rate ~0.052, up to 50× peers) corrupts CSV-header arrays. |
| Worth watching | BitNet-2B-4T (Microsoft) | <2.3 GB | 1-bit instruction-tuned; perfect JSON tool calls on laptop CPUs in <2.3s in cited tests. |
| Worth watching | Gemma-4 E4B, Qwen3-4B, SmolLM3-3B | — | Newer entries; less independent benchmarking yet. |

**Discipline:** N-of-2 consistency check on every researcher upload —
run both models, accept on agreement, escalate to curator review on
disagreement. Roughly 2× inference cost; orthogonal failure modes
(Gemma wraps in chatter; Qwen over-calls) make the union strictly
better than either alone.

**Pydantic at the boundary**, every time the LLM speaks. Validate every
emission; retry with the validation error as feedback. The difference
between 87% reliable and 99% reliable is the validation loop, not the
model choice.

**Licensing flag:** Gemma uses a custom non-OSI license; Llama same.
Qwen3 and Phi-4-mini are cleaner on redistribution. Verify each before
bundling.

---

## §3 — The correlator (the "mpa-conform-solver")

**Verdict:** must build, but every piece is solved and the building
blocks are vendorable. Port `multipletau`'s (Ramírez/Sukumaran/Vorselaars/Likhtman
multi-τ blocking) ~few-hundred-line numerical core to a standalone Rust
crate, add t_w / t_obs windowing and n_realizations averaging natively,
expose canonical (τ, C(τ), χ(τ)) outputs, compile to WASM alongside
`mpa-solver`.

Rationale: introducing a Python runtime boundary (via `multipletau` or
`pycorrelate`) would break the offline-after-download story. Rust →
WASM keeps the deployment dependency-free. The mathematics is fixed;
the port is bounded engineering.

This is the **first reusable artifact** the wider statistical-physics
community is likely to care about. Design the API and docs accordingly.

---

## §4 — Provenance signing

The four briefs converge tightly. Threat model: air-gapped verification
in 2030 by a researcher with only the downloaded bundle.

**Skip:**
- Sigstore / cosign — TUF root rotations break offline verification.
  X.509 + Merkle-proof surface is enormous relative to the use case.
- Full SLSA provenance — over-specified for researcher-generated bundles.
- OpenPGP via `pgpy` — works offline but keyring complexity + larger
  attack surface.

**Use:** Ed25519 + canonical-JSON manifest fingerprint, wrapped in an
in-toto Statement, enveloped in DSSE, with JCS (RFC 8785) canonical
serialization. The spectrum:

1. **Minimal viable:** canonical JSON manifest listing each bundle
   file with BLAKE3 or SHA-256 hashes; Ed25519 detached signature over
   the manifest; embedded public-key fingerprint. Verification: ~50-line
   Python verifier using `cryptography` (Apache-2.0/BSD), or `minisign`
   (~100-byte signature files).
2. **Add structure:** wrap payload in in-toto Statement (Subject →
   Predicate). Lightweight; what SLSA uses under the hood.
3. **Add determinism:** JCS canonical JSON eliminates whitespace /
   key-ordering signature breakage. *This matters more than algorithm
   choice* — non-canonical JSON is the most common cause of valid
   signatures failing verification in practice.
4. **Add envelope discipline:** DSSE wraps payload + payload type +
   signature into a single deterministically verifiable JSON object.

**Bundle layout (v0.2 target):**

```
declaration_bundle.json   # the bundle itself
manifest.json             # canonical JSON, BLAKE3 hashes of bundle body
manifest.dsse             # DSSE envelope around in-toto Statement
pubkey.txt                # human-readable Ed25519 public key
verify.html               # static page (WebCrypto) for browser-based verification
```

Degrades gracefully: even if DSSE / in-toto tooling vanishes, the raw
Ed25519 signature over the canonical manifest can be verified by hand
with any Ed25519 implementation.

---

## §5 — Emergent recommendations (from cross-reading the four briefs)

These are not in any single brief; they emerge when read together.

### Canonicalization is the actual product
Extraction quality is not the bottleneck. Deterministic serialization,
frozen upstream snapshots, retrieval timestamps, cache fingerprints,
replayable manifests *are*. Treat JCS canonical JSON, schema versioning
from day one, and explicit provenance for every external metadata fetch
(Crossref / OpenAlex — *mutable* upstream) as first-class requirements.
**Snapshot the upstream payload alongside the bundle; do not just record
the DOI.**

### An all-Rust/WASM porch is feasible
Combining Rust correlator + `anyrepair` (Rust CSV) + `csvql` (Zig SIMD)
+ `mpa-solver` (already WASM) suggests a single WASM blob for the
numerical and parsing layers. DuckDB-WASM as the streaming porch
engine. The static `verify.html` for provenance. The bundled offline
mode becomes the *primary* deployment story; the bring-your-own-model
API mode is a transparent overlay.

### Bundle includes its own verifier
`verify.html` (static, WebCrypto) lets the 2030 researcher verify
without installing Python, Rust, or `minisign`. Mirrors the
offline-audit philosophy. Pair with a `verify.py` for CLI users; ship
both.

### Two extraction models with orthogonal failure modes
Gemma-3-4B fails by emitting valid JSON wrapped in chatter; Qwen-2.5-3B
fails by over-calling tools or producing slightly off-schema JSON. The
failure modes are complementary. N-of-2 consistency check.

### RO-Crate and Data Package as sidecars
`declaration_bundle.json` stays canonical; emit RO-Crate and
`frictionless` Data Package manifests alongside so Zenodo / Dataverse
/ institutional repos can ingest without bespoke connectors.

### MCP security in offline mode
- Pin MCP server versions by hash.
- Sandbox LLM tool invocations to a scoped working directory.
- Treat any text extracted from user uploads as **untrusted input** —
  never concatenate into instructions (tool-poisoning).

### Reproducible environments from day one
`pixi` (prefix.dev, BSD) or `conda-pack` for relocatable env. The
reproducibility unit is pinned (Python deps + model weights + MCP
servers + correlator binary), and the build system must pin all of
them together.

### The correlator is the leading reusable artifact
A clean Rust crate for multi-τ FDR observables, with a sensible API
and good docs, is something the wider statistical-physics community
currently does not have. If `mpa-conform` is built well, this is the
piece most likely to take on a life of its own. Invest in API design
and docs accordingly.
