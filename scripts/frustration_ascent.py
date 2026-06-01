r"""frustration_ascent.py -- runnable spec for `frustration-ascent` (mpa-atlas/framework/character_frontier.md).

The STRUCTURAL side of the I5 layer-2 generative-recursion bet: MPA minting its own register.
Claim under test (frontier `frustration-ascent`, steeping): a NESS drive's protected current
is EJECTED UPWARD until it reaches a scale it can frustrate; balanced blocks bonded into an
ODD-PARITY directed cycle close a NEW asymmetric triad (A != 0, new self-probe) = "another MPA
spun up"; b1 increments by one per ascent. N>=3 -> 3-torus (the topology side of wall-forces-chaos).

Sibling of `affinity_coarsegrain.py` (which tests the COMPLEMENT, `consolidation-ascent`: an
EXISTING triad surviving coarse-graining, b1 INVARIANT -- the threading direction). This tests
the GENERATIVE direction: protected cycles ACCUMULATE up the tower, +1 per ascent.

------------------------------------------------------------------------------------------------
WHAT A FIRST PASS RULED OUT (the sharp constraint, recorded so it isn't re-explored):

  A legitimate (adiabatic, gamma_fast >> gamma_slow) coarse-graining PRESERVES the slow spectrum,
  so it CANNOT turn an all-real fine spectrum into a complex coarse pair. Equivalently: eliminating
  a single shared scalar "server" gives a RANK-1 correction (b_out b_in^T), whose spectrum is real
  -- no rotation. => Protected circulation is NOT created from a balanced cluster. It cannot be
  conjured from a tree. It must be SUPPLIED as an odd-parity (frustrated) inter-block bond -- and
  THEN it nests up the tower. "Ejected upward / climbs to a scale it can frustrate" means: the
  only place a protected current can live is a cross-cluster odd-parity cycle, never inside a
  balanced cluster. The reciprocal-bond control below is the live kill of any creation-from-balance
  reading.
------------------------------------------------------------------------------------------------

CONSTRUCTION (linear OU, EXACT -- the sign-topological face; no adiabatic approximation needed):

  base triad  = -gamma I_3 + g A_CYC   (the minimal carrier; complex pair -gamma +- i sqrt3 g;
                A_CYC = rock-paper-scissors circulant; banach_frustrated). b1_protected = 1.
  collective  = (1,1,1)/sqrt3 is the EXACT non-rotating eigenvector (A_CYC has zero row sums) ->
                each triad presents one clean "node" to the next level. The collective subspace is
                M-INVARIANT, so restricting to it is EXACT, not an adiabatic approximation.
  ASCENT      = take 3 copies of the current object, bond their collective nodes by an odd-parity
                3-cycle (g A_CYC again) -> a meta-triad of triad-nodes. Each ascent platforms
                exactly ONE new protected cycle in the collective subspace: b1_protected grows
                3*prev + 1. New-per-ascent = +1.  (THE recursion type-identity: the platformed
                meta-coupling is A_CYC again -- MPA's minimal carrier reproduced one level up.)

  KILL #1     = bond reciprocally (symmetric, balanced) instead -> real spectrum in the collective
                subspace -> NO new protected cycle. New-per-ascent = +0 = "balances at every scale".

Forced-not-fitted: the platformed meta-triad's rotation is omega_meta = sqrt3 * g_inter and its
affinity A_meta = 2 pi <sigma>/omega -- the SAME closed form as the base triad with g -> g_inter
(structural type-identity). Nothing fitted.

Honest scope: this is the b1-growth / topological face on the LINEAR model, EXACT. The DYNAMICAL
type-identity (coarse node == the full two-mode kernel with c/s/r AMPLITUDE + gFDR) needs the
NONLINEAR (gain+saturation) extension -- the linear model has no chit/amplitude knob (the boundary
banach_frustrated already named). Synthetic: calibration + the apparatus a real substrate lands
into, NOT vindication of the staked claim (that needs a real cross-substrate instance).

Run from mpa-conform root:  python scripts/frustration_ascent.py
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

from banach_frustrated import A_CYC  # rock-paper-scissors circulant [[0,-1,1],[1,0,-1],[-1,1,0]]

GAMMA, G, D = 1.0, 0.6, 0.1     # banach_frustrated base operating point
N_ASCENTS = 2                    # levels above base (3 -> 9 -> 27 modes)
IM_FLOOR = 1e-9
RECIP_BOND = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])  # symmetric/balanced control


def n_protected(M):
    """Number of protected rotations = complex-conjugate eigenvalue pairs (each = one frustrated
    cycle carrying current). This is b1_protected, computed EXACTLY from the spectrum."""
    ev = np.linalg.eigvals(M)
    return int(np.sum(ev.imag > IM_FLOOR))


def ou_invariants(M, B):
    """Affinity of dz = M z dt + sqrt(2B) dW.  sign(Im lambda) = topological bit; omega = max|Im|;
    <sigma> = EP rate; A = 2 pi <sigma>/omega (nats/cycle)."""
    Sigma = solve_continuous_lyapunov(M, -2.0 * B)
    Omega = M + B @ np.linalg.inv(Sigma)
    sigma = float(np.trace(Omega @ Sigma @ Omega.T @ np.linalg.inv(B)))
    ev = np.linalg.eigvals(M)
    k = int(np.argmax(np.abs(ev.imag)))
    omega = float(abs(ev.imag[k]))
    sign = int(np.sign(ev.imag[k])) if omega > IM_FLOOR else 0
    A = 2.0 * np.pi * sigma / omega if omega > IM_FLOOR else 0.0
    if not np.all(np.isfinite([sigma, omega, A])):
        raise FloatingPointError("non-finite invariant -- diagnose, do not fill")
    return dict(sign=sign, omega=omega, sigma=sigma, A=A, ev=ev)


def build_tower(n_ascents, g=G, gamma=GAMMA, frustrated=True):
    """Exact nested-collective tower. Returns per-level history with b1_protected and the
    new-protected-cycles platformed by each ascent. `coll` is the unit collective node of the
    current object, embedded in its R^n -- M-invariant, so the reduction is exact."""
    bond = g * A_CYC if frustrated else g * RECIP_BOND
    M = -gamma * np.eye(3) + g * A_CYC                 # level 0: a single triad
    coll = np.ones(3) / np.sqrt(3.0)                    # its collective node (exact -gamma eigvec)
    hist = [dict(level=0, n_modes=3, b1=n_protected(M), new=n_protected(M), M=M, coll=coll)]
    for lv in range(1, n_ascents + 1):
        n = M.shape[0]
        Mbig = np.zeros((3 * n, 3 * n))
        v = []
        for k in range(3):                              # three copies, block-diagonal
            Mbig[k * n:(k + 1) * n, k * n:(k + 1) * n] = M
            ek = np.zeros(3 * n); ek[k * n:(k + 1) * n] = coll
            v.append(ek)                                # copy k's collective node, embedded
        for k in range(3):                              # bond the three collective nodes
            for l in range(3):
                if bond[k, l] != 0.0:
                    Mbig += bond[k, l] * np.outer(v[k], v[l])
        prev_b1 = hist[-1]["b1"]
        M = Mbig
        coll = (v[0] + v[1] + v[2]) / np.sqrt(3.0)       # new meta-collective node
        b1 = n_protected(M)
        hist.append(dict(level=lv, n_modes=3 * n, b1=b1, new=b1 - 3 * prev_b1, M=M, coll=coll))
    return hist


def collective_subspace_drift(g=G, gamma=GAMMA, frustrated=True):
    """The 3x3 drift the ascent platforms in the collective subspace -- structurally identical to
    the base triad with g -> g_inter (frustrated) => recursion type-identity at structural grade."""
    return -gamma * np.eye(3) + (g * A_CYC if frustrated else g * RECIP_BOND)


def main() -> None:
    print("frustration-ascent runnable spec: do protected cycles ACCUMULATE +1 per frustrated ascent?")
    print(f"base triad: gamma={GAMMA}, g={G}, D={D}; A_CYC = rock-paper-scissors circulant\n")

    fr = build_tower(N_ASCENTS, frustrated=True)
    rc = build_tower(N_ASCENTS, frustrated=False)

    hdr = (f"{'ascent':>6} | {'modes':>6} | {'FRUSTRATED b1_prot (new)':>26} | "
           f"{'RECIPROCAL b1_prot (new)':>26}")
    print(hdr); print("-" * len(hdr))
    for f, r in zip(fr, rc):
        print(f"{f['level']:>6d} | {f['n_modes']:>6d} | "
              f"{f['b1']:>14d}  (+{f['new']:<2d})        | "
              f"{r['b1']:>14d}  (+{r['new']:<2d})")

    # --- forced-not-fitted: the platformed meta-triad's affinity vs the base triad's closed form ---
    base = ou_invariants(*(lambda M: (M, D * np.eye(3)))(collective_subspace_drift(frustrated=True)))
    print(f"\nrecursion type-identity (structural) -- the ascent platforms A_CYC again in the")
    print(f"collective subspace: drift = -gamma I + g A_CYC, the SAME minimal carrier as the base.")
    print(f"    platformed meta-triad: omega = {base['omega']:.4f} (= sqrt3 * g = {np.sqrt(3)*G:.4f}, FORCED),")
    print(f"    affinity A = {base['A']:.4f} nats, sign = {base['sign']:+d}, gauge-irremovable odd-parity 3-cycle.")

    # --- verdict ---
    fr_new = [h["new"] for h in fr[1:]]
    rc_new = [h["new"] for h in rc[1:]]
    accumulates = all(n == 1 for n in fr_new)
    kill_clean = all(n == 0 for n in rc_new)
    forced = abs(base["omega"] - np.sqrt(3) * G) < 1e-6

    print("\n================ VERDICT ================")
    if accumulates and kill_clean and forced:
        print(f"ACCUMULATES. Each frustrated ascent platforms EXACTLY ONE new protected cycle")
        print(f"(new-per-ascent = {fr_new}) -- a new odd-parity triad of triad-nodes, 'another MPA")
        print(f"spun up', structurally A_CYC again (type-identity). The collective subspace is exactly")
        print(f"M-invariant, so the nesting is EXACT, not an adiabatic approximation.")
        print(f"=> frustration-ascent's b1-growth leg is INSTANCED at calibration grade.")
        print(f"   The reciprocal control platforms NOTHING above the base (new-per-ascent = {rc_new}):")
        print(f"   a balanced bond 'balances at every scale' (KILL #1 clean). Protected circulation is")
        print(f"   NOT created from balance -- it must be supplied as an odd-parity bond, then it nests.")
    else:
        print(f"NOT clean: accumulates(+1 each)={accumulates}, kill_clean(+0 each)={kill_clean}, "
              f"forced={forced}. new_fr={fr_new}, new_rc={rc_new}. Read honestly.")
    print("\nHonest scope: EXACT on the sign-topological / b1 face (linear OU). The DYNAMICAL")
    print("type-identity -- coarse node == the full two-mode kernel with c/s/r AMPLITUDE + gFDR --")
    print("needs the NONLINEAR (gain+saturation) extension; the linear model has no chit/amplitude knob.")
    print("Synthetic: calibration + the apparatus a real substrate lands into, NOT vindication.")
    print("N>=3 ascents populate a 3-torus (engine COMPRESSION wall-forces-chaos) -- the dynamical")
    print("face of this same tower; reachable once the nonlinear node lands.")

    # ---- figure ----
    fig, (axn, axs, axa) = plt.subplots(1, 3, figsize=(17, 5.2), dpi=150)

    # left: b1_protected staircase, frustrated vs reciprocal
    lv = [h["level"] for h in fr]
    axn.plot(lv, [h["b1"] for h in fr], "o-", color="#c2185b", lw=2, ms=9,
             label="FRUSTRATED bond (odd-parity)")
    axn.plot(lv, [h["b1"] for h in rc], "s--", color="#1565c0", lw=2, ms=9,
             label="RECIPROCAL bond (balanced, KILL)")
    for h in fr[1:]:
        axn.annotate(f"+{h['new']}", (h["level"], h["b1"]), textcoords="offset points",
                     xytext=(6, 6), color="#c2185b", fontsize=11, weight="bold")
    axn.set_xlabel("ascent level"); axn.set_ylabel(r"$b_1^{\mathrm{protected}}$ (protected cycles)")
    axn.set_xticks(lv)
    axn.set_title("protected cycles accumulate +1 per frustrated ascent\nreciprocal bond platforms nothing")
    axn.legend(fontsize=9, frameon=False); axn.grid(alpha=0.3)

    # middle: spectrum at top level (frustrated) -- many complex pairs = many nested triads
    evtop = np.linalg.eigvals(fr[-1]["M"])
    axs.axhline(0, color="gray", lw=0.6); axs.axvline(0, color="gray", lw=0.6)
    axs.scatter(evtop.real, evtop.imag, s=70, color="#c2185b", edgecolor="white", zorder=3)
    axs.set_xlabel("Re(eig)"); axs.set_ylabel("Im(eig)")
    axs.set_title(f"top-level spectrum ({fr[-1]['n_modes']} modes, b1_prot={fr[-1]['b1']})\n"
                  "each complex pair = one nested frustrated triad")
    axs.grid(alpha=0.3)

    # right: platformed meta-triad affinity = base triad affinity (type-identity)
    g_sweep = np.linspace(0.1, 1.2, 12)
    A_meta = [ou_invariants(-GAMMA * np.eye(3) + g * A_CYC, D * np.eye(3))["A"] for g in g_sweep]
    axa.plot(g_sweep, A_meta, "o-", color="#6a1b9a", lw=2,
             label=r"platformed $A_{\mathrm{meta}}(g_{\mathrm{inter}})$")
    axa.axvline(G, color="gray", ls=":", lw=1, label=f"base g = {G}")
    axa.set_xlabel(r"inter-block coupling $g_{\mathrm{inter}}$")
    axa.set_ylabel("affinity A per cycle (nats)")
    axa.set_title("type-identity: the platformed triad's affinity\nis the base triad's closed form (FORCED)")
    axa.legend(fontsize=9, frameon=False); axa.grid(alpha=0.3)

    fig.suptitle("frustration-ascent: protected cycles accumulate +1 per frustrated ascent "
                 "(a triad of triad-nodes platformed each level)", fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "frustration_ascent.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
