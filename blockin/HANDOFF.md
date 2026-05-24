# HANDOFF — conform block-in

Slow-invariant carrier. CONTRACTS as the silhouette firms. The session's *question*
lives in the library (a hand-authored `questions/<slug>/entry.md`), not here. This
file carries only what persists across sessions.

Full design + why: memory `project_conform_blockin_apparatus`. Repo context:
mpa-conform/CLAUDE.md, mpa-central/SYSTEM_OVERVIEW.md.

---

## 0. Resistance line  [stable]
Reaching for the tau_obs sweep, the bootstrap cost, the full characterization
tensor, or the 10-category protocol as a *plan*? Stop — you're painting scales.
One brittle vertical at a time; the silhouette precipitates, it is not designed.

## 1. Rules of the game  [stable — do NOT grow]
- **Researcher-voice questions.** One observable, "is it nominal?", in the
  researcher's own field terms. They bring ONE operating point, not a sweep.
  Framework structure (chit / regime / FDR migration) lives only in the sealed
  `answer_path` — never in the blind packet. Researcher-voice IS the blinding.
- **nominal = interior of the open interval; headroom to the nearest asymptote is
  the reading.** "You are here, with this much room," not a regime lecture.
- **kernel pre-gate first**: sweep tau_obs; k_frust must NOT migrate (kill if it does).
- **FDR locus = universal readout** (chi vs C(0)-C(tau)); always computable.
- **open-interval / NaN tripwire**: never test "= boundary"; test departure toward it.
- **route-don't-mix**: `cage_edges` are conditional routes kept as structure (the
  Catmull-Clark cage — collapse axes freely, but record where a slice points at a
  neighbor, or it smooths into disconnected islands).
- **data-path independence**: the sim makes the data, analytics makes the truth.
- **conform is the examinee, never the answer key.** Ground truth is always analytic.
- **blind packet** = { question, minimal_structure, data_path }. Nothing else.
- **brittle is the mandate.** Team of ~3, not NASA, not ten years. Bespoke per
  substrate; the common shape precipitates later, it is not built up front.

## 2. Silhouette-so-far  [pointer — do not duplicate here]
The silhouette is the **pipeline**, and it lives in `blockin/PIPELINE.md`, not here.

**Workflow vs pipeline — do not re-merge (this slip recurs):** this file is the
WORKFLOW (the method — how we pose verticals and accrete the silhouette). PIPELINE.md
is the OBJECT under study (MPA's data-prep machinery). The workflow *wraps* the
pipeline; the loop's single "answerer-session" step (§5) **is** one traversal of
PIPELINE.md. Thin seam: blind packet + data in, view + verdict out.

Status: PIPELINE.md is ASSUMED (design-derived) — zero verticals have tested any
module. Contours get marked EARNED as verticals land. Researcher-voice-as-blinding
stays a workflow rule (§1); the minimal-structure gate lives in PIPELINE.md's SELECTION
module.

## 3. Open hypothesis under test  [shrinks as resolved]
- **10-category separability**: do real substrates land in one category cleanly, or
  smear across several? (Unanswered — testing by accumulation.)

## 4. Vertical ledger  [append 1 line/session; compress periodically]
```
slug                  | category claimed | clean/smeared | bound (first asymptote, Δ→next) | residue
laser_ro_nominal_v1   | 1 (Vertex)       | CLEAN         | underdamped band ζ=0.32 Q=1.58; 1-sided headroom→critical(ζ→1) | BLIND MATCH (placement+nominal, RMS 3e-7); 2-sided headroom NOT closeable from 1 pt → needs Q(χ̂) band/sweep (readout-bridge finding, rediscovered blind); no cage_edge, no KILL; not NULL (refined: blinding contour earned). earned/.
```

## 5. The session loop  [stable]   (mechanics: PROTOCOL.md)
```
enter HANDOFF
-> pose (dumb): pick entry, run its freeze, SANITIZE data, emit blind packet + blind data
-> answerer-session = a BLIND SUBAGENT (own context, sanitized inputs only — never the
   seal): (1) kernel pre-gate, (2) FDR locus + bespoke instrumentation, (3) first
   asymptote + headroom; returns verdict + provenance-per-claim + self-describing view
-> unseal (orchestrator holds the seal): compare to entry.sealed_answer -> match/miss/kill
   (a MATCH with empty provenance = hollow MATCH, not a win)
-> if miss matches a cage_edge signature: route to the neighbor, re-pose (now or next)
-> deposit one residue line in the ledger (incl. bound/headroom); NULL pass if no refinement
-> accrete EARNED tags/findings (append, automatic); contraction is human-gated
-> every ~3 verticals: re-read the ledger, update §3
-> move spent entry to earned/; commit per PROTOCOL commit rule
```
`pose.py` is built: runs the slug's freeze, emits ONLY the pre-SEALED half to
`workspace/<slug>.packet.md`, and a code-side leak tripwire refuses to emit if a
framework token crosses into the blind half. Per-substrate freeze stays bespoke
(the common shape precipitates at substrate N, not before — that is design, not a gap).

## 6. Pointers  [minimal]
- **loop mechanics** (roles, read manifests, blinding, answerer contract, commit rule):
  `blockin/PROTOCOL.md`. The §5 loop below is the WHAT; PROTOCOL is the HOW.
- library: `blockin/questions/<slug>/` (entry.md + freeze + data/).
- seed substrates (clean ground truth, "our data"): class-B laser
  (mpa-central/library/{ro_damping_audit,laser_conform_Q}.py), kww_oracle,
  two_temp_ou, ou_equilibrium, Banach, driven_ring / banach_frustrated.
- HOLD (known-contaminated, do NOT seed from): unnormalized quantum chi, zero-filled
  brain C/chi, null glass tau_env (mpa-central DEFERRED.md library-refresh), and any
  conform-touched seed-corpus bundle (examinee output).
- conform pieces to quarry (as examinee, never answer key): conformer/compute/
  {inversion, gfdr_model, five_vector}.py.

---
### Pick up here (end of session 2026-05-24)

This session built the apparatus and found its shape; it did **not** run a vertical.
- The **bounding box** of MPA data prep (~80 questions) and the **sparsification
  cuts** that collapse it — all in `PIPELINE.md`.
- The **pipeline vs workflow** split (this file = workflow; `PIPELINE.md` = the
  object / silhouette). Do not re-merge — the slip recurs.
- The **dev/prod phase cut**: dev relaxes precision/discipline (incl. pristine
  data-handling, reference-blind only), keeps topology (the arrow, camera-first,
  the seam); prod re-installs via the relaxation ledger (`PIPELINE.md` §Phase Interface).
- `README.md` rewritten to convey the force to a cold session (read it first if new).
- Old pre-block-in handoff (`docs/next-session-handoff.md`) deleted; its production
  owed-items (v0.5 5-vector persist, camera auto-derivation, glass-flip adjudication)
  are production-path, recoverable from git.

State: the loop is now AUTOMATED and vertical 1 is BLINDING-VALIDATED. `laser_ro_nominal_v1`
was re-posed to an isolated blind subagent (sanitized inputs only, never the seal); it
independently recovered γ_RO=0.100, ω_RO=0.300, ζ=0.316, Q=1.58 (RMS 3e-7) and independently
rediscovered the headroom finding. BLIND MATCH on placement+nominal; no cage_edge, no KILL;
vertex CLEAN. Canonical record (the blind run): `earned/laser_ro_nominal_v1/{RESULT.md,
answer.py,view.png}`. PIPELINE contours earned: ADMISSION, FRAME, SELECTION (I1/vertex),
ROOT OP (Banach inversion — load-bearer), + the blinding contour.

**Apparatus added this session (the pass-1 workflow gaps, now fixed):**
- `PROTOCOL.md` — the loop mechanics: two-context roles (orchestrator vs blind subagent),
  per-role READ MANIFESTS (the "deferred read" — and do NOT read `dev_profile.json`), the
  answerer contract (verdict = claims + provenance; `not_grounded[]` is where findings live),
  the hollow-MATCH guard, accrete-vs-contract (contraction human-gated), null-pass, and the
  COMMIT RULE. Authoring the next question stays human — the loop automates answer+refine only.
- `pose.py` now SANITIZES the data artifact (strips provenance, tripwire) — the blind boundary
  covers the CSV, not just `entry.md` (pass-1 leak: the raw header named the substrate + r=2.0).
- `view_header.py` — the self-describing view standard: every view stamps question + verdict +
  placement + grounded/not-grounded, sized to content. A loaded PNG explains itself.

**The standing finding — READOUT headroom bridge (confirmed blind).** A single operating point
closes PLACEMENT + the LOCAL nominal verdict + ONE-sided headroom (toward ζ→1, sluggish), but
NOT the TWO-SIDED headroom (which way "less damping" points) — that needs the framework Q(χ̂)
band, absent from one curve. SELECTION's single-point collapse vs READOUT's two-sided headroom
is the structural tension to resolve next.

**Next move — the live design question (decide, don't pre-build):** close the headroom bridge
one of two ways. (a) inject the analytic Banach Q(χ̂) map as the reference so a single point
gets placed on a *band* (`conformer/compare/banach_overlay.py` — overlay, not sweep); or
(b) author a multi-point sweep vertical (researcher brings 2–3 bias points). Author its
`entry.md`, then run the loop per `PROTOCOL.md` (pose → blind subagent → unseal → refine →
commit). Do NOT build both — one brittle vertical at a time (§0).
