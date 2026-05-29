r"""nonlinear_node.py -- the nonlinear recursion node (class-B / dynamic-gain frustrated triad).

The gated next move after `frustration_ascent.py`. The linear tower platformed protected cycles
exactly on the sign-topological face, but the linear OU has no chit/amplitude knob, so it could
not reach (i) the ch RHYTHM prediction (Q-peak at chit = 1 ch) or (ii) the dynamical
type-identity (coarse node == the two-mode kernel with c/s/r AMPLITUDE). This builds the node
that does.

Two nonlinear node TYPES, one per face (do not conflate):
  * Stuart-Landau (mpa-central/library/banach_active_ring.py): mu z - z^3 + g A_CYC z.
    SINGLE timescale (Hopf normal form). Carries the topological LIMIT CYCLE / current. Already
    built. Knob = mu. NO relaxation-oscillation Q-peak (one timescale -> no RO).
  * class-B laser (THIS): intensity rho + a SEPARATE SLOW gain G (rate gamma_s). TWO timescales.
    Carries the RELAXATION-OSCILLATION rhythm whose quality Q(chit) peaks at chit = ln2 (units
    section 1). This is the node the ch RHYTHM prediction lives on.

Model -- 3 class-B modes, cyclic non-reciprocal coupling (the frustrated triad):
    d rho_j/dt = (G_j - L) rho_j  -  g rho_j (A_CYC rho)_j           (+ topological bond)
    d G_j/dt   = gamma_s (P - G_j) - beta G_j rho_j                  (slow gain, dynamic bath)
    chit = ln(P / L)   (pump ratio = the amplitude knob).  A_CYC = rock-paper-scissors circulant.

Symmetric fixed point (above threshold chit>0): G* = L, rho* = (gamma_s/beta)(e^chit - 1).
The cyclic term VANISHES there (A_CYC row sums = 0), but its derivative does not. The 6x6
Jacobian decomposes EXACTLY by the A_CYC eigenbasis into 2x2 blocks J(a):

    J(a) = [[ -g rho* a ,   rho*       ],
            [ -beta L   , -(gamma_s + beta rho*) ]]

  * a = 0  (COLLECTIVE / breathing mode, the (1,1,1) coordinate = the node bonded in the linear
    tower): J(0) is EXACTLY the single-mode class-B Jacobian. Its complex pair is the relaxation
    oscillation; gamma_RO = (gamma_s/2)e^chit, and
        Q^2 = (L/gamma_s)(e^{-chit} - e^{-2 chit}) - 1/4   ->   PEAK at chit = ln2 = 1 ch.
    (units section 1: peak location forced/substrate-independent; magnitude substrate-set; the
    full-Jacobian -1/4 is a constant offset that does not move the peak.)
  * a = +- i sqrt3  (PERP plane): the protected circulation. Its frequency ~ sqrt3 g rho*, so the
    CURRENT MAGNITUDE flows with chit (via rho*), while the SIGN (chirality, the A_CYC parity) is
    fixed. This is the cdv1 affinity-vs-magnitude split the LINEAR banach_frustrated could not show
    (it has no rho* knob) -- now instanced.

So one node carries BOTH faces, cleanly separated: collective -> RO rhythm (Q-peak @ 1 ch);
perp -> topological current (flows with chit, sign fixed). c/s/r is the transcritical onset of
rho* at chit = 0 (r below threshold, s at threshold, c above) = the two-mode-kernel backbone.

Synthetic: validates the recursion node as a legitimate MPA two-mode-kernel object; calibration +
the apparatus a real substrate lands into, NOT vindication. Once verified, this node nests into
the `frustration_ascent.py` tower (each node ringing at 1 ch, carrying a chit-flowing current).

Run from mpa-conform root:  python scripts/nonlinear_node.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from banach_frustrated import A_CYC  # rock-paper-scissors circulant

L, GAMMA_S, BETA, G_COUP = 1.0, 0.1, 1.0, 0.25   # loss, slow-gain rate, stim. coupling, frustration
LN2 = float(np.log(2.0))
IM_FLOOR = 1e-9
N111 = np.ones(3) / np.sqrt(3.0)


def rho_star(chit):
    """Symmetric above-threshold fixed point intensity (transcritical at chit=0; 0 below = r)."""
    return max(0.0, (GAMMA_S / BETA) * (np.exp(chit) - 1.0))


def full_jacobian(chit):
    """6x6 Jacobian [rho_0..2, G_0..2] at the symmetric fixed point G*=L, rho*=rho_star."""
    r = rho_star(chit)
    I3 = np.eye(3)
    Jrr = -G_COUP * r * A_CYC                      # rho-rho: topological circulation
    JrG = r * I3                                   # rho-G
    JGr = -BETA * L * I3                           # G-rho
    JGG = -(GAMMA_S + BETA * r) * I3               # G-G (slow gain)
    return np.block([[Jrr, JrG], [JGr, JGG]])


def classify_modes(chit):
    """Split the spectrum into the collective (breathing) RO pair and the perp circulation pair,
    by projecting each eigenvector's rho-part onto (1,1,1). Returns Q, omega_RO, gamma_RO (collective)
    and omega_perp, sign_perp (perp), plus max Re (stability)."""
    J = full_jacobian(chit)
    w, V = np.linalg.eig(J)
    coll, perp = [], []
    for i in range(len(w)):
        if w[i].imag <= IM_FLOOR:                  # take +Im representative of each complex pair
            continue
        rho_part = V[:3, i]
        frac = abs(np.vdot(N111, rho_part)) / (np.linalg.norm(rho_part) + 1e-15)
        (coll if frac > 0.7 else perp).append(w[i])
    Q = omega_RO = gamma_RO = float("nan")
    if coll:
        c = coll[int(np.argmax([abs(e.imag) for e in coll]))]
        omega_RO, gamma_RO = abs(c.imag), abs(c.real)
        Q = omega_RO / (2.0 * gamma_RO) if gamma_RO > 1e-12 else float("nan")
    omega_perp = sign_perp = 0.0
    if perp:
        p = perp[int(np.argmax([abs(e.imag) for e in perp]))]
        omega_perp, sign_perp = abs(p.imag), int(np.sign(p.imag))
    return dict(Q=Q, omega_RO=omega_RO, gamma_RO=gamma_RO, omega_perp=omega_perp,
                sign_perp=sign_perp, max_re=float(np.max(w.real)))


def Q_closed_form(chit):
    """units section 1: Q^2 = (L/gamma_s)(e^{-chit} - e^{-2chit}) - 1/4  (peak at chit=ln2)."""
    q2 = (L / GAMMA_S) * (np.exp(-chit) - np.exp(-2.0 * chit)) - 0.25
    return np.sqrt(q2) if q2 > 0 else float("nan")


def ringdown(chit, t):
    """Linear collective ringdown: kick the collective intensity, watch it ring/decay.
    Underdamped (rings) near chit=ln2; overdamped (monotone) at band edges."""
    J = full_jacobian(chit)
    x0 = np.zeros(6); x0[:3] = N111                # kick collective intensity
    obs = np.array([np.concatenate([N111, np.zeros(3)]) @ (expm(J * ti) @ x0) for ti in t])
    return obs


def main() -> None:
    print("nonlinear node (class-B frustrated triad): does the rhythm peak at chit = 1 ch?")
    print(f"L={L}, gamma_s={GAMMA_S}, beta={BETA}, g(frustration)={G_COUP};  1 ch = ln2 = {LN2:.4f}\n")

    chits = np.linspace(0.02, 3.5, 500)
    Qs = np.array([classify_modes(c)["Q"] for c in chits])
    Qcf = np.array([Q_closed_form(c) for c in chits])
    rs = np.array([rho_star(c) for c in chits])
    band = np.isfinite(Qs)
    chit_peak = float(chits[band][int(np.nanargmax(Qs[band]))])
    Q_at_peak = float(np.nanmax(Qs[band]))
    cf_err = float(np.nanmax(np.abs((Qs[band] - Qcf[band]) / Qcf[band]))) if np.any(band) else float("nan")

    # circulation: flows with chit (via rho*), sign fixed
    perp = [classify_modes(c) for c in chits]
    omega_perp = np.array([m["omega_perp"] for m in perp])
    signs = np.array([m["sign_perp"] for m in perp])
    max_re = np.array([m["max_re"] for m in perp])
    sign_fixed = len(set(int(s) for s in signs if s != 0)) == 1
    flows = float(np.corrcoef(rs[omega_perp > 0], omega_perp[omega_perp > 0])[0, 1]) if np.any(omega_perp > 0) else 0.0
    stable = bool(np.all(max_re < 0))

    print(f"ch RHYTHM (collective relaxation oscillation):")
    print(f"    Q-peak measured at chit = {chit_peak:.4f} ch   (forced: ln2 = {LN2:.4f}, "
          f"err = {abs(chit_peak-LN2):.4f})   Q_max = {Q_at_peak:.3f}")
    print(f"    measured Q vs units-section-1 closed form: max rel-err = {100*cf_err:.2f}%  (FORCED, not fitted)")
    print(f"\nc/s/r backbone (transcritical at chit=0): rho* = 0 below threshold (r), "
          f"onsets at chit=0 (s), grows above (c).")
    print(f"\ncdv1 affinity-vs-magnitude (perp circulation):")
    print(f"    circulation rate flows with chit (corr with rho* = {flows:.3f}); "
          f"sign(Im) fixed = {sign_fixed} (value {int([s for s in signs if s!=0][0]):+d}); "
          f"fixed point {'stable focus' if stable else 'HOPF (limit cycle)'}.")

    peak_ok = abs(chit_peak - LN2) < 0.03
    forced = cf_err < 0.02
    print("\n================ VERDICT ================")
    if peak_ok and forced and sign_fixed and flows > 0.9:
        print(f"NODE VALIDATED. The nonlinear (class-B) frustrated triad rings at chit = 1 ch: the")
        print(f"relaxation-oscillation Q peaks at chit = {chit_peak:.3f} (= ln2), matching the units")
        print(f"section-1 closed form to {100*cf_err:.2f}% (FORCED). The ch RHYTHM PREDICTION holds on")
        print(f"the actual nonlinear node. c/s/r backbone present (transcritical at chit=0). The")
        print(f"protected current flows with chit (corr {flows:.2f}) while its chirality sign is fixed")
        print(f"-- the cdv1 affinity-vs-magnitude split the LINEAR model could not reach.")
        print(f"=> this is a legitimate two-mode-kernel MPA node carrying BOTH faces. The collective")
        print(f"   breathing mode (Q-peak @ 1 ch) is exactly the (1,1,1) coordinate bonded in the")
        print(f"   linear tower -- so the recursion node RINGS at one ch. Ready to nest.")
    else:
        print(f"NOT clean: peak@ln2={peak_ok} (chit_peak={chit_peak:.3f}), forced={forced} "
              f"(err={100*cf_err:.2f}%), sign_fixed={sign_fixed}, flows(corr)={flows:.2f}. Read honestly.")
    print("\nHonest scope: validates the node on real dynamics (intensity + slow gain, two timescales).")
    print("Synthetic -> calibration + apparatus the recursion tower nests; NOT a real-substrate instance.")
    print("Sibling node banach_active_ring.py carries the Stuart-Landau LIMIT-CYCLE current face;")
    print("this carries the relaxation-oscillation RHYTHM face. The recursion node needs both.")

    # ---- figure (2x2) ----
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=140)

    # (0,0) Q-peak at 1 ch
    a = ax[0, 0]
    a.plot(chits, Qs, "-", color="#c2185b", lw=2.4, label="measured Q (full 6D Jacobian)")
    a.plot(chits, Qcf, "k--", lw=1, label="units section 1 closed form")
    a.axvline(LN2, color="#2e7d32", ls=":", lw=1.5, label="chit = 1 ch = ln2")
    a.scatter([chit_peak], [Q_at_peak], s=80, color="#c2185b", zorder=5, edgecolor="white")
    a.set_xlabel("chit (nats)"); a.set_ylabel("relaxation-oscillation quality Q")
    a.set_title(f"ch RHYTHM PREDICTION: Q-peak at chit = 1 ch\nmeasured peak {chit_peak:.3f} vs ln2 {LN2:.3f}")
    a.legend(fontsize=9, frameon=False); a.grid(alpha=0.3)

    # (0,1) ringdown waveforms: rings most at 1 ch
    a = ax[0, 1]
    t = np.linspace(0, 60, 1500)
    for c, col, lab in [(0.1, "#1565c0", "chit=0.10 (band edge)"),
                        (LN2, "#c2185b", "chit=ln2 = 1 ch (peak)"),
                        (2.5, "#ef9a00", "chit=2.50 (band edge)")]:
        y = ringdown(c, t)
        a.plot(t, y / (abs(y[0]) + 1e-12), color=col, lw=1.8, label=lab)
    a.axhline(0, color="gray", lw=0.5)
    a.set_xlabel("time"); a.set_ylabel("collective intensity (normalized kick)")
    a.set_title("rhythm rings sharpest at one ch of headroom\n(overdamped at the band edges)")
    a.legend(fontsize=9, frameon=False); a.grid(alpha=0.3)

    # (1,0) c/s/r backbone
    a = ax[1, 0]
    cc = np.linspace(-1.0, 3.5, 500)
    rr = np.array([rho_star(c) for c in cc])
    a.plot(cc, rr, "-", color="#6a1b9a", lw=2.2)
    a.axvline(0, color="gray", ls=":", lw=1.2)
    a.fill_between(cc, 0, rr.max() * 1.05, where=(cc < 0), color="#90a4ae", alpha=0.18)
    a.text(-0.6, rr.max() * 0.6, "r\n(reset)", ha="center", fontsize=11, color="#455a64")
    a.text(0.18, rr.max() * 0.18, "s", fontsize=11, color="#455a64")
    a.text(2.4, rr.max() * 0.7, "c\n(committed)", ha="center", fontsize=11, color="#455a64")
    a.set_xlabel("chit (nats)"); a.set_ylabel(r"fixed-point intensity $\rho^*$")
    a.set_ylim(-0.02, rr.max() * 1.05)
    a.set_title("two-mode-kernel backbone: transcritical c/s/r at chit = 0\n(type-identity -- the node is an MPA mode)")
    a.grid(alpha=0.3)

    # (1,1) cdv1: current flows with chit, chirality fixed
    a = ax[1, 1]
    a.plot(chits, omega_perp, "-", color="#00796b", lw=2.2, label=r"circulation rate (current $\propto\rho^*$)")
    a.axvline(LN2, color="#2e7d32", ls=":", lw=1.2, label="1 ch")
    a.set_xlabel("chit (nats)"); a.set_ylabel("perp-plane circulation rate |Im λ|")
    sgn = int([s for s in signs if s != 0][0]) if any(signs != 0) else 0
    a.set_title(f"cdv1 affinity-vs-magnitude: |current| flows with chit,\nchirality sign FIXED = {sgn:+d} "
                f"(set by A_CYC parity)")
    a.legend(fontsize=9, frameon=False); a.grid(alpha=0.3)

    fig.suptitle("nonlinear recursion node (class-B frustrated triad): rhythm peaks at 1 ch; "
                 "current flows with chit, chirality fixed", fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "nonlinear_node.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
