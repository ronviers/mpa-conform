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
    model's hardcoded tau_max = 1000.
  - Banach (protocol-matched): canonical state fixed by the bundle's
    tau_obs (single observation window) -- chit_nu = chit_0 * exp(-nu)
    where nu = tau_obs / tau_scale. Then C(tau), chi(tau) read from
    gfdr_model.generate_locus at that fixed canonical state across the
    dimensionless lag tau_dim. Mirrors the substrate's actual
    measurement protocol: one window, one canonical state, observable
    trajectory swept within the window. Does not refit; uses only the
    bundle's declared tau_obs and fitted (chit, gamma_AB).
  - Per-window parallax (faint gray): the 31 per-kernel-width
    trail-vector views read from the source grind cell's per_window
    arrays (C_d_mean, chi_d_mean across the schedule's 31 tau_windows).
    Each window-index trace runs across the cell's sample times in the
    same dimensionless frame as the aggregated empirical markers. Lives
    in trail-vector denom space (RULES §5) while the aggregated markers
    live in raw-readout denom space -- the vertical spread between the
    two is the parallax the framework's channel aggregation strips.

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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from mpa_scale_solver.banach import BanachSubstrate

from conformer.compute import gfdr_model


LIBRARY_ROOT = Path("H:/mpa-central/library/data")

# Bundle substrate_class -> grind-cell folder name under library/data/.
_CLASS_TO_FOLDER = {
    "ck-glassy": "glass",
    "surface-code-qec": "quantum",
    "neural-population": "brain",
}


@dataclass(frozen=True)
class Trace:
    label: str
    tau: list[float]
    C: list[float]
    chi: list[float]
    C_sem: Optional[list[float]] = None
    chi_sem: Optional[list[float]] = None


@dataclass(frozen=True)
class WindowTrace:
    """One per-kernel-width trail-vector trace across sample times.

    tau is in the same dimensionless frame as the aggregated empirical
    markers (sample-time / tau_scale). C and chi are C_d_mean / chi_d_mean
    -- trail-vector observables, different coordinate space from the
    aggregated empirical's raw-readout C, chi (RULES §5).
    """
    tau_window: float
    tau: list[float]
    C: list[float]
    chi: list[float]


@dataclass(frozen=True)
class PathView:
    """Predicted + Banach pair at one fitted chit (one inversion path).

    Each curator-time path through the data (two-stage analytical+ensemble
    refine; lens-solver predictor-corrector with cdv1 prior) produces its
    own chit, which propagates into both the framework's analytical model
    (predicted) and the BanachSubstrate canonical-state propagation
    (banach). Holding them together lets the renderer draw the trio
    side-by-side per path.
    """
    label: str
    chit: float
    gamma_AB: float
    banach_chit_nu: float
    predicted: Trace
    banach: Trace


@dataclass(frozen=True)
class ComparisonData:
    bundle_id: str
    substrate_class: str
    xdot_choice: str
    tau_scale: float
    tau_obs_native: float
    banach_nu_obs: float
    ground_truth_regime: Optional[str]
    empirical: Trace
    two_stage: PathView
    lens_solver: Optional[PathView]
    cross_path_disagreement: Optional[float]
    chi_convention: str = "fdr_dimensionless"
    chi_convention_note: str = ""
    per_window: list[WindowTrace] = field(default_factory=list)


# Cache lens-solver batch results: one fit_translation_field call covers a
# whole (substrate_folder, xdot_kind) batch; compare-all hits this 22x for
# the same batch on ck-glassy.
_LENS_CHIT_CACHE: dict[tuple[str, str], dict[str, float]] = {}


def _lens_solver_chits_for_class(
    substrate_folder: str,
    xdot_kind: str,
    *,
    max_passes: int = 10,
    rng_seed: int = 0,
) -> dict[str, float]:
    """Run lens_solver_prior (predictor active, bootstrap=False) on every
    cell in H:/mpa-central/library/data/<folder>/ that matches xdot_kind.
    Returns {operating_point.label: chit}. Cached per (folder, xdot_kind).
    """
    key = (substrate_folder, xdot_kind)
    if key in _LENS_CHIT_CACHE:
        return _LENS_CHIT_CACHE[key]

    from mpa_lens_solver import fit_translation_field

    folder_path = LIBRARY_ROOT / substrate_folder
    if not folder_path.is_dir():
        _LENS_CHIT_CACHE[key] = {}
        return {}

    cells: list[dict] = []
    for p in sorted(folder_path.glob("*.json")):
        try:
            cell = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (cell.get("xdot_kind") or "") == xdot_kind:
            cells.append(cell)

    if not cells:
        _LENS_CHIT_CACHE[key] = {}
        return {}

    field_obj = fit_translation_field(
        substrate_folder, cells, xdot_kind,
        max_passes=max_passes, rng_seed=rng_seed, bootstrap=False,
    )
    chits = {
        rule.operating_point.label: float(rule.canonical.chit)
        for rule in field_obj.rule
    }
    _LENS_CHIT_CACHE[key] = chits
    return chits


def _build_path_view(
    label: str,
    chit_0: float,
    gamma_0: float,
    emp_lag_dim: list[float],
    emp_display_dim: list[float],
    nu_obs: float,
    *,
    kww_params: Optional[dict] = None,
) -> PathView:
    """Compute predicted + Banach traces from one path's fitted state.

    Model evaluation is ALWAYS at lag (emp_lag_dim) -- the substrate's
    natural time variable per RULES §10 and the v0.4 schema's lag/display
    split. The plot's x-axis uses display_dim (Trace.tau field).

    Predicted: framework's analytical model at the fitted state, evaluated
    at the empirical's dimensionless lag values.
      - If kww_params is provided (v0.4 6-vector), uses
        generate_kww_glass_locus(chit, q_EA, tau_alpha, beta_KWW, tau_beta, X, T).
      - Otherwise falls back to generate_locus(chit) (v0.3 1-param).

    Banach: protocol-matched -- single canonical state per measurement
    window at nu_obs, observable swept across the same lag grid. Banach's
    canonical-state propagation through nu currently flows chit only;
    when the scale-solver lands the vector-state extension (follow-on),
    Banach will flow the full 6-vector.
    """
    def _model_at(chit_state: float) -> dict:
        if kww_params is None:
            return gfdr_model.generate_locus(chit_state)
        return gfdr_model.generate_kww_glass_locus(chit_state, **kww_params)

    pred_model = _model_at(chit_0)
    pred_C, pred_chi = [], []
    for ld in emp_lag_dim:
        c, ch = gfdr_model._interp_log_tau(pred_model, ld)
        pred_C.append(c)
        pred_chi.append(ch)
    predicted = Trace(label=f"predicted ({label})", tau=list(emp_display_dim),
                      C=pred_C, chi=pred_chi)

    banach = BanachSubstrate(chit_0=chit_0, gamma_AB_0=gamma_0)
    banach_state = banach.state_at(nu_obs)
    banach_model = _model_at(banach_state.chit)
    b_C, b_chi = [], []
    for ld in emp_lag_dim:
        c, ch = gfdr_model._interp_log_tau(banach_model, ld)
        b_C.append(c)
        b_chi.append(ch)
    banach_trace = Trace(label=f"banach ({label})", tau=list(emp_display_dim),
                         C=b_C, chi=b_chi)

    return PathView(
        label=label,
        chit=chit_0,
        gamma_AB=gamma_0,
        banach_chit_nu=float(banach_state.chit),
        predicted=predicted,
        banach=banach_trace,
    )


def _resolve_cell_path(bundle: dict, bundle_path: Path) -> Optional[Path]:
    """Locate the source grind cell for this bundle. Bundle filenames
    are <cell-stem>.bundle.json; library cells live at
    H:/mpa-central/library/data/<folder>/<cell-stem>.json where folder
    is the substrate-class -> folder mapping. Returns None if the cell
    can't be located (the parallax overlay is best-effort -- a missing
    cell drops the overlay without breaking the three-way plot)."""
    folder = _CLASS_TO_FOLDER.get(bundle.get("substrate_class", ""))
    if folder is None:
        return None
    if not bundle_path.name.endswith(".bundle.json"):
        return None
    cell_stem = bundle_path.name[: -len(".bundle.json")]
    cell_path = LIBRARY_ROOT / folder / f"{cell_stem}.json"
    return cell_path if cell_path.is_file() else None


def _load_per_window_traces(
    cell_path: Path, tau_scale: float, *, display_axis: str = "t",
) -> list[WindowTrace]:
    """Read the 31 per-kernel-width trail-vector traces from the grind
    cell's results.all_samples[].per_window arrays. One WindowTrace per
    schedule.tau_windows entry.

    display_axis selects which time field drives the plotted x-axis:
      - "t"  (default for substrates whose community plots vs sample-time,
              e.g. glass-CK convention)
      - "dt" (the framework-canonical lag)
    The underlying observables are unchanged; only the visual x-axis
    placement differs."""
    cell = json.loads(cell_path.read_text(encoding="utf-8"))
    schedule = cell.get("schedule") or {}
    tau_windows = [float(tw) for tw in (schedule.get("tau_windows") or [])]
    samples = (cell.get("results") or {}).get("all_samples") or []
    if not tau_windows or not samples:
        return []

    n_windows = len(tau_windows)
    tau_per_window: list[list[float]] = [[] for _ in range(n_windows)]
    C_per_window: list[list[float]] = [[] for _ in range(n_windows)]
    chi_per_window: list[list[float]] = [[] for _ in range(n_windows)]
    for s in samples:
        x_axis_value = s.get(display_axis)
        if x_axis_value is None:
            continue
        pw = s.get("per_window") or []
        if len(pw) != n_windows:
            continue
        x_dim = float(x_axis_value) / tau_scale
        for i, entry in enumerate(pw):
            C_d = entry.get("C_d_mean")
            chi_d = entry.get("chi_d_mean")
            if C_d is None or chi_d is None:
                continue
            tau_per_window[i].append(x_dim)
            C_per_window[i].append(float(C_d))
            chi_per_window[i].append(float(chi_d))

    return [
        WindowTrace(
            tau_window=tau_windows[i],
            tau=tau_per_window[i],
            C=C_per_window[i],
            chi=chi_per_window[i],
        )
        for i in range(n_windows)
        if tau_per_window[i]
    ]


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


def _glass_kww_prior_from_T(T: float) -> dict:
    """Substrate-default KWW + FDT-violation prior for glass at operating
    point temperature T (cdv1 leading-order per RULES §15).

    Used by banach_overlay as a v0.4 fallback when the bundle's
    fitted_params doesn't yet carry the 6-vector (i.e., the 6-param
    inversion hasn't landed for this bundle). Provides a substrate-
    default visualization that the future inversion will refine.

    Values are typical spin-glass-literature defaults plus a simple
    T-dependent q_EA / tau_alpha / X:
      q_EA(T) = clip(1 - T, [0.05, 0.99])   (deeper below Tc -> higher plateau)
      tau_alpha(T): grows rapidly as T -> 0 (frozen aging). For T in [0.2, 1.5]:
                    tau_alpha ~ 1 / T^2 in lag-dimensionless units.
      beta_KWW: 0.5 (typical)
      tau_beta: 0.001 (fast cage rattling)
      X(T): 1 above Tc=1.0; ramps down to ~0.1 deep below.

    Tc=1.0 is the 3D EA glass transition used by the substrate library;
    refinements come from the 6-param inversion in a follow-on session.
    """
    T = float(T)
    Tc = 1.0
    q_EA = max(0.05, min(0.99, 1.0 - T))
    tau_alpha = max(1.0, 50.0 / max(T, 0.05) ** 2)
    beta_KWW = 0.5
    tau_beta = 0.001
    if T >= Tc:
        X = 1.0
    else:
        X = max(0.05, min(1.0, T / Tc))
    return {
        "q_EA": q_EA,
        "tau_alpha": tau_alpha,
        "beta_KWW": beta_KWW,
        "tau_beta": tau_beta,
        "X": X,
        "T": T,
    }


def _kww_params_from_bundle(bundle: dict, fitted: dict) -> Optional[dict]:
    """If the v0.4 bundle carries the substrate-thermodynamic 6-vector
    (q_EA, tau_alpha, beta_KWW, tau_beta, X) plus T, return the kwargs
    dict for generate_kww_glass_locus. Otherwise None (caller falls back
    to the 1-parameter generate_locus).

    T can ride in fitted_params or in observable.metadata.operating_point_T.
    For v0.4 bundles produced before a 6-param inversion ships, the
    5 KWW params will not be present and this returns None -- the
    bundle is still readable, just with the v0.3-style 1-param model.
    """
    required = ("q_EA", "tau_alpha", "beta_KWW", "tau_beta", "X")
    if any(fitted.get(k) is None for k in required):
        return None
    T = fitted.get("T")
    if T is None:
        meta = (bundle.get("observable") or {}).get("metadata") or {}
        T = meta.get("operating_point_T")
    if T is None:
        return None
    return {
        "q_EA": float(fitted["q_EA"]),
        "tau_alpha": float(fitted["tau_alpha"]),
        "beta_KWW": float(fitted["beta_KWW"]),
        "tau_beta": float(fitted["tau_beta"]),
        "X": float(fitted["X"]),
        "T": float(T),
    }


def load_comparison(bundle_path: Path) -> ComparisonData:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_id = bundle.get("bundle_id") or bundle_path.stem
    substrate_class = bundle.get("substrate_class", "unknown")
    xdot_choice = bundle.get("xdot_choice", "unknown")
    schema_version = bundle.get("schema", "declaration-bundle.v0.3")

    fit_prov = bundle.get("fit_provenance") or {}
    fitted = fit_prov.get("fitted_params") or {}
    chit_two_stage = float(fitted.get("chit", 0.0))
    gamma_two_stage = float(fitted.get("gamma_AB", 0.0))

    # v0.4 substrate-thermodynamic 6-vector (q_EA, tau_alpha, beta_KWW,
    # tau_beta, X). When all five (+ T) are present in fitted_params or
    # observable.metadata, use the extended forward model. Otherwise
    # fall back to the substrate's cdv1 leading-order prior when the
    # substrate has one declared (currently: ck-glassy via
    # _glass_kww_prior_from_T). The substrate-default prior produces an
    # immediately useful visualization that future 6-param inversion
    # refinements supersede.
    kww_params = _kww_params_from_bundle(bundle, fitted)
    if kww_params is None and substrate_class == "ck-glassy":
        meta = (bundle.get("observable") or {}).get("metadata") or {}
        T = meta.get("operating_point_T")
        if T is not None:
            kww_params = _glass_kww_prior_from_T(float(T))

    obs = bundle.get("observable") or {}
    rows = obs.get("data") or []
    if len(rows) < 2:
        raise ValueError(
            f"bundle has < 2 observable rows; nothing to plot: {bundle_path.name}"
        )

    tau_scale = _resolve_tau_scale(bundle)

    # v0.4: tau IS lag (the framework canonical model time). display_tau
    # is the substrate-community plot variable (optional; fall back to
    # tau for v0.3- bundles that only carried one).
    emp_lag_native = [float(r["tau"]) for r in rows]
    emp_display_native = [float(r.get("display_tau", r["tau"])) for r in rows]
    emp_lag_dim = [t / tau_scale for t in emp_lag_native]
    emp_display_dim = [t / tau_scale for t in emp_display_native]
    emp_C = [float(r["C"]) for r in rows]
    emp_chi = [float(r["chi"]) for r in rows]
    emp_C_sem = [float(r.get("C_sem") or 0.0) for r in rows]
    emp_chi_sem = [float(r.get("chi_sem") or 0.0) for r in rows]
    empirical = Trace(
        label="empirical",
        tau=emp_display_dim, C=emp_C, chi=emp_chi,
        C_sem=emp_C_sem, chi_sem=emp_chi_sem,
    )

    tau_obs_val = (bundle.get("tau_obs") or {}).get("value")
    if tau_obs_val is None:
        tau_obs_val = float(np.median(emp_lag_native))
    nu_obs = float(tau_obs_val) / tau_scale

    two_stage_view = _build_path_view(
        "two_stage_inversion", chit_two_stage, gamma_two_stage,
        emp_lag_dim, emp_display_dim, nu_obs,
        kww_params=kww_params,
    )

    # Lens-solver prior: re-run fit_translation_field on the substrate
    # batch so the predictor has trajectory history (per cross_path.py's
    # rationale -- single-cell calls would null the predictor signal).
    # Cached per (substrate_folder, xdot_kind).
    lens_view: Optional[PathView] = None
    cross_path_disag: Optional[float] = None
    folder = _CLASS_TO_FOLDER.get(substrate_class)
    if folder:
        try:
            lens_chits = _lens_solver_chits_for_class(folder, xdot_choice)
        except Exception:
            lens_chits = {}
        cell_path_for_label = _resolve_cell_path(bundle, bundle_path)
        op_label: Optional[str] = None
        if cell_path_for_label:
            cell_doc = json.loads(cell_path_for_label.read_text(encoding="utf-8"))
            op_label = (cell_doc.get("operating_point") or {}).get("label")
        chit_lens = lens_chits.get(op_label) if op_label else None
        if chit_lens is not None:
            lens_view = _build_path_view(
                "lens_solver_prior", float(chit_lens), gamma_two_stage,
                emp_lag_dim, emp_display_dim, nu_obs,
                kww_params=kww_params,
            )
            cross_path_disag = abs(chit_two_stage - float(chit_lens))

    gt_regime = ((obs.get("metadata") or {}).get("ground_truth_regime")) or None

    meta = (obs.get("metadata") or {})
    chi_conv = meta.get("chi_convention", "fdr_dimensionless")
    chi_conv_note = meta.get("chi_convention_note", "")

    # Per-window parallax uses the same display axis as the aggregated
    # empirical markers (sample.t for glass-CK; the cell's per_window
    # entries are at sample times, not lags, so display_axis="t" is the
    # natural alignment for visual layering).
    cell_path = _resolve_cell_path(bundle, bundle_path)
    per_window = (
        _load_per_window_traces(cell_path, tau_scale, display_axis="t")
        if cell_path else []
    )
    _ = schema_version  # reserved for future schema-conditional behavior

    return ComparisonData(
        bundle_id=bundle_id,
        substrate_class=substrate_class,
        xdot_choice=xdot_choice,
        tau_scale=tau_scale,
        tau_obs_native=float(tau_obs_val),
        banach_nu_obs=nu_obs,
        ground_truth_regime=gt_regime,
        empirical=empirical,
        two_stage=two_stage_view,
        lens_solver=lens_view,
        cross_path_disagreement=cross_path_disag,
        chi_convention=chi_conv,
        chi_convention_note=chi_conv_note,
        per_window=per_window,
    )


def _y_limits_from(*series_lists) -> tuple[float, float]:
    """Compute a y-axis range from several series. Adds a small margin
    so curves at the top/bottom edges don't hug the frame."""
    vals: list[float] = []
    for s in series_lists:
        if s is None:
            continue
        for v in s:
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if fv != fv or fv == float("inf") or fv == float("-inf"):
                continue
            vals.append(fv)
    if not vals:
        return (-0.05, 1.05)
    lo, hi = min(vals), max(vals)
    pad = max(0.02, 0.08 * (hi - lo))
    return (lo - pad, hi + pad)


def _draw_path_column(
    ax_C, ax_chi, data: ComparisonData, view: PathView, *, show_per_window_label: bool,
) -> None:
    """Draw one column (C panel + chi panel) for one inversion path."""
    # Per-window parallax beneath everything (zorder=1). Per-window
    # trail-vector observables can blow up the y-axis on substrates
    # where their natural range differs from the raw (C, chi); we
    # explicitly clamp the y-limits below to the empirical + model
    # curves' range so the load-bearing physics stays visible.
    for i, wt in enumerate(data.per_window):
        kwargs = dict(color="0.55", linewidth=0.7, alpha=0.35, zorder=1)
        if i == 0 and show_per_window_label:
            kwargs["label"] = f"per-window (n={len(data.per_window)}, trail-vector)"
        ax_C.plot(wt.tau, wt.C, **kwargs)
        ax_chi.plot(wt.tau, wt.chi, **kwargs)

    ax_C.errorbar(
        data.empirical.tau, data.empirical.C, yerr=data.empirical.C_sem,
        fmt="o", color="black", markersize=4, capsize=2,
        label="empirical (substrate)", zorder=3,
    )
    ax_C.plot(
        view.predicted.tau, view.predicted.C,
        color="C0", linewidth=1.6, zorder=2,
        label=f"predicted (chit={view.chit:.3f})",
    )
    ax_C.plot(
        view.banach.tau, view.banach.C,
        color="C3", linewidth=1.6, linestyle="--", zorder=2,
        label=(
            f"banach (nu_obs={data.banach_nu_obs:.3g}, "
            f"chit_nu={view.banach_chit_nu:.3f})"
        ),
    )
    ax_C.set_xscale("log")
    ax_C.set_ylabel("C(tau)")
    ax_C.legend(loc="best", fontsize=7.5, frameon=False)
    ax_C.grid(True, alpha=0.25)

    chi_uncalibrated = data.chi_convention != "fdr_dimensionless"
    # When the bundle's chi is not in FDR-canonical form, the model's
    # predicted/banach chi traces are in a different coordinate space
    # than the empirical markers. Render them pale and label them as
    # "canonical prediction (chi uncalibrated for this substrate)" to
    # avoid the visual impression of a fit failure. The empirical chi
    # is plotted as-is; consumers know it is uncalibrated by reading
    # the chi_convention metadata.
    model_alpha = 0.35 if chi_uncalibrated else 1.0
    model_zorder = 1 if chi_uncalibrated else 2
    pred_label = (
        "predicted (canonical; chi uncalibrated for this substrate)"
        if chi_uncalibrated else "predicted"
    )
    banach_label = (
        "banach (canonical; chi uncalibrated for this substrate)"
        if chi_uncalibrated else "banach"
    )

    ax_chi.errorbar(
        data.empirical.tau, data.empirical.chi, yerr=data.empirical.chi_sem,
        fmt="o", color="black", markersize=4, capsize=2,
        label="empirical (substrate; chi uncalibrated)" if chi_uncalibrated
              else "empirical (substrate)",
        zorder=3,
    )
    ax_chi.plot(
        view.predicted.tau, view.predicted.chi,
        color="C0", linewidth=1.6, zorder=model_zorder, alpha=model_alpha,
        label=pred_label,
    )
    ax_chi.plot(
        view.banach.tau, view.banach.chi,
        color="C3", linewidth=1.6, linestyle="--", zorder=model_zorder,
        alpha=model_alpha,
        label=banach_label,
    )
    if chi_uncalibrated:
        ax_chi.text(
            0.02, 0.97,
            f"chi_convention = {data.chi_convention!r}\n"
            f"empirical and model curves live in different coordinate spaces;\n"
            f"normalization owed (see chi_convention_lock_in.md)",
            transform=ax_chi.transAxes, va="top", ha="left", fontsize=7.5,
            color="0.35",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff5d6",
                      edgecolor="0.7", alpha=0.8),
        )
    ax_chi.set_xscale("log")
    ax_chi.set_xlabel(
        f"display tau (dimensionless = display_tau_native / tau_scale; "
        f"tau_scale={data.tau_scale:.1f}, tau_obs_native={data.tau_obs_native:.3g}). "
        f"Model evaluated at lag (sample.dt), result plotted at display_tau (sample.t)."
    )
    ax_chi.set_ylabel("chi(tau)")
    ax_chi.legend(loc="best", fontsize=7.5, frameon=False)
    ax_chi.grid(True, alpha=0.25)

    # Clamp y-limits to empirical + model curves only; per-window fan
    # may extend outside the frame on substrates where trail-vector
    # observables have a different natural range than the raw (C, chi).
    ax_C.set_ylim(*_y_limits_from(
        data.empirical.C, view.predicted.C, view.banach.C,
    ))
    ax_chi.set_ylim(*_y_limits_from(
        data.empirical.chi, view.predicted.chi, view.banach.chi,
    ))


def render_png(data: ComparisonData, out_path: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if data.lens_solver is None:
        # Lens-solver path unavailable (no folder mapping, no batch result,
        # or label miss). Fall back to single-column layout.
        fig, (ax_C, ax_chi) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
        _draw_path_column(ax_C, ax_chi, data, data.two_stage,
                          show_per_window_label=True)
        ax_C.set_title("two-stage inversion (lens-solver unavailable)", fontsize=9)
    else:
        fig, axes = plt.subplots(2, 2, figsize=(15, 8), sharex=True, sharey="row")
        (ax_C_ts, ax_C_ls), (ax_chi_ts, ax_chi_ls) = axes
        _draw_path_column(ax_C_ts, ax_chi_ts, data, data.two_stage,
                          show_per_window_label=True)
        _draw_path_column(ax_C_ls, ax_chi_ls, data, data.lens_solver,
                          show_per_window_label=False)
        ax_C_ts.set_title(
            f"two-stage inversion  ·  chit={data.two_stage.chit:.3f}",
            fontsize=10,
        )
        ax_C_ls.set_title(
            f"lens-solver prior  ·  chit={data.lens_solver.chit:.3f}",
            fontsize=10,
        )
        # Drop redundant y-label from the right column.
        ax_C_ls.set_ylabel("")
        ax_chi_ls.set_ylabel("")

    gt = f", gt_regime={data.ground_truth_regime}" if data.ground_truth_regime else ""
    disag = (
        f"  ·  |chit_two_stage - chit_lens|={data.cross_path_disagreement:.3f}"
        if data.cross_path_disagreement is not None else ""
    )
    title = (
        f"{data.bundle_id}\n"
        f"{data.substrate_class} / {data.xdot_choice}{gt}{disag}"
    )
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path
