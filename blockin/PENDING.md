# PENDING — the open-state register (working-tree bookkeeping)

A standing register of everything **deliberately left open / floating** in this repo's working
tree, plus cross-repo crumbs riding with it. It is **not** part of the block-in apparatus (that
is the four modules — PIPELINE/WORKFLOW/meta-SOP/HANDOFF); it is a coordination ledger the
block-in's §0 reconcile leans on. It lives in `blockin/` for adjacency to the baton and the
reconcile, but its **scope is the whole repo** — most of what floats here is *not* block-in work.

**Why it exists.** Floating is fine — even preferable — during dev. The hazard is not the
floating; it is *undocumented* floating under session-to-session amnesia: a fresh session sees a
dirty `git status` and cannot tell expected-float from real drift. This register makes floating
**safe**, so nothing has to be force-closed each session just to keep track of it.

**The reconcile contract (consumed by meta-SOP §0).** Diff `git status` against this register:
- a path/arc **listed here** → **expected-float**: leave it, do not clobber it, do not bundle it
  into an unrelated commit;
- a change **not listed here** → **drift to investigate**: a stale baton, another arc, or real
  work to reconcile — surface it (do not guess).

**Cadence + upkeep.** Standing / cross-pass — it changes slowly, as arcs land or open (distinct
from HANDOFF's per-pass churn). When an arc lands, **delete its row**; when something new starts
floating, **add a row**. Keep it thin: a register, not a ticket tracker. Detail lives in the
referenced docs, never duplicated here.

---

## Open / floating (dated)

| since | what (paths / arc) | kind | why floating | rides-with / owner | close-condition |
|---|---|---|---|---|---|
| 2026-05-23 | `CLAUDE.md`, `README.md`, `docs/` renames (`ROADMAP`→archive, `next-session-handoff` del) | uncommitted-arc | cross-repo doc consolidation cdv1→mpav1, in-flight (README/CLAUDE still name `laser_ro_threshold_v2`, stale) | consolidation arc (Ron) | arc lands; README/CLAUDE four-module lists then gain a PENDING reference |
| 2026-05-22 | `conformer/compute/{inversion,five_vector}.py`, `conformer/cli.py`, `docs/{asymptotic-closure-proposal,banach-substrate-reference,five_vector_inversion_blockin}.md`, `scripts/test_*.py`, `scripts/census_in_family.py` | uncommitted-arc | five-vector inversion (X-recovery fitter) WIP | five-vector arc (Ron); design in `docs/five_vector_inversion_blockin.md`, status in `mpa-central/DEFERRED.md` §mpa-conform | arc lands |
| 2026-05-25 | `README.md` `docs/` row — deferral-doc pointer | riding-crumb | one line layered inside the single monolithic consolidation README hunk; cannot be peeled out to commit alone | rides with the consolidation arc | commits with that arc |
| 2026-05-25 | `mpa-central/DEFERRED.md` — conform→viewer crumb (§mpa-conform) | riding-crumb (cross-repo) | added to a file already carrying Ron's homochirality §846 entry; mpa-central has **no gitleaks hook** | rides with the mpa-central arc | commits with that arc (or patch-stage just the hunk + manual `gitleaks protect --staged --redact` on request) |

## Deferred-for-later (pointers — not working-tree state; here so there is one entry point)
- **conform→viewer design dials** → [`docs/deferred-for-auditor.md`](../docs/deferred-for-auditor.md) (grown; present/expose/lag + the freeze-can't-compute detector + watch-list/entry).
- **cross-repo parking lot** → `mpa-central/DEFERRED.md`.
