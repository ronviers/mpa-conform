"""Three-way comparison: empirical vs predicted vs Banach (protocol-matched).

For a single declaration_bundle, produce a two-panel C(tau) + chi(tau)
PNG, all three traces evaluated in *dimensionless tau frame* so the
framework's analytical model gfdr_model.generate_locus (native range
[0.01, 1000]) has its full dynamic range available.

  - Empirical: substrate measurement (markers + SEM bars) read from
    bundle.observable.data, x-axis rescaled to tau_dim = tau / tau_scale.
  - Predicted: framework's analytical model at the fitted (chit, gamma_AB),
    evaluated at the same dimensionless tau values. Recomputed here
    rather than read from bundle.fit_provenance.predicted_locus because
    the stored predicted is in native frame and saturates against the
    model's tau_max=1000 boundary. Same chit, same model, frame chosen
    for visibility.
  - Banach (protocol-matched): canonical state fixed by the bundle's
    tau_obs (single observation window) -- chit_nu = chit_0 * exp(-nu)
    where nu = tau_obs / tau_scale. Then C(tau), chi(tau) read from
    gfdr_model.generate_locus at that fixed canonical state across the
    dimensionless lag tau_dim. Mirrors the substrate's actual
    measurement protocol: one window, one canonical state, observable
    trajectory swept within the window. Does not refit; uses only the
    bundle's declared tau_obs and fitted (chit, gamma_AB).

The "RG-flow sweep" interpretation (treat the empirical lag axis itself
as RG-flow depth, so canonical state evolves across the sweep) was an
earlier reading of this module. It produced smooth Banach traces that
did not match empirical's measurement cadence because it mixed
substrate-side lag with canonical-side depth on the same axis. The
protocol-matched reading here keeps the axis interpretation consistent
across all three traces.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from mpa_scale_solver.banach import BanachSubstrate

from conformer.compute import gfdr_model


@dataclass(frozen=True)
class Trace:
    label: str
    tau: list[float]
    C: list[float]
    chi: list[float]
    C_sem: Optional[list[float]] = None
    chi_sem: Optional[list[float]] = None


@dataclass(frozen=True)
class ComparisonData:
    bundle_id: str
    substrate_class: str
    xdot_choice: str
    fitted_chit: float
    fitted_gamma_AB: float
    tau_scale: float
    tau_obs_native: float
    banach_nu_obs: float
    banach_chit_nu: float
    ground_truth_regime: Optional[str]
    empirical: Trace
    predicted: Trace
    banach: Trace


def _resolve_tau_scale(bundle: dict) -> float:
    """Recover the tau_scale used during inversion fit. Stored in the
    bundle's preprocessing_log under operation=tau_rescale_for_fit;
    fall back to median empirical tau if absent."""
    obs = bundle.get("observable") or {}
    for entry in obs.get("preprocessing_log") or []:
        if entry.get("operation") == "tau_rescale_for_fit":
            ts = (entry.get("parameters") or {}).get("tau_scale")
            if isinstance(ts, (int, float)) and ts > 0:
                return float(ts)
    rows = obs.get("data") or []
    taus = [float(r["tau"]) for r in rows if "tau" in r]
    return float(np.median(taus)) if taus else 1.0


def load_comparison(bundle_path: Path) -> ComparisonData:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_id = bundle.get("bundle_id") or bundle_path.stem
    substrate_class = bundle.get("substrate_class", "unknown")
    xdot_choice = bundle.get("xdot_choice", "unknown")

    fit_prov = bundle.get("fit_provenance") or {}
    fitted = fit_prov.get("fitted_params") or {}
    chit_0 = float(fitted.get("chit", 0.0))
    gamma_0 = float(fitted.get("gamma_AB", 0.0))

    obs = bundle.get("observable") or {}
    rows = obs.get("data") or []
    if len(rows) < 2:
        raise ValueError(
            f"bundle has < 2 observable rows; nothing to plot: {bundle_path.name}"
        )

    tau_scale = _resolve_tau_scale(bundle)

    emp_tau_native = [float(r["tau"]) for r in rows]
    emp_tau_dim = [t / tau_scale for t in emp_tau_native]
    emp_C = [float(r["C"]) for r in rows]
    emp_chi = [float(r["chi"]) for r in rows]
    emp_C_sem = [float(r.get("C_sem") or 0.0) for r in rows]
    emp_chi_sem = [float(r.get("chi_sem") or 0.0) for r in rows]
    empirical = Trace(
        label="empirical",
        tau=emp_tau_dim, C=emp_C, chi=emp_chi,
        C_sem=emp_C_sem, chi_sem=emp_chi_sem,
    )

    # Predicted in dimensionless frame: framework's analytical model at
    # the fitted chit_0, evaluated at the same dimensionless lag values
    # the empirical sits at. This is recomputed (not read from
    # bundle.fit_provenance.predicted_locus) because the stored locus is
    # in native tau frame and saturates against the model's hardcoded
    # tau_max = 1000.
    pred_model = gfdr_model.generate_locus(chit_0)
    pred_C, pred_chi = [], []
    for td in emp_tau_dim:
        c, ch = gfdr_model._interp_log_tau(pred_model, td)
        pred_C.append(c)
        pred_chi.append(ch)
    predicted = Trace(
        label="predicted", tau=list(emp_tau_dim), C=pred_C, chi=pred_chi,
    )

    # Banach protocol-matched: one canonical state per measurement
    # window, observable swept across lag. Use the bundle's declared
    # tau_obs (representative value across the grinder's 31 windows) to
    # fix Banach's depth; canonical state is exp(-lambda * nu) at that
    # depth; observable is gfdr_model at that fixed state.
    tau_obs_val = (bundle.get("tau_obs") or {}).get("value")
    if tau_obs_val is None:
        tau_obs_val = float(np.median(emp_tau_native))
    nu_obs = float(tau_obs_val) / tau_scale
    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_0)
    banach_state = banach.state_at(nu_obs)
    banach_model = gfdr_model.generate_locus(banach_state.chit)
    banach_C, banach_chi = [], []
    for td in emp_tau_dim:
        c, ch = gfdr_model._interp_log_tau(banach_model, td)
        banach_C.append(c)
        banach_chi.append(ch)
    banach_trace = Trace(
        label="banach", tau=list(emp_tau_dim), C=banach_C, chi=banach_chi,
    )

    gt_regime = ((obs.get("metadata") or {}).get("ground_truth_regime")) or None

    return ComparisonData(
        bundle_id=bundle_id,
        substrate_class=substrate_class,
        xdot_choice=xdot_choice,
        fitted_chit=chit_0,
        fitted_gamma_AB=gamma_0,
        tau_scale=tau_scale,
        tau_obs_native=float(tau_obs_val),
        banach_nu_obs=nu_obs,
        banach_chit_nu=banach_state.chit,
        ground_truth_regime=gt_regime,
        empirical=empirical,
        predicted=predicted,
        banach=banach_trace,
    )


def render_png(data: ComparisonData, out_path: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax_C, ax_chi) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # Panel 1: C(tau)
    ax_C.errorbar(
        data.empirical.tau, data.empirical.C,
        yerr=data.empirical.C_sem,
        fmt="o", color="black", markersize=4, capsize=2,
        label="empirical (substrate)",
    )
    ax_C.plot(
        data.predicted.tau, data.predicted.C,
        color="C0", linewidth=1.6,
        label=f"predicted (chit={data.fitted_chit:.3f})",
    )
    ax_C.plot(
        data.banach.tau, data.banach.C,
        color="C3", linewidth=1.6, linestyle="--",
        label=(
            f"banach (nu_obs={data.banach_nu_obs:.3g}, "
            f"chit_nu={data.banach_chit_nu:.3f})"
        ),
    )
    ax_C.set_xscale("log")
    ax_C.set_ylabel("C(tau)")
    ax_C.legend(loc="best", fontsize=8, frameon=False)
    ax_C.grid(True, alpha=0.25)

    # Panel 2: chi(tau)
    ax_chi.errorbar(
        data.empirical.tau, data.empirical.chi,
        yerr=data.empirical.chi_sem,
        fmt="o", color="black", markersize=4, capsize=2,
        label="empirical (substrate)",
    )
    ax_chi.plot(
        data.predicted.tau, data.predicted.chi,
        color="C0", linewidth=1.6,
        label="predicted",
    )
    ax_chi.plot(
        data.banach.tau, data.banach.chi,
        color="C3", linewidth=1.6, linestyle="--",
        label="banach",
    )
    ax_chi.set_xscale("log")
    ax_chi.set_xlabel(
        f"tau (dimensionless = native / tau_scale; tau_scale={data.tau_scale:.1f}, "
        f"tau_obs_native={data.tau_obs_native:.3g})"
    )
    ax_chi.set_ylabel("chi(tau)")
    ax_chi.legend(loc="best", fontsize=8, frameon=False)
    ax_chi.grid(True, alpha=0.25)

    gt = f", gt_regime={data.ground_truth_regime}" if data.ground_truth_regime else ""
    title = (
        f"{data.bundle_id}\n"
        f"{data.substrate_class} / {data.xdot_choice}  ·  "
        f"fit: chit={data.fitted_chit:.3f}, gamma_AB={data.fitted_gamma_AB:.3f}{gt}"
    )
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path
