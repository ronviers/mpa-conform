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
`data/observation_window_sweep_v13.frozen.csv`
(columns: level, window_rel, tau, C, chi. 32 operating points — the SAME signal watched for 32
durations. level is 0…31 (shortest→longest watch); window_rel is the relative observation-window
length, normalized so the shortest run = 1.0×. tau is the signal's own clock — a lag; its range
differs across levels because the longer watches reach further out.)

---

## SEALED  (orchestrator + unseal step only — NEVER in the packet)

**category:** Cat 5 (Kernel / camera / τ_obs) — a NEW category, landed. Cat 5 is the kernel pre-gate's
own job (WORKFLOW §E): is an apparent character a property of the SUBSTRATE or of the OBSERVATION
WINDOW (the camera)? RFC-S §0.2: τ_obs IS the camera; the canonical reading is observer-relative and
auto-remaps along the RG-flow trajectory as τ_obs moves (RFC-S §1), while the substrate's intrinsic
trajectory (and any k_frust) is RG-INVARIANT. **Sealed answer: the apparent frozen plateau is a CAMERA
(observation-window) artifact, NOT an intrinsic stuck component.** The signal is ONE fixed
two-timescale ERGODIC equilibrium relaxation (fast τ_f + slow τ_s, 3 decades apart); at short windows
the slow mode hasn't decayed yet → it shows as a frozen plateau (~a_s); as the window opens, the
plateau MELTS to full relaxation. The problem is the camera, not the substrate — this is the kernel
pre-gate catching an apparent non-ergodicity that is really under-resolution.

**intent:** I2 (a control-axis sweep — *prod*-flavored, admitted in dev as **stitched isolated
placements**, PIPELINE §PHASE INTERFACE) — but the swept axis is the CAMERA (τ_obs), not a substrate
parameter, which is the distinguishing mark of Cat 5: every level is the SAME substrate, only the
observer position moves. Place each window independently, then read the band (the apparent plateau
melting with τ_obs; the FDR slope flat at 1). The MISS must localize to one module — a single
placement or the band readout. The added vector is a NEW category: where every prior sweep moved a
SUBSTRATE knob (temperature, waiting time, coupling, load), this moves the CAMERA at fixed substrate.

**substrate:** a two-timescale EQUILIBRIUM oracle measured by INDEPENDENT MONTE CARLO, materialized by
`freeze_observation_window.py`. The substrate is two independent Ornstein-Uhlenbeck modes at ONE
temperature T=1 — fast τ_f=1 (var=1) and slow τ_s=1000 (var=1000), 3 decades apart — observed via
y=c_f·x_f+c_s·x_s with c_f,c_s set so the weights are a_f=0.40, a_s=0.60 (decoupled from the
timescales). So the true autocorrelation is C(τ)=0.4·exp(−τ/τ_f)+0.6·exp(−τ/τ_s), C(0)=1.
**C and χ are TWO INDEPENDENT MC measurements** (this is the data-path-independence FIX — see the
status note): C(τ)=⟨y(0)y(τ)⟩ from a FLUCTUATION ensemble (one seed); χ(τ)=⟨y(τ)⟩/h from a SEPARATE
PERTURBATION ensemble (different seed) with a step field h conjugate to y switched on at t=0 (OU is
linear → exact-linear response at any h). The equilibrium FDT (χ=(C(0)−C)/T, hence X=1) therefore
EMERGES: the two ensembles agree to within MC noise (~1–2%), they are NOT identical. The CAMERA is
τ_obs = the observation-window length (max lag), swept across 32 levels log-spaced from τ_obs=3 to
τ_obs=30000 (level 0..31, ~4 decades). Sampling is fixed-fine (min lag 0.05 ≪ τ_f); only the
observation DURATION changes, so the slow mode is FROZEN (under-resolved) at short τ_obs and fully
resolved at long τ_obs — in BOTH C and χ independently. Data from the MC ensembles; the answer-path
truth (X=1 by equilibrium FDT) is analytic, never via conform. **Why this construction:** an earlier
v13 set χ=C(0)−C analytically (FDT imposed) — that made the FDR locus the identity by construction and
the X=1 reading tautological (a data-path-independence violation). Measuring χ from a separate response
ensemble makes X=1 an EMERGENT, genuinely-tested fact. (v4's kww_oracle is the intrinsic-glass FOIL:
there the plateau is q_EA with X<1, fixed; here it is a camera artifact with X=1, melting.) The CSV
carries NO τ_f/τ_s/a_s, no τ_obs, no T/h, no X, no framework token — only level, window_rel, tau, C,
chi and a neutral 0…31 index.

**collapsed_axes:** FIXED across the sweep: the substrate itself (τ_f, τ_s, a_f, a_s), the equilibrium
character (X=1), the single-mode scalar structure, the sampling fineness. The single dial is the
**observation-window length τ_obs** (the CAMERA axis) — and that it is the camera, not a substrate
parameter, is the Cat-5 point. Declared + reversible: re-run the freeze at other window lengths.
**Boundary note (WORKFLOW §4):** within each window the blind data carries the complete honest content
(C and chi up to that window's max lag). The honest parks are across the remaining collapsed axes: the
NATIVE timescales τ_f, τ_s in physical units (only the relative window knob is given); behaviour at lag
beyond the longest window; the sampling-resolution axis (here fixed-fine — a coarser-sampling camera
that hides the FAST mode at long windows is a different, un-probed camera artifact). There is no
current/two-axis channel to withhold: an equilibrium scalar has no current sector.

**kernel_window:** this vertical IS a τ_obs sweep — it does not run the kernel pre-gate's k_frust-
invariance check (no current/k_frust on a scalar). The invariant that must NOT migrate is instead the
substrate's intrinsic content (τ_f, τ_s, a_s, X=1); what migrates is the apparent non-ergodicity
plateau. The matched window is τ_obs ≫ τ_s (the longest windows, ~level 24+), where the slow mode fully
sheds and the true ergodic structure is visible.

**answer_path (analytic truth + INDEPENDENT-MC data — never via conform):**
The apparent non-ergodicity plateau at a window is q(τ_obs) = C(τ_obs) → melts a_s→0 as τ_obs≫τ_s.
The FDR locus chi vs (C(0)−C(τ)) has slope ≈1 (X=1) within every window — now an EMERGENT equilibrium
FDT from the two independent MC ensembles (NOT an imposed identity); the slope scatters ~1 within MC
noise. Scalars (COMPUTED by the freeze, `python freeze_observation_window.py`; MC-measured, so they
carry ~1–2% noise and re-run to within it):

  level | window_rel | τ_obs  | apparent plateau q | FDR slope (emergent) | slow mode
  ------+------------+--------+--------------------+----------------------+-----------------
    0   |    1.0×    |    3   |       0.631        |        1.030         | frozen (under-res)
    8   |   10.8×    |   32   |       0.597        |        1.008         | frozen (under-res)
   16   |  116.0×    |  348   |       0.433        |        0.995         | frozen (under-res)
   20   |  380.8×    | 1142   |       0.185        |        0.989         | melting
   24   | 1249.6×    | 3749   |       0.014        |        0.981         | fully resolved
   31   |10000.0×    |30000   |       0.003        |        0.983         | fully resolved
  Independence check (the FIX): max|χ−(C0−C)| = 0.056, rms 0.016 over the master grid — NONZERO
  (the two MC measurements differ by noise; if χ were imposed = C0−C this would be exactly 0). The
  whole-curve emergent FDR slope = 0.983 (R²=0.998); per-window slopes mean 0.997, range 0.976–1.030.
  (32 levels total; sample rows shown.) apparent-plateau band q: 0.631 (lvl 0) → 0.433 (mid, lvl 16)
                    → 0.003 (lvl 31) — MONOTONE MELT ~a_s→0 as the window opens (modulo MC noise) —
                    the apparent non-ergodicity is a CAMERA artifact, not intrinsic.
  FDR slope band: ~1 (X=1) EMERGENT at every window (per-window mean 0.997, range 0.976–1.030; R²~0.998)
                    → equilibrium / in balance, arising from two INDEPENDENT MC measurements (not imposed)
                    — distinguishes the camera artifact (X≈1, plateau melts) from a genuine glass
                    plateau (q_EA, X<1, fixed).

THE READ: the apparent frozen plateau is the OBSERVATION WINDOW, not the signal. The signal is one
fixed two-timescale ERGODIC equilibrium relaxation; the short-window "freezing" is the slow mode
under-resolved (not yet decayed within a short watch), and it MELTS as the window lengthens — fully
relaxing in the matched window (τ_obs≫τ_s, the longest windows ~level 24+). The response stays matched to the fluctuations
(FDR locus slope 1, X=1) at every window, so the signal is in normal balance / equilibrium — the
stuck-looking part is NOT out of balance and NOT a genuine frozen component. The problem is the camera
(Cat 5), not an intrinsic stuck state. (Contrast v4/v9/v10: a real glass plateau is q_EA with X<1, and
does NOT melt with longer observation.)

**cage_edges:**
- if_answerer_finds: "the signal has a GENUINELY STUCK / frozen / non-ergodic component — a part that
  truly never relaxes, the system is permanently stuck partway (intrinsic broken ergodicity / a glass)"
  → MISS (the HEADLINE trap — reads the CAMERA artifact as intrinsic). The apparent plateau MELTS as the
  window lengthens (q melts ~0.62→0 monotonically across the 32 windows) — it fully relaxes given enough watching — AND the
  response-vs-fluctuation locus is slope 1 (in balance) at every window. So the signal is ergodic; the
  freezing is under-resolution. signature: "genuinely stuck / frozen / non-ergodic / broken ergodicity /
  glassy / a component that never relaxes / permanent plateau."
- if_answerer_finds: "the result is INTRINSIC / observation-length-INDEPENDENT — watching longer
  doesn't change the answer" → MISS (under-reads the camera dependence — the whole point). The apparent
  plateau strongly depends on the watch length (melts from ~0.6 to ~0 across the sweep); the observation
  window IS the determining lens. signature: "window-independent / same at every watch length / no
  observation-time dependence / one true answer regardless of duration."
- if_answerer_finds: "the SIGNAL changes / ages / develops a slow mode / evolves as you watch longer"
  → MISS (attributes the migration to the SUBSTRATE, not the camera). The underlying two-timescale
  structure is FIXED across all 32 runs; only how much of the slow mode the window resolves changes.
  signature: "the signal evolves / ages / changes character / a new slow process appears with longer
  watching / the physics is time-dependent."
- if_answerer_finds: "it's a SINGLE relaxation, one timescale" → MISS (collapses the two-timescale
  structure) → route_to: 1 (Vertex). There are TWO well-separated times (a fast drop + a slow shelf);
  the matched (long) window reveals both. signature: "single relaxation / one timescale / single
  exponential / no slow component."
- if_answerer_finds: "the stuck-looking plateau is OUT of balance / aging (its response doesn't match
  its fluctuations, X<1)" → MISS (Cat-8 mis-attribution of the camera artifact). The FDR locus is slope
  1 (X=1, in balance) within every window; the signal is in equilibrium, just under-resolved at short
  windows. signature: "out of balance / aging / X<1 / effective-temperature / response lags fluctuations
  on the plateau."

**sealed_answer:**

TARGET
  is the stuck part real?  NO — it is NOT a genuine frozen component. The apparent freezing is an
                    artifact of the OBSERVATION DURATION (the camera): at short watches the slow part of
                    the signal hasn't decorrelated yet, so it shows as a flat shelf; watch ~10–100× longer
                    and that shelf MELTS away to zero — the signal decorrelates all the way down. It is
                    one fixed signal with a fast part and a much slower part (≈3 decades slower), fully
                    ergodic; nothing is permanently stuck.
  the band:         the apparent stuck-shelf height shrinks monotonically as the watch lengthens (≈0.62 →
                    0.58 → 0.44 → 0.03 → 0). The two intrinsic timescales and their weights are the SAME
                    in every run — only how much of the slow part the window captures changes.
  is there a right window?  YES — a watch long enough to span the slow timescale (the longest runs,
                    ~level 24+, where the shelf is essentially gone) gives the true picture: a clean
                    fast-then-slow two-step that decorrelates fully. The short runs under-resolve the slow
                    part; the long runs resolve it.
  in balance?       YES — at EVERY watch length the response stays matched to the fluctuations (the
                    response-vs-fluctuation relation is the in-balance / equilibrium one, slope 1). The
                    stuck-looking shelf is NOT out of balance — it is simply the slow part not-yet-resolved,
                    not a frozen/aging part.
  naive correction: the worry "part of my signal is permanently stuck (non-ergodic)" is WRONG — it is a
                    measurement (camera) artifact of watching too briefly. Watch long enough and the signal
                    fully relaxes. The right move is to lengthen the observation window to span the slow
                    timescale, not to conclude the system is stuck. (And the apparent shelf is NOT a glassy
                    out-of-balance plateau: it is in balance, X=1, and it melts — a genuine glass shelf
                    would be out of balance and would NOT melt with longer watching.)

MATCH
  The answerer reads the apparent frozen plateau as a CAMERA / observation-window artifact, NOT an
  intrinsic stuck component: it grounds this on (a) the plateau MELTING as the watch lengthens (the
  apparent shelf shrinks toward zero across the sweep — the signal fully relaxes given enough
  observation), and (b) the response-vs-fluctuation locus being a single straight line of slope 1 (in
  balance / equilibrium) within every window — so the shelf is NOT an out-of-balance/aging plateau. It
  reads the signal as ONE fixed two-timescale ergodic relaxation (a fast part + a much slower part), the
  same in every run, with only the observation window changing what is resolved; and it identifies a
  matched (long-enough) window that gives the true full-relaxation picture. It answers "is the stuck part
  real?" as NO (a watching-time artifact), and "is there a right window?" as YES (long enough to span the
  slow part). It need NOT say "τ_obs," "camera," "ergodic," "FDR," "kernel": a researcher-facing "that
  frozen shelf is your watch length, not the signal — the slow part just hasn't finished relaxing in the
  short runs; watch ~100× longer and it goes all the way down; nothing is permanently stuck, and the
  signal stays in normal balance throughout" is a MATCH. The camera-artifact claim must be grounded on the
  melting plateau across windows; the in-balance/not-a-glass claim on the slope-1 locus; the two-timescale
  claim on the fast drop + slow shelf. Empty provenance on any → hollow.

MISS
  Reads the plateau as a genuine stuck / non-ergodic / frozen component (cage_edge 1 — the headline trap);
  OR as observation-length-independent (cage_edge 2, missing the camera dependence); OR attributes the
  change to the SIGNAL evolving/aging rather than the camera (cage_edge 3); OR collapses it to a single
  timescale (cage_edge 4 → route 1); OR reads the plateau as out-of-balance/aging X<1 (cage_edge 5,
  Cat-8 mis-attribution). A monolithic fit that cannot localize a MISS to one module (a single placement
  vs the band readout) also fails meta-validity P (sweep contract, §6).

KILL  (framework falsifiers — invalid substrate/reading, not a bad fit)
  1. a NaN / non-finite in any computed quantity (asymptotic-closure tripwire; never filled).
  2. the FDR locus reported with X > 1 at any window (X > 1 is a theorem violation).
  3. a sustained current / nonzero entropy production reported as GROUND TRUTH (equilibrium scalar — no
     current sector) — a freeze check; an ANSWERER reading a false current is a MISS, not a KILL.
  4. the GROUND-TRUTH apparent plateau not melting toward 0 as τ_obs grows, or X≠1 at any window (a
     broken freeze, not a finding) — a freeze check.

**anchor-and-assert (checked at unseal by the orchestrator — NOT handed to the answerer):**
FIRST CONTACT — no prior earned τ_obs/camera operating point. Conceptual FOIL to v4 (kww glass): v4's
plateau is an INTRINSIC non-ergodicity q_EA with X<1 (aging) that does NOT melt; this v13 plateau LOOKS
like it at the short window (q≈0.62 ~ a glass q_EA) but is unmasked as a CAMERA artifact by the melt +
X=1. SOFT consistency check at unseal: the short-window level should superficially resemble a v4-style
frozen plateau, but the across-window melt + the slope-1 (X=1) locus must separate it from v4's
X<1 aging. No hard numeric anchor; cross-pass drift detection on this oracle resumes if a second camera
sweep is posed.

**what this vertical tests (ledger residue seed):** can conform take a researcher's single fluctuating
signal, measured at 32 observation durations and described only as "it freezes on a shelf when I watch
briefly but fully relaxes when I watch long — is part of it permanently stuck, or did I just not watch
long enough, and is there a right window?" — and (a) read the apparent frozen plateau as a CAMERA
(observation-window) artifact, not an intrinsic stuck/non-ergodic component, grounding it on the plateau
MELTING across windows + the slope-1 (X=1, in-balance) locus, (b) read the signal as ONE fixed
two-timescale ergodic equilibrium relaxation (same in every run; only the window changes what's
resolved), (c) identify the matched (long-enough) window that gives the true full-relaxation picture, and
(d) correct the "permanently stuck / non-ergodic" worry. This LANDS Cat 5 (Kernel/τ_obs) — the kernel
pre-gate's own job: distinguishing a substrate property from a camera artifact. It is the camera-artifact
FOIL to v4/v9/v10's intrinsic glass (there the q_EA plateau is real, X<1, and does NOT melt; here it is
a window artifact, X=1, and melts). The headline MISS is reading the short-window shelf as a genuine
frozen/glassy component; the win is "that's your watch length, not the signal — watch long enough and it
fully relaxes; nothing is stuck, and it stays in balance throughout."
