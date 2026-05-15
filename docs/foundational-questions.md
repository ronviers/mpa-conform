# Foundational questions — mpa-conform

An append-as-you-go log of open architectural / design questions that
surface between sessions. Pair with [`foundational-answers.md`](foundational-answers.md);
both are read together at session start.

**Workflow.** When a question surfaces mid-session, append it here. When
resolved, the decision is written up in `foundational-answers.md` and
the question gets an **ANSWERED** marker plus a pointer. Don't delete
answered questions — they are the design record.

**Upstream authority.** The architectural decision that created this repo
is [mpa-auditor §Q12 correction note
(2026-05-15)](../../mpa-auditor/docs/foundational-answers.md). Treat it
as binding.

---

## Schema / bundle shape

### Q-bundle-extension-discipline — closed top-level vs open extension surface
The v0.1 schema declares `additionalProperties: false` at the top level
(parallel to mpa-auditor's contracts 01/02 pre-Q11). The bundle is a
**versioned exchange contract**, so adding fields means bumping
`schema` to `declaration-bundle.v0.2`, not riding `additionalProperties`.
Open question: should this hold long-term, or should we open a
designated extension surface (a nested `extensions: {}` object, or a
specific top-level key like `metadata`) for forward-compatible
researcher-path additions that don't merit a schema bump? The auditor's
Q11 resolution went the *open* direction for its contracts; the
declaration bundle might want to stay closed since it's a far simpler
shape and version bumps are cheap.

### Q-glass-chit-sign — bootstrap convention vs cdv1 convention
The bootstrap (`mpa-auditor/docs/mpa-conform-bootstrap.md` §5 step 4)
reads:
> Glass: chit ≈ −f(T − Tc) per cdv1 §Bridge to v9. T < Tc → chit ≪ 0
> (s-aging); T → Tc⁺ → chit → 0⁺.

cdv1 §The chit unit reads chit < 0 → r-regime, chit → 0⁺ → s-regime.
EA glass below Tc is the aging-CK phase (the s-regime in MPA terms;
library cells carry `operating_point.gt = 's'` below Tc as a receipt).
The bootstrap's "T < Tc → chit ≪ 0" appears inconsistent with the
cdv1 sign convention.

**Implementation choice (v0.1):** the curator path follows cdv1 —
`chit = Tc - T` (positive below Tc, negative above). The bootstrap text
likely carries a typo. Either cdv1 or the bootstrap is canonical;
flagging here so a foundational session resolves it.
**Status:** TRACKED — implementation follows cdv1; bootstrap text needs
either a correction note or an alternative interpretation.

### Q-brain-class-mapping — `neural-population` vs `mpa-brain-langevin`
v0.1 maps brain library cells to the `neural-population` class id (the
closest match in mpa-auditor's seeded 12-class roster). Bootstrap §5
step 1 named the alternative: coin a new class
(`mpa-brain-langevin`?). The trade-off:
- `neural-population` keeps the class registry stable and ships now.
- `mpa-brain-langevin` carries more honest semantics (Langevin
  dynamics on synaptic-weight trajectories vs broader "neural
  population" coverage) but is a class-genesis event affecting
  mpa-auditor's `corpus/substrate-classes.json`.

The user should call this. v0.1 defaults to `neural-population` and
surfaces the choice here for review.
**Status:** TRACKED — user adjudication.

---

## Agentic surface (researcher path, deferred)

### Q-mcp-vs-vendored — broker external MCPs, vendor own, or both?
Tracked upstream as
[mpa-auditor Q14](../../mpa-auditor/docs/foundational-questions.md#q14).
The 2026-05-15 unified research report (`docs/research-findings.md`)
recommends **both**:
- **Broker external** for mature surfaces (DOI via
  `cyanheads/openalex-mcp-server`, citation via `jhlee0619/citecheck`).
- **Vendor own** for surfaces that don't exist yet (`pint`-wrapper for
  units, the correlator MCP).
- **Keep local-deterministic** for surfaces that don't need an MCP at
  all (license → SPDX via JSON + alias table).

**Status:** TRACKED — research-findings carries the per-surface
recommendation; settles when the researcher path lands.

### Q-bundled-llm-choice — Gemma-3-4B + qwen25-3b-openclaw, or different stack?
Research-findings §2 names the current best picks. Open: do we ship
both as N-of-2 by default, or only when the user opts in (since it's
2× inference cost)?

**Status:** TRACKED — pick at researcher-path session.

### Q-signing-floor — v0.2 minimum, v0.3+ optional richness
v0.2 lands Ed25519 + BLAKE3 + JCS + DSSE-around-in-toto (per
research-findings §4). Open: is the in-toto Statement layer mandatory
at v0.2, or do we keep it optional (plain Ed25519 + JCS + manifest hash
as the floor, in-toto as the recommended add)? The "researcher with
downloaded copy in 2030" use case argues for the floor to be as small
as possible.

**Status:** TRACKED — pick at v0.2 schema session.

---

## Curator-path internals (parking lot)

### Q-per-window-slicing — defer or default to one-per-slice
v0.1 emits one bundle per cell with window-aggregated `(t, C_mean,
chi_mean)`. Bootstrap §5 step 2's recommendation was one-per-slice with
a `data_group_id` linking. Defer until a consumer (M-Corpus, per-tau_obs
analysis) demands it.

**Status:** TRACKED — deferred until consumer demand.

### Q-fit-provenance-shape — flat vs structured
v0.1 emits `fit_provenance.fitted_params` as a flat object — same
shape mpa-auditor's M-Inversion proper carries. The auditor's Q8 noted
that the *conditioning*-carrying object is the forward shape. Do
curator-path bundles need to carry conditioning estimates too, or is
that researcher-path territory only?

**Status:** TRACKED — likely settled when v0.2 lands.

---

## Scale management

### Q-scale-management-as-compute-scaffolding — τ_obs as the canonical scaffolding for all compute
v0.1 treats `tau_obs` as bundle **metadata** (declared, units, method).
Compute paths (inversion, observables, leading-order substrate rules)
operate in substrate-native τ directly. The Session 1 inversion port
exposed the consequence: fits saturate at the analytical model's tau
range for any substrate whose native τ doesn't accidentally line up
with the analytical model's canonical range.

v9 Foundational Principle #2 reads otherwise: *"τ_obs is the camera;
canonical representation is observer-relative."* RFC-S §1: *"Cross-
position structure (auto-remap as τ_obs moves) is the flow trajectory
itself."* RFC-S Principle #6: *"MPA scale management is **infinite**.
Infinity-machinery is imported directly, not patched on case-by-case."*

The criterion the user named (2026-05-15): **"if scale management was
not intense, it was not going to work."** v0.1's compute path is not
intense enough to be the framework. Every observation should flow
through a τ_obs projection on entry; every fit should be parameterized
by τ_obs; the bundle should carry both substrate-native (for display)
and canonical (load-bearing) versions of every observable.

**Resolution direction (2026-05-15, foundational session):** spawn
`mpa-scale-solver` as a sibling kernel to `mpa-solver` — distinct named
family of operations (RG-flow operator, regime classifier, gamut,
five-intent mapping, translation-field evaluator) per RFC-S §§1–5.
mpa-conform vendors it; the inversion rewires to canonical-frame on
entry. v0.2 schema bumps to make `tau_obs` compute-active and add
`observable.canonical_data` as the load-bearing field.

**Status:** RESOLUTION-DRAFTED (2026-05-15) — see
[`docs/mpa-scale-solver-bootstrap.md`](mpa-scale-solver-bootstrap.md)
for the fork handoff. The scale-solver bootstrap is the unblocker for
v0.2; the schema bump and curator-pipeline rewrite ride in once it
ships.

## (other topics — append new sections below as they surface)
