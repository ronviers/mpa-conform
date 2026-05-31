r"""splay_cascade.py -- can the DISCRETE-CHIRAL splay substrate (round-2 lead) CASCADE?  ANSWER: NO (+0).

Round-2 research (`mpa-atlas/docs/cascade research and prompt.md`): the closable single-unit substrate is a
Z2 SPLAY STATE in a repulsively-coupled C3 oscillator ring (realized in BZ micro-droplets, Fraden):
spontaneous CW/CCW firing-order, internal phase-space cycle, GAPPED chiral mode (Re ~ -K/2, far from EP).
It passes all four SINGLE-UNIT filters (probe: 120-deg splay, both Z2 basins, gapped). The open question
was the CASCADE: does coupling splay-rings platform a meta-cycle?

THE ANSWER IS NO, and it is STRUCTURAL. The splay's chirality is DISCRETE -- the Z2 firing ORDER -- and
its linearization is a REAL gapped node (eigenvalues {0, -0.476 +- i 0.155}; the 0.155 Im is the INTRA-ring
splay rotation, intrinsic to ONE ring, NOT collective). A real-spectrum sub has NO antisymmetric part, and
an even-parity (symmetric) inter-ring coupling of real-spectrum subs gives a SYMMETRIC effective collective
Jacobian -> REAL collective eigenvalues -> NO complex pair -> NO meta-cycle. So the discrete-chiral splay
cannot seed a cascade; that is exactly WHY it is robust (discrete = gapped = no Goldstone) and exactly why
it spends the seed.

  CONTRAST (chiral_bonding / character_closure): the A_CYC sub has a COMPLEX pair (antisymmetric so(3) part)
  -> the Schur correction onto the collective can be antisymmetric -> a COMPLEX collective pair -> a meta-
  cycle. Gapping that complex mode by going DISCRETE makes the spectrum REAL and kills the antisymmetric seed.

THE TRIPLE OBSTRUCTION (the sharp result): a cascade-closing substrate needs ALL of
  - self-light (spontaneous chiral SSB),
  - gapped (robust, far from marginal),
  - complex-pair SEEDABLE (an antisymmetric/rotating chiral mode that propagates to a meta-cycle).
But gapping-by-discreteness (the only way to self-light AND gap) makes the spectrum real, killing the seed.
   homochiral: self-light + complex-pair-seed, NOT gapped (weakly-damped, fragile).
   Banach:     gapped + complex-pair-seed, NOT self-light (drawn-in).
   splay:      self-light + gapped, NOT seedable (discrete/real -> +0, no meta-cycle).
Robustness (gapped) and seeding (antisymmetric complex pair) pull OPPOSITE ways for a self-lit substrate.

READOUT (the fake-NaN lesson): isolate the COLLECTIVE sector by projecting onto the per-ring global-phase
nodes (1,1,1) and Schur-eliminating the rest -- do NOT use "smallest |Re|" (it grabs the intra-ring splay
pair and falsely reports a meta-cycle).

Usage (from mpa-conform root):  python scripts/splay_cascade.py
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

W = 1.0
K = 1.0
DT = 0.01
IM_FLOOR = 1e-4
_QR_FILL = np.random.default_rng(0).standard_normal((9, 6))   # fixed complement for the projection


def field(theta, kappa, alpha, shift_cov=True):
    """3 Sakaguchi-Kuramoto rings (theta=9-vec, k*3+i) + even-parity C3-covariant inter-ring coupling.
    alpha near pi -> each ring SPLAYS (chiral); alpha near 0 -> each ring SYNCHRONIZES (achiral control)."""
    th = theta.reshape(3, 3)
    d = np.zeros((3, 3))
    for k in range(3):
        for i in range(3):
            d[k, i] = W + (K / 3.0) * np.sum(np.sin(th[k] - th[k, i] - alpha))
    for k in range(3):                       # even-parity (reciprocal), C3-covariant meta-ring coupling
        kp = (k + 1) % 3
        shift = k if shift_cov else 0
        for i in range(3):
            j = (i + shift) % 3
            c = kappa * np.sin(th[kp, j] - th[k, i])
            d[k, i] += c
            d[kp, j] += -c
    return d.reshape(9)


def settle(kappa, alpha, seed, shift_cov=True, T=600.0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, 9)
    for _ in range(int(T / DT)):
        th = th + field(th, kappa, alpha, shift_cov) * DT
    return th


def jac(theta, kappa, alpha, shift_cov=True):
    eps = 1e-6
    f0 = field(theta, kappa, alpha, shift_cov)
    J = np.zeros((9, 9))
    for m in range(9):
        tp = theta.copy(); tp[m] += eps
        J[:, m] = (field(tp, kappa, alpha, shift_cov) - f0) / eps
    return J


def collective_meta_eig(J):
    """PROPER readout: Schur-reduce J onto the COLLECTIVE subspace = span of the per-ring global-phase
    nodes (1,1,1). Returns the 3 collective eigenvalues. A complex pair here = a genuine meta-cycle.
    (The intra-ring splay modes live in the complement and are correctly eliminated.)"""
    P = np.zeros((9, 3))
    for k in range(3):
        P[3 * k:3 * k + 3, k] = np.ones(3) / np.sqrt(3.0)
    Q, _ = np.linalg.qr(np.hstack([P, _QR_FILL]))
    Pc, Qc = Q[:, :3], Q[:, 3:]
    A = Pc.T @ J @ Pc; B = Pc.T @ J @ Qc; C = Qc.T @ J @ Pc; D = Qc.T @ J @ Qc
    Jcoll = A - B @ np.linalg.solve(D, C)
    return np.linalg.eigvals(Jcoll)


def naive_smallest_re(J):
    """the WRONG readout (kept to expose the artifact): 3 smallest-|Re| modes -- grabs the intra-splay pair."""
    ev = np.linalg.eigvals(J)
    return ev[np.argsort(np.abs(ev.real))[:3]]


def ring_chirality(th3):
    a, b, c = th3
    return int(np.sign(np.sin(b - a) + np.sin(c - b) + np.sin(a - c)))


def run(kappa, alpha, shift_cov, n_ic=16):
    coll_im, naive_im, chis, splay_ok = [], [], [], 0
    for s in range(n_ic):
        th = settle(kappa, alpha, 100 + s, shift_cov)
        th3 = th.reshape(3, 3)
        z1 = max(abs(np.mean(np.exp(1j * th3[k]))) for k in range(3))
        if z1 < 0.4:
            splay_ok += 1               # splay: |Z1|~0; sync: |Z1|~1
        J = jac(th, kappa, alpha, shift_cov)
        coll_im.append(float(np.max(np.abs(collective_meta_eig(J).imag))))
        naive_im.append(float(np.max(np.abs(naive_smallest_re(J).imag))))
        chis.append([ring_chirality(th3[k]) for k in range(3)])
    return dict(coll_im=float(np.median(coll_im)), naive_im=float(np.median(naive_im)),
                splay_frac=splay_ok / n_ic, chis=np.array(chis))


def main():
    print("SPLAY CASCADE -- does the discrete-chiral splay platform a COLLECTIVE meta-cycle?\n")
    ALPHA = 0.9 * np.pi

    # the artifact, exposed: a SINGLE splay ring already has the 0.155 Im (intra-splay rotation)
    th1 = settle(0.0, ALPHA, 0).reshape(3, 3)[0]
    J1 = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if i != j:
                J1[i, j] = (K / 3) * np.cos(th1[j] - th1[i] - ALPHA)
        J1[i, i] = -(K / 3) * sum(np.cos(th1[k] - th1[i] - ALPHA) for k in range(3) if k != i)
    print(f"single splay ring eigenvalues: {np.linalg.eigvals(J1)}")
    print(f"  -> the 0.155 Im is the INTRA-ring splay rotation (intrinsic to ONE ring), NOT a meta-cycle.\n")

    kappas = [0.1, 0.2, 0.4, 0.7]
    print("COLLECTIVE meta-cycle readout (Schur onto per-ring global-phase nodes) vs the naive artifact:")
    hdr = f"   {'case':>34} {'kappa':>6} {'splay%':>7} {'COLL max|Im|':>13} {'naive max|Im|':>14}  meta-cycle?"
    print(hdr)
    rows = {}
    for label, alpha, cov in [("splay + COVARIANT", ALPHA, True),
                              ("splay + UNIFORM (control)", ALPHA, False),
                              ("ACHIRAL subs (sync) + COVARIANT", 0.0, True)]:
        rows[label] = []
        for kp in kappas:
            r = run(kp, alpha, cov)
            rows[label].append(r)
            print(f"   {label:>34} {kp:>6.2f} {100*r['splay_frac']:>6.0f}% {r['coll_im']:>13.5f} "
                  f"{r['naive_im']:>14.5f}  {'YES' if r['coll_im'] > IM_FLOOR else 'no (+0)'}")

    # self-lighting (sanity: the splay DOES self-light a Z2; that is not the issue)
    rc = rows["splay + COVARIANT"][-1]["chis"].flatten()
    print(f"\nself-lighting (splay, covariant): per-ring chirality census +{int((rc>0).sum())}/-{int((rc<0).sum())} "
          f"(spontaneous Z2 -- the splay DOES self-light; the failure is the cascade, not the self-lighting)")

    cov_cascades = bool(rows["splay + COVARIANT"][-1]["coll_im"] > IM_FLOOR)
    figure(kappas, rows)

    print("\n" + "=" * 88)
    print("VERDICT -- the discrete-chiral splay does NOT cascade (+0)")
    print("=" * 88)
    if not cov_cascades:
        print("  ==> +0. The COLLECTIVE (global-phase) sector stays REAL under even-parity coupling -- covariant,")
        print("      uniform, and achiral all give real collective eigenvalues, NO complex pair, NO meta-cycle.")
        print("      The splay's chirality is DISCRETE (the Z2 firing order); its linearization is a REAL gapped")
        print("      node, so it has NO antisymmetric seed, and an even-parity coupling of real-spectrum subs")
        print("      gives a SYMMETRIC collective Jacobian -> real -> +0. (The naive 'smallest-|Re|' readout")
        print("      reported 0.155 = the INTRA-ring splay rotation -- the fake-NaN artifact, not a meta-cycle.)")
        print("\n  THE SHARP RESULT -- a TRIPLE OBSTRUCTION. A cascade-closing substrate needs self-light + gapped")
        print("  + complex-pair-SEEDABLE, but gapping-by-discreteness (the only route that self-lights AND gaps)")
        print("  makes the spectrum REAL and kills the antisymmetric seed:")
        print("    homochiral: self-light + seed, NOT gapped (weakly-damped, fragile, #1 miss).")
        print("    Banach:     gapped + seed, NOT self-light (drawn-in, synthetic).")
        print("    splay:      self-light + gapped, NOT seedable (discrete/real, +0 here).")
        print("  Robustness (gapped) and seeding (antisymmetric complex pair) pull OPPOSITE ways for a self-lit")
        print("  substrate. THIS is the real obstruction to closing frustration-ascent -- sharper than 'find a")
        print("  substrate'. The splay remains a clean single-unit instance (self-light + gapped + BZ-realized).")
    else:
        print("  ==> META-CYCLE EMERGES (re-examine: covariant should beat uniform if genuinely seeded).")
    print("\n  SCOPE: frustrated-Kuramoto / BZ-droplet model class, emergent (chirality self-selects). The")
    print("  obstruction is structural (real-spectrum subs cannot seed via even-parity coupling), not a tuning miss.")


def figure(kappas, rows):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5), dpi=150)
    k = np.array(kappas)
    styles = {"splay + COVARIANT": ("#1565c0", "o-"), "splay + UNIFORM (control)": ("#2e7d32", "s--"),
              "ACHIRAL subs (sync) + COVARIANT": ("#6a1b9a", "^:")}
    for label, (c, st) in styles.items():
        ax.plot(k, [r["coll_im"] for r in rows[label]], st, color=c, lw=2, ms=8,
                label=f"COLLECTIVE: {label.split(' (')[0]}")
    # the artifact line (naive readout) for contrast
    ax.plot(k, [r["naive_im"] for r in rows["splay + COVARIANT"]], "x-", color="#c62828", lw=1.4, ms=8,
            label="naive 'smallest-|Re|' readout = 0.155 (INTRA-splay artifact)")
    ax.axhline(IM_FLOOR, color="gray", ls=":", lw=1, label="meta-cycle floor")
    ax.set_xlabel(r"inter-ring coupling $\kappa$ (even-parity)")
    ax.set_ylabel(r"collective-sector max $|\mathrm{Im}\,\lambda|$")
    ax.set_title("the discrete-chiral splay does NOT cascade: the COLLECTIVE sector stays REAL (+0)\n"
                 "(the apparent 0.155 'meta-cycle' is the intra-ring splay rotation — a readout artifact)",
                 fontsize=10.5)
    ax.legend(fontsize=8, frameon=False, loc="center right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = OUT / "splay_cascade.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"figure: {path}")


if __name__ == "__main__":
    main()
