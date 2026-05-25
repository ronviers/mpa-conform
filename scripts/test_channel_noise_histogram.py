"""Per-channel residual histograms vs the noise floor — "find the noise".

The fitter (fit_kww5) currently sees only C_mean / chi_mean and compares its
joint residual to one magic scalar (RESIDUAL_GATE=0.10). But every library cell
ships each channel's noise floor (C_sem, chi_sem). This diagnostic puts the
fit residual back next to the grain it should be measured against:

  for each channel (C, chi): histogram (empirical - model) over all lags, and
  draw the noise floor (+/- mean SEM) on the same axis.

  residuals piled at 0, narrower than the grain  -> NOISE (fit is as good as the
                                                     data allows)
  residuals shifted / wider than the grain       -> SIGNAL the model can't capture

The per-channel signal-to-noise number is RMS(residual) / RMS(sem). That is the
whitened/normalized residual the gate should use instead of an absolute 0.10.

Subjects: kww_oracle (in-family; residuals should be grain) vs square_wave
(out-of-family; residuals should burst past the grain).

Run: python H:/mpa-conform/scripts/test_channel_noise_histogram.py
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
from conformer.compute import five_vector, gfdr_model

DATA = "H:/mpa-central/library/data"
OUT = Path("H:/mpa-conform/output/diagnostics/channel_noise_histogram.png")

SUBJECTS = [
    ("kww_oracle (in-family)",  f"{DATA}/kww_oracle/kww_oracle__X0.5__velocity.json", 1.0),
    ("square_wave (out-family)", f"{DATA}/square_wave/square_wave__P100__velocity.json", 1.0),
]


def rows_for(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]
    return rows


def model_at(fit, tau_query):
    loc = gfdr_model.generate_kww_glass_locus(
        fit.chit, q_EA=fit.q_EA, tau_alpha=fit.tau_alpha, beta_KWW=fit.beta_KWW,
        tau_beta=fit.tau_beta, X=fit.X, T=fit.T)
    Cm = np.array([gfdr_model._interp_log_tau(loc, float(t))[0] for t in tau_query])
    chim = np.array([gfdr_model._interp_log_tau(loc, float(t))[1] for t in tau_query])
    return Cm, chim


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(SUBJECTS), 2, figsize=(13, 5.2 * len(SUBJECTS)))
    if len(SUBJECTS) == 1:
        axes = axes[None, :]

    print("===== per-channel residual vs noise floor =====")
    for r, (tag, path, T) in enumerate(SUBJECTS):
        rows = rows_for(path)
        fit = five_vector.fit_kww5(rows, T=T)
        tau = np.array([row["tau"] for row in rows])
        C = np.array([row["C"] for row in rows]); chi = np.array([row["chi"] for row in rows])
        C_sem = np.array([row["C_sem"] for row in rows]); chi_sem = np.array([row["chi_sem"] for row in rows])
        Cm, chim = model_at(fit, tau)

        gate = "IN " if fit.in_domain else "OUT"
        print(f"\n{tag}  [{gate}] resid={fit.residual:.4f} (gate {five_vector.RESIDUAL_GATE})")
        for ax, name, emp, mod, sem in (
            (axes[r, 0], "C",   C,   Cm,   C_sem),
            (axes[r, 1], "chi", chi, chim, chi_sem),
        ):
            res = emp - mod
            floor = float(np.sqrt(np.mean(sem ** 2)))            # RMS noise floor
            rrms = float(np.sqrt(np.mean(res ** 2)))             # RMS residual
            snr = rrms / floor if floor > 1e-12 else float("inf")
            print(f"    {name:>3} channel: RMS resid={rrms:.4f}  noise floor(SEM)={floor:.4f}  "
                  f"S/N={snr:.1f}  -> {'NOISE' if snr <= 1.5 else 'SIGNAL'}")

            ax.hist(res, bins=20, color="C0" if name == "C" else "C1", alpha=0.75,
                    edgecolor="k", linewidth=0.4)
            ax.axvline(0, color="k", lw=1)
            if floor > 1e-12:
                ax.axvspan(-floor, floor, color="gray", alpha=0.25, label=f"+/-SEM grain ({floor:.3f})")
            else:
                ax.axvline(0, color="red", lw=2, label="noise floor ~ 0 (deterministic)")
            snr_txt = f"S/N = {snr:.1f}" if np.isfinite(snr) else "S/N = inf (floor~0)"
            verdict = "NOISE" if (np.isfinite(snr) and snr <= 1.5) else "SIGNAL"
            ax.set_title(f"{tag}\n{name} residuals  |  {snr_txt}  ->  {verdict}", fontsize=10)
            ax.set_xlabel(f"{name}_empirical - {name}_model")
            ax.set_ylabel("count (lags)")
            ax.legend(fontsize=8); ax.grid(alpha=0.3, axis="y")

    fig.suptitle("Find the noise: fit residual per channel, drawn against its own grain (SEM)",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
