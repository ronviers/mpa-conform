"""freeze — melt_cooling_sweep_v9  (bespoke, one substrate, brittle by design)

The DYNAMICAL-category-CROSSING probe: the ONE separability case left open after v8.
v6 (discrete reciprocity cut), v7 (metric axis WITHIN a category), and v8 (metric axis
crossing a THERMODYNAMIC critical point in equilibrium) all stayed SHARP — no smear. But
v8 sharpened the form: a thermodynamic phase boundary is not an MPA dynamical-category
boundary (crossing it in equilibrium keeps X=1). The genuinely-open question is a metric
axis that crosses a real DYNAMICAL-category boundary: equilibrium (Cat 1, X=1) ->
out-of-equilibrium AGING (Cat 8, X<1). That boundary is the GLASS TRANSITION Tg.

Substrate: a GLASS-TRANSITION ORACLE — the v8 pattern (analytic correlator, truth computed
HERE, never via conform) built on the v4 kww_oracle two-step form, swept across Tg. It
models a supercooled melt COOLED through its glass transition: at each temperature the
fluctuation correlator is the two-timescale KWW

  C(tau)   = (1 - q_EA) * exp(-tau / tau_beta)
           +      q_EA  * exp(-(tau / tau_alpha)**beta_KWW)
  chi(tau) = (1 - q_EA) * (1 - exp(-tau / tau_beta))            # FAST beta part, FDT: slope 1
           +  X * q_EA  * (1 - exp(-(tau / tau_alpha)**beta_KWW)) # SLOW alpha part, FDT slope X

A fast beta-relaxation drops C to the plateau q_EA; a slow STRETCHED (beta<1) alpha-
relaxation finally sheds it. The FDR locus chi vs (1 - C) is therefore TWO-SLOPE: slope 1
on the fast part (quasi-equilibrium), then slope X on the slow part. X is the slow-mode FDT
violation (X = T/T_eff): X = 1 is equilibrium (Cat 1), X < 1 is glassy aging (Cat 8).

THE PHYSICS OF THE CROSSING (why it SMEARS — the honest sealed answer): the glass transition
is a KINETIC crossover, not a sharp thermodynamic transition. As the melt is cooled the
alpha-relaxation time tau_alpha grows steeply (Vogel-Fulcher-like) toward the observation/
cooling window. While tau_alpha <= the equilibration window the slow modes equilibrate -> X=1
(liquid). Once tau_alpha exceeds it, the slow modes freeze out of equilibrium at T_eff > T ->
X < 1 (aging glass), the deeper the quench the smaller X. So X(T) crosses 1 -> X_floor
SMOOTHLY across Tg, with INTERMEDIATE levels at intermediate X (partially aged). X is DERIVED
from tau_alpha by the fall-out rule, not hand-drawn:

    X(level) = clamp(1 - SLOPE * log10(tau_alpha / tau_alpha_at_Tg), X_floor, 1)

The expected result: the Cat-1 -> Cat-8 crossing SMEARS (a crossover band of intermediate X),
UNLIKE the topologically-sharp reciprocity cut (v6) and UNLIKE the no-kind-change metric axes
(v7/v8). The teeth: conform must READ the intermediate X (place the mid levels as PARTIALLY
aged, not snap each to X=1 or X=X_floor), must NOT call the hot levels aging, must NOT call the
cold levels equilibrium, and must read the two-step structure (not collapse the slow tail to a
single Vertex relaxation). This is the X<1 (aging) DYNAMICAL crossing that v8's X=1
(equilibrium) thermodynamic crossing was the clean foil for.

WHY AN ORACLE (and not the library glass MC cells): the library glass cells have null
tau_env_analytic below Tg (camera-scale unplaced; X read only at raw-slope, not validated --
mpa-central DEFERRED.md library-refresh), so a blind X(T)-crossover read off them would not
isolate conform. The oracle encodes X(T) directly as the slow-mode FDT ratio of the aging
state (X is a correlator parameter, exactly as v4's kww_oracle prescribed X=0.5), so the
crossover is clean and freeze-computed. (A real fragile glass-former is the external physics
this idealizes; the oracle is the clean stand-in until the library refresh lands.)

BLINDING: the emitted CSV carries ONLY (level, tau, C, chi). It does NOT carry temperature,
Tg, tau_alpha, tau_beta, q_EA (the plateau), beta_KWW, X, T_eff, the FDR slopes, or any
framework token. A glass researcher's correlation + response measurement at five temperatures
yields exactly these curves. The level index is a neutral 0..4 (hot->cold); native
temperatures are withheld (v7/v8: absolute distance-in-native-units is not blind-closeable).

Run:  python H:/mpa-conform/blockin/questions/melt_cooling_sweep_v9/freeze_glass_transition.py

Emits:  data/melt_cooling_sweep_v9.frozen.csv   (level,tau,C,chi -- the blind artifact)
        prints the SEALED ground truth (per-level tau_alpha, q_EA, X, two-slope FDR fast/slow
        slopes, single-line R^2; the X crossover band) for the author to paste / human to
        eyeball. The CSV carries NONE of it.
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
OUT = HERE / "data" / "melt_cooling_sweep_v9.frozen.csv"

# ----- oracle parameters (the SEAL; none of this reaches the CSV) -----------------
# five temperatures cooled through Tg (level 0 = hot liquid ... level 4 = deep glass).
# hand-set monotonic phenomenology (the v4/v8 pattern): the cage q_EA deepens and the
# alpha-time tau_alpha grows steeply (VF-like) as the melt is cooled.
TAU_ALPHA = np.array([1.0, 3.0, 10.0, 40.0, 150.0])   # alpha-relaxation time (grows ~150x)
Q_EA      = np.array([0.30, 0.40, 0.55, 0.68, 0.80])  # non-ergodicity plateau (deepens)
BETA_KWW  = 0.55       # stretching exponent of the alpha-relaxation (beta<1)
TAU_BETA  = 0.05       # fast beta-relaxation time (tau_beta << tau_alpha -> clean two-step)

# X(T) DERIVED from the fall-out rule: the slow modes equilibrate (X=1) while tau_alpha is
# within the equilibration window (here taken to set in at level 1 = operational Tg), then
# fall out of equilibrium the more tau_alpha exceeds it. X = T/T_eff < 1 below Tg.
TAU_ALPHA_TG = 3.0     # tau_alpha at the operational glass transition (level 1)
X_SLOPE      = 0.33    # how fast X drops per decade of tau_alpha beyond Tg (fragility)
X_FLOOR      = 0.50    # deepest-quench aging value (T_eff/T = 2), as in v4

N_TAU = 36             # log-spaced lags per level
WIN_MULT = 15.0        # window out to ~15*tau_alpha so the alpha-relaxation sheds (slope X readable)


def X_of(tau_alpha: float) -> float:
    x = 1.0 - X_SLOPE * np.log10(tau_alpha / TAU_ALPHA_TG)
    return float(np.clip(x, X_FLOOR, 1.0))


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
        ta, q = float(TAU_ALPHA[lvl]), float(Q_EA[lvl])
        X = X_of(ta)
        tau_max = WIN_MULT * ta
        taus = np.concatenate(([0.0], np.geomspace(0.005, tau_max, N_TAU - 1)))
        C, chi = kww_C_chi(taus, q, ta, X)
        per_level.append(dict(level=lvl, tau=taus, C=C, chi=chi, q_EA=q, tau_alpha=ta, X=X))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{t:.6g},{c:.8g},{x:.8g}")
    return lines, per_level


def two_slope_fdr(L):
    """Fast- and slow-segment slopes of chi vs (1-C), and the R^2 of a SINGLE-line fit
    (high when X=1 / single slope, dropping as the X<1 bend appears). Computed here, not
    via conform -- the answer-key is the prescribed X, the freeze just confirms slow=X."""
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
    s_fast, s_slow = slope(fast), slope(slow)
    A = np.vstack([drop, np.ones_like(drop)]).T
    (m, b), *_ = np.linalg.lstsq(A, chi, rcond=None)
    pred = A @ [m, b]
    r2 = 1.0 - np.sum((chi - pred) ** 2) / max(np.sum((chi - chi.mean()) ** 2), 1e-30)
    return dict(level=L["level"], s_fast=s_fast, s_slow=s_slow, r2_single=r2)


def main():
    lines, pl = materialize()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# melt_cooling_sweep_v9 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# Five settings (level 0..4) of one fluctuating quantity in one material cooled across\n"
        "# its settings; tau is the material's own clock (a lag). Columns: level,tau,C,chi. No\n"
        "# temperatures, no model parameters. Each level has its own settling window, so tau\n"
        "# ranges differ (the slowest settings need the longest watching).\n"
        "level,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  beta_KWW={BETA_KWW}  tau_beta={TAU_BETA}  Tg at level 1 (tau_alpha={TAU_ALPHA_TG})"
          f"  X_floor={X_FLOOR}  X_slope/decade={X_SLOPE}")
    print(f"  {'lvl':>3} {'tau_alpha':>9} {'q_EA':>6} {'X(=T/Teff)':>11} "
          f"{'FDR fast':>9} {'FDR slow':>9} {'single-line R2':>15} {'kind':>22}")
    for L in pl:
        f = two_slope_fdr(L)
        kind = "equilibrium (Cat 1)" if L["X"] > 0.97 else \
               ("deep aging (Cat 8)" if L["X"] <= X_FLOOR + 0.02 else "partially aged (crossover)")
        print(f"  {L['level']:>3} {L['tau_alpha']:>9.1f} {L['q_EA']:>6.2f} {L['X']:>11.3f} "
              f"{f['s_fast']:>9.3f} {f['s_slow']:>9.3f} {f['r2_single']:>15.5f} {kind:>22}")
    Xband = [round(L["X"], 3) for L in pl]
    print(f"  X crossover band: {Xband}  -> SMOOTH 1 -> {X_FLOOR} (a CROSSOVER, not a jump);"
          f" intermediate levels are PARTIALLY aged")
    print(f"  q_EA band: {[round(L['q_EA'],2) for L in pl]} (plateau deepens);"
          f" tau_alpha band: {[L['tau_alpha'] for L in pl]} (alpha-time grows ~150x)")
    print(f"  KIND crosses Cat 1 (X=1, single-slope FDR) -> Cat 8 (X<1, two-slope FDR) across Tg,")
    print(f"      and it SMEARS: the mid levels sit at intermediate X (the first axis that smears).")
    print(f"wrote {OUT}  ({len(lines)} rows, 5 levels)")


if __name__ == "__main__":
    main()
