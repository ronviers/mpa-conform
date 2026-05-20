"""Curator-path post-processor — walks the mpa-central library and emits
committed declaration_bundle.v0.2 + DataUpload artifacts plus per-class
driver profiles.

v0.2 (this revision):
  - Schema bumped v0.1 -> v0.2; fit_provenance becomes required with
    fitted_params + predicted_locus + audit_delta + scale-solver stamps.
  - Per-cell inversion fit via conformer.compute.inversion.invert (replaces
    v0.1's leading-order-rule-only fit_provenance).
  - Substrate-conditional tau rescaling for the fit only (the bundle
    stores native-frame tau in observable.data unchanged).
  - mpa_scale_solver v1.0.0 validation + provenance stamps when a driver
    profile is available; degrades to local-only when not.

Acceptance test:
  1. Runs over all 60 grind cells without erroring; per-cell failures logged.
  2. Output dir contains 60 DataUpload bundles + 3 driver-profile JSONs.
  3. Each DataUpload validates against declaration-bundle.v0.2.
  4. Each driver profile validates against driver-profile.v0.2.json.
  5. fit_provenance.audit_delta.locus_residual is finite for every cell with >=2 usable rows.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import mpa_scale_solver as mss

from conformer.calibration import cross_path as _cross_path
from conformer.calibration import percentile as _percentile
from conformer.compute import gfdr_model, inversion
from conformer.curator.driver_profile_builder import (
    CDV1_VERSION,
    GAMUT_SEEDS,
    build_driver_profile,
)
from conformer.curator.substrate_class_rules import (
    canonical_params,
    class_id_for,
    tau_obs_aggregated_note,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = Path("H:/mpa-central/library/data")
DEFAULT_OUTPUT = REPO_ROOT / "output" / "seed-corpus"
SCHEMA_PATH = REPO_ROOT / "schema" / "declaration-bundle.v0.3.json"

MPA_CONFORM_VERSION = "v0.3.0"
MPA_SCALE_SOLVER_VERSION = mss.__version__


def _stable_dumps(obj: Any) -> str:
    """v0.2 'json-stable-keys' (unchanged from v0.1); JCS is the signing-
    track concern (parallel to this schema bump)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_body(bundle_without_signature: dict[str, Any]) -> str:
    return hashlib.sha256(_stable_dumps(bundle_without_signature).encode("utf-8")).hexdigest()


def _cell_paths(library_root: Path) -> list[Path]:
    paths = []
    for sub in ("brain", "glass", "quantum"):
        d = library_root / sub
        if not d.is_dir():
            continue
        paths.extend(sorted(d.glob("*.json")))
    return paths


def _extract_observable(cell: dict[str, Any]) -> dict[str, Any]:
    """Top-level (lag, C_mean, chi_mean) from all_samples. Lag-anchored
    canonical time per v0.4 schema: observable.data[].tau IS the framework
    lag (= sample.dt = sample-time minus t_w). Sample-time is preserved
    in display_tau for substrates whose community plots vs absolute time
    (CK 1993 convention for glass).

    Previous revisions (v0.1-v0.3) emitted sample.t as "tau", which
    conflated the model's internal time variable (lag) with the plot's
    x-axis (community-chosen display). The conflation produced visual
    artifacts (the hairpin) at small lag and forced any 1-parameter fit
    onto a coordinate-compressed empirical. v0.4 separates the two: the
    model gets lag; display gets display_tau.

    Returns native-frame rows; rescaling for the fit happens separately
    in _resolve_tau_scale + _rows_for_fit.
    """
    samples = cell.get("results", {}).get("all_samples", [])
    rows: list[dict[str, Any]] = []
    n_real: Optional[int] = None
    any_uncertainty = False
    for s in samples:
        lag = s.get("dt")             # canonical model time = lag since snapshot
        sample_time = s.get("t")      # display convention (sample-time)
        C = s.get("C_mean")
        chi = s.get("chi_mean")
        C_sem = s.get("C_sem")
        chi_sem = s.get("chi_sem")
        if lag is None or C is None or chi is None:
            continue
        row = {"tau": float(lag), "C": float(C), "chi": float(chi)}
        if sample_time is not None:
            row["display_tau"] = float(sample_time)
        if C_sem is not None:
            row["C_sem"] = float(C_sem)
            any_uncertainty = True
        if chi_sem is not None:
            row["chi_sem"] = float(chi_sem)
            any_uncertainty = True
        rows.append(row)
        if n_real is None and "n_realizations" in s:
            n_real = int(s["n_realizations"])
    return {"rows": rows, "n_realizations": n_real, "uncertainty_reported": any_uncertainty}


def _coverage_range(rows: list[dict[str, Any]], key: str) -> list[float]:
    if not rows:
        return [0.0, 0.0]
    values = [r[key] for r in rows if key in r]
    if not values:
        return [0.0, 0.0]
    return [min(values), max(values)]


# Per-substrate chi-convention declarations. The bundle's
# observable.data[].chi values are NOT directly comparable across
# substrates today -- each substrate's grinder primitive emits chi in
# its own convention. Glass happens to emit in FDR-dimensionless form
# (verified by Session 7's KWW + FDT-violation fit, RMS 0.073 on the
# T=0.5 cell). Brain and QEC do not -- empirical chi/dC ratios vary
# structurally across the cell, not just by scale.
#
# This metadata field declares the convention explicitly so downstream
# consumers (banach_overlay, the auditor's eventual chi rendering, the
# 6-param inversion) can respect it. Per-substrate normalization
# mappings (the actual translation from substrate-emitted to FDR-
# canonical) are owed to follow-on sessions and require substrate-
# domain expertise -- see docs/papers/chi_convention_lock_in.md.
_CHI_CONVENTION_BY_SUBSTRATE: dict[str, str] = {
    "glass":   "fdr_dimensionless",
    "brain":   "substrate_emitted_uncalibrated",
    "quantum": "substrate_emitted_uncalibrated",
}

_CHI_CONVENTION_NOTES: dict[str, str] = {
    "glass": (
        "Glass spin-flip and spin-relative xdot emit chi in FDR-dimensionless "
        "form. Verified empirically at T=0.5: the FDT line T*chi = dC fits "
        "with the KWW + FDT-violation 6-vector (Session 7, RMS 0.073). "
        "No normalization needed; the model's chi(C) form applies directly."
    ),
    "brain": (
        "Neural-population velocity, position-relative, position-displacement, "
        "and boundary-cross xdot all emit chi in a substrate-conventional form "
        "that is NOT FDR-canonical. Empirical chi/dC ratio varies by ~32x "
        "across a single cell (suspended scenario): functional form, not "
        "scalar, mismatch with FDT. The chi axis's mapping onto canonical "
        "form is owed to a follow-on session with brain-substrate domain input."
    ),
    "quantum": (
        "Surface-code QEC detection-event and events-since-snap xdot emit chi "
        "in a cumulative-event-statistics frame (empirical chi ~ 13 at p_base "
        "= 0.001; the framework's FDT prediction would be < 1.0, off by ~13x). "
        "The chi axis's mapping onto canonical form is owed to a follow-on "
        "session that decides the QEC chi normalization (likely involves "
        "p_base * t_obs total events, or sqrt(events) variance scale)."
    ),
}


def _chi_convention_for(substrate: str) -> str:
    """Per-substrate declaration of chi-axis convention. See module-level
    _CHI_CONVENTION_BY_SUBSTRATE for the lookup."""
    return _CHI_CONVENTION_BY_SUBSTRATE.get(substrate, "substrate_emitted_uncalibrated")


def _chi_convention_note_for(substrate: str) -> str:
    """Per-substrate human-readable rationale for the chi_convention. See
    module-level _CHI_CONVENTION_NOTES for the lookup."""
    return _CHI_CONVENTION_NOTES.get(substrate, "Convention unknown for this substrate; treat empirical chi as uncalibrated.")


def _operating_point_summary(substrate: str, op: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in op.items() if v is not None}


# --- v0.2 additions: tau rescaling + fit + audit_delta ----------------


def _resolve_tau_scale(substrate: str, tau_env: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[float, str]:
    """Substrate-conditional tau scale for the fit. Returns (scale, rationale).

    The analytical gFDR model (conformer.compute.gfdr_model) is parameterized
    with tau_c ~ O(10) in the c regime; library cells carry tau values in
    [501, 45000]. Without rescaling, the stage-1 analytical fit saturates
    (any chit looks the same in the model's asymptotic tail). Rescaling
    by tau_env makes the fit dimensionless and lands the curve in the
    model's resolving range.

    Per ROADMAP.md §v0.2 'adjacent fix'. The bundle's observable.data
    still carries native tau; rescaling is internal to the fit.
    """
    val = tau_env.get("value") if isinstance(tau_env, dict) else None
    if isinstance(val, (int, float)) and val > 0 and val == val:  # finite & positive
        return float(val), f"tau_env_analytic.value ({tau_env.get('method', '?')})"
    # Fallback: substrate-conditional median-tau scale.
    taus = [r["tau"] for r in rows if "tau" in r]
    if not taus:
        return 1.0, "fallback: no rows; scale=1 (fit is moot)"
    med = float(statistics.median(taus))
    return med, f"fallback: tau_env null/unbounded ({tau_env.get('method', '?') if isinstance(tau_env, dict) else 'absent'}); using median tau ({med:.3g})"


def _rows_for_fit(rows: list[dict[str, Any]], tau_scale: float) -> list[dict[str, Any]]:
    """Native rows -> dimensionless-tau rows for inversion.invert."""
    return [{**r, "tau": float(r["tau"]) / tau_scale} for r in rows]


def _predicted_locus_rows(fit_chit: float, native_rows: list[dict[str, Any]], tau_scale: float) -> list[dict[str, Any]]:
    """Analytical locus at fit_chit, interpolated at the empirical native-tau
    values. Returns one row per native row with (tau_native, C_predicted,
    chi_predicted)."""
    model = gfdr_model.generate_locus(fit_chit)
    out: list[dict[str, Any]] = []
    for r in native_rows:
        tau_native = float(r["tau"])
        tau_dim = tau_native / tau_scale
        C_pred, chi_pred = gfdr_model._interp_log_tau(model, tau_dim)
        out.append({"tau": tau_native, "C_predicted": C_pred, "chi_predicted": chi_pred})
    return out


def _per_row_residuals(native_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for emp, pred in zip(native_rows, pred_rows):
        out.append({
            "tau": float(emp["tau"]),
            "C_residual": float(emp["C"]) - float(pred["C_predicted"]),
            "chi_residual": float(emp["chi"]) - float(pred["chi_predicted"]),
        })
    return out


def _gamut_spec_for(class_id: str) -> Optional[mss.GamutSpec]:
    """Build a mpa_scale_solver.GamutSpec from the driver_profile_builder
    GAMUT_SEEDS dict for this class. Returns None if the class isn't seeded."""
    seed = GAMUT_SEEDS.get(class_id)
    if not seed:
        return None
    # GAMUT_SEEDS uses chit_range only; gamma_AB is unbounded in v0.1 seeds.
    # Use a generous gamma envelope for the gamut check.
    return mss.GamutSpec(
        chit_range=tuple(seed["chit_range"]),
        gamma_AB_range=(-1.0, 1.0),
        tau_obs_range=None,
        out_of_scope_residual_threshold=seed.get("out_of_scope_residual_threshold", 0.05),
    )


def _provenance_to_dict(p: mss.Provenance) -> dict[str, Any]:
    return {
        "solver_version": p.solver_version,
        "operation": p.operation,
        "timestamp_ns": int(p.timestamp_ns),
        "dispatch_path": p.dispatch_path.value if hasattr(p.dispatch_path, "value") else str(p.dispatch_path),
        "table_version": p.table_version,
        "notes": list(p.notes),
    }


def _validation_to_dict(v: mss.ValidationReport) -> dict[str, Any]:
    return {
        "asymptotic_closure_compliant": bool(v.asymptotic_closure_compliant),
        "k_frust_invariant": bool(v.k_frust_invariant),
        "round_trip_residual": (float(v.round_trip_residual) if v.round_trip_residual is not None else None),
        "notes": list(v.notes),
    }


def _v03_audit_delta_extras(
    fit_diagnostics_dict: Optional[dict[str, Any]],
    substrate: str,
    path: str,
    cross_path_disagreement: Optional[float],
) -> dict[str, Any]:
    """v0.3 additive audit_delta block: raw fit_diagnostics + per-substrate
    baseline percentiles + cross-path disagreement.

    Each field is computed independently and can be None when the
    underlying signal is not available (no baseline for this substrate
    yet, only one path ran for this cell, etc.)."""
    if fit_diagnostics_dict is None:
        return {
            "fit_diagnostics": None,
            "diagnostic_percentiles": None,
            "cross_path_disagreement": cross_path_disagreement,
        }
    baseline = _percentile.load_baseline(substrate)
    pcts = _percentile.percentiles_for_diagnostics(fit_diagnostics_dict, path, baseline)
    return {
        "fit_diagnostics": fit_diagnostics_dict,
        "diagnostic_percentiles": pcts,
        "cross_path_disagreement": cross_path_disagreement,
    }


def _run_fit(
    native_rows: list[dict[str, Any]],
    tau_scale: float,
    class_id: str,
    tau_obs_value: Optional[float],
    canonical_seed: dict[str, Any],
    substrate: str,
    cross_path_disagreement: Optional[float],
) -> dict[str, Any]:
    """Run inversion.invert in dimensionless frame + scale-solver validation
    stamps. Returns the full fit_provenance object per v0.2 schema."""
    rows_dim = _rows_for_fit(native_rows, tau_scale)
    fit = inversion.invert(rows_dim, initial_gamma=canonical_seed.get("gamma_AB", -0.3))

    pred_rows = _predicted_locus_rows(fit.chit, native_rows, tau_scale)
    per_row_res = _per_row_residuals(native_rows, pred_rows)
    locus_residual_native = sum(r["C_residual"] ** 2 + r["chi_residual"] ** 2 for r in per_row_res) / max(1, len(per_row_res))

    method = "two_stage_with_gamma_fit" if fit.gamma_constrained else "two_stage_locus_fit"

    canonical_state = mss.CanonicalState(
        chit=fit.chit, gamma_AB=fit.gamma_AB, k_frust=bool(canonical_seed.get("k_frust", False))
    )
    tau_obs_for_stamps = float(tau_obs_value) if tau_obs_value is not None else 1.0

    regime_reading = mss.regime_at(canonical_state, tau_obs_for_stamps)
    regime_label = regime_reading.regime

    in_gamut: Optional[bool] = None
    gamut_spec = _gamut_spec_for(class_id)
    if gamut_spec is not None:
        gamut_out = mss.gamut_classify(canonical_state, tau_obs_for_stamps, gamut_spec)
        in_gamut = bool(gamut_out.get("in_gamut"))

    # Optional richer stamps: only ride when we have a driver profile shape
    # that scale-solver can parse. The first walk-pass doesn't yet have the
    # profile (it's built after all cells walk), so we skip apply_translation
    # stamps here. Future v0.3+: two-pass walk to fold the profile-derived
    # apply_translation provenance back into already-built bundles.
    inv_prov = _provenance_to_dict(mss.make_provenance(
        operation="inversion_chain_locus_fit_plus_regime_at",
        dispatch_path=mss.DispatchPath.DIRECT_COMPUTE,
    ))
    inv_val = {
        "asymptotic_closure_compliant": not (abs(fit.chit) < 1e-6 and abs(fit.gamma_AB) < 1e-6),
        "k_frust_invariant": True,
        "round_trip_residual": float(locus_residual_native),
        "notes": [
            f"chit_observable={fit.chit_observable}",
            f"gamma_observable={fit.gamma_observable}",
            f"stage1_chit={fit.stage1_chit}",
            f"stage2_n_ensemble={fit.stage2_n_ensemble} stage2_n_analytical={fit.stage2_n_analytical}",
        ],
    }

    return {
        "fitted_params": {
            "chit": float(fit.chit),
            "gamma_AB": float(fit.gamma_AB),
        },
        "predicted_locus": {
            "rows": pred_rows,
            "model": "gfdr_analytical",
        },
        "audit_delta": {
            "locus_residual": float(locus_residual_native),
            "gamma_residual": (float(fit.gamma_residual) if fit.gamma_residual is not None else None),
            "per_row_residuals": per_row_res,
            "regime_label": regime_label,
            "in_gamut": in_gamut,
            **_v03_audit_delta_extras(
                fit_diagnostics_dict=(fit.fit_diagnostics.to_dict() if fit.fit_diagnostics is not None else None),
                substrate=substrate,
                path="two_stage_inversion",
                cross_path_disagreement=cross_path_disagreement,
            ),
        },
        "method": method,
        "substrate_class_id": class_id,
        "observable_used": {
            "chit": fit.chit_observable,
            "gamma_AB": fit.gamma_observable,
        },
        "k_frust_hint": bool(canonical_seed.get("k_frust", False)),
        "note": (
            "v0.3 curator-time inversion fit. Two-stage chit (analytical + ensemble refine) "
            f"in dimensionless tau frame (tau_scale={tau_scale:.6g}). Predicted locus + "
            "audit_delta in native tau frame. Scale-solver stamps via regime_at + gamut_classify "
            "(v1.0.0). audit_delta carries fit_diagnostics + diagnostic_percentiles "
            "(per-substrate baseline) + cross_path_disagreement. Viewers consume; they do not refit."
        ),
        "inversion_provenance": inv_prov,
        "inversion_validation": inv_val,
    }


def _fit_provenance_leading_order_fallback(canonical: dict[str, Any], class_id: str, reason: str) -> dict[str, Any]:
    """When the cell has no usable observable rows, fall back to the
    leading-order-rule shape from v0.1. Still required-shape per v0.2 but
    with stub predicted_locus + audit_delta. v0.3 fields are null —
    fit_diagnostics/percentiles/cross-path all require a real fit."""
    return {
        "fitted_params": {"chit": float(canonical["chit"]), "gamma_AB": float(canonical["gamma_AB"])},
        "predicted_locus": {"rows": [], "model": "gfdr_analytical"},
        "audit_delta": {
            "locus_residual": float("inf"),
            "gamma_residual": None,
            "per_row_residuals": [],
            "regime_label": gfdr_model.vertex_regime(float(canonical["chit"])),
            "in_gamut": None,
            "fit_diagnostics": None,
            "diagnostic_percentiles": None,
            "cross_path_disagreement": None,
        },
        "method": "leading_order_substrate_rule",
        "substrate_class_id": class_id,
        "observable_used": {"chit": "leading-order-substrate-rule", "gamma_AB": "leading-order-substrate-rule"},
        "k_frust_hint": bool(canonical.get("k_frust", False)),
        "note": f"Leading-order substrate-class rule (v0.1 carry-over). Reason: {reason}",
        "inversion_provenance": None,
        "inversion_validation": None,
    }


# --- bundle assembly ---------------------------------------------------


def conform_cell(
    cell_path: Path,
    substrate: str,
    *,
    cross_path_disagreement: Optional[float] = None,
) -> dict[str, Any]:
    """Build a declaration_bundle.v0.3 from a single library cell.

    cross_path_disagreement (v0.3): pre-computed |chit_two_stage -
    chit_lens_solver_prior| for this cell within its substrate batch.
    Computed once per substrate in run() so the lens-solver batch sees
    full trajectory context (predictor active). None when the substrate
    batch wasn't lens-solver-fit (degraded mode)."""
    cell = json.loads(cell_path.read_text(encoding="utf-8"))
    op = cell.get("operating_point", {})
    xdot = cell.get("xdot_kind") or "unknown"
    schedule = cell.get("schedule", {})
    tau_env = cell.get("tau_env_analytic") or {}

    obs = _extract_observable(cell)
    rows = obs["rows"]
    if not rows:
        raise ValueError(f"empty observable: {cell_path.name}")

    canonical_seed = canonical_params(substrate, op)
    class_id = class_id_for(substrate)

    bundle_id = str(uuid.uuid4())
    op_summary = _operating_point_summary(substrate, op)

    tau_windows = schedule.get("tau_windows") or []
    tau_obs_repr = tau_windows[len(tau_windows) // 2] if tau_windows else None

    tau_units = "mc_steps" if substrate == "glass" else ("qec_rounds" if substrate == "quantum" else "neural_time_units")
    columns = [
        {
            "name": "tau", "units": tau_units,
            "description": (
                "Lag since snapshot (= sample.dt = sample-time minus t_w). "
                "The framework's canonical FDR parametric variable. "
                "v0.4: lag-anchored, previous schemas (v0.1-v0.3) emitted "
                "sample-time here -- see display_tau for that."
            ),
            "physical_quantity": "delay_time", "uncertainty_column": None,
            "coverage_range": _coverage_range(rows, "tau"),
            "validity_range": _coverage_range(rows, "tau"),
            "range_source": "computed",
        },
        {
            "name": "display_tau", "units": tau_units,
            "description": (
                "Substrate-community display convention for the FDR x-axis "
                "(= sample.t = lag + t_w). For glass, the CK 1993 convention "
                "plots vs sample-time, so curators rendering for the glass "
                "community use this field on the x-axis. Display only -- "
                "the model evaluates at tau (lag)."
            ),
            "physical_quantity": "delay_time", "uncertainty_column": None,
            "coverage_range": _coverage_range(rows, "display_tau"),
            "validity_range": _coverage_range(rows, "display_tau"),
            "range_source": "computed",
        },
        {
            "name": "C", "units": "dimensionless",
            "description": "Autocorrelation C(lag). Window-aggregated top-level C_mean from grind cell.",
            "physical_quantity": "correlation",
            "uncertainty_column": "C_sem" if any("C_sem" in r for r in rows) else None,
            "coverage_range": _coverage_range(rows, "C"),
            "validity_range": _coverage_range(rows, "C"),
            "range_source": "computed",
        },
        {
            "name": "chi", "units": "dimensionless",
            "description": "Integrated response chi(lag). Window-aggregated top-level chi_mean.",
            "physical_quantity": "response",
            "uncertainty_column": "chi_sem" if any("chi_sem" in r for r in rows) else None,
            "coverage_range": _coverage_range(rows, "chi"),
            "validity_range": _coverage_range(rows, "chi"),
            "range_source": "computed",
        },
    ]

    # v0.2 fit: tau rescale -> inversion -> predicted_locus -> audit_delta.
    tau_scale, tau_scale_rationale = _resolve_tau_scale(substrate, tau_env, rows)
    if len(rows) >= 2:
        fit_prov = _run_fit(
            rows, tau_scale, class_id, tau_obs_repr, canonical_seed,
            substrate=substrate, cross_path_disagreement=cross_path_disagreement,
        )
    else:
        fit_prov = _fit_provenance_leading_order_fallback(canonical_seed, class_id, "cell has <2 usable rows")

    body: dict[str, Any] = {
        "schema": "declaration-bundle.v0.4",
        "bundle_id": bundle_id,
        "tier": "curated",
        "substrate_class": class_id,
        "xdot_choice": xdot,
        "tau_obs": {
            "value": tau_obs_repr,
            "units": tau_units,
            "method": "aggregated",
            "note": tau_obs_aggregated_note(substrate),
        },
        "provenance": {
            "citation_text": (
                f"MPA Central library, {substrate} substrate, {cell_path.name}. "
                "Generated by H:/mpa-central/library/grind_library.py "
                "(LIBRARY_SPEC.md v1.0)."
            ),
            "authors": ["MPA Central library curators"],
            "publication_title": None,
            "publication_venue": "mpa-central library (internal)",
            "publication_year": 2026,
            "doi": None,
            "doi_verified": False,
            "url": "https://github.com/ronviers/mpa-central",
            "collection_date": cell.get("completed_at"),
            "license": "MIT",
            "license_url": "https://opensource.org/license/mit",
            "acknowledgments_text": None,
            "bibtex": None,
            "contact_email": None,
            "version_or_doi_of_dataset": cell.get("library_spec_version"),
        },
        "columns": columns,
        "observable": {
            "format": "canonical_fdr",
            "data": rows,
            "n_rows": len(rows),
            "n_realizations": obs["n_realizations"],
            "uncertainty_reported": obs["uncertainty_reported"],
            "uncertainty_methodology": {
                "type": "sem",
                "description": "Per-sample SEM from grind cell's n_realizations ensemble (LIBRARY_SPEC.md §Realizations).",
            } if obs["uncertainty_reported"] else None,
            "preprocessing_log": [
                {
                    "operation": "extract_top_level_observable",
                    "parameters": {
                        "source": "all_samples[].{dt,t,C_mean,chi_mean}",
                        "tau_field": "dt (lag since snapshot, framework-canonical)",
                        "display_tau_field": "t (sample-time, substrate-community display)",
                    },
                    "rationale": (
                        "v0.4 lag/display split: model reads tau=lag; viewer reads "
                        "display_tau for the substrate community's preferred x-axis."
                    ),
                    "reversible": True,
                },
                {
                    "operation": "tau_rescale_for_fit",
                    "parameters": {"tau_scale": tau_scale, "rationale": tau_scale_rationale},
                    "rationale": (
                        "Per ROADMAP §v0.2 adjacent fix: dimensionless-tau rescaling for inversion fit "
                        "(internal). observable.data is native-frame and unchanged."
                    ),
                    "reversible": True,
                },
            ],
            "metadata": {
                "library_tau_windows": tau_windows,
                "library_t_w": schedule.get("t_w"),
                "library_t_obs": schedule.get("t_obs"),
                "library_n_realizations_cell": schedule.get("n_realizations"),
                "tau_env_analytic": tau_env,
                "ground_truth_regime": op.get("gt"),
                "operating_point_T": op.get("T"),
                "operating_point_h_field": op.get("h_field"),
                "operating_point_p_base": op.get("p_base"),
                "tau_anchoring": "lag",
                "chi_convention": _chi_convention_for(substrate),
                "chi_convention_note": _chi_convention_note_for(substrate),
            },
        },
        "scalar_observables": None,
        "fit_provenance": fit_prov,
        "declaration_trail": [
            {
                "kind": "substrate_class",
                "answered_by": "curator",
                "value": class_id,
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "Mapped from library cell substrate via SUBSTRATE_TO_CLASS_ID.",
            },
            {
                "kind": "xdot_choice",
                "answered_by": "curator",
                "value": xdot,
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "Read from grind cell's xdot_kind field.",
            },
            {
                "kind": "tau_obs",
                "answered_by": "curator",
                "value": {"method": "aggregated", "representative_value": tau_obs_repr},
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "Window-aggregated reading; per-window slicing deferred.",
            },
            {
                "kind": "license",
                "answered_by": "curator",
                "value": "MIT",
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "mpa-central library is MIT-licensed; bundles inherit.",
            },
            {
                "kind": "canonical_params",
                "answered_by": "curator",
                "value": canonical_seed,
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "Leading-order substrate-class rule seeded the initial gamma_AB; full inversion ran on top.",
            },
            {
                "kind": "fit_method",
                "answered_by": "curator",
                "value": fit_prov["method"],
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "v0.2: curator-time inversion fit + scale-solver validation stamps.",
            },
        ],
        "declaration_assistant": None,
        "raw_data_archive_ref": f"local://{cell_path.as_posix()}",
        "version_context": {
            "mpa_conform": MPA_CONFORM_VERSION,
            "cdv1": CDV1_VERSION,
            "mpa_scale_solver": MPA_SCALE_SOLVER_VERSION,
            "openalex_mcp": None,
            "citecheck": None,
            "primary_llm": None,
            "secondary_llm": None,
            "correlator": None,
        },
    }

    body["signature"] = {
        "manifest_hash": _hash_body(body),
        "manifest_hash_alg": "sha256",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "signed_by": "mpa-conform curator (v0.3)",
        "algorithm": "none",
        "canonical_form": "json-stable-keys",
        "envelope": None,
        "pubkey_fingerprint": None,
    }

    # Keep the canonical that goes into driver-profile.translation_field as
    # the leading-order rule seed (the driver profile is built from these,
    # not from per-cell fits; fits feed the bundle's audit_delta, not the
    # profile's lookup table).
    bundle_meta_carry = {
        "bundle_id": bundle_id,
        "_relative_path": "",
        "_operating_point_summary": op_summary,
        "xdot_choice": xdot,
        "tier": "curated",
        "_canonical": canonical_seed,
        "_op_full": op,
        "_tau_env_analytic": tau_env,
    }
    return {"body": body, "meta": bundle_meta_carry}


def _slug(substrate: str, cell_name: str) -> str:
    return cell_name.removesuffix(".json")


def _write_data_upload(out_root: Path, class_id: str, cell_path: Path, body: dict[str, Any]) -> Path:
    class_dir = out_root / class_id
    class_dir.mkdir(parents=True, exist_ok=True)
    out_path = class_dir / f"{_slug(cell_path.parent.name, cell_path.name)}.bundle.json"
    out_path.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def _write_driver_profile(out_root: Path, class_id: str, profile: dict[str, Any]) -> Path:
    class_dir = out_root / class_id
    class_dir.mkdir(parents=True, exist_ok=True)
    out_path = class_dir / "driver-profile.json"
    out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def _compute_cross_path_disagreements_for_substrate(
    substrate: str, cell_paths: list[Path],
) -> dict[str, Optional[float]]:
    """v0.3: per substrate batch, run two_stage_inversion per cell + a
    single batched lens_solver_prior call (predictor active across the
    trajectory), return {operating_point_label: disagreement}.

    Failures in either path produce None for that cell — no cross-path
    signal but the v0.2 fit still emits."""
    cells: list[dict[str, Any]] = []
    for p in cell_paths:
        try:
            cells.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue

    two_stage_by_label: dict[str, Optional[float]] = {}
    for cell in cells:
        op_label = cell.get("operating_point", {}).get("label")
        if op_label is None:
            continue
        tau_env_block = cell.get("tau_env_analytic") or {}
        tau_env_val = tau_env_block.get("value")
        rows = _extract_observable(cell)["rows"]
        if len(rows) < 2:
            two_stage_by_label[op_label] = None
            continue
        tau_scale, _ = _resolve_tau_scale(substrate, tau_env_block, rows)
        rows_dim = _rows_for_fit(rows, tau_scale)
        try:
            fit = inversion.invert(rows_dim, initial_gamma=-0.3)
            two_stage_by_label[op_label] = float(fit.chit)
        except Exception:
            two_stage_by_label[op_label] = None

    xdot = (cells[0].get("xdot_kind") or "unknown") if cells else "unknown"
    try:
        return _cross_path.cross_path_disagreements_for_batch(
            substrate, cells, xdot, two_stage_by_label, max_passes=10, rng_seed=0,
        )
    except Exception as e:
        print(f"  [warn] cross-path for {substrate} failed: {e}", file=sys.stderr)
        return {label: None for label in two_stage_by_label}


def run(library_root: Path = DEFAULT_LIBRARY, output_root: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)

    cells: list[Path] = _cell_paths(library_root)
    if not cells:
        raise SystemExit(f"no library cells found under {library_root}")

    per_class_cells: dict[str, list[dict[str, Any]]] = {}
    per_class_uploads: dict[str, list[dict[str, Any]]] = {}
    failures: list[dict[str, Any]] = []
    successes = 0

    # v0.3: group by substrate, pre-compute cross-path disagreements per
    # substrate batch (lens-solver call with predictor active), then loop
    # cells with the disagreement looked up per cell.
    cells_by_substrate: dict[str, list[Path]] = {}
    for cell_path in cells:
        cells_by_substrate.setdefault(cell_path.parent.name, []).append(cell_path)

    cross_path_map_by_substrate: dict[str, dict[str, Optional[float]]] = {}
    for substrate, paths in cells_by_substrate.items():
        print(f"computing cross-path disagreements for {substrate} ({len(paths)} cells)...")
        cross_path_map_by_substrate[substrate] = _compute_cross_path_disagreements_for_substrate(
            substrate, paths,
        )

    for cell_path in cells:
        substrate = cell_path.parent.name
        cell_label: Optional[str] = None
        try:
            cell_label = json.loads(cell_path.read_text(encoding="utf-8")).get("operating_point", {}).get("label")
        except Exception:
            cell_label = None
        cross_path_disagreement = cross_path_map_by_substrate.get(substrate, {}).get(cell_label) if cell_label else None

        try:
            result = conform_cell(cell_path, substrate, cross_path_disagreement=cross_path_disagreement)
            body = result["body"]
            meta = result["meta"]
            class_id = body["substrate_class"]
            out_path = _write_data_upload(output_root, class_id, cell_path, body)
            meta["_relative_path"] = str(out_path.relative_to(output_root))
            per_class_uploads.setdefault(class_id, []).append({**meta, "bundle_id": body["bundle_id"]})
            per_class_cells.setdefault(class_id, []).append({
                "operating_point": meta["_op_full"],
                "canonical": meta["_canonical"],
                "xdot_choice": meta["xdot_choice"],
                "tau_env_analytic": meta["_tau_env_analytic"],
                "data_upload_id": body["bundle_id"],
            })
            successes += 1
            print(f"[ok] {cell_path.name} -> {out_path.relative_to(output_root.parent)}")
        except Exception as e:
            failures.append({"cell": cell_path.name, "substrate": substrate, "error": str(e)})
            print(f"[fail] {cell_path.name}: {e}", file=sys.stderr)

    profile_paths: dict[str, str] = {}
    for class_id, cells_for_class in per_class_cells.items():
        try:
            profile = build_driver_profile(
                class_id,
                cells_for_class,
                per_class_uploads[class_id],
            )
            p = _write_driver_profile(output_root, class_id, profile)
            profile_paths[class_id] = str(p.relative_to(output_root.parent))
            print(f"[ok] driver profile {class_id} -> {p.relative_to(output_root.parent)}")
        except Exception as e:
            failures.append({"class": class_id, "error": f"driver profile build failed: {e}"})
            print(f"[fail] driver profile {class_id}: {e}", file=sys.stderr)

    summary = {
        "schema": SCHEMA_PATH.name,
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "library_root": str(library_root),
        "output_root": str(output_root),
        "cells_total": len(cells),
        "cells_succeeded": successes,
        "cells_failed": len(failures),
        "failures": failures,
        "data_uploads_by_class": {k: len(v) for k, v in per_class_uploads.items()},
        "driver_profiles": profile_paths,
        "mpa_conform_version": MPA_CONFORM_VERSION,
        "mpa_scale_solver_version": MPA_SCALE_SOLVER_VERSION,
    }
    summary_path = output_root / "_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSummary: {successes}/{len(cells)} cells; "
          f"{len(profile_paths)} driver profiles; "
          f"summary at {summary_path.relative_to(output_root.parent)}")
    return summary


if __name__ == "__main__":
    run()
