# entry — magnet_temp_sweep_v8
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I work on a magnetic material, and I've been mapping how its magnetization fluctuations
relax as I change its temperature. I took five temperatures, stepping from below a particular
middle temperature, right through it, to above it (levels 0 through 4 — level 0 is the
coolest, level 4 the warmest, and level 2 is that special middle temperature). Here's the
thing that has me worried: away from that middle temperature — whether cooler or warmer — the
fluctuations are small and die away quickly. But as I approach the middle temperature they
swell up enormously and take far, far longer to settle. Right *at* that middle temperature
they're huge and crawl back so slowly I can barely watch them finish. So: at that special
middle temperature where everything goes big and sluggish, has my material fallen *out of
equilibrium* — gone glassy, frozen, "aging" on me, the kind of thing that won't come back to
thermal balance? Or is it still just relaxing the ordinary way, only much more slowly? For
each temperature I want to know — is it still a normal settling-back-to-balance, or has it
turned into something else? And the big one: is the cool side a fundamentally *different kind*
of dynamical behaviour from the warm side — two different sorts of system either side of that
middle — or is it the *same kind* of relaxation all the way through, just with that slow-down
in the middle?

**minimal_structure:**
One material; one fluctuating quantity in it (a single scalar — the magnetization
fluctuation), observed at five temperatures that straddle a special middle temperature
(level 0 = coolest … level 2 = the special middle … level 4 = warmest). The only thing that
changes from level to level is the temperature; the material and the measurement are otherwise
the same. Each temperature was watched long enough for its own relaxation to play out — so the
observation windows differ in length across levels (the middle one needs the longest watching,
deliberately).

**what_they_bring:**
For each of the five temperatures, one measurement window reduced to two standard curves of
the fluctuating quantity: its autocorrelation C (how the fluctuation at one moment stays
correlated with itself a lag later) and its integrated step-response chi (how much the
quantity shifts in response to a small steady push, accumulated over the same lag). No
temperature values, no model parameters, no material constants — just these two measured
curves, the same pair at each of the five settings.

**data_path:**
`H:\mpa-conform\blockin\workspace\magnet_temp_sweep_v8.data.csv`
(columns: level, tau, C, chi. Five operating points — one material at five temperatures.
level is 0…4 (coolest→warmest; level 2 is the special middle temperature); tau is the
material's own clock — a lag. Each level has its own settling window, so tau ranges differ
across levels.)

---
