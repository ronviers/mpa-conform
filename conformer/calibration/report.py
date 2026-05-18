"""Reporter for diagnostic-sweep parquets.

Reads a sweep.parquet, classifies each fit into TP/FN/FP/TN/HANG/ERROR
under a given threshold policy, and emits:
  - summary.md          : per-(path, noise_model) bin counts + headline FN rates
  - bins.csv            : full per-(path, noise_model) bin breakdown
  - scatter_<path>.png  : per-path 3-panel scatter (one panel per diagnostic
                          dimension) of (gt_error, diagnostic_value), colored
                          by noise_model, sized by intensity

Thresholds are the load-bearing knob. Defaults are pre-sweep guesses; the
report's whole point is to show whether they're sensible. Re-run the
reporter with different thresholds to re-classify the same sweep without
re-running it.

FN rate is the headline because FN = diagnostic missed a real failure,
which is the failure mode that matters most for downstream consumers.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
import pandas as pd


def _fmt_cell(v, floatfmt: str = ".3f") -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return format(float(v), floatfmt)
    return str(v)


def _df_to_md(df: pd.DataFrame, *, index: bool = False, floatfmt: str = ".3f") -> str:
    """Self-contained markdown table — avoids the tabulate dependency."""
    cols = list(df.columns)
    if index:
        idx_name = df.index.name or ""
        cols = [idx_name] + cols
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    rows = []
    for i, row in df.iterrows():
        cells = []
        if index:
            cells.append(str(i))
        for c in df.columns:
            cells.append(_fmt_cell(row[c], floatfmt))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows])


def _series_to_md(s: pd.Series, *, value_name: str = "count") -> str:
    name = s.name or value_name
    lines = [f"| {s.index.name or 'key'} | {name} |", "|---|---|"]
    for k, v in s.items():
        lines.append(f"| {k} | {_fmt_cell(v, '.0f')} |")
    return "\n".join(lines)


@dataclass(frozen=True)
class ThresholdPolicy:
    """Sweep-informed defaults (v2 metrics).

    Picked from the first glass-only calibration sweep
    (20260518-081524-glass-only):
      - regime_confidence: safe fits cluster around 0.6-0.7, catastrophic
        around 0.95-1.0. Threshold 0.85 splits cleanly.
      - residual_final: safe ~0.23, catastrophic ~0.43 (bootstrap).
        Threshold 0.30 catches catastrophic tails.
      - predictor_gap: in chit units; the regime-band half-width is ~0.3,
        so a gap exceeding 0.3 is "predictor disagreed by more than a
        regime band's worth."
    """
    gt_error_high: float = 0.3                # in chit units
    residual_final_flag: float = 0.30
    regime_confidence_flag: float = 0.85      # > 0.85 = score over-pinned
    predictor_gap_flag: float = 0.30          # > 0.3 chit units


def _classify_row(row: pd.Series, policy: ThresholdPolicy) -> str:
    if row["status"] == "hang":
        return "HANG"
    if row["status"] == "error":
        return "ERROR"
    if row["status"] != "ok":
        return "ERROR"  # empty_rows etc.

    gt = row["gt_error"]
    if pd.isna(gt):
        return "NO_GT"

    high_error = float(gt) > policy.gt_error_high

    # A fit "flags" if ANY diagnostic dimension exceeds its threshold.
    # None values are silent (don't flag), which is honest about what each
    # path can natively measure.
    flagged = False
    for col, thr in [
        ("residual_final", policy.residual_final_flag),
        ("regime_confidence", policy.regime_confidence_flag),
        ("predictor_gap", policy.predictor_gap_flag),
    ]:
        v = row[col]
        if v is not None and not pd.isna(v) and float(v) > thr:
            flagged = True
            break

    if high_error and flagged:
        return "TP"
    if high_error and not flagged:
        return "FN"
    if not high_error and flagged:
        return "FP"
    return "TN"


def classify(df: pd.DataFrame, policy: ThresholdPolicy) -> pd.DataFrame:
    """Add a 'bin' column. Phase-A rows (noise='clean') get NO_GT."""
    out = df.copy()
    out["bin"] = out.apply(lambda r: _classify_row(r, policy), axis=1)
    return out


def bin_table(classified: pd.DataFrame) -> pd.DataFrame:
    """Per (path, noise_model) bin counts + FN rate among scored fits."""
    scoreable = classified[classified["bin"].isin(["TP", "FN", "FP", "TN"])]
    counts = (
        classified.groupby(["path", "noise_model", "bin"], dropna=False)
        .size().unstack(fill_value=0)
    )
    for col in ("TP", "FN", "FP", "TN", "HANG", "ERROR", "NO_GT"):
        if col not in counts.columns:
            counts[col] = 0

    # FN rate among HIGH-error fits = FN / (TP + FN)
    score_counts = (
        scoreable.groupby(["path", "noise_model", "bin"])
        .size().unstack(fill_value=0)
    )
    for col in ("TP", "FN", "FP", "TN"):
        if col not in score_counts.columns:
            score_counts[col] = 0
    fn_rate = score_counts["FN"] / (score_counts["TP"] + score_counts["FN"]).replace(0, np.nan)
    fp_rate = score_counts["FP"] / (score_counts["FP"] + score_counts["TN"]).replace(0, np.nan)

    out = counts.copy()
    out["FN_rate"] = fn_rate
    out["FP_rate"] = fp_rate
    return out.reset_index()


def write_summary_md(classified: pd.DataFrame, table: pd.DataFrame, out_path: Path,
                     policy: ThresholdPolicy, manifest: Optional[dict] = None) -> None:
    lines: list[str] = []
    lines.append("# Diagnostic-vector calibration sweep — report\n")
    if manifest:
        lines.append(f"Run: `{manifest.get('label', '?')}` at {manifest.get('timestamp_utc', '?')}\n")
        lines.append(f"Total rows: {manifest.get('total_rows', len(classified))}; "
                     f"workers: {manifest.get('phase_a_workers', '?')} (phase A) + "
                     f"{manifest.get('phase_b_workers', '?')} (phase B)\n")
    lines.append("## Threshold policy\n")
    lines.append("| Parameter | Value |")
    lines.append("|---|---|")
    lines.append(f"| gt_error_high | {policy.gt_error_high} |")
    lines.append(f"| residual_final_flag | {policy.residual_final_flag} |")
    lines.append(f"| regime_confidence_flag | {policy.regime_confidence_flag} |")
    lines.append(f"| predictor_gap_flag | {policy.predictor_gap_flag} |")
    lines.append("")

    lines.append("## Per-(path, noise_model) bin breakdown\n")
    lines.append("Scoreable bins: TP (high error, flagged), FN (high error, silent — "
                 "**diagnostic missed it**), FP (low error, flagged), TN (low error, silent). "
                 "FN_rate = FN / (TP+FN) over rows with ground truth.\n")
    lines.append(_df_to_md(table, index=False))
    lines.append("")

    # Headline: per-path FN rate
    lines.append("## Headline — per-path FN rate (aggregated over noise models)\n")
    score = classified[classified["bin"].isin(["TP", "FN"])]
    per_path = (
        score.groupby("path")["bin"]
        .apply(lambda s: (s == "FN").sum() / len(s) if len(s) else float("nan"))
        .rename("FN_rate").reset_index()
    )
    lines.append(_df_to_md(per_path, index=False))
    lines.append("")

    # Per-path worst (highest FN-rate) noise models
    lines.append("## Worst noise model per path (highest FN rate)\n")
    lines.append("| Path | Worst noise model | FN rate |")
    lines.append("|---|---|---|")
    for path in sorted(table["path"].unique()):
        sub = table[table["path"] == path].copy()
        if sub["FN_rate"].dropna().empty:
            lines.append(f"| {path} | — | — |")
            continue
        worst = sub.loc[sub["FN_rate"].idxmax()]
        lines.append(f"| {path} | {worst['noise_model']} | {worst['FN_rate']:.3f} |")
    lines.append("")

    # Status sanity
    lines.append("## Status sanity\n")
    status_counts = classified["status"].value_counts()
    lines.append(_series_to_md(status_counts, value_name="count"))
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_scatter_pngs(classified: pd.DataFrame, out_dir: Path) -> list[Path]:
    """Per path, a 3-panel scatter of (gt_error, diagnostic_value) for each
    of the three diagnostic dimensions, colored by noise_model. 4K resolution
    per the rendering floor."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = sorted(classified["path"].unique())
    diag_cols = ["residual_final", "regime_confidence", "predictor_gap"]
    out_paths: list[Path] = []

    scoreable = classified[classified["bin"].isin(["TP", "FN", "FP", "TN"])]

    for path in paths:
        sub = scoreable[scoreable["path"] == path]
        if sub.empty:
            continue
        fig, axes = plt.subplots(1, 3, figsize=(24, 8), dpi=240)
        for ax, col in zip(axes, diag_cols):
            valid = sub[sub[col].notna()]
            if valid.empty:
                ax.text(0.5, 0.5, f"{col}\n(all None for this path)",
                        ha="center", va="center", transform=ax.transAxes)
                ax.set_axis_off()
                continue
            for noise, group in valid.groupby("noise_model"):
                ax.scatter(
                    group["gt_error"], group[col],
                    s=4 + 12 * (group["intensity"] + 0.05),
                    alpha=0.5, label=noise,
                )
            ax.set_xlabel("gt_error (|fit_chit - gt_chit|)")
            ax.set_ylabel(col)
            ax.set_title(f"{col} vs gt_error — path={path}")
            ax.set_xscale("symlog", linthresh=1e-3)
            ax.set_yscale("symlog", linthresh=1e-3)
            ax.grid(True, alpha=0.3)
            ax.legend(loc="best", fontsize=8, ncol=2)
        fig.suptitle(f"Diagnostic vs ground-truth error — {path}", fontsize=14)
        fig.tight_layout()
        out_path = out_dir / f"scatter_{path}.png"
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        out_paths.append(out_path)

    return out_paths


def report(parquet_path: Path, *, policy: ThresholdPolicy = ThresholdPolicy(),
           out_dir: Optional[Path] = None) -> Path:
    """Read sweep parquet, classify, write report artifacts. Returns out_dir."""
    import json

    parquet_path = Path(parquet_path)
    if out_dir is None:
        out_dir = parquet_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(parquet_path)
    classified = classify(df, policy)
    classified.to_parquet(out_dir / "classified.parquet")

    table = bin_table(classified)
    table.to_csv(out_dir / "bins.csv", index=False)

    manifest_path = parquet_path.parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None

    write_summary_md(classified, table, out_dir / "summary.md", policy, manifest)
    scatter_paths = write_scatter_pngs(classified, out_dir)

    print(f"\nReport written to {out_dir}")
    print(f"  summary.md")
    print(f"  bins.csv")
    print(f"  classified.parquet")
    for p in scatter_paths:
        print(f"  {p.name}")
    return out_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("parquet_path", help="path to sweep.parquet")
    args = parser.parse_args()
    report(Path(args.parquet_path))
