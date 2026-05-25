# entry — three_species_cycle_noise_sweep_v5
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
This is a follow-up on a three-population community I looked at before — three populations
locked in a cyclic standoff (the first outcompetes the second, the second the third, the
third the first), which keeps cycling and never settles. Last time the one thing I couldn't
answer from a single run was the practical one: if I could calm the environment down — less
external buffeting — would the cycling slow down and eventually settle to a steady balance,
or would the community keep turning anyway? So this time I ran the SAME community at five
different levels of environmental noise, from a fifth of my usual buffeting up to four times
it (my usual setting is the middle one). For each level I reduced the run to the same
statistics. My question is simply: as I turn the environmental noise down, does the turnover
slow down or stop — is the cycling something the noise is driving — or does the community
keep cycling at the same rate no matter how calm or stirred-up I make the environment? And
either way, what is it that the noise level actually changes about the turnover, if anything?

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each suppresses the next
around the cycle (1→2→3→1). Three nodes, three directed links, and the links do NOT come in
matched forward/back pairs: the influence of population 1 on 2 is not the mirror of 2 on 1.
It does not reduce to one population plus an environment — the loop is the thing. Noise
enters each population. The SAME community/wiring throughout; only the environmental noise
level changes between the five runs.

**what_they_bring:**
Five observation windows of the SAME community, one per environmental-noise level, indexed
1→5 by noise in increasing order (level 1 = calmest, ~0.2× the baseline buffeting; level 3 =
the baseline; level 5 = stirred hardest, ~4× baseline). Each run is reduced to the standard
statistics in the community's two-dimensional turnover plane (the plane in which the
abundances trade off; the overall total is held aside): the autocorrelation C of the
turnover signal; its integrated step response chi; the two *directed* cross-correlations Cxy
and Cyx between the two turnover axes (how axis x now relates to axis y a lag tau later, and
vice versa); and the running tally of how far around the cycle the community has actually
swung — the mean cumulative turnover angle phiMean as a function of elapsed time, with its
spread phiVar across the run's sub-windows. No model parameters, no coupling strengths — just
the relative noise level they set and these measured curves from each run.

**data_path:**
`H:\mpa-conform\blockin\workspace\three_species_cycle_noise_sweep_v5.data.csv`
(columns: level, noise_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar. FIVE operating points —
the same community at five environmental-noise levels. level is the ordered noise index
(1=calmest…5=stirred-hardest); noise_rel is the relative buffeting amplitude they set,
normalized so the baseline run = 1.0×. tau is the community's own clock: a lag for the
two-point columns, an elapsed time for the turnover-angle columns.)

---
