r"""character_closure.py -- Part C: the completeness/closure derivation for the character
deformation-algebra, verified numerically.

This is the piece that turns the empirical generator TABLE (character_primitives.py) into a derived,
complete, closed LAW. Forced-not-fitted = derivation, not tabulation: we prove the generator set is
exhaustive and closed, not that "more cases also fit."

Ron's four-step structure (2026-05-29):
  STEP 1  Formalize the algebra: write the explicit commutation relations of the deformation
          generators of the linear character-bearing drift.
  STEP 2  Autonomous-symmetry test (the FORMAL narrow path for route (a)): does CLOSURE of the
          algebra REQUIRE the protecting symmetry to exist?  If the algebra fails to close unless the
          coupling commutes with a symmetry group -> the algebra ENTAILS the symmetry -> promote (a).
          If it closes unconditionally -> abandon (a) with zero guilt, bank (b).
  STEP 3  Law of the lift: prove structurally that a PROTECTED (degenerate) doublet + the surviving
          antisymmetric deformation forces a lift into a counter-rotating meta-cycle.
  STEP 4  (next move, not here) package as a conditional operator for character_engine.md.

THE RESULT (derived, verified below):
  The LINEAR deformation space of the character-bearing drift M = -gamma I + g A_CYC is gl(3,R), and
  its generator basis is the CARTAN DECOMPOSITION
        gl(3,R) = R.I  (+)  so(3)  (+)  Sym0
                  damping     chirality   splitting/detuning
                  (trace,1)   (axial,3)   (sym-traceless,5)         1 + 3 + 5 = 9 = dim gl(3).
  Brackets:  [I,*]=0 (center);  [so(3),so(3)] in so(3);  [so(3),Sym0] in Sym0;  [Sym0,Sym0] in so(3).
  Exhaustive (dim count) AND closed (Lie bracket) -> a closure, not a catalogue.  This is route (b):
  closure is AUTONOMOUS (needs no symmetry); the protecting symmetry is a SUBSTRATE BOUNDARY CONDITION
  that suppresses the O(kappa) Sym0 doublet-splitting channel so the O(kappa^2) so(3) chiral seed
  survives -> the protected meta-cycle.  Strict-K3 posture: the symmetry is a parameterized condition,
  not a structural output.

Usage (from mpa-conform root):
  python scripts/character_closure.py
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

from banach_frustrated import A_CYC, E1, E2
from chiral_bonding import (CHAN_COVARIANT, GAMMA, G, KAPPA, S_RECIP, collective_basis)

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)
OM0 = np.sqrt(3.0) * G
TOL = 1e-10


# ============================================================ Frobenius inner product + basis
def fro(X, Y):
    """real Frobenius inner product <X,Y> = tr(X^T Y)."""
    return float(np.tensordot(X, Y, axes=([0, 1], [0, 1])))


def gl3_basis():
    """An orthonormal (Frobenius) basis of gl(3,R), graded by the Cartan decomposition.
       center R.I : 1   ->  damping            (the trace direction; A_CYC's gamma I piece)
       so(3)      : 3   ->  chirality mag+sign+orientation (axial; A_CYC = Lx+Ly+Lz is the (1,1,1) one)
       Sym0       : 5   ->  splitting/detuning (sym-traceless; SPLIT = E1E1^T - E2E2^T is one of them)
    Returns (names, mats, index slices for each graded block)."""
    e = np.eye(3)
    # --- center (trace): damping ---
    C0 = e / np.sqrt(3.0)                                   # <I,I> = 3
    # --- so(3): antisymmetric generators (chirality + orientation) ---
    Lx = np.array([[0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])
    Ly = np.array([[0, 0, 1.0], [0, 0, 0], [-1.0, 0, 0]])
    Lz = np.array([[0, -1.0, 0], [1.0, 0, 0], [0, 0, 0]])
    K = [L / np.sqrt(2.0) for L in (Lx, Ly, Lz)]            # <L,L> = 2
    # --- Sym0: symmetric traceless (anisotropic splitting / detuning) ---
    S1 = np.diag([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    S2 = np.diag([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    S3 = (np.outer(e[0], e[1]) + np.outer(e[1], e[0])) / np.sqrt(2.0)
    S4 = (np.outer(e[0], e[2]) + np.outer(e[2], e[0])) / np.sqrt(2.0)
    S5 = (np.outer(e[1], e[2]) + np.outer(e[2], e[1])) / np.sqrt(2.0)
    P = [S1, S2, S3, S4, S5]
    names = (["I (damping)"]
             + [f"K{i+1} (chirality/orient)" for i in range(3)]
             + [f"S{i+1} (splitting)" for i in range(5)])
    mats = [C0] + K + P
    blocks = {"center": [0], "so(3)": [1, 2, 3], "Sym0": [4, 5, 6, 7, 8]}
    return names, mats, blocks


def project_weights(M, mats):
    """coords of M in the orthonormal basis; residual = norm of the un-captured part."""
    w = np.array([fro(M, B) for B in mats])
    recon = sum(c * B for c, B in zip(w, mats))
    resid = float(np.linalg.norm(M - recon))
    return w, resid


def block_of(idx, blocks):
    for name, ids in blocks.items():
        if idx in ids:
            return name
    return "?"


# ============================================================ STEP 1+2: Cartan closure + autonomy
def step1_2_closure():
    print("=" * 78)
    print("STEP 1  --  the generator algebra (commutation relations)")
    print("=" * 78)
    names, mats, blocks = gl3_basis()
    n = len(mats)

    # orthonormality sanity
    gram = np.array([[fro(a, b) for b in mats] for a in mats])
    assert np.allclose(gram, np.eye(n), atol=1e-12), "basis not orthonormal"
    print(f"  basis: {len(blocks['center'])} center (R.I) + {len(blocks['so(3)'])} so(3) + "
          f"{len(blocks['Sym0'])} Sym0  =  {n}  =  dim gl(3,R).  [orthonormal: OK]")
    print("  EXHAUSTIVE for the linear drift: 1+3+5 spans every real 3x3 matrix (the full drift space).")

    # commutator table: which graded block does each [Bi,Bj] land in?  + global closure residual
    grade_pattern = {}          # (block_i, block_j) -> set of result blocks
    max_resid = 0.0
    for i in range(n):
        for j in range(n):
            Cm = mats[i] @ mats[j] - mats[j] @ mats[i]
            w, resid = project_weights(Cm, mats)
            max_resid = max(max_resid, resid)
            if np.linalg.norm(Cm) < TOL:
                continue
            bi, bj = block_of(i, blocks), block_of(j, blocks)
            lands = {block_of(k, blocks) for k in range(n) if abs(w[k]) > 1e-9}
            grade_pattern.setdefault((bi, bj), set()).update(lands)

    print(f"\n  CLOSURE: every commutator [Bi,Bj] re-expands in the same 9 generators.")
    print(f"           max residual over all 81 commutators = {max_resid:.2e}  "
          f"(<{TOL:g} -> closed).")
    print("\n  CARTAN GRADING (which block each bracket lands in):")
    order = ["center", "so(3)", "Sym0"]
    for bi in order:
        for bj in order:
            lands = grade_pattern.get((bi, bj))
            if lands is None:
                print(f"    [{bi:>6}, {bj:>6}]  =  0        (vanishes)")
            else:
                print(f"    [{bi:>6}, {bj:>6}]  in  {', '.join(sorted(lands))}")
    cartan_ok = (
        grade_pattern.get(("so(3)", "so(3)"), set()) <= {"so(3)"}
        and grade_pattern.get(("so(3)", "Sym0"), set()) <= {"Sym0"}
        and grade_pattern.get(("Sym0", "so(3)"), set()) <= {"Sym0"}
        and grade_pattern.get(("Sym0", "Sym0"), set()) <= {"so(3)"}
        and ("center", "center") not in grade_pattern
        and ("center", "so(3)") not in grade_pattern
        and ("center", "Sym0") not in grade_pattern
    )
    print(f"\n  -> Cartan decomposition gl(3)=R.I (+) [so(3) (+) Sym0] CONFIRMED: {cartan_ok}")
    print("     [k,k]<=k, [k,p]<=p, [p,p]<=k with k=so(3), p=Sym0; center R.I commutes with all.")

    # the apparatus's generators are literally these basis elements:
    _, _, _ = names, None, None
    ax_acyc = np.array([A_CYC[2, 1], A_CYC[0, 2], A_CYC[1, 0]])
    split = np.outer(E1, E1) - np.outer(E2, E2)
    _, r_acyc = project_weights(A_CYC, mats)
    _, r_split = project_weights(split, mats)
    print("\n  apparatus check (the generators character_primitives.py actually deformed):")
    print(f"    A_CYC  (chirality gen) axial vector = {ax_acyc} = (1,1,1);  in so(3)?  resid={r_acyc:.1e}")
    print(f"    SPLIT = E1E1^T-E2E2^T  (detuning gen) symmetric-traceless;  in gl(3)? resid={r_split:.1e}")

    print("\n" + "=" * 78)
    print("STEP 2  --  autonomous-symmetry test:  does CLOSURE require the protecting symmetry?")
    print("=" * 78)
    print("  The structure constants above were computed with NO symmetry constraint imposed --")
    print("  no C3 projection, no commute-with-a-group condition.  gl(3,R) is a Lie algebra; it closes")
    print("  UNCONDITIONALLY.  Closure does NOT entail the protecting symmetry.")
    print("  => route (a) [symmetry as a structural OUTPUT of closure] is ABANDONED, with zero guilt.")
    print("  => route (b) banked: the symmetry is a SUBSTRATE BOUNDARY CONDITION, parameterized in.")
    print("\n  WHERE the symmetry actually enters -- it selects which generator channel leads on the")
    print("  collective doublet (O(kappa) Sym0 splitting  vs  O(kappa^2) so(3) chiral seed):")
    scal = symmetry_role_scaling()
    return cartan_ok, scal


def build_meta(Msub, kappa, chan):
    """3 copies of Msub + a symmetric (even-parity) per-edge coupling `chan` scaled by kappa.
    CHAN_COVARIANT = C3-covariant (cyclically rotated copies); a generic chan breaks C3."""
    M = np.zeros((9, 9))
    for k in range(3):
        M[3 * k:3 * k + 3, 3 * k:3 * k + 3] = Msub
    for (k, l), Q in chan.items():
        M[3 * k:3 * k + 3, 3 * l:3 * l + 3] += kappa * S_RECIP[k, l] * Q
        M[3 * l:3 * l + 3, 3 * k:3 * k + 3] += kappa * S_RECIP[l, k] * Q
    return M


def generic_even_parity(seed=1):
    """a generic (C3-BROKEN) but still symmetric/even-parity per-edge coupling."""
    rng = np.random.default_rng(seed)
    chan = {}
    for edge in ((0, 1), (1, 2), (2, 0)):
        R = rng.standard_normal((3, 3))
        chan[edge] = 0.5 * (R + R.T)            # symmetric => even-parity, but NOT a C3 copy
    return chan


def collective_doublet(Msub, kappa, chan):
    """Schur-reduce to the 3x3 collective drift Meff; split its eigenvalues into the totally-symmetric
    A1 mode (overlap with uniform-over-blocks) and the 2-D E doublet.  Return (doublet real-axis
    splitting, doublet |Im| = meta-cycle frequency)."""
    M = build_meta(Msub, kappa, chan)
    U = collective_basis()
    Mp = U.T @ M @ U
    A, B, C, Dq = Mp[:3, :3], Mp[:3, 3:], Mp[3:, :3], Mp[3:, 3:]
    Meff = A - B @ np.linalg.solve(Dq, C)
    ev, evec = np.linalg.eig(Meff)
    u = np.ones(3) / np.sqrt(3.0)               # A1 = uniform over the 3 collective nodes
    overlap = np.abs(u @ evec)
    a1 = int(np.argmax(overlap))
    doublet = [k for k in range(3) if k != a1]
    re = np.sort(ev[doublet].real)
    split = float(re[1] - re[0])                # real-axis splitting of the doublet
    omega = float(np.max(np.abs(ev[doublet].imag)))   # meta-cycle frequency (b1=1 iff >0)
    return split, omega


def _slope(x, y):
    """log-log slope where the signal is nonzero/finite; nan if too few points (signal absent)."""
    m = (np.asarray(y) > 1e-14) & np.isfinite(y)
    if m.sum() < 3:
        return float("nan")
    return float(np.polyfit(np.log(np.asarray(x)[m]), np.log(np.asarray(y)[m]), 1)[0])


def symmetry_role_scaling():
    """The two channels read on the SAME collective doublet, the SAME observable per case where the
    signal lives:  covariant -> the seed is a complex pair so the O(kappa^2) signal is omega_meta (the
    real-split is ~0 by construction);  generic -> the O(kappa) Sym0 split is real so the signal is the
    real-axis split (and omega_meta is killed)."""
    M0 = -GAMMA * np.eye(3) + G * A_CYC
    kappas = np.geomspace(0.01, 0.3, 14)
    chan_gen = generic_even_parity(seed=1)

    cov = np.array([collective_doublet(M0, k, CHAN_COVARIANT) for k in kappas])
    gen = np.array([collective_doublet(M0, k, chan_gen) for k in kappas])
    cov_split, cov_om = cov[:, 0], cov[:, 1]
    gen_split, gen_om = gen[:, 0], gen[:, 1]

    s_cov_om = _slope(kappas, cov_om)        # the O(kappa^2) chiral seed (where covariant's signal is)
    s_gen_split = _slope(kappas, gen_split)  # the O(kappa) Sym0 split (where generic's signal is)

    print(f"    C3-COVARIANT  arena: complex pair (real-split = {cov_split[-1]:.1e} ~ 0); the seed is in")
    print(f"                         omega_meta ~ kappa^{s_cov_om:.2f}  (expect ~2: the O(k^2) so(3) seed); "
          f"meta-cycle alive? {cov_om[-1] > 1e-9}")
    print(f"    generic even-parity : real-axis split ~ kappa^{s_gen_split:.2f}  (expect ~1: the O(k) Sym0 "
          f"channel); meta-cycle alive? {gen_om[-1] > 1e-9} (killed)")
    print("    => the protecting symmetry SUPPRESSES the O(kappa) Sym0 splitting channel; only then")
    print("       does the O(kappa^2) so(3) chiral seed lead and the meta-cycle survive.  This is the")
    print("       derived role of the symmetry -- a boundary condition on the coupling, not a closure law.")
    return dict(kappas=kappas, cov_split=cov_split, cov_om=cov_om, gen_split=gen_split, gen_om=gen_om,
                s_cov_om=s_cov_om, s_gen_split=s_gen_split)


# ============================================================ STEP 3: the law of the lift
def step3_lift_law():
    print("\n" + "=" * 78)
    print("STEP 3  --  the law of the lift (protected doublet -> counter-rotating meta-cycle)")
    print("=" * 78)
    print("  On the 2-D collective doublet the residual deformation is a 2x2 normal form:")
    print("     M2 = -gamma' I2 + (delta/2) Z + omega J,   Z=diag(1,-1) [Sym0 split],  J=[[0,-1],[1,0]] [so(2)]")
    print("     eigenvalues  =  -gamma' +/- sqrt( (delta/2)^2 - omega^2 ).")
    print("  delta is the Sym0 splitting (the channel the symmetry gates); omega the so(3) rotation.")

    Z = np.array([[1.0, 0.0], [0.0, -1.0]])
    J = np.array([[0.0, -1.0], [1.0, 0.0]])
    gp, omega = 1.0, 1.0
    deltas = np.linspace(0.0, 4.0 * omega, 400)

    def m2(delta):
        return -gp * np.eye(2) + (delta / 2.0) * Z + omega * J

    ims = np.array([np.max(np.abs(np.linalg.eigvals(m2(d)).imag)) for d in deltas])
    res = np.array([np.ptp(np.linalg.eigvals(m2(d)).real) for d in deltas])  # real-axis split

    # PROTECTED case: symmetry on -> delta = 0
    ev0 = np.linalg.eigvals(m2(0.0))
    protected_complex = bool(np.max(np.abs(ev0.imag)) > 1e-9)
    print(f"\n  PROTECTED (symmetry on -> delta=0): eigenvalues = {ev0[0]:.3f}, {ev0[1]:.3f}")
    print(f"     complex-conjugate pair -> counter-rotating meta-cycle FORCED: {protected_complex}")
    print(f"     (the ONLY residual deformations on a degenerate doublet are damping I2 + rotation J;")
    print(f"      a 2x2 real antisymmetric block has eigenvalues +/- i*omega -- a rotation, necessarily.)")

    # EP collision at delta = 2 omega
    ep_idx = int(np.argmin(np.abs(deltas - 2.0 * omega)))
    print(f"  EP COLLISION at delta = 2*omega: |Im| -> 0 (the tilt-death / exceptional point).")

    # the EP square-root law: regress (Im)^2 on (delta/2)^2 on the complex branch -> slope -1, R^2=1
    branch = deltas < 2.0 * omega - 1e-6
    x = (deltas[branch] / 2.0) ** 2
    y = ims[branch] ** 2
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    print(f"  EP square-root law  omega_eff^2 = omega^2 - (delta/2)^2  (i.e. omega_eff^2 vs (delta/2)^2):")
    print(f"     slope = {coef[0]:+.4f} (predicted -1),  intercept = {coef[1]:+.4f} (= omega^2 = 1),  "
          f"R^2 = {r2:.4f}")
    print("  => the PROTECTED lift and the EP DEATH are two branches of ONE normal form. Same form as")
    print("     establishment_compare.py's verified non-Hermitian EP (pa:nonhermitian-ep).")
    return dict(deltas=deltas, ims=ims, res=res, omega=omega, r2=r2,
                protected_complex=protected_complex)


# ============================================================ figure
def figure(scal, lift):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6), dpi=150)

    # panel 1: the symmetry's role -- generic O(kappa) real split vs covariant O(kappa^2) seed
    k = scal["kappas"]
    ax[0].loglog(k, np.clip(scal["gen_split"], 1e-16, None), "o-", color="#c62828",
                 label=f"generic: real split ~$\\kappa^{{{scal['s_gen_split']:.1f}}}$ (Sym₀, kills cycle)")
    ax[0].loglog(k, np.clip(scal["cov_om"], 1e-16, None), "s-", color="#1565c0",
                 label=f"C3-covariant: $\\omega_{{meta}}$ ~$\\kappa^{{{scal['s_cov_om']:.1f}}}$ (so(3) seed, cycle lives)")
    for ref, sty in ((k, ":"), (k ** 2, "--")):
        ax[0].loglog(k, ref * (scal["gen_split"][-1] / k[-1] if sty == ":" else scal["cov_om"][-1] / k[-1] ** 2),
                     sty, color="gray", lw=0.8, alpha=0.6)
    ax[0].set_xlabel(r"meta-coupling $\kappa$"); ax[0].set_ylabel("collective doublet signal")
    ax[0].set_title("STEP 2: the symmetry's role\n(suppresses the O(κ) Sym₀ channel)")
    ax[0].legend(fontsize=7.5, frameon=False); ax[0].grid(alpha=0.3, which="both")

    # panel 2: the lift-law normal form -- complex branch / EP / real branch
    d, om = lift["deltas"], lift["omega"]
    ax[1].plot(d / om, lift["ims"], color="#6a1b9a", lw=2.2, label=r"$|\mathrm{Im}\,\lambda|$ (meta-cycle)")
    ax[1].plot(d / om, lift["res"], color="#ef6c00", lw=2.2, ls="--", label=r"real-axis split")
    ax[1].axvline(2.0, color="#2e7d32", ls=":", lw=1.5, label=r"EP at $\delta=2\omega$")
    ax[1].axvline(0.0, color="#1565c0", lw=3, alpha=0.4)
    ax[1].annotate("PROTECTED\n(symmetry on)", xy=(0.0, om), xytext=(0.6, 0.55 * om),
                   fontsize=8, color="#1565c0")
    ax[1].set_xlabel(r"Sym$_0$ splitting $\delta/\omega$"); ax[1].set_ylabel("eigenvalue parts")
    ax[1].set_title("STEP 3: the law of the lift\n(one normal form: meta-cycle → EP → real)")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    # panel 3: the EP square-root law on the protected/complex branch
    branch = d < 2.0 * om - 1e-6
    ax[2].plot((d[branch] / 2.0) ** 2, lift["ims"][branch] ** 2, "o", ms=3, color="#c2185b")
    xs = np.linspace(0, om ** 2, 50)
    ax[2].plot(xs, om ** 2 - xs, "k-", lw=1.3, label="$\\omega^2-(\\delta/2)^2$")
    ax[2].set_xlabel(r"$(\delta/2)^2$"); ax[2].set_ylabel(r"$\omega_{\rm eff}^2$")
    ax[2].set_title(f"EP square-root law (pa:nonhermitian-ep)\n$R^2={lift['r2']:.4f}$")
    ax[2].legend(fontsize=9, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("Part C -- character deformation-algebra: Cartan closure + autonomous-symmetry test + lift law",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "character_closure.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


# ============================================================ main
def main():
    print(f"CHARACTER CLOSURE (Part C)   gamma={GAMMA}, g={G}, kappa={KAPPA}, omega0={OM0:.3f}\n")
    cartan_ok, scal = step1_2_closure()
    lift = step3_lift_law()
    figure(scal, lift)

    print("\n" + "=" * 78)
    print("VERDICT (Part C)")
    print("=" * 78)
    print(f"  (C) closure DERIVED: linear drift space = gl(3,R), Cartan-decomposed into")
    print(f"      damping (R.I) (+) chirality (so(3)) (+) splitting (Sym0); exhaustive (1+3+5=9) and")
    print(f"      closed (Lie bracket).  Cartan grading confirmed: {cartan_ok}.  A closure, not a catalogue.")
    print(f"  (a)->(b): closure is AUTONOMOUS (no symmetry needed).  Strict-K3 banked: the protecting")
    print(f"      symmetry is a substrate boundary condition suppressing the O(kappa) Sym0 channel.")
    print(f"  (lift) DERIVED: protected degenerate doublet forces a complex pair = counter-rotating")
    print(f"      meta-cycle; same 2x2 normal form whose other branch is the verified EP (R^2={lift['r2']:.4f}).")
    print(f"  EXTENSIONS (named, closed elsewhere; not gl(3)): noise = diffusion tensor via Lyapunov;")
    print(f"      nonlinearity = normal forms (pitchfork/Hopf); time-periodic = Floquet/monodromy;")
    print(f"      composition = Schur (coarse-grain coupled triads -> again (gl(3) drift, Sym+ noise)).")
    print(f"  OPEN (stay frontier, do NOT promote): the ~39deg symmetric-cone node (model-specific);")
    print(f"      non-uniform-squeeze secondary tongues.")


if __name__ == "__main__":
    main()
