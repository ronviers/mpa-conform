"""flood_grid.py -- the synthetic basin map.

Tile the one-ball card (scripts/one_ball.py) across a (chit_bit, gamma) patch
so the c/s/r basins and the KILL region show up as one picture, and the
trajectories sit in relation to each other.

chit is reported in BITS per character_units.md: chit_bit = chit/ln2, and
chit_bit=1 (the Q-peak, chit=ln2) is the canonical cross-substrate comparison
point. Each cell is one ball's gFDR locus, coloured by its measured regime
(read from the locus, not from the input chit). Runaway balls show KILL --
a result, not an error.

Run from repo root:  python scripts/flood_grid.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
for p in (str(REPO_ROOT), str(SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conformer.compute.observables import gfdr_locus
from one_ball import INV_E, REGIME_COLOR, place_tau_obs, read_X, regime_from_X  # noqa: E402

LN2 = float(np.log(2.0))

# chit in BITS (chit_bit). Negatives = reset side; {0.5,1,2} are the
# character_units.md canonical sweep points; chit_bit=1 is the Q-peak.
CHIT_BITS = [-2.0, -1.0, 0.0, 0.5, 1.0, 2.0]
# gamma in D-units, rows ordered high->low so cooperative (<0) sits at the bottom.
GAMMAS = [0.6, 0.4, 0.2, 0.0, -0.2]


def one_cell(chit_bit: float, gamma: float, seed: int = 0) -> dict:
    chit = chit_bit * LN2
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # runaway emits overflow warnings; KILL is caught below
        try:
            loc = gfdr_locus(chit, gamma, seed=seed)
        except RuntimeError:
            return {"regime": "runaway", "X": None}
    C, chi = loc["C"], loc["chi"]
    dC_norm = 1.0 - C
    X, _ = read_X(dC_norm, chi)
    return {"regime": regime_from_X(X), "X": X, "dC": dC_norm, "chi": chi}


def main() -> None:
    nrow, ncol = len(GAMMAS), len(CHIT_BITS)
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 2.1, nrow * 2.0), dpi=160)

    text_grid: list[str] = []
    for i, g in enumerate(GAMMAS):
        row_syms: list[str] = []
        for j, cb in enumerate(CHIT_BITS):
            ax = axes[i][j]
            res = one_cell(cb, g)
            regime = res["regime"]
            col = REGIME_COLOR[regime]
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor(col)
                spine.set_linewidth(1.5)

            if regime == "runaway":
                ax.set_facecolor("#ececec")
                ax.text(0.5, 0.5, "diverged", ha="center", va="center",
                        fontsize=11, color=REGIME_COLOR["runaway"], weight="bold")
                row_syms.append("div")
            else:
                ax.set_facecolor(col + "14")  # faint regime tint (hex alpha)
                ax.plot([0, 1], [0, 1], ls="--", color="#999", lw=0.8)
                ax.plot(res["dC"], res["chi"], color=col, lw=1.8)
                ax.set_xlim(-0.02, 1.02)
                ax.set_ylim(-0.02, 1.05)
                Xs = "n/a" if res["X"] is None else f"{res['X']:.2f}"
                ax.text(0.04, 0.96, f"{regime.upper()}  X={Xs}", ha="left", va="top",
                        fontsize=9, color=col, weight="bold")
                row_syms.append(regime)

            if i == 0:
                star = "  *Q-peak" if abs(cb - 1.0) < 1e-9 else ""
                ax.set_title(f"chit_bit={cb:g}{star}", fontsize=10,
                             weight=("bold" if star else "normal"))
            if j == 0:
                ax.set_ylabel(f"gamma={g:g}", fontsize=10)
        text_grid.append(f"  gamma={g:+.1f} | " + "  ".join(f"{s:>4}" for s in row_syms))

    fig.suptitle("synthetic basin map -- gFDR loci across (chit_bit, gamma)   "
                 "[chit in bits, chit_bit=1 = Q-peak; X is single-slope triage]",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = REPO_ROOT / "output" / "one_ball" / "flood_grid.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    header = "          " + "  ".join(f"{cb:>4g}" for cb in CHIT_BITS)
    print("regime map (rows gamma, cols chit_bit):")
    print(header)
    for line in text_grid:
        print(line)
    print(f"\ngrid: {out}")


if __name__ == "__main__":
    main()
