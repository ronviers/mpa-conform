"""normalize_chit.py -- one-at-a-time normalization probe.

Hold gamma=0 (the orthogonal axis). Sweep chit in BITS. Run N seeds. Watch
X(chit_bit): does it settle to a forced fraction near the Q-peak
(chit_bit=1), or wander?

Discipline:
  - Single-slope X biases UP, so the TRUE value sits at or below the band.
    2/3 and 3/4 are drawn as references; we read the floor, never one point.
  - Seed-spread is the margin m (character_units.md): can we even tell 2/3 from 3/4
    here? margin = |3/4 - 2/3| / std.
  - Every divergence gets a dt-refine recheck. If halving dt makes it finite,
    the non-finite was NUMERICAL (artifact of a crossed/clamped zero); if it
    persists, it is a candidate genuine boundary. Tagged, never hidden, never
    relabelled as a verdict.

Run from repo root:  python scripts/normalize_chit.py
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
from one_ball import read_X  # noqa: E402

LN2 = float(np.log(2.0))
GAMMA = 0.0                      # the orthogonal axis
CHIT_BITS = np.linspace(-2.0, 2.0, 21)
SEEDS = range(8)
TWO_THIRDS, THREE_QUARTERS = 2.0 / 3.0, 3.0 / 4.0


def x_at(chit: float, seed: int, dt: float) -> float | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loc = gfdr_locus(chit, GAMMA, seed=seed, dt=dt)  # raises on divergence
    X, _ = read_X(1.0 - loc["C"], loc["chi"])
    return X


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dt", type=float, default=0.01)
    DT = ap.parse_args().dt

    means, stds, ns = [], [], []
    diverge_log: list[str] = []
    for cb in CHIT_BITS:
        chit = cb * LN2
        xs: list[float] = []
        for s in SEEDS:
            try:
                X = x_at(chit, s, dt=DT)
            except RuntimeError:
                # dt-refine recheck: fake (numerical) vs persistent (boundary?)
                try:
                    x_at(chit, s, dt=DT / 2.0)
                    diverge_log.append(f"  chit_bit={cb:+.2f} seed={s}: NUMERICAL (finite at dt/2)")
                except RuntimeError:
                    diverge_log.append(f"  chit_bit={cb:+.2f} seed={s}: PERSISTENT (diverges at dt/2 too)")
                continue
            if X is not None and np.isfinite(X):
                xs.append(X)
        if xs:
            means.append(float(np.mean(xs)))
            stds.append(float(np.std(xs)))
            ns.append(len(xs))
        else:
            means.append(np.nan); stds.append(np.nan); ns.append(0)

    means = np.array(means); stds = np.array(stds)

    # --- plot ---
    fig, ax = plt.subplots(figsize=(11, 6), dpi=170)
    ax.axhline(1.0, ls="-", color="#7c3aed", lw=1, alpha=0.6, label="X=1 (over / excluded above)")
    ax.axhline(THREE_QUARTERS, ls=":", color="#666", lw=1, label="3/4")
    ax.axhline(TWO_THIRDS, ls=":", color="#999", lw=1, label="2/3")
    ax.axvline(0.0, ls="--", color="#dd8b1a", lw=1, alpha=0.7)
    ax.axvline(1.0, ls="--", color="#2b6cb0", lw=1.2)
    ax.text(1.0, 0.02, " Q-peak", color="#2b6cb0", fontsize=10, va="bottom")
    ax.text(0.0, 0.02, " threshold", color="#dd8b1a", fontsize=10, va="bottom", ha="right")

    finite = np.isfinite(means)
    ax.errorbar(CHIT_BITS[finite], means[finite], yerr=stds[finite],
                fmt="o-", color="#1a1a1a", ecolor="#888", capsize=3, lw=1.5, ms=4,
                label="single-slope X (biases UP -> true X is at/below)")
    ax.set_xlabel("chit_bit  (chit / ln2;  Q-peak = 1)")
    ax.set_ylabel("X  (FDR ratio, single-slope)")
    ax.set_ylim(0.0, 1.3)
    ax.set_title(f"normalize chit, hold gamma=0 (orthogonal axis) -- X(chit_bit), {len(list(SEEDS))} seeds, dt={DT}")
    ax.legend(loc="upper left", fontsize=9, frameon=False)

    out = REPO_ROOT / "output" / "one_ball" / f"normalize_chit_gamma0_dt{DT}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    # --- report ---
    print(f"gamma=0 sweep, {len(list(SEEDS))} seeds, single-slope X (biases up):\n")
    print("  chit_bit   meanX    std    n")
    for cb, m, sd, n in zip(CHIT_BITS, means, stds, ns):
        mark = "  <- Q-peak" if abs(cb - 1.0) < 1e-9 else ("  <- threshold" if abs(cb) < 1e-9 else "")
        ms = "   nan " if not np.isfinite(m) else f"{m:6.3f}"
        ss = "  nan" if not np.isfinite(sd) else f"{sd:5.3f}"
        print(f"  {cb:+6.2f}   {ms}  {ss}  {n:2d}{mark}")

    # margin: can we tell 2/3 from 3/4 at the Q-peak?
    qi = int(np.argmin(np.abs(CHIT_BITS - 1.0)))
    if np.isfinite(stds[qi]) and stds[qi] > 0:
        margin = abs(THREE_QUARTERS - TWO_THIRDS) / stds[qi]
        print(f"\n  Q-peak: X = {means[qi]:.3f} +/- {stds[qi]:.3f} (single-slope, biased up)")
        print(f"  margin to separate 2/3 from 3/4 here: |3/4-2/3|/std = {margin:.1f}"
              f"  ({'resolvable' if margin >= 10 else 'NOT resolvable at m>=10'})")

    if diverge_log:
        print("\n  divergences (fake vs persistent, by dt-refine):")
        print("\n".join(diverge_log))
    else:
        print("\n  no divergences on the gamma=0 axis (runaways are off-axis / coupling-induced).")
    print(f"\n  plot: {out}")


if __name__ == "__main__":
    main()
