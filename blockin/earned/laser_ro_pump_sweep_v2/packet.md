# entry — laser_ro_pump_sweep_v2
# Hand-authored by the orchestrator (non-blind; holds the seal). The blind ANSWERER
# is a separate fresh context that sees ONLY the BLIND PACKET below — so author !=
# answerer is preserved. Everything above "## SEALED" is emitted to the answerer by
# pose.py; keep it researcher-voice with zero framework framing. SEALED below the line.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
I characterized my laser across its whole useful pump range — four settling curves,
from only just over the point where it starts lasing (curve 1) up to driven good and
hard (curve 4). Down at the bottom the output sags back slowly and barely overshoots,
sluggish. In the middle it snaps back with a clean, crisp ring. Up at the top it still
rings, but honestly it looks a touch less crisp than the middle did. I'd always just
assumed "more drive = snappier response, more stability margin," so I'd run it hard.
Across these four, where is my response actually at its healthiest, and which way is
the room — am I really buying margin by cranking the drive up, or is there a sweet
spot I'm driving past?

**minimal_structure:**
One driven, damped mode exchanging energy with a single reservoir — one thing and its
bath. No second oscillator, no loop. The same device throughout; only the pump changes
between the four curves.

**what_they_bring:**
Four settling curves, indexed 1→4 by pump in increasing order (curve 1 = barely
lasing; curve 4 = driven hard). For each: the output's autocorrelation C and its
integrated step response chi, each sampled out to where that curve has settled. No
absolute pump numbers — just the order, low to high.

**data_path:**
`H:\mpa-conform\blockin\workspace\laser_ro_pump_sweep_v2.data.csv`
(columns: curve, tau, C, chi. Each curve sits on its OWN settling window — the slow
near-threshold curve runs much longer in tau than the crisp middle ones.)

---
