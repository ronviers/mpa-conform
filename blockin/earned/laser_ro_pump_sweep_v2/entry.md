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
`data/laser_ro_pump_sweep_v2.frozen.csv`
(columns: curve, tau, C, chi. Each curve sits on its OWN settling window — the slow
near-threshold curve runs much longer in tau than the crisp middle ones.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** 1 (Vertex) — HYPOTHESIS, inherited from v1/v2 and unchanged by the move
(same substrate, single-mode structure, no edges). The pump sweep is a control axis,
NOT added structure — it does not create an edge or a loop. A single-mode trace at any
pump cannot carry edge shear or a circulating current; if the answerer reports either,
that is a structure mismatch (see KILL).

**intent:** I2 (camera-scale / migration along a control axis) — the FIRST I2 vertical.
v1 and the staged single-point v2 were I1 (place ONE point). The added vector here is
the **pump axis itself**: four operating points spanning the relaxation-oscillation
Q-band. Per meta-SOP §2 a multi-point question is prod intent; the human elected to
spend the owed sweep that PIPELINE.md §5 named to close the two-sided-headroom buckle.
This is the one added vector (the control axis), nothing more — still one substrate,
one channel-pair (C, chi), one structure.

**substrate:** our canonical class-B laser (G = kappa = 1, gamma_s = 0.10), at FOUR
pump ratios r (curve→r): 1→1.01, 2→1.04, 3→2.00, 4→12.00. Materialized by
`freeze_laser_ro_pump_sweep.py` from the laser's own linear NESS propagator
(mpa-central/library/ro_damping_audit.py, laser_conform_Q.py; mpa-legal Finding 5).
Data path is independent of conform. The CSV carries NO r/pump value — r = e^chit
would let a blind conform back out placement without fitting (data-path independence);
the researcher's order (low→high) is the only scale context in the packet.

**collapsed_axes:** the SWEEP is the added (uncollapsed) axis — four points along r.
Still FIXED: G, kappa, gamma_s, Lamb closure (no multimode, no memory), single mode
(0 edges). tau_obs is implicit per curve in its own sampling window; each curve runs
~8 e-foldings of its slowest mode (so the slow near-threshold curve spans far more tau
than the crisp middle ones). Declared + reversible: re-run the freeze at other r to add
points. WHY four: one BELOW the underdamped<->overdamped wall (overdamped, anchors the
sluggish wall), one JUST above it (the old v2 point), one AT the Q-peak (the sweet
spot), one PAST the peak (shows the roll-off — that more drive is not monotonically
better). Three points would show the peak; the fourth proves non-monotonicity on the
far side.

**kernel_window:** single mode → a circulating current is structurally impossible at
every pump. Each curve's window resolves its own settle (curve 1 overdamped: long slow
decay, no ring; curves 2–4 ring on 2*pi/omega_RO with envelope 1/gamma_RO). A
circulating-current reading on any curve is a detection artifact or a bug, not physics.

**answer_path (analytic — never via conform):**
Class-B Jacobian J = [[0, G n*], [-kappa, -(gamma_s + G n*)]], n* = gamma_s (r-1).
Eigenvalues give the RO observables directly (frame-invariant; never via conform). For
this laser gamma_RO = gamma_s*r/2, omega_0 = sqrt(kappa*gamma_s*(r-1)), and
Q = omega_RO/(2 gamma_RO) PEAKS EXACTLY at r = 2 (Q = 1.5); the underdamped band is
r in (r_crit = 1.026334, ~38.97); Q → 0 at BOTH walls (both over-damping). COMPUTED by
the freeze (`python freeze_laser_ro_pump_sweep.py`):

    curve  r      chit     gamma_RO  omega_RO  omega_0   Q       zeta_nat  overshoot  regime
    1      1.01   0.0100   0.0505    0.0000    0.0316    0.0000  1.5970    0.00%      OVERDAMPED (no ring; sluggish / critical-slowing wall, r→1)
    2      1.04   0.0392   0.0520    0.0360    0.0632    0.3462  0.8222    1.07%      just-underdamped (barely overshoots; near the wall)
    3      2.00   0.6931   0.1000    0.3000    0.3162    1.5000  0.3162    35.09%     Q-PEAK (crispest ring; the sweet spot)
    4     12.00   2.4849   0.6000    0.8602   1.0488     0.7169  0.5721    11.18%     past the peak (over-driven; Q more than halved)

So the migration is: curve 1 OVERDAMPED at the low-drive critical-slowing wall (Q=0,
omega_0 tiny) → curve 2 just-underdamped, barely overshoots → curve 3 the Q-PEAK
(crispest, Q=1.5) → curve 4 PAST the peak, Q rolled back to 0.72 — more than halved
(still rings, but the trend clearly reversed). Q is NON-MONOTONIC in r (mpa-legal Finding 5: the flowing
gamma_RO, not the frozen gamma_s/2): it rises off the low wall, peaks at r=2, and falls
again. Curve 3 (r=2, the sweet spot) is exactly where v1's single point landed
(ζ≈0.33, Q≈1.58) — the sweep anchors back to the earned v1 placement.

**cage_edges:**
- if_answerer_finds: "more drive (higher curve) => monotonically crisper / more
  stability margin" → route_to: 1 — the naive worry UNCORRECTED, the MISS this vertical
  targets. The data shows curve 4 LESS crisp than curve 3: Q is non-monotonic, peaks in
  the middle. Reading the sweep as monotonic-in-drive ignores the roll-off the fourth
  point exists to show.
  signature: "healthiest = highest drive / margin grows monotonically with pump"
- if_answerer_finds: "the sluggish low-drive curve (1/2) is near INSTABILITY / marginal
  / near blow-up" → route_to: 1 — the same wrong read v2 targeted. Near threshold the
  danger is critical SLOWING (over-damping), NOT oscillatory instability. A class-B
  laser above threshold is always stable; "barely ringing / sluggish" means APPROACHING
  the over-damping wall, the opposite of marginal-toward-blow-up.
  signature: "sluggish/low-overshoot read as near-instability / near-blow-up"
- if_answerer_finds: "circulating current / a loop signature in a single-mode trace at
  any pump" → route_to: null (KILL) — 0 edges; impossible. (Complex eigen-pairs of the
  single-mode Jacobian are the ring-down, not a loop current.)

**sealed_answer:**

TARGET
  migration:        curve 1 overdamped at the low-drive over-damping / critical-slowing
                    wall (sluggish, no ring) → curve 2 just-underdamped (barely
                    overshoots, near that wall) → curve 3 the SWEET SPOT (crispest ring,
                    the peak of the response quality) → curve 4 PAST the peak (still
                    rings, but the response quality has started to fall again).
  sweet_spot:       curve 3 — the response is healthiest in the MIDDLE of the pump
                    range, not at the top.
  nominal_verdict:  ALL FOUR are nominal/stable (no instability anywhere — a class-B
                    laser above threshold is always stable). The "edge" the researcher
                    senses at the low end is the over-damping / critical-slowing wall,
                    NOT an instability edge.
  two-sided headroom (NOW GROUNDABLE — the v1 gap closed by the sweep):
                    from the low end, the near wall is the over-damping / critical-
                    slowing wall (toward less drive, r→1); the HEALTHY direction is MORE
                    drive, toward the middle peak. But MORE drive is NOT monotonically
                    better: past the peak (curve 4) the response quality rolls back off.
                    So the room is bounded on BOTH sides and the optimum is interior —
                    the correction to "more drive = more margin."

MATCH
  The answerer reads the four curves as a migration, identifies curve 3 (the middle) as
  the crispest / healthiest, and reports that the response quality is NON-MONOTONIC in
  pump — rising off a sluggish low-drive wall, peaking in the middle, and falling again
  by curve 4. It corrects the naive worry: driving harder is healthy only UP TO the
  sweet spot; past it you lose crispness, you do not keep gaining margin. It places the
  low curves near the OVER-DAMPING wall (not instability). It need NOT say "Q" or
  "zeta": a researcher-facing "your response is best in the middle of your pump range,
  not at the top — down low you're near the point where it stops ringing and goes
  sluggish, up high you've gone past the snappiest point and it's softening again" is a
  MATCH.

MISS
  Reports the response as MONOTONICALLY crisper / more-margin with more drive (misses
  the curve-4 roll-off; the naive worry uncorrected — cage_edge 1); OR calls the
  sluggish low curves marginal / near-instability / near blow-up (cage_edge 2); OR
  fails to identify an interior sweet spot at all (reads the sweep as a single trend).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. zeta (either convention) or the response-quality measure attains EXACTLY 0 or ∞ at
     a finite curve (boundaries are asymptotic-only; NaN tripwire — a NaN here is the
     §Asymptotic-closure falsifier, never fallback-filled). NOTE: curve 1 is genuinely
     overdamped, so its DAMPED ring frequency is 0 by construction — that is the
     over-damped regime, not a boundary attained at finite drive; the falsifier is a
     0/∞ in zeta_nat or the natural frequency, which stay finite and nonzero here.
  2. a circulating-current / loop signature reported for a single-mode trace at any pump.
  3. any curve read as genuinely unstable (growing): a class-B laser above threshold is
     always stable — instability here means the freeze or the reading is broken.

**what this vertical tests (ledger residue seed):** does the headroom readout close
the TWO-SIDED gap once the data actually spans the band — can conform take a researcher
sweep (no framework terms, just "low to high drive") and (a) place each curve, (b) read
the NON-MONOTONIC response-quality band off the migration, (c) name the interior sweet
spot and correct "more drive = more margin," and (d) keep naming the low-drive wall as
over-damping (not instability)? A read that says "crisper all the way up" is the MISS;
a read that finds the middle sweet spot and bounds the room on both sides is the win —
and it is the v1 not_grounded[] item (two-sided headroom) finally grounded by data.
