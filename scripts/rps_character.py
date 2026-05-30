r"""rps_character.py -- cross `staked:character-primitives` on RPS (the real emergent C3 arena).

Move #1 of promotion_crossing_handoff.md: run the deformation apparatus (the gl(3) Cartan
generators / character_closure.py) ON the rock-paper-scissors substrate's EMERGENT Jacobian,
not on the hand-drawn synthetic A_CYC. RPS is real-emergent (vindication-grade, per the campaign's
authored-vs-emergent criterion) and C3-symmetric (the substrate-supplied protecting symmetry the
conditional deformation-algebra law needs).

THE CLAIM UNDER TEST  (staked:character-primitives; frontier + receipts §deformation-generators):
  the character deformation-generator basis is the Cartan decomposition
      gl(3,R) = R.I (+) so(3) (+) Sym0      (damping (+) chirality (+) splitting/detuning),
  exhaustive (1+3+5=9) and closed; REAL character COMPOSES from these generators with the forced
  canonical responses; closure is autonomous, the protecting symmetry a substrate boundary condition
  (strict-K3).  Promote gate (staked->promoted): a REAL symmetric chiral substrate whose native
  character composes from these generators with these forced responses (the coverage instance).

WHY RPS IS THE INSTANCE (forced, not fitted): the synthetic apparatus HAND-DREW A_CYC (the chirality
generator).  RPS PRODUCES it.  The May-Leonard Jacobian at the coexistence fixed point
    M_RPS = -x* (I + alpha S + beta S^2)        (S = cyclic shift; x* = 1/(1+alpha+beta))
decomposes EXACTLY into the three Cartan channels, and its antisymmetric part is
    Antisym(M_RPS) = x*(alpha-beta)/2 * A_CYC   (axial vector along (1,1,1); residual 0)
-- the chirality generator is EMERGENT, forced onto the so(3) (1,1,1) axis by the competition, with
handedness = sign(alpha-beta).  The hand-tuned (gamma,g) of the synthetic model are, on RPS, forced
functions of (alpha,beta,x*): gamma_eff = x*[1-(alpha+beta)/2], g_eff = x*(alpha-beta)/2.  And the
intrinsic Sym0 part of M_RPS is ISOTROPIC on the chiral plane (S+S^2 = J-I acts as -I perp to
(1,1,1)) -- it shifts the doublet uniformly, never splits it: the doublet degeneracy the lift law
needs is itself substrate-protected.  That is the vindication the coverage stake was waiting on.

PRE-REGISTERED CROSSING BAR (all must hold; a clean miss is also evidence, sharpening the gate):
  C1 composition (K1): M_RPS in gl(3) Cartan, residual<1e-10; chirality aligned to (1,1,1)/A_CYC,
     |cos|>0.999, sign=sign(alpha-beta); damping in center, splitting in Sym0.
  C2 emergent / no-creation-from-balance: drive delta=alpha-beta -> 0: the so(3) chirality
     magnitude -> 0 linearly and flips sign through the (never-visited) achiral point; chirality is
     the ONLY delta-odd channel (center + Sym0 are delta-even).
  C3 lift on the RPS meta-arena (native deformation within C3): three C3-coupled RPS triads close a
     protected meta-cycle (b1 3->4, a slow drift eigenpair, drive-independent); a generic C3-broken
     coupling kills it (~0% closure over random bond-sets); channel scaling omega_meta ~ kappa^2
     (so(3) seed) vs real-split ~ kappa (Sym0) -- the symmetry honestly supplied, not hand-imposed.
  C4 forced response (K2+): deform the emergent chiral plane by the Sym0 splitting generator ->
     the non-Hermitian EP normal form omega^2 = omega0_RPS^2 - s^2, R^2>0.999, EP at s=omega0
     (pa:nonhermitian-ep; s = the splitting control, EP at delta=2 omega0 in the delta=2s convention).
  C5 drive-flow (K4 / I5): the chimeric sign is invariant over the demographic-noise drive, |J| ~
     sigma^2 -> 0 as drive->0; every channel magnitude flows with (alpha,beta,x*,sigma) -- no inert
     constant (the meta-cycle is a drift eigenpair, hence drive-independent by construction).
  K2 QUARANTINE: the ~39deg symmetric-cone node + the non-uniform-squeeze secondary tongues stay
     model-specific -- NOT claimed here, NOT promoted (they remain frontier per the staked entry).

Usage (from mpa-conform root):  python scripts/rps_character.py
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
from rps_triad import coexistence, jacobian, circulation
from chiral_bonding import S_RECIP, CHAN_COVARIANT, collective_basis, IM_FLOOR
from character_closure import gl3_basis, project_weights, build_meta, collective_doublet, generic_even_parity

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

# base RPS operating point: asymmetric (chiral), alpha+beta<2 -> stable circulating focus
A0, B0 = 0.5, 1.0
SPLIT = np.outer(E1, E1) - np.outer(E2, E2)        # the Sym0 doublet-splitting generator (in-plane)
U9 = collective_basis()


def cartan_weights(M):
    """coords of M in the orthonormal gl(3) Cartan basis, grouped by graded block + residual."""
    names, mats, blocks = gl3_basis()
    w, resid = project_weights(M, mats)
    energy = {blk: float(np.sqrt(np.sum(w[ids] ** 2))) for blk, ids in blocks.items()}
    return w, resid, energy, names, blocks


def chirality_axial(M):
    """the so(3) chirality content of M as an axial vector (rotation axis x magnitude)."""
    a = 0.5 * (M - M.T)
    return np.array([a[2, 1], a[0, 2], a[1, 0]])


def sub_omega(alpha, beta):
    xs = 1.0 / (1.0 + alpha + beta)
    return float(xs * np.sqrt(3.0) / 2.0 * abs(alpha - beta))


def gamma_rot(alpha, beta):
    """the rotating (chiral) mode damping of M_RPS = x*[1-(alpha+beta)/2]. RPS's chiral modes are
    WEAKLY damped vs the radial collective node (x*(1+alpha+beta)); this -- not the synthetic gamma=1
    -- is the scale that bounds a stable meta-coupling, so the natural kappa flows with it."""
    xs = 1.0 / (1.0 + alpha + beta)
    return float(xs * (1.0 - (alpha + beta) / 2.0))


def meta_kappa(alpha, beta):
    """gentle, stable meta-coupling scaled to RPS's emergent chiral damping (matches the synthetic
    kappa/gamma ~ 0.3-0.4 regime; flows with the operating point, no inert constant)."""
    return 0.4 * gamma_rot(alpha, beta)


def meta_readout(M, om_sub):
    """full-spectrum b1 + the emergent SLOW pair (meta-cycle) relative to RPS's own sub frequency,
    and the Schur coarse chirality onto the collective nodes. A meta-cycle is 'closed' only when the
    arena is STABLE (max_re<0) -- an unstable arena's low-frequency pairs are not a protected cycle
    (the off-scale-kappa trap: never read a destabilised arena as a closed cycle)."""
    ev = np.linalg.eigvals(M)
    ims = np.sort(np.abs(ev.imag[ev.imag > IM_FLOOR]))
    b1 = int(len(ims))
    slow = ims[ims < 0.5 * om_sub] if om_sub > 0 else np.array([])
    omega_meta = float(slow.max()) if len(slow) else 0.0
    max_re = float(np.max(ev.real))
    stable = max_re < 0.0
    closed = stable and (b1 >= 4) and (omega_meta > IM_FLOOR)
    Mp = U9.T @ M @ U9
    P, B, C, Dq = Mp[:3, :3], Mp[:3, 3:], Mp[3:, :3], Mp[3:, 3:]
    Meff = P - B @ np.linalg.solve(Dq, C)
    a = 0.5 * (Meff - Meff.T)
    coarse = float(np.array([a[2, 1], a[0, 2], a[1, 0]]) @ np.ones(3))
    return dict(omega_meta=omega_meta, b1=b1, coarse=coarse, max_re=max_re,
                stable=stable, closed=closed, ev=ev)


def _slope(x, y):
    m = (np.asarray(y) > 1e-15) & np.isfinite(y)
    if m.sum() < 3:
        return float("nan")
    return float(np.polyfit(np.log(np.asarray(x)[m]), np.log(np.asarray(y)[m]), 1)[0])


# ============================================================ C1 + C2: composition
def section_composition():
    print("=" * 88)
    print("C1 + C2  --  COMPOSITION: the emergent RPS Jacobian decomposes into the Cartan generators")
    print("=" * 88)
    M = jacobian(A0, B0)
    xs = float(coexistence(A0, B0)[0])
    w, resid, energy, names, blocks = cartan_weights(M)
    ax = chirality_axial(M)
    cos111 = float(ax @ np.ones(3) / (np.linalg.norm(ax) * np.sqrt(3)))
    sgn = int(np.sign(ax @ np.ones(3)))
    acyc_res = float(np.linalg.norm(0.5 * (M - M.T) - xs * (A0 - B0) / 2.0 * A_CYC))

    print(f"  base RPS: alpha={A0}, beta={B0}, x*={xs:.4f}  ->  M_RPS = -x*(I + a S + b S^2)")
    print(f"  Cartan block energies: center(damping)={energy['center']:.4f}  "
          f"so(3)(chirality)={energy['so(3)']:.4f}  Sym0(splitting)={energy['Sym0']:.4f}")
    print(f"  exhaustive/closed (K1): reconstruction residual = {resid:.2e}  (<1e-10 -> M_RPS lives in gl(3))")
    print(f"  chirality channel: axial vector = {np.round(ax,5)}  -> aligned to (1,1,1)/A_CYC: "
          f"|cos|={abs(cos111):.6f}, sign={sgn:+d} (=sign(alpha-beta)={int(np.sign(A0-B0)):+d})")
    print(f"  EMERGENT, not hand-drawn: Antisym(M_RPS) = x*(a-b)/2 * A_CYC, residual = {acyc_res:.2e}")

    # C2: drive delta=alpha-beta through zero at fixed alpha+beta -> which channels are delta-odd?
    s_tot = A0 + B0
    deltas = np.linspace(-0.9, 0.9, 41)
    chi_mag, chi_sgn, cen, sym = [], [], [], []
    for d in deltas:
        a, b = (s_tot + d) / 2, (s_tot - d) / 2
        Md = jacobian(a, b)
        wd, _, ed, _, _ = cartan_weights(Md)
        axd = chirality_axial(Md)
        chi_mag.append(np.linalg.norm(axd))
        chi_sgn.append(int(np.sign(axd @ np.ones(3))) if np.linalg.norm(axd) > 1e-12 else 0)
        cen.append(ed["center"]); sym.append(ed["Sym0"])
    chi_mag = np.array(chi_mag); chi_sgn = np.array(chi_sgn)
    cen = np.array(cen); sym = np.array(sym)
    # chirality odd: flips sign across delta=0 and ->0 there; center+Sym0 even: ~flat in |delta|
    nz = chi_sgn[chi_sgn != 0]
    chir_flips = bool(len(set(nz.tolist())) > 1)
    chir_zero_at0 = float(chi_mag[np.argmin(np.abs(deltas))]) < 1e-6
    cen_even = float(np.std(cen) / (np.mean(cen) + 1e-12)) < 1e-6      # center independent of delta sign
    sym_even = bool(np.allclose(sym, sym[::-1], atol=1e-9))           # Sym0 symmetric in delta
    print(f"\n  C2 no-creation-from-balance (drive delta=alpha-beta -> 0 at fixed alpha+beta={s_tot}):")
    print(f"     chirality magnitude -> 0 at the achiral point: {chir_zero_at0}; sign flips across it: {chir_flips}")
    print(f"     chirality is the ONLY delta-odd channel: center delta-even={cen_even}, Sym0 delta-even={sym_even}")
    print(f"     (the achiral point alpha=beta is the never-visited boundary -- read in the interior only)")

    c1 = (resid < 1e-10) and (abs(cos111) > 0.999) and (sgn == int(np.sign(A0 - B0))) and (acyc_res < 1e-9)
    c2 = chir_zero_at0 and chir_flips and cen_even and sym_even
    return dict(M=M, xs=xs, energy=energy, ax=ax, cos111=cos111, resid=resid, acyc_res=acyc_res,
                deltas=deltas, chi_mag=chi_mag, chi_sgn=chi_sgn, cen=cen, sym=sym, c1=c1, c2=c2)


# ============================================================ C4: forced EP response on the plane
def section_ep():
    print("\n" + "=" * 88)
    print("C4  --  FORCED RESPONSE: deform the emergent chiral plane by the Sym0 splitting generator")
    print("=" * 88)
    M = jacobian(A0, B0)
    om0 = sub_omega(A0, B0)
    ss = np.linspace(0.0, 2.4 * om0, 240)
    oms = np.array([float(np.max(np.abs(np.linalg.eigvals(M + s * SPLIT).imag))) for s in ss])
    branch = ss < om0 - 1e-9
    x = (ss[branch]) ** 2
    y = oms[branch] ** 2
    Amat = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(Amat, y, rcond=None)
    yhat = Amat @ coef
    ss_res = float(np.sum((y - yhat) ** 2)); ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    ep_idx = int(np.argmax(oms < 1e-6))
    ep_s = float(ss[ep_idx]) if np.any(oms < 1e-6) else float("nan")
    print(f"  emergent base frequency omega0 = x*(sqrt3/2)|a-b| = {om0:.5f}")
    print(f"  EP square-root law  omega^2 = omega0^2 - s^2  (Sym0 control s; delta=2s -> EP at delta=2 omega0):")
    print(f"     slope = {coef[0]:+.4f} (predicted -1), intercept = {coef[1]:+.5f} (= omega0^2 = {om0**2:.5f}), "
          f"R^2 = {r2:.5f}")
    print(f"     EP collision (omega->0) at s = {ep_s:.4f}  (predicted omega0 = {om0:.4f})  "
          f"-- the non-Hermitian exceptional point pa:nonhermitian-ep")
    c4 = (r2 > 0.999) and (abs(coef[0] + 1.0) < 0.02) and (abs(ep_s - om0) < 0.02 * om0 + 1e-3)
    return dict(ss=ss, oms=oms, om0=om0, r2=r2, slope=coef[0], intercept=coef[1], ep_s=ep_s, c4=c4)


# ============================================================ C3: lift on the RPS meta-arena
def section_lift():
    print("\n" + "=" * 88)
    print("C3  --  LIFT on the RPS META-ARENA: three C3-coupled RPS triads (native deformation in C3)")
    print("=" * 88)
    M = jacobian(A0, B0)
    om_sub = sub_omega(A0, B0)
    kappa = meta_kappa(A0, B0)     # scaled to RPS's emergent chiral damping (gamma_rot), NOT synthetic gamma=1
    print(f"  meta-coupling kappa = 0.4*gamma_rot = {kappa:.4f}  (gamma_rot = x*[1-(a+b)/2] = "
          f"{gamma_rot(A0,B0):.4f}; RPS's chiral modes are weakly damped, so the stable scale is ~10x")
    print(f"  smaller than the synthetic gamma=1 arena -- kappa=0.3 there over-drives RPS into instability)")

    cov = meta_readout(build_meta(M, kappa, CHAN_COVARIANT), om_sub)
    chan_gen = generic_even_parity(seed=1)
    gen = meta_readout(build_meta(M, kappa, chan_gen), om_sub)
    # rewire: swap alpha<->beta (reverse the cycle) -> meta-cycle handedness should flip
    Mrev = jacobian(B0, A0)
    rev = meta_readout(build_meta(Mrev, kappa, CHAN_COVARIANT), sub_omega(B0, A0))

    print(f"  C3-COVARIANT coupling : b1={cov['b1']} (3->{cov['b1']}), omega_meta={cov['omega_meta']:.5f}, "
          f"max_re={cov['max_re']:+.4f}, coarse_chir={cov['coarse']:+.4f}  -> protected meta-cycle "
          f"{'CLOSES' if cov['closed'] else 'absent'}")
    print(f"  generic C3-broken     : b1={gen['b1']}, omega_meta={gen['omega_meta']:.5f}  -> "
          f"{'cycle CLOSED' if gen['closed'] else 'killed (no protected cycle)'}")
    print(f"  REWIRE (alpha<->beta) : coarse_chir={rev['coarse']:+.4f} (was {cov['coarse']:+.4f}) -> "
          f"handedness flips: {np.sign(rev['coarse']) == -np.sign(cov['coarse'])}")

    # genericity census: over random C3-broken even-parity bond-sets, how often does a cycle close?
    rng = np.random.default_rng(11)
    n_stable = n_close = 0
    while n_stable < 300:
        chan = {}
        for edge in ((0, 1), (1, 2), (2, 0)):
            R = rng.standard_normal((3, 3)); R = 0.5 * (R + R.T); R /= np.linalg.norm(R)
            chan[edge] = R
        r = meta_readout(build_meta(M, kappa, chan), om_sub)
        if not r["stable"]:
            continue
        n_stable += 1
        if r["closed"]:
            n_close += 1
    print(f"  genericity census (n={n_stable} stable random C3-broken bond-sets): protected cycle closes "
          f"in {100*n_close/n_stable:.0f}%  (O(kappa) Sym0 split overwhelms the O(kappa^2) so(3) seed)")

    # channel scaling: covariant omega_meta ~ kappa^2 (so(3) seed) vs generic real-split ~ kappa (Sym0)
    kaps = np.geomspace(0.003, 0.06, 16)
    cov_om = np.array([collective_doublet(M, k, CHAN_COVARIANT)[1] for k in kaps])
    gen_sp = np.array([collective_doublet(M, k, chan_gen)[0] for k in kaps])
    s_cov = _slope(kaps, cov_om); s_gen = _slope(kaps, gen_sp)
    print(f"  channel scaling: covariant omega_meta ~ kappa^{s_cov:.2f} (expect ~2, so(3) seed); "
          f"generic real-split ~ kappa^{s_gen:.2f} (expect ~1, Sym0)")

    c3 = (cov['closed'] and cov['b1'] == 4
          and (not gen['closed'])
          and (np.sign(rev['coarse']) == -np.sign(cov['coarse']))
          and (n_close / n_stable) < 0.05
          and abs(s_cov - 2) < 0.4 and abs(s_gen - 1) < 0.4)
    return dict(cov=cov, gen=gen, rev=rev, frac_close=n_close / n_stable, kappa=kappa,
                kaps=kaps, cov_om=cov_om, gen_sp=gen_sp, s_cov=s_cov, s_gen=s_gen,
                om_sub=om_sub, c3=c3)


# ============================================================ C5: drive-flow + I5 / no inert constant
def section_drive():
    print("\n" + "=" * 88)
    print("C5  --  DRIVE-FLOW (K4/I5): chimeric sign drive-invariant, |J|~sigma^2; every channel flows")
    print("=" * 88)
    sigmas = np.array([0.008, 0.014, 0.024, 0.04])
    Js = np.array([circulation(A0, B0, sigma=s, T=1500.0, seed=1) for s in sigmas])
    signs = np.sign(Js)
    hand = int(np.sign(A0 - B0))
    sign_inv = bool(np.all(signs == signs[0]) and signs[0] == hand)
    slope = float(np.polyfit(np.log(sigmas), np.log(np.abs(Js)), 1)[0])
    print(f"  demographic-noise drive sweep: sign(J) all = {int(signs[0]):+d} (= handedness {hand:+d}): "
          f"invariant={sign_inv}")
    print(f"  |J| ~ sigma^{slope:.2f} (expect ~2: amplitude flows with drive, -> 0 as drive->0; the")
    print(f"     meta-cycle is a drift eigenpair -> drive-independent sign by construction)")

    # no inert constant: every Cartan channel magnitude flows with the RPS operating point
    pts = [(0.5, 1.0), (0.7, 0.9), (1.0, 0.3)]
    print("  flow check (no inert constant -- every channel moves with (alpha,beta,x*)):")
    print(f"     {'(alpha,beta)':>14} {'x*':>7} {'damping':>9} {'chirality':>10} {'splitting':>10}")
    chans = []
    for a, b in pts:
        _, _, e, _, _ = cartan_weights(jacobian(a, b))
        xs = float(coexistence(a, b)[0])
        print(f"     {str((a,b)):>14} {xs:>7.4f} {e['center']:>9.4f} {e['so(3)']:>10.4f} {e['Sym0']:>10.4f}")
        chans.append([e['center'], e['so(3)'], e['Sym0']])
    chans = np.array(chans)
    flows = bool(np.all(chans.std(0) / (chans.mean(0) + 1e-12) > 1e-3))
    print(f"     all three channels vary across operating points (no frozen constant): {flows}")
    c5 = sign_inv and (abs(slope - 2) < 0.5) and flows
    return dict(sigmas=sigmas, Js=Js, slope=slope, sign_inv=sign_inv, flows=flows, c5=c5)


# ============================================================ figure
def figure(comp, ep, lift, drive):
    fig, ax = plt.subplots(2, 2, figsize=(15, 10), dpi=150)

    # (0,0) composition: Cartan block energies + the delta-odd chirality channel
    a0 = ax[0, 0]
    a0.plot(comp["deltas"], comp["chi_mag"] * comp["chi_sgn"], "o-", color="#c2185b", lw=2, ms=3,
            label="chirality so(3) (signed) -- delta-ODD")
    a0.plot(comp["deltas"], comp["cen"], "s-", color="#1565c0", lw=1.5, ms=2, label="damping center -- even")
    a0.plot(comp["deltas"], comp["sym"], "^-", color="#2e7d32", lw=1.5, ms=2, label="splitting Sym0 -- even")
    a0.axvline(0, color="gray", ls="--", lw=1.2)
    a0.annotate("achiral point\n(alpha=beta, never visited)", xy=(0, 0), xytext=(0.1, max(comp["cen"]) * 0.5),
                fontsize=8, color="gray")
    a0.set_xlabel(r"asymmetry $\delta=\alpha-\beta$"); a0.set_ylabel("Cartan channel energy (signed for so(3))")
    a0.set_title("C1/C2: M_RPS composes from {damping, chirality, splitting};\n"
                 "chirality is the EMERGENT so(3) A_CYC, the only $\\delta$-odd channel")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3)

    # (0,1) EP normal form on the emergent plane
    a1 = ax[0, 1]
    om0 = ep["om0"]
    a1.plot((ep["ss"] / 2.0) ** 2 * 4, ep["oms"] ** 2, "o", ms=2.5, color="#6a1b9a", label=r"$\omega^2$ measured")
    xs = np.linspace(0, om0 ** 2, 50)
    a1.plot(xs, om0 ** 2 - xs, "k-", lw=1.4, label=r"$\omega_0^2 - s^2$ (EP law)")
    a1.axvline(om0 ** 2, color="#2e7d32", ls=":", lw=1.5, label=f"EP at $s=\\omega_0$")
    a1.set_xlabel(r"$s^2$ (Sym$_0$ splitting control)"); a1.set_ylabel(r"$\omega^2$ (chiral pair)")
    a1.set_title(f"C4: forced EP normal form on the emergent plane\n"
                 f"$\\omega^2=\\omega_0^2-s^2$, $R^2={ep['r2']:.4f}$ (pa:nonhermitian-ep)")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    # (1,0) lift: full spectrum covariant (b1 3->4) vs generic (killed)
    a2 = ax[1, 0]
    ev_c = lift["cov"]["ev"]; ev_g = lift["gen"]["ev"]
    a2.axhline(0, color="gray", lw=0.6); a2.axvline(0, color="gray", lw=0.6)
    a2.scatter(ev_g.real, ev_g.imag, s=55, color="#1565c0", marker="s",
               label=f"generic C3-broken (killed, b1={lift['gen']['b1']})", zorder=2)
    a2.scatter(ev_c.real, ev_c.imag, s=70, color="#c2185b", edgecolor="white",
               label=f"C3-covariant (b1=3->{lift['cov']['b1']})", zorder=3)
    om = lift["cov"]["omega_meta"]
    a2.scatter([ev_c.real[np.argmin(np.abs(np.abs(ev_c.imag) - om))]], [om], s=240, facecolor="none",
               edgecolor="#2e7d32", lw=2.4, label=f"EMERGENT meta-cycle ($\\omega$={om:.3f})", zorder=4)
    a2.set_xlabel("Re(eig)"); a2.set_ylabel("Im(eig)")
    a2.set_title(f"C3: protected meta-cycle closes only under C3-symmetry\n"
                 f"(closes in {100*lift['frac_close']:.0f}% of generic bond-sets)")
    a2.legend(fontsize=7.5, frameon=False, loc="upper left"); a2.grid(alpha=0.3)

    # (1,1) channel scaling + drive sweep (two y-axes)
    a3 = ax[1, 1]
    a3.loglog(lift["kaps"], np.clip(lift["gen_sp"], 1e-16, None), "s-", color="#c62828",
              label=f"generic real-split ~$\\kappa^{{{lift['s_gen']:.1f}}}$ (Sym0)")
    a3.loglog(lift["kaps"], np.clip(lift["cov_om"], 1e-16, None), "o-", color="#1565c0",
              label=f"covariant $\\omega_{{meta}}$ ~$\\kappa^{{{lift['s_cov']:.1f}}}$ (so(3) seed)")
    a3.set_xlabel(r"meta-coupling $\kappa$"); a3.set_ylabel("collective-doublet signal")
    a3.set_title(f"C3 channel scaling ($\\kappa^2$ seed vs $\\kappa$ split) +\n"
                 f"C5 drive: sign invariant, $|J|\\sim\\sigma^{{{drive['slope']:.1f}}}$")
    a3.legend(fontsize=8, frameon=False); a3.grid(alpha=0.3, which="both")
    a3b = a3.twinx()
    a3b.loglog(drive["sigmas"], np.abs(drive["Js"]), "^--", color="#6a1b9a", label="|J| (drive)")
    a3b.set_ylabel("|circulation J|", color="#6a1b9a")

    fig.suptitle("RPS character-primitives crossing -- real emergent C3 substrate composes from the "
                 "gl(3) Cartan generators with forced responses", fontsize=12.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = OUT / "rps_character.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


# ============================================================ main
def main():
    print("RPS CHARACTER-PRIMITIVES CROSSING  --  the deformation apparatus on a real emergent C3 arena")
    print(f"base operating point: alpha={A0}, beta={B0} (asymmetric chiral; alpha+beta<2 stable focus)\n")
    comp = section_composition()
    ep = section_ep()
    lift = section_lift()
    drive = section_drive()
    figure(comp, ep, lift, drive)

    print("\n" + "=" * 88)
    print("VERDICT  --  staked:character-primitives on RPS")
    print("=" * 88)
    bar = [("C1 composition (Cartan, chirality=emergent A_CYC)", comp["c1"]),
           ("C2 no-creation-from-balance (chirality the only delta-odd channel)", comp["c2"]),
           ("C3 lift closes (b1 3->4, conditional on C3, kappa^2 vs kappa)", lift["c3"]),
           ("C4 forced EP normal form (R^2>0.999, EP at omega0)", ep["c4"]),
           ("C5 drive-flow (sign invariant, |J|~sigma^2, channels flow)", drive["c5"])]
    for label, ok in bar:
        print(f"   [{'PASS' if ok else 'MISS'}]  {label}")
    all_ok = all(ok for _, ok in bar)
    print("\n  K2 QUARANTINE respected: the ~39deg symmetric-cone node and the non-uniform-squeeze")
    print("     secondary tongues are NOT claimed/promoted here -- they stay model-specific (frontier).")
    if all_ok:
        print("\n  ==> CROSSES.  A real emergent C3-symmetric substrate (RPS) instances the coverage stake:")
        print("      its native character COMPOSES from the gl(3) Cartan generators -- damping (center),")
        print("      the EMERGENT chirality A_CYC (so(3), forced onto (1,1,1), not hand-drawn), and the")
        print("      splitting (Sym0) -- with the forced responses (EP normal form R^2~1) and the lift law")
        print("      (protected meta-cycle, conditional on the substrate-supplied C3 symmetry: kappa^2 seed")
        print("      vs kappa split).  K1-K4 do not fire.  => staked:character-primitives -> promoted.")
        print("      SCOPE (honest): one real emergent instance (ecological 3-cycle), linear-Jacobian reading")
        print("      at coexistence.  Does NOT over-promote two-bits (needs the floor-isolation protocol) or")
        print("      homochirality (needs a biochemical chiral-autocatalysis net); RPS is not their instance.")
        print("      Does NOT cross frustration-ascent's self-lighting leg (RPS handedness is wired, not an SSB).")
    else:
        print("\n  ==> CLEAN MISS on at least one criterion -- do NOT cross; report the miss (it sharpens the gate).")


if __name__ == "__main__":
    main()
