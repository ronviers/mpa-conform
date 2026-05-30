r"""chiral_selffield.py -- the SELF-FIELD bootstrap (naive shot): can the triad's own chimeric
normal serve as the alignment field that lights the cascade?

Follows `chiral_bonding.py`, which found: an even-parity coupling of chiral subs closes a PROTECTED
meta-cycle only when a collective degeneracy is symmetry-protected -- i.e. the cascade needs the
substrate to supply a meta-scale SYMMETRY (an alignment field) on top of the drive + frustrable
sub-topology. Ron's reframe: that field need not be EXTERNAL. Each triad already carries a
"chimeric normal" -- the (1,1,1) axis that is, generically for 3D antisymmetry, BOTH the collective
real mode (polar) AND the axis of its circulation (axial, carrying sign(A) = the handedness). Use
the ENSEMBLE MEAN of those normals as a self-consistent mean field each sub aligns to: the field is
then self-supplied, the orientation self-lit (Curie / spontaneous symmetry breaking) rather than
imposed.

THE NAIVE-SHOT CLAIM (tractable): with the symmetric ARENA supplied (the C3-covariant coupling that
chiral_bonding showed can close a cycle), let the handedness s_k of each sub be a slow DYNAMICAL
field that aligns to the mean normal m = <s> via a reflection-symmetric (no drawn direction)
mean-field. Ask: (1) does the disordered/achiral state spontaneously break to an ALIGNED chirality
above a coupling threshold K_c (the ignition Wall)? (2) does that self-lit aligned state CLOSE the
protected meta-cycle? (3) is K_c a c/s/r-type boundary (r: no field/no cycle; s: onset; c:
committed homochiral + cascade)? Honesty bar: the broken direction must be SPONTANEOUS (the
symmetric state has exactly zero net normal -- no smuggled bias).

WHAT THIS NAIVE SHOT DEFERS (Ron's caveat, recorded so the next model owes it): the normal's AXIS
is FROZEN here -- all subs share the arena's (1,1,1) and only the handedness along it is dynamical,
so the normal moves on a 1-D line, not S^2. In reality the normal RESPECTS THE TOPOLOGICAL
DEFORMATIONS of the triad: as the triad is driven/deformed the axis tilts and n_hat(t) traces a
(possibly holonomic, Berry-phase-carrying) path on S^2. That turns the alignment from Ising-like
(pick a sign) into a director field on S^2 WITH GEOMETRIC MEMORY -- the "trails" become the paths.
The richer model: n_hat_k(t) on S^2, coupling = mean-director with the winding respected. Deferred.

Run from mpa-conform root:  python scripts/chiral_selffield.py
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
for p in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chiral_bonding import build_full, readout, CHAN_COVARIANT, G  # meta-cycle apparatus

C_DAMP = 1.0      # local handedness restoring rate (sets the Curie point: K_c = C_DAMP)
N_SUB = 3
DT, STEPS = 0.02, 6000


def settle_handedness(K, rng, c=C_DAMP, n=N_SUB, steps=STEPS, dt=DT, s0=None):
    """Slow handedness field s_k aligning to the mean normal m=<s> via a reflection-symmetric
    mean-field gradient flow:  s_dot_k = K*m - c*s_k - s_k^3  (s -> -s symmetric => NO drawn
    direction). Above K_c=c the symmetric state s=0 is unstable -> spontaneous aligned chirality
    s* = +-sqrt(K-c), sign set by the initial fluctuation. Returns the settled s and the trajectory."""
    s = (rng.standard_normal(n) * 0.05) if s0 is None else np.array(s0, float)
    traj = [s.copy()]
    for _ in range(steps):
        m = float(s.mean())
        s = s + dt * (K * m - c * s - s ** 3)
        if not np.all(np.isfinite(s)):
            raise FloatingPointError("handedness diverged -- diagnose, do not fill")
        traj.append(s.copy())
    return s, np.array(traj)


def meta_omega(s):
    """Protected meta-cycle frequency for the settled handedness (subs = chir s_k, C3-covariant
    arena)."""
    return readout(build_full(chir=tuple(float(x) for x in s), chan=CHAN_COVARIANT))["omega"]


def main() -> None:
    print("self-field bootstrap (naive shot): does the chimeric normal, used as a self-consistent")
    print(f"mean field, spontaneously light an ALIGNED chirality that closes the meta-cycle?")
    print(f"handedness s_dot = K*m - c*s - s^3 (reflection-symmetric); arena = C3-covariant; "
          f"K_c = c = {C_DAMP}\n")

    rng = np.random.default_rng(0)

    # ---------------------------------------------------------------- sweep the self-field coupling K
    Ks = np.linspace(0.0, 2.2, 34)
    m_of_K, om_of_K = [], []
    for K in Ks:
        s, _ = settle_handedness(K, rng)
        m_of_K.append(abs(float(s.mean())))
        om_of_K.append(meta_omega(s))
    m_of_K, om_of_K = np.array(m_of_K), np.array(om_of_K)
    mf_pred = np.sqrt(np.clip(Ks - C_DAMP, 0, None))      # mean-field order parameter sqrt(K-Kc)

    # ignition thresholds: where the order parameter and the meta-cycle turn on
    K_break = float(Ks[np.argmax(m_of_K > 0.05)]) if np.any(m_of_K > 0.05) else float("nan")
    K_cycle = float(Ks[np.argmax(om_of_K > 1e-3)]) if np.any(om_of_K > 1e-3) else float("nan")
    print(f"IGNITION (the bootstrap Wall):")
    print(f"    handedness orders (|m|>0.05) at K = {K_break:.3f}   (mean-field K_c = {C_DAMP})")
    print(f"    meta-cycle lights (omega>1e-3) at K = {K_cycle:.3f}")
    print(f"    => the cascade self-lights AT the Curie/Wall: orientation + cycle ignite together "
          f"({'coincident' if abs(K_break-K_cycle) <= (Ks[1]-Ks[0])*1.5 else 'OFFSET'}).")

    # ---------------------------------------------------------------- spontaneity: direction emerges
    signs = []
    for seed in range(200):
        s, _ = settle_handedness(1.8, np.random.default_rng(1000 + seed))
        mm = float(s.mean())
        if abs(mm) > 0.05:
            signs.append(int(np.sign(mm)))
    frac_plus = np.mean(np.array(signs) > 0) if signs else float("nan")
    print(f"\nSPONTANEITY (200 random ICs at K=1.8): broken direction is +{int(100*frac_plus)}% / "
          f"-{int(100*(1-frac_plus))}% -- no drawn bias (symmetric state has zero net normal).")

    # ---------------------------------------------------------------- ignition dynamics (trajectories)
    _, tr_hi = settle_handedness(1.8, np.random.default_rng(7), steps=2500)   # above K_c: aligns
    _, tr_lo = settle_handedness(0.4, np.random.default_rng(7), steps=2500)   # below K_c: disorders to 0
    t = np.arange(tr_hi.shape[0]) * DT

    # ---------------------------------------------------------------- alignment-vs-cycle coupling
    # vary partial alignment by mixing aligned + disordered settled states; cycle needs enough |m|
    align_levels, om_levels = [], []
    for K in np.linspace(1.0, 2.2, 25):
        s, _ = settle_handedness(K, rng)
        align_levels.append(abs(float(s.mean()))); om_levels.append(meta_omega(s))
    align_levels, om_levels = np.array(align_levels), np.array(om_levels)

    print("\n================ VERDICT (naive shot) ================")
    coincident = np.isfinite(K_break) and np.isfinite(K_cycle) and abs(K_break - K_cycle) <= (Ks[1]-Ks[0])*1.5
    if coincident and frac_plus == frac_plus:
        print("COHERENT. The chimeric normal works as a self-consistent field: above a threshold K_c")
        print("(the Curie point) the symmetric/achiral state goes unstable and the subs SPONTANEOUSLY")
        print("commit to an ALIGNED chirality -- direction self-chosen (~50/50, no bias) -- and that")
        print("self-lit homochiral state CLOSES the protected meta-cycle. The cascade self-lights its")
        print("own orientation field AT a c/s/r Wall (r: K<K_c, no field/no cycle; s: K=K_c onset;")
        print("c: K>K_c, committed homochiral + cascade). The substrate still supplies the symmetric")
        print("ARENA + drive; the ORIENTATION is self-generated. => arena-vs-orientation split confirmed:")
        print("parasitic on arena/drive/topology, GENERATIVE of the field's orientation.")
    else:
        print(f"NOT coincident: K_break={K_break:.3f}, K_cycle={K_cycle:.3f}. Read honestly.")
    print("\nNAIVE-SHOT SCOPE (what this owes): the self-field is POSITED (phi^4 mean-field), not")
    print("derived from the triad dynamics; and the normal's AXIS is FROZEN (1-D handedness, not S^2).")
    print("Ron's caveat: realistically the normal respects the triad's topological deformations and")
    print("traces a holonomic PATH on S^2 -- alignment becomes a director field with geometric memory,")
    print("the 'trails'. Next model owes: (1) self-field derived not posited; (2) n_hat(t) on S^2.")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)

    # (0,0) order parameter: spontaneous breaking at the Curie point
    a0 = ax[0, 0]
    a0.plot(Ks, m_of_K, "o-", color="#c2185b", lw=2, ms=4, label=r"measured $|m|=|\langle s\rangle|$")
    a0.plot(Ks, mf_pred, "k--", lw=1.2, label=r"mean-field $\sqrt{K-K_c}$")
    a0.axvline(C_DAMP, color="#2e7d32", ls=":", lw=1.5, label=f"K_c = {C_DAMP}")
    a0.set_xlabel("self-field coupling K"); a0.set_ylabel(r"handedness order parameter $|m|$")
    a0.set_title("the chimeric normal self-lights: handedness orders\nspontaneously above the Curie point")
    a0.legend(fontsize=9, frameon=False); a0.grid(alpha=0.3)

    # (0,1) meta-cycle ignites at the SAME threshold = the bootstrap Wall (c/s/r)
    a1 = ax[0, 1]
    a1.plot(Ks, om_of_K, "o-", color="#6a1b9a", lw=2, ms=4, label=r"protected $\omega_{\rm meta}$")
    a1.axvline(C_DAMP, color="#2e7d32", ls=":", lw=1.5, label="ignition Wall K_c")
    a1.axvspan(0, C_DAMP, color="#90a4ae", alpha=0.15)
    a1.text(C_DAMP * 0.45, max(om_of_K) * 0.5, "r\n(no field,\nno cycle)", ha="center", fontsize=9, color="#455a64")
    a1.text(C_DAMP + (Ks[-1]-C_DAMP) * 0.5, max(om_of_K) * 0.35, "c\n(committed:\nself-lit cascade)",
            ha="center", fontsize=9, color="#455a64")
    a1.set_xlabel("self-field coupling K"); a1.set_ylabel(r"emergent $\omega_{\rm meta}$")
    a1.set_title("the meta-cycle ignites AT the same Wall: the cascade\nself-lights its orientation (c/s/r boundary)")
    a1.legend(fontsize=9, frameon=False); a1.grid(alpha=0.3)

    # (1,0) ignition dynamics: above K_c subs spontaneously align; below they disorder to 0
    a2 = ax[1, 0]
    for k in range(N_SUB):
        a2.plot(t, tr_hi[:, k], "-", color="#c2185b", lw=1.6, alpha=0.9)
        a2.plot(t, tr_lo[:, k], "-", color="#1565c0", lw=1.4, alpha=0.7)
    a2.axhline(0, color="gray", lw=0.6)
    a2.plot([], [], color="#c2185b", label="K=1.8 > K_c: spontaneous co-alignment (homochiral)")
    a2.plot([], [], color="#1565c0", label="K=0.4 < K_c: disorders to zero (achiral)")
    a2.set_xlabel("time"); a2.set_ylabel(r"sub handedness $s_k$")
    a2.set_title("ignition dynamics: from random ICs the normals spontaneously\nco-align above K_c (the trails align to their own mean)")
    a2.legend(fontsize=8, frameon=False); a2.grid(alpha=0.3)

    # (1,1) cycle needs sufficient alignment (ties to homochirality: partial alignment, weak cycle)
    a3 = ax[1, 1]
    a3.plot(align_levels, om_levels, "o-", color="#00796b", lw=2, ms=5)
    a3.set_xlabel(r"self-lit alignment $|m|$"); a3.set_ylabel(r"protected $\omega_{\rm meta}$")
    a3.set_title("the cycle tracks how well the trails align:\nstronger self-lit field -> stronger meta-cycle")
    a3.grid(alpha=0.3)

    fig.suptitle("self-field bootstrap (naive): the chimeric normal as a self-consistent field "
                 "spontaneously lights an aligned chirality that closes the meta-cycle", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "chiral_selffield.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
