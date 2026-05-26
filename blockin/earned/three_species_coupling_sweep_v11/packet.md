# entry — three_species_coupling_sweep_v11
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.
#
# STATUS: STAGED, NOT YET POSED. Freeze built + run; seal freeze-computed. Awaiting
# Ron's human-glance of the answer key before the blind pass (meta-SOP §2 safeguard).

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
This is another follow-up on that three-population community — three populations locked in a
cyclic standoff (the first outcompetes the second, the second the third, the third the first),
which keeps cycling and never settles. Earlier I established that calming the environment down
doesn't slow the cycling — the turnover keeps going at the same rate however calm or stirred-up
I make things. So the noise isn't what drives the loop. That leaves the obvious next question:
what IS setting the turnover rate? My suspicion is the *strength of the interactions themselves*
— how hard each population presses on the next around the cycle. So this time I held the
environment fixed (same noise throughout) and instead dialed the interaction strength: five
runs of the SAME three-population loop, from a quarter of my baseline coupling up to four times
it (baseline is the middle run). For each I reduced the run to the same statistics. My question:
as I strengthen the cyclic interaction, does the community cycle FASTER — does the turnover rate
TRACK the interaction strength — or does the rate stay put while only something else changes (or
does the loop behave some third way)? And at the weak-coupling end, is there still a genuine
directed cycle, or does it stop being a loop? I want to know what the turnover rate is actually
set by.

**minimal_structure:**
Three interacting populations arranged in a closed directed loop — each suppresses the next
around the cycle (1→2→3→1). Three nodes, three directed links, and the links do NOT come in
matched forward/back pairs: the influence of population 1 on 2 is not the mirror of 2 on 1. It
does not reduce to one population plus an environment — the loop is the thing. The SAME community
wiring TOPOLOGY and the SAME environmental noise throughout; only the STRENGTH of the cyclic
interaction changes between the five runs.

**what_they_bring:**
Five observation windows of the SAME community, one per interaction-strength level, indexed 1→5
by coupling in increasing order (level 1 = weakest, ~0.25× the baseline interaction; level 3 =
the baseline; level 5 = strongest, ~4× baseline). Each run is reduced to the standard statistics
in the community's two-dimensional turnover plane (the plane in which the abundances trade off;
the overall total is held aside): the autocorrelation C of the turnover signal; its integrated
step response chi; the two *directed* cross-correlations Cxy and Cyx between the two turnover axes
(how axis x now relates to axis y a lag tau later, and vice versa); and the running tally of how
far around the cycle the community has actually swung — the mean cumulative turnover angle phiMean
as a function of elapsed time, with its spread phiVar across the run's sub-windows. No model
parameters, no coupling values — just the relative interaction strength they set and these measured
curves from each run. Each run was watched on the community's own clock (a slower loop watched
longer), so the lag/time ranges differ across the five.

**data_path:**
`H:\mpa-conform\blockin\workspace\three_species_coupling_sweep_v11.data.csv`
(columns: level, coupling_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar. FIVE operating points —
the same community at five cyclic-interaction strengths. level is the ordered coupling index
(1=weakest…5=strongest); coupling_rel is the relative interaction strength they set, normalized so
the baseline run = 1.0×. tau is the community's own clock: a lag for the two-point columns, an
elapsed time for the turnover-angle columns.)

---
