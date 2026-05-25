"""Does the camera (tau_obs) frame a substrate at any timescale?

Take kww_oracle (in-family, planted X=0.5, full 5-vector round-trip) and stretch
its time so the relaxation takes 30 years -- then 30 million years. The camera
(tau_scale) is conform's knob: it tracks the substrate's intrinsic time. If it
does its job, the dimensionless lag (lag / tau_scale) is invariant and Banach
adapts identically -- absolute timescale irrelevant.

For each stretch we multiply every lag by K and set tau_scale = tau_env * K
(the camera tracking the substrate). The recovered 5-vector should not move.

Run: python H:/mpa-conform/scripts/test_camera_scale_invariance.py
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
OUT = Path("H:/mpa-conform/output/diagnostics/camera_scale_invariance.png")
T = 1.0
SECONDS_PER_YEAR = 365.25 * 24 * 3600


def base_rows():
    c = json.load(open(CELL))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    tau_env = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    lag = np.array([e["dt"] for e in s], float)
    rows = [{"tau": float(e["dt"]), "C": float(e["C_mean"]), "chi": float(e["chi_mean"]),
             "C_sem": float(e.get("C_sem", 0.0)), "chi_sem": float(e.get("chi_sem", 0.0))} for e in s]
    return rows, lag, float(tau_env)


def fit_at(rows, lag, tau_env, K):
    """Stretch every lag by K; the camera (tau_scale) tracks: tau_scale = tau_env * K."""
    stretched = [dict(r, tau=r["tau"] * K) for r in rows]
    res = inversion.invert(stretched, tau_scale=tau_env * K, T=T, skip_stage2=True)
    return res.five_vector_fit, lag * K, tau_env * K


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows, lag, tau_env = base_rows()
    # original native span, then stretch so the *relaxation* (tau_env) = 30 yr, 30 Myr.
    K_30yr = (30 * SECONDS_PER_YEAR) / tau_env
    cases = [
        ("native", 1.0),
        ("30 years", K_30yr),
        ("30 million yr", K_30yr * 1e6),
    ]

    print(f"kww_oracle X0.5  (native tau_env = {tau_env:g} steps)")
    print(f"{'case':<16} {'tau_scale (s)':>14} {'gate':>4} {'X':>7} {'q_EA':>7} "
          f"{'beta':>7} {'resid':>8} {'C S/N':>7}")
    fits = []
    for label, K in cases:
        fv, lag_s, scale_s = fit_at(rows, lag, tau_env, K)
        fits.append((label, fv, lag_s))
        snrC = fv.channel_snr.get("C", float("nan"))
        print(f"{label:<16} {scale_s:>14.3g} {'IN' if fv.in_domain else 'OUT':>4} "
              f"{fv.X:>7.3f} {fv.q_EA:>7.3f} {fv.beta_KWW:>7.3f} {fv.residual:>8.4f} {snrC:>7.2f}")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 6.2))

    # LEFT: raw C(lag) at each absolute timescale -- same shape, shifted in time
    cols = ["tab:blue", "tab:orange", "tab:green"]
    C = np.array([r["C"] for r in rows])
    for (label, fv, lag_s), col in zip(fits, cols):
        axL.plot(lag_s, C, "o-", ms=3, color=col, alpha=0.8, label=f"{label}")
    axL.set_xscale("log")
    axL.set_xlabel("absolute lag (substrate's own time units / seconds)")
    axL.set_ylabel("C")
    axL.set_title("WITHOUT the camera: raw C vs absolute time\nsame substrate, three wildly different timescales")
    axL.legend(); axL.grid(alpha=0.3)

    # RIGHT: FDT plane -- every stretch lands on the SAME curve (camera framed it)
    dl = np.linspace(0, 1, 50)
    axR.plot(dl, dl, "k--", lw=0.9, alpha=0.5, label="FDT line (X=1)")
    dC = 1.0 - C
    for (label, fv, lag_s), col, mk in zip(fits, cols, ["o", "s", "^"]):
        axR.plot(dC, T * np.array([r["chi"] for r in rows]), mk, ms=7, color=col,
                 alpha=0.6, label=f"{label}  X={fv.X:.3f}")
        loc = gfdr_model.generate_kww_glass_locus(
            fv.chit, q_EA=fv.q_EA, tau_alpha=fv.tau_alpha, beta_KWW=fv.beta_KWW,
            tau_beta=fv.tau_beta, X=fv.X, T=fv.T)
        o = np.argsort(1.0 - loc["C"])
        axR.plot((1.0 - loc["C"])[o], (fv.T * loc["chi"])[o], "-", color=col, lw=1.5, alpha=0.7)
    axR.set_xlabel(r"$\Delta C = 1 - C$"); axR.set_ylabel(r"$T\cdot\chi$")
    axR.set_title("WITH the camera: dimensionless FDT plane\nall three timescales coincide -- tau_obs framed it")
    axR.set_xlim(0, 1.05); axR.set_ylim(0, 1.05)
    axR.legend(fontsize=8); axR.grid(alpha=0.3)

    fig.suptitle("Camera scale-invariance: kww_oracle relaxing over 30 yr vs 30 Myr.\n"
                 "The camera (tau_scale, conform's knob) tracks the substrate's intrinsic time -> "
                 "Banach adapts identically.", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
