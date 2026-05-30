r"""library_chiral_screen.py -- screen the mpa-central library for a substrate that could close
`frustration-ascent`: spontaneous chiral SSB + protected INTERNAL cyclic current + a GAPPED (far-from-EP,
non-Goldstone) chiral mode. (Sharpened criterion from `mpa-atlas/docs/cascade research and prompt.md`.)

The four requirements (a substrate must satisfy ALL to be usable):
  (a) SPONTANEOUS chiral/parity SSB (handedness self-selected, not built-in / drawn by the drive sign);
  (b) a PROTECTED cyclic current (a directed loop / NESS circulation), not a relaxational flow;
  (c) INTERNAL-cycle (rotation in order-parameter / state space), not physical real-space rotation;
  (d) a GAPPED chiral mode: the rotating pair's damping Re(lambda_chiral) is comparable to the
      longitudinal damping (far from the exceptional point / marginal), NOT a soft near-Goldstone mode
      (Re -> 0) -- that softness is what made the homochiral cascade tilt-brittle (#1).

This screens the two INTERNAL-cycle library primitives by their deterministic mean-field linearization
(the only ones that even carry a state-space cycle):
  - lotka_volterra : the coexistence fixed point Jacobian is [[0, -beta*gamma/delta],[delta*alpha/beta, 0]]
                     -> eigenvalues +- i*sqrt(alpha*gamma), Re = 0 EXACTLY: a conservative CENTER = the
                     maximally-soft (marginal) chiral mode = the fragile extreme. Fails (d) maximally; the
                     predator-prey loop direction is structural, not spontaneous -> fails (a) too.
  - driven_ring    : 1D tilted washboard, running current v=sign(F)*sqrt(F^2-A^2) for |F|>A. Direction is
                     EXPLICIT (sign F) -> fails (a); 1D phase -> no chiral PLANE / no rotating pair (c/d N/A).
The rest of the library carries no internal chiral cycle (sk, voter, fbm, sir, east, wright_fisher,
heston, levy_flight, logistic_chaos, ising/ou/two_temp_ou) or is physical-rotation/explicit (abp).

Reference (the robust target): the dimensionless Banach -I + g*A_CYC -> eigenvalues -1, -1 +- i*sqrt3*g:
a GAPPED chiral pair (Re = -1, far from marginal) -- passes (d), but synthetic (drawn-in chirality).

Usage (from mpa-conform root):  python scripts/library_chiral_screen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)
A_CYC = np.array([[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]])


def lv_jacobian(alpha, beta, gamma, delta):
    """Lotka-Volterra mean-field Jacobian at the coexistence fixed point (X*=gamma/delta, Y*=alpha/beta,
    in units of N). J = [[0, -beta*gamma/delta],[delta*alpha/beta, 0]] -> eigenvalues +- i sqrt(alpha*gamma)."""
    return np.array([[0.0, -beta * gamma / delta], [delta * alpha / beta, 0.0]])


def chiral_gap(M):
    """Re of the dominant complex (rotating) pair; None if no complex pair. The gap = how far the chiral
    mode is from marginal (Re=0 = soft/Goldstone; Re<<0 = gapped/robust)."""
    ev = np.linalg.eigvals(M)
    cpx = ev[np.abs(ev.imag) > 1e-9]
    if len(cpx) == 0:
        return None, ev
    j = int(np.argmax(np.abs(cpx.imag)))
    return float(cpx[j].real), ev


def main():
    print("LIBRARY CHIRAL SCREEN -- is there a usable substrate (spontaneous SSB + gapped internal chiral mode)?\n")
    print("criterion: (a) spontaneous chiral SSB  (b) protected cyclic current  (c) internal-cycle"
          "  (d) GAPPED chiral mode (far from EP, not soft Goldstone)\n")

    # ---- lotka_volterra across its grind operating points ----
    print("LOTKA-VOLTERRA (internal predator-prey cycle) -- deterministic Jacobian at coexistence:")
    print(f"   {'alpha':>6} {'eigenvalues':>26} {'Re(chiral)':>11}  verdict")
    lv_gaps = []
    for alpha in (0.5, 0.8, 1.0, 1.2, 1.6):
        M = lv_jacobian(alpha, 1.0, 1.0, 1.0)
        re, ev = chiral_gap(M)
        lv_gaps.append(re)
        print(f"   {alpha:>6.2f} {np.array2string(ev, precision=3):>26} {re:>+11.3f}  "
              f"{'MARGINAL (soft/Goldstone) -> FRAGILE' if abs(re) < 1e-9 else 'gapped'}")
    lv_marginal = bool(all(abs(g) < 1e-9 for g in lv_gaps))
    print(f"   => LV chiral mode is a CONSERVATIVE CENTER at every operating point (Re=0 exactly):"
          f" maximally SOFT. marginal={lv_marginal}")
    print("   => fails (d) maximally; the predator-prey loop direction is structural (not spontaneous) -> fails (a).\n")

    # ---- driven_ring ----
    A, F = 1.0, 2.0
    v = np.sign(F) * np.sqrt(max(F * F - A * A, 0.0))
    print(f"DRIVEN_RING (1D tilted washboard) -- running current v = sign(F)*sqrt(F^2-A^2) = {v:+.3f} for F={F}>A={A}")
    print("   => direction is EXPLICIT (set by sign F) -> fails (a); 1D phase -> no chiral PLANE / no rotating pair (c/d N/A).\n")

    # ---- reference: the robust (but synthetic) target ----
    Mban = -1.0 * np.eye(3) + 0.1 * A_CYC
    re_ban, ev_ban = chiral_gap(Mban)
    print(f"REFERENCE -- dimensionless Banach (-I + 0.1 A_CYC): eigenvalues {np.array2string(ev_ban, precision=3)}, "
          f"Re(chiral)={re_ban:+.2f}")
    print("   => GAPPED chiral pair (passes d), but chirality is drawn-in (synthetic, fails the real/emergent gate).\n")

    # ---- the screen table (structural classification of the whole library) ----
    print("=" * 90)
    print("SCREEN TABLE (whole library):  substrate | (a) spont-SSB | (b) cyclic | (c) internal | (d) gapped")
    print("=" * 90)
    table = [
        ("lotka_volterra", "no (structural dir)", "yes", "yes", "NO (marginal center)"),
        ("driven_ring",    "no (sign F)",         "yes (1D)", "yes", "n/a (1D, no plane)"),
        ("abp",            "no (explicit/torque)","yes",  "no (physical rot.)", "-"),
        ("sk / voter / fbm / sir / east / wright_fisher / heston / levy_flight / logistic_chaos / ising / ou / two_temp_ou",
                           "no", "no internal chiral cycle", "-", "-"),
        ("[dimensionless Banach: ref]", "no (drawn-in)", "yes", "yes", "YES (gapped) -- but synthetic"),
        ("[homochiral triad: what we built]", "YES (Frank SSB)", "yes", "yes", "NO (weakly-damped plane = #1 miss)"),
    ]
    for row in table:
        print(f"  {row[0]}")
        print(f"       a={row[1]:<22} b={row[2]:<26} c={row[3]:<20} d={row[4]}")

    figure(lv_gaps, re_ban)

    print("\n" + "=" * 90)
    print("VERDICT -- the library is RULED OUT (clean negative)")
    print("=" * 90)
    print("  No library substrate satisfies even (a) spontaneous chiral SSB into an internal cycle. The two")
    print("  internal-cycle primitives are the FAILURE archetypes for the two halves of the gap:")
    print("    - lotka_volterra: a CONSERVATIVE CENTER (Re=0) = the maximally-soft / near-Goldstone chiral")
    print("      mode = the fragile extreme criterion (d) is meant to exclude (and its loop is not spontaneous).")
    print("    - driven_ring: a running current whose direction is DRAWN IN (sign F), 1D, no chiral plane.")
    print("  Neither self-lights; LV is exactly the marginal-mode pathology. ⇒ the library cannot close")
    print("  frustration-ascent; the EXTERNAL hunt for a real emergent substrate with a SPONTANEOUS chiral")
    print("  SSB AND a GAPPED (far-from-EP) internal chiral mode is the only path. The screen also confirms")
    print("  criterion (d) discriminates: LV (Re=0, fragile) vs Banach (Re=-1, gapped) are cleanly separated.")


def figure(lv_gaps, re_ban):
    fig, ax = plt.subplots(1, 1, figsize=(7.5, 5.5), dpi=150)
    # LV eigenvalues (on the imaginary axis = marginal) across operating points
    for alpha, c in zip((0.5, 0.8, 1.0, 1.2, 1.6), plt.cm.viridis(np.linspace(0, 0.85, 5))):
        ev = np.linalg.eigvals(lv_jacobian(alpha, 1.0, 1.0, 1.0))
        ax.scatter(ev.real, ev.imag, s=90, color=c, zorder=3,
                   label=f"LV α={alpha} (Re=0, marginal)" if alpha in (0.5, 1.6) else None)
    # Banach reference (gapped, Re=-1)
    evb = np.linalg.eigvals(-1.0 * np.eye(3) + 0.1 * A_CYC)
    ax.scatter(evb.real, evb.imag, s=120, marker="s", color="#2e7d32", zorder=3,
               edgecolor="white", label="Banach ref (Re=-1, GAPPED)")
    ax.axvline(0, color="#c62828", ls="--", lw=1.5, label="marginal line (soft/Goldstone)")
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_xlabel("Re(λ)  — chiral-mode damping (gap)"); ax.set_ylabel("Im(λ)  — rotation rate")
    ax.set_title("library screen: every Lotka-Volterra operating point sits ON the marginal line\n"
                 "(soft/Goldstone chiral mode = fragile); a usable substrate needs Re(λ_chiral) ≪ 0 (gapped)",
                 fontsize=10.5)
    ax.set_xlim(-1.3, 0.6)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = OUT / "library_chiral_screen.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
