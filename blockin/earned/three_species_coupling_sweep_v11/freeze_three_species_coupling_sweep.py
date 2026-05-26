"""freeze — three_species_coupling_sweep_v11  (bespoke, one substrate, brittle by design)

The owed v5 vector, spent: a STRUCTURE SWEEP on the Cat-10 (Non-Reciprocal) cyclic current.
v5 swept the NOISE at fixed wiring and found the turnover rate / per-cycle directedness FLAT
(noise-INDEPENDENT) — calming the environment does not slow the loop. But v5 could only answer
the noise counterfactual; it HONESTLY parked the complementary claim: that the rate / affinity
is SET BY THE WIRING — i.e. it TRACKS the coupling structure g/gamma. That park lived across a
collapsed axis (the coupling strength g). This freeze opens that axis: the SAME community, SAME
noise, at five COUPLING strengths, fixed gamma.

Substrate (same as v3/v5): the noisy frustrated Banach-class reference
(mpa-central/library/banach_frustrated.py) — three modes, cyclic non-reciprocal
(rock-paper-scissors) coupling, driven by noise:
    dz = M z dt + sqrt(2D) dW,   M = -gamma I + g A_cyc,
    A_cyc = [[0,-1,1],[1,0,-1],[-1,1,0]]  (antisymmetric circulant).
Eigenvalues of M: -gamma (real), -gamma +/- i*sqrt(3)*g (complex pair = the k_frust current
signature). NOTE: the real part is ALWAYS -gamma, for ANY g -> the cycle is STABLE at every
coupling (no instability edge); only the ROTATION rate omega = sqrt(3) g changes.

THE PHYSICS THE SWEEP READS (exact, linear OU — the current TRACKS the wiring):
  - omega = sqrt(3) g, gam_eff = gamma. So omega/gamma = sqrt(3) (g/gamma) TRACKS the coupling
    LINEARLY: the loop spins faster the stronger the cyclic wiring.
  - <sigma> = 6 g^2 / gamma TRACKS the coupling QUADRATICALLY (entropy production rate).
  - affinity per cycle A = <sigma> * (cycle time) = (6 g^2/gamma) * (2 pi / omega)
    = (12 pi / (sqrt(3) gamma)) g  TRACKS the coupling LINEARLY (each loop more irreversible
    the stronger the wiring).
  - The winding DRIFT (phiMean rate) ~ omega TRACKS g; the directed turnover rate is the wiring.
  So the band is: as the cyclic coupling strengthens, omega/gamma, the drift rate, and the
  affinity all RISE (linearly), <sigma> rises quadratically. The current is SET BY THE
  STRUCTURE. Together with v5 (noise-FLAT) this pins it: the current is the WIRING, not the
  weather.

THE TOOTH (vs v5's flat band, and vs the Cat-1 laser): v5's discriminator was "flat across
noise". v11's is "TRACKS across structure". And the Cat-1/Cat-10 separation survives the whole
sweep: a class-B laser ring-down has the SAME damped-cosine autocorr C, but ZERO current
(Cxy == Cyx). Here Cxy == -Cyx (a real circulating current) at EVERY coupling g>0 — its
MAGNITUDE shrinks as g->0 (the loop opens) but the KIND stays Cat-10 for all g>0 (consistent
with v6: the reciprocity cut is TOPOLOGICALLY sharp — g->0 deletes the loop rather than blurring
the class; only g=0 EXACTLY is Cat-1). The load-bearing result is the TRACKING; the g->0 edge is
a secondary consistency reading, not the claim.

ANCHOR-AND-ASSERT: level 3 is g=0.6 — v3/v5's exact wiring (at the same D=0.1). Its placement
(omega/gamma = sqrt(3)*0.6 = 1.039, sustained current, stable NESS) must reproduce v3/v5's
earned values; the orchestrator checks this at unseal (NOT handed to the blind answerer — that
would leak the anchor). Cheap cross-pass drift detection.

Ground truth is exact (linear OU) + a per-level NESS winding simulation, computed HERE from the
structure, never via conform (data-path independence). Per-level seeded (BASE_SEED + level) so
each level is independently reproducible and the sweep is order-independent.

BLINDING: the emitted CSV carries ONLY (level, coupling_rel, tau, C, chi, Cxy, Cyx, phiMean,
phiVar). coupling_rel is the researcher's OWN control knob — the relative cyclic-interaction
strength they dialed, normalized to their baseline run (level 3 = 1.0x). It carries NO
g/gamma/D, no omega, no entropy rate, no affinity, no eigenvalues, no framework token. Each
level is watched on its OWN clock (its own rotation period sets the window), so tau ranges
differ across levels (the weakly-coupled, slow loops need the longest watching).

Run:  python H:/mpa-conform/blockin/questions/three_species_coupling_sweep_v11/freeze_three_species_coupling_sweep.py

Emits: data/three_species_coupling_sweep_v11.frozen.csv  (the blind artifact)
       prints the SEALED ground truth (per-level placements, the TRACKING band, the anchor
       reproduction, TUR floor) for the author to paste / the human to eyeball. CSV carries none.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov

# reuse the library substrate as the answer-path (the truth, never via conform)
sys.path.insert(0, "H:/mpa-central/library")
import banach_frustrated as bf  # noqa: E402

# fixed noise + relaxation (same D as v3/v5); the SWEEP is over the coupling strength g.
GAMMA, D = 1.0, 0.10
G_SWEEP = [0.15, 0.30, 0.60, 1.20, 2.40]    # cyclic coupling (geometric, 16x span)
ANCHOR_IDX = 2                               # level 3 (1-based) -> g=0.60 == v3/v5's wiring
G_BASE = G_SWEEP[ANCHOR_IDX]                 # baseline for the relative knob
BASE_SEED = 11
N_REAL = 2000
DT = 0.01
N_TAU = 120

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "three_species_coupling_sweep_v11.frozen.csv"

P = bf.P            # 2x3 rotation-plane projector
A_CYC = bf.A_CYC


def level_time_grid(M, omega):
    """Per-level window: watch ~6 of THIS level's own rotation periods, but at least ~8
    relaxation times so the NESS is settled and the loop is clearly resolved. Each coupling
    has its own clock — the weak, slow loops need the longest watching (correct camera, not
    an artifact)."""
    ev = np.linalg.eigvals(M)
    slowest = float(-np.max(ev.real))            # = gamma (real part is -gamma for all g)
    t_settle = 8.0 / slowest
    t_rot = 6.0 * (2.0 * np.pi / omega) if omega > 1e-9 else t_settle
    t_max = max(t_settle, t_rot)
    return np.linspace(t_max / 400.0, t_max, N_TAU)


def resolved_winding(M, t_grid, rng, n_real=N_REAL, dt=DT):
    """Tau-resolved ensemble winding in the rotation plane: cumulative net turnover angle
    phi(tau) over elapsed observation time, sampled on t_grid. Mean = the directed current
    rate (drift), Var = the diffusive spread. DRIFT ~ omega TRACKS the coupling g."""
    sd = np.sqrt(2.0 * D * dt)
    z = rng.standard_normal((n_real, 3)) * np.sqrt(D)
    for _ in range(3000):                                  # equilibrate to the NESS
        z = z + (z @ M.T) * dt + rng.standard_normal((n_real, 3)) * sd
    steps = np.maximum(1, np.round(t_grid / dt).astype(int))
    n_steps = int(steps[-1])
    u = z @ P.T
    phi = np.zeros(n_real)
    mean = np.empty_like(t_grid)
    var = np.empty_like(t_grid)
    k = 0
    for s in range(1, n_steps + 1):
        z = z + (z @ M.T) * dt + rng.standard_normal((n_real, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        u = un
        while k < len(steps) and steps[k] == s:
            mean[k] = phi.mean()
            var[k] = phi.var(ddof=1)
            k += 1
    return bf.finite("phiMean", mean), bf.finite("phiVar", var)


def plane_correlations(M, Sigma, t):
    """Exact OU two-point functions projected onto the rotation plane. Normalized C
    (symmetric autocorr), chi (integrated x-response), and the two directed cross-
    correlations Cxy, Cyx. The damped-cosine FREQUENCY = omega TRACKS g, so the SHAPE
    itself carries the structure-dependence (unlike v5 where it was level-invariant)."""
    c0 = P @ Sigma @ P.T
    scale = 0.5 * (c0[0, 0] + c0[1, 1])
    C = np.empty_like(t); Cxy = np.empty_like(t); Cyx = np.empty_like(t); Rxx = np.empty_like(t)
    for i, ti in enumerate(t):
        Pr = expm(M * ti)
        c = P @ Pr @ Sigma @ P.T
        r = P @ Pr @ P.T
        C[i] = 0.5 * (c[0, 0] + c[1, 1]) / scale
        Cxy[i] = c[0, 1] / scale
        Cyx[i] = c[1, 0] / scale
        Rxx[i] = r[0, 0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (Rxx[1:] + Rxx[:-1]) * np.diff(t))])
    return C, chi, Cxy, Cyx


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    rows = []      # (level, coupling_rel, tau, C, chi, Cxy, Cyx, phiMean, phiVar)
    seal = []      # per-level sealed scalars
    for lvl, g in enumerate(G_SWEEP, start=1):
        M, sigma, ev, omega, gam_eff = bf.exact(GAMMA, g, D)
        t = level_time_grid(M, omega)
        Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
        C, chi, Cxy, Cyx = plane_correlations(M, Sigma, t)
        rng = np.random.default_rng(BASE_SEED + lvl)                 # per-level seed
        phiMean, phiVar = resolved_winding(M, t, rng)
        m = bf.measure(GAMMA, g, D, np.random.default_rng(BASE_SEED + 100 + lvl))  # canonical cross-check
        coupling_rel = g / G_BASE
        for j in range(len(t)):
            rows.append((lvl, coupling_rel, t[j], C[j], chi[j], Cxy[j], Cyx[j], phiMean[j], phiVar[j]))
        tau_obs = float(t[-1])
        Jbar, Jvar = float(phiMean[-1]), float(phiVar[-1])
        drift_rate = Jbar / tau_obs
        cycles = abs(Jbar) / (2.0 * np.pi)
        A_inslice = sigma * tau_obs / cycles if cycles > 1e-9 else float("nan")
        asym_peak = float(np.max(np.abs(Cxy - Cyx)))
        seal.append(dict(lvl=lvl, g=g, coupling_rel=coupling_rel, omega=omega, gam_eff=gam_eff,
                         ratio=omega / gam_eff, sigma=sigma, drift=drift_rate, Jbar=Jbar,
                         Jvar=Jvar, A=A_inslice, A_cross=m["A"], T_cross=m["T"],
                         tur_ok=m["tur_ok"], asym=asym_peak, tau_obs=tau_obs))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# three_species_coupling_sweep_v11 — ONE cyclic community, FIVE cyclic-coupling\n")
        f.write("# strengths (the researcher's own interaction-strength knob; level 3 = their\n")
        f.write("# baseline run). The environment/noise is the SAME at every level.\n")
        f.write("# columns: level (1..5, ordered weak->strong coupling), coupling_rel (relative\n")
        f.write("#          cyclic-interaction strength, normalized to the baseline level 3 = 1.0x),\n")
        f.write("#          tau (community clock — a lag for the two-point columns, elapsed time for\n")
        f.write("#          the winding columns), C (normalized rotation-plane autocorr), chi\n")
        f.write("#          (integrated response), Cxy / Cyx (the two directed cross-correlations\n")
        f.write("#          between the two community-rotation axes), phiMean / phiVar (mean and\n")
        f.write("#          variance of the cumulative net turnover angle up to elapsed tau).\n")
        f.write("# All columns dimensionless (angle in radians). Five operating points (a sweep).\n")
        f.write("# Each level watched on its OWN clock, so tau ranges differ (slow loops watched longer).\n")
        f.write("# Generated by the community's own linear NESS propagator + per-level sim — not via conform.\n")
        f.write("level,coupling_rel,tau,C,chi,Cxy,Cyx,phiMean,phiVar\n")
        for lvl, cr, ti, ci, xi, cxy, cyx, pm, pv in rows:
            f.write(f"{lvl},{cr:.4f},{ti:.6f},{ci:.6f},{xi:.6f},{cxy:.6f},{cyx:.6f},{pm:.6f},{pv:.6f}\n")

    # ---- sealed report (author + human-eyeball only; NOT in the CSV) ----
    ratio_arr = np.array([s["ratio"] for s in seal])
    drift_arr = np.array([s["drift"] for s in seal])
    A_arr = np.array([s["A"] for s in seal])
    sigma_arr = np.array([s["sigma"] for s in seal])
    g_arr = np.array([s["g"] for s in seal])

    print("=== SEALED ground truth (author + human-eyeball only — NOT in the CSV) ===")
    print(f"substrate: noisy frustrated N=3 cyclic non-reciprocal OU, FIXED noise (D={D}), "
          f"gamma={GAMMA}; SWEEP over coupling g = {G_SWEEP}")
    print("M depends on g -> omega = sqrt(3) g TRACKS the coupling; real part = -gamma for ALL g")
    print("(stable at every coupling, no instability edge). Per-level placements:")
    hdr = (f"  {'lvl':>3} {'g':>5} {'coup_rel':>8} {'omega/gam':>10} {'<sigma>':>9} "
           f"{'drift~om':>9} {'phiMean':>8} {'affinity':>9} {'|Cxy-Cyx|':>10} {'tur':>4}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for s in seal:
        mark = "<= ANCHOR (==v3/v5, g=0.6)" if s["lvl"] == ANCHOR_IDX + 1 else ""
        print(f"  {s['lvl']:>3} {s['g']:>5.2f} {s['coupling_rel']:>8.2f} {s['ratio']:>10.4f} "
              f"{s['sigma']:>9.4f} {s['drift']:>9.3f} {s['Jbar']:>8.1f} {s['A']:>9.2f} "
              f"{s['asym']:>10.4f} {'ok' if s['tur_ok'] else 'XX':>4}  {mark}")
    print()
    # tracking checks: omega/gamma linear in g, <sigma> quadratic in g, drift linear in g
    ratio_over_g = ratio_arr / g_arr            # should be ~constant sqrt(3)=1.732
    sigma_over_g2 = sigma_arr / g_arr**2        # should be ~constant 6/gamma=6.0
    drift_over_omega = drift_arr / ratio_arr    # drift rate / omega (gam=1) -> ~constant
    print("THE BAND (the story — the current TRACKS the wiring):")
    print(f"  omega/gamma:   {[round(s['ratio'],3) for s in seal]}  -> RISES ~LINEARLY with g "
          f"(omega/gam / g = {ratio_over_g.mean():.3f} +/- {100*ratio_over_g.std()/ratio_over_g.mean():.1f}%, = sqrt(3))")
    print(f"  drift rate:    {[round(s['drift'],3) for s in seal]}  -> RISES with g, tracks omega "
          f"(drift/omega = {drift_over_omega.mean():.3f} +/- {100*drift_over_omega.std()/abs(drift_over_omega.mean()):.1f}%)")
    print(f"  <sigma>:       {[round(s['sigma'],3) for s in seal]}  -> RISES ~QUADRATICALLY with g "
          f"(<sigma>/g^2 = {sigma_over_g2.mean():.3f} +/- {100*sigma_over_g2.std()/sigma_over_g2.mean():.1f}%, = 6/gamma)")
    print(f"  affinity/cyc:  {[round(s['A'],2) for s in seal]}  -> RISES ~LINEARLY with g "
          f"(each loop more irreversible the stronger the wiring)")
    print(f"  |Cxy-Cyx| peak: {[round(s['asym'],3) for s in seal]}  -> current MAGNITUDE grows with g; "
          f"Cxy==-Cyx (a real current) at EVERY g>0 (Cat-10 stays sharp; g->0 shrinks it, doesn't blur)")
    print()
    print("VERDICT (researcher terms): strengthening the cyclic (rock-paper-scissors) interaction")
    print("  SPEEDS UP the turnover — the loop spins faster the stronger the wiring (rate ~ g), and")
    print("  each loop is more irreversible (affinity ~ g; dissipation ~ g^2). Weakening it slows the")
    print("  loop toward a crawl (and at zero coupling there is no loop at all). The turnover rate is")
    print("  SET BY THE WIRING. With v5 (rate FLAT across noise) this pins it: the current is the")
    print("  WIRING, not the weather. v5's parked structure-dependence, now GROUNDED by the g-sweep.")
    print(f"ANCHOR: level 3 (coupling_rel=1.0, g=0.6) is v3/v5's exact point — omega/gamma "
          f"{seal[ANCHOR_IDX]['ratio']:.3f} (sqrt(3)*0.6=1.039), current present, stable. Reproduce at unseal.")
    print()
    print("GROUNDED (the sweep spans the coupling axis -> structure-dependence now GROUNDED):")
    print("  omega/gamma, drift rate, affinity all TRACK g (linearly); <sigma> tracks g^2; the current")
    print("  magnitude |Cxy-Cyx| grows with g; the Cat-1/Cat-10 separation (Cxy != Cyx) holds at every")
    print("  g>0; the two-frame TUR floor T>=1 holds at every level.")
    print("NOT GROUNDED (honest parks, across DIFFERENT collapsed axes):")
    print("  - absolute g/gamma in native units (only the RELATIVE coupling knob is in the data; the")
    print("    proportionality CONSTANT in native units is not blind-closeable — v7/v8/v9 native-unit limit).")
    print("  - the cdv1 'J flows with chit, affinity FIXED' claim: that needs the NONLINEAR")
    print("    (Stuart-Landau-cyclic, gain+saturation) extension — this LINEAR model has affinity ~ g")
    print("    (no amplitude/chit knob). A collapsed model-class axis, not under-provisioning.")
    print("  - the g=0 boundary itself (pure relaxation, Cat-1): approached (rate->0) but not sampled.")

    # self-consistency assertions (author-side; the sealed key must hold together)
    for s in seal:
        ev = np.linalg.eigvals(bf.exact(GAMMA, s["g"], D)[0])
        assert np.sum(np.abs(ev.imag) > 1e-9) == 2, "must have a complex eigenvalue PAIR at every g"
        assert np.all(ev.real < 0), "all modes damped (stable NESS) at every g"
    assert ratio_over_g.std() / ratio_over_g.mean() < 0.02, "omega/gamma must be LINEAR in g (sqrt(3))"
    assert sigma_over_g2.std() / sigma_over_g2.mean() < 0.02, "<sigma> must be QUADRATIC in g (6/gamma)"
    assert np.all(np.diff(ratio_arr) > 0), "omega/gamma must RISE monotonically with g (tracking)"
    assert np.all(np.diff([s['asym'] for s in seal]) > 0), "current magnitude must rise with g"
    assert all(s["tur_ok"] for s in seal), "TUR floor T>=1 must hold at every level (T<1 = KILL)"
    assert all(s["Jbar"] > 5.0 for s in seal), "winding drift resolved clearly nonzero at every level"
    assert abs(ratio_over_g.mean() - np.sqrt(3.0)) < 0.02, "omega/gamma/g must equal sqrt(3)"
    assert abs(sigma_over_g2.mean() - 6.0 / GAMMA) < 0.05, "<sigma>/g^2 must equal 6/gamma"
    print("\nself-consistent: complex pair + all-damped at every g + omega/gamma=sqrt(3)*g (linear) "
          "+ <sigma>=6g^2/gamma (quadratic) + rising current + TUR holds. OK.")
    print(f"wrote {OUT}  ({len(rows)} rows = {len(G_SWEEP)} levels x {N_TAU} samples)")


if __name__ == "__main__":
    main()
