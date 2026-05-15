"""Acceptance test for the curator-path post-processor (bootstrap §5).

Runs the walker, then validates every emitted bundle and driver profile
against its authoritative schema. Sufficient for first-session acceptance;
deeper integration tests (loading into mpa-auditor as a fixture) live as
a manual smoke test in the README.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_BUNDLE = REPO_ROOT / "schema" / "declaration-bundle.v0.1.json"
SCHEMA_DRIVER = Path("H:/mpa-atlas/schema/driver-profile.v0.2.json")
SCHEMA_DATA_UPLOAD = Path("H:/mpa-auditor/contracts/05-data-upload.schema.json")
SEED_CORPUS = REPO_ROOT / "output" / "seed-corpus"


def _validator(schema_path: Path) -> jsonschema.protocols.Validator:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _bundle_to_data_upload(body: dict) -> dict:
    """The auditor expects a contract-05 DataUpload (upload_id, timestamp,
    provenance, columns, n_rows, data, original_hash, validated). The
    declaration_bundle is a richer object; this helper projects it down
    so the smoke-test in mpa-auditor (drop via FILE_DROPPED) can use it
    without bundle-import logic landing first.
    """
    obs = body["observable"]
    return {
        "upload_id": body["bundle_id"],
        "timestamp": body["signature"]["signed_at"],
        "substrate_class": body["substrate_class"],
        "provenance": body["provenance"],
        "columns": [
            {k: v for k, v in c.items() if k in {"name", "units", "description", "physical_quantity", "uncertainty_column", "coverage_range", "validity_range", "range_source"}}
            for c in body["columns"]
        ],
        "data": obs["data"],
        "n_rows": obs["n_rows"],
        "original_hash": body["signature"]["manifest_hash"],
        "validated": True,
        "tier": body["tier"],
        "validation": {"status": "curated"},
        "declaration_trail": body["declaration_trail"],
    }


def test_all_bundles_validate():
    v = _validator(SCHEMA_BUNDLE)
    n = 0
    for class_dir in SEED_CORPUS.iterdir():
        if not class_dir.is_dir():
            continue
        for bundle_path in sorted(class_dir.glob("*.bundle.json")):
            body = json.loads(bundle_path.read_text(encoding="utf-8"))
            v.validate(body)
            n += 1
    assert n == 60, f"expected 60 bundles, got {n}"
    print(f"OK: {n} bundles validated against declaration-bundle.v0.1")


def test_all_driver_profiles_validate():
    v = _validator(SCHEMA_DRIVER)
    n = 0
    for class_dir in SEED_CORPUS.iterdir():
        if not class_dir.is_dir():
            continue
        profile_path = class_dir / "driver-profile.json"
        if not profile_path.exists():
            continue
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        v.validate(profile)
        n += 1
    assert n == 3, f"expected 3 driver profiles, got {n}"
    print(f"OK: {n} driver profiles validated against driver-profile.v0.2")


def test_bundles_project_to_contract_05():
    v = _validator(SCHEMA_DATA_UPLOAD)
    n = 0
    # Sample one bundle from each class.
    for class_dir in SEED_CORPUS.iterdir():
        if not class_dir.is_dir():
            continue
        for bundle_path in sorted(class_dir.glob("*.bundle.json"))[:1]:
            body = json.loads(bundle_path.read_text(encoding="utf-8"))
            data_upload = _bundle_to_data_upload(body)
            v.validate(data_upload)
            n += 1
    assert n == 3, f"expected to sample 3 (one per class), got {n}"
    print(f"OK: {n} bundles project to valid contract-05 DataUpload")


def test_summary_run_clean():
    summary_path = SEED_CORPUS / "_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["cells_failed"] == 0, f"failures: {summary['failures']}"
    assert summary["cells_succeeded"] == 60
    print("OK: summary reports 60/60 cells, 0 failures")


if __name__ == "__main__":
    test_summary_run_clean()
    test_all_bundles_validate()
    test_all_driver_profiles_validate()
    test_bundles_project_to_contract_05()
    print("\nAll acceptance tests passed.")
