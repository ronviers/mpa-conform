"""ideal_library.py -- the library of ideal substrates, page 1.

OFAT over the FIVE-VECTOR. Each ideal substrate is a gFDR signature generated
analytically from (q_EA, tau_alpha, beta_KWW, tau_beta, X, T) via
gfdr_model.generate_kww_glass_locus. The five-vector is the INPUT, so every
library entry is self-labeling -- no inversion, no measurement read, all answer
key. These are the reference instances substrates get conformed AGAINST.

(Why not the Banach lambda-split? The analytical forward model is chit-only --
gamma never enters the leading-order locus -- so a lambda_gamma split moves no
observable. The five-vector library lives in the KWW generator, where the vector
is set directly.)

Hold the baseline, vary one vector at a time:
    python scripts/ideal_library.py --vary X     --values 1.0,0.75,0.5,0.25
    python scripts/ideal_library.py --vary q_EA  --values 0.4,0.6,0.8
    python scripts/ideal_library.py --vary beta_KWW --values 0.4,0.6,0.8,1.0

Run from repo root:  python scripts/ideal_library.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

from conformer.compute.gfdr_model import generate_kww_glass_locus

# Baseline five-vector (+ T). Glass-like, per the gfdr_model docstring.
BASELINE = dict(chit=0.0, q_EA=0.7, tau_alpha=50.0, beta_KWW=0.6, tau_beta=0.5, X=0.5, T=1.0)
VECTOR_KEYS = ("q_EA", "tau_alpha", "beta_KWW", "tau_beta", "X")


def main() -> None:
    ap = argparse.ArgumentParser(description="ideal-substrate library page (OFAT over five-vector)")
    ap.add_argument("--vary", choices=VECTOR_KEYS, default="X")
    ap.add_argument("--values", type=str, default="1.0,0.75,0.5,0.25")
    for k, v in BASELINE.items():
        ap.add_argument(f"--{k}", type=float, default=v)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    base = {k: getattr(args, k) for k in BASELINE}
    values = [float(x) for x in args.values.split(",")]
    cmap = cm.get_cmap("viridis", len(values))

    fig, (axl, axc) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=170)

    # equilibrium reference (X=1, slope 1)
    axl.plot([0, 1], [0, 1], ls="--", color="#888", lw=1, label="X=1 (equilibrium FDT)")

    print(f"OFAT over {args.vary}; baseline " +
          " ".join(f"{k}={v:g}" for k, v in base.items() if k != args.vary))
    print(f"{'value':>8}  {'q_EA':>5} {'tau_a':>6} {'bKWW':>5} {'tau_b':>5} {'X':>5}  knee(dC=1-q_EA)")

    for i, val in enumerate(values):
        p = dict(base)
        p[args.vary] = val
        loc = generate_kww_glass_locus(**p)
        C, chi, tau = loc["C"], loc["chi"], loc["tau"]
        dC = 1.0 - C
        col = cmap(i)

        axl.plot(dC, chi, color=col, lw=2,
                 label=f"{args.vary}={val:g}  (q_EA={p['q_EA']:g}, X={p['X']:g})")
        axc.plot(tau, C, color=col, lw=2, label=f"{args.vary}={val:g}")

        knee = 1.0 - p["q_EA"]
        print(f"{val:8g}  {p['q_EA']:5.2f} {p['tau_alpha']:6g} {p['beta_KWW']:5.2f} "
              f"{p['tau_beta']:5.2f} {p['X']:5.2f}  {knee:.3f}")

    # mark the plateau knee (where the aging branch starts) for the baseline q_EA
    if args.vary != "q_EA":
        axl.axvline(1.0 - base["q_EA"], ls=":", color="#c53030", lw=1, alpha=0.6)
        axl.text(1.0 - base["q_EA"], 0.02, " knee (q_EA)", color="#c53030", fontsize=8, rotation=90, va="bottom")

    axl.set_xlim(-0.02, 1.02); axl.set_ylim(-0.02, 1.05)
    axl.set_xlabel("dC = 1 - C(tau)"); axl.set_ylabel("chi  (T=1)")
    axl.set_title("gFDR locus -- aging branch slope = X")
    axl.legend(loc="upper left", fontsize=8, frameon=False)

    axc.set_xscale("log")
    axc.set_xlabel("tau"); axc.set_ylabel("C(tau)")
    axc.set_ylim(-0.02, 1.02)
    axc.set_title("correlator C(tau) -- two-step KWW")
    axc.legend(loc="upper right", fontsize=8, frameon=False)

    fig.suptitle(f"ideal-substrate library -- OFAT over {args.vary}  "
                 f"(five-vector = input = label; analytical, no measurement)",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    out_dir = REPO_ROOT / "output" / "ideal_library"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else out_dir / f"ideal_library_vary_{args.vary}.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nlibrary page: {out}")


if __name__ == "__main__":
    main()
