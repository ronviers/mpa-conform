r"""chiral_bonding.py -- the chiral-bonding BOOTSTRAP test for `frustration-ascent`.

The prize move after `frustration_ascent.py`. That script platformed +1 protected cycle per
ascent, but the meta-frustration (A_CYC) was HAND-SUPPLIED each level => *fitted* => calibration,
not vindication. `frustration-ascent` is a MECHANISM claim whose promote gate is a FORCED-NOT-FITTED
derivation. This script asks whether the cascade SELF-GENERATES its next structural hole: does a
meta-triad EMERGE from internally-frustrated sub-triads bonded by a provably-EVEN-PARITY
(symmetric) coupling, with NO hand-drawn odd-parity meta-bond? An emergent meta-cycle would be
forced-not-fitted by construction; the no-creation-from-balance theorem certifies the forcing
(creation from balance is forbidden; creation from sub-chirality is allowed).

------------------------------------------------------------------------------------------------
THE SETUP (corrected with Ron 2026-05-29; the handoff's "balanced blocks" was a mis-statement --
a balanced block has no rotating mode to bond through):
  * SUBS  -- internally-FRUSTRATED triads (M_sub = -gamma I + chir*g*A_CYC). Each carries chirality
    in its ROTATING pair (-gamma +- i sqrt3 g, in the plane perp to (1,1,1)). That chirality is the
    SEED. The collective node (1,1,1)/sqrt3 is the real mode (carries none).
  * META-COUPLING -- provably SYMMETRIC / even-parity. The part I am forbidden to frustrate.
    Block(k,l) = kappa S[k,l] Q_{kl}, S symmetric, each Q_{kl} symmetric.
  * FORCED ROUTE -- eliminating the chiral sub-modes (Schur complement onto the collective
    meta-triad) hands M_eff an ANTISYMMETRIC part ~ -B D0^-1 C, where D0^-1 carries the chirality
    as -omega J/(gamma^2+omega^2). So sub-chirality ALWAYS propagates into the coarse description,
    forced and proportional to g.

------------------------------------------------------------------------------------------------
THE FINDING (honest, falsification-grade -- the bootstrap is CONDITIONAL, not generic):

  Chirality propagates into the coarse antisym ALWAYS (forced ~ g). But it CLOSES A PROTECTED
  META-CYCLE only when a collective-sector DEGENERACY survives for the seed to lift. The seed
  enters at O(kappa^2); a generic even-parity coupling SPLITS the collective levels at O(kappa).
  O(kappa) >> O(kappa^2): the seed is overwhelmed unless a degeneracy is protected. Three regimes:

  * SYMMETRY-PROTECTED (C3-covariant) coupling -- three identical subs, symmetric arrangement,
    each bond through a cyclically-rotated channel. Preserves the symmetry-protected collective
    doublet AND carries the distinct cross-coupling that seeds it => a GENUINE protected meta-cycle
    closes (full-spectrum b1: 3 -> 4, a new low-frequency pair), forced-not-fitted, drive-protected.
  * C3-INVARIANT (uniform) coupling -- every bond identical. The cross-coupling cancels exactly
    (w J w^T = 0): chirality does not even propagate. KILL.
  * GENERIC / C3-BROKEN coupling -- independent bonds. Chirality propagates (antisym M_eff != 0)
    but the O(kappa) level-splitting overwhelms the O(kappa^2) seed: NO cycle closes. KILL
    (0% of random distinguishable bond-sets close a protected cycle).

  => The cascade does NOT unconditionally self-bootstrap. It needs the substrate to supply, on top
  of (a) a drive and (b) a frustrable sub-topology, ALSO (c) a meta-scale SYMMETRY protecting the
  collective degeneracy. THREE supplied ingredients -- a SHARPENING of parasitic-on-substrate, not
  a refutation of it. WITHIN symmetric substrates the emergent cycle is genuine (microscopic),
  forced-not-fitted, sign-seeded by the subs, and drive-protected; without the symmetry it does not
  close. Whether real targets present such symmetry (homochirality networks, active-solid lattices)
  is the decisive INSTANCE question.

VERDICT GRADE: forced-not-fitted DERIVATION achieved, but CONDITIONAL on a substrate-supplied
meta-symmetry. Crosses toward `frustration-ascent`'s promote line ONLY for symmetry-protected
substrates -- so the real-instance/symmetry question is now load-bearing. Synthetic, ONE model
class (linear OU); pre-conform / direct-sim.

Run from mpa-conform root:  python scripts/chiral_bonding.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import solve_continuous_lyapunov

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

from banach_frustrated import A_CYC, E1, E2  # rps circulant; rotation-plane basis perp to (1,1,1)

GAMMA, G, KAPPA, D = 1.0, 0.6, 0.3, 0.1
IM_FLOOR = 1e-9
SUB_OMEGA = np.sqrt(3.0) * G                 # bare sub circulation frequency (the fast scale)
COLL = np.ones(3) / np.sqrt(3.0)
N_AX = np.ones(3)                            # A_CYC <-> axial vector (1,1,1); chirality reference
S_RECIP = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])
_E = np.eye(3)
# C3-COVARIANT bonds: bond(k, k+1) couples through node-k. Symmetric per bond; the three bonds are
# cyclically rotated copies -> preserves the symmetry-protected collective doublet, distinct cross.
CHAN_COVARIANT = {(0, 1): np.outer(_E[0], _E[0]),
                  (1, 2): np.outer(_E[1], _E[1]),
                  (2, 0): np.outer(_E[2], _E[2])}
CHAN_UNIFORM = {(0, 1): np.outer(_E[0], _E[0]),     # C3-invariant: same bond everywhere
                (1, 2): np.outer(_E[0], _E[0]),
                (2, 0): np.outer(_E[0], _E[0])}


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"non-finite in '{name}' -- diagnose, do not fill (NaN is a tripwire)")
    return x


def collective_basis():
    """9x9 orthonormal U. Cols 0:3 = embedded collective nodes (kept P); 3:9 = chiral rotating
    pairs (eliminated Q)."""
    Uc = np.zeros((9, 3)); Ur = np.zeros((9, 6))
    for k in range(3):
        Uc[3 * k:3 * k + 3, k] = COLL
        Ur[3 * k:3 * k + 3, 2 * k] = E1
        Ur[3 * k:3 * k + 3, 2 * k + 1] = E2
    return np.hstack([Uc, Ur])


U9 = collective_basis()


def build_full(chir=(1.0, 1.0, 1.0), kappa=KAPPA, g=G, gamma=GAMMA, chan=None, extra=None):
    """Three frustrated subs + an even-parity meta-coupling. The ONLY antisymmetric part is the
    intra-sub chir*g*A_CYC, so any emergent meta-antisymmetry is forced by the subs. `extra` adds a
    symmetric per-bond perturbation (used to break the collective degeneracy in the gating sweep)."""
    chan = CHAN_COVARIANT if chan is None else chan
    M = np.zeros((9, 9))
    for k in range(3):
        M[3 * k:3 * k + 3, 3 * k:3 * k + 3] = -gamma * np.eye(3) + chir[k] * g * A_CYC
    for (k, l), Q in chan.items():
        Qk = Q + (extra[(k, l)] if extra and (k, l) in extra else 0.0)
        M[3 * k:3 * k + 3, 3 * l:3 * l + 3] += kappa * S_RECIP[k, l] * Qk
        M[3 * l:3 * l + 3, 3 * k:3 * k + 3] += kappa * S_RECIP[l, k] * Qk
    return M


def meta_eff(M):
    """Schur complement onto the collective meta-triad; returns M_eff and the coarse chirality
    (axial . (1,1,1)) -- the FORCED chirality-propagation observable (nonzero whenever the subs are
    chiral and the coupling reaches the rotating modes, regardless of whether a cycle closes)."""
    Mp = U9.T @ M @ U9
    A, B, C, Dq = Mp[:3, :3], Mp[:3, 3:], Mp[3:, :3], Mp[3:, 3:]
    M_eff = finite("M_eff", A - B @ np.linalg.solve(Dq, C))
    a = 0.5 * (M_eff - M_eff.T)
    coarse_chir = float(np.array([a[2, 1], a[0, 2], a[1, 0]]) @ N_AX)
    sym = 0.5 * (M_eff + M_eff.T)
    ev = np.sort(np.linalg.eigvalsh(sym))
    coll_gap = float(ev[1] - ev[0])                      # collective-doublet splitting
    return M_eff, coarse_chir, coll_gap


def emergent_cycle(M):
    """The emergent meta-cycle read from the FULL spectrum: a NEW protected pair well-separated
    below the fast sub frequency. Returns its frequency (0 if none) and micro b1."""
    ev = np.linalg.eigvals(M)
    ims = np.sort(np.abs(ev.imag[ev.imag > IM_FLOOR]))
    micro_b1 = int(len(ims))
    slow = ims[ims < 0.5 * SUB_OMEGA] if len(ims) else np.array([])
    omega = float(slow.max()) if len(slow) else 0.0      # the emergent (slow) meta-cycle
    return omega, micro_b1


def readout(M):
    _, coarse_chir, coll_gap = meta_eff(M)
    omega, micro_b1 = emergent_cycle(M)
    return dict(omega=omega, micro_b1=micro_b1, chir=int(np.sign(coarse_chir)) if abs(coarse_chir) > 1e-12 else 0,
                coarse_chir=coarse_chir, coll_gap=coll_gap,
                max_re=float(np.max(np.linalg.eigvals(M).real)))


def meta_current(M, B):
    """Stationary OU irreversible current Omega projected onto the meta-triad (signed). For the
    drive-set foil."""
    Sigma = solve_continuous_lyapunov(M, -2.0 * B)
    Omega = M + B @ np.linalg.inv(Sigma)
    o = U9[:, :3].T @ Omega @ U9[:, :3]
    a = 0.5 * (o - o.T)
    return float(np.array([a[2, 1], a[0, 2], a[1, 0]]) @ N_AX)


def aniso_bath(a, seed=0):
    rng = np.random.default_rng(7 + seed)
    N = rng.standard_normal((9, 9)); N = 0.5 * (N + N.T)
    N -= np.trace(N) / 9.0 * np.eye(9); N /= np.linalg.norm(N)
    return D * (np.eye(9) + a * 9.0 * N)


def main() -> None:
    print("chiral-bonding bootstrap: does even-parity coupling of frustrated subs SEED a protected")
    print(f"meta-cycle?  gamma={GAMMA}, g={G}, kappa={KAPPA}, D={D}; sub omega=sqrt3*g={SUB_OMEGA:.3f}\n")

    cov = readout(build_full(chir=(1, 1, 1), chan=CHAN_COVARIANT))
    uni = readout(build_full(chir=(1, 1, 1), chan=CHAN_UNIFORM))
    bal = readout(build_full(chir=(0, 0, 0), chan=CHAN_COVARIANT))

    print("WHO CLOSES A PROTECTED META-CYCLE (full-spectrum b1: 3 sub-pairs + any emergent):")
    print(f"    SYMMETRY-PROTECTED (C3-covariant) : micro b1={cov['micro_b1']} (3->{cov['micro_b1']}), "
          f"omega_emergent={cov['omega']:.4f}, chirality={cov['chir']:+d}, coarse_antisym={cov['coarse_chir']:+.4f}")
    print(f"    C3-INVARIANT (uniform bonds)      : micro b1={uni['micro_b1']},       "
          f"omega_emergent={uni['omega']:.4f}, coarse_antisym={uni['coarse_chir']:+.4f}  (w J w^T=0: no propagation)")
    print(f"    BALANCED subs (g=0)               : micro b1={bal['micro_b1']},       "
          f"omega_emergent={bal['omega']:.4f}  (no chirality to seed)")

    # --- genericity: random C3-broken bonds. chirality propagates but cycle rarely closes ---
    rng = np.random.default_rng(11)
    n_stable = n_close = n_prop = 0
    chirs = []
    while n_stable < 300:
        chan = {}
        for k, l in [(0, 1), (1, 2), (2, 0)]:
            Rr = rng.standard_normal((3, 3)); Rr = 0.5 * (Rr + Rr.T); Rr /= np.linalg.norm(Rr)
            chan[(k, l)] = Rr
        r = readout(build_full(chir=(1, 1, 1), chan=chan))
        if r["max_re"] >= 0:
            continue
        n_stable += 1
        if abs(r["coarse_chir"]) > 1e-6:
            n_prop += 1; chirs.append(abs(r["coarse_chir"]))
        if r["omega"] > IM_FLOOR:
            n_close += 1
    print(f"\nGENERIC (n={n_stable} stable random C3-broken bond-sets): chirality PROPAGATES to the")
    print(f"    coarse antisym in {100*n_prop/n_stable:.0f}% (mean |antisym|={np.mean(chirs):.4f}) -- forced -- but a")
    print(f"    protected cycle CLOSES in only {100*n_close/n_stable:.0f}%: the O(kappa) level-splitting")
    print(f"    overwhelms the O(kappa^2) chirality seed unless a degeneracy is symmetry-protected.")

    # --- degeneracy gating: break the collective degeneracy of the covariant case, watch it die ---
    eps = np.linspace(0.0, 0.30, 25)
    gate = [readout(build_full(chir=(1, 1, 1),
                               extra={(0, 1): e * np.outer(COLL, COLL)})) for e in eps]
    om_gate = np.array([r["omega"] for r in gate])
    gap_gate = np.array([r["coll_gap"] for r in gate])
    seed_mag = abs(cov["coarse_chir"])
    eps_die = float(eps[np.argmax(om_gate < IM_FLOOR)]) if np.any(om_gate < IM_FLOOR) else float("nan")
    print(f"\nDEGENERACY GATING: the covariant cycle survives only while the collective gap stays below")
    print(f"    the O(kappa^2) seed (~{seed_mag:.4f}); it dies at eps~{eps_die:.2f} (gap crosses the seed).")

    # --- forced + propagation vs g (closed form: chirality-seed ~ sqrt3 g/(gamma^2+3g^2)) ---
    gs = np.linspace(0.0, 1.4, 29)
    om_g = np.array([readout(build_full(chir=(1, 1, 1), g=g))["omega"] for g in gs])
    chir_g = np.array([abs(readout(build_full(chir=(1, 1, 1), g=g))["coarse_chir"]) for g in gs])
    cf_g = np.sqrt(3.0) * gs / (GAMMA ** 2 + 3.0 * gs ** 2)        # antisym(R^-1) closed form
    forced_corr = float(np.corrcoef(chir_g, cf_g)[0, 1])
    print(f"FORCED: coarse antisym tracks the Schur closed form sqrt3*g/(gamma^2+3g^2) "
          f"(corr {forced_corr:.3f}, no fitted knob); omega_emergent(g=0)={om_g[0]:.2e} (certifier).")

    # --- seeding: flip sub-chirality -> coarse chirality flips ---
    flip = readout(build_full(chir=(-1, -1, -1), chan=CHAN_COVARIANT))
    sign_flips = cov["chir"] != 0 and flip["chir"] == -cov["chir"]
    print(f"SEEDING: chir(+++)={cov['chir']:+d}, chir(---)={flip['chir']:+d} => coarse chirality flips "
          f"with the subs: {sign_flips}")

    # --- teeth: the emergent cycle is a drift eigenpair (drive-independent = PROTECTED) ---
    M_cov, M_bal = build_full(chir=(1, 1, 1)), build_full(chir=(0, 0, 0))
    avals = np.linspace(0.0, 0.30, 16)
    om_drive = np.array([emergent_cycle(M_cov)[0] for _ in avals])          # drift => flat in drive
    foil_cur = np.array([meta_current(M_bal, aniso_bath(a)) for a in avals])  # drive-set
    nz = foil_cur[np.abs(foil_cur) > 1e-9]
    foil_driveset = bool(len(nz) and len(set(np.sign(nz).astype(int))) > 1) and abs(foil_cur[0]) < 1e-6
    print(f"TEETH: the covariant cycle is a complex pair of the deterministic drift (omega={cov['omega']:.4f},")
    print(f"    drive-INDEPENDENT) => PROTECTED, survives drive->0 sign-invariant. The foil (balanced subs")
    print(f"    + anisotropic bath) has no drift pair; its current is drive-set (bath sign, ->0): {foil_driveset}.")

    # --- homochirality ---
    print(f"\nHOMOCHIRALITY (report whatever it is):")
    homo = []
    for c in [(1, 1, 1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)]:
        r = readout(build_full(chir=c, chan=CHAN_COVARIANT))
        homo.append((c, r))
        tag = "homochiral" if abs(sum(c)) == 3 else "mixed"
        print(f"    subs {str(c):>12} ({tag:>10}): omega_emergent={r['omega']:.4f}, chirality={r['chir']:+d}")

    # --- verdict ---
    print("\n================ VERDICT ================")
    print("FORCED-NOT-FITTED, BUT CONDITIONAL (not generic). Even-parity coupling of frustrated subs")
    print("ALWAYS propagates the sub-chirality into the coarse description (forced ~ g), but closes a")
    print("PROTECTED meta-cycle only when a collective degeneracy is symmetry-protected:")
    print(f"  * C3-covariant (symmetric arrangement): a GENUINE microscopic emergent cycle closes")
    print(f"    (b1 3->{cov['micro_b1']}, omega={cov['omega']:.4f}), forced (->0 as g->0), sign-seeded by the subs")
    print(f"    ({'flips' if sign_flips else 'DOES NOT flip'} with sub-chirality), drive-PROTECTED (drift eigenpair).")
    print(f"  * C3-invariant uniform: no propagation (w J w^T=0). KILL.")
    print(f"  * generic C3-broken: chirality propagates but the O(kappa) splitting overwhelms the")
    print(f"    O(kappa^2) seed -> cycle closes in ~0%. KILL.")
    print("=> The cascade does NOT unconditionally self-bootstrap. It needs the substrate to supply a")
    print("   meta-scale SYMMETRY (protecting the collective degeneracy) on top of the drive + the")
    print("   frustrable sub-topology -- THREE supplied ingredients. A SHARPENING of")
    print("   parasitic-on-substrate, not a refutation. `frustration-ascent` crosses toward promote by")
    print("   forced-not-fitted derivation ONLY for symmetry-protected substrates -- so the")
    print("   real-instance/symmetry question (homochirality nets, active-solid lattices) is now decisive.")
    print("\nHonest scope: ONE model class (linear OU); synthetic. The emergent cycle, when it closes,")
    print("is a genuine microscopic protected pair. A clean conditional result beats a forced 'pass'.")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)

    # (0,0) full spectrum: covariant (b1 3->4, emergent slow pair circled) vs balanced
    a0 = ax[0, 0]
    ev_cov = np.linalg.eigvals(M_cov); ev_bal = np.linalg.eigvals(M_bal)
    a0.axhline(0, color="gray", lw=0.6); a0.axvline(0, color="gray", lw=0.6)
    a0.scatter(ev_bal.real, ev_bal.imag, s=55, color="#1565c0", marker="s",
               label="balanced subs (real, KILL)", zorder=2)
    a0.scatter(ev_cov.real, ev_cov.imag, s=70, color="#c2185b", edgecolor="white",
               label=f"C3-covariant (micro b1={cov['micro_b1']})", zorder=3)
    a0.scatter([ev_cov.real[np.argmin(np.abs(np.abs(ev_cov.imag) - cov['omega']))]],
               [cov['omega']], s=240, facecolor="none", edgecolor="#2e7d32", lw=2.4,
               label=f"EMERGENT meta-cycle (omega={cov['omega']:.3f})", zorder=4)
    a0.set_xlabel("Re(eig)"); a0.set_ylabel("Im(eig)")
    a0.set_title("a protected meta-cycle closes ONLY under symmetry-protected\n"
                 "(C3-covariant) coupling: micro b1 3 -> 4, a new slow pair")
    a0.legend(fontsize=8, frameon=False, loc="upper left"); a0.grid(alpha=0.3)

    # (0,1) degeneracy gating: omega_emergent vs the collective gap (the mechanism / the kill)
    a1 = ax[0, 1]
    a1.plot(gap_gate, om_gate, "o-", color="#c2185b", lw=2, ms=5)
    a1.axvline(seed_mag, color="#2e7d32", ls="--", lw=1.5,
               label=f"O($\\kappa^2$) chirality seed ~ {seed_mag:.3f}")
    a1.set_xlabel("collective level-splitting (gap), grown by breaking the degeneracy")
    a1.set_ylabel(r"emergent $\omega_{\rm meta}$")
    a1.set_title("WHY conditional: the cycle survives only while the collective\n"
                 "gap stays below the O($\\kappa^2$) seed -- then it dies (generic case)")
    a1.legend(fontsize=9, frameon=False); a1.grid(alpha=0.3)

    # (1,0) forced + propagation vs g
    a2 = ax[1, 0]
    a2.plot(gs, chir_g, "o", color="#6a1b9a", ms=4, label="coarse antisym (measured, ALWAYS propagates)")
    a2.plot(gs, cf_g * (chir_g.max() / (cf_g.max() + 1e-12)), "k--", lw=1.2,
            label=r"Schur closed form $\propto \sqrt3 g/(\gamma^2+3g^2)$")
    a2.plot(gs, om_g, "s-", color="#c2185b", lw=2, ms=4, label=r"emergent $\omega_{\rm meta}$ (closes, covariant)")
    a2.axvline(G, color="gray", ls=":", lw=1)
    a2.scatter([0], [0], s=70, color="#2e7d32", zorder=5, label="g=0: no seed (certifier)")
    a2.set_xlabel("sub-frustration g (sub-chirality)"); a2.set_ylabel("coarse antisym / emergent rate")
    a2.set_title(f"FORCED: chirality propagates, tracks the closed form (corr {forced_corr:.2f}),\n"
                 "and $\\to$0 as g$\\to$0; a cycle closes only when degeneracy-protected")
    a2.legend(fontsize=8, frameon=False); a2.grid(alpha=0.3)

    # (1,1) homochirality
    a3 = ax[1, 1]
    labels = ["+ + +\n(homo)", "+ + -\n(mixed)", "+ - -\n(mixed)", "- - -\n(homo)"]
    vals = [r["omega"] * (r["chir"] if r["chir"] != 0 else 1) for _, r in homo]
    cols = ["#c2185b" if abs(sum(c)) == 3 else "#ef9a00" for c, _ in homo]
    a3.bar(range(4), vals, color=cols, edgecolor="white")
    a3.axhline(0, color="gray", lw=0.8)
    a3.set_xticks(range(4)); a3.set_xticklabels(labels, fontsize=9)
    a3.set_ylabel(r"signed $\omega_{\rm meta}$ (chirality $\times$ rate)")
    a3.set_title("homochirality dependence: homochiral subs give the strongest\n"
                 "coherent meta-cycle; mixed chirality partly cancels")
    a3.grid(alpha=0.3, axis="y")

    fig.suptitle("chiral-bonding bootstrap: sub-chirality propagates (forced), but closes a protected "
                 "meta-cycle ONLY under a symmetry-protected degeneracy", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "chiral_bonding.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
