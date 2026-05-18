"""Percentile lookup against a substrate's diagnostic baseline.

Loads the per-substrate baseline JSON written by baselines.py and turns
a raw diagnostic value into its percentile within the known-good
distribution for that (substrate, path, field).

Module-level cache so we don't re-parse JSON per call. Baselines change
rarely (when the library expands or solver changes), so caching forever
in-process is fine.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


DEFAULT_BASELINES_ROOT = Path("H:/mpa-central/library/baselines")


@dataclass(frozen=True)
class Baseline:
    substrate: str
    paths: dict[str, dict]  # path -> {n, fields: {field -> percentile_dict | None}}


_cache: dict[tuple[str, str], Optional[Baseline]] = {}


def load_baseline(substrate: str,
                  baselines_root: Path = DEFAULT_BASELINES_ROOT) -> Optional[Baseline]:
    """Load and cache the substrate's baseline. Returns None if no baseline
    file exists yet (new substrate — percentile lookups will return None)."""
    key = (substrate, str(baselines_root))
    if key in _cache:
        return _cache[key]
    path = baselines_root / f"{substrate}.json"
    if not path.is_file():
        _cache[key] = None
        return None
    body = json.loads(path.read_text(encoding="utf-8"))
    baseline = Baseline(substrate=substrate, paths=body.get("paths", {}))
    _cache[key] = baseline
    return baseline


def clear_cache() -> None:
    """For tests / after rewriting baselines on disk."""
    _cache.clear()


def percentile_of(value: Optional[float], field: str, path: str,
                  baseline: Optional[Baseline]) -> Optional[float]:
    """Return value's percentile in the baseline's (path, field) distribution,
    as a number in [0, 1]. Returns None when:
      - value is None or non-finite
      - baseline is None (no baseline for this substrate yet)
      - the (path, field) has no percentile data (not applicable to this path)
    Below p01 -> 0.0; above p99 -> 1.0; linearly interpolated otherwise.
    """
    if value is None or not np.isfinite(float(value)):
        return None
    if baseline is None:
        return None

    path_block = baseline.paths.get(path)
    if path_block is None:
        return None
    field_block = path_block.get("fields", {}).get(field)
    if field_block is None:
        return None

    # field_block: {"p01": ..., "p05": ..., ..., "p99": ...}
    keys = sorted(field_block.keys())  # 'p01', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99'
    pcts = np.asarray([float(k[1:]) / 100.0 for k in keys])
    vals = np.asarray([float(field_block[k]) for k in keys])

    v = float(value)
    if v <= vals[0]:
        return 0.0
    if v >= vals[-1]:
        return 1.0
    return float(np.interp(v, vals, pcts))


def percentiles_for_diagnostics(diag_dict: dict, path: str,
                                baseline: Optional[Baseline]) -> dict[str, Optional[float]]:
    """Compute percentiles for all three diagnostic fields at once.
    Returns {field: percentile_or_None}."""
    return {
        field: percentile_of(diag_dict.get(field), field, path, baseline)
        for field in ("residual_final", "regime_confidence", "predictor_gap")
    }
