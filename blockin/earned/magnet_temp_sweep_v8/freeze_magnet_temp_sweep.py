"""freeze — magnet_temp_sweep_v8  (bespoke, one substrate, brittle by design)

The METRIC-BOUNDARY-CROSSING probe: the one separability case v6 (discrete cut) and
v7 (metric axis WITHIN a category) left open. v6 showed the 1<->10 cut is TOPOLOGICALLY
sharp; v7 showed Cat 1 does not smear along a CONTINUOUS axis (it critically slows toward
an EDGE, monotonically). The remaining question: a metric axis that CROSSES a critical
point INTO (apparently) another phase -- does the dynamical KIND smear, or stay sharp?

Substrate: an EQUILIBRIUM-CRITICALITY ORACLE (the v4 pattern -- an analytic correlator
with truth computed HERE, never via conform -- applied to a thermodynamic critical point).
It models the CONNECTED order-parameter fluctuation of a magnet swept in temperature
through its critical (Curie) point: a SINGLE relaxational mode in thermal equilibrium, at
five control settings straddling the critical value g_c (level 2 = critical).

  C(tau)   = C0(g) * exp(-lam(g) * tau)              (connected correlator -> 0)
  chi(tau) = (C0(g)/T) * (1 - exp(-lam(g) * tau))    (equilibrium FDT: integrated response)

By the equilibrium fluctuation-dissipation THEOREM this gives, at EVERY level, an EXACTLY
AFFINE FDR locus chi vs (C0 - C) of slope 1/T and X = 1 -- the reversible/equilibrium
signature -- INDEPENDENT of how slow lam gets or how big C0 gets. That is the whole point:

  - lam(g)  = the spectral gap (relaxation rate). DIPS to a finite floor at g_c
              (van Hove critical slowing, finite-size-rounded): lam = lam_floor + kappa*(g-g_c)^2.
              => the relaxation time tau_corr = 1/lam PEAKS at the critical middle level.
  - C0(g)   = the static order-parameter-fluctuation amplitude = the static susceptibility
              chi_static (since chi_inf = C0/T). PEAKS at g_c, tied to the timescale by the
              2D-Ising critical-exponent ratio chi ~ xi^(gamma/nu) ~ tau_corr^(gamma/(z*nu))
              with gamma=7/4, nu=1, z=2.17 => exponent 0.806. So susceptibility and timescale
              diverge together with the textbook exponent relation, not arbitrarily.

THE TOOTH (the FALSIFICATION.md ising_equilibrium PENDING falsifier, made clean):
right at the critical point the fluctuations go HUGE (C0 peaks) and SLUGGISH (tau_corr peaks)
-- the naive read is "it has fallen out of equilibrium / gone glassy / it is AGING (X<1)."
The truth is reversible CRITICAL SLOWING: X = 1 at the critical point exactly (FDR locus
stays affine, slope 1/T). Critical slowing is NOT aging. AND: the cool side and the warm
side look quantitatively different (one is "below", one "above" the special temperature),
but they are the SAME dynamical KIND -- a reversible equilibrium relaxation, X=1 -- at every
level. A thermodynamic phase boundary is NOT an MPA dynamical-CATEGORY boundary.

This is the boundary-CROSSING companion to v7's boundary-APPROACH: v7's band diverges
MONOTONICALLY toward an edge it never reaches; here the band PEAKS at an interior critical
point and recovers on the far side -- the axis passes THROUGH criticality and the category
stays Cat 1 the whole way. It is the X=1 (reversible) counterpart to v4's X<1 (aging) glass:
same diverging-timescale surface, opposite FDT verdict.

WHY AN ORACLE (and not the library's ising_equilibrium MC cells): the finite-L (L=32) Monte
Carlo cells do not cleanly EXHIBIT X=1 across the transition -- the ordered phase plateaus at
the frozen magnetization m^2 (spin-flip C barely decays; the FDR locus goes degenerate/
near-vertical) and the critical cell is noisy, so a blind X=1 read off the raw cells would
not isolate conform (a miss could mean "data too noisy"). The library's own intended clean
X-read routes through conform's fit_kww5 -- the EXAMINEE -- so it cannot seal. The oracle
models the CONNECTED correlator directly, equilibrium FDT exact: X=1 is the sealed truth and
the locus is clean by construction, exactly as v4's kww_oracle sealed its X<1. (Onsager
Tc=2.269 and the equilibrium-FDT X=1 are the external physics this idealizes; the oracle is
the clean stand-in until the library refresh places the glass/ising camera-scale.)

BLINDING: the emitted CSV carries ONLY (level, tau, C, chi). It does NOT carry the control
value g, g_c, the gap lam, C0, T, tau_corr, the susceptibility, the slope, X, the critical
exponents, or any framework token. A magnet researcher's correlation + susceptibility
measurement at five temperatures yields exactly these curves; the framework reading stays
sealed. The level index is a neutral 0..4 (cool->warm); the native temperatures are NOT
emitted (withheld native control magnitudes, per v7 -- absolute distance-in-native-units is
not blind-closeable; the closeable content is the observable band).

Run:  python H:/mpa-conform/blockin/questions/magnet_temp_sweep_v8/freeze_magnet_temp_sweep.py

Emits:  data/magnet_temp_sweep_v8.frozen.csv   (level,tau,C,chi -- the blind artifact)
        prints the SEALED ground truth (per-level lam, tau_corr, C0/chi_static, FDR slope,
        R^2, X; the peak location) for the author to paste / the human to eyeball. The CSV
        carries NONE of it.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "magnet_temp_sweep_v8.frozen.csv"

# ----- oracle parameters (the SEAL; none of this reaches the CSV) -----------------
T = 1.0                       # bath temperature in the FDR units -> FDR slope = 1/T = 1
LAM_FLOOR = 0.02              # finite-size-rounded spectral gap AT criticality -> tau_max=50
KAPPA = 0.5                   # curvature of the gap's parabolic dip about g_c
LAM_REF = LAM_FLOOR           # susceptibility reference rate (so chi peaks where lam dips)
CHI_PEAK = 5.0               # static susceptibility (C0) at the critical level
EXP_CHI = 7.0 / 4.0 / (2.17 * 1.0)   # gamma/(z*nu) = 1.75/2.17 = 0.806 -- 2D Ising, model A

# control offsets delta = g - g_c for the five levels (level 2 = critical, delta=0).
# asymmetric like a real T-sweep straddling Tc (cool side closer, warm side reaches further).
DELTAS = np.array([-0.40, -0.15, 0.0, 0.20, 0.50])
N_TAU = 30                    # log-spaced lags per level
E_FOLDINGS = 8.0              # each level watched out to ~8 e-foldings of ITS OWN slow mode


def lam_of(delta: float) -> float:
    return LAM_FLOOR + KAPPA * delta * delta


def C0_of(lam: float) -> float:
    # static susceptibility / fluctuation amplitude, tied to the timescale by the
    # 2D-Ising exponent ratio: chi ~ tau_corr^(gamma/(z nu)) = (lam_ref/lam)^0.806.
    return CHI_PEAK * (LAM_REF / lam) ** EXP_CHI


def seal_table():
    rows = []
    for lvl, d in enumerate(DELTAS):
        lam = lam_of(d)
        C0 = C0_of(lam)
        tau_corr = 1.0 / lam
        chi_static = C0 / T
        rows.append(dict(level=lvl, delta=d, lam=lam, tau_corr=tau_corr,
                         C0=C0, chi_static=chi_static))
    return rows


def materialize():
    """Emit (level, tau, C, chi) for all five levels; return the per-level curves for
    the seal's locus check."""
    lines = []
    per_level = []
    for lvl, d in enumerate(DELTAS):
        lam = lam_of(d)
        C0 = C0_of(lam)
        tau_max = E_FOLDINGS / lam
        taus = np.concatenate(([0.0], np.geomspace(0.2, tau_max, N_TAU - 1)))
        C = C0 * np.exp(-lam * taus)
        chi = (C0 / T) * (1.0 - np.exp(-lam * taus))
        per_level.append(dict(level=lvl, tau=taus, C=C, chi=chi, C0=C0, lam=lam))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{t:.6g},{c:.8g},{x:.8g}")
    return lines, per_level


def fdr_check(pl):
    """Independent (NON-conform) least-squares of chi vs (C0 - C); equilibrium FDT
    predicts slope = 1/T, R^2 = 1, X = 1 exactly. Computed here so the seal is a
    COMPUTED key, not a prose assertion (meta-SOP answer-key safeguard)."""
    out = []
    for L in pl:
        drop = L["C"][0] - L["C"]            # C0 - C(tau)
        chi = L["chi"]
        A = np.vstack([drop, np.ones_like(drop)]).T
        (slope, icpt), *_ = np.linalg.lstsq(A, chi, rcond=None)
        pred = A @ [slope, icpt]
        ss = 1.0 - np.sum((chi - pred) ** 2) / max(np.sum((chi - chi.mean()) ** 2), 1e-30)
        out.append(dict(level=L["level"], slope=slope, R2=ss, X=slope * T))
    return out


def main():
    lines, pl = materialize()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# magnet_temp_sweep_v8 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# Five settings (level 0..4) of one fluctuating quantity in one material; tau is the\n"
        "# material's own clock (a lag). Columns: level,tau,C,chi. No control values, no model\n"
        "# parameters. Each level has its own settling window, so tau ranges differ.\n"
        "level,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    seal = seal_table()
    fdr = fdr_check(pl)
    peak = max(seal, key=lambda r: r["tau_corr"])["level"]

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  T={T}  lam_floor={LAM_FLOOR}  kappa={KAPPA}  chi_exp gamma/(z nu)={EXP_CHI:.4f}")
    print(f"  {'lvl':>3} {'delta':>7} {'lam(gap)':>9} {'tau_corr':>9} "
          f"{'C0=chi_st':>10} {'FDRslope':>9} {'R2':>8} {'X':>6}")
    for s, f in zip(seal, fdr):
        print(f"  {s['level']:>3} {s['delta']:>7.2f} {s['lam']:>9.4f} {s['tau_corr']:>9.2f} "
              f"{s['C0']:>10.3f} {f['slope']:>9.4f} {f['R2']:>8.5f} {f['X']:>6.4f}")
    print(f"  PEAK (critical slowing + susceptibility) at level {peak} "
          f"(tau_corr={seal[peak]['tau_corr']:.1f}, chi_static={seal[peak]['chi_static']:.2f})")
    print(f"  band: tau_corr {[round(s['tau_corr'],1) for s in seal]} "
          f"(peaked, ~{max(s['tau_corr'] for s in seal)/min(s['tau_corr'] for s in seal):.0f}x range)")
    print(f"  band: chi_static {[round(s['chi_static'],2) for s in seal]} (peaked)")
    print(f"  X = 1 and FDR R^2 = 1 at EVERY level -> reversible equilibrium, NOT aging,")
    print(f"      KIND invariant across the critical crossing.")
    print(f"wrote {OUT}  ({len(lines)} rows, {len(DELTAS)} levels)")


if __name__ == "__main__":
    main()
