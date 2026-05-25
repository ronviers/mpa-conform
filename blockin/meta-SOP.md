# meta-SOP — the evolution governance (how the three artifacts evolve)

The **meta-SOP**: the standard operating procedure for how a pass-result *evolves* the
pipeline, the workflow, and the handoff, and how the *next* question is chosen. It is
the fourth module — and it is a different **level** from the others, which is exactly
why it gets its own file (modular sparsification):

- **WORKFLOW.md** is *also* an SOP — the **pass-SOP**: how to take one measurement
  (traverse the pipeline → a graded verdict). It operates *on the pipeline*.
- **This file is the META-SOP**: how a verdict+residue *evolves the artifacts* and
  *selects the next question*. It operates *on pipeline + workflow + handoff*.

If you find yourself writing "how to run a pass" here, it belongs in WORKFLOW. If you
find yourself writing "how to evolve the docs / pick the next question" in WORKFLOW, it
belongs here.

**The verb is not the same for all three:**
- the meta-SOP **refines** PIPELINE (accrete earned contours) and WORKFLOW (patch a
  method gap a pass exposed) — slow, semi-stable artifacts it *edits*;
- the meta-SOP **maintains** HANDOFF (rewrite the baton each pass) — fast working
  memory it keeps *current* (that's where the on-entry reconcile lives).

**The recursion terminates at the human.** The meta-SOP governs evolution of the other
three; refining the **meta-SOP itself stays with the human** — the top level is
human-held, the same instinct as "authoring stays gated." Otherwise it is SOPs all the
way up.

**Seams.** workflow → meta-SOP: **{verdict, residue, `not_grounded[]`}** in (a pass
produces it, this consumes it). meta-SOP → handoff: current state in, **next-move +
ledger line** out.

---

## 0. On-entry reconcile (do this FIRST, every session)

Before authoring or running anything, reconcile **disk vs HANDOFF** (`git log`,
`git status`, `git diff --cached`, `ls questions/ earned/`):
- **First, classify the dirty tree against [`PENDING.md`](PENDING.md)** (the open-state
  register). A path/arc listed there is *expected-float* — leave it, don't clobber it, don't
  bundle it into an unrelated commit. Anything dirty and *not* in PENDING is **drift to
  investigate**. This turns a messy `git status` from a judgment call into a mechanical check —
  the amnesia-safety this step exists for. (If you resolve an arc or open a new float, update
  PENDING: it is maintained, not archival.)
- Does `questions/` already hold an entry the handoff doesn't mention? (A half-authored
  or staged vertical from a prior session.)
- Is there uncommitted block-in state PENDING doesn't account for? (Drift the handoff/register
  didn't record.)
- Does the handoff's "current state / next move" match what's actually on disk
  (earned/, ledger, the last verdict)?
- **Parallel sessions share one working tree.** Is there *staged-but-uncommitted* or
  *untracked* work from another session/arc (a restructure staged here, a vertical
  authored there)? Treat it as real state: do not clobber it, do not bundle it blindly
  into your commit. **One writer per pass** — if another session is mid-pass on
  `blockin/`, do not also edit `blockin/`.

A resuming session that charges ahead on a stale baton is the failure this step
prevents (it bit pass 2: a vertical sat in `questions/` while the handoff still said
"author the next one"). Reconcile, then proceed. If disk and handoff disagree and you
cannot tell which is right, surface it to the human — do not guess. *(Validated
2026-05-24: a cold parallel session resumed from the baton, correctly read a staged
restructure + an authored vertical as expected state — not drift — and stopped at the
human gate. §0 working as intended.)*

## 1. The author role (non-blind)

The next `entry.md` is written by an **author-subagent**: a spawn *separate* from the
blind answerer, and **non-blind** — it creates the seal, so it may read everything
(prior `RESULT.md`, the substrate's freeze, the framework docs). It must not, however,
leak framework tokens into the blind half of the entry it writes (`pose.py`'s tripwire
catches that). Authoring is the highest-leverage judgment in the enterprise; it stays
gated (see §5).

## 2. Question evolution (verdict → next entry)

The author's move is fixed by the PRIOR pass's verdict:

| prior verdict | author's move |
|---|---|
| **MATCH** (genuine, refined a contour) | **ADVANCE** — author one vertical adding exactly **one vector**, chosen to make groundable whatever the last pass put in `not_grounded[]`. One vector, never two. |
| **MISS** + matches a `cage_edge` | **ROUTE** — re-pose the same question at the neighbor category the edge names. |
| **MISS**, no `cage_edge` | **ISOLATE** — do NOT advance. Author a *simpler* vertical (collapse one axis) to localize the broken module. Failure subtracts vectors. |
| **NULL / hollow MATCH** | **SHARPEN** — re-author the same target with teeth (operating point nearer an asymptote / a claim the data must ground). Persisting NULL → mark region converged, jump category. |
| **KILL** | **HALT** — hand to the human with the diagnostic. A dev KILL is a broken freeze/reading; do not auto-generate on a broken apparatus. |

Success adds a vector and moves outward; unanticipated failure subtracts vectors and
moves inward. The answerer's `not_grounded[]` is the generator's fuel — the honest "I
couldn't ground X" writes the next question.

**Escalation — a recurring gap promotes itself to the default (the SOP learns its own
defaults).** A `not_grounded[]` item that recurs across passes is not a per-vertical
curiosity — it is the signal that the *default data shape is mismatched to the reading
we say we produce*. When the same gap is parked **twice**, it escalates from "owed" to
**the default next vector**: closing it stops being optional and becomes the standing
move until it closes. *Worked instance:* "two-sided headroom not closeable from one
operating point" recurred (v1, then the staged single-point v2) → escalated to
**subdivide the operating-point cage-edge into a sweep** (v2 became
`laser_ro_pump_sweep_v2`). The human at the top of the recursion may also *elect to
spend* an owed item early — PIPELINE §5 explicitly named the sweep as the sanctioned
close for this buckle, and the human spent it; that is a legitimate exercise of the
top-level call, **not drift**. Generalize: every recurring gap escalates its own fix, so
the default keeps being learned from the ledger rather than decreed up front. (This is
why §0 reconcile and §4 aggregation read the ledger — escalation is a ledger-driven act.)
*Outcome (2026-05-25):* the sweep met its **conform-side** aim — two-sided headroom became
mechanically groundable. But the *verdict-ranking* layered on top ("which curve is
healthiest") inverted on a researcher utility-lens the blind packet cannot carry; that layer
became a **researcher dial** (not re-posed as a SHARPEN), parked in
`docs/deferred-for-auditor.md` Entry 1. Lesson for escalation generally: an escalated fix can
close its *mechanical* gap and still surface that the remaining ambiguity is an **interpretive
degree of freedom the researcher should own.** The detector is the answer-key safeguard run in
reverse: when the sealed verdict *cannot be freeze-computed*, that is not a teeth-defect to
sharpen away — it is the tell that the choice is a researcher dial (which axis to collapse,
what sign to read with, which lens defines "healthy"). Catalogue it as a viewport control;
do not pin a preference into a blind question. The framework *presents and exposes*; it does
not *lead*.

**Dev/prod constraint on "one vector":** a researcher bringing multiple operating points
is intent I2 = *prod*. Dev-legal single-vector moves keep researcher-voice (one point):
a τ_obs re-windowing sweep of the same curve, a harder single operating point near an
asymptote, or a new substrate/category. A gap that *only* a multi-point sweep or a
pipeline-reference change can close is logged as owed, not forced into a dev question.

**The answer-key safeguard (non-negotiable):** the author derives the `sealed_answer`,
but it must be **computed by the freeze / answer_path code** (e.g. Jacobian eigenvalues),
never asserted in prose. Otherwise the pass measures "two LLMs agree," not "conform
matches analytic truth." Until the author has a track record, a human eyeballs each
computed key before the blind pass runs.

## 3. Refine: accrete freely, contract only with the human

- **Accretion is append-only and automatable**: add `[EARNED v=<slug>]` tags to
  PIPELINE, write a finding/buckle note, append the ledger residue line. Do this every
  pass. **Keep earned/finding/status notes in a `> blockquote` or an `[EARNED …]`/
  `[CONTACT …]` tag** — never in the plain-text generic step body. `pose.py`'s traversal
  sanitizer strips exactly those forms to build the blind answerer's copy and fail-closes
  if a substrate/answer token leaks into the recipe; a finding written as a plain step
  line will refuse to pose. (This is the fix for the accretion-vs-blinding hole: the
  silhouette firms in PIPELINE for the human, while the answerer reads only the generic
  recipe.)
- **Contraction is gated**: compressing/deleting earned scaffolding ("the silhouette
  firmed") can smooth away a distinction still in use (*peel, not scrape*). The loop
  proposes contractions; a human approves them. Never auto-delete a hypothesis.
- **Workflow refinement** (not just pipeline): if a pass exposes a *method* gap — a hole
  in WORKFLOW or in this file — that is itself a finding. Patch it (accretion) or, if it
  changes the method's shape, flag it for the human. (Pass 1's blinding hole and pass 2's
  baton-drift were both workflow/meta-SOP refinements, not pipeline contours.)

## 4. Cross-pass aggregation (every ~3 verticals)

Re-read the §ledger (HANDOFF) and update the open hypothesis (HANDOFF §"Open
hypothesis", currently separability: do substrates land clean or smear?). One vertical
is a dot; the hypothesis only moves when the loop **reads its own ledger**. Without this
step the hypothesis stays inert.

## 5. Null pass + the gate boundaries

A pass **succeeds** if it produces a truthful residue AND either firms a contour or
names a gap. A pass that yields only a hollow MATCH with no refinement is a **NULL
pass** — flag it `NULL` in the ledger. A run of NULL passes means the silhouette
converged or the questions went toothless; both are signals for the human, not noise to
hide.

**Automated vs gated:** the loop runs **answer + refine** hands-off (pose → blind
answerer → unseal → accrete → deposit → commit). It does **not** run authoring
unattended — the author-subagent *proposes* the next entry; a human glance clears the
computed answer key; then the pass runs. (A fully headless API runner is deferred until
the policy survives ~3 passes — don't automate a loop you haven't watched work.)

## 6. Commit (backgrounded — the hook does the worrying)

A finished pass commits its `blockin/**` changes, and the part that used to need care is
**already automatic**: this repo has a gitleaks **pre-commit hook**
(`gitleaks protect --staged --redact`) that runs on every commit — no manual scan, no
ceremony; if it trips, fix the leak, never bypass it. That leaves three quiet defaults:

- **Scope is `blockin/`.** Stage the pass's files (+ any moved `earned/<slug>/`); never
  `git add -A`; never stage `dev_profile.json` or `output/**`. On a shared tree, glance
  `git diff --cached` so you don't sweep up another arc's staged work. A block-in commit
  is **mpa-conform-local** — it never reaches into `../mpa-auditor`: the conform→auditor
  seam is a PR into `seed-corpus/` (the §Q12 file-import boundary), not a commit. Safe
  radius = exactly `blockin/`.
- **Message:** `blockin: <slug> — <MATCH/MISS/KILL/NULL>, <one-line finding>`; surface the
  hash; don't push unless asked.
- **Surfaces to the human, never auto:** a meta-doc change to these four files *outside a
  pass*, and any destructive op (history rewrite, force-push, `earned/` deletion).

Standing authorization covers ordinary pass commits — the human asked once, here.

## 7. Result images — the minimal standard + the library

Every pass that reaches a verdict emits **one PNG**, built by `view_header.py`, and they
all share one format so the library reads uniformly — a single point and an N-test sweep
are the same *kind* of object. The standard is **minimal on purpose**: it does little, but
what it shows is complete. Add nothing decorative.

**Minimal contents (the floor).**

*A — the header band* (text, identical structure every time):
- **Stamp** — slug · timestamp · phase (e.g. `DEV/blind`).
- **The question, broken down as the researcher posed it** — the researcher-voice question
  (verbatim), the `minimal_structure`, and `what_they_bring`. This decomposition is what
  makes a result legible cold; keep it exactly this shape.
- **Verdict** — the answer in the researcher's terms (nominal? near which wall? which way
  is the room?).
- **Placement** — the framework read (the numbers): ζ/Q/γ/ω for a single point; the
  per-test placements **and the band** for a sweep.
- **grounded[]** — which observable/module established each claim.
- **not_grounded[]** — the honest limits; where the finding lives.

*B — the plot boxes* (graphs; count and content are bespoke per substrate, but always a
grid of boxes, every rendered property mapped to framework data — no decoration):
- **single test:** e.g. C(τ) + the conformed fit · the χ settle · the FDR locus.
- **sweep / multi-test:** the same box grid, plus — **required** — one box showing the
  **band** (the swept quantity vs the control axis, e.g. Q vs operating-point: the
  low→peak→roll-off the sweep exists to reveal), with the per-test curves shown (overlaid
  or small-multiples). Each test legible on its own; the band/migration readable by eye.
- Either way: nominality (or the band shape) must be **readable off the image without the
  prose**. *Grabs aren't story — the band is the story.*

**Naming → the library.** Write the PNG as **`view_<YYYYMMDD-HHMMSS>.png`** in
`earned/<slug>/` (use `view_header.timestamped_view_path()`, and pass its returned stamp as
the header's `date=` so the stamp on the image matches its filename). The timestamp is set
once per run, so re-runs and variants **accumulate** instead of overwriting. The **results
library is the union of `earned/**/view_*.png`** — browsable by slug (the folder) and by
time (the name); no separate gallery to maintain. (v1's legacy `view.png` stays as-is —
forward-only; the timestamped name applies from here.)
