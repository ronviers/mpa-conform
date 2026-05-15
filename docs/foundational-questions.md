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

## (other topics — append new sections below as they surface)
