"""Noise models for the diagnostic sweep.

Seven structured pathologies plus a clean passthrough. Each function:
    (rows: list[dict], intensity: float, rng_seed: int) -> list[dict]

intensity=0 always returns a clean copy (passthrough). The intensity
scale is comparable across models — at intensity=1.0 each model produces
"order of dynamic range" degradation, give or take. Higher intensities
are explicitly past-the-cliff territory.

All models are seeded; same (rows, intensity, rng_seed) -> byte-identical
output. Rows are not mutated in place — every model returns a new list of
new dicts.

Models:
  clean                  - intensity ignored; copy
  gaussian               - additive Gaussian on (C, chi)
  drift                  - low-freq sinusoidal trend on (C, chi)
  quantization           - round (C, chi) to fewer significant figures
  row_dropout            - remove a fraction of rows
  calibration_bias       - constant offset on (C, chi)
  tau_jitter             - multiplicative jitter on tau
  multimodal_contamination - blend row sequence with its reverse
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np


def _copy_rows(rows: list[dict]) -> list[dict]:
    return [dict(r) for r in rows]


def _dyn_range(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if key in r]
    if not vals:
        return 1.0
    spread = float(max(vals) - min(vals))
    return spread if spread > 0 else 1.0


def clean(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Passthrough. intensity ignored — included so the dispatch is uniform."""
    return _copy_rows(rows)


def gaussian(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Additive Gaussian on C and chi with sigma = intensity * dynamic_range."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    rng = np.random.default_rng(rng_seed)
    out = _copy_rows(rows)
    sigma_C = float(intensity) * _dyn_range(rows, "C")
    sigma_chi = float(intensity) * _dyn_range(rows, "chi")
    for r in out:
        r["C"] = float(r["C"] + rng.normal(0.0, sigma_C))
        r["chi"] = float(r["chi"] + rng.normal(0.0, sigma_chi))
    return out


def drift(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Single-cycle sinusoid added to (C, chi). amp = intensity * dynamic_range,
    phase = uniform random per rng_seed. Mimics slow sensor drift."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    rng = np.random.default_rng(rng_seed)
    amp_C = float(intensity) * _dyn_range(rows, "C")
    amp_chi = float(intensity) * _dyn_range(rows, "chi")
    phase = float(rng.uniform(0.0, 2 * math.pi))
    n = len(rows)
    out = _copy_rows(rows)
    for i, r in enumerate(out):
        t = i / max(1, n - 1)
        wave = math.sin(2 * math.pi * t + phase)
        r["C"] = float(r["C"] + amp_C * wave)
        r["chi"] = float(r["chi"] + amp_chi * wave)
    return out


def quantization(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Round C and chi to (8 * (1 - intensity)) significant figures.
    intensity=0 -> 8 sig figs (effectively no rounding); intensity=1 -> 0 sig
    figs (clamp to 1)."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    sig_figs = max(1, int(round(8.0 * (1.0 - min(1.0, float(intensity))))))
    out = _copy_rows(rows)
    for r in out:
        for key in ("C", "chi"):
            v = float(r[key])
            if v == 0.0:
                continue
            decimals = sig_figs - int(math.floor(math.log10(abs(v)))) - 1
            r[key] = round(v, decimals)
    return out


def row_dropout(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Drop each row independently with probability = min(1, intensity).
    Returns possibly-empty list; callers must handle len < 2 downstream."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    rng = np.random.default_rng(rng_seed)
    keep_mask = rng.uniform(size=len(rows)) > min(1.0, float(intensity))
    return [dict(r) for i, r in enumerate(rows) if keep_mask[i]]


def calibration_bias(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Constant offset on C and chi. Offset = uniform(-1, 1) * intensity *
    dynamic_range. Same offset across all rows (constant bias, not noise)."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    rng = np.random.default_rng(rng_seed)
    bias_C = float(rng.uniform(-1, 1)) * float(intensity) * _dyn_range(rows, "C")
    bias_chi = float(rng.uniform(-1, 1)) * float(intensity) * _dyn_range(rows, "chi")
    out = _copy_rows(rows)
    for r in out:
        r["C"] = float(r["C"] + bias_C)
        r["chi"] = float(r["chi"] + bias_chi)
    return out


def tau_jitter(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Multiplicative Gaussian jitter on tau. Each row gets tau * max(0.01,
    1 + N(0, intensity)). Mimics irregular sampling."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    rng = np.random.default_rng(rng_seed)
    out = _copy_rows(rows)
    for r in out:
        jitter = float(rng.normal(0.0, float(intensity)))
        r["tau"] = float(r["tau"] * max(0.01, 1.0 + jitter))
    return out


def multimodal_contamination(rows: list[dict], intensity: float, rng_seed: int) -> list[dict]:
    """Blend each row with the row at the mirrored index, weight = intensity.
    Mimics two-process contamination without requiring a second cell. At
    intensity=1 the sequence is fully reversed."""
    if intensity == 0 or not rows:
        return _copy_rows(rows)
    out = _copy_rows(rows)
    n = len(rows)
    w = min(1.0, float(intensity))
    for i, r in enumerate(out):
        partner = rows[n - 1 - i]
        r["C"] = float((1 - w) * r["C"] + w * partner["C"])
        r["chi"] = float((1 - w) * r["chi"] + w * partner["chi"])
    return out


NOISE_MODELS: dict[str, Callable[[list[dict], float, int], list[dict]]] = {
    "clean": clean,
    "gaussian": gaussian,
    "drift": drift,
    "quantization": quantization,
    "row_dropout": row_dropout,
    "calibration_bias": calibration_bias,
    "tau_jitter": tau_jitter,
    "multimodal_contamination": multimodal_contamination,
}
