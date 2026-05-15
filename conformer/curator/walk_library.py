"""Curator-path post-processor — walks the mpa-central library and emits
committed declaration_bundle.v0.1 + DataUpload artifacts plus per-class
driver profiles.

Pure post-processing. Read-only over H:/mpa-central/library. Writes to
output/seed-corpus/. No LLM, no MCP, no network. ~300 lines.

Acceptance test (mpa-conform-bootstrap.md §5):
  1. Runs over all 60 grind cells without erroring; per-cell failures logged.
  2. Output dir contains 60 DataUpload bundles + 3 driver-profile JSONs.
  3. Each DataUpload validates against mpa-auditor's contract-05 + this
     repo's declaration-bundle.v0.1 schema (the curator bundle is a
     superset of contract-05's required fields).
  4. Each driver profile validates against driver-profile.v0.2.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from conformer.curator.driver_profile_builder import (
    CDV1_VERSION,
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
SCHEMA_PATH = REPO_ROOT / "schema" / "declaration-bundle.v0.1.json"

MPA_CONFORM_VERSION = "v0.1.0-bootstrap"


def _stable_dumps(obj: Any) -> str:
    """Canonicalization for hashing: sorted keys, no whitespace.
    v0.1 'json-stable-keys'; v0.2+ will switch to JCS (RFC 8785) per unified
    report §5."""
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
    """Top-level (t, C_mean, chi_mean) from all_samples per bootstrap §5
    step 3. Window-aggregated; per-tau_obs slicing deferred."""
    samples = cell.get("results", {}).get("all_samples", [])
    rows: list[dict[str, Any]] = []
    n_real: int | None = None
    any_uncertainty = False
    for s in samples:
        tau = s.get("t")
        C = s.get("C_mean")
        chi = s.get("chi_mean")
        C_sem = s.get("C_sem")
        chi_sem = s.get("chi_sem")
        if tau is None or C is None or chi is None:
            continue
        row = {"tau": float(tau), "C": float(C), "chi": float(chi)}
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


def _operating_point_summary(substrate: str, op: dict[str, Any]) -> dict[str, Any]:
    # Strip nulls for display; keep raw op available in bundle metadata.
    return {k: v for k, v in op.items() if v is not None}


def conform_cell(cell_path: Path, substrate: str) -> dict[str, Any]:
    """Build a declaration_bundle.v0.1 from a single library cell."""
    cell = json.loads(cell_path.read_text(encoding="utf-8"))
    op = cell.get("operating_point", {})
    xdot = cell.get("xdot_kind") or "unknown"
    schedule = cell.get("schedule", {})
    tau_env = cell.get("tau_env_analytic") or {}

    obs = _extract_observable(cell)
    rows = obs["rows"]
    if not rows:
        raise ValueError(f"empty observable: {cell_path.name}")

    canonical = canonical_params(substrate, op)
    class_id = class_id_for(substrate)

    bundle_id = str(uuid.uuid4())
    op_summary = _operating_point_summary(substrate, op)

    # tau_obs.value: the library doesn't pick a single tau_obs window for
    # the aggregated reading. Set to the median of the window grid as a
    # representative ('method=aggregated' carries the why).
    tau_windows = schedule.get("tau_windows") or []
    tau_obs_repr = tau_windows[len(tau_windows) // 2] if tau_windows else None

    columns = [
        {
            "name": "tau",
            "units": "mc_steps" if substrate == "glass" else ("qec_rounds" if substrate == "quantum" else "neural_time_units"),
            "description": "Lag time (FDR parametric variable). From grind cell all_samples[].t.",
            "physical_quantity": "delay_time",
            "uncertainty_column": None,
            "coverage_range": _coverage_range(rows, "tau"),
            "validity_range": _coverage_range(rows, "tau"),
            "range_source": "computed",
        },
        {
            "name": "C",
            "units": "dimensionless",
            "description": "Autocorrelation C(tau). Window-aggregated top-level C_mean from grind cell.",
            "physical_quantity": "correlation",
            "uncertainty_column": "C_sem" if any("C_sem" in r for r in rows) else None,
            "coverage_range": _coverage_range(rows, "C"),
            "validity_range": _coverage_range(rows, "C"),
            "range_source": "computed",
        },
        {
            "name": "chi",
            "units": "dimensionless",
            "description": "Integrated response chi(tau). Window-aggregated top-level chi_mean.",
            "physical_quantity": "response",
            "uncertainty_column": "chi_sem" if any("chi_sem" in r for r in rows) else None,
            "coverage_range": _coverage_range(rows, "chi"),
            "validity_range": _coverage_range(rows, "chi"),
            "range_source": "computed",
        },
    ]

    body: dict[str, Any] = {
        "schema": "declaration-bundle.v0.1",
        "bundle_id": bundle_id,
        "tier": "curated",
        "substrate_class": class_id,
        "xdot_choice": xdot,
        "tau_obs": {
            "value": tau_obs_repr,
            "units": "mc_steps" if substrate == "glass" else ("qec_rounds" if substrate == "quantum" else "neural_time_units"),
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
                    "parameters": {"source": "all_samples[].{t,C_mean,chi_mean}"},
                    "rationale": "Bootstrap §5 step 3: window-aggregated reading from library cell.",
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
            },
        },
        "scalar_observables": None,
        "fit_provenance": {
            "fitted_params": {
                "chit": canonical["chit"],
                "gamma_AB": canonical["gamma_AB"],
            },
            "k_frust_hint": canonical.get("k_frust", False),
            "observable_used": {"chit": "leading-order-substrate-rule", "gamma_AB": "leading-order-substrate-rule"},
            "substrate_class_id": class_id,
            "method": canonical["method"],
            "note": "Curator-path leading-order canonical-parameter estimate at the operating point. The auditor's M-Inversion proper still fits its own (chit, gamma_AB) from the observable; this is a seed for the driver profile's translation_field, NOT a constraint on the audit.",
        },
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
                "rationale": "Window-aggregated reading; per-window slicing deferred (bootstrap §5 step 2).",
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
                "value": canonical,
                "at": datetime.now(timezone.utc).isoformat(),
                "rationale": "Leading-order substrate-class rule (substrate_class_rules.canonical_params).",
            },
        ],
        "declaration_assistant": None,
        "raw_data_archive_ref": f"local://{cell_path.as_posix()}",
        "version_context": {
            "mpa_conform": MPA_CONFORM_VERSION,
            "cdv1": CDV1_VERSION,
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
        "signed_by": "mpa-conform curator (v0.1 bootstrap)",
        "algorithm": "none",
        "canonical_form": "json-stable-keys",
        "envelope": None,
        "pubkey_fingerprint": None,
    }

    bundle_meta_carry = {
        "bundle_id": bundle_id,
        "_relative_path": "",
        "_operating_point_summary": op_summary,
        "xdot_choice": xdot,
        "tier": "curated",
        "_canonical": canonical,
        "_op_full": op,
        "_tau_env_analytic": tau_env,
    }
    return {"body": body, "meta": bundle_meta_carry}


def _slug(substrate: str, cell_name: str) -> str:
    # cell name pattern: glass__T0.500__spin-flip.json -> glass__T0.500__spin-flip
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


def run(library_root: Path = DEFAULT_LIBRARY, output_root: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)

    cells: list[Path] = _cell_paths(library_root)
    if not cells:
        raise SystemExit(f"no library cells found under {library_root}")

    per_class_cells: dict[str, list[dict[str, Any]]] = {}
    per_class_uploads: dict[str, list[dict[str, Any]]] = {}
    failures: list[dict[str, Any]] = []
    successes = 0

    for cell_path in cells:
        substrate = cell_path.parent.name
        try:
            result = conform_cell(cell_path, substrate)
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
    }
    summary_path = output_root / "_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSummary: {successes}/{len(cells)} cells; "
          f"{len(profile_paths)} driver profiles; "
          f"summary at {summary_path.relative_to(output_root.parent)}")
    return summary


if __name__ == "__main__":
    run()
