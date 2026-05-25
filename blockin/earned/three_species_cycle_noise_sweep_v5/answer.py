"""three_species_cycle_noise_sweep_v5 — BLIND ANSWERER analysis script.

Reads ONLY the sanitized .data.csv. Computes, per operating point (independent
single-point placements), the framework read, then reads the band across the five
noise levels. Builds the self-describing result image.

Question (researcher voice): a three-population cyclic standoff (1->2->3->1) that
never settles. Same community run at five environmental-noise levels. As noise is
turned DOWN, does the turnover slow/stop (noise-driven cycling) or keep turning at
the same rate (intrinsic cycling)? And what does the noise level actually change
about the turnover, if anything?

Pipeline traversal (sanitized):
  0 ADMISSION  - dimensionless columns present; convenience data admitted (dev).
  1 FRAME      - tau is the system clock; lag for C/chi/Cxy/Cyx, elapsed for phi*.
                 One control sweep (noise_rel), placed as 5 independent points.
  2 SELECTION  - 3 nodes / 3 directed non-reciprocal links / one closed cycle ->
                 current-bearing (the directed cross-corr Cxy=-Cyx is the tell).
                 Intent: I2 migration BUILT AS stitched I1 placements + one band read.
  3 ROOT OP    - per level: FDR locus (chi vs C0 - C(tau)); winding RATE (slope of
                 phiMean vs tau); phase-DIFFUSION baseline rate (robust median
                 pointwise slope of phiVar vs tau, immune to cycle-count jumps),
                 plus an explicit count/size of the sporadic phiVar jumps.
  4 GATES      - current present -> directed cross-correlation antisymmetry checked.
  5 READOUT    - band: which fitted quantity migrates with noise, which is invariant.
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, r"H:\mpa-conform\blockin")
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

HERE = r"H:\mpa-conform\blockin\workspace"
DATA = Path(HERE) / "three_species_cycle_noise_sweep_v5.data.csv"


def ls_slope(x, y):
    """Plain least-squares slope, intercept, R^2."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2)) + 1e-12
    return float(coef[0]), float(coef[1]), 1.0 - ss_res / ss_tot


def diffusion_baseline(tau, pv):
    """Robust phase-diffusion rate = median of positive pointwise slopes d(phiVar)/dtau.
    Immune to the sporadic single-step cycle-count jumps that contaminate a global
    least-squares fit. Returns (rate, n_jumps, max_jump)."""
    dpv = np.diff(pv)
    dtau = np.diff(tau)
    rate_pw = dpv / dtau
    base_rate = float(np.median(rate_pw[rate_pw > 0]))
    typ_step = base_rate * dtau            # the increment a clean diffusion would give
    excess = dpv - typ_step
    n_jumps = int(np.sum(excess > 50.0))   # steps far above clean diffusion increment
    max_jump = float(np.max(dpv))
    return base_rate, n_jumps, max_jump


def main():
    raw = np.genfromtxt(DATA, delimiter=",", names=True)
    levels = np.unique(raw["level"]).astype(int)

    per_level = {}
    for lv in levels:
        m = raw["level"] == lv
        d = {k: raw[k][m] for k in raw.dtype.names}
        order = np.argsort(d["tau"])
        for k in d:
            d[k] = d[k][order]
        noise = float(np.median(d["noise_rel"]))

        tau, C, chi = d["tau"], d["C"], d["chi"]
        C0 = C[0]  # C at smallest lag ~= C(0)

        # FDR locus: chi vs (C0 - C(tau)); slope ~ effective inverse-temperature (FDT).
        fdr_x = C0 - C
        msk = chi > 0.02 * chi.max()
        fdr_slope, _, fdr_r2 = ls_slope(fdr_x[msk], chi[msk])

        # C-relaxation: first zero-crossing of C -> oscillatory decorrelation lag.
        zc = np.where(np.diff(np.sign(C)) != 0)[0]
        tau_relax = float(tau[zc[0]]) if len(zc) else np.nan

        # directed-current gate: antisymmetry Cxy = -Cyx ; current magnitude & lag.
        antisym = float(np.max(np.abs(d["Cxy"] + d["Cyx"])))   # ~0 if antisymmetric
        cross_peak = float(np.max(np.abs(d["Cxy"])))
        tau_cross_peak = float(tau[np.argmax(np.abs(d["Cxy"]))])

        # WINDING RATE: slope of phiMean vs elapsed tau (turnover frequency).
        wind_rate, _, wind_r2 = ls_slope(tau, d["phiMean"])

        # PHASE-DIFFUSION baseline rate (robust) + sporadic-jump accounting.
        diff_rate, n_jumps, max_jump = diffusion_baseline(tau, d["phiVar"])

        # phiMean monotone? (a backward step = a real phase slip vs a count glitch)
        n_back = int(np.sum(np.diff(d["phiMean"]) < 0))

        per_level[lv] = dict(
            noise=noise, C0=C0, tau_relax=tau_relax,
            fdr_slope=fdr_slope, fdr_r2=fdr_r2,
            antisym=antisym, cross_peak=cross_peak, tau_cross_peak=tau_cross_peak,
            wind_rate=wind_rate, wind_r2=wind_r2,
            diff_rate=diff_rate, n_jumps=n_jumps, max_jump=max_jump, n_back=n_back,
            tau=tau, C=C, chi=chi, Cxy=d["Cxy"], Cyx=d["Cyx"],
            phiMean=d["phiMean"], phiVar=d["phiVar"], fdr_x=fdr_x,
        )

    # ---- BAND across levels ----
    noises = np.array([per_level[lv]["noise"] for lv in levels])
    wind_rates = np.array([per_level[lv]["wind_rate"] for lv in levels])
    diff_rates = np.array([per_level[lv]["diff_rate"] for lv in levels])
    cross_peaks = np.array([per_level[lv]["cross_peak"] for lv in levels])
    n_jumps = np.array([per_level[lv]["n_jumps"] for lv in levels])

    base = per_level[levels[0]]
    twopoint_max_dev = 0.0
    for lv in levels[1:]:
        for col in ("C", "chi", "Cxy", "Cyx"):
            twopoint_max_dev = max(
                twopoint_max_dev, float(np.max(np.abs(per_level[lv][col] - base[col])))
            )

    wind_mean = float(np.mean(wind_rates))
    wind_rel_spread = float((wind_rates.max() - wind_rates.min()) / wind_mean)
    diff_mean = float(np.mean(diff_rates))
    diff_rel_spread = float((diff_rates.max() - diff_rates.min()) / diff_mean)
    diff_corr = float(np.corrcoef(noises, diff_rates)[0, 1])

    # ---------- console ----------
    print("=" * 86)
    print("three_species_cycle_noise_sweep_v5 — per-level placements")
    print("=" * 86)
    print(f"{'lvl':>3} {'noise':>6} {'wind_rate':>10} {'(R2)':>6} "
          f"{'diff_base':>10} {'n_jump':>6} {'max_jump':>10} {'xpeak':>7} {'antisym':>9}")
    for lv in levels:
        p = per_level[lv]
        print(f"{lv:>3} {p['noise']:>6.3f} {p['wind_rate']:>10.5f} {p['wind_r2']:>6.3f} "
              f"{p['diff_rate']:>10.3f} {p['n_jumps']:>6d} {p['max_jump']:>10.2f} "
              f"{p['cross_peak']:>7.4f} {p['antisym']:>9.2e}")
    print("-" * 86)
    print(f"two-point block (C/chi/Cxy/Cyx) max deviation across levels = {twopoint_max_dev:.2e}")
    print(f"winding-rate: mean {wind_mean:.4f} rad/clock, relative spread {wind_rel_spread:.3%}")
    print(f"phase-diffusion baseline: mean {diff_mean:.3f}, relative spread {diff_rel_spread:.3%}, "
          f"corr-with-noise {diff_corr:.3f}")
    print(f"sporadic phiVar jumps per level (>clean increment): {dict(zip(levels.tolist(), n_jumps.tolist()))}")
    print("=" * 86)

    # ---------- header strings ----------
    question = (
        "Three populations in a cyclic standoff (1>2>3>1) that never settles. Same community "
        "run at five environmental-noise levels (0.2x..4x baseline). As I turn the environmental "
        "noise DOWN, does the turnover slow down or stop (is the cycling noise-driven) or does the "
        "community keep cycling at the same rate? And either way, what does the noise level "
        "actually change about the turnover?"
    )
    minimal_structure = (
        "3 nodes, 3 directed non-reciprocal links, one closed cycle (1>2>3>1); the loop is "
        "irreducible (not 1 population + environment); noise enters each population; same wiring "
        "at all 5 levels."
    )
    verdict = (
        "INTRINSIC, not noise-driven. The turnover RATE is invariant across the entire noise sweep: "
        f"the winding rate (phiMean/tau) = {wind_mean:.3f} rad/clock with only {wind_rel_spread:.1%} "
        "spread from 0.2x to 4x noise, and the autocorrelation C plus the directed cross-correlations "
        "Cxy/Cyx are byte-IDENTICAL across all five levels. Turning the environment down will NOT slow "
        "or stop the cycling; the cycle is a sustained internal current of the loop (Cxy=-Cyx, present "
        "even at the calmest level). As for what the noise changes about the turnover: within these "
        "statistics, strikingly little. The baseline phase-diffusion rate (d(phiVar)/dtau) is also "
        f"nearly flat (~{diff_mean:.0f} per clock, {diff_rel_spread:.0%} spread, no clean monotone "
        f"trend with noise, corr={diff_corr:.2f}). The only noise-correlated feature is SPORADIC large "
        "jumps in phiVar (phase-slip / cycle-count excursions) that appear at the middle levels but not "
        "monotonically; on the evidence here that is best read as occasional phase slips rather than a "
        "clean diffusion law, and is flagged not-grounded. Bottom line: the cycling is intrinsic and "
        "rate-stable; the noise level barely moves any robustly-measured property of the turnover."
    )
    placement = (
        f"wind_rate ~ {wind_mean:.3f} rad/clock INVARIANT (spread {wind_rel_spread:.1%}, all R2=1.00); "
        f"C0={base['C0']:.3f}, oscillatory C (first zero-cross tau~{base['tau_relax']:.2f}); "
        f"Cxy=-Cyx antisym |Cxy+Cyx|=0 -> sustained directed current ALL levels; "
        f"diff_baseline ~ {diff_mean:.0f}/clock (spread {diff_rel_spread:.0%}); sporadic phiVar "
        f"jumps only at L3/L4 (non-monotone)."
    )
    grounded = [
        "Cycling is intrinsic, not noise-driven: the winding RATE (slope of phiMean vs elapsed tau) = "
        f"{wind_rates.min():.3f}..{wind_rates.max():.3f} rad/clock across noise 0.2x..4x, relative "
        f"spread {wind_rel_spread:.1%}, every per-level fit R2=1.00 -> flat. [phiMean column, "
        "per-level slope fit].",
        "The two-point structure is independent of noise: C, chi, Cxy, Cyx are IDENTICAL across all "
        f"five levels (max cross-level deviation {twopoint_max_dev:.0e}) -> the decorrelation and "
        "response of the turnover plane do not change with buffeting. [C/chi/Cxy/Cyx, cross-level "
        "compare].",
        "A genuine sustained cycle (directed current) exists even at the calmest level: Cxy = -Cyx "
        f"(antisymmetric, |Cxy+Cyx|=0) with nonzero peak ~{cross_peaks.mean():.2f} at finite lag "
        "(tau~{:.2f}) -> chirality of the 1>2>3>1 loop. [Cxy, Cyx columns].".format(base["tau_cross_peak"]),
        "The baseline phase-diffusion rate is also essentially noise-INVARIANT: robust median "
        f"d(phiVar)/dtau = {diff_rates.min():.1f}..{diff_rates.max():.1f} (~{diff_mean:.0f}/clock, "
        f"spread {diff_rel_spread:.0%}, corr with noise {diff_corr:.2f}) -> no clean monotone "
        "diffusion-vs-noise law. [phiVar column, robust pointwise slope].",
        "FDR locus (chi vs C0-C(tau)) is well-defined and noise-invariant (same C/chi everywhere), "
        "placing the system in a stationary, non-settling regime. [C, chi columns].",
    ]
    not_grounded = [
        "WHAT the noise changes about the turnover, as a clean law: the question's second half is "
        "only weakly answerable. The robustly-measured properties (rate, two-point block, baseline "
        "diffusion) are all ~noise-independent; the one noise-associated feature is sporadic large "
        "phiVar jumps (phase slips) at L3/L4 that do NOT scale monotonically with noise (L5, the "
        "highest, is the cleanest). The provided statistics cannot distinguish 'noise sets a phase-"
        "slip rate' from 'cycle-count glitches in the sub-window angle accounting.' [phiVar outliers; "
        "no per-point grain/uncertainty supplied].",
        "Whether rate-invariance persists BELOW 0.2x noise (toward the deterministic limit): the sweep "
        "floor is 0.2x; a transition off the low end cannot be ruled out. [collapsed axis: no operating "
        "point below level 1].",
        "Individual coupling strengths / which of the three links dominates: the directed cross-"
        "correlation gives chirality and a current magnitude, not the per-edge weights (researcher "
        "brought no model parameters). [not in the provided observables].",
        "Any researcher PREFERENCE among noise levels (which is 'best/healthiest'): that selects through "
        "an interpretive choice the researcher brings; the band is grounded per level, the choice is a "
        "viewport dial, not a conform call. [value-laden, not computable from the freeze].",
    ]

    def draw(axes, stamp):
        ax0, ax1, ax2, ax3 = axes
        cmap = plt.cm.viridis(np.linspace(0, 1, len(levels)))

        # BOX 0 -- THE BAND: swept quantities vs control axis (noise_rel)
        ax0b = ax0.twinx()
        ax0.plot(noises, wind_rates, "o-", color="#0a5d00", lw=2)
        ax0.axhline(wind_mean, color="#0a5d00", ls=":", lw=1, alpha=0.6)
        ax0b.plot(noises, diff_rates, "s--", color="#8b0000", lw=2)
        ax0b.axhline(diff_mean, color="#8b0000", ls=":", lw=1, alpha=0.5)
        ax0.set_xscale("log")
        ax0.set_xlabel("noise_rel (x baseline)  [control axis]")
        ax0.set_ylabel("winding rate phiMean/tau [rad/clock]", color="#0a5d00")
        ax0b.set_ylabel("phase-diffusion baseline d(phiVar)/dtau", color="#8b0000")
        ax0.set_ylim(0, max(wind_rates) * 1.6)
        ax0b.set_ylim(0, max(diff_rates) * 1.6)
        ax0.set_title("THE BAND: rate INVARIANT and diffusion ~flat across noise", fontsize=9)
        ax0.tick_params(axis="y", labelcolor="#0a5d00")
        ax0b.tick_params(axis="y", labelcolor="#8b0000")
        ax0.grid(alpha=0.3)
        for x, y in zip(noises, wind_rates):
            ax0.annotate(f"{y:.3f}", (x, y), fontsize=7, color="#0a5d00",
                         xytext=(0, 6), textcoords="offset points", ha="center")

        # BOX 1 -- phiMean(tau): lines overlap (rate invariant)
        for lv, c in zip(levels, cmap):
            p = per_level[lv]
            ax1.plot(p["tau"], p["phiMean"], color=c, lw=1.3, label=f"L{lv} ({p['noise']:g}x)")
        ax1.set_xlabel("elapsed tau (system clock)")
        ax1.set_ylabel("phiMean (cumulative turnover angle)")
        ax1.set_title("Cumulative winding: same slope at every noise level", fontsize=9)
        ax1.legend(fontsize=6.5, loc="upper left")
        ax1.grid(alpha=0.3)

        # BOX 2 -- phiVar(tau): baseline fan + sporadic jumps marked
        allpv = np.concatenate([per_level[lv]["phiVar"] for lv in levels])
        for lv, c in zip(levels, cmap):
            p = per_level[lv]
            ax2.plot(p["tau"], p["phiVar"], color=c, lw=1.1, alpha=0.6,
                     label=f"L{lv} ({p['noise']:g}x) base~{p['diff_rate']:.0f}, jumps={p['n_jumps']}")
        ax2.set_xlabel("elapsed tau (system clock)")
        ax2.set_ylabel("phiVar (spread of turnover angle)")
        ax2.set_title("Phase spread: ~common baseline; sporadic jumps at L3/L4", fontsize=9)
        ax2.legend(fontsize=6, loc="upper left")
        ax2.grid(alpha=0.3)
        ax2.set_ylim(0, np.percentile(allpv, 96))

        # BOX 3 -- directed current + autocorr (all levels identical -> show base)
        p = base
        ax3.plot(p["tau"], p["Cxy"], color="#00468b", lw=1.6, label="Cxy (x->y)")
        ax3.plot(p["tau"], p["Cyx"], color="#b8860b", lw=1.6, label="Cyx (y->x)")
        ax3.plot(p["tau"], p["C"], color="#444444", lw=1.0, ls=":", label="C (autocorr)")
        ax3.axhline(0, color="k", lw=0.6)
        ax3.set_xlim(0, 10)
        ax3.set_xlabel("lag tau (system clock)")
        ax3.set_ylabel("correlation")
        ax3.set_title("Directed current Cxy=-Cyx -> chiral cycle (identical all levels)", fontsize=9)
        ax3.legend(fontsize=7, loc="upper right")
        ax3.grid(alpha=0.3)

    out, STAMP = timestamped_view_path(HERE)
    fig, axes = figure_with_header(
        n_plots=4, slug="three_species_cycle_noise_sweep_v5",
        date=STAMP, phase="DEV/blind",
        question=question, minimal_structure=minimal_structure, verdict=verdict,
        grounded=grounded, not_grounded=not_grounded, placement=placement,
    )
    draw(axes, STAMP)
    fig.savefig(out, dpi=150)
    print(f"\nwrote view: {out}")
    return out


if __name__ == "__main__":
    main()
