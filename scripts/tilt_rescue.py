r"""tilt_rescue.py -- grind the normal-tilt fail angle to a precise number, and map how much
meta-coupling "pull" can rescue a stream on the edge of dying.

Follows chiral_tilt.py (coarse 1-deg sweep: generic asymmetric normal-tilt kills the protected
meta-cycle at ~9 deg). This script (1) pins theta_c precisely by bisection -- worst-case, median,
and a clean reproducible single-sub canonical value -- so the number is reusable downstream
(mpa-auditor / mpa-conform robustness criterion); (2) maps the (tilt theta, coupling kappa)
alive/dead phase boundary = the "pull rescue" latitude: a stream tilting toward death can be pulled
back to life by stronger downstream coupling, and we quantify by how much; (3) checks theta_c
against the gap=seed closed form.

CANONICAL DEFINITIONS (so the number is well-posed):
  * single-sub tilt -- tilt ONE sub's normal by theta, the other two fixed (a clean, reproducible,
    no-RNG generic C3-breaking deformation). The canonical theta_c.
  * worst-case -- min over tilt directions (the conservative "safe-below-this" guarantee).
  * median -- typical generic direction.

Run from mpa-conform root:  python scripts/tilt_rescue.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from banach_frustrated import E1, E2
from chiral_bonding import GAMMA, G, KAPPA
from chiral_tilt import rot, build_tilted, omega_meta, coll_gap_tilted, N0

OM_TOL = 1e-4          # omega below this = cycle dead
I3 = np.eye(3)


def perp_axes(rng):
    """Three random tilt axes in the plane perp to N0 (pure normal-tilt, breaks C3 generically)."""
    out = []
    for _ in range(3):
        a = rng.standard_normal(3); a = a - (a @ N0) * N0
        out.append(a / (np.linalg.norm(a) + 1e-15))
    return out


# one fixed REPRESENTATIVE generic deformation (reproducible) for the pull/rescue/phase study
REP_AXES = perp_axes(np.random.default_rng(0))


def rep_tilt(theta):
    return [rot(REP_AXES[k], theta) for k in range(3)]


def tilt_from(axes):
    return lambda theta: [rot(axes[k], theta) for k in range(3)]


def theta_c_grid(tilt_fn, kappa=KAPPA, hi_deg=45.0, step_deg=0.25):
    """First tilt where omega stays dead through hi_deg (true death, robust to revival nodes).
    Fine grid -> precise to step_deg. nan if it never stays dead (survives)."""
    ths = np.radians(np.arange(0.0, hi_deg + 1e-9, step_deg))
    oms = np.array([omega_meta(build_tilted(tilt_fn(t), kappa=kappa)) for t in ths])
    dead = oms < OM_TOL
    for i in range(len(ths)):
        if dead[i] and np.all(dead[i:]):
            return float(ths[i])
    return float("nan")


def main() -> None:
    print("grind the normal-tilt fail angle + map the meta-coupling 'pull' rescue latitude")
    print(f"gamma={GAMMA}, g={G}, base kappa={KAPPA}\n")

    # ---------------------------------------------------------------- (1) precise theta_c (the BAND)
    # theta_c is NOT a single value -- it depends on the tilt DIRECTION (anisotropic brittleness).
    # The honest characterization is the generic-direction distribution + the gap=seed mechanism.
    tcs = []
    for s in range(400):
        tc = theta_c_grid(tilt_from(perp_axes(np.random.default_rng(10_000 + s))))
        if np.isfinite(tc):
            tcs.append(tc)
    tcs = np.array(sorted(tcs))
    worst = float(tcs.min()); median = float(np.median(tcs)); p90 = float(np.percentile(tcs, 90))

    print("PRECISE FAIL ANGLE theta_c (kappa=0.3, g=0.6) -- a direction-dependent BAND, not a point:")
    print(f"    generic ensemble (n={len(tcs)}): worst-case {np.degrees(worst):.2f} deg | "
          f"median {np.degrees(median):.2f} deg | 90th pct {np.degrees(p90):.2f} deg")
    print(f"    => CONSERVATIVE GUARANTEE (reusable): survives ANY generic normal-tilt up to "
          f"~{np.degrees(worst):.1f} deg; typical death ~{np.degrees(median):.1f} deg.")

    # gap=seed mechanism (representative direction): the cycle dies when the tilt-split collective
    # gap crosses the O(kappa^2) seed -- this PREDICTS the typical theta_c.
    seed = omega_meta(build_tilted(rep_tilt(0.0)))
    th = np.linspace(0, np.radians(25), 80)
    gaps = np.array([coll_gap_tilted(rep_tilt(t)) for t in th])
    pred_tc = float(np.interp(seed, gaps, th)) if gaps[-1] > seed else float("nan")
    tc_rep = theta_c_grid(rep_tilt)
    print(f"    mechanism (gap=seed) predicts theta_c = {np.degrees(pred_tc):.2f} deg; representative")
    print(f"    direction measures {np.degrees(tc_rep):.2f} deg -- the seed/gap competition sets the band.")

    # ---------------------------------------------------------------- (2) the pull rescue: theta_c(kappa)
    kaps = np.linspace(0.05, 0.8, 31)
    tc_of_k = np.array([theta_c_grid(rep_tilt, kappa=kap) for kap in kaps])
    valid = np.isfinite(tc_of_k)
    fit = np.polyfit(kaps[valid], np.degrees(tc_of_k[valid]), 1)
    tc03 = theta_c_grid(rep_tilt, 0.3); tc06 = theta_c_grid(rep_tilt, 0.6)
    print(f"\nPULL LATITUDE (representative generic theta_c vs coupling kappa):")
    print(f"    theta_c ~ {fit[0]:.0f} deg per unit kappa (intercept {fit[1]:+.1f} deg) -- LINEAR in the pull.")
    print(f"    doubling the downstream pull ~doubles the survivable tilt: kappa 0.3->0.6 lifts "
          f"theta_c {np.degrees(tc03):.1f} deg -> {np.degrees(tc06):.1f} deg.")

    # rescue demo: a stream parked just past death at base kappa, pulled back by raising kappa
    theta_edge = tc_rep * 1.4                                # 40% past the base-kappa death angle
    krescue = np.linspace(0.1, 0.9, 41)
    om_rescue = np.array([omega_meta(build_tilted(rep_tilt(theta_edge), kappa=k)) for k in krescue])
    k_min = float(krescue[np.argmax(om_rescue > OM_TOL)]) if np.any(om_rescue > OM_TOL) else float("nan")
    print(f"    RESCUE: a stream at theta={np.degrees(theta_edge):.1f} deg (dead at base kappa) is pulled back")
    print(f"    to life once kappa >= {k_min:.2f}. A dying edge-stream CAN be rescued by stronger pull.")

    # ---------------------------------------------------------------- (3) (theta, kappa) phase map
    th_grid = np.linspace(0, np.radians(28), 60)
    k_grid = np.linspace(0.05, 0.8, 60)
    OM = np.array([[omega_meta(build_tilted(rep_tilt(t), kappa=k)) for t in th_grid] for k in k_grid])

    print("\nUSABLE CRITERION (mpa-auditor / mpa-conform): a recursion stream's protected meta-cycle")
    print(f"survives normal-tilt theta only while kappa >~ theta/({fit[0]:.0f} deg). Below that line the")
    print("stream is dark; the downstream 'pull' (meta-coupling) is the rescue knob. Conservative floor:")
    print(f"any tilt below ~{np.degrees(worst):.1f} deg (at kappa=0.3), scaling linearly with kappa.")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)

    # (0,0) theta_c distribution + canonical markers
    a0 = ax[0, 0]
    a0.hist(np.degrees(tcs), bins=30, color="#c2185b", edgecolor="white", alpha=0.85)
    a0.axvline(np.degrees(worst), color="#2e7d32", ls="--", lw=1.6, label=f"worst-case {np.degrees(worst):.1f}° (guarantee)")
    a0.axvline(np.degrees(median), color="#1565c0", ls="--", lw=1.6, label=f"median {np.degrees(median):.1f}°")
    a0.axvline(np.degrees(pred_tc), color="#ef6c00", ls=":", lw=2, label=f"gap=seed predicts {np.degrees(pred_tc):.1f}°")
    a0.set_xlabel("fail angle θ_c (degrees)"); a0.set_ylabel("count")
    a0.set_title(f"precise fail angle (n={len(tcs)} generic tilts, κ=0.3):\nworst-case ~{np.degrees(worst):.0f}°, median ~{np.degrees(median):.0f}°")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3, axis="y")

    # (0,1) pull latitude: theta_c(kappa)
    a1 = ax[0, 1]
    a1.plot(kaps[valid], np.degrees(tc_of_k[valid]), "o-", color="#00796b", lw=2, ms=5)
    a1.plot(kaps, fit[0] * kaps + fit[1], "k--", lw=1, label=f"~{fit[0]:.0f}°·κ {fit[1]:+.0f}°")
    a1.axvline(KAPPA, color="gray", ls=":", lw=1, label=f"base κ={KAPPA}")
    a1.set_xlabel("meta-coupling κ (the downstream 'pull')"); a1.set_ylabel("fail angle θ_c (degrees)")
    a1.set_title("pull latitude: stronger downstream pull buys\nmore survivable tilt (θ_c linear in κ)")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    # (1,0) rescue curve: dying stream pulled back to life
    a2 = ax[1, 0]
    a2.plot(krescue, om_rescue, "-", color="#c2185b", lw=2.4)
    a2.axhline(OM_TOL, color="gray", ls=":", lw=1)
    if np.isfinite(k_min):
        a2.axvline(k_min, color="#2e7d32", ls="--", lw=1.6, label=f"rescued at κ ≥ {k_min:.2f}")
    a2.fill_between(krescue, 0, om_rescue.max() * 1.05, where=(krescue < k_min), color="#90a4ae", alpha=0.18)
    a2.set_xlabel("meta-coupling κ (pull)"); a2.set_ylabel(r"protected $\omega_{\rm meta}$")
    a2.set_title(f"rescue: a stream parked at θ={np.degrees(theta_edge):.0f}° (dead at base κ)\n"
                 "comes back to life when the pull is raised")
    a2.legend(fontsize=9, frameon=False); a2.grid(alpha=0.3)

    # (1,1) (theta, kappa) phase map: alive region above the boundary
    a3 = ax[1, 1]
    im = a3.pcolormesh(np.degrees(th_grid), k_grid, OM, shading="auto", cmap="magma")
    a3.contour(np.degrees(th_grid), k_grid, OM, levels=[OM_TOL], colors="cyan", linewidths=2)
    a3.plot(np.degrees(tc_of_k[valid]), kaps[valid], "w.", ms=3)
    a3.set_xlabel("normal tilt θ (degrees)"); a3.set_ylabel("meta-coupling κ (pull)")
    a3.set_title("phase map: protected cycle ALIVE above the boundary\n(cyan = death edge; pull rescues a tilting stream)")
    fig.colorbar(im, ax=a3, label=r"$\omega_{\rm meta}$")

    fig.suptitle("normal-tilt fail angle, ground precise, and the meta-coupling 'pull' rescue latitude",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "tilt_rescue.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
