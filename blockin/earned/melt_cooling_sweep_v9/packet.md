# entry — melt_cooling_sweep_v9
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.
#
# STATUS: STAGED, NOT YET POSED. Freeze built + run; seal freeze-computed and
# human-glanced (Ron, 2026-05-25). Next session: §0 reconcile, re-glance, pose, run the
# blind pass. Registered in PENDING.md as expected-float.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I work on a material that flows like a (very viscous) liquid when it's warm but stiffens up
into a solid-ish state when I cool it — it doesn't crystallize, it just gradually stops
flowing. I've measured how its internal fluctuations relax at five temperatures, stepping
from warm down to cold (levels 0 through 4; level 0 is the warmest, level 4 the coldest).
When it's warm the fluctuations relax cleanly and completely. As I cool it they get a lot
slower, and a two-stage character appears: a quick partial drop, then a long slow crawl the
rest of the way down. At the coldest settings that slow crawl takes so long I'm not sure it
ever actually finishes inside my measurement. Here's what worries me: when a material gets
this sluggish on cooling, it can stop being a normal warm liquid that's just slow, and instead
fall *out of thermal equilibrium* — get stuck, "age," stop properly relaxing back to balance,
so that its response to a push no longer matches its own fluctuations the way an
equilibrium material's does. So for each temperature I want to know: is this still an ordinary
liquid that's merely slow (still in thermal balance), or has it genuinely fallen out of
equilibrium and started aging? If it's somewhere in between, *how far* out of balance is it?
And the big one: as I cool from warm to cold, does the change from "ordinary liquid" to "stuck
/ aging" happen ABRUPTLY at one particular temperature — a sharp switch — or GRADUALLY across
a range, with the middle temperatures sitting partway between the two?

**minimal_structure:**
One material; one fluctuating quantity in it (a single scalar), observed at five temperatures
as it is cooled from warm (level 0) to cold (level 4). The only thing that changes from level
to level is the temperature; the material and the measurement are otherwise the same. Each
temperature was watched long enough for its own slow relaxation to (mostly) play out — so the
observation windows differ in length across levels, the cold ones much longer than the warm
ones (deliberate: the cold settings relax far more slowly).

**what_they_bring:**
For each of the five temperatures, one measurement window reduced to two standard curves of
the fluctuating quantity: its autocorrelation C (how the fluctuation stays correlated with
itself a lag later) and its integrated step-response chi (how much the quantity shifts in
response to a small steady push, accumulated over the same lag). No temperature values, no
model parameters, no material constants — just these two measured curves, the same pair at
each of the five settings.

**data_path:**
`H:\mpa-conform\blockin\workspace\melt_cooling_sweep_v9.data.csv`
(columns: level, tau, C, chi. Five operating points — one material at five temperatures.
level is 0…4 (warmest→coldest); tau is the material's own clock — a lag. Each level has its
own settling window, so tau ranges differ across levels, the cold ones reaching to much
longer lags.)

---
