"""Tests for cross-path disagreement utility."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.calibration import cross_path


def _glass_cell(T: float, gt: str = "c") -> dict:
    return {
        "operating_point": {
            "label": f"T={T:.3f}", "scenario": None, "h_field": 0.1,
            "T": T, "p_base": None, "delta_p": None, "gt": gt,
        },
    }


def test_disagreement_none_when_either_input_none():
    assert cross_path.cross_path_disagreement(None, 0.5) is None
    assert cross_path.cross_path_disagreement(0.5, None) is None
    assert cross_path.cross_path_disagreement(None, None) is None


def test_disagreement_returns_abs_difference():
    assert cross_path.cross_path_disagreement(0.5, 0.3) == pytest.approx(0.2)
    assert cross_path.cross_path_disagreement(0.3, 0.5) == pytest.approx(0.2)


def test_disagreement_zero_when_paths_agree():
    assert cross_path.cross_path_disagreement(0.7, 0.7) == 0.0


def test_lens_solver_prior_chits_for_batch_returns_per_label_dict():
    cells = [_glass_cell(0.2), _glass_cell(0.5), _glass_cell(1.1, gt="s")]
    out = cross_path.lens_solver_prior_chits_for_batch(
        "glass", cells, "spin-flip", max_passes=0,
    )
    assert set(out.keys()) == {"T=0.200", "T=0.500", "T=1.100"}
    for label, chit in out.items():
        assert isinstance(chit, float)


def test_lens_solver_prior_chits_for_batch_empty_returns_empty():
    out = cross_path.lens_solver_prior_chits_for_batch(
        "glass", [], "spin-flip",
    )
    assert out == {}


def test_cross_path_disagreements_for_batch_combines_inputs():
    cells = [_glass_cell(0.2), _glass_cell(0.5)]
    two_stage = {"T=0.200": 0.95, "T=0.500": 0.55}
    out = cross_path.cross_path_disagreements_for_batch(
        "glass", cells, "spin-flip", two_stage, max_passes=0,
    )
    assert set(out.keys()) == {"T=0.200", "T=0.500"}
    # The prior fit for glass T=0.2 should be Tc - T = 0.9
    # So disagreement = |0.95 - 0.9| = 0.05 (roughly)
    assert out["T=0.200"] is not None
    assert 0.0 <= out["T=0.200"] < 1.0


def test_cross_path_disagreements_passes_through_none():
    cells = [_glass_cell(0.2), _glass_cell(0.5)]
    two_stage = {"T=0.200": None, "T=0.500": 0.55}
    out = cross_path.cross_path_disagreements_for_batch(
        "glass", cells, "spin-flip", two_stage, max_passes=0,
    )
    assert out["T=0.200"] is None
    assert out["T=0.500"] is not None
