"""Is the tau_obs camera tracking? Synthetic substrates on the Banach ruler.

Extends substrate_inversion_camera.py (glass/brain/QEC) to the synthetic control
substrates, run through the production inversion (invert() + the 5-vector gate we
just wired in). The Banach ruler (generate_locus canonical c->s->r loci) is the
overlay; each substrate's (dC, T*chi) points show where its tau_obs window is
pointed, colored by the per-channel gate verdict.

The camera "tracks" when the window traverses the migration interior. It does NOT
track when:
  - the substrate is oscillatory (sine/square): dC overshoots past 1 (C<0,
    anticorrelation) -> the points leave the migration manifold entirely.
  - the window is parked at the decorrelated tail (dC~1, tau_obs->inf) or stuck
    in a narrow band (NESS/chaos): no migration is traversed.

Run: python H:/mpa-conform/scripts/test_synthetic_camera.py
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

DATA = "H:/mpa-central/library/data"
OUT = Path("H:/mpa-conform/output/diagnostics/synthetic_camera.png")
T = 1.0

# (label, glob, family-prior)
SUBS = [
    ("two_temp_ou X0.5",  f"{DATA}/two_temp_ou/two_temp_ou__X0.5__velocity.json"),
    ("kww_oracle X0.5",   f"{DATA}/kww_oracle/kww_oracle__X0.5__velocity.json"),
    ("ou_equilibrium",    f"{DATA}/ou_equilibrium/ou_equilibrium__tau100__velocity.json"),
    ("voter nu0.001",     f"{DATA}/voter/voter__nu0.001__opinion-flip.json"),
    ("logistic_chaos",    f"{DATA}/logistic_chaos/logistic_chaos__r3.6__velocity.json"),
    ("driven_ring F1.5",  f"{DATA}/driven_ring/driven_ring__F1.5__velocity.json"),
    ("sine_wave P100",    f"{DATA}/sine_wave/sine_wave__P100__velocity.json"),
    ("square_wave P100",  f"{DATA}/square_wave/square_wave__P100__velocity.json"),
]

REGIME_COL = {"deep_c": "#1f77b4", "c_near_s": "#2ca02c", "s_critical": "#d62728",
              "r_near_s": "#9467bd", "deep_r": "#7f7f7f"}


def camera_reading(dC):
    if dC.max() > 1.30:   # genuine anticorrelation (C < -0.3), not tail noise around C=0
        return "oscillatory / OFF-manifold (C<0)"
    if (dC.max() - dC.min()) < 0.15:
        return "stuck (window not traversing)"
    if dC.min() > 0.85:
        return "tau_obs->inf (parked at r tail)"
    if dC.max() < 0.50:
        return "tau_obs->0 (interior-low only)"
    return "MIGRATION INTERIOR (tracks)"


def load(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"], "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]
    dC = 1.0 - np.array([r["C"] for r in rows])
    chi = np.array([r["chi"] for r in rows])
    return rows, scale, dC, chi


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = []
    print(f"{'substrate':<18} | gate | camera reading")
    print("-" * 72)
    for label, patt in SUBS:
        g = glob.glob(patt)
        if not g:
            print(f"{label:<18} | MISSING {patt}"); continue
        rows, scale, dC, chi = load(g[0])
        res = inversion.invert(rows, tau_scale=scale, T=T, skip_stage2=True)
        fv = res.five_vector_fit
        in_dom = bool(fv and fv.in_domain)
        reading = camera_reading(dC)
        print(f"{label:<18} | {'IN ' if in_dom else 'OUT'} | dC=[{dC.min():.2f},{dC.max():.2f}]  {reading}")
        results.append((label, dC, chi, in_dom, reading, fv))

    # One panel per substrate: its data + its OWN fitted Banach curve (the
    # Banach substrate adapted to that data via the inversion, not a fixed ruler).
    ncol = 4
    nrow = int(np.ceil(len(results) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 4.3 * nrow))
    axes = np.atleast_1d(axes).ravel()

    for ax, (label, dC, chi, in_dom, reading, fv) in zip(axes, results):
        col = "tab:green" if in_dom else "tab:red"
        # empirical data
        ax.plot(dC, T * chi, "o", ms=5, color=col, alpha=0.8, label="data", zorder=3)
        # Banach adapted to THIS substrate (5-vector fit)
        if fv is not None:
            loc = gfdr_model.generate_kww_glass_locus(
                fv.chit, q_EA=fv.q_EA, tau_alpha=fv.tau_alpha, beta_KWW=fv.beta_KWW,
                tau_beta=fv.tau_beta, X=fv.X, T=fv.T)
            dC_m = 1.0 - loc["C"]; Tchi_m = fv.T * loc["chi"]
            o = np.argsort(dC_m)
            ax.plot(dC_m[o], Tchi_m[o], "-", color="tab:blue", lw=2.2,
                    label="Banach (5-vec fit)", zorder=2)
            # leading-order cdv1 (un-adapted) for contrast
            loc0 = gfdr_model.generate_locus(fv.chit)
            dC0 = 1.0 - loc0["C"]
            o0 = np.argsort(dC0)
            ax.plot(dC0[o0], loc0["chi"][o0], ":", color="gray", lw=1.3,
                    label="cdv1 leading-order", zorder=1)
        xmax = max(1.1, float(dC.max()) * 1.05)
        ylim = max(1.05, float((T * chi).max()) * 1.1)
        dl = np.linspace(0, min(1.0, xmax), 40)
        ax.plot(dl, dl, "k--", lw=0.8, alpha=0.5)
        ax.set_xlim(-0.05, xmax); ax.set_ylim(-0.05, ylim)
        title_gate = "IN" if in_dom else "OUT"
        xtxt = (f"X={fv.X:.2f}  chit={fv.chit:.2f}  resid={fv.residual:.3f}"
                if fv is not None else "no fit")
        ax.set_title(f"{label}  [{title_gate}]\n{xtxt}", fontsize=9,
                     color=col)
        ax.text(0.5, -0.02, reading, transform=ax.transAxes, ha="center", va="top",
                fontsize=7.5, color="#555")
        ax.set_xlabel(r"$\Delta C$"); ax.set_ylabel(r"$T\cdot\chi$")
        ax.legend(fontsize=7, loc="upper left"); ax.grid(alpha=0.3)

    for ax in axes[len(results):]:
        ax.axis("off")

    fig.suptitle("Banach adapted to each synthetic substrate (per-substrate fit, not a fixed ruler)\n"
                 "blue = Banach 5-vector fit to THIS data; green=gate IN, red=OUT", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
