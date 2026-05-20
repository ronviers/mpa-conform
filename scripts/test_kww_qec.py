"""Cross-substrate KWW transfer test: does the glass apparatus hold on QEC?

Parallel to test_kww_glass.py. Same diagnostic shape, same 3-axis sweep,
but loading a surface-code-qec cell instead of glass. Tests whether the
KWW + FDT-violation 6-vector that closed glass at T=0.5 (C RMS 0.025,
chi RMS 0.073) transfers to QEC at p=1e-3.

The honest expectation: it falls apart. RULES §7 already records the
hierarchy-direction inversion (glass walks c -> s -> r as tau widens;
syndrome substrates walk r -> s -> c, opposite direction). The QEC
community's substrate-thermodynamic content lives in different
observables (logical error rate, threshold structure, syndrome
statistics) -- not in q_EA / tau_alpha / beta_KWW / tau_beta / X.

But render-look-decide: the visual is the receipt. If it falls apart
we know QEC needs its own apparatus (which validates the per-substrate
discipline). If it surprisingly holds, we have something more universal
than expected.

Run from H:/mpa-conform:
    python scripts/test_kww_qec.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.compute import gfdr_model


# Mid-range QEC cell: p_base ~ 1e-3, regime "s" (intermediate, not trivially
# decorrelated, not deep r). detection-event xdot.
CELL_PATH = Path(
    "H:/mpa-central/library/data/quantum/quantum__p1e-03__detection-event.json"
)

# Glass-apparatus parameters reused verbatim (the same 6-vector that
# closed glass at T=0.5). The whole point of this test is to see what
# happens when these are pointed at QEC data unchanged.
Q_EA = 0.94
TAU_ALPHA = 137.0
BETA_KWW = 0.5
TAU_BETA = 0.3
X_FDT = 0.4

# QEC cells don't carry T (they have p_base instead). Use T=1.0 as
# dimensionless default for the FDT line slope -- this is one of the
# substrate-conditional bits that the glass apparatus doesn't account
# for. The QEC community would normalize chi differently.
T_DEFAULT = 1.0

# Bundle's fitted chit for this QEC cell (loaded below for the
# 1-param current-model overlay).


def kww_glass_locus(
    q_EA: float, tau_alpha: float, beta_KWW: float, tau_beta: float,
    *, X: float = 1.0, T: float = 1.0,
    n_points: int = 1000, tau_min: float = 1e-4, tau_max: float = 1e3,
) -> dict:
    """Same KWW + FDT-violation form as test_kww_glass.py. Imported
    inline so this script is self-contained and the glass apparatus
    is visibly the same object being tested."""
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

    # QEC's tau_env_analytic.value is finite (= 1/p_base, leading-order
    # analytic). Use it directly; fall back to median if absent.
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


def _read_lens_chit(emp_op_label: str) -> float | None:
    """Look up the lens-solver fit for this cell from the v0.4 bundle's
    cross_path_disagreement (when available). Returns None if no bundle
    found -- the diagnostic falls back to a hardcoded mid-range chit."""
    bundle_path = (
        REPO_ROOT / "output" / "seed-corpus" / "surface-code-qec"
        / "quantum__p1e-03__detection-event.bundle.json"
    )
    if not bundle_path.is_file():
        return None
    b = json.loads(bundle_path.read_text(encoding="utf-8"))
    fp = b.get("fit_provenance") or {}
    fitted = fp.get("fitted_params") or {}
    return float(fitted.get("chit", 0.0))


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    emp = load_empirical(CELL_PATH)
    op = emp["operating_point"]
    lens_chit = _read_lens_chit(op.get("label", "")) or 0.0

    # The glass apparatus evaluated at the empirical's lag values, but
    # using glass's hand-picked params (Q_EA=0.94 etc.). This is the
    # cross-substrate test object: how badly does glass-form miss QEC?
    kww_glass_model = kww_glass_locus(
        Q_EA, TAU_ALPHA, BETA_KWW, TAU_BETA,
        X=X_FDT, T=T_DEFAULT,
    )

    current_model = gfdr_model.generate_locus(lens_chit)

    cur_C_t, cur_chi_t = interp_log_tau(current_model, emp["tau_dim_t"])
    kww_C_t, kww_chi_t = interp_log_tau(kww_glass_model, emp["tau_dim_dt"])
    cur_C_dt, cur_chi_dt = interp_log_tau(current_model, emp["tau_dim_dt"])
    kww_C_dt, kww_chi_dt = interp_log_tau(kww_glass_model, emp["tau_dim_dt"])
    cur_C_aging, cur_chi_aging = interp_log_tau(current_model, emp["tau_dim_tw_aging"])
    kww_C_aging, kww_chi_aging = interp_log_tau(kww_glass_model, emp["tau_dim_dt"])

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
                  label=f"glass-KWW (RMS={rms_kww_C:.3f})")
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
                    label=f"glass-KWW (RMS={rms_kww_chi:.3f})")
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
        f"Cross-substrate KWW transfer test  ·  surface-code-qec "
        f"{op.get('label', '?')}  ·  gt_regime={op.get('gt', '?')}  ·  "
        f"xdot={emp['xdot_kind']}  ·  t_w={emp['t_w']:.0f}, "
        f"tau_scale=1/p_base={emp['tau_scale']:.1f}\n"
        f"Glass-KWW params (verbatim from glass T=0.5 test): "
        f"q_EA={Q_EA}, tau_alpha={TAU_ALPHA}, beta_KWW={BETA_KWW}, "
        f"tau_beta={TAU_BETA}, X={X_FDT}, T={T_DEFAULT} (no T in QEC; default 1.0)"
    )
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()

    out_dir = REPO_ROOT / "output" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kww_qec_test__p1e-03__detection-event.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)

    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"empirical C range:   [{emp['C'].min():.5f}, {emp['C'].max():.5f}]")
    print(f"empirical chi range: [{emp['chi'].min():.2f}, {emp['chi'].max():.2f}]")
    print()
    for label, rms in [
        ("sample.t (current bundle)", rms_t),
        ("sample.dt (framework lag)", rms_dt),
        ("sample.dt / t_w (CK aging)", rms_aging),
    ]:
        print(f"axis = {label}:")
        print(f"  C  RMS: current={rms[2]:.4f}  glass-KWW={rms[0]:.4f}")
        print(f"  chi RMS: current={rms[3]:.4f}  glass-KWW={rms[1]:.4f}")


if __name__ == "__main__":
    main()
