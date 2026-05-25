# entry — coupling_ramp_v7
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I have a community of three populations whose interactions are *mutual* — each pair pushes
back on the other, a matched give-and-take, not a one-way chase around a loop. I can dial up
the overall strength of those interactions with a single knob, and I've recorded the
community at five settings, from gentle up to quite strong (levels 0 through 4). As I crank
the knob up, the abundances swing in bigger excursions and take noticeably longer to settle
back down. Here's what's nagging me: if I keep turning it up, is this community going to
start genuinely *oscillating* or *cycling* — going around the loop on its own — or even tip
over into something runaway/unstable? For each setting I want to know: is it still just
settling back to balance (however slowly), or has it started to genuinely cycle? Am I
approaching some edge — and if so, how close am I, and how would I know from the data? And
the big one: does cranking the interaction strength change *what kind of system this is*, or
is it the same kind of thing all the way up, just more so?

**minimal_structure:**
One community, three populations arranged in a loop, observed at five increasing
interaction-strength settings (level 0 = gentlest … level 4 = strongest). The interactions
are mutual / matched (the influence of one population on another is met by a comparable
influence back), not a one-directional cycle. Noise enters each population. The only thing
that changes from level to level is the overall interaction strength; the wiring and the
noise are otherwise the same. Each level was watched long enough for its own settling to
play out (so the observation windows differ in length across levels — that is deliberate, a
stronger setting needs longer watching).

**what_they_bring:**
For each level, one observation window reduced to the standard statistics in the community's
two-dimensional turnover plane (the plane in which the three abundances trade off; the
overall total is held aside). Per level: the autocorrelation C of the turnover signal; its
integrated step-response chi; the two *directed* cross-correlations Cxy and Cyx between the
two turnover axes; and the running tally of net cumulative turnover angle — phiMean vs
elapsed time, with its spread phiVar across the run's sub-windows. No model parameters, no
interaction-strength magnitudes, no noise level — just these measured curves, the same set
at each of the five settings.

**data_path:**
`H:\mpa-conform\blockin\workspace\coupling_ramp_v7.data.csv`
(columns: level, tau, C, chi, Cxy, Cyx, phiMean, phiVar. Five operating points — one
community at five interaction-strength settings. level is 0…4 (gentlest→strongest); tau is
the community's own clock: a lag for the two-point columns, an elapsed time for the
turnover-angle columns. Each level has its own settling window, so tau ranges differ.)

---
