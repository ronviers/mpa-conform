"""Tests for the per-substrate baseline + percentile-lookup apparatus."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.calibration import baselines, percentile


# --- baselines.compute_baselines_from_sweep ------------------------------

def _synthetic_sweep_df() -> pd.DataFrame:
    """Two substrates, two paths, mix of intensities + statuses."""
    rows = []
    for substrate in ("glass", "quantum"):
        for path in ("two_stage_inversion", "lens_solver_prior"):
            # 100 known-good baseline rows: status ok, low intensity
            for i in range(100):
                rows.append({
                    "substrate": substrate, "path": path,
                    "noise_model": "gaussian", "intensity": 0.001,
                    "seed_idx": 0, "cell_id": f"cell_{i}",
                    "status": "ok",
                    "residual_final": 0.05 + 0.001 * i,           # 0.05 .. 0.15
                    "regime_confidence": 0.5 + 0.004 * i,         # 0.5 .. 0.9
                    "predictor_gap": None if path == "two_stage_inversion" else 0.01 * i,
                })
            # 50 high-noise rows that should NOT count toward baseline
            for i in range(50):
                rows.append({
                    "substrate": substrate, "path": path,
                    "noise_model": "gaussian", "intensity": 0.5,
                    "seed_idx": 0, "cell_id": f"cell_noisy_{i}",
                    "status": "ok",
                    "residual_final": 5.0,
                    "regime_confidence": 0.99,
                    "predictor_gap": None if path == "two_stage_inversion" else 2.0,
                })
            # 5 error rows that should be excluded
            for i in range(5):
                rows.append({
                    "substrate": substrate, "path": path,
                    "noise_model": "gaussian", "intensity": 0.01,
                    "seed_idx": 0, "cell_id": f"cell_err_{i}",
                    "status": "error",
                    "residual_final": None, "regime_confidence": None,
                    "predictor_gap": None,
                })
    return pd.DataFrame(rows)


def test_filter_baseline_rows_excludes_high_noise_and_errors():
    df = _synthetic_sweep_df()
    filtered = baselines._filter_baseline_rows(df)
    assert (filtered["status"] == "ok").all()
    assert (filtered["intensity"] <= baselines.LOW_NOISE_CEILING).all()
    # 100 ok rows per (substrate, path) at intensity=0.001 -> 2 substrates x 2 paths = 400
    assert len(filtered) == 400


def test_compute_baselines_writes_one_json_per_substrate(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    written = baselines.compute_baselines_from_sweep(parquet_path, out_root)
    assert set(written.keys()) == {"glass", "quantum"}
    for sub, p in written.items():
        assert p.is_file()
        body = json.loads(p.read_text())
        assert body["substrate"] == sub
        assert body["schema_version"] == baselines.SCHEMA_VERSION
        assert set(body["paths"].keys()) == {"two_stage_inversion", "lens_solver_prior"}


def test_baseline_predictor_gap_is_null_for_two_stage(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    body = json.loads((out_root / "glass.json").read_text())
    assert body["paths"]["two_stage_inversion"]["fields"]["predictor_gap"] is None
    assert body["paths"]["lens_solver_prior"]["fields"]["predictor_gap"] is not None


def test_baseline_percentiles_are_monotone(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    body = json.loads((out_root / "glass.json").read_text())
    rf = body["paths"]["two_stage_inversion"]["fields"]["residual_final"]
    keys = sorted(rf.keys())
    vals = [rf[k] for k in keys]
    assert vals == sorted(vals), f"percentile values not monotone: {dict(zip(keys, vals))}"


# --- percentile.percentile_of --------------------------------------------

def test_percentile_returns_none_when_no_baseline_file(tmp_path):
    percentile.clear_cache()
    out = percentile.load_baseline("nonexistent_substrate", tmp_path)
    assert out is None
    pct = percentile.percentile_of(0.05, "residual_final", "two_stage_inversion", out)
    assert pct is None


def test_percentile_returns_none_for_none_value(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    assert percentile.percentile_of(None, "residual_final", "two_stage_inversion", b) is None


def test_percentile_returns_none_for_field_not_in_path(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    # two_stage_inversion has no predictor_gap baseline
    pct = percentile.percentile_of(0.5, "predictor_gap", "two_stage_inversion", b)
    assert pct is None


def test_percentile_below_p01_returns_zero(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    # residual_final baseline is 0.05..0.15; a value way below should be 0.0
    pct = percentile.percentile_of(0.001, "residual_final", "two_stage_inversion", b)
    assert pct == 0.0


def test_percentile_above_p99_returns_one(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    # residual_final baseline is 0.05..0.15; a value way above should be 1.0
    pct = percentile.percentile_of(10.0, "residual_final", "two_stage_inversion", b)
    assert pct == 1.0


def test_percentile_at_median_returns_near_half(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    body = json.loads((out_root / "glass.json").read_text())
    p50_val = body["paths"]["two_stage_inversion"]["fields"]["residual_final"]["p50"]
    pct = percentile.percentile_of(p50_val, "residual_final", "two_stage_inversion", b)
    # Should land near 0.5 (the p50 percentile)
    assert 0.45 < pct < 0.55


def test_percentiles_for_diagnostics_returns_all_fields(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    b = percentile.load_baseline("glass", out_root)
    diag = {
        "residual_final": 0.10,
        "regime_confidence": 0.70,
        "predictor_gap": None,
    }
    out = percentile.percentiles_for_diagnostics(diag, "two_stage_inversion", b)
    assert set(out.keys()) == {"residual_final", "regime_confidence", "predictor_gap"}
    assert out["residual_final"] is not None
    assert out["regime_confidence"] is not None
    assert out["predictor_gap"] is None  # not in baseline for this path


def test_load_baseline_is_cached(tmp_path):
    df = _synthetic_sweep_df()
    parquet_path = tmp_path / "sweep.parquet"
    df.to_parquet(parquet_path)
    out_root = tmp_path / "baselines"
    baselines.compute_baselines_from_sweep(parquet_path, out_root)
    percentile.clear_cache()
    a = percentile.load_baseline("glass", out_root)
    b = percentile.load_baseline("glass", out_root)
    assert a is b  # cache returns same instance
