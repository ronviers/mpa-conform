# RESULT — laser_ro_nominal_v1   (landed 2026-05-24, DEV — BLINDING-VALIDATED)

First vertical. What it tested: can conform take ONE researcher-voiced settling
curve (zero framework terms in the question) and return the correct nominal
verdict + two-sided headroom? I.e. does researcher-voice blinding hold, and can
conform place a single point on the (sealed) Q-band map?

> **Re-run BLIND 2026-05-24 (supersedes the plumbing-only first run).** After the
> harness was built (sanitized data artifact + isolated answerer context + commit
> rule, see `../../PROTOCOL.md`), the vertical was re-posed to a fresh subagent that
> saw ONLY the blind packet + the sanitized `data/laser_ro_nominal_v1.data.csv` —
> never `entry.md`, the raw `.frozen.csv`, or any freeze script. It independently
> recovered γ=0.1000, ω=0.3000, ζ=0.316, Q=1.58 (RMS 2.8e-7) and **independently
> rediscovered the headroom finding** (two-sided headroom not closeable from one
> point) without being steered toward it. The canonical `answer.py` + `view.png`
> here ARE that blind run. Conclusion: the placement+nominal MATCH and the headroom
> gap are robust under genuine blinding — not artifacts of an author who knew the
> seal. The author==answerer caveat below is therefore RESOLVED for this vertical.

## Verdict: MATCH (placement + nominal) / INCOMPLETE (two-sided headroom)

- **Root op (Banach inversion).** Conformed the single-mode Banach (a damped
  oscillator — the canonical form for "one driven mode + one bath") to C(τ):
  γ_RO=0.1000, ω_RO=0.3000, ζ=0.316, Q=1.58, RMS resid 2.8e-7. The fit is
  *exact* because the data is a linear-NESS propagator — the canonical form IS
  the substrate at this order.
- **Placement MATCH.** Underdamped RO band, ζ≈0.33, Q≈1.5 — equals the seal
  (ζ~0.33, Q~1.5 at the Q-peak χ̂~ln2). The answerer never needed to say "χ̂".
- **Nominal verdict MATCH.** Stable, underdamped ring-down (~6 visible cycles,
  envelope decays ~0.35×/half-cycle, flat by τ≈60); not marginal, not overdamped.
- **No cage_edge tripped** (no monotonic-Q artifact, no spurious current).
- **No KILL** (ζ never attained 0; single mode → no k_frust; trace stable,
  not growing).
- **View:** `view.png` — ring-down + conformed envelope (left), χ overshoot→
  plateau 1.698 (mid), FDR locus χ vs C₀−C as an inward spiral (right). The
  spiral is the NESS character; an equilibrium FDT would be a straight line.

## Finding — instability relocated to the READOUT headroom bridge (as predicted)

A single operating point closes PLACEMENT and the LOCAL nominal verdict, and a
**one-sided** headroom (toward more damping, ζ→1 critical/sluggish — directly
visible in how shallow the ring is). It does **not** close the **two-sided**
headroom: whether LESS damping heads toward instability or toward a SECOND
overdamped wall. That distinction is the entire correction to the researcher's
naive worry ("more ringing ⇒ nearer blow-up"), and it lives in the framework
Q(χ̂) band — non-monotonic, peaking here, overdamped walls both sides — which a
single curve does not carry. The answerer correctly **refused** to fabricate it.

→ SELECTION's "one operating point" collapse is in structural tension with
READOUT's "two-sided headroom." Closing it needs either (a) the analytic Banach
Q(χ̂) map injected as the reference (`conformer/compare/banach_overlay.py` —
overlay, places one point on a band), or (b) a multi-point sweep vertical
(researcher brings 2–3 bias points). That is the live design question for the
next vertical. One at a time — do not build both.

## Contamination — RESOLVED for this vertical

The *first* run was author==answerer: the sealed answer was seen while reading
`entry.md` to learn the apparatus, so it certified plumbing only. That hole was
the pass-1 finding about the WORKFLOW, and it drove the harness build (isolated
answerer + data sanitization + read manifests, `../../PROTOCOL.md`). The **blind
re-run** above closes it: a fresh isolated answerer reached the same MATCH from
sanitized inputs alone. Blinding rigor stays formally OFF in dev (PIPELINE §Phase
Interface), but this vertical was in fact run blind and survived.

## Reproduce
`python blockin/earned/laser_ro_nominal_v1/answer.py` (reads the frozen CSV in
`data/`, re-emits the view). The freeze (`freeze_laser_ro.py`) regenerates the
data from the laser's own propagator — data-path independent of conform.
