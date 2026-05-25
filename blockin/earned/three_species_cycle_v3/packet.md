# entry — three_species_cycle_v3
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I study a small community of three populations locked in a cyclic standoff — the first
outcompetes the second, the second outcompetes the third, and the third outcompetes the
first, round and round (the textbook rock-paper-scissors arrangement). When I watch them
over a long run they never settle: the abundances keep cycling, one cresting while the
next is rising and the last is crashing, over and over. Here's what I can't tell from
just staring at the wiggles: is this a *real, persistent turnover* — the community
genuinely going around the loop in one direction, never reaching a steady balance — or
is it just damped oscillation around a stable coexistence point that the environmental
noise keeps kicking back into motion? Those look the same in a single abundance trace.
And practically: if I could calm the environment down (less external buffeting), would
the cycling die away and settle, or would the community keep turning anyway? Is this
community stable, or is the perpetual cycling a sign it's near some edge?

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each one suppresses
the next around the cycle (1→2→3→1). Three nodes, three directed links, and the links do
NOT come in matched forward/back pairs: the influence of population 1 on 2 is not the
mirror of 2 on 1. It does not reduce to one population plus an environment — the loop is
the thing. Noise enters each population.

**what_they_bring:**
One long observation window of the three abundances, reduced to the standard statistics in
the community's two-dimensional turnover plane (the plane in which the abundances trade
off; the overall total is held aside). For that plane they bring everything that one run
yields: the autocorrelation C of the turnover signal; its integrated step response chi;
the two *directed* cross-correlations Cxy and Cyx between the two turnover axes (how axis x
now relates to axis y a lag tau later, and vice versa); and the running tally of how far
around the cycle the community has actually swung — the mean cumulative turnover angle
phiMean as a function of elapsed time, together with its spread phiVar across the run's
sub-windows. No model parameters, no coupling strengths, no noise level — just these
measured curves from the one run.

**data_path:**
`H:\mpa-conform\blockin\workspace\three_species_cycle_v3.data.csv`
(columns: tau, C, chi, Cxy, Cyx, phiMean, phiVar. One operating point — a single
community, a single observation window. tau is the community's own clock: a lag for the
two-point columns, an elapsed time for the turnover-angle columns.)

---
