"""Smoke tests for v2 FitDiagnostics emitted by the two-stage inversion path."""
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

from mpa_lens_solver import FitDiagnostics

from conformer.compute import gfdr_model, inversion


def _synthetic_rows(chit_true: float) -> list[dict]:
    locus = gfdr_model.generate_locus(chit_true)
    return [
        {"tau": float(t), "C": float(c), "chi": float(ch)}
        for t, c, ch in zip(locus["tau"], locus["C"], locus["chi"])
    ]


def test_invert_populates_fit_diagnostics():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    assert result.fit_diagnostics is not None
    assert isinstance(result.fit_diagnostics, FitDiagnostics)


def test_diagnostics_source_is_two_stage_inversion():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    assert result.fit_diagnostics.source == "two_stage_inversion"


def test_diagnostics_predictor_gap_always_none_for_two_stage():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    assert result.fit_diagnostics.predictor_gap is None


def test_diagnostics_n_passes_two_when_stage2_ran():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    assert result.fit_diagnostics.n_passes == 2


def test_diagnostics_n_passes_one_when_stage2_skipped():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows, skip_stage2=True)
    assert result.fit_diagnostics.n_passes == 1
    assert result.fit_diagnostics.regime_confidence is None


def test_residual_final_is_raw_value():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    assert result.fit_diagnostics.residual_final == pytest.approx(result.locus_residual)


def test_regime_confidence_in_unit_interval_when_stage2_ran():
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    conf = result.fit_diagnostics.regime_confidence
    assert conf is not None
    assert 0.0 <= conf <= 1.0


def test_regime_confidence_high_for_chit_far_from_boundary():
    """chit_true = -1.5 sits deep in the deep_c regime, far from any
    boundary. Stage 2 candidates should all share the same regime -> off
    fraction ~ 0 -> confidence ~ 1.0 (fully pinned)."""
    rows = _synthetic_rows(-1.5)
    result = inversion.invert(rows)
    assert result.fit_diagnostics.regime_confidence == pytest.approx(1.0, abs=0.01)


def test_diagnostics_to_dict_is_json_serializable():
    import json
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    json.dumps(result.fit_diagnostics.to_dict())


def test_diagnostics_v2_field_names():
    """Lock the v2 field names. v1 names (residual_plateau, regime_stability,
    predictor_agreement) must NOT appear in the dict."""
    rows = _synthetic_rows(0.3)
    result = inversion.invert(rows)
    d = result.fit_diagnostics.to_dict()
    assert set(d.keys()) == {
        "residual_final", "regime_confidence", "predictor_gap",
        "source", "n_passes",
    }
