"""Per-substrate diagnostic baselines.

For each (substrate, path, diagnostic_field), compute the percentile
distribution of fit_diagnostics values across known-good fits. The
substrate library IS the calibration set; new substrates extend it.

Known-good = rows from a sweep parquet with status='ok' AND noise
intensity below LOW_NOISE_CEILING (effectively the clean/near-clean
fits). This gives ~5-10x more samples than Phase A alone while still
representing "the fit when nothing is wrong."

Output: one JSON per substrate at the baselines_root:
  {
    "schema_version": "1.0",
    "substrate": "glass",
    "source_parquet": "...",
    "computed_at": "ISO-8601",
    "n_samples_total": 1280,
    "low_noise_ceiling": 0.01,
    "paths": {
      "two_stage_inversion": {
        "n": 420,
        "fields": {
          "residual_final":    {"p01": ..., "p10": ..., "p50": ..., "p90": ..., "p99": ...},
          "regime_confidence": {...},
          "predictor_gap":     null
        }
      },
      ...
    }
  }

Re-runnable: re-run when the library adds substrates or the sweep
re-runs after a solver change. The percentile interpolation downstream
uses np.interp, so any percentile set is sufficient.

CLI:
  python -m conformer.calibration.baselines [--parquet PATH] [--baselines-root PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


DEFAULT_BASELINES_ROOT = Path("H:/mpa-central/library/baselines")
DEFAULT_SWEEP_PARQUET = Path(
    "H:/mpa-conform/output/calibration/20260518-132746-full-3sub/sweep.parquet"
)

# Below this intensity we consider the fit "essentially clean" and use it
# as known-good baseline material. 0.01 = 1% of dynamic range — well below
# the noise floor where catastrophic failures start.
LOW_NOISE_CEILING = 0.01

# Percentile points stored per field. Downstream np.interp uses these
# directly. p01/p99 are kept for the auditor's "extreme outlier" badge.
PERCENTILES_TO_STORE = (1.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 99.0)

DIAGNOSTIC_FIELDS = ("residual_final", "regime_confidence", "predictor_gap")

SCHEMA_VERSION = "1.0"


def _filter_baseline_rows(sweep_df: pd.DataFrame) -> pd.DataFrame:
    """Known-good = status ok + intensity below the low-noise ceiling.

    Phase A rows (noise_model == 'clean') have intensity = 0 and are
    included. Phase B rows with intensity in (0, LOW_NOISE_CEILING] are
    also included — same substrate, same path, near-zero noise.
    """
    return sweep_df[
        (sweep_df["status"] == "ok")
        & (sweep_df["intensity"] <= LOW_NOISE_CEILING)
    ].copy()


def _percentiles_for_field(series: pd.Series) -> Optional[dict[str, float]]:
    """Compute the stored percentile set, or None if the series is empty
    or fully None (the field doesn't apply to this path)."""
    finite = series.replace([np.inf, -np.inf], np.nan).dropna()
    if finite.empty:
        return None
    arr = finite.to_numpy()
    pcts = np.percentile(arr, list(PERCENTILES_TO_STORE))
    return {f"p{int(p):02d}": float(v) for p, v in zip(PERCENTILES_TO_STORE, pcts)}


def _baseline_for_substrate(sub_df: pd.DataFrame, substrate: str,
                            source_parquet: str) -> dict:
    """Build the per-substrate baseline JSON object."""
    paths_out: dict[str, dict] = {}
    for path, pg in sub_df.groupby("path"):
        fields_out: dict[str, Optional[dict[str, float]]] = {}
        for field in DIAGNOSTIC_FIELDS:
            if field not in pg.columns:
                fields_out[field] = None
                continue
            fields_out[field] = _percentiles_for_field(pg[field])
        paths_out[path] = {
            "n": int(len(pg)),
            "fields": fields_out,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "substrate": substrate,
        "source_parquet": source_parquet,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "n_samples_total": int(len(sub_df)),
        "low_noise_ceiling": LOW_NOISE_CEILING,
        "percentile_points": list(PERCENTILES_TO_STORE),
        "paths": paths_out,
    }


def compute_baselines_from_sweep(parquet_path: Path,
                                 baselines_root: Path) -> dict[str, Path]:
    """Read sweep parquet, compute per-substrate baselines, write JSONs.
    Returns {substrate: path_written}."""
    sweep_df = pd.read_parquet(parquet_path)
    print(f"loaded sweep: {len(sweep_df)} rows from {parquet_path}")

    baseline_df = _filter_baseline_rows(sweep_df)
    print(f"known-good baseline rows: {len(baseline_df)} "
          f"(status=ok and intensity<={LOW_NOISE_CEILING})")

    baselines_root.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for substrate, sub_df in baseline_df.groupby("substrate"):
        baseline = _baseline_for_substrate(sub_df, substrate, str(parquet_path))
        out_path = baselines_root / f"{substrate}.json"
        out_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
        written[substrate] = out_path
        for path, body in baseline["paths"].items():
            field_summary = ", ".join(
                f"{k}=p50:{body['fields'][k]['p50']:.3f}" if body['fields'][k] else f"{k}=null"
                for k in DIAGNOSTIC_FIELDS
            )
            print(f"  {substrate}/{path}: n={body['n']}  {field_summary}")
        print(f"  -> {out_path}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", type=str, default=str(DEFAULT_SWEEP_PARQUET))
    parser.add_argument("--baselines-root", type=str, default=str(DEFAULT_BASELINES_ROOT))
    args = parser.parse_args()
    compute_baselines_from_sweep(Path(args.parquet), Path(args.baselines_root))


if __name__ == "__main__":
    main()
