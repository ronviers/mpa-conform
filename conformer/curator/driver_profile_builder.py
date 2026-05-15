"""Driver profile builder — produces RFC-S §4 / driver-profile.v0.2.json
shape per substrate class. Pure post-processing over the per-cell
DataUploads + their canonical-parameter estimates."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


CDV1_VERSION = "v9.1"
PROFILE_VERSION = "v0.1.0-mpa-conform-bootstrap"
TARGET_RFC_VERSIONS = ["MPA-RFC-S v0.2"]


# Gamut seeds: leading-order numerical envelopes per class. Carried
# forward from mpa-auditor's M6 per-class stand-in (corpus/substrate-
# classes.json), refined as instances land.
GAMUT_SEEDS: dict[str, dict[str, Any]] = {
    "ck-glassy": {
        "chit_range": [-1.0, 1.0],          # T grid 0.2..1.8 -> chit grid -0.8..+0.8
        "tau_obs_constraint": None,
        "out_of_scope_residual_threshold": 0.05,
        "s_window_width_formula": None,
        "s_window_width_floor": None,
    },
    "surface-code-qec": {
        "chit_range": [-1.7, 4.7],          # p 1e-4..5e-2 -> ln(p_th/p) span
        "tau_obs_constraint": None,
        "out_of_scope_residual_threshold": 0.05,
        "s_window_width_formula": "hard_wall:indicator(p>=p_threshold)",
        "s_window_width_floor": 0.0,
    },
    "neural-population": {
        "chit_range": [-1.0, 1.0],
        "tau_obs_constraint": None,
        "out_of_scope_residual_threshold": 0.05,
        "s_window_width_formula": None,
        "s_window_width_floor": None,
    },
}


def _intents_skeleton() -> dict[str, Any]:
    """Five intents per RFC-S §3. v0.1: only I5 (reference output) is
    supported by the curator path; others ride as supported:false
    placeholders."""
    return {
        "I1": {"supported": False, "note": "operating-point set — not exercised at v0.1 curator path"},
        "I2": {"supported": False, "note": "scale management (tau_obs camera sweep) — researcher path / future"},
        "I3": {"supported": False, "note": "intent design constraints — auditor Navigate-mode territory"},
        "I4": {"supported": False, "note": "translation field round-trip — RFC-S §5 deferred"},
        "I5": {"supported": True, "note": "reference outputs — populated from per-cell DataUploads below"},
    }


def build_driver_profile(class_id: str, cells_for_class: list[dict[str, Any]], data_uploads_for_class: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble a driver profile from a class's cells and their DataUploads.

    Arguments:
        class_id: target substrate class id (e.g. 'ck-glassy').
        cells_for_class: list of (operating_point + chit/gamma_AB estimate) dicts
            built by walk_library. Each carries:
              { 'operating_point': {...},
                'canonical': {'chit': ..., 'gamma_AB': ..., 'method': ...},
                'xdot_choice': str,
                'tau_env_analytic': {...},
                'data_upload_id': str }
        data_uploads_for_class: the parallel list of DataUpload bundles
            (used to drive reference_outputs pointers).
    """
    now = datetime.now(timezone.utc).isoformat()

    operating_envelope: dict[str, Any] = {
        "axes": _operating_envelope_axes(class_id, cells_for_class),
        "n_cells": len(cells_for_class),
        "xdot_choices": sorted({c["xdot_choice"] for c in cells_for_class}),
    }

    translation_field: dict[str, Any] = {
        "direction": "forward",
        "shape": "lookup_table",
        "description": (
            "Forward-only translation field (mpa-auditor §Q13): canonical -> "
            "substrate-native. v0.1 leading-order lookup over operating-point "
            "axes. The backward map is never built."
        ),
        "rule": [
            {
                "operating_point": c["operating_point"],
                "xdot_choice": c["xdot_choice"],
                "canonical": c["canonical"],
            }
            for c in cells_for_class
        ],
    }

    reference_outputs = [
        {
            "data_upload_id": b["bundle_id"],
            "data_upload_path": b["_relative_path"],
            "operating_point": b["_operating_point_summary"],
            "xdot_choice": b["xdot_choice"],
            "tier": b["tier"],
        }
        for b in data_uploads_for_class
    ]
    if not reference_outputs:
        # driver-profile.v0.2 requires reference_outputs minItems=1. If the
        # class somehow produced no cells (shouldn't happen for the 60-cell
        # library), this is the honest failure mode.
        raise ValueError(f"class {class_id} has no reference_outputs — refusing to emit driver profile")

    return {
        "header": {
            "profile_version": PROFILE_VERSION,
            "target_rfc_versions": TARGET_RFC_VERSIONS,
            "substrate_class": class_id,
            "characterization_date": now,
            "authority": "mpa-conform curator path (bootstrap session, 2026-05-15)",
            "validation_history": [],
            "regime_classifier_axis": _regime_classifier_axis(class_id),
        },
        "operating_envelope": operating_envelope,
        "gamut": GAMUT_SEEDS[class_id],
        "translation_field": translation_field,
        "intents": _intents_skeleton(),
        "reference_outputs": reference_outputs,
        "metadata": {
            "source": "H:/mpa-central/library/data/{brain,glass,quantum}/*.json",
            "library_spec_version": "1.0",
            "cdv1_version": CDV1_VERSION,
            "leading_order_notes": "Gamut chit_range derived from the library's operating-point grid mapped through substrate_class_rules.canonical_params. Refines as substrate-side measurement lands.",
            "bootstrap_handoff": "mpa-auditor/docs/mpa-conform-bootstrap.md §5",
        },
    }


def _operating_envelope_axes(class_id: str, cells: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-class envelope axes: which operating-point fields actually vary."""
    if class_id == "ck-glassy":
        Ts = sorted({c["operating_point"].get("T") for c in cells if c["operating_point"].get("T") is not None})
        return {"T": {"values": Ts, "units": "Tc-relative", "tc_used": 1.0}}
    if class_id == "surface-code-qec":
        ps = sorted({c["operating_point"].get("p_base") for c in cells if c["operating_point"].get("p_base") is not None})
        return {"p_base": {"values": ps, "units": "dimensionless", "p_threshold_used": 1e-2}}
    if class_id == "neural-population":
        scenarios = sorted({c["operating_point"].get("scenario") for c in cells if c["operating_point"].get("scenario")})
        return {"scenario": {"values": scenarios, "units": "categorical"}}
    return {}


def _regime_classifier_axis(class_id: str) -> str:
    # See driver-profile.v0.2.json header.regime_classifier_axis docs.
    # Glass walks T (a damping-axis proxy in EA Ising) — but classified as
    # 'damping' would mean Q-resonance; glass is more squarely 'drive'-like
    # (T as inverse-drive). Surface-code is 'drive' (p_base as drive). Brain
    # is use-case-dependent (scenario is categorical, not a single axis).
    if class_id == "neural-population":
        return "use-case-dependent"
    return "drive"
