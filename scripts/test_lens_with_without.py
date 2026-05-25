"""What does the MPA lens do? kww_oracle, with vs without the lens applied.

kww_oracle has PLANTED truth (q_EA, tau_alpha, beta_KWW, tau_beta, X), so "does
the lens do what it's supposed to" has a checkable answer: applied as designed, it
should recover the planted values.

WITHOUT the lens  : the raw substrate observables as measured -- C(tau) and chi(tau)
                    decay curves vs native lag. Two curves; the FDT-violation X is
                    nowhere directly readable.
WITH the lens (as designed): the production inversion (invert(): native lag / tau_scale
                    -> dimensionless lag, 5-vector KWW+FDT fit). The data re-coordinated
                    into the canonical FDT-violation plane (deltaC vs T*chi), where X is
                    the slope of the aging branch, and the fitted Banach curve overlaid.
                    The recovered 5-vector is printed against the planted truth.

Run: python H:/mpa-conform/scripts/test_lens_with_without.py
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
from conformer.compute import gfdr_model, inversion

CELL = glob.glob("H:/mpa-central/library/data/kww_oracle/kww_oracle__X0.5__velocity.json")[0]
OUT = Path("H:/mpa-conform/output/diagnostics/lens_with_without.png")
T = 1.0
# Planted truth (kww_oracle/grind.py; tau in tau_env=20 units -> tau_alpha=20/20=1.0).
TRUTH = dict(X=0.5, q_EA=0.7, tau_alpha=1.0, beta_KWW=0.6, tau_beta=0.05)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c = json.load(open(CELL))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    lag = np.array([e["dt"] for e in s], float)              # native lag (no lens)
    C = np.array([e["C_mean"] for e in s], float)
    chi = np.array([e["chi_mean"] for e in s], float)
    C_sem = np.array([e.get("C_sem", 0.0) for e in s], float)
    chi_sem = np.array([e.get("chi_sem", 0.0) for e in s], float)

    rows = [{"tau": float(t_), "C": float(cc), "chi": float(ch),
             "C_sem": float(cs), "chi_sem": float(xs)}
            for t_, cc, ch, cs, xs in zip(lag, C, chi, C_sem, chi_sem)]
    res = inversion.invert(rows, tau_scale=scale, T=T, skip_stage2=True)
    fv = res.five_vector_fit

    print("=== kww_oracle: lens applied as designed (invert + 5-vector) ===")
    print(f"tau_scale (camera) = {scale}")
    print(f"{'param':<10} {'planted':>9} {'recovered':>10} {'|err|':>8}")
    for k in ("X", "q_EA", "tau_alpha", "beta_KWW", "tau_beta"):
        rec = getattr(fv, k)
        print(f"{k:<10} {TRUTH[k]:>9.3f} {rec:>10.3f} {abs(rec-TRUTH[k]):>8.3f}")
    print(f"gate: {'IN' if fv.in_domain else 'OUT'}  residual={fv.residual:.4f}")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 6.4))

    # ---- WITHOUT the lens: raw decay curves vs native lag ----
    axL.plot(lag, C, "o-", color="tab:blue", ms=4, label="C(tau)")
    axL.plot(lag, chi, "s-", color="tab:orange", ms=4, label="chi(tau)")
    axL.set_xscale("log")
    axL.set_xlabel("native lag  tau  (substrate units)")
    axL.set_ylabel("C,  chi")
    axL.set_title("WITHOUT the lens\nraw substrate observables (two decay curves)")
    axL.text(0.5, -0.16, "the FDT-violation X is not directly readable here",
             transform=axL.transAxes, ha="center", fontsize=9, color="#555")
    axL.legend(); axL.grid(alpha=0.3)

    # ---- WITH the lens (as designed): FDT-violation plane + recovered Banach curve ----
    dC = 1.0 - C
    loc = gfdr_model.generate_kww_glass_locus(
        fv.chit, q_EA=fv.q_EA, tau_alpha=fv.tau_alpha, beta_KWW=fv.beta_KWW,
        tau_beta=fv.tau_beta, X=fv.X, T=fv.T)
    dC_m = 1.0 - loc["C"]; Tchi_m = fv.T * loc["chi"]
    o = np.argsort(dC_m)
    dl = np.linspace(0, 1, 50)
    axR.plot(dl, dl, "k--", lw=1.0, alpha=0.6, label="FDT line (X=1)")
    axR.plot(dC, T * chi, "o", color="tab:green", ms=6, label="data (re-coordinated)", zorder=3)
    axR.plot(dC_m[o], Tchi_m[o], "-", color="tab:blue", lw=2.4,
             label="Banach 5-vec fit (the lens)", zorder=2)
    # mark the aging-branch slope = X
    thr = 1.0 - fv.q_EA
    axR.axvline(thr, color="gray", ls=":", lw=1, alpha=0.7)
    axR.text(thr + 0.01, 0.05, "q_EA knee", fontsize=8, color="gray")
    axR.set_xlabel(r"$\Delta C = 1 - C$  (migration progress)")
    axR.set_ylabel(r"$T\cdot\chi$")
    axR.set_title("WITH the lens (applied as designed)\ncanonical FDT-violation plane")
    box = (f"recovered vs planted:\n"
           f"X      {fv.X:.2f}  (truth {TRUTH['X']:.2f})\n"
           f"q_EA   {fv.q_EA:.2f}  (truth {TRUTH['q_EA']:.2f})\n"
           f"beta   {fv.beta_KWW:.2f}  (truth {TRUTH['beta_KWW']:.2f})\n"
           f"gate   {'IN' if fv.in_domain else 'OUT'}  resid {fv.residual:.3f}")
    axR.text(0.97, 0.03, box, transform=axR.transAxes, ha="right", va="bottom",
             fontsize=8.5, family="monospace",
             bbox=dict(boxstyle="round", fc="#f5f5f5", ec="#aaa"))
    axR.set_xlim(0, 1.05); axR.set_ylim(0, 1.05)
    axR.legend(loc="upper left", fontsize=8); axR.grid(alpha=0.3)

    fig.suptitle("What the MPA lens does: same kww_oracle data, with vs without.\n"
                 "The lens re-coordinates raw decay into the FDT plane where the planted X "
                 "becomes a measurable slope -- and recovers it.", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
