"""Cross-substrate KWW transfer test: brain (neural-population substrate).

Parallel to test_kww_glass.py and test_kww_qec.py. Same diagnostic shape,
same 3-axis sweep, loading a brain cell instead.

Cell choice: brain__suspended__velocity. Why:
  - scenario=suspended is gt=s (intermediate regime, direct analog of
    glass T=0.5 which is also gt=s)
  - xdot=velocity is the per-step (instantaneous derivative) ẋ choice,
    analog of glass's spin-flip per-step ẋ
  - Empirical shape: C decays 0.085 -> 0.024 across dt=1..9000;
    chi grows 0.006 -> 0.207. Same qualitative shape as glass aging
    (decay + growth), different absolute scales.

Honest expectation: brain has roughly the right shape for the glass
apparatus, but parameters will be re-tuned to match brain's smaller
C magnitudes and different chi scale. RULES §15: the substrate-
thermodynamic content per substrate; the leading-order chit + KWW
form may transfer; the specific (q_EA, tau_alpha, beta_KWW, tau_beta,
X) values will be brain-specific.

The cross-substrate test is whether the 6-vector form can fit brain
with re-tuned values (apparatus transfers) or whether brain needs a
structurally different form (apparatus does not transfer).

Run from H:/mpa-conform:
    python scripts/test_kww_brain.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.compute import gfdr_model


CELL_PATH = Path(
    "H:/mpa-central/library/data/brain/brain__suspended__velocity.json"
)

# Hand-tuned for brain__suspended__velocity:
#   q_EA ~ 0.085 (the plateau value empirical sits at for small dt --
#                 already past the beta-piece by dt=1)
#   tau_alpha ~ 18 (dimensionless; from anchor: C(dt=9000)=0.024 with
#                   beta_KWW=0.5 implies tau_alpha ~ 18 in tau_env units)
#   beta_KWW ~ 0.5 (typical stretching, no reason to deviate from glass)
#   tau_beta ~ 0.003 (small; the beta-piece must be fully decayed by
#                     dt=1/tau_env=0.003, i.e. tau_beta is sub-dimensionless)
#   X ~ ? -- the FDT slope on brain. Empirical chi at small lag is 0.006
#            (not dC=0.915, factor of 150 off from FDT-equilibrium with T=1).
#            X probably very small for brain, OR chi normalized differently.
#            Try X=0.01 to start; this is the value that needs investigation.
#   T ~ 1.0 (brain has no temperature; default 1.0 for the FDT slope)
Q_EA = 0.085
TAU_ALPHA = 18.0
BETA_KWW = 0.5
TAU_BETA = 0.003
X_FDT = 0.01
T_DEFAULT = 1.0


def kww_glass_locus(
    q_EA: float, tau_alpha: float, beta_KWW: float, tau_beta: float,
    *, X: float = 1.0, T: float = 1.0,
    n_points: int = 1000, tau_min: float = 1e-4, tau_max: float = 1e3,
) -> dict:
    """Same KWW + FDT-violation form as the other diagnostics. Inline
    so the test object is visibly the same across substrate tests."""
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

    sample_t = np.array([float(s["t"]) for s in samples])
    sample_dt = np.array([float(s["dt"]) for s in samples])
    t_w = float((cell.get("schedule") or {}).get("t_w", 0.0))

    # Brain has tau_env_analytic.value = 300 (scenario_table). Use directly.
    tau_env = (cell.get("tau_env_analytic") or {}).get("value")
    if isinstance(tau_env, (int, float)) and tau_env > 0 and tau_env == tau_env:
        tau_scale = float(tau_env)
    else:
        tau_scale = float(np.median(sample_t))

    C = np.array([float(s["C_mean"]) for s in samples])
    chi = np.array([float(s["chi_mean"]) for s in samples])
    C_sem = np.array([float(s.get("C_sem") or 0.0) for s in samples])
    chi_sem = np.array([float(s.get("chi_sem") or 0.0) for s in samples])

    return {
        "tau_dim_t": sample_t / tau_scale,
        "tau_dim_dt": sample_dt / tau_scale,
        "tau_dim_tw_aging": sample_dt / t_w,
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


def _read_lens_chit() -> float:
    bundle_path = (
        REPO_ROOT / "output" / "seed-corpus" / "neural-population"
        / "brain__suspended__velocity.bundle.json"
    )
    if not bundle_path.is_file():
        return 0.0
    b = json.loads(bundle_path.read_text(encoding="utf-8"))
    return float((b.get("fit_provenance") or {}).get("fitted_params", {}).get("chit", 0.0))


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    emp = load_empirical(CELL_PATH)
    op = emp["operating_point"]
    lens_chit = _read_lens_chit()

    kww_model = kww_glass_locus(
        Q_EA, TAU_ALPHA, BETA_KWW, TAU_BETA,
        X=X_FDT, T=T_DEFAULT,
    )
    current_model = gfdr_model.generate_locus(lens_chit)

    cur_C_t, cur_chi_t = interp_log_tau(current_model, emp["tau_dim_t"])
    kww_C_t, kww_chi_t = interp_log_tau(kww_model, emp["tau_dim_dt"])
    cur_C_dt, cur_chi_dt = interp_log_tau(current_model, emp["tau_dim_dt"])
    kww_C_dt, kww_chi_dt = interp_log_tau(kww_model, emp["tau_dim_dt"])
    cur_C_aging, cur_chi_aging = interp_log_tau(current_model, emp["tau_dim_tw_aging"])
    kww_C_aging, kww_chi_aging = interp_log_tau(kww_model, emp["tau_dim_dt"])

    fig, axes = plt.subplots(2, 3, figsize=(18, 8))
    (ax_C_t, ax_C_dt, ax_C_aging), (ax_chi_t, ax_chi_dt, ax_chi_aging) = axes

    def _draw(ax_C, ax_chi, tau_dim, kww_C, kww_chi, cur_C, cur_chi, axis_label):
        rms_kww_C = float(np.sqrt(np.mean((emp["C"] - kww_C) ** 2)))
        rms_kww_chi = float(np.sqrt(np.mean((emp["chi"] - kww_chi) ** 2)))
        rms_cur_C = float(np.sqrt(np.mean((emp["C"] - cur_C) ** 2)))
        rms_cur_chi = float(np.sqrt(np.mean((emp["chi"] - cur_chi) ** 2)))

        ax_C.errorbar(tau_dim, emp["C"], yerr=emp["C_sem"], fmt="o",
                      color="black", markersize=4, capsize=2, zorder=3,
                      label="empirical")
        ax_C.plot(tau_dim, cur_C, color="C0", linewidth=1.6, zorder=2,
                  label=f"current 1-param chit={lens_chit:.2f} (RMS={rms_cur_C:.3f})")
        ax_C.plot(tau_dim, kww_C, color="C2", linewidth=1.8, zorder=2,
                  label=f"brain-KWW (RMS={rms_kww_C:.3f})")
        ax_C.set_xscale("log")
        ax_C.set_ylabel("C(tau)")
        ax_C.set_title(f"x-axis: {axis_label}", fontsize=10)
        ax_C.legend(loc="best", fontsize=8, frameon=False)
        ax_C.grid(True, alpha=0.25)

        ax_chi.errorbar(tau_dim, emp["chi"], yerr=emp["chi_sem"], fmt="o",
                        color="black", markersize=4, capsize=2, zorder=3,
                        label="empirical")
        ax_chi.plot(tau_dim, cur_chi, color="C0", linewidth=1.6, zorder=2,
                    label=f"current 1-param (RMS={rms_cur_chi:.3f})")
        ax_chi.plot(tau_dim, kww_chi, color="C2", linewidth=1.8, zorder=2,
                    label=f"brain-KWW (RMS={rms_kww_chi:.3f})")
        ax_chi.set_xscale("log")
        ax_chi.set_xlabel(f"tau ({axis_label})")
        ax_chi.set_ylabel("chi(tau)")
        ax_chi.legend(loc="best", fontsize=8, frameon=False)
        ax_chi.grid(True, alpha=0.25)
        return rms_kww_C, rms_kww_chi, rms_cur_C, rms_cur_chi

    rms_t = _draw(ax_C_t, ax_chi_t, emp["tau_dim_t"], kww_C_t, kww_chi_t,
                  cur_C_t, cur_chi_t, "sample.t / tau_scale")
    rms_dt = _draw(ax_C_dt, ax_chi_dt, emp["tau_dim_dt"], kww_C_dt, kww_chi_dt,
                   cur_C_dt, cur_chi_dt, "sample.dt / tau_scale (framework lag)")
    rms_aging = _draw(ax_C_aging, ax_chi_aging, emp["tau_dim_tw_aging"],
                      kww_C_aging, kww_chi_aging, cur_C_aging, cur_chi_aging,
                      "sample.dt / t_w (CK aging-anchored)")

    title = (
        f"Cross-substrate KWW transfer test  ·  neural-population "
        f"{op.get('label', 'suspended')}  ·  gt_regime={op.get('gt', '?')}  ·  "
        f"xdot={emp['xdot_kind']}  ·  t_w={emp['t_w']:.0f}, "
        f"tau_scale=tau_env_scenario={emp['tau_scale']:.1f}\n"
        f"Brain-KWW params (hand-tuned for brain__suspended__velocity): "
        f"q_EA={Q_EA}, tau_alpha={TAU_ALPHA}, beta_KWW={BETA_KWW}, "
        f"tau_beta={TAU_BETA}, X={X_FDT}, T={T_DEFAULT}"
    )
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()

    out_dir = REPO_ROOT / "output" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kww_brain_test__suspended__velocity.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)

    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"empirical C range:   [{emp['C'].min():.4f}, {emp['C'].max():.4f}]")
    print(f"empirical chi range: [{emp['chi'].min():.4f}, {emp['chi'].max():.4f}]")
    print()
    for label, rms in [
        ("sample.t (current bundle)", rms_t),
        ("sample.dt (framework lag)", rms_dt),
        ("sample.dt / t_w (CK aging)", rms_aging),
    ]:
        print(f"axis = {label}:")
        print(f"  C  RMS: current={rms[2]:.4f}  brain-KWW={rms[0]:.4f}")
        print(f"  chi RMS: current={rms[3]:.4f}  brain-KWW={rms[1]:.4f}")


if __name__ == "__main__":
    main()
