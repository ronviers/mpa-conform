# Foundational answers — mpa-conform

Resolved architectural decisions. Pair with [`foundational-questions.md`](foundational-questions.md).

This file is **revisable, not frozen** — when an answer turns out to be
wrong, edit it, add a correction note dated, and update the matching
question. Don't delete old answers; they are the design record.

**Upstream authority:** the architectural decisions in
[mpa-auditor §Q12 correction note (2026-05-15)](../../mpa-auditor/docs/foundational-answers.md)
are binding here. This file declares mpa-conform-internal decisions that
are downstream of §Q12.

---

## §0 — The bundle is the contract

The auditor accepts `declaration_bundle.json` and only
`declaration_bundle.json`. The bundle is the entire surface between
mpa-conform and mpa-auditor. There is no callback, no live link, no
runtime inference. mpa-conform writes; mpa-auditor reads.

**Schema authority:** [`schema/declaration-bundle.v0.1.json`](../schema/declaration-bundle.v0.1.json)
is authoritative. The hand-rolled validators (none yet — relying on
`jsonschema`) are a deliberate thin lagging subset (same posture as
mpa-auditor §Q11).

**Schema versioning:** the bundle is closed at the top level — adding
fields means bumping `schema` (`declaration-bundle.v0.1` →
`declaration-bundle.v0.2`). The auditor switches import logic on the
declared schema version.

---

## §1 — Two paths, one bundle

The curator and researcher paths produce **the same bundle shape**.
This is the load-bearing simplification: the auditor's bundle-import
logic does not branch on `tier`; the tier is metadata that gates
downstream aggregation, not import logic.

The two paths differ in *how* they fill the fields:

| Field | Curator path | Researcher path |
|---|---|---|
| `tier` | `'curated'` | `'user'` |
| `substrate_class` | Looked up from `SUBSTRATE_TO_CLASS_ID` | Researcher-declared (or LLM-assist-proposed) |
| `xdot_choice` | Read from grind cell `xdot_kind` | Researcher-declared |
| `tau_obs.method` | `'aggregated'` (window-aggregated reading) | `'declared'` / `'swept'` / `'defaulted'` |
| `provenance` | Synthesized from library metadata | Researcher-declared + DOI-verified via MCP |
| `observable.format` | `'canonical_fdr'` (pass-through from grind cell) | `'canonical_fdr'` (post-correlator) |
| `declaration_trail[].answered_by` | `'curator'` | `'researcher'`, `'llm_assist'`, `'mcp_tool'`, `'defaulted'` |
| `declaration_assistant` | `null` | Present (model id, MCP tools used, N-of-2 status) |
| `fit_provenance` | Leading-order substrate-class rule | Absent (researcher doesn't fit; the auditor does) |
| `signature.algorithm` (v0.1) | `'none'` | `'none'` |
| `signature.algorithm` (v0.2+) | `'ed25519-dsse-intoto'` | `'ed25519-dsse-intoto'` |

---

## §2 — Curator path: window-aggregated reading

The library cells carry per-`tau_obs`-window observables (the 31-entry
`per_window` array per `all_samples[]` row). The curator path reads the
**top-level** `C_mean` / `chi_mean` — a window-aggregated reading —
per bootstrap §5 step 3. This produces one bundle per cell, with 29–31
`(tau, C, chi)` rows from the `t_sample` grid.

`tau_obs.method = 'aggregated'` carries the why: the window choice was
deferred (aggregated across all 31 windows), not actively declared. A
future session can land per-window slicing (one bundle per cell ×
window = 31 bundles per cell), linked by `data_group_id`, when M-Corpus
or per-`tau_obs` analysis demands it.

---

## §3 — Forward-only canonical-parameter estimate

The curator-path bundle carries `fit_provenance.fitted_params` with
leading-order (chit, γ_AB) at the operating point, computed by
[`substrate_class_rules.canonical_params`](../conformer/curator/substrate_class_rules.py).
This is the **forward half** of the translation field per mpa-auditor
§Q13: canonical → substrate-native is built; substrate-native →
canonical is never built. The auditor's Inversion Engine still fits its
own (chit, γ_AB) from the observable; the bundle's `fit_provenance` is
a *seed* for the driver profile's translation field, not a constraint
on the audit.

**Substrate rules (v0.1, leading order):**

| Substrate | Rule | Notes |
|---|---|---|
| `glass` (ck-glassy) | `chit = Tc - T`, Tc = 1.0; γ_AB = 0 | Follows cdv1 sign convention; below Tc → s-aging side, above → r side. See Q-glass-chit-sign for the bootstrap-vs-cdv1 sign discrepancy. |
| `quantum` (surface-code-qec) | `chit = ln(p_threshold / p_base)`, p_threshold = 1e-2; γ_AB = 0 | Below threshold → chit > 0 (c-like); crossing → chit ≈ 0; above → chit < 0. |
| `brain` (neural-population) | Scenario table: committed → (+1.0, -0.5), suspended → (+0.05, 0), conflict → (0, +0.5, k_frust=true), reset → (-1.0, 0) | Conflict scenario flags `k_frust: true`. |

These refine as substrate-side measurement lands (same posture as
`mpa-central/library/TAU_ENV_OWED.md`'s `tau_env_analytic`).

---

## §4 — Signing strata (v0.1 minimal, v0.2+ full)

The v0.1 schema declares the full signing strata as forward-compatible
fields so v0.2 lands without a schema bump. v0.1 itself uses minimal
manifest hash + signed_by:

```jsonc
{
  "signature": {
    "manifest_hash": "<sha256 of canonicalized body>",
    "manifest_hash_alg": "sha256",
    "signed_at": "2026-05-15T...Z",
    "signed_by": "mpa-conform curator (v0.1 bootstrap)",
    "algorithm": "none",
    "canonical_form": "json-stable-keys",
    "envelope": null,
    "pubkey_fingerprint": null
  }
}
```

**v0.2 target** (per research-findings §4 — Ed25519 + BLAKE3 + JCS +
DSSE-around-in-toto):

```jsonc
{
  "signature": {
    "manifest_hash": "<blake3 of jcs-canonicalized body>",
    "manifest_hash_alg": "blake3",
    "signed_at": "...",
    "signed_by": "researcher orcid / curator name",
    "algorithm": "ed25519-dsse-intoto",
    "canonical_form": "jcs-rfc8785",
    "envelope": { /* DSSE envelope around in-toto Statement */ },
    "pubkey_fingerprint": "<Ed25519 public key fingerprint>"
  }
}
```

Per research-findings §4 the threat model — air-gapped verification in
2030 — eliminates Sigstore/cosign (TUF root rotations break verification
in the offline-after-download story). Ed25519 + manifest fingerprint
survives indefinitely; even if DSSE/in-toto tooling vanishes, the raw
signature over the canonical manifest can be verified by hand.

The bundle ships with a static `verify.html` (v0.2+) that uses
WebCrypto to validate offline. Mirrors mpa-auditor's pure-static
philosophy. See research-findings §5.

---

## §5 — What rides where

| Concern | Lives in |
|---|---|
| Schema (auditor-facing contract) | `schema/declaration-bundle.v0.1.json` |
| Curator-path pipeline | `conformer/curator/walk_library.py` |
| Substrate-class translation rules | `conformer/curator/substrate_class_rules.py` |
| Driver-profile builder | `conformer/curator/driver_profile_builder.py` |
| Researcher-path (placeholder) | `conformer/researcher/` |
| Open architectural questions | `docs/foundational-questions.md` |
| Resolved decisions (this file) | `docs/foundational-answers.md` |
| Outside-research synthesis | `docs/research-findings.md` |
| Per-session next-step detail | `docs/next-session-handoff.md` |
| Plan / sequence | `docs/ROADMAP.md` |
| History (per-session log) | `README.md` § Session Log |
