"""freeze — laser_ro_pump_sweep_v2  (bespoke, one substrate, brittle by design)

The FIRST intent-I2 vertical: a researcher who brought a SWEEP, not one point.
The SAME canonical class-B laser, sampled at FOUR pump ratios spanning the
relaxation-oscillation Q-band — from just above the lasing threshold (sluggish,
overdamped) up through the Q-peak (crisp ring) and out onto the over-driven side
(rolling back off). This is the prod move PIPELINE.md §5 named to close the
two-sided-headroom buckle: a single point cannot carry the Q(chit) band; the sweep
measures it. (Per meta-SOP §2 a multi-point question is intent I2 — the human elected
to spend the owed prod sweep; recorded in HANDOFF.)

The physics is OUR canonical class-B laser (mpa-central/library/ro_damping_audit.py,
laser_conform_Q.py; mpa-legal Finding 5). Ground truth comes from the Jacobian
eigenvalues directly at each r — frame-invariant, never via conform (data-path
independence). For this laser (G=kappa=1, gamma_s=0.10):
    gamma_RO = gamma_s * r / 2,   omega_0 = sqrt(kappa * gamma_s * (r-1)),
    Q = omega_RO / (2 gamma_RO) peaks EXACTLY at r = 2 (Q = 1.5); the underdamped
    band is r in (r_crit ~ 1.026, ~38.97). Q -> 0 at BOTH walls (both over-damping):
    the low-drive critical-slowing wall (r -> 1) and a far high-drive wall (r ~ 39).

BLINDING: the emitted CSV carries ONLY (curve, tau, C, chi). It does NOT carry r or
any pump value — r = e^chit would let a blind conform back out the placement without
fitting, defeating data-path independence. The researcher's scale context (curve 1 =
barely lasing ... curve 4 = driven hard) lives in the packet prose, not the data.
Each curve is sampled on its OWN settling window (its slowest eigenmode decays ~8
e-foldings) — so the FRAME stage must rescale each to dimensionless lag.

Run:  python H:/mpa-conform/blockin/questions/laser_ro_pump_sweep_v2/freeze_laser_ro_pump_sweep.py

Emits:  data/laser_ro_pump_sweep_v2.frozen.csv   (curve,tau,C,chi — the blind artifact)
        prints the SEALED ground truth table (per-curve chit, gamma_RO, omega_RO,
        omega_0, Q, zeta_nat, regime) for the author to paste / the human to eyeball.
        The CSV carries NONE of it.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov
from scipy.optimize import brentq

# --- our canonical class-B laser (G = kappa = 1, slow population gamma_s << kappa)
G, KAPPA, GAMMA_S = 1.0, 1.0, 0.10

# the sweep: four pump ratios r spanning the Q-band. Curve index = drive order.
#   r=1.01  below r_crit -> OVERDAMPED, no ring (sluggish / critical-slowing wall)
#   r=1.04  just above r_crit -> just-underdamped, barely overshoots (the old v2 pt)
#   r=2.00  the Q-PEAK exactly -> crisp ring, the sweet spot
#   r=12.0  well past the peak -> ringing distinctly less crisp, Q more than halved
#           (over-driven side; still well inside the band, far wall ~r=39)
R_SWEEP = [1.01, 1.04, 2.00, 12.00]

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "laser_ro_pump_sweep_v2.frozen.csv"


def jacobian(r):
    n_star = GAMMA_S * (r - 1.0)
    J = np.array([[0.0, G * n_star], [-KAPPA, -(GAMMA_S + G * n_star)]])
    return J, n_star


def native_RO(r):
    """Exact RO observables from the Jacobian eigenvalues (dimensionless Q is
    frame-invariant). omega_0 = sqrt(det) is the undamped natural frequency;
    zeta_nat = gamma_RO/omega_0 is the critical-damping criterion (=1 at the wall)."""
    J, _ = jacobian(r)
    ev = np.linalg.eigvals(J)
    gamma_RO = float(-ev.real.mean())
    omega_RO = float(np.max(np.abs(ev.imag)))          # damped ring frequency (0 if overdamped)
    det = float(np.linalg.det(J))
    omega_0 = float(np.sqrt(det)) if det > 0 else 0.0  # undamped natural frequency
    Q = omega_RO / (2.0 * gamma_RO) if (gamma_RO > 0 and omega_RO > 0) else 0.0
    zeta_nat = gamma_RO / omega_0 if omega_0 > 0 else np.inf
    underdamped = bool(np.any(np.abs(ev.imag) > 1e-12))
    slowest_rate = float(np.min(np.abs(ev.real)))      # sets the settling window
    return gamma_RO, omega_RO, omega_0, Q, zeta_nat, underdamped, slowest_rate


def r_critical():
    """Underdamped<->overdamped transition: discriminant trace^2 - 4 det = 0."""
    def disc(r):
        n = GAMMA_S * (r - 1.0)
        tr = GAMMA_S + n
        det = KAPPA * n
        return tr * tr - 4.0 * det
    return float(brentq(disc, 1.0001, 1.5))


def C_chi(r, t):
    """C(tau) = normalized photon-number autocorrelation; chi(tau) = integrated
    impulse response (the FDR susceptibility). Linear NESS propagator."""
    J, _ = jacobian(r)
    D = np.diag([max(GAMMA_S * (r - 1.0), 1e-6), GAMMA_S])
    Sigma = solve_continuous_lyapunov(J, -2.0 * D)
    C = np.empty_like(t); Rresp = np.empty_like(t)
    for i, ti in enumerate(t):
        P = expm(J * ti)
        C[i] = (P @ Sigma)[0, 0]
        Rresp[i] = P[0, 0]
    C = C / C[0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (Rresp[1:] + Rresp[:-1]) * np.diff(t))])
    return C, chi


def overshoot_pct(zeta):
    return (np.exp(-np.pi * zeta / np.sqrt(1.0 - zeta * zeta)) * 100.0
            if 0.0 < zeta < 1.0 else 0.0)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    r_crit = r_critical()

    rows = []          # (curve, tau, C, chi) for the blind CSV
    sealed = []        # per-curve ground truth for the table
    for idx, r in enumerate(R_SWEEP, start=1):
        g, w_d, w_0, Q, zeta_nat, underdamped, slowest = native_RO(r)
        # settle each curve on its OWN window: slowest eigenmode ~8 e-foldings,
        # but at least a few ring periods where it rings (resolve the overshoot).
        t_settle = 8.0 / slowest if slowest > 0 else 8.0 / g
        t_ring = 6.0 * (2.0 * np.pi / w_d) if w_d > 0 else 0.0
        t_max = max(t_settle, t_ring)
        t = np.linspace(t_max / 400.0, t_max, 80)
        C, chi = C_chi(r, t)
        for ti, ci, xi in zip(t, C, chi):
            rows.append((idx, ti, ci, xi))
        sealed.append(dict(curve=idx, r=r, chit=float(np.log(r)), gamma_RO=g,
                           omega_RO=w_d, omega_0=w_0, Q=Q, zeta_nat=zeta_nat,
                           underdamped=underdamped, overshoot=overshoot_pct(zeta_nat)))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# laser_ro_pump_sweep_v2 — four settling curves across a pump sweep.\n")
        f.write("# columns: curve (drive-order index 1..4), tau (substrate clock),\n")
        f.write("#          C (normalized autocorr), chi (integrated response).\n")
        f.write("# C, chi dimensionless. Each curve on its own settling window.\n")
        f.write("# Generated by the laser's own linear NESS propagator — not via conform.\n")
        f.write("curve,tau,C,chi\n")
        for idx, ti, ci, xi in rows:
            f.write(f"{idx},{ti:.6f},{ci:.6f},{xi:.6f}\n")

    # which curve is the Q-peak (the sweet spot)?
    peak = max(sealed, key=lambda s: s["Q"])

    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"laser: class-B, G={G} kappa={KAPPA} gamma_s={GAMMA_S}")
    print(f"r_crit (underdamped<->overdamped wall) = {r_crit:.6f}")
    print(f"underdamped band: r in ({r_crit:.3f}, ~38.97);  Q peaks EXACTLY at r=2 (=1.5)")
    print()
    hdr = ("curve", "r", "chit", "gamma_RO", "omega_RO", "omega_0", "Q",
           "zeta_nat", "overshoot%", "regime")
    print(f"{hdr[0]:>5} {hdr[1]:>6} {hdr[2]:>8} {hdr[3]:>9} {hdr[4]:>9} "
          f"{hdr[5]:>8} {hdr[6]:>7} {hdr[7]:>9} {hdr[8]:>10}  {hdr[9]}")
    for s in sealed:
        if not s["underdamped"]:
            regime = "OVERDAMPED (no ring; sluggish / critical-slowing wall, r->1)"
        elif s["zeta_nat"] > 0.7:
            regime = "just-underdamped (barely overshoots; near the wall)"
        elif s["curve"] == peak["curve"]:
            regime = "Q-PEAK (crispest ring; the sweet spot)"
        else:
            regime = "underdamped, past the peak (over-driven; Q rolling off)"
        zn = "inf" if not np.isfinite(s["zeta_nat"]) else f"{s['zeta_nat']:.4f}"
        print(f"{s['curve']:>5} {s['r']:>6.2f} {s['chit']:>8.4f} {s['gamma_RO']:>9.4f} "
              f"{s['omega_RO']:>9.4f} {s['omega_0']:>8.4f} {s['Q']:>7.4f} "
              f"{zn:>9} {s['overshoot']:>9.2f}%  {regime}")
    print()
    print(f"SWEET SPOT: curve {peak['curve']} (r={peak['r']}, Q={peak['Q']:.4f}) — the Q-peak.")
    print("MIGRATION: curve 1 overdamped (sluggish wall) -> 2 just-underdamped -> "
          "3 Q-PEAK (crisp) -> 4 past peak (Q rolling off).")
    print("TWO-SIDED HEADROOM (now groundable from the sweep): from the low end the "
          "near wall is the critical-slowing / over-damping wall (toward r->1); the "
          "HEALTHY direction is MORE drive toward the peak; PAST the peak Q rolls back "
          "off (more drive is NOT monotonically better — there is a sweet spot).")

    # self-consistency assertions (author-side; the sealed key must hold together)
    assert not sealed[0]["underdamped"], "curve 1 (r=1.01) must be overdamped (below r_crit)"
    assert sealed[1]["underdamped"] and sealed[1]["zeta_nat"] > 0.7, \
        "curve 2 (r=1.04) must be just-underdamped, near the wall"
    assert peak["curve"] == 3 and abs(peak["r"] - 2.0) < 1e-9, "Q-peak must be curve 3 (r=2)"
    assert sealed[3]["Q"] < peak["Q"], "curve 4 (r=4) must be past the peak (Q rolled off)"
    print("\nself-consistent: overdamped@1, near-wall@2, Q-peak@3, rolled-off@4. OK.")
    print(f"wrote {OUT}  ({len(rows)} rows, {len(R_SWEEP)} curves)")


if __name__ == "__main__":
    main()
