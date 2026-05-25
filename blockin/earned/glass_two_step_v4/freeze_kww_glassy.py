"""freeze — glass_two_step_v4  (bespoke, one substrate, brittle by design)

The FIRST Cat-8 (Phase / glassy) vertical — the first to light the two-step
fluctuation-response sector (a frozen-in plateau + a stretched slow relaxation
with a SLOW-mode FDT violation) that a single-mode Vertex substrate cannot reach.

Substrate: the KWW oracle (mpa-central/library/primitives/kww_oracle) — a sum of
independent OU modes realizing a prescribed two-timescale relaxation:
    C(tau)   = (1-q_EA)*exp(-tau/tau_beta) + q_EA*exp(-(tau/tau_alpha)^beta_KWW)
    chi(tau) = (1-q_EA)*(1-exp(-tau/tau_beta))         (fast beta part, FDT: X=1)
             + X*q_EA*(1 - alpha_relax(tau))           (slow alpha part, FDT-violated X<1)
A fast beta-relaxation drops C to the plateau q_EA; a slow STRETCHED
(beta_KWW<1) alpha-relaxation finally relaxes it. The slow modes carry an
effective-temperature mismatch T_eff = T/X (X<1) — the glassy aging signature.

THE TOOTH (vs the Vertex laser, Cat 1, and vs a merely-slow equilibrium): the
class-B laser is a SINGLE underdamped mode (a ring-down, X=1 equilibrium). A
merely-slow-but-equilibrated material would show ONE relaxation and an FDR locus
of slope 1 throughout (X=1). This substrate has (a) a TWO-step C with a plateau,
(b) a STRETCHED slow tail (beta_KWW<1, not single-exponential), and (c) a
two-SLOPE FDR locus: slope 1 (quasi-equilibrium) for the fast part, then slope
X<1 (aging) for the slow part. "It relaxes slowly" does NOT settle whether it is
equilibrated-slow (X=1) or out-of-equilibrium / aging (X<1). The discriminator is
the long-lag FDR slope X, read off chi-vs-(1-C) past the plateau knee.

This is the clean X<1 counterpart to the parked mm1_queue tension (FALSIFICATION.md
FINDING 3): there the truth was reversible critical slowing (X=1) and the trap was
OVER-claiming aging; here the truth is genuine aging (X<1) and the trap is
UNDER-claiming (reading it as equilibrium critical slowing).

Ground truth is exact (the substrate's own mode-sum correlator — the honest "red"
curve), computed HERE, never via conform (data-path independence). For the operating
point q_EA=0.7, tau_alpha=1.0, beta_KWW=0.6, tau_beta=0.05, X=0.5.

BLINDING: the emitted CSV carries ONLY (tau, C, chi) — the correlation and the
integrated step-response. It does NOT carry q_EA, tau_alpha, beta_KWW, tau_beta, X,
the FDR slopes, the plateau height, the effective temperature, or any framework
token. A glass researcher's correlation + susceptibility measurement yields exactly
these two curves; the framework reading stays sealed.

Run:  python H:/mpa-conform/blockin/questions/glass_two_step_v4/freeze_kww_glassy.py

Emits:  data/glass_two_step_v4.frozen.csv   (tau,C,chi — the blind artifact)
        prints the SEALED ground truth (5-vector, two-slope FDR, plateau, T_eff)
        for the author to paste / the human to eyeball. The CSV carries NONE of it.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np

# reuse the library substrate as the answer-path (the truth, never via conform)
sys.path.insert(0, "H:/mpa-central/library")
sys.path.insert(0, "H:/mpa-central/library/primitives")
from kww_oracle.measurements import kww_C_chi  # noqa: E402

# one operating point (a single material's worth of data — I1 placement, not a sweep).
# ~2 decades of timescale separation (tau_beta << tau_alpha) so the fast beta-relaxation
# fully sheds BEFORE the slow alpha-relaxation begins — a clean plateau + clean two-slope
# FDR (the marginal ~1 decade smears the crossover and the fast FDT slope reads <1).
Q_EA, TAU_ALPHA, BETA_KWW, TAU_BETA, X = 0.70, 5.0, 0.60, 0.005, 0.50

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "glass_two_step_v4.frozen.csv"


def two_slope_fdr(C, chi, q_EA):
    """Read the FDR locus chi vs dC=(1-C) as the two physically-meaningful slopes:
    the quasi-equilibrium slope on the fast (beta) segment and the aging slope on
    the slow (alpha) segment, each a straight-line LS fit over a dC band chosen to
    sit cleanly INSIDE its segment (away from the crossover knee at dC=1-q_EA, where
    the two relaxations overlap and the local slope interpolates between 1 and X)."""
    dC = 1.0 - C
    knee = 1.0 - q_EA
    fast = (dC > 0.04) & (dC < knee - 0.08)      # inside the beta-relaxation, off the knee
    slow = (dC > knee + 0.12) & (dC < 0.95)      # inside the alpha-relaxation, off the knee
    def slope(mask):
        x, y = dC[mask], chi[mask]
        A = np.vstack([x, np.ones_like(x)]).T
        s, _ = np.linalg.lstsq(A, y, rcond=None)[0]
        return float(s)
    return slope(fast), slope(slow), knee


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # --- the blind observables: one waiting-time window, correlation + response.
    # span: from well inside the fast beta-relaxation to well past the alpha tail,
    # log-spaced so the plateau and the stretched tail both resolve.
    tau = np.geomspace(TAU_BETA / 5.0, TAU_ALPHA * 20.0, 200)
    C, chi = kww_C_chi(tau, Q_EA, TAU_ALPHA, BETA_KWW, TAU_BETA, X)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# glass_two_step_v4 — one material, one observation (waiting-time) window.\n")
        f.write("# columns: tau (the material's own lag/clock), C (normalized\n")
        f.write("#          autocorrelation of the slow observable, C(0)=1), chi\n")
        f.write("#          (integrated step-response / susceptibility to a small field).\n")
        f.write("# All columns dimensionless. One operating point.\n")
        f.write("# Generated by the material's own relaxation-mode correlator — not via conform.\n")
        f.write("tau,C,chi\n")
        for ti, ci, xi in zip(tau, C, chi):
            f.write(f"{ti:.6f},{ci:.6f},{xi:.6f}\n")

    # --- the sealed truth (computed here from the structure; never via conform) ---
    fast_slope, slow_slope, knee = two_slope_fdr(C, chi, Q_EA)
    chi_inf_eq = 1.0                                   # what an X=1 equilibrium would give
    chi_inf = (1.0 - Q_EA) * 1.0 + Q_EA * X            # the actual plateau of chi
    T_eff_ratio = 1.0 / X                              # T_eff/T for the slow modes
    # plateau readout: C right after the fast (beta) drop, before the stretched alpha
    # erodes it — the value near q_EA. (A stretched alpha has no FLAT plateau; this is
    # the post-fast-drop shoulder, which sits just below the q_EA amplitude.)
    i_plat = int(np.argmin(np.abs(tau - 6.0 * TAU_BETA)))
    C_plateau = float(C[i_plat])

    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"substrate: KWW oracle (sum-of-OU two-timescale glass), one operating point")
    print(f"  prescribed 5-vector:")
    print(f"    q_EA (plateau / frozen fraction) = {Q_EA}")
    print(f"    tau_alpha (slow timescale)       = {TAU_ALPHA}")
    print(f"    beta_KWW (stretching, <1=stretched) = {BETA_KWW}")
    print(f"    tau_beta (fast timescale)        = {TAU_BETA}   (separation {TAU_ALPHA/TAU_BETA:.0f}x)")
    print(f"    X (slow-mode FDT-violation ratio) = {X}")
    print()
    print(f"  FDR locus chi vs (1-C) — the two-slope aging signature:")
    print(f"    fast-segment slope (quasi-equilibrium) = {fast_slope:.3f}   (expect ~1)")
    print(f"    knee at dC = 1-q_EA                     = {knee:.3f}")
    print(f"    slow-segment slope (aging)             = {slow_slope:.3f}   (expect ~X={X})")
    print(f"    => two distinct slopes: 1 then X<1. An equilibrated-slow material")
    print(f"       (X=1) would be slope 1 throughout. The slope drop IS the aging.")
    print()
    print(f"  plateau: C ~ {C_plateau:.3f} just after the fast drop (the q_EA={Q_EA} shoulder)")
    print(f"  chi(inf) actual = {chi_inf:.3f}   (an X=1 equilibrium would reach {chi_inf_eq:.3f})")
    print(f"  effective temperature of the slow modes: T_eff = T/X = {T_eff_ratio:.2f} T (hotter than bath)")
    print()
    print("PLACEMENT: glassy / aging s-regime. A two-step relaxation: fast beta-drop to a")
    print("  frozen-in plateau q_EA, then a STRETCHED (beta_KWW<1) slow alpha-relaxation; the")
    print("  slow degrees of freedom are FDT-violated at ratio X<1 (effective temperature")
    print("  T_eff=T/X > T). STABLE stationary glassy state — not crossing a transition.")
    print("NAIVE-WORRY CORRECTION: it is NOT 'just slow but in equilibrium'. The long-lag FDR")
    print("  slope is X<1, not 1 — the slow modes sit at a higher effective temperature than")
    print("  the fast ones; fluctuation-dissipation is violated in the alpha-relaxation.")
    print()
    print("GROUNDED IN-SLICE (one waiting-time window, complete honest content — WORKFLOW §4):")
    print("  the two-step C shape + the plateau q_EA, the stretching beta_KWW<1 (non-single-")
    print("  exponential tail), and the two-slope FDR locus (slope 1 then slope X<1) — the full")
    print("  5-vector is non-degenerate from this one (C, chi) pair (the segmented/5-vector fit).")
    print("NOT GROUNDED (across a COLLAPSED AXIS only — the legitimate next vector):")
    print("  whether the X<1 reflects GENUINE waiting-time-dependent aging (non-stationary, t_w-")
    print("  dependent) or a STATIONARY effective-temperature — one stationary window cannot tell")
    print("  them apart; distinguishing needs a WAITING-TIME (t_w) sweep = a collapsed axis, I2/prod.")

    # self-consistency assertions (author-side; the sealed key must hold together)
    assert np.all(np.isfinite(C)) and np.all(np.isfinite(chi)), "no NaN/inf (asymptotic-closure tripwire)"
    assert abs(fast_slope - 1.0) < 0.15, "fast-segment FDR slope must be ~1 (quasi-equilibrium)"
    assert abs(slow_slope - X) < 0.12, "slow-segment FDR slope must be ~X (the aging slope)"
    assert slow_slope < fast_slope - 0.2, "the two slopes must be DISTINCT (slope 1 then slope X<1)"
    assert 0.0 < X < 1.0, "X must be a genuine FDT violation in (0,1) — X>=1 would be a KILL"
    assert abs(C_plateau - Q_EA) < 0.08, "C must show a post-fast-drop shoulder near q_EA"
    print("\nself-consistent: finite + fast-slope~1 + slow-slope~X + distinct slopes + plateau~q_EA. OK.")
    print(f"wrote {OUT}  ({len(tau)} rows, one operating point)")


if __name__ == "__main__":
    main()
