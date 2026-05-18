"""Unit tests for noise models + tiny end-to-end sweep verify."""
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

from conformer.calibration import noise_models, sweep


_BASE_ROWS = [
    {"tau": 0.5, "C": 0.95, "chi": 0.05},
    {"tau": 1.0, "C": 0.80, "chi": 0.20},
    {"tau": 2.0, "C": 0.60, "chi": 0.40},
    {"tau": 4.0, "C": 0.40, "chi": 0.60},
    {"tau": 8.0, "C": 0.20, "chi": 0.80},
]


# --- noise models: clean passthrough + determinism + intensity=0 -----

@pytest.mark.parametrize("name", list(noise_models.NOISE_MODELS))
def test_noise_model_intensity_zero_is_passthrough(name):
    fn = noise_models.NOISE_MODELS[name]
    out = fn(_BASE_ROWS, 0.0, rng_seed=42)
    assert len(out) == len(_BASE_ROWS)
    for a, b in zip(_BASE_ROWS, out):
        assert a["tau"] == pytest.approx(b["tau"])
        assert a["C"] == pytest.approx(b["C"])
        assert a["chi"] == pytest.approx(b["chi"])


@pytest.mark.parametrize("name", [
    n for n in noise_models.NOISE_MODELS if n != "clean"
])
def test_noise_model_deterministic_same_seed(name):
    fn = noise_models.NOISE_MODELS[name]
    a = fn(_BASE_ROWS, 0.1, rng_seed=42)
    b = fn(_BASE_ROWS, 0.1, rng_seed=42)
    assert len(a) == len(b)
    for ra, rb in zip(a, b):
        for k in ra:
            assert ra[k] == pytest.approx(rb[k])


@pytest.mark.parametrize("name", [
    "gaussian", "drift", "calibration_bias", "tau_jitter",
])
def test_noise_model_does_not_mutate_input(name):
    fn = noise_models.NOISE_MODELS[name]
    before = [dict(r) for r in _BASE_ROWS]
    fn(_BASE_ROWS, 0.5, rng_seed=42)
    for a, b in zip(_BASE_ROWS, before):
        assert a == b


def test_row_dropout_reduces_count_at_intensity_one():
    out = noise_models.row_dropout(_BASE_ROWS, 1.0, rng_seed=0)
    # intensity=1 -> drop probability=1 -> almost certainly empty
    assert len(out) <= len(_BASE_ROWS)


def test_quantization_reduces_sig_figs_at_high_intensity():
    out = noise_models.quantization(_BASE_ROWS, 1.0, rng_seed=0)
    for r in out:
        # 1 sig fig means values like 0.9 or 0.2, not 0.95 or 0.20
        assert r["C"] != pytest.approx(_BASE_ROWS[0]["C"], abs=0.01) or r["C"] == _BASE_ROWS[0]["C"]


def test_multimodal_contamination_reverses_at_intensity_one():
    out = noise_models.multimodal_contamination(_BASE_ROWS, 1.0, rng_seed=0)
    reversed_C = [r["C"] for r in reversed(_BASE_ROWS)]
    out_C = [r["C"] for r in out]
    for a, b in zip(out_C, reversed_C):
        assert a == pytest.approx(b)


# --- tiny end-to-end sweep ---------------------------------------------

def test_tiny_sweep_lens_solver_paths_run_clean(tmp_path):
    """Locks the lens-solver branch of _run_worker against silent v1/v2
    field-name drift. The two_stage_inversion test below uses a different
    branch — they have to be exercised separately."""
    cfg = sweep.SweepConfig(
        substrates=("glass",),
        paths=("lens_solver_prior", "lens_solver_bootstrap"),
        noise_models=("gaussian",),
        intensities=(0.0, 0.1),
        n_seeds=1,
        cell_limit_per_substrate=2,
        output_root_str=str(tmp_path),
        per_worker_timeout_s=120.0,
        n_workers=2,
        max_passes_lens_solver=3,
    )
    parquet_path = sweep.run_sweep(cfg, label="lens-smoke")
    import pandas as pd
    df = pd.read_parquet(parquet_path)
    error_rows = df[df["status"] == "error"]
    assert len(error_rows) == 0, (
        f"lens-solver paths errored:\n{error_rows['error_msg'].iloc[0][:300]}"
    )
    assert set(df["source"].dropna().unique()) <= {
        "lens_solver_prior", "lens_solver_bootstrap",
    }


def test_tiny_sweep_runs_and_writes_parquet(tmp_path):
    """One-off integration smoke test: tiny matrix, real library, parquet
    produced with expected columns and row count."""
    cfg = sweep.SweepConfig(
        substrates=("glass",),
        paths=("two_stage_inversion",),
        noise_models=("gaussian",),
        intensities=(0.0, 0.1),
        n_seeds=1,
        cell_limit_per_substrate=2,
        output_root_str=str(tmp_path),
        per_worker_timeout_s=120.0,
        n_workers=2,
        max_passes_lens_solver=5,
    )
    parquet_path = sweep.run_sweep(cfg, label="tiny")
    assert parquet_path.exists()
    assert parquet_path.suffix == ".parquet"

    import pandas as pd
    df = pd.read_parquet(parquet_path)

    expected_cols = {
        "substrate", "path", "noise_model", "intensity", "seed_idx", "cell_id",
        "fit_chit", "fit_residual", "gt_chit", "gt_error",
        "residual_final", "regime_confidence", "predictor_gap",
        "n_passes", "source", "wall_time_s", "status", "error_msg",
    }
    assert expected_cols.issubset(set(df.columns))

    # Phase A: 1 substrate x 1 path x 2 cells = 2 outcomes
    # Phase B: 1 substrate x 1 path x 1 noise x 2 intensities x 1 seed x 2 cells = 4 outcomes
    # Total expected: 6
    assert len(df) == 6

    # Phase A: noise_model='clean'
    phase_a = df[df["noise_model"] == "clean"]
    assert len(phase_a) == 2
    assert all(phase_a["status"] == "ok")
    assert all(phase_a["gt_chit"].isna())  # phase A has no GT (it defines GT)

    # Phase B: gaussian noise; intensity=0.0 should still fit and have GT
    phase_b = df[df["noise_model"] == "gaussian"]
    assert len(phase_b) == 4
    assert all(phase_b["status"] == "ok")
    assert all(phase_b["gt_chit"].notna())
    assert all(phase_b["source"] == "two_stage_inversion")

    # FitDiagnostics shape: two_stage always populates source + n_passes
    assert all(phase_b["n_passes"].notna())

    # Manifest written
    manifest_path = parquet_path.parent / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["total_rows"] == 6
    assert manifest["config"]["substrates"] == ["glass"]
