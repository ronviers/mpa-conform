"""banach_ruler.py -- the Banach reference family (the ruler).

Renders the canonical Banach backbone's c -> s -> (r-limit) migration along
tau_obs (= the RG-flow depth nu). This is the REFERENCE substrates get conformed
AGAINST -- never the reverse (the arrow: substrate pristine and fixed, Banach
regenerable and conformed to it). It is the ruler, not a measurement.

Parameterized by FIELD OF VIEW (the chit zoom). tau_obs span = ln(FOV), so a
100x field of view costs only ~4.6 units of tau_obs and every number stays O(1)
(the exponential works for us: tau_obs is the LOG of the FOV). Reparameterize on
a whim:
    python scripts/banach_ruler.py --fov 1000 --steps 50
    python scripts/banach_ruler.py --fov 100 --chit0-ch 2 --gamma0 -0.5 --lam 1

chit reported in ch (= chit/ln2) per mpa_units.md; chit_ch=1 is the Q-peak.

Run from repo root:  python scripts/banach_ruler.py
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), "H:/mpa-scale-solver"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

import mpa_scale_solver as mss
from mpa_scale_solver.banach import BanachSubstrate

LN2 = math.log(2.0)
# Five-bucket canonical classifier (vertex_regime) -> a c->s->r colour gradient.
REGIME_COLOR = {
    "deep_c": "#1a4480", "c_near_s": "#2b6cb0",
    "s_critical": "#dd8b1a",
    "s_near_r": "#dd5a1a", "deep_r": "#c53030",
    "k_frust": "#2f855a",
}


def regime_color(label: str) -> str:
    if label in REGIME_COLOR:
        return REGIME_COLOR[label]
    if label.startswith("deep_c") or label.startswith("c"):
        return REGIME_COLOR["c_near_s"]
    if label.startswith("s"):
        return REGIME_COLOR["s_critical"]
    if label.startswith("r") or label.startswith("deep_r"):
        return REGIME_COLOR["deep_r"]
    return "#888"


CS_BOUNDARY_CH = 0.2 / LN2  # chit=0.2 is the Banach c/s boundary -> ~0.29 ch


def regime_of(state, nu: float) -> str:
    reading = mss.regime_at(state, float(nu))
    reg = getattr(reading.regime, "value", reading.regime)
    return str(reg)


def build(fov: float, chit0_ch: float, gamma0: float, lam: float, steps: int):
    sub = BanachSubstrate(
        chit_0=chit0_ch * LN2, gamma_AB_0=gamma0,
        lambda_chit=lam, lambda_gamma=lam,
    )
    nu_max = math.log(fov)
    nus = np.linspace(0.0, nu_max, steps)
    chit_ch, gammas, regimes = [], [], []
    for nu in nus:
        st = sub.state_at(float(nu))
        chit_ch.append(st.chit / LN2)
        gammas.append(st.gamma_AB)
        regimes.append(regime_of(st, nu))
    return nus, np.array(chit_ch), np.array(gammas), regimes


def main() -> None:
    ap = argparse.ArgumentParser(description="Banach reference ruler")
    ap.add_argument("--fov", type=float, default=100.0, help="chit dynamic range (zoom)")
    ap.add_argument("--chit0-ch", type=float, default=2.0, help="deep-c start, in ch")
    ap.add_argument("--gamma0", type=float, default=-0.5)
    ap.add_argument("--lam", type=float, default=1.0, help="canonical contraction rate")
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    nus, chit_ch, gammas, regimes = build(
        args.fov, args.chit0_ch, args.gamma0, args.lam, args.steps
    )
    cols = [regime_color(r) for r in regimes]

    fig, (axm, axt) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=170)

    # --- left: the migration along the camera (tau_obs) ---
    axm.plot(nus, chit_ch, color="#444", lw=1, zorder=1)
    axm.scatter(nus, chit_ch, c=cols, s=36, zorder=2, edgecolor="white", linewidth=0.4)
    axm.set_yscale("log")
    axm.axhline(CS_BOUNDARY_CH, ls="--", color="#c53030", lw=1, alpha=0.6)
    axm.text(nus[-1], CS_BOUNDARY_CH, " c/s boundary", color="#c53030", fontsize=8, va="bottom", ha="right")
    for lvl in (0.5, 1.0, 2.0):
        axm.axhline(lvl, ls=":", color="#999", lw=0.8)
        axm.text(0, lvl, f" {lvl:g} ch", color="#666", fontsize=8, va="bottom")
    axm.set_xlabel("tau_obs  (= nu, RG-flow depth;  span = ln FOV)")
    axm.set_ylabel("chit_ch  (= chit / ln2)   [log]")
    axm.set_title(f"migration along the camera  (FOV = {args.fov:g}x)")

    # --- right: the canonical (chit_ch, gamma) trajectory ---
    sc = axt.scatter(chit_ch, gammas, c=nus, cmap="viridis", s=40,
                     edgecolor="white", linewidth=0.4)
    axt.plot(chit_ch, gammas, color="#bbb", lw=0.8, zorder=0)
    axt.axvline(CS_BOUNDARY_CH, ls="--", color="#c53030", lw=1, alpha=0.6)
    axt.set_xscale("log")
    axt.invert_xaxis()  # flow runs left-to-right toward M_2 (origin)
    axt.set_xlabel("chit_ch   [log, flow ->]")
    axt.set_ylabel("gamma_AB")
    axt.set_title("canonical (chit_ch, gamma) -- the ray to M_2")
    fig.colorbar(sc, ax=axt, label="tau_obs")

    fig.suptitle(
        f"Banach reference family (the RULER) -- c -> s -> r-limit;  "
        f"conform substrates AGAINST this, never the reverse",
        fontsize=13, weight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    out_dir = REPO_ROOT / "output" / "banach_ruler"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else out_dir / f"banach_ruler_fov{args.fov:g}.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    # report
    print(f"FOV={args.fov:g}x  chit0={args.chit0_ch:g} ch  gamma0={args.gamma0:g}  "
          f"lam={args.lam:g}  steps={args.steps}")
    print(f"tau_obs span: [0, {nus[-1]:.3f}]   chit_ch: [{chit_ch[0]:.3f} -> {chit_ch[-1]:.4f}]   "
          f"gamma: [{gammas[0]:.3f} -> {gammas[-1]:.4f}]")
    print("regime sequence:", " ".join(regimes))
    print(f"ruler: {out}")


if __name__ == "__main__":
    main()
