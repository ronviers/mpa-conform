"""freeze — glass_quench_wait_v10  (bespoke, one substrate, brittle by design)

The WAITING-TIME (t_w) vector: the meta-SOP-escalated question v4 parked TWICE and v9
left standing. v4 (single deep-aging point) and v9 (a temperature sweep through Tg, each
level at one implicit age) both read the slow-mode FDT violation X<1 off the two-slope FDR
locus -- but neither could tell WHICH KIND of out-of-equilibrium it is:

  (A) GENUINE AGING -- non-stationary. The system keeps evolving after the quench: the
      slow (alpha) relaxation gets SLOWER the longer you wait (tau_alpha grows with the
      waiting time t_w). The two-time functions C(t_w + tau, t_w), chi depend on t_w, NOT
      on the lag tau alone -- they are NOT time-translation invariant (TTI). It never
      settles into a fixed state.
  (B) STATIONARY effective-temperature -- a fixed out-of-equilibrium STEADY state. X < 1
      but the curves are TTI: they depend only on the lag tau, identical at every waiting
      time. You wait longer and nothing changes.

Both give a bent FDR locus with a slow-segment slope X < 1 at a SINGLE waiting time, so a
single-t_w measurement (v4, each v9 level) CANNOT separate them. The discriminator is the
t_w AXIS: sweep the waiting time and ask whether the curves SHIFT (A, aging) or COLLAPSE
(B, stationary).

Substrate: a GLASS-AGING ORACLE -- the v9 glass-transition oracle (two-step KWW, truth
computed HERE, never via conform) held at ONE deep-quench temperature (below Tg) and swept
along the WAITING-TIME axis instead of temperature. At waiting time t_w the two-time
fluctuation correlator is the two-timescale KWW with an age-dependent alpha-time:

  C(tau; t_w)   = (1 - q_EA) * exp(-tau / tau_beta)
                +      q_EA  * exp(-(tau / tau_alpha(t_w))**beta_KWW)
  chi(tau; t_w) = (1 - q_EA) * (1 - exp(-tau / tau_beta))             # FAST beta part, FDT slope 1
                +  X * q_EA  * (1 - exp(-(tau / tau_alpha(t_w))**beta_KWW)) # SLOW alpha part, slope X

The fast beta-relaxation drops C to the plateau q_EA and is EQUILIBRATED at every age (TTI,
FDT slope 1). The slow stretched alpha-relaxation is the aging one: its time grows with the
waiting time by the SIMPLE-AGING law (full aging, mu = 1):

    tau_alpha(t_w) = TAU_ALPHA_REF * (t_w / T_W_REF)**MU          # MU = 1 -> tau_alpha ~ t_w

THE PHYSICS (the honest sealed answer -- GENUINE AGING, case A): below Tg the slow manifold
is out of equilibrium at a well-defined effective temperature T_eff > T, so the slow-mode
FDT ratio X = T/T_eff = X_FLOOR < 1 is AGE-INDEPENDENT (a property of the frozen slow modes,
not of how long you waited). What DOES change with age is the alpha-time: the older the
sample, the slower it relaxes (tau_alpha grows ~ t_w). So across the t_w sweep:
  * X is FLAT at X_FLOOR (slow-segment FDR slope ~0.5 at every age) -> out of equilibrium,
    NOT re-equilibrating;
  * fast-segment FDR slope ~1 at every age -> the beta part stays equilibrated;
  * tau_alpha GROWS ~ t_w and the C(tau) curves do NOT collapse onto a master curve in raw
    lag tau (at a fixed lag the older sample is MORE correlated) -> NON-stationary = AGING.
The system keeps evolving; it never reaches a stationary state. This RESOLVES v4's parked
question: the X<1 is genuine waiting-time aging, not a stationary eff-T.

The teeth: conform must read the t_w-DEPENDENCE (tau_alpha grows with age, curves do not
collapse) as GENUINE AGING -- and must NOT (1) read a stationary eff-T / TTI steady state
[the headline trap: a single-t_w mindset that ignores the shift], (2) read re-equilibration
(X -> 1 with age), (3) collapse the two-step to a single mode, (4) read an oscillation/
current, or (5) read the relaxation SPEEDING UP with age (wrong direction). The win:
"out of balance on the slow modes (about half) at every age, in balance on the fast modes,
AND it keeps aging -- the relaxation slows the longer you wait; it never settles."

WHY AN ORACLE (not the library glass MC cells): the library glass cells carry ONE fixed t_w
each and have null tau_env_analytic below Tg (camera-scale unplaced; X read only at raw-slope,
not validated -- mpa-central DEFERRED.md library-refresh), so a real t_w ladder is not in the
library and a blind read off it would not isolate conform. The oracle encodes the aging law
tau_alpha(t_w) and the age-independent slow-mode X directly (X a correlator parameter, exactly
as v4's kww_oracle prescribed X=0.5), so the aging signature is clean and freeze-computed.
(A real aging structural glass after a quench is the external physics this idealizes.)

ANCHOR (checked at unseal, NOT told to the answerer): level 2 (t_w = T_W_REF) is built with
tau_alpha = 150, q_EA = 0.80, beta_KWW = 0.55, X = 0.50 -- IDENTICAL to melt_cooling_sweep_v9
level 4 (the deepest-quench point). Its single-time C(tau), chi(tau) curves reproduce v9 L4
exactly; its placement (X=0.5, two-step, plateau 0.80) must reproduce v9 L4's reading. Cross-
pass drift detection.

BLINDING: the emitted CSV carries ONLY (level, tau, C, chi). It does NOT carry the waiting
time, temperature, Tg, tau_alpha, tau_beta, q_EA, beta_KWW, X, T_eff, the FDR slopes, the
aging exponent MU, or any framework token. A glass researcher who quenches a sample and
measures correlation + response at five increasing ages yields exactly these curves. The
level index is a neutral 0..4 (youngest -> oldest); native times are withheld (v7/v8/v9:
absolute distance-in-native-units is not blind-closeable).

Run:  python H:/mpa-conform/blockin/questions/glass_quench_wait_v10/freeze_glass_aging.py

Emits:  data/glass_quench_wait_v10.frozen.csv   (level,tau,C,chi -- the blind artifact)
        prints the SEALED ground truth (per-level t_w, tau_alpha, q_EA, X, two-slope FDR
        fast/slow slopes; the aging diagnostics: tau_alpha ~ t_w, fixed-lag C climb, non-
        collapse) for the author to paste / human to eyeball. The CSV carries NONE of it.
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
OUT = HERE / "data" / "glass_quench_wait_v10.frozen.csv"

# ----- oracle parameters (the SEAL; none of this reaches the CSV) -----------------
# ONE deep-quench temperature (below Tg, the aging regime), measured at FIVE increasing
# waiting times t_w after the quench (level 0 = youngest ... level 4 = oldest). The ONLY
# thing that changes level-to-level is the AGE; the material and temperature are fixed.
WAIT      = np.array([1.0, 2.0, 4.0, 8.0, 16.0])   # waiting time t_w after quench (arb units; 16x span)
MU        = 1.0        # aging exponent: tau_alpha ~ t_w**MU  (MU=1 -> full/simple aging)
T_W_REF   = 4.0        # reference waiting time -> level 2 (the v9-L4 anchor point)
TAU_ALPHA_REF = 150.0  # tau_alpha at t_w = T_W_REF (= v9 level-4 alpha-time: the anchor)

Q_EA      = 0.80       # non-ergodicity plateau (deep cage; = v9 level 4) -- FIXED (one temperature)
BETA_KWW  = 0.55       # stretching exponent of the alpha-relaxation (beta<1; = v9 level 4)
TAU_BETA  = 0.05       # fast beta-relaxation time (tau_beta << tau_alpha -> clean two-step)
X_FLOOR   = 0.50       # slow-mode FDT ratio X = T/T_eff of the aging state -- AGE-INDEPENDENT (= v4/v9 deepest)

N_TAU     = 36         # log-spaced lags per level
WIN_MULT  = 15.0       # window out to ~15*tau_alpha so the alpha-relaxation sheds (slope X readable)


def tau_alpha_of(t_w: float) -> float:
    return TAU_ALPHA_REF * (t_w / T_W_REF) ** MU


def kww_C_chi(tau, q_EA, tau_alpha, X):
    fast_C = (1.0 - q_EA) * np.exp(-tau / TAU_BETA)
    slow_C = q_EA * np.exp(-(tau / tau_alpha) ** BETA_KWW)
    C = fast_C + slow_C
    chi = (1.0 - q_EA) * (1.0 - np.exp(-tau / TAU_BETA)) \
        + X * q_EA * (1.0 - np.exp(-(tau / tau_alpha) ** BETA_KWW))
    return C, chi


def materialize():
    lines = []
    per_level = []
    for lvl in range(5):
        t_w = float(WAIT[lvl])
        ta = tau_alpha_of(t_w)
        tau_max = WIN_MULT * ta
        taus = np.concatenate(([0.0], np.geomspace(0.005, tau_max, N_TAU - 1)))
        C, chi = kww_C_chi(taus, Q_EA, ta, X_FLOOR)
        per_level.append(dict(level=lvl, tau=taus, C=C, chi=chi,
                              q_EA=Q_EA, tau_alpha=ta, X=X_FLOOR, t_w=t_w))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{t:.6g},{c:.8g},{x:.8g}")
    return lines, per_level


def two_slope_fdr(L):
    """Fast- and slow-segment slopes of chi vs (1-C). Fast ~1 (beta part, FDT), slow ~X
    (alpha part, FDT-violated). Computed here, not via conform -- the answer-key is the
    prescribed X; the freeze just confirms slow=X at every age."""
    drop = 1.0 - L["C"]              # C(0)=1 so C(0)-C = 1-C
    chi = L["chi"]
    q = L["q_EA"]
    knee = 1.0 - q                   # fast part shed -> the plateau knee in (1-C)
    fast = drop < 0.8 * knee
    slow = drop > knee + 0.10 * q    # well past the knee, into the alpha-decay
    def slope(mask):
        if mask.sum() < 2:
            return float("nan")
        return float(np.polyfit(drop[mask], chi[mask], 1)[0])
    return dict(level=L["level"], s_fast=slope(fast), s_slow=slope(slow))


def C_at_reference_lag(per_level, tau_ref):
    """Non-stationarity probe: C interpolated at ONE fixed lag tau_ref, level by level.
    If the curves were TTI (stationary), this is constant across levels. Under aging it
    CLIMBS with t_w (the older sample is more correlated at the same lag)."""
    out = []
    for L in per_level:
        c = float(np.interp(tau_ref, L["tau"], L["C"]))
        out.append(c)
    return out


def main():
    lines, pl = materialize()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# glass_quench_wait_v10 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# Five settings (level 0..4) of one fluctuating quantity in ONE material at ONE\n"
        "# temperature, measured at five successively longer waiting times after a quench;\n"
        "# tau is the material's own clock (a lag). Columns: level,tau,C,chi. No times, no\n"
        "# temperatures, no model parameters. Each level has its own settling window, so tau\n"
        "# ranges differ (the older settings need the longest watching).\n"
        "level,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  ONE temperature (deep below Tg); q_EA={Q_EA}  beta_KWW={BETA_KWW}  tau_beta={TAU_BETA}"
          f"  X(slow,age-independent)={X_FLOOR}  aging law: tau_alpha ~ t_w**{MU}")
    print(f"  {'lvl':>3} {'t_w':>6} {'tau_alpha':>9} {'tau_a/t_w':>9} {'q_EA':>6} {'X':>6} "
          f"{'FDR fast':>9} {'FDR slow':>9}")
    for L in pl:
        f = two_slope_fdr(L)
        print(f"  {L['level']:>3} {L['t_w']:>6.1f} {L['tau_alpha']:>9.1f} "
              f"{L['tau_alpha']/L['t_w']:>9.2f} {L['q_EA']:>6.2f} {L['X']:>6.2f} "
              f"{f['s_fast']:>9.3f} {f['s_slow']:>9.3f}")
    tw_band = [L["t_w"] for L in pl]
    ta_band = [round(L["tau_alpha"], 1) for L in pl]
    X_band = [round(L["X"], 3) for L in pl]
    print(f"  t_w band:       {tw_band}  (waiting time, the swept axis; 16x span)")
    print(f"  tau_alpha band: {ta_band}  -> GROWS ~ t_w (full aging, MU={MU}); ratio tau_a/t_w CONSTANT")
    print(f"  X band:         {X_band}  -> FLAT at {X_FLOOR} (slow-mode eff-T is age-INDEPENDENT; X<1 = out of equilibrium)")
    # non-stationarity probe at a fixed reference lag (inside every window: min tau_max ~ 560)
    tau_ref = 50.0
    Cref = C_at_reference_lag(pl, tau_ref)
    print(f"  C at fixed lag tau={tau_ref}: {[round(c,3) for c in Cref]}  -> CLIMBS with t_w"
          f" (NOT time-translation invariant -> the curves do NOT collapse -> AGING, not stationary)")
    print(f"  ANCHOR: level 2 (t_w={T_W_REF}) has tau_alpha=150, q_EA=0.80, beta=0.55, X=0.50"
          f" == v9 level 4 EXACTLY (single-time curves identical).")
    print(f"  THE READ: GENUINE waiting-time AGING (case A). Slow modes out of equilibrium (X={X_FLOOR}<1)")
    print(f"      at EVERY age (not re-equilibrating); fast modes equilibrated (slope 1); and the slow")
    print(f"      relaxation SLOWS with age (tau_alpha ~ t_w, curves non-TTI) -> it never settles into a")
    print(f"      stationary eff-T state. Resolves v4's parked genuine-aging-vs-stationary question.")
    print(f"wrote {OUT}  ({len(lines)} rows, 5 levels)")


if __name__ == "__main__":
    main()
