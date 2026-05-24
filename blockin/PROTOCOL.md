# PROTOCOL — how a block-in pass runs (the loop mechanics)

Thin operating doc. HANDOFF.md = the silhouette content (rules of the game + ledger).
PIPELINE.md = the object under study. **This file = the mechanics of running one pass**:
who reads what, how blinding is enforced, what the answerer must return, what gets
written back, and how to commit. Read it once; it does not get re-litigated per pass.

The loop automates **answer + refine**, never **question authoring**. `pose.py` is a
dumb dispatcher ("not an inventor"); choosing the next vertical and writing its
`entry.md` is human-gated judgment — the highest-leverage step, kept off the loop until
the generator precipitates.

---

## Roles (two contexts, never merged)

| | ORCHESTRATOR | BLIND ANSWERER |
|---|---|---|
| who | this session / the human-driven driver | a fresh subagent, spawned per pass |
| holds the seal? | YES (authors/unseals) | NO — must be unable to see it |
| job | pose → spawn → unseal → compare → refine → commit | traverse PIPELINE on the blind inputs, return a verdict + view |

Blinding is **structural, not honor-system**: the answerer runs in its own context and
is handed only sanitized inputs. It *cannot* read the seal because it is never given a
path to it. Pass 1 defeated blinding by reading `entry.md` to "understand the apparatus"
— a fresh agent would do the same. The split below makes that impossible.

## Read manifests (the deferred-read — obey per role)

**ORCHESTRATOR reads:** `HANDOFF.md`, `PIPELINE.md`, this file, the slug's `entry.md`
(incl. the sealed half — the orchestrator legitimately holds it), prior `earned/` only
if needed. **Do NOT read `dev_profile.json`** — it is ~83 KB of mostly recursive
`output/shots/*.exr` filenames; it is a context-bomb and informs nothing here.

**BLIND ANSWERER reads ONLY:**
- `workspace/<slug>.packet.md`   (the blind packet)
- `workspace/<slug>.data.csv`    (the SANITIZED data — never the raw `.frozen.csv`)
- `PIPELINE.md`                  (the traversal it follows)
- `HANDOFF.md` §1 (rules of the game) + this file's *Answerer contract* below
- `view_header.py`               (the view standard helper)

**BLIND ANSWERER must NEVER read:** `entry.md`, anything under `questions/` or
`earned/`, any `freeze_*.py` (substrate truth), the raw `*.frozen.csv`, or
`dev_profile.json`. Reading any of these invalidates the pass as a blinding test.

## Blinding boundary covers the DATA, not just the seal

The blind packet is `{question, minimal_structure, data_path}` — but `data_path` must
point at a file that does not name the substrate. `pose.py` sanitizes: it strips every
`#` provenance line from `.frozen.csv`, keeps only the column header + numeric rows,
trips if any prose or framework token survives, and rewrites the packet's `data_path`
to the sanitized copy. (Pass-1 leak: the raw header read `substrate: class-B laser …
r=2.0` — most of the sealed answer, sitting in the "blind" data.)

## Answerer contract (what the blind answerer returns)

A verdict is not a label — it is a set of **claims, each with provenance**. Required:
- **placement** (framework read): the conformed Banach member + deformation (e.g.
  `zeta, Q, gamma, omega`); fit residual.
- **verdict** in researcher terms: nominal vs departing-toward-an-asymptote; the
  headroom sentence ("you are here, with this much room").
- **grounded[]**: for each claim, *which observable / pipeline module* established it.
- **not_grounded[]**: every claim the inputs could **not** support — stated, never
  fabricated. *This list is where findings come from.* (Pass 1: two-sided headroom is
  not closeable from one operating point — that refusal was the whole result.)
- **view**: a PNG built via `view_header.py` so it self-describes (question + verdict +
  grounded/not-grounded + placement stamped on the image). Plots below the band are
  bespoke. *Grabs aren't story* — the band is the story.

**Guard against the hollow MATCH:** an answerer that emits the researcher-plausible
answer with empty `grounded[]` is a null result wearing a green check. A claim with no
provenance is not a claim. The orchestrator rejects a verdict whose `grounded[]` is
empty for a non-trivial claim.

## Unseal + compare (orchestrator)

Compare the answerer's verdict to `entry.sealed_answer` → **MATCH / MISS / KILL**.
- A **MATCH** must name *which pipeline module did the work*; a match the answerer could
  only have guessed (placement in `grounded[]` empty) is logged as a **hollow MATCH**,
  not a win.
- A **MISS** that matches a `cage_edge` signature → route to the neighbor, re-pose.
- A **KILL** (boundary attained / structure mismatch) halts and is diagnosed — in prod
  it is a framework falsification; in dev it is a bug in the freeze or the reading.

## Refine: accrete freely, contract only with the human

- **Accretion is append-only and automatable**: add `[EARNED v=<slug>]` tags, write a
  finding/buckle note, append the ledger residue line. Do this every pass.
- **Contraction is gated**: compressing/deleting earned scaffolding ("the silhouette
  firmed") can smooth away a distinction still in use (*peel, not scrape*). The loop
  proposes contractions; a human approves them. Never auto-delete a hypothesis.
- **Cross-pass aggregation (every ~3 verticals):** re-read the §4 ledger and update
  HANDOFF §3 (separability hypothesis). One vertical is a dot; the hypothesis only
  moves when the loop *reads its own ledger*. Without this step §3 stays inert.

## Null pass (make it visible)

A pass **succeeds** if it produces a truthful residue AND either firms a contour or
names a gap. A pass that yields only a hollow MATCH with no refinement is a **NULL
pass** — flag it `NULL` in the ledger. A run of NULL passes means the silhouette
converged or the questions went toothless; both are signals for the human, not noise to
hide.

## Commit rule (stop re-deciding this every pass)

Standing authorization for **block-in pass commits** (this is the human asking, per
mpa-conform CLAUDE.md "never auto-commit unless asked"):
1. Stage ONLY this pass's block-in changes: `blockin/**` (incl. the moved
   `earned/<slug>/`). Never bundle unrelated working-tree changes; never `git add -A`.
2. **gitleaks scan staged content first** (`gitleaks protect --staged --redact`) — this
   repo has no pre-commit hook. Abort the commit on any hit.
3. Never stage `dev_profile.json`, secrets, or `output/**` (large/gitignored artifacts).
4. Commit message: `blockin: <slug> — <MATCH/MISS/KILL/NULL>, <one-line finding>`.
5. Surface the hash. Do NOT push unless the human asks.
Destructive ops (history rewrite, force-push, `earned/` deletion) are NOT authorized —
they keep prompting.
