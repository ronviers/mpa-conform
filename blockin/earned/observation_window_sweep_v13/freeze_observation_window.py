"""freeze — observation_window_sweep_v13  (bespoke, one substrate, brittle by design)

The Cat-5 (Kernel / camera / tau_obs) landing — a NEW category. Cat 5 is the kernel
pre-gate's own job (WORKFLOW §E): is an apparent regime a property of the SUBSTRATE, or of
the OBSERVATION WINDOW (the camera)? RFC-S §0.2: tau_obs IS the camera; the canonical reading
is observer-relative and auto-remaps along the RG-flow trajectory as tau_obs moves (RFC-S §1),
while the substrate's intrinsic trajectory (and any k_frust) is RG-INVARIANT. "The problem is
the camera" (Cat 5) is when the apparent character is set by tau_obs, not by the substrate.

THE SUBSTRATE (fixed, equilibrium, two-timescale): one passive fluctuating signal whose true
autocorrelation is a FIXED two-exponential —
    C(tau) = a_f*exp(-tau/tau_f) + a_s*exp(-tau/tau_s),   tau_f << tau_s  (3 decades apart)
in thermal equilibrium, so the response obeys the FDT exactly:
    chi(tau) = (C(0) - C(tau)) / T,   T = 1,  C(0) = a_f + a_s = 1   ->  X = 1 at every lag.
The signal is ERGODIC: given enough time it fully decorrelates (C -> 0). Its intrinsic content
(tau_f, tau_s, a_s, and X=1) is FIXED — it does not depend on how you look at it.

THE CAMERA (the swept axis): tau_obs = the OBSERVATION-WINDOW length (how long you watch / the
max lag you can measure), swept across five levels from short to long. Sampling is fixed-fine
(min lag << tau_f, so the FAST mode is always resolved); only the observation DURATION changes.
What the camera does to the SLOW mode:
  - tau_obs << tau_s  (short window): the slow mode has barely decayed within the window, so the
    measured C drops by the fast amount a_f and then PLATEAUS at ~a_s. Read in isolation, this
    looks like a FROZEN / non-ergodic component (an apparent non-ergodicity plateau q ~ a_s) —
    indistinguishable, from ONE short window, from a genuine glass plateau q_EA.
  - tau_obs >> tau_s  (long / matched window): the slow mode fully decays within the window; the
    measured C goes all the way to 0 — fully ergodic, a clean two-step.
So as tau_obs sweeps short->long, the apparent non-ergodicity plateau MELTS (q: ~a_s -> 0). The
apparent regime (non-ergodic vs ergodic) is a function of the CAMERA, not the substrate.

THE TWO TEETH (what separates a Cat-5 CAMERA artifact from a Cat-8 intrinsic glass):
  1. The apparent plateau MELTS as the window opens — a genuine frozen/non-ergodic (aging) plateau
     q_EA would NOT melt with longer observation (it is fixed by the substrate). Melting => camera.
  2. The FDR locus chi vs (C(0)-C(tau)) is a single straight line of slope 1 (X=1) within EVERY
     window — the signal is in equilibrium / in balance at every camera setting. A genuine glass
     plateau is OUT of equilibrium (bent locus, slow-segment slope X<1, the v4/v9/v10 aging
     signature). X=1 everywhere => not a glass; the freezing is under-resolution, not aging.
So the headline trap is reading the short-window plateau as an INTRINSIC frozen / non-ergodic /
glassy component (a Cat-8 mis-attribution). The correct read: it is a CAMERA (observation-window)
artifact (Cat 5) — the substrate is one fixed two-timescale ERGODIC equilibrium relaxation; the
apparent freezing is the slow mode under-resolved by a short window; the matched window (tau_obs
spanning tau_s) resolves the true ergodic structure.

INVARIANT (must NOT migrate — the RG-invariant / k_frust analogue for this scalar): the intrinsic
two timescales (tau_f, tau_s), the slow-mode weight a_s, and the equilibrium character X=1. What
MIGRATES is only the apparent non-ergodicity plateau q(tau_obs) — the camera's reading position
on the fixed RG trajectory.

WHY AN ORACLE (and not a library cell): the truth needed is "the SAME fixed equilibrium two-step,
windowed at five tau_obs" with X=1 exactly and a clean a_s plateau that melts — the analytic
two-exponential gives that exactly and makes the camera-vs-substrate distinction blind-readable.
(A real two-timescale fluctuating signal measured for five different durations is the external
physics this idealizes. v4's kww_oracle is the intrinsic-glass FOIL: there the plateau is q_EA
with X<1, fixed; here it is a camera artifact with X=1, melting.)

ANCHOR: FIRST CONTACT on this oracle — no prior earned tau_obs/camera operating point. Conceptual
FOIL to v4 (kww glass: intrinsic q_EA plateau, X<1, does not melt) — the short-window level here
mimics a glass plateau (q~0.6) but is unmasked as a camera artifact by the melt + X=1. Checked
conceptually at unseal, not a hard numeric anchor.

BLINDING: the emitted CSV carries ONLY (level, window_rel, tau, C, chi). window_rel is the
researcher's OWN knob — the relative observation-window length, normalized to the shortest run
(level 0 = 1.0x). It carries NO tau_f/tau_s/a_s, no tau_obs, no X, no framework token. A researcher
who measures one signal's autocorrelation + response over five observation durations yields exactly
these curves. The level index is a neutral 0..4 (shortest -> longest watching).

Run:  python H:/mpa-conform/blockin/questions/observation_window_sweep_v13/freeze_observation_window.py

Emits: data/observation_window_sweep_v13.frozen.csv  (level,window_rel,tau,C,chi — the blind artifact)
       prints the SEALED ground truth (per-window apparent plateau, FDR slope, the melt band) for
       the author/human. CSV carries none of it.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "observation_window_sweep_v13.frozen.csv"

# ----- the FIXED substrate (the SEAL; none of this reaches the CSV) -----------------
TAU_F = 1.0        # fast intrinsic time
TAU_S = 1000.0     # slow intrinsic time (3 decades slower)
A_F   = 0.40       # fast-mode weight
A_S   = 0.60       # slow-mode weight (the apparent plateau height at short windows); A_F+A_S=1 => C(0)=1
T     = 1.0        # FDT temperature -> X=1 (equilibrium) at every lag

# ----- the CAMERA: observation-window length tau_obs, swept short -> long ----------
# 32 levels log-spaced across the data's time span (3 .. 30000, ~4 decades: a short watch that
# resolves the fast mode + freezes the slow one, up to a watch >> tau_s that resolves both). The
# dense sweep makes the plateau-melt a continuous movie across 32 little plot boxes (one per level).
N_LEVELS = 32
TAU_OBS = np.geomspace(3.0, 30000.0, N_LEVELS)   # level 0..31 (short -> long watch)
MIN_LAG = 0.05     # fixed-fine sampling floor (<< tau_f, so the FAST mode is always resolved)
N_TAU   = 40


def C_of(tau):
    return A_F * np.exp(-tau / TAU_F) + A_S * np.exp(-tau / TAU_S)


def C_chi(tau):
    C = C_of(tau)
    chi = (C_of(0.0) - C) / T            # equilibrium FDT, X=1
    return C, chi


def materialize():
    lines, per = [], []
    win_base = float(TAU_OBS[0])
    for lvl, tobs in enumerate(TAU_OBS):
        tobs = float(tobs)
        taus = np.concatenate(([0.0], np.geomspace(MIN_LAG, tobs, N_TAU - 1)))
        C, chi = C_chi(taus)
        window_rel = tobs / win_base
        per.append(dict(level=lvl, tau_obs=tobs, window_rel=window_rel, taus=taus, C=C, chi=chi))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{window_rel:.6g},{t:.6g},{c:.8g},{x:.8g}")
    return lines, per


def fdr_slope(C, chi):
    """Slope of chi vs (C(0)-C(tau)) through the origin. = 1 (X=1) within every window
    (equilibrium). Computed here, not via conform."""
    drop = C[0] - C
    m = float(np.dot(drop, chi) / np.dot(drop, drop))
    pred = m * drop
    r2 = 1.0 - float(np.sum((chi - pred) ** 2) / max(np.sum((chi - chi.mean()) ** 2), 1e-30))
    return m, r2


def main():
    lines, per = materialize()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# observation_window_sweep_v13 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# ONE fluctuating signal, measured at FIVE observation-window lengths (level 0 shortest\n"
        "# watching -> level 4 longest). tau is the signal's own clock (a lag). Columns: level,\n"
        "# window_rel (relative observation-window length, normalized to the shortest run = 1.0x),\n"
        "# tau, C (autocorrelation), chi (integrated step-response). No times, no model parameters.\n"
        "# Sampling is fixed-fine; only the observation DURATION (max lag) differs across levels.\n"
        "level,window_rel,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  FIXED substrate: two-exponential equilibrium relaxation, tau_f={TAU_F}, tau_s={TAU_S}, "
          f"a_f={A_F}, a_s={A_S}; X=1 at every lag (FDT). The CAMERA is tau_obs (window length).")
    print(f"  {len(per)} levels, tau_obs log-spaced {TAU_OBS[0]:.2f} .. {TAU_OBS[-1]:.0f}. Sample rows:")
    print(f"  {'lvl':>3} {'tau_obs':>9} {'window_rel':>10} {'app. plateau q':>14} "
          f"{'FDR slope':>9} {'R2':>6} {'X':>4} {'slow-mode resolved?':>20}")
    qs, slopes = [], []
    for L in per:
        m, r2 = fdr_slope(L["C"], L["chi"])
        q_app = float(L["C"][-1])                      # C at the window edge = apparent plateau
        qs.append(q_app); slopes.append(m)
    for i, L in enumerate(per):
        if i % 4 != 0 and i != len(per) - 1:           # print every 4th level + the last
            continue
        q_app = qs[i]
        resolved = "frozen (under-res)" if q_app > 0.5 * A_S else ("melting" if q_app > 0.05 else "fully resolved")
        print(f"  {L['level']:>3} {L['tau_obs']:>9.1f} {L['window_rel']:>10.1f} {q_app:>14.4f} "
              f"{slopes[i]:>9.4f} {1.0:>6.3f} {1.0:>4.1f} {resolved:>20}")
    print(f"  apparent-plateau band q(tau_obs) [{len(qs)} levels]: first {round(qs[0],3)} ... "
          f"mid {round(qs[len(qs)//2],3)} ... last {round(qs[-1],3)}; monotone melt, max step {max(qs[i]-qs[i+1] for i in range(len(qs)-1)):.3f}")
    print(f"     -> MELTS from ~a_s={A_S} (slow mode frozen by the short window) to ~0 (fully resolved)")
    print(f"     -> the apparent NON-ERGODICITY is a CAMERA (observation-window) artifact, NOT intrinsic.")
    print(f"  FDR slope band: all = 1.000 (range {min(slopes):.4f}..{max(slopes):.4f}, R2=1.000) -> "
          f"X=1 within EVERY window (EQUILIBRIUM / in balance)")
    print(f"     -> distinguishes this CAMERA artifact (X=1, plateau melts) from a genuine GLASS plateau")
    print(f"        (q_EA, X<1, does NOT melt -- the v4/v9/v10 aging signature).")
    print(f"  INVARIANT (does NOT migrate): tau_f, tau_s, a_s, and X=1. MIGRATES: only q(tau_obs).")
    print(f"  THE READ: the apparent frozen plateau is the OBSERVATION WINDOW, not the signal. The signal")
    print(f"      is one fixed two-timescale ERGODIC equilibrium relaxation; the short-window 'freezing'")
    print(f"      is the slow mode under-resolved; watch long enough (matched window, tau_obs>>tau_s) and")
    print(f"      it fully relaxes. The problem is the CAMERA (Cat 5), not an intrinsic frozen state.")

    # self-consistency assertions (author-side)
    for L in per:
        m, r2 = fdr_slope(L["C"], L["chi"])
        assert abs(m - 1.0) < 1e-6, f"FDR slope must be 1 (X=1) at every window; got {m}"
        assert r2 > 1.0 - 1e-9, "FDR locus must be an exact straight line through origin (equilibrium)"
        assert np.all(np.isfinite(L["C"])) and np.all(np.isfinite(L["chi"])), "no NaN"
    assert qs[0] > 0.5 and qs[-1] < 0.05, "apparent plateau must FROZEN at short window and MELT at long"
    assert all(qs[i] >= qs[i + 1] - 1e-9 for i in range(len(qs) - 1)), "apparent plateau must melt monotonically"
    print("\nself-consistent: X=1 / FDR slope 1 at every window + apparent plateau melts monotonically "
          "~a_s->0 + no NaN. OK.")
    print(f"wrote {OUT}  ({len(lines)} rows, {len(TAU_OBS)} levels)")


if __name__ == "__main__":
    main()
