# entry — laser_ro_nominal_v1
# Hand-authored (first vertical; the voice is learned by writing, not templated).
# SEALED below the line. The answerer-session sees only the BLIND PACKET.

---

## BLIND PACKET  (all the answerer-session may see)

**question:**
When I nudge my laser's drive a little around its operating point, the output
overshoots and rings down before it settles. Is that ring-down nominal — or is my
damping marginal, closer to instability than it should be?

**minimal_structure:**
One driven, damped mode exchanging energy with a single reservoir — one thing and
its bath. No second oscillator, no loop.

**what_they_bring:**
One settling curve at one bias — the output's autocorrelation and its integrated
response after a small step.

**data_path:**
`data/laser_ro_nominal_v1.frozen.csv`

---

## SEALED  (author + unseal step only — NEVER in the packet)

**category:** 1 (Vertex) — HYPOTHESIS. A single-mode trace cannot carry edge shear
or a circulating current; if the answerer reports either, that is a structure
mismatch (see KILL).

**substrate:** our canonical class-B laser (G = kappa = 1, gamma_s = 0.10), ONE
operating point r = 2 (chit = ln2). Materialized by `freeze_laser_ro.py` from the
laser's own linear NESS propagator (mpa-central/library/ro_damping_audit.py,
laser_conform_Q.py; mpa-legal Finding 5). Data path is independent of conform.

**collapsed_axes:** SINGLE operating point — the researcher has one laser at one
bias, no sweep. FIXED: G, kappa, gamma_s, Lamb closure (no multimode, no memory).
tau_obs is implicit in the sampling window (~6 RO periods; envelope ~1/gamma_RO).
Declared + reversible: re-run the freeze at other r to add points later. WHY: we
test the amplitude face at one point; the sign-topological face is absent by
construction (0 edges).

**kernel_window:** single mode -> k_frust is structurally impossible. The window
spans ~6 RO periods (period 2*pi/omega_RO ~ 21) and resolves the ring-down; the
envelope decays on ~1/gamma_RO ~ 10. A circulating-current reading here is a
detection artifact or a bug, not physics.

**answer_path (analytic — never via conform):**
Class-B Jacobian J = [[0, G n*], [-kappa, -(gamma_s + G n*)]], n* = gamma_s (r-1).
Eigenvalues give gamma_RO = (gamma_s/2) e^chit, omega_RO = sqrt(det - gamma_RO^2),
det = kappa gamma_s (r-1), Q = omega_RO / (2 gamma_RO). At r = 2:
gamma_RO = 0.10, omega_RO = 0.30, Q = 1.50, zeta = 0.333 (underdamped).
Q is NON-MONOTONIC in chit, peaks at r = 2, and -> 0 at BOTH ends (mpa-legal
Finding 5: the legal flowing gamma_RO, not the frozen gamma_s/2). So this point
sits at the healthiest damping — the top of the underdamped ringing band — with
overdamped walls on both sides: critical slowing as r -> 1 (chit -> 0+, the
s-threshold) and RO damping out deep in c (large r).

**cage_edges:**
- if_answerer_finds: "more ringing => closer to instability, or Q growing without
  bound deep in c"  -> route_to: 1  -- the frozen-gamma_RO monotonic artifact.
  Legal Q is bounded and non-monotonic; the ring-down band is healthy interior,
  not an instability ramp.  signature: "Q monotonic-increasing in recovered chit"
- if_answerer_finds: "circulating current / complex spectrum with no drive, in a
  single-mode trace"  -> route_to: null (KILL)  -- 0 edges; impossible.

**sealed_answer:**

TARGET
  placement:        underdamped RO band, at/near the Q-peak (chit ~ ln2 ~ 0.69),
                    zeta ~ 0.33, Q ~ 1.5
  nominal_verdict:  NOMINAL — healthiest damping; the ring-down is expected, not marginal
  headroom:         room BOTH ways before it goes sluggish — toward the s-threshold
                    (r -> 1, critical slowing) and deep into c (RO damps out). Both
                    walls are over-damping, NOT blow-up.

MATCH
  The answerer reads the curve as a stable, damped ring-down (underdamped but well
  inside stability), places it in the healthy band, and reports nominal with
  two-sided headroom. It need NOT say "chit" or "Q": a researcher-facing "your
  ring-down is healthy, with margin before it gets sluggish either way" is a match.

MISS
  Calls the ring-down marginal / near-instability (treats more ringing as nearer
  blow-up); OR reads "more margin the deeper you drive" (the frozen-gamma_RO
  artifact); OR places it overdamped.

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. Q or zeta attains EXACTLY 0 at this finite operating point (boundaries are
     asymptotic-only; NaN tripwire).
  2. a circulating-current / k_frust signature is reported for a single-mode trace.
  3. the trace is read as genuinely unstable (growing): a class-B laser above
     threshold is always stable — instability here means the freeze or the reading
     is broken.

**what this vertical tests (ledger residue seed):** can conform take ONE
researcher-voiced settling curve, with zero framework terms in the question, and
return the correct nominal verdict + two-sided headroom? I.e. does researcher-voice
blinding hold, and can conform place a single point on the (sealed) Q-band map?
