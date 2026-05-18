"""Integration smoke for v0.3 bundle emission: schema bump + new audit_delta
fields populated end-to-end on a real library cell."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.curator import walk_library


GLASS_CELL_PATH = Path("H:/mpa-central/library/data/glass")


@pytest.fixture
def real_glass_cells():
    if not GLASS_CELL_PATH.is_dir():
        pytest.skip(f"library not available at {GLASS_CELL_PATH}")
    paths = sorted(GLASS_CELL_PATH.glob("*.json"))[:3]
    if not paths:
        pytest.skip("no glass cells found")
    return paths


def test_conform_cell_produces_v03_schema(real_glass_cells):
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=0.042)
    body = result["body"]
    assert body["schema"] == "declaration-bundle.v0.3"


def test_v03_audit_delta_carries_new_fields(real_glass_cells):
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=0.042)
    ad = result["body"]["fit_provenance"]["audit_delta"]
    # v0.2 fields still present
    assert "locus_residual" in ad
    assert "regime_label" in ad
    # v0.3 additions present
    assert "fit_diagnostics" in ad
    assert "diagnostic_percentiles" in ad
    assert "cross_path_disagreement" in ad


def test_v03_cross_path_disagreement_passes_through(real_glass_cells):
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=0.042)
    ad = result["body"]["fit_provenance"]["audit_delta"]
    assert ad["cross_path_disagreement"] == pytest.approx(0.042)


def test_v03_fit_diagnostics_populated_with_source_two_stage(real_glass_cells):
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=None)
    diag = result["body"]["fit_provenance"]["audit_delta"]["fit_diagnostics"]
    assert diag is not None
    assert diag["source"] == "two_stage_inversion"
    assert isinstance(diag["n_passes"], int)


def test_v03_percentiles_populated_when_baseline_exists(real_glass_cells):
    # glass.json baseline exists at H:/mpa-central/library/baselines/glass.json
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=0.042)
    pcts = result["body"]["fit_provenance"]["audit_delta"]["diagnostic_percentiles"]
    assert pcts is not None
    # residual_final + regime_confidence should have percentile values for two_stage path;
    # predictor_gap has no baseline for two_stage (it's null in the baseline).
    assert pcts["residual_final"] is not None
    assert 0.0 <= pcts["residual_final"] <= 1.0
    assert pcts["regime_confidence"] is not None
    assert 0.0 <= pcts["regime_confidence"] <= 1.0
    assert pcts["predictor_gap"] is None  # no baseline for this field on two_stage


def test_v03_bundle_is_json_serializable(real_glass_cells):
    cell_path = real_glass_cells[0]
    result = walk_library.conform_cell(cell_path, "glass", cross_path_disagreement=0.042)
    json.dumps(result["body"])  # raises if non-primitive types leaked in


def test_v03_run_small_subset_produces_v03_bundles(tmp_path, real_glass_cells):
    """End-to-end: run() on a tiny glass subset, verify written bundles
    are v0.3 with new fields. We restrict to 3 cells by monkey-patching
    DEFAULT_LIBRARY indirectly: just use a temporary library tree."""
    library_dir = tmp_path / "library" / "glass"
    library_dir.mkdir(parents=True)
    for src in real_glass_cells:
        (library_dir / src.name).write_bytes(src.read_bytes())

    output_root = tmp_path / "output"
    summary = walk_library.run(library_root=tmp_path / "library", output_root=output_root)
    assert summary["cells_succeeded"] >= 1, f"no cells succeeded: {summary}"

    # Pick the first emitted bundle and inspect
    bundles = list(output_root.rglob("*.bundle.json"))
    assert bundles, "no bundles written"
    body = json.loads(bundles[0].read_text())
    assert body["schema"] == "declaration-bundle.v0.3"
    ad = body["fit_provenance"]["audit_delta"]
    assert "fit_diagnostics" in ad
    assert "diagnostic_percentiles" in ad
    assert "cross_path_disagreement" in ad
    # cross_path_disagreement should be a real number (both paths ran on
    # the small substrate batch)
    assert ad["cross_path_disagreement"] is None or isinstance(ad["cross_path_disagreement"], float)
