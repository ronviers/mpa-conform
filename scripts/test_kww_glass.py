"""KWW-extension diagnostic: does the glass community's apparatus close the gap?

Standalone test of whether freeing (q_EA, tau_alpha, beta_KWW, tau_beta) as
direct parameters -- instead of projecting them through chit via
alpha_s(chit) and plateau_height(chit) -- lets the analytical model reach
the empirical's shape at glass T=0.5.

Renders one figure with three curves on the C(tau) and chi(tau) panels:
  - empirical (black markers) from the grind cell
  - current 1-parameter model at lens-solver chit (blue)
  - KWW-extended model at hand-picked glass params (green)

If green traces the empirical, the path is real and we propagate to the
production model + grind + Banach. If it doesn't, look at what's still
missing before committing.

Run:
    python -m scripts.test_kww_glass
or
    python H:/mpa-conform/scripts/test_kww_glass.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.compute import gfdr_model


CELL_PATH = Path("H:/mpa-central/library/data/glass/glass__T0.500__spin-flip.json")

# Hand-picked glass parameters. Plausible starting point for glass T=0.5:
#   q_EA       ~ 0.7    Edwards-Anderson plateau, between empirical's 0.94 and 0.56
#   tau_alpha  ~ 10     alpha-relaxation onset in dimensionless tau
#   beta_KWW   ~ 0.7    typical stretching exponent for spin glasses
#   tau_beta   ~ 0.5    beta-piece timescale (same as current hardcoded)
Q_EA = 0.94
TAU_ALPHA = 137.0
BETA_KWW = 0.5
TAU_BETA = 0.3
# FDT-violation ratio (X=1 means FDT holds; X<1 means aging-FDT violated).
# Back-of-envelope on T*chi-vs-dC plot:
#   (T*chi_end - (1-q_EA)) / (dC_end - (1-q_EA))
#   = (0.5*0.42 - 0.06) / (0.44 - 0.06) = 0.15 / 0.38 ~= 0.40
X_FDT = 0.4

# dt-axis variant (axis = sample.dt / tau_scale_median). Dimensionless
# range is [0.0013, 40] -- spans 4.5 decades, so the small-tau cluster
# the t-axis bunched into a hairpin gets spread cleanly across the
# beta-piece's natural range. Beta-piece needs a small tau_beta to live
# in that range.
Q_EA_DT = 0.94
TAU_ALPHA_DT = 200.0
BETA_KWW_DT = 0.4
TAU_BETA_DT = 0.002
X_FDT_DT = 0.4

# Aging-warp variant (axis = sample.dt / t_w). Same KWW form, different
# internal timescales because the dimensionless tau range changed.
Q_EA_AGING = 0.94
TAU_ALPHA_AGING = 300.0
BETA_KWW_AGING = 0.5
TAU_BETA_AGING = 0.005
X_FDT_AGING = 0.4

# Lens-solver chit for this cell (from the cross_path_disagreement test).
LENS_CHIT = 0.55


def kww_glass_locus(
    q_EA: float, tau_alpha: float, beta_KWW: float, tau_beta: float,
    *, X: float = 1.0, T: float = 1.0,
    n_points: int = 1000, tau_min: float = 1e-4, tau_max: float = 1e3,
) -> dict:
    """Classical glass decomposition with the four C-axis parameters AND
    the FDT-violation chi axis (the missing axis).

    C(tau) = (1 - q_EA) * exp(-tau / tau_beta)
           + q_EA       * exp(-(tau / tau_alpha) ** beta_KWW)

    chi(C): FDT / FDT-violation piecewise linear (CK 1993 / BCKM review):
      - Equilibrium branch (C >= q_EA, i.e., dC <= 1-q_EA):
          T*chi = dC          (FDT holds; slope 1 on the (dC, T*chi) plot)
      - Aging branch (C < q_EA, i.e., dC > 1-q_EA):
          T*chi = (1-q_EA) + X * (dC - (1-q_EA))   (FDT-violated)

    X is the FDT-violation ratio (= T/T_eff). X -> 1 = quasi-equilibrium
    aging; X -> 0 = frozen aging. Distinct from beta_KWW (time-axis
    stretching exponent). T is the substrate's operating-point temperature.
    Previous revision conflated X with beta_KWW and dropped the 1/T
    factor on the equilibrium branch.
    """
    ts = np.linspace(0.0, 1.0, n_points)
    tau = tau_min * np.power(tau_max / tau_min, ts)

    C_beta = (1.0 - q_EA) * np.exp(-tau / tau_beta)
    C_alpha = q_EA * np.exp(-np.power(tau / tau_alpha, beta_KWW))
    C = C_beta + C_alpha
    dC = 1.0 - C

    threshold = 1.0 - q_EA
    chi = np.where(
        dC <= threshold,
        dC / T,
        (threshold + X * (dC - threshold)) / T,
    )

    return {"tau": tau, "C": C, "chi": chi}


def load_empirical(cell_path: Path):
    cell = json.loads(cell_path.read_text(encoding="utf-8"))
    samples = cell["results"]["all_samples"]

    # Two candidate time axes for the FDR parametric plot:
    #   sample.t  -- sample-time (= t_w + dt). What walk_library currently
    #                identifies as "tau" in the bundle's observable.data.
    #   sample.dt -- lag since snapshot (= t - t_w). The framework's
    #                nominal "tau" per CK 1993 / RULES rule 3.
    # At early samples these differ by ~500x; at late samples they converge.
    sample_t = np.array([float(s["t"]) for s in samples])
    sample_dt = np.array([float(s["dt"]) for s in samples])
    t_w = float((cell.get("schedule") or {}).get("t_w", 0.0))

    # Match walk_library._resolve_tau_scale for the legacy axis (sample.t):
    # prefer tau_env_analytic.value when finite/positive; otherwise fall
    # back to median. T=0.5 is below Tc -- tau_env_analytic.value is null
    # per rule 13's aging-window-bounded fallback.
    tau_env = (cell.get("tau_env_analytic") or {}).get("value")
    if isinstance(tau_env, (int, float)) and tau_env > 0 and tau_env == tau_env:
        tau_scale = float(tau_env)
    else:
        tau_scale = float(np.median(sample_t))
    tau_native = sample_t  # legacy axis for backward-compat references
    C = np.array([float(s["C_mean"]) for s in samples])
    chi = np.array([float(s["chi_mean"]) for s in samples])
    C_sem = np.array([float(s.get("C_sem") or 0.0) for s in samples])
    chi_sem = np.array([float(s.get("chi_sem") or 0.0) for s in samples])

    return {
        "tau_dim_t": sample_t / tau_scale,           # bundle's current axis
        "tau_dim_dt": sample_dt / tau_scale,         # framework lag, linear rescale
        "tau_dim_tw_aging": sample_dt / t_w,         # t_w-anchored aging (CK 1993)
        "C": C, "chi": chi, "C_sem": C_sem, "chi_sem": chi_sem,
        "tau_scale": tau_scale, "t_w": t_w,
        "operating_point": cell.get("operating_point", {}),
        "substrate": cell.get("substrate"),
        "xdot_kind": cell.get("xdot_kind"),
    }


def interp_log_tau(model: dict, tau_query_arr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Cs = np.array([gfdr_model._interp_log_tau(model, float(t))[0] for t in tau_query_arr])
    chis = np.array([gfdr_model._interp_log_tau(model, float(t))[1] for t in tau_query_arr])
    return Cs, chis


def _draw_axis(ax_C, ax_chi, tau_dim, emp, kww_C_at, kww_chi_at, current_C_at,
               current_chi_at, axis_label: str) -> tuple[float, float, float, float]:
    rms_current_C = float(np.sqrt(np.mean((emp["C"] - current_C_at) ** 2)))
    rms_kww_C = float(np.sqrt(np.mean((emp["C"] - kww_C_at) ** 2)))
    rms_current_chi = float(np.sqrt(np.mean((emp["chi"] - current_chi_at) ** 2)))
    rms_kww_chi = float(np.sqrt(np.mean((emp["chi"] - kww_chi_at) ** 2)))

    ax_C.errorbar(tau_dim, emp["C"], yerr=emp["C_sem"], fmt="o", color="black",
                  markersize=4, capsize=2, zorder=3, label="empirical")
    ax_C.plot(tau_dim, current_C_at, color="C0", linewidth=1.6, zorder=2,
              label=f"current 1-param (RMS={rms_current_C:.3f})")
    ax_C.plot(tau_dim, kww_C_at, color="C2", linewidth=1.8, zorder=2,
              label=f"KWW-extended (RMS={rms_kww_C:.3f})")
    ax_C.set_xscale("log")
    ax_C.set_ylabel("C(tau)")
    ax_C.set_title(f"x-axis: {axis_label}", fontsize=10)
    ax_C.legend(loc="best", fontsize=8, frameon=False)
    ax_C.grid(True, alpha=0.25)

    ax_chi.errorbar(tau_dim, emp["chi"], yerr=emp["chi_sem"], fmt="o", color="black",
                    markersize=4, capsize=2, zorder=3, label="empirical")
    ax_chi.plot(tau_dim, current_chi_at, color="C0", linewidth=1.6, zorder=2,
                label=f"current 1-param (RMS={rms_current_chi:.3f})")
    ax_chi.plot(tau_dim, kww_chi_at, color="C2", linewidth=1.8, zorder=2,
                label=f"KWW-extended (RMS={rms_kww_chi:.3f})")
    ax_chi.set_xscale("log")
    ax_chi.set_xlabel(f"tau ({axis_label}) dimensionless")
    ax_chi.set_ylabel("chi(tau)")
    ax_chi.legend(loc="best", fontsize=8, frameon=False)
    ax_chi.grid(True, alpha=0.25)
    return rms_current_C, rms_kww_C, rms_current_chi, rms_kww_chi


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    emp = load_empirical(CELL_PATH)
    T_subs = float(emp["operating_point"].get("T", 1.0))

    current_model = gfdr_model.generate_locus(LENS_CHIT)
    # Each axis variant gets its own KWW timescales tuned to its
    # dimensionless tau range. Physical params (q_EA, X, beta_KWW) are
    # the same substrate properties; timescales (tau_alpha, tau_beta)
    # rescale with the axis denominator.
    kww_model_t = kww_glass_locus(
        Q_EA, TAU_ALPHA, BETA_KWW, TAU_BETA,
        X=X_FDT, T=T_subs,
    )
    kww_model_dt = kww_glass_locus(
        Q_EA_DT, TAU_ALPHA_DT, BETA_KWW_DT, TAU_BETA_DT,
        X=X_FDT_DT, T=T_subs,
        tau_min=1e-5, tau_max=1e3,
    )
    kww_model_aging = kww_glass_locus(
        Q_EA_AGING, TAU_ALPHA_AGING, BETA_KWW_AGING, TAU_BETA_AGING,
        X=X_FDT_AGING, T=T_subs,
        tau_min=1e-5, tau_max=1e3,
    )

    # KEY: the model evaluates at the substrate's natural time variable
    # (lag = sample.dt) regardless of what x-axis the plot uses. The
    # current revision was conflating "x-axis label" with "model internal
    # time" -- the missing thing the hairpin diagnostic surfaced.
    # All three columns evaluate KWW at lag-anchored tau internally; the
    # x-axis only determines where the curve is *drawn*, not where it is
    # *sampled*. The current 1-param model stays naive (samples at the
    # plot x-axis) so the comparison shows the cost of the conflation.
    cur_C_t, cur_chi_t = interp_log_tau(current_model, emp["tau_dim_t"])
    kww_C_t, kww_chi_t = interp_log_tau(kww_model_dt, emp["tau_dim_dt"])
    cur_C_dt, cur_chi_dt = interp_log_tau(current_model, emp["tau_dim_dt"])
    kww_C_dt, kww_chi_dt = interp_log_tau(kww_model_dt, emp["tau_dim_dt"])
    cur_C_aging, cur_chi_aging = interp_log_tau(current_model, emp["tau_dim_tw_aging"])
    kww_C_aging, kww_chi_aging = interp_log_tau(kww_model_dt, emp["tau_dim_dt"])
    # kww_model_t / kww_model_aging are no longer used -- the model only
    # needs one parameterization (in lag-anchored time); the x-axis is
    # display-only.
    _ = (kww_model_t, kww_model_aging)

    fig, axes = plt.subplots(2, 3, figsize=(18, 8), sharey="row")
    (ax_C_t, ax_C_dt, ax_C_aging), (ax_chi_t, ax_chi_dt, ax_chi_aging) = axes

    rms_t = _draw_axis(
        ax_C_t, ax_chi_t, emp["tau_dim_t"], emp, kww_C_t, kww_chi_t,
        cur_C_t, cur_chi_t,
        axis_label="sample.t / tau_scale  (current bundle)",
    )
    rms_dt = _draw_axis(
        ax_C_dt, ax_chi_dt, emp["tau_dim_dt"], emp, kww_C_dt, kww_chi_dt,
        cur_C_dt, cur_chi_dt,
        axis_label="sample.dt / tau_scale  (framework lag, linear rescale)",
    )
    rms_aging = _draw_axis(
        ax_C_aging, ax_chi_aging, emp["tau_dim_tw_aging"], emp,
        kww_C_aging, kww_chi_aging, cur_C_aging, cur_chi_aging,
        axis_label="sample.dt / t_w  (CK1993 aging-anchored)",
    )

    op = emp["operating_point"]
    title = (
        f"KWW + time-warp test  ·  glass {op.get('label', '?')}  ·  "
        f"gt_regime={op.get('gt', '?')}  ·  xdot={emp['xdot_kind']}  ·  "
        f"t_w={emp['t_w']:.0f}, tau_scale_median={emp['tau_scale']:.1f}\n"
        f"KWW(t-axis): q_EA={Q_EA}, tau_alpha={TAU_ALPHA}, beta_KWW={BETA_KWW}, tau_beta={TAU_BETA}, X={X_FDT}, T={T_subs}    "
        f"KWW(dt-axis): q_EA={Q_EA_DT}, tau_alpha={TAU_ALPHA_DT}, beta_KWW={BETA_KWW_DT}, tau_beta={TAU_BETA_DT}, X={X_FDT_DT}    "
        f"KWW(aging-warp): q_EA={Q_EA_AGING}, tau_alpha={TAU_ALPHA_AGING}, beta_KWW={BETA_KWW_AGING}, tau_beta={TAU_BETA_AGING}, X={X_FDT_AGING}"
    )
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()

    out_dir = REPO_ROOT / "output" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kww_glass_test__T0.500__spin-flip.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)

    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    for label, rms in [
        ("sample.t (current bundle)", rms_t),
        ("sample.dt (framework lag)", rms_dt),
        ("sample.dt / t_w (CK aging)", rms_aging),
    ]:
        print(f"axis = {label}:")
        print(f"  C  RMS: current={rms[0]:.4f}  kww={rms[1]:.4f}")
        print(f"  chi RMS: current={rms[2]:.4f}  kww={rms[3]:.4f}")


if __name__ == "__main__":
    main()
