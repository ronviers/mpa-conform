# entry — glass_two_step_v4
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I study a disordered material — a supercooled liquid as it approaches structural
arrest. I track one slow structural observable and measure two things about it: its
autocorrelation C (how a fluctuation now persists into a fluctuation a time later) and
its susceptibility chi (how that same observable responds to a small steady applied
field). When I watch C relax, it does NOT come down in one smooth step. It drops quickly
partway, then hangs on a long shoulder for a stretch, and only much later does it
slowly, raggedly finish relaxing the rest of the way — and that final decay is not a
clean exponential, it's drawn-out and stretched. Here is what I cannot tell from the
relaxation curve alone: is my material simply EQUILIBRATED but slow — an ordinary
thermal state that just takes a long time to forget itself — or is it OUT of equilibrium,
with the slow, stuck part of it effectively running "hotter" than the fast part that
relaxes promptly? Those two look the same in the decay curve C by itself. And
practically: is this material sitting in a stable settled state, or is that long stuck
shoulder a sign it is near an arrest it is about to cross?

**minimal_structure:**
A single relaxing structural observable in a disordered medium, with a SEPARATION of
timescales: a population of fast degrees of freedom that relax promptly, and a population
of slow degrees of freedom that are nearly frozen and relax only over a much longer (and
stretched, non-exponential) timescale. It is not one clean relaxation time — it is two
well-separated populations, fast and slow, sharing the one observable. The researcher can
push the observable with a small steady field and watch the integrated response.

**what_they_bring:**
One long observation on a single sample held at a fixed preparation/waiting condition,
reduced to the two standard curves over the material's own lag time: the normalized
autocorrelation C(tau) of the slow observable (C(0)=1), and the integrated step-response
/ susceptibility chi(tau) to a small field conjugate to that observable. That is the
complete content of the one measurement — both curves over the full lag range, from
inside the fast relaxation out past the slow stretched tail. No mode decomposition, no
model parameters, no temperatures — just the measured C and chi.

**data_path:**
`H:\mpa-conform\blockin\workspace\glass_two_step_v4.data.csv`
(columns: tau, C, chi. One operating point — one sample, one preparation/waiting
condition. tau is the material's own lag time. C is the normalized autocorrelation
(C(0)=1); chi is the integrated step-response to a small applied field.)

---
