"""one_ball.py -- the minimal viable flood: ONE ball, shown through tau_obs.

A "ball" = one operating point (chit, gamma_AB) released into the universal
two-mode kernel. We run the real gFDR (two INDEPENDENT ensembles, per the
observation_window_sweep_v13 data-path-independence rule -- C and chi are never
each other by fiat), place tau_obs at the substrate's OWN relaxation time
(unsupervised; never dialed to make a regime appear), and read the FDR slope X
from the measurement, not from the input chit.

Output: one "ball card" PNG -- correlator + gFDR locus + verdict. This card is
the tile the flood grid will later be built from. One ball now.

A ball whose kernel runs away is reported as a KILL (a result), not swallowed.

Run from the repo root:
    python scripts/one_ball.py                 # default ball
    python scripts/one_ball.py --chit 0.0 --gamma -0.3
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

from conformer.compute.observables import gfdr_locus

INV_E = float(np.exp(-1.0))

# Regime -> colour. Colour maps to the verdict (data), not decoration.
# "over" = single-slope X > 1, which the engine excludes (X>>1 is the
# documented upward bias of single-slope on a curved locus) -- flagged, not
# clamped, and a signal the five-vector read is mandatory here.
REGIME_COLOR = {"c": "#2b6cb0", "s": "#dd8b1a", "r": "#c53030",
                "over": "#7c3aed", "runaway": "#1a1a1a"}


def place_tau_obs(tau: np.ndarray, C: np.ndarray) -> tuple[float, bool]:
    """tau_obs = the ball's own relaxation time: first lag where the
    normalized correlator C(tau)/C(0) falls to 1/e. Substrate-set, not
    tuned. Returns (tau_obs, resolved); resolved=False means the watch
    never reached the decay (under-resolved -- an honest flag)."""
    below = np.nonzero(C <= INV_E)[0]
    if below.size == 0:
        return float(tau[-1]), False
    return float(tau[below[0]]), True


def read_X(dC_norm: np.ndarray, chi_norm: np.ndarray) -> tuple[float | None, np.ndarray]:
    """Single-slope FDR ratio X = slope of chi_norm vs dC_norm over the
    resolved band dC_norm in [0.1, 0.9]. NOTE: single-slope biases UP --
    fine for one-ball triage, not a certified read (use five-vector for
    that). Returns (X, mask)."""
    mask = (dC_norm >= 0.1) & (dC_norm <= 0.9) & np.isfinite(chi_norm) & np.isfinite(dC_norm)
    if mask.sum() < 2:
        return None, mask
    slope = float(np.polyfit(dC_norm[mask], chi_norm[mask], 1)[0])
    return slope, mask


def regime_from_X(X: float | None) -> str:
    if X is None:
        return "s"  # undefined band -> treat as ambiguous middle
    if X < 0.25:
        return "c"          # suppressed, horizontal locus
    if X > 1.15:
        return "over"       # X>1 excluded -> single-slope failed; five-vector needed
    if X > 0.75:
        return "r"          # unit slope, equilibrium
    return "s"              # aging, below the diagonal


def card(chit: float, gamma: float, out_path: Path, seed: int = 0) -> dict:
    title = f"ball  chit={chit:+.2f}  gamma={gamma:+.2f}"
    try:
        loc = gfdr_locus(chit, gamma, seed=seed)
    except RuntimeError as e:
        # The ball rolled off the table. A result, not an error to hide.
        fig, ax = plt.subplots(figsize=(12, 5), dpi=200)
        ax.set_axis_off()
        ax.text(0.5, 0.6, "DIVERGED", ha="center", va="center",
                fontsize=52, color=REGIME_COLOR["runaway"], weight="bold")
        ax.text(0.5, 0.4, f"{title}\nkernel ran away: {e}", ha="center", va="center",
                fontsize=13, color="#444")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return {"regime": "runaway", "X": None, "tau_obs": None, "reason": str(e)}

    tau, C, chi = loc["tau"], loc["C"], loc["chi"]
    dC_norm = 1.0 - C          # grows 0 -> 1
    chi_norm = chi             # grows 0 -> 1 in equilibrium
    tau_obs, resolved = place_tau_obs(tau, C)
    X, mask = read_X(dC_norm, chi_norm)
    regime = regime_from_X(X)
    col = REGIME_COLOR[regime]

    fig, (axc, axl) = plt.subplots(1, 2, figsize=(12, 5), dpi=200)

    # --- left: correlator with the watch window marked ---
    axc.plot(tau, C, color=col, lw=2)
    axc.axhline(INV_E, ls=":", color="#888", lw=1)
    axc.axvspan(tau[0], tau_obs, color=col, alpha=0.10)
    axc.axvline(tau_obs, ls="--", color=col, lw=1.5)
    axc.set_xscale("log")
    axc.set_xlim(left=float(tau[1]), right=float(tau[-1]))  # tau[0]=0 would stretch the log axis to nothing
    axc.set_xlabel("lag  tau")
    axc.set_ylabel("C(tau) / C(0)")
    axc.set_ylim(-0.05, 1.05)
    axc.set_title("watch the ball relax")
    axc.text(tau_obs, 1.0, f"  tau_obs={tau_obs:.2f}" + ("" if resolved else "  (under-resolved)"),
             color=col, fontsize=10, va="top")

    # --- right: gFDR locus with the equilibrium diagonal + measured slope ---
    axl.plot([0, 1], [0, 1], ls="--", color="#888", lw=1, label="X=1 (equilibrium FDT)")
    axl.plot(dC_norm, chi_norm, color=col, lw=2, label="this ball")
    if X is not None:
        xs = np.array([0.0, 1.0])
        axl.plot(xs, X * xs, color=col, lw=1, ls="-.", alpha=0.7,
                 label=f"slope X={X:.2f}")
    axl.set_xlim(-0.02, 1.02)
    axl.set_ylim(-0.02, 1.05)
    axl.set_xlabel("dC_norm = 1 - C(tau)/C(0)")
    axl.set_ylabel("chi_norm")
    axl.set_title("gFDR locus")
    axl.legend(loc="upper left", fontsize=9, frameon=False)

    verdict = {"c": "committed (held)", "s": "suspended (aging)", "r": "reset / equilibrium",
               "over": "X>1 -- excluded (five-vector needed)"}[regime]
    Xs = "n/a" if X is None else f"{X:.2f}"
    fig.suptitle(f"{title}   ->   {regime.upper()}: {verdict}   (X={Xs}, single-slope triage)",
                 fontsize=14, color=col, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return {"regime": regime, "X": X, "tau_obs": tau_obs, "resolved": resolved}


def main() -> None:
    ap = argparse.ArgumentParser(description="one ball through tau_obs")
    ap.add_argument("--chit", type=float, default=0.5)
    ap.add_argument("--gamma", type=float, default=-0.3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    out_dir = REPO_ROOT / "output" / "one_ball"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else out_dir / f"ball_chit{args.chit:+.2f}_g{args.gamma:+.2f}.png"

    res = card(args.chit, args.gamma, out_path, seed=args.seed)
    print(f"ball chit={args.chit:+.2f} gamma={args.gamma:+.2f} -> {res['regime'].upper()}"
          f"  X={res['X']}  tau_obs={res['tau_obs']}")
    print(f"card: {out_path}")


if __name__ == "__main__":
    main()
