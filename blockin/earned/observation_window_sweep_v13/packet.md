# entry — observation_window_sweep_v13
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.
#
# STATUS: CORRECTED RE-RUN (2026-05-26). The first v13 oracle IMPOSED the FDT relation
# (chi = C0 - C analytically) -> the X=1 reading was tautological (Ron caught this). This
# version measures C and chi as TWO INDEPENDENT Monte-Carlo ensembles, so FDT/X=1 EMERGES
# (within MC noise) rather than being typed in. Researcher-voice packet unchanged; only the
# SEALED half updated. Re-posed + re-graded this session.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I have a single fluctuating signal — one scalar quantity wandering around its average. I measured how
it decorrelates from itself (its autocorrelation) and how it responds to a small steady push (its
integrated step-response), and here's the thing that's bugging me: the answer seems to depend on how
LONG I watch. I ran the measurement at 32 different observation durations — the same signal, the same
everything, just watched for longer and longer stretches (level 0 is the shortest watch, level 31 the
longest, the durations stepping up smoothly across about four decades). When I watch only briefly, the signal
drops part of the way down and then seems to FREEZE — it sits on a flat shelf and doesn't decorrelate
any further, as if part of it is permanently stuck. When I watch for a long time, that shelf isn't
there — the signal eventually decorrelates all the way down to zero. So I genuinely can't tell which
picture is real. Two things I need to know. **First:** does my signal have a genuinely STUCK /
frozen component — a part that truly never relaxes, so the system is permanently stuck partway — or is
the apparent freezing just an artifact of not having watched long enough (a slow part I'm
under-resolving in the short runs)? **Second:** if it's the watching-time, is there a "right"
observation duration that gives me the true picture — and is the signal, properly measured, in normal
balance (its response matched to its fluctuations) or is the stuck-looking part actually out of
balance?

**minimal_structure:**
One fluctuating signal (a single scalar). The signal and everything about it is IDENTICAL across the
32 runs — the ONLY thing that changes from level to level is the observation duration (how long I
watched / how far out in lag I could measure). Sampling within each run is equally fine; the runs
differ only in total length. Level 0 = shortest watch, level 31 = longest; the durations step up
smoothly across ~4 decades.

**what_they_bring:**
For each of the 32 observation durations, one run reduced to two standard curves of the signal: its
autocorrelation C (how a fluctuation stays correlated with itself a lag later) and its integrated
step-response chi (how much the signal shifts in response to a small steady push, accumulated over the
same lag). No model parameters, no timescales given — just these two measured curves at each of the
32 watch-lengths. Because the runs differ in length, the lag range covered differs across levels
(the longer watches reach to much longer lags).

**data_path:**
`H:\mpa-conform\blockin\workspace\observation_window_sweep_v13.data.csv`
(columns: level, window_rel, tau, C, chi. 32 operating points — the SAME signal watched for 32
durations. level is 0…31 (shortest→longest watch); window_rel is the relative observation-window
length, normalized so the shortest run = 1.0×. tau is the signal's own clock — a lag; its range
differs across levels because the longer watches reach further out.)

---
