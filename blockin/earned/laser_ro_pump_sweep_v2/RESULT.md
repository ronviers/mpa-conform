# RESULT — laser_ro_pump_sweep_v2   (graded 2026-05-25, DEV — MISS-with-finding, meta-validity P)

Second vertical, first **I2** (sweep / migration along a control axis). The escalated
move (meta-SOP §2): subdivide v1's single operating point into a 4-curve pump sweep so
the two-sided headroom v1 could not close becomes groundable. What it tested: can conform
take a researcher's ordered settling sweep (no framework terms — "low to high drive") and
(a) place each curve, (b) read the non-monotonic response band, (c) name where the
response is healthiest, (d) correct "more drive = more margin"?

Run BLIND: a fresh isolated answerer saw only the sanitized packet + `data/*.data.csv` +
the sanitized `*.traversal.md` — never `entry.md`, the raw `.frozen.csv`, any freeze
script, or the raw `PIPELINE.md`. `answer_fit.py` / `answer_view.py` / `verdict.md` /
`view_*.png` ARE that blind run.

## Verdict: MISS-with-finding (meta-validity P) — placements MATCH, bottom-line verdict INVERTED

The conform machinery reproduced the analytic truth; the **question** is what failed.

- **Placements MATCH.** Independent single-curve damped-mode fits recovered the sealed
  per-curve regimes — blind ζ vs sealed ζ_nat: curve 1 `2.67 / 1.60` (both overdamped;
  magnitude loose — overdamped ζ is poorly constrained), 2 `0.90 / 0.82`, 3 `0.28 / 0.32`,
  4 `0.55 / 0.57`. Band shape MATCH: non-monotonic with the extremum at curve 3, curve 1
  the over-damping wall (not instability).
- **Anchor-and-assert SATISFIED.** The blind fit independently placed curve 3 at ζ≈0.28,
  reproducing v1's earned ζ≈0.32 at the same operating point. Cross-pass drift: none.
- **No KILL.** Single mode every curve, no loop/current signature, curve 1's ring=0 read
  correctly as regime-zero (overdamped), not a boundary attained.
- **Two-sided headroom became groundable** — the *mechanical* aim of the escalation
  worked: the answerer named both ends (low = overdamped/sluggish wall; high = recovering,
  not a wall). v1's `not_grounded[]` item is closeable once the data spans the band.

**But the researcher-facing verdict inverted:** the seal says healthiest = **curve 3**
(the Q-peak / crispest ring = the sweet spot, roll-off past it); the blind answerer says
healthiest = **curve 2** (nearest a well-damped ζ≈0.7), with the crisp middle (curve 3)
the **lowest-margin** point. Both agree curve 3 is the crispest — they invert whether that
is *healthiest*.

## Finding — the verdict flips on a health-metric the packet never supplied

"Healthiest" is not what the Jacobian computes. The freeze computes ζ/Q/ω (both runs
reproduced them); turning those into "healthiest" requires choosing a metric —
**Q-crispness** (seal → curve 3) vs **ζ-stability-margin** (blind → curve 2) — and the
data places those at opposite curves. The blind packet did not carry the metric, so the
blind answerer took the general-engineering default (ζ≈0.7 is the healthy settle) and
reached the opposite, defensible conclusion.

Per the meta-SOP answer-key safeguard, the sealed verdict's "healthiest = curve 3" is
**prose-asserted beyond its computed basis** — exactly the seam a genuinely blind answerer
splits. The vertical therefore lacks **teeth** (meta-validity P): its verdict is not
hard-to-vary because it is not uniquely determined by the blind data. This is NOT a conform
failure (placements + band + anchor all held); it matches no `cage_edge`, so the mechanical
"MISS → ISOLATE (conform broke)" route misfits — the defect is the question, not conform.

→ The READOUT two-sided-headroom contour does **NOT** earn `[EARNED]` from this pass. The
*mechanical* groundability was shown, but the verdict layer is unresolved. Next move:
re-author **v3** with the health metric disambiguated in researcher voice — either supply
it ("I want a fast clean settle without overshoot" → ζ-margin → curve 2; or "I want the
sharpest resonant response" → Q-crispness → curve 3) or pose a value-free verdict the data
uniquely determines (e.g. "which curve rings most / settles slowest"). That re-pose adds
the teeth (meta-SOP §2 SHARPEN); authoring stays gated.

## Blinding — intact

The answerer used "zeta" naturally (the native output of fitting a damped second-order
model — discovery from the data, not a leak) and never referenced pump ratios, "laser",
"class-B", or the sealed Q=1.5; its ζ values are its own fits, close to but not identical
to the seal. The pass is a real blinding test, and it cut against the seal.

## Apparatus fixes this pass (folded into the blinding commit)

- `pose.py` `blind_half` matched `## SEALED` as a raw substring, so the entry's own header
  comment (which names the marker) split the packet empty. Fixed to match the divider as a
  section-header *line*.
- `pose.py` now emits a sanitized `workspace/<slug>.traversal.md` (strips earned/finding
  blockquotes + `[EARNED]` tags, fail-closes on substrate/answer tokens). PIPELINE.md had
  accreted the v2 answer + substrate names into the doc the blind answerer was required to
  read — the canonical read-path leaked. WORKFLOW §3 now points the answerer at the
  sanitized traversal; meta-SOP §3 records the blockquote/tag convention.

## Reproduce
`python blockin/earned/laser_ro_pump_sweep_v2/answer_fit.py` then `answer_view.py` (read
the sanitized data; re-emit the fits + view). The freeze
(`freeze_laser_ro_pump_sweep.py`) regenerates the data from the laser's own NESS
propagator — data-path independent of conform.
