# entry — community_pair_v6
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I monitor two separate small communities, each three populations interacting around a
loop (population 1 acts on 2, 2 acts on 3, 3 acts on 1). In both communities the
abundances never sit still — they swing and wiggle continuously over my whole
observation window, and honestly the two look pretty similar when I just watch the raw
traces. I set the two communities up under different interaction arrangements, but I
can't tell from the wiggles whether that actually produced any real difference in how
they behave. For EACH community I want to know: is the swinging a *genuine, persistent
turnover* — the community really going around its loop, over and over, never settling —
or is it just relaxing toward a steady balance with the environmental noise keeping it
jiggling around that balance? And the bottom line: are these two communities
fundamentally the SAME kind of system, or are they genuinely different in some way I
can't see by eye? Is either one unstable / near some edge, or are both basically
healthy?

**minimal_structure:**
Two communities, labeled 0 and 1 in the data. Each is three populations arranged in a
closed directed loop (1→2→3→1), each population influencing the next around the cycle,
with noise entering each population. Three nodes, three directed links per community. I
arranged the two communities' interactions differently when I built them, but what that
difference *does* — whether it changes the dynamics at all, and if so how — is exactly
what I'm asking you to read out. Don't assume the two are the same; don't assume they're
different.

**what_they_bring:**
For each community, one long observation window reduced to the standard statistics in
that community's two-dimensional turnover plane (the plane in which the three abundances
trade off against each other; the overall total is held aside). For each community they
bring everything one run yields in that plane: the autocorrelation C of the turnover
signal; its integrated step-response chi; the two *directed* cross-correlations Cxy and
Cyx between the two turnover axes (how axis x now relates to axis y a lag tau later, and
vice versa); and the running tally of how far around the cycle the community has actually
swung — the mean cumulative turnover angle phiMean as a function of elapsed time, with its
spread phiVar across the run's sub-windows. No model parameters, no coupling strengths, no
noise levels — just these measured curves, the same set for each of the two communities.

**data_path:**
`H:\mpa-conform\blockin\workspace\community_pair_v6.data.csv`
(columns: community, tau, C, chi, Cxy, Cyx, phiMean, phiVar. Two operating points — two
communities, one observation window each. community is 0 or 1; tau is each community's own
clock: a lag for the two-point columns, an elapsed time for the turnover-angle columns.)

---
