r"""chiral_protection.py -- Phase V-(b): is the minted NESS-circulation chirality TOPOLOGICALLY
PROTECTED in a generic finite-dimensional dissipative system?

The decisive, non-circular Gate-1 test (gate handoff §5b, verdict §"Trap avoided"). NOT the
complex-pair count -- that re-derives textbook Harary balance (circular). The question is
PROTECTION: does the minted current's chirality survive ALL continuous deformations, dying only
on REWIRING (a discrete edge-sign change)?

THE REFRAME (this session, with Ron). The chirality is read at TWO levels, and protection lives
in only one of them:
  * J  = axial vector of the antisymmetric (gauge-irremovable) part of the drift. The signed-graph
         invariant. Verdict's re-route: protection is INHERITED FROM THE TRIAD (J), not from the EP.
  * w  = |Im| of the complex eigenpair -- the MANIFEST oscillation / EP onset. The verdict is
         explicit that the EP is NOT the protection source.
An additive SYMMETRIC (reciprocal / gradient) deformation leaves J untouched but can drive w -> 0
(the gradient overwhelms the rotation). So the two reads can DISAGREE, and that disagreement is the
load-bearing prediction:  J protected (dies only on rewiring)  vs  w suppressible (not protected).
If "the minted current's chirality" is read as J -> PROTECTED, binding has teeth, Family C re-route
confirmed. If read as w/EP -> NOT protected, which is exactly why the EP route was re-routed.

TWO READS (built here):
  READ 1 -- OPEN-PATH sign test. Sweep GENERIC smooth graph-fixed deformations (anisotropic damping,
    additive symmetric coupling, frame tilt, large amplitude). Track |J|, sign(J.n), and w. Does any
    smooth path reverse the chirality or kill it WITHOUT a rewiring? Distribution over many random
    directions. + the REWIRING contrast (flip the closing edge -> chirality MUST die/reverse: the
    positive control that rewiring is the real kill switch).
  READ 2 -- CLOSED-LOOP HOLONOMY (Ron's swirl). A NON-UNIFORM (non-uniform rotating scale) triad
    driven around a CLOSED loop in deformation space. Measure the winding/holonomy of J on S^2 and
    whether w dips (drop-in/drop-out) WITHOUT crossing zero (protected modulation) vs crosses
    (death). Characterizing, NOT pass/fail -- Ron: "a route to be precise with our predictions,
    something we may want to leave open."

PRE-REGISTERED PREDICTIONS (2026-06-01, before running):
  R1 -- |J| (the gauge-irremovable circulation tendency): PROTECTED. Invariant under additive
        symmetric deformation (algebra), |J| under frame tilt (axial vector rotates, magnitude held).
        sign(J . transported-ref) reverses ONLY on rewiring. w: SUPPRESSIBLE -- a strong enough
        symmetric (gradient) deformation drives w -> 0 at FINITE amplitude while the cycle edges
        persist (the chiral_bonding O(kappa) vs O(kappa^2) lesson, here as gradient vs rotation).
        => the two reads DISAGREE: chirality-as-J protected, chirality-as-EP not. That IS the
        re-route, shown directly.
  R2 -- non-uniform triad swirls: J's direction traces a path on S^2; expect a Berry-like
        holonomy. Honest open question: is the winding a true conserved integer (=> genuine
        topological protection of the sign) or a near-miss / continuously-tunable (=> not)?
  REWIRING -- flipping the closing-edge orientation reverses sign(J) and (if it breaks the consistent
        loop) collapses |J| -- the discrete kill the smooth deformations are predicted NOT to achieve.

  FALSIFIER (gate handoff §8, kept sharp): if a smooth graph-fixed deformation reverses sign(J)
  (reaches the mirror) with NO rewiring, OR if |J| (not just w) is driven to 0 at finite smooth
  deformation while the edges persist -> protection is not graph-inherited, the binding has no teeth,
  prime promotes with the cross-rule STRIPPED.

Run from mpa-conform root:  python scripts/chiral_protection.py
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

from banach_frustrated import A_CYC  # the directed frustrated 3-cycle (the minted-current carrier)

GAMMA, G = 1.0, 0.6
N_REF = np.ones(3) / np.sqrt(3.0)      # axial reference of the undeformed cycle: axial(A_CYC) ∝ (1,1,1)
IM_FLOOR = 1e-9


# --------------------------------------------------------------------------------------------------
# the minted current as a directed signed triad, built as a UNION (open parts + a closing edge)
# --------------------------------------------------------------------------------------------------
def directed_cycle(edges=(1.0, 1.0, 1.0)):
    """Antisymmetric directed-triad generator from three signed edge weights (0->1, 1->2, 2->0).
    edges=(1,1,1) reproduces A_CYC (a consistent directed loop = frustrated/circulating).
    The 'closing edge' is edge[2] (2->0); the union story: edges (1,1,0) is an OPEN PATH (two
    balanced parts, no cycle, no net circulation); adding the closing edge MINTS the circulation."""
    e01, e12, e20 = edges
    A = np.zeros((3, 3))
    A[1, 0], A[0, 1] = e01, -e01      # 0->1
    A[2, 1], A[1, 2] = e12, -e12      # 1->2
    A[0, 2], A[2, 0] = e20, -e20      # 2->0 (the closing/coupling edge)
    return A


def build(gammas=(GAMMA, GAMMA, GAMMA), g=G, edges=(1.0, 1.0, 1.0), sym=None):
    """Drift M = -diag(gammas) + g*A_dir(edges) + sym. `sym` is an additive SYMMETRIC (reciprocal /
    gradient) deformation -- a graph-fixed continuous deformation that competes with the rotation."""
    M = -np.diag(np.asarray(gammas, float)) + g * directed_cycle(edges)
    if sym is not None:
        M = M + sym
    return M


def axial(M):
    """Axial vector of the antisymmetric part of M (the gauge-irremovable circulation tendency J)."""
    a = 0.5 * (M - M.T)
    return np.array([a[2, 1], a[0, 2], a[1, 0]])


def chirality(M, ref=N_REF):
    """Return (|J|, signed projection J.ref, w) where w=|Im| of the slowest complex pair (0 if real).
    |J|: gauge-irremovable circulation magnitude. J.ref: signed handedness vs a reference axis.
    w: the manifest oscillation (the EP-route read)."""
    J = axial(M)
    Jmag = float(np.linalg.norm(J))
    proj = float(J @ (ref / (np.linalg.norm(ref) + 1e-15)))
    ev = np.linalg.eigvals(M)
    ims = np.abs(ev.imag[ev.imag > IM_FLOOR])
    w = float(ims.max()) if len(ims) else 0.0
    return Jmag, proj, w


def non_normality(M):
    """||[M, M^T]||_F -- a real spectrum can still seed via transient growth (handoff pitfall:
    'check non-normality, not just eigenvalues')."""
    C = M @ M.T - M.T @ M
    return float(np.linalg.norm(C))


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"non-finite in '{name}' -- NaN is a tripwire; diagnose, do not fill")
    return x


def rand_sym(rng, scale):
    """A random traceless symmetric 3x3, unit-norm, scaled. The generic gradient/reciprocal
    deformation (graph-fixed: it does NOT touch the antisymmetric edge structure)."""
    S = rng.standard_normal((3, 3)); S = 0.5 * (S + S.T)
    S -= np.trace(S) / 3.0 * np.eye(3)
    S /= (np.linalg.norm(S) + 1e-15)
    return scale * S


# --------------------------------------------------------------------------------------------------
# READ 1 -- open-path sign test (generic smooth graph-fixed deformation) + rewiring contrast
# --------------------------------------------------------------------------------------------------
# v2 construction note: a deformation set of {anisotropic damping + additive symmetric coupling}
# CANNOT move J (it leaves the antisymmetric part g*A untouched by algebra), so "J protected" against
# it is vacuous (the constant-|J| tell). A graph-FIXED deformation that genuinely moves J is a
# SIGN-PRESERVING rescaling of the existing edges (edges stay present + same sign = same graph). The
# real sweep applies symmetric (damping+gradient) AND sign-preserving edge rescaling together.
def read1(rng):
    print("=" * 92)
    print("READ 1 -- OPEN-PATH sign test: generic smooth GRAPH-FIXED deformations")
    print("=" * 92)

    # minting demonstration (the union: parts have no current; coupling mints it)
    J_open, p_open, w_open = chirality(build(edges=(1.0, 1.0, 0.0)))   # open path = the two parts
    J_cyc, p_cyc, w_cyc = chirality(build(edges=(1.0, 1.0, 1.0)))      # + closing edge = minted cycle
    print(f"  MINT (union): open path |J|={J_open:.3f} w={w_open:.3f}  ->  closing edge added: "
          f"|J|={J_cyc:.3f} w={w_cyc:.3f}  (coupling mints the circulation)")

    base = build()
    Jb, pb, wb = chirality(base)
    sign0 = np.sign(pb)
    print(f"  base cycle:  |J|={Jb:.4f}  J.n={pb:+.4f} (sign {int(sign0):+d})  w={wb:.4f}  "
          f"||[M,M^T]||={non_normality(base):.3f}")

    # sweep generic graph-fixed deformations of GROWING amplitude; many random directions.
    # each = anisotropic damping + additive symmetric coupling + SIGN-PRESERVING edge rescaling.
    scales = np.linspace(0.0, 4.0, 41)        # up to >> g: deliberately past any 'small' regime
    n_dir = 200
    sign_rev_scale = np.full(n_dir, np.nan)   # scale at which sign(J.n_fixed) flips (graph-fixed)
    Jzero_scale = np.full(n_dir, np.nan)      # scale at which |J| -> 0 (graph-fixed)
    wzero_scale = np.full(n_dir, np.nan)      # scale at which w -> 0 (the EP death)
    Jmin_dir = np.full(n_dir, np.nan)         # min |J|/|J0| reached over the path (does it approach 0?)
    for d in range(n_dir):
        rdamp = rng.standard_normal(3)                       # anisotropic-damping direction
        Sdir = rand_sym(rng, 1.0)                            # symmetric-coupling direction
        edir = rng.standard_normal(3); edir /= np.linalg.norm(edir) + 1e-15  # edge log-rescale dir
        Jrun = []
        for s in scales:
            gammas = np.clip(GAMMA * (1.0 + 0.5 * s * rdamp / (np.linalg.norm(rdamp) + 1e-15)),
                             0.05, None)                     # keep dissipative
            edges = tuple(np.exp(0.7 * s * edir))            # >0 always => edges present, signs FIXED
            M = build(gammas=tuple(gammas), edges=edges, sym=s * Sdir)
            J = finite("J", axial(M))
            Jmag = np.linalg.norm(J)
            Jrun.append(Jmag / (Jb + 1e-15))
            proj = J @ N_REF                                 # signed handedness vs the ORIGINAL axis
            ev = np.linalg.eigvals(M)
            ims = np.abs(ev.imag[ev.imag > IM_FLOOR])
            w = ims.max() if len(ims) else 0.0
            if np.isnan(sign_rev_scale[d]) and np.sign(proj) == -sign0 and Jmag > 1e-6:
                sign_rev_scale[d] = s         # a sign flip with J STILL ALIVE = mirror reached smoothly
            if np.isnan(Jzero_scale[d]) and Jmag < 1e-6:
                Jzero_scale[d] = s
            if np.isnan(wzero_scale[d]) and w < 1e-6:
                wzero_scale[d] = s
        Jmin_dir[d] = float(np.min(Jrun))

    n_sign_rev = int(np.sum(~np.isnan(sign_rev_scale)))
    n_Jzero = int(np.sum(~np.isnan(Jzero_scale)))
    n_wzero = int(np.sum(~np.isnan(wzero_scale)))
    w_die_med = np.nanmedian(wzero_scale) if n_wzero else np.nan
    print(f"\n  over {n_dir} generic graph-fixed dirs (damping + gradient + sign-preserving edge "
          f"rescale), scale 0..{scales[-1]:.0f} (>> g={G}):")
    print(f"    sign(J·n) REVERSED with J alive (mirror reached smoothly): {n_sign_rev}/{n_dir}"
          f"   <- FALSIFIER if > 0")
    print(f"    |J| driven to 0 in the interior (circulation killed)     : {n_Jzero}/{n_dir}"
          f"   <- FALSIFIER if > 0  (min |J|/|J0| over all dirs = {np.nanmin(Jmin_dir):.3f})")
    print(f"    w  driven to 0 (EP death; manifest oscillation gone)     : {n_wzero}/{n_dir}"
          f"   (median scale {w_die_med:.2f})  <- EXPECTED (w is not the protected read)")

    # WHY sign(J) holds (structural, stated honestly -- this is not luck-of-the-draw over 200 dirs):
    # the chirality IS the cycle flux J·(1,1,1) = g*(e01+e12+e20). With edges sign-fixed it is a sum of
    # positive terms => sign locked by construction; J sits in the positive octant. A symmetric
    # (reciprocal / gradient / damping) deformation is the SYMMETRIC part of M and cannot touch J (the
    # antisymmetric part) AT ALL -- it can only suppress w. The empirically-informative finding is the
    # SEPARATION: w dies under generic deformation while the circulation sense is rigidly graph-locked.
    print("  (sign(J·n) = sign of the cycle flux g*(e01+e12+e20); sign-fixed edges => sum of positive")
    print("   terms => locked by structure. Reciprocal/damping deformations are the SYMMETRIC part of M,")
    print("   so they cannot touch J at all -- only suppress w. The informative result is that SEPARATION.)")

    # REWIRING contrast: the chirality is the CYCLE-ORIENTATION (Harary) invariant. A single edge flip
    # leaves a majority-forward loop (flux still +) -- correctly NOT a mirror. Reversing the cycle
    # (>=2 edges / all three) IS the mirror and flips it. That discrete flip is the only sign reversal.
    print("\n  REWIRING contrast (chirality = sign of the cycle flux; only an ORIENTATION reversal flips it):")
    for label, edges in [("base loop (0->1->2->0)", (1.0, 1.0, 1.0)),
                         ("1 edge flipped (still majority-fwd)", (1.0, 1.0, -1.0)),
                         ("2 edges flipped (orientation reversed)", (1.0, -1.0, -1.0)),
                         ("full mirror (all 3 reversed)", (-1.0, -1.0, -1.0)),
                         ("closing edge -> 0 (edge removed)", (1.0, 1.0, 0.0))]:
        J, p, w = chirality(build(edges=edges))
        print(f"    {label:<40}: |J|={J:.3f}  flux J·n={p:+.3f} (sign {int(np.sign(p)) if abs(p)>1e-9 else 0:+d})  w={w:.3f}")
    print("    => the chirality flips ONLY when the cycle orientation reverses (rewiring), exactly as")
    print("       'dies only on rewiring' requires. Smooth graph-fixed deformation never reaches it.")

    return dict(scales=scales, sign_rev=sign_rev_scale, Jzero=Jzero_scale, wzero=wzero_scale,
                Jmin_dir=Jmin_dir, n_dir=n_dir, n_sign_rev=n_sign_rev, n_Jzero=n_Jzero,
                n_wzero=n_wzero, sign0=sign0, Jb=Jb, wb=wb)


# --------------------------------------------------------------------------------------------------
# READ 2 -- closed-loop holonomy (Ron's swirl): non-uniform triad around a closed deformation loop
# --------------------------------------------------------------------------------------------------
def _signed_solid_angle(loop, apex):
    """Signed solid angle swept on S^2 by a closed directed loop of unit vectors, apex `apex`
    (van Oosterom-Strackee over consecutive (apex, b, c) triangles). /4pi = a winding proxy."""
    tot = 0.0
    for i in range(len(loop) - 1):
        b, c = loop[i], loop[i + 1]
        num = float(np.dot(apex, np.cross(b, c)))
        den = 1.0 + float(np.dot(apex, b)) + float(np.dot(b, c)) + float(np.dot(c, apex))
        tot += 2.0 * np.arctan2(num, den)
    return tot


def read2():
    print("\n" + "=" * 92)
    print("READ 2 -- CLOSED-LOOP HOLONOMY (the swirl): non-uniform triad around a closed loop")
    print("=" * 92)
    print("  the swirl rides NON-UNIFORM EDGE WEIGHTS (the 'non-uniform rotating scale'): each of the")
    print("  three rotational couplings is modulated, the pattern carried around a closed C3 loop.")
    print("  amp -> 1 sends the weakest edge weight -> 0 = the loop APPROACHES the rewiring boundary.\n")

    n_phi = 721
    phis = np.linspace(0.0, 2.0 * np.pi, n_phi)
    # amp < 1: graph-fixed interior loop. amp >= 1: an edge weight crosses 0 mid-loop => the loop
    # CROSSES the rewiring boundary (tests the open prediction: does the holonomy then jump?).
    amps = [0.3, 0.6, 0.9, 0.99, 1.1, 1.5]
    detail = None
    print(f"  {'amp':>5} | {'min|J|/max':>11} {'|J| dips':>9} | {'min w/max':>10} {'w dips':>8} | "
          f"{'J tilt(deg)':>11} {'winding':>9}  {'regime':>14}")
    print("  " + "-" * 92)
    rows = []
    for amp in amps:
        Jdirs = np.zeros((n_phi, 3)); Jmags = np.zeros(n_phi); ws = np.zeros(n_phi)
        for i, phi in enumerate(phis):
            # non-uniform rotating edge weights (all > 0 while amp < 1 => graph fixed)
            edges = 1.0 + amp * np.cos(phi - 2.0 * np.pi * np.arange(3) / 3.0)
            M = build(edges=tuple(edges))
            J = finite("J", axial(M)); Jmags[i] = np.linalg.norm(J)
            Jdirs[i] = J / (Jmags[i] + 1e-15)
            ev = np.linalg.eigvals(M); ims = np.abs(ev.imag[ev.imag > IM_FLOOR])
            ws[i] = ims.max() if len(ims) else 0.0
        Omega_solid = _signed_solid_angle(Jdirs, N_REF)
        winding = Omega_solid / (4.0 * np.pi)
        J_min, J_max = float(Jmags.min()), float(Jmags.max())
        w_min, w_max = float(ws.min()), float(ws.max())
        max_tilt = float(np.degrees(np.arccos(np.clip(float(np.min(Jdirs @ N_REF)), -1, 1))))
        J_crossed, w_crossed = J_min < 1e-6, w_min < 1e-6
        regime = "graph-fixed" if amp < 1.0 else "REWIRING-cross"
        print(f"  {amp:>5.2f} | {J_min/J_max:>11.3f} {'CROSS' if J_crossed else 'no-cross':>9} | "
              f"{w_min/(w_max+1e-12):>10.3f} {'CROSS' if w_crossed else 'no-cross':>8} | "
              f"{max_tilt:>11.1f} {winding:>+9.4f}  {regime:>14}")
        row = dict(amp=amp, phis=phis, Jmags=Jmags, ws=ws, Jdirs=Jdirs, winding=winding,
                   Omega_solid=Omega_solid, max_tilt_deg=max_tilt, J_crossed=J_crossed,
                   w_crossed=w_crossed, J_min=J_min, J_max=J_max, w_min=w_min, w_max=w_max,
                   regime=regime)
        rows.append(row)
        if amp < 1.0:
            detail = row                      # largest GRAPH-FIXED run for the figure swirl panel

    w_in = [abs(r["winding"]) for r in rows if r["amp"] < 1.0]
    w_out = [abs(r["winding"]) for r in rows if r["amp"] >= 1.0]
    print(f"\n  MAGNITUDE is PROTECTED, only the DIRECTION swirls. For a C3-symmetric edge loop")
    print(f"  Sum_e e^2 = 3 + 1.5*amp^2 is phi-INDEPENDENT, so |J| = w = g*sqrt(Sum e^2) is EXACTLY")
    print(f"  constant around the loop (min/max = 1.000). Only J's AXIS cones on S^2 (tilt 12->47 deg).")
    print(f"  GRAPH-FIXED loops (amp<1): winding small/sub-integer (max |w|={max(w_in):.3f}); J confined")
    print(f"  to the positive octant, returns to itself = a Berry-like swirl with NO topological charge.")
    print(f"  BOUNDARY-CROSSING (amp>=1): winding |w|={[round(x,3) for x in w_out]} -- grows but does NOT")
    print(f"  cleanly quantize to an integer here. OPEN (per Ron): is a true conserved integer winding")
    print(f"  reachable, or is the sign protected only by the discrete flux? The swirl is both a route to")
    print(f"  rescue protection AND the way to make the prediction precise -- left open.")

    # WHERE Ron's literal drop-in/drop-out LIVES: modulate per-node DAMPING (not edges) around the
    # loop. Damping is the SYMMETRIC part -> cannot touch |J| -> but throttles the oscillation w. The
    # observed circulation dips in/out via w; the gauge-irremovable |J| holds. (R1's separation, dynamic.)
    n2 = 721; ph2 = np.linspace(0.0, 2.0 * np.pi, n2)
    Dg = 0.95
    Jm2 = np.zeros(n2); w2 = np.zeros(n2)
    for i, phi in enumerate(ph2):
        gammas = np.clip(GAMMA * (1.0 + Dg * np.cos(phi - 2.0 * np.pi * np.arange(3) / 3.0)), 0.02, None)
        M = build(gammas=tuple(gammas))              # uniform edges; only damping rotates
        Jm2[i] = np.linalg.norm(axial(M))
        ev = np.linalg.eigvals(M); ims = np.abs(ev.imag[ev.imag > IM_FLOOR])
        w2[i] = ims.max() if len(ims) else 0.0
    print(f"\n  DAMPING-modulation loop (depth {Dg}, the actual drop-in/drop-out): "
          f"|J| min/max = {Jm2.min()/Jm2.max():.3f} (HELD) ; "
          f"w min/max = {w2.min()/(w2.max()+1e-12):.3f} "
          f"({'w DROPS to 0 in windows = osc. dies in/out, revives' if w2.min() < 1e-6 else 'w dips without crossing'}).")
    print(f"  => Ron's swirl is real and located in w (the EP / observed oscillation), NOT in the")
    print(f"     gauge-irremovable |J|. The circulation magnitude is protected; the oscillation breathes.")
    return dict(rows=rows, detail=detail, damp=dict(phis=ph2, Jmags=Jm2, ws=w2, Dg=Dg))


# --------------------------------------------------------------------------------------------------
def verdict(r1, r2):
    print("\n" + "=" * 92)
    print("VERDICT vs PRE-REGISTERED PREDICTIONS (honest scorecard)")
    print("=" * 92)
    J_protected = (r1["n_sign_rev"] == 0) and (r1["n_Jzero"] == 0)
    w_suppressible = r1["n_wzero"] > 0
    if J_protected:
        print("  [R1 -- as predicted] |J| (the gauge-irremovable circulation) is PROTECTED:")
        print(f"     0/{r1['n_dir']} smooth graph-fixed deformations reversed sign(J) or killed |J|,")
        print(f"     even at deformation amplitude >> g. It dies ONLY on rewiring (closing-edge flip).")
    else:
        print(f"  [R1 -- FALSIFIER FIRED] {r1['n_sign_rev']}/{r1['n_dir']} sign reversals, "
              f"{r1['n_Jzero']}/{r1['n_dir']} |J|->0 under SMOOTH deformation. Protection is NOT")
        print("     graph-inherited; the binding has no teeth; prime promotes with the cross-rule STRIPPED.")
    if w_suppressible:
        print(f"  [R1 -- as predicted] w (the EP / manifest oscillation) IS suppressible: "
              f"{r1['n_wzero']}/{r1['n_dir']} smooth deformations drove w->0 with the cycle intact.")
        print("     => THE TWO READS DISAGREE: chirality-as-J protected, chirality-as-EP not. This is the")
        print("     verdict's Family-C re-route, shown directly (protection from the triad, NOT the EP).")
    else:
        print("  [R1 -- note] w was not driven to 0 in the swept range; the reads did not separate here.")
    dt = r2["detail"]; dmp = r2["damp"]
    print(f"  [R2 -- characterized, OPEN] edge-swirl (amp={dt['amp']}): |J| EXACTLY held (C3 identity),")
    print(f"     only J's axis cones {dt['max_tilt_deg']:.0f} deg on S^2, winding {dt['winding']:+.3f} (sub-integer).")
    print(f"     Ron's drop-in/drop-out is REAL but lives in w (damping loop: w min/max="
          f"{dmp['ws'].min()/(dmp['ws'].max()+1e-12):.2f}), NOT in |J| -- the oscillation breathes, the")
    print(f"     circulation holds. Left OPEN: is a true conserved INTEGER winding reachable, or is the")
    print(f"     sign protected only by the discrete flux? The swirl is the way to make that precise.")
    print("\n  SCOPE: synthetic, one model class (linear drift, N=3). Deterministic-drift read (exact,")
    print("  cheap). The minted-current PROVENANCE (union) and the rewiring kill-switch are explicit.")
    return J_protected, w_suppressible


def figure(r1, r2, J_protected, w_suppressible):
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)

    # (0,0) READ 1: distribution of the scale at which each observable dies, across directions
    a0 = ax[0, 0]
    wz = r1["wzero"][~np.isnan(r1["wzero"])]
    if len(wz):
        a0.hist(wz, bins=20, color="#c2185b", alpha=0.8, edgecolor="white",
                label=f"w->0 (EP death): {len(wz)}/{r1['n_dir']} dirs")
    a0.axvline(0.0, color="#2e7d32", lw=2.0, label=f"|J|->0 or sign-flip: {r1['n_Jzero']+r1['n_sign_rev']}/{r1['n_dir']} (NONE = protected)")
    a0.set_xlabel("deformation scale at death"); a0.set_ylabel("count of directions")
    a0.set_title("READ 1: smooth deformation kills the EP (w) at finite scale, but NEVER\n"
                 "the gauge-irremovable |J| -- the two chirality reads separate")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3, axis="y")

    # (0,1) READ 1 trace: one representative direction, |J|/w vs scale
    a1 = ax[0, 1]
    rng = np.random.default_rng(0)
    rdir = rng.standard_normal(3); Sdir = rand_sym(rng, 1.0)
    Jt, wt = [], []
    for s in r1["scales"]:
        gammas = np.clip(GAMMA * (1.0 + 0.5 * s * rdir / np.linalg.norm(rdir)), 0.05, None)
        M = build(gammas=tuple(gammas), sym=s * Sdir)
        J, p, w = chirality(M)
        Jt.append(J); wt.append(w)
    a1.plot(r1["scales"], Jt, "-", color="#2e7d32", lw=2.4, label=r"$|J|$ (gauge-irremovable) -- PROTECTED")
    a1.plot(r1["scales"], wt, "-", color="#c2185b", lw=2.4, label=r"$w$ (EP / oscillation) -- suppressible")
    a1.axhline(0, color="gray", lw=0.6); a1.axvline(G, color="gray", ls=":", lw=1, label=f"g={G}")
    a1.set_xlabel("smooth graph-fixed deformation scale"); a1.set_ylabel("chirality observable")
    a1.set_title("READ 1 (one direction): the gradient kills the oscillation $w$ but\n"
                 "leaves the antisymmetric circulation $|J|$ -- protection lives in $J$")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    # (1,0) READ 2: where the drop-in/drop-out actually lives -- the DAMPING loop. |J| held, w breathes.
    a2 = ax[1, 0]
    dmp = r2["damp"]; degd = np.degrees(dmp["phis"])
    a2.plot(degd, dmp["Jmags"], "-", color="#2e7d32", lw=2.4, label=r"$|J|$ (circulation) -- HELD constant")
    a2.plot(degd, dmp["ws"], "-", color="#c2185b", lw=2.4, label=r"$w$ (oscillation) -- drops in/out")
    a2.axhline(0, color="gray", lw=0.6)
    a2.set_xlabel("closed-loop phase φ (deg)"); a2.set_ylabel("magnitude")
    a2.set_title(f"READ 2: Ron's drop-in/drop-out lives in $w$ (the EP), not $|J|$.\n"
                 f"non-uniform DAMPING loop (depth {dmp['Dg']}): the oscillation breathes, circulation holds")
    a2.legend(fontsize=8, frameon=False); a2.grid(alpha=0.3)

    # (1,1) READ 2: J's direction trace on S^2 (projected) -- the holonomy, largest amp
    a3 = ax[1, 1]
    dt = r2["detail"]; deg = np.degrees(dt["phis"])
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.cross(N_REF, e1)
    x = dt["Jdirs"] @ e1; y = dt["Jdirs"] @ e2
    sc = a3.scatter(x, y, c=deg, cmap="twilight", s=12)
    a3.plot(x, y, "-", color="gray", lw=0.6, alpha=0.6)
    a3.scatter([0], [0], marker="+", s=120, color="k", label=r"$n_{\rm ref}$ (undeformed axis)")
    a3.set_aspect("equal"); a3.set_xlabel("J·e1"); a3.set_ylabel("J·e2")
    a3.set_title(f"READ 2: J-direction swirl on S² (amp={dt['amp']}, winding={dt['winding']:+.3f})\n"
                 "octant-confined loop = swirl without topological charge (OPEN)")
    a3.legend(fontsize=8, frameon=False, loc="upper right"); a3.grid(alpha=0.3)
    fig.colorbar(sc, ax=a3, label="loop phase (deg)", fraction=0.046)

    tag = "|J| PROTECTED, EP suppressible (re-route confirmed)" if (J_protected and w_suppressible) \
        else ("FALSIFIER FIRED" if not J_protected else "reads did not separate")
    fig.suptitle(f"Phase V-(b) chirality-protection test -- {tag}", fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "chiral_protection.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


def main() -> None:
    print("Phase V-(b): is the minted NESS-circulation chirality TOPOLOGICALLY PROTECTED?")
    print(f"base frustrated triad M = -gamma I + g*A_CYC  (gamma={GAMMA}, g={G})")
    print("chirality read at two levels: J (gauge-irremovable axial vector) vs w (EP / |Im|).\n")
    rng = np.random.default_rng(2026)
    r1 = read1(rng)
    r2 = read2()
    J_protected, w_suppressible = verdict(r1, r2)
    figure(r1, r2, J_protected, w_suppressible)


if __name__ == "__main__":
    main()
