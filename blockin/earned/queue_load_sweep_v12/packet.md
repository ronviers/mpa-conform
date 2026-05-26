# entry — queue_load_sweep_v12
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
I run a single-server queue — jobs arrive, wait in line, get served one at a time. I can dial the
LOAD on it: how heavily it's used, i.e. how close the arrival rate is to what the server can handle.
I measured the queue at five increasing loads, from comfortably loaded up to running very near its
capacity (level 0 = lightest load, level 4 = heaviest, closest to the limit). As I push the load up
toward the limit, two things happen and they worry me: the queue length takes much LONGER to settle
back after a wander (the fluctuations get very slow), and the queue length swings get much LARGER
(the line size becomes wildly variable). Here's what I can't tell from the raw curves: is the queue,
near its capacity limit, still a well-behaved system that's merely SLOW and noisy — its response to a
small extra push still in proportion to its own natural fluctuations, the way a normal system in
balance behaves — or has it tipped into some kind of STUCK / pathological state where its response
no longer keeps up with its fluctuations (so that the system has, in effect, fallen out of balance)?
So for each load I want to know: is the response still matched to the fluctuations (in balance), or
has it fallen out of balance? And the practical one: as I push toward the capacity limit, am I just
getting slower-and-noisier-but-fine, or am I approaching a genuine breakdown — and how close to the
limit am I?

**minimal_structure:**
One queue (one fluctuating quantity — the queue length, a single scalar), measured at five increasing
loads. The only thing that changes from level to level is the load (how close to capacity); the queue
and the measurement are otherwise the same. Each load was watched long enough for its own slow
settling to (mostly) play out — so the observation windows differ in length across levels, the
heavily-loaded ones much longer than the lightly-loaded ones (deliberate: near the limit the queue
settles far more slowly).

**what_they_bring:**
For each of the five loads, one measurement window reduced to two standard curves of the queue length:
its autocorrelation C (how a fluctuation in the line length stays correlated with itself a lag later)
and its integrated step-response chi (how much the queue length shifts in response to a small steady
bump in the load, accumulated over the same lag). No load values, no rates, no model parameters — just
these two measured curves, the same pair at each of the five loads.

**data_path:**
`H:\mpa-conform\blockin\workspace\queue_load_sweep_v12.data.csv`
(columns: level, util_rel, tau, C, chi. Five operating points — one queue at five loads. level is
0…4 (lightest→heaviest, toward the capacity limit); util_rel is the relative load they set, normalized
so the lightest run = 1.0×. tau is the queue's own clock — a lag. Each level has its own settling
window, so tau ranges differ across levels, the heavily-loaded ones reaching to much longer lags.)

---
