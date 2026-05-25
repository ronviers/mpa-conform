"""Control ladder through the per-channel S/N gate (five_vector.SNR_GATE).

Carries each cell's grain (C_sem/chi_sem) into fit_kww5 so the gate is the
per-channel signal-to-noise test instead of the scalar RESIDUAL_GATE. Renders
per-channel S/N (RMS residual / RMS grain) across the ladder, with the gate line
and the IN/OUT verdict. Channels reporting ~zero noise (analytic-oracle chi) are
marked deterministic and excluded from the gate, not divided by.

Run: python H:/mpa-conform/scripts/test_channel_gate_ladder.py
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
from conformer.compute import five_vector

DATA = "H:/mpa-central/library/data"
OUT = Path("H:/mpa-conform/output/diagnostics/channel_gate_ladder.png")

# (label, glob, T, expected). Expected is the prior, not enforced — we read the verdict.
LADDER = [
    ("two_temp_ou X0.5\n(in-family)",  f"{DATA}/two_temp_ou/two_temp_ou__X0.5__velocity.json", 1.0, "IN"),
    ("kww_oracle X0.5\n(in-family)",   f"{DATA}/kww_oracle/kww_oracle__X0.5__velocity.json",   1.0, "IN"),
    ("glass T1.3\n(r-regime)",         f"{DATA}/glass/glass__T1.300__spin-flip.json",          1.0, "IN"),
    ("sine_wave P100\n(out-family)",   f"{DATA}/sine_wave/sine_wave__P100__velocity.json",     1.0, "OUT"),
    ("square_wave P100\n(out-family)", f"{DATA}/square_wave/square_wave__P100__velocity.json", 1.0, "OUT"),
    ("driven_ring F1.5\n(NESS)",       f"{DATA}/driven_ring/driven_ring__F1.5__velocity.json", 0.5, "OUT"),
]


def rows_for(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    return [{"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels, snr_C, snr_chi, verdicts, dets = [], [], [], [], []
    print(f"===== control ladder through per-channel gate (SNR_GATE={five_vector.SNR_GATE}) =====")
    for label, patt, T, exp in LADDER:
        g = glob.glob(patt)
        if not g:
            print(f"  {label.splitlines()[0]:<22} MISSING ({patt})"); continue
        fit = five_vector.fit_kww5(rows_for(g[0]), T=T)
        sC = fit.channel_snr["C"]; sX = fit.channel_snr["chi"]
        gate = "IN " if fit.in_domain else "OUT"
        agree = "ok" if gate.strip() == exp else "** FLIP vs prior **"
        print(f"  {label.splitlines()[0]:<22} [{gate}] (prior {exp} {agree}) "
              f"C S/N={sC:6.1f}  chi S/N={'inf' if not np.isfinite(sX) else f'{sX:6.1f}'}  "
              f"| floor C={fit.channel_floor['C']:.4f} chi={fit.channel_floor['chi']:.4f}")
        labels.append(label)
        # plot deterministic channels at the gate line height with a marker instead of inf
        snr_C.append(sC if np.isfinite(sC) else None)
        snr_chi.append(sX if np.isfinite(sX) else None)
        dets.append((not np.isfinite(sC), not np.isfinite(sX)))
        verdicts.append(fit.in_domain)

    n = len(labels)
    x = np.arange(n)
    w = 0.38
    fig, ax = plt.subplots(figsize=(14, 7))
    gate = five_vector.SNR_GATE

    def plot_channel(vals, dets_i, offset, color, name):
        for i, v in enumerate(vals):
            if v is None:  # deterministic channel: no grain to whiten
                ax.scatter(x[i] + offset, gate, marker="x", s=80, color=color, zorder=5)
                ax.annotate("det.", (x[i] + offset, gate), textcoords="offset points",
                            xytext=(0, 6), ha="center", fontsize=7, color=color)
            else:
                ax.bar(x[i] + offset, max(v, 1e-2), w, color=color,
                       alpha=0.85, label=name if i == 0 else None)

    plot_channel(snr_C, [d[0] for d in dets], -w / 2, "C0", "C channel S/N")
    plot_channel(snr_chi, [d[1] for d in dets], +w / 2, "C1", "chi channel S/N")

    ax.axhline(gate, color="k", ls="--", lw=1.6, label=f"SNR_GATE = {gate}x grain")
    ax.set_yscale("log")
    ax.set_ylim(0.05, max(200, ax.get_ylim()[1]))
    for i, ok in enumerate(verdicts):
        ax.annotate("IN" if ok else "OUT", (x[i], ax.get_ylim()[1] * 0.6),
                    ha="center", fontweight="bold", color="green" if ok else "red")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("per-channel S/N  =  RMS residual / RMS grain (log)")
    ax.set_title("Control ladder through the per-channel S/N gate\n"
                 "in-family channels sit below the line (residual within grain); "
                 "out-of-family burst above it")
    ax.legend(loc="upper left", fontsize=9); ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
