"""Where does the 5-vector break? Per-parameter recovery sweep on kww_oracle.

Sweep each parameter across a plausible range (others held at kww_oracle's truth),
regenerate the substrate, and run it back through the fit -- but with realistic
NOISE injected at the cell's grain (C_sem). A noiseless sweep is an inverse crime
(invert the exact model you generated -> trivially perfect); noise is what exposes
which parameters stay pinned vs smear out (identifiability under measurement).

Per sweep point: N_REAL noise realizations; plot mean recovered +/- std vs planted.
Tight band on the identity line = recoverable; wide/off-diagonal = breaks. Note the
gate can stay IN (residual ~ grain) while a parameter is unrecoverable -- goodness
of fit != identifiability.

Run: python H:/mpa-conform/scripts/test_five_vector_breakage.py
"""
from __future__ import annotations
import sys, json, glob
from pathlib import Path

sys.path.insert(0, "H:/mpa-conform")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from conformer.compute import gfdr_model, five_vector

CELL = glob.glob("H:/mpa-central/library/data/kww_oracle/kww_oracle__X0.5__velocity.json")[0]
OUT = Path("H:/mpa-conform/output/diagnostics/five_vector_breakage.png")
T = 1.0
N_REAL = 10
TRUTH = dict(q_EA=0.7, tau_alpha=1.0, beta_KWW=0.6, tau_beta=0.05, X=0.5)

SWEEPS = {
    "q_EA":      np.linspace(0.15, 0.92, 9),
    "tau_alpha": np.geomspace(0.2, 5.0, 9),
    "beta_KWW":  np.linspace(0.25, 1.0, 9),
    "tau_beta":  np.geomspace(0.005, 0.5, 9),
    "X":         np.linspace(0.0, 1.0, 9),
}
LOGX = {"tau_alpha", "tau_beta"}


def lag_grid_and_grain():
    c = json.load(open(CELL))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    lag = np.array([e["dt"] for e in s], float) / scale
    C_sem = np.array([e.get("C_sem", 0.0) for e in s], float)
    chi_sem = np.array([e.get("chi_sem", 0.0) for e in s], float)
    # the analytic oracle reports chi_sem~0; give chi a floor grain so the noisy
    # test isn't secretly noiseless in the response channel.
    chi_sem = np.where(chi_sem > 1e-6, chi_sem, float(np.median(C_sem)))
    return lag, C_sem, chi_sem


def clean_locus(vec, lag):
    loc = gfdr_model.generate_kww_glass_locus(0.0, T=T, **vec)
    C = np.array([gfdr_model._interp_log_tau(loc, float(t_))[0] for t_ in lag])
    chi = np.array([gfdr_model._interp_log_tau(loc, float(t_))[1] for t_ in lag])
    return C, chi


def recover(vec, lag, C_sem, chi_sem, rng):
    C0, chi0 = clean_locus(vec, lag)
    recs = []
    gates = []
    for _ in range(N_REAL):
        C = C0 + rng.normal(0, C_sem)
        chi = chi0 + rng.normal(0, chi_sem)
        rows = [{"tau": float(t_), "C": float(cc), "chi": float(ch),
                 "C_sem": float(cs), "chi_sem": float(xs)}
                for t_, cc, ch, cs, xs in zip(lag, C, chi, C_sem, chi_sem)]
        fit = five_vector.fit_kww5(rows, chit_prior=0.0, T=T)
        recs.append(fit); gates.append(fit.in_domain)
    return recs, gates


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lag, C_sem, chi_sem = lag_grid_and_grain()
    rng = np.random.default_rng(7)
    fig, axes = plt.subplots(1, 5, figsize=(22, 4.7))

    print(f"{'param':<10} {'planted':>9} {'rec mean':>9} {'rec std':>8} {'|bias|':>8} {'frac IN':>8}")
    for ax, (param, values) in zip(axes, SWEEPS.items()):
        planted, mean, std, fin = [], [], [], []
        for v in values:
            vec = dict(TRUTH); vec[param] = float(v)
            recs, gates = recover(vec, lag, C_sem, chi_sem, rng)
            vals = np.array([getattr(f, param) for f in recs])
            planted.append(float(v)); mean.append(float(vals.mean()))
            std.append(float(vals.std())); fin.append(float(np.mean(gates)))
            print(f"{param:<10} {v:>9.3f} {vals.mean():>9.3f} {vals.std():>8.3f} "
                  f"{abs(vals.mean()-v):>8.3f} {np.mean(gates):>8.2f}")

        planted = np.array(planted); mean = np.array(mean); std = np.array(std)
        # color each point by the (fixed) identifiability flag applied to this point's spread
        is_ts = param in five_vector._TIMESCALE
        ip = five_vector._PARAM_NAMES.index(param)
        lo_b, hi_b = float(five_vector._LOWER[ip]), float(five_vector._UPPER[ip])
        pt_cols = []
        for m, sd in zip(mean, std):
            if is_ts:
                railed = (m <= lo_b * 3) or (m >= hi_b / 3)
                cv = sd / abs(m) if abs(m) > 1e-9 else np.inf
                ident = (cv < five_vector.TIMESCALE_CV_GATE) and not railed
            else:
                span = hi_b - lo_b
                railed = (m - lo_b) < 0.01 * span or (hi_b - m) < 0.01 * span
                ident = (sd < five_vector.BOUNDED_STD_GATE) and not railed
            pt_cols.append("0.6" if railed else ("tab:green" if ident else "tab:red"))
        lo = min(planted.min(), (mean - std).min()); hi = max(planted.max(), (mean + std).max())
        ax.plot([lo, hi], [lo, hi], "k--", lw=1, alpha=0.6)
        for x_, y_, e_, c_ in zip(planted, mean, std, pt_cols):
            ax.errorbar([x_], [y_], yerr=[e_], fmt="o", ms=6, color=c_,
                        ecolor=c_, elinewidth=1.5, capsize=3, zorder=3)
        ax.axvline(TRUTH[param], color="gray", ls=":", lw=1, alpha=0.7)
        if param in LOGX:
            ax.set_xscale("log"); ax.set_yscale("log")
        gthr = (f"CV<{five_vector.TIMESCALE_CV_GATE}" if is_ts
                else f"std<{five_vector.BOUNDED_STD_GATE}")
        ax.set_xlabel(f"planted {param}"); ax.set_ylabel(f"recovered {param}")
        ax.set_title(f"{param}  (pinned if {gthr})"); ax.grid(alpha=0.3)

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color="tab:green", ls="", label="pinned (flag: identified)"),
        Line2D([0], [0], marker="o", color="tab:red", ls="", label="mush (flag: NOT identified)"),
        Line2D([0], [0], marker="o", color="0.6", ls="", label="railed at a bound"),
    ]
    fig.legend(handles=handles, loc="upper right", fontsize=9, ncol=3)
    fig.suptitle(f"Where does the 5-vector break? kww_oracle, noise at the cell grain, "
                 f"{N_REAL} realizations/point.\nPoints colored by the (fixed) identifiability "
                 f"flag — does it call 'mush' exactly where recovery goes wide?", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=190); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
