"""CLI entry: python -m conformer.calibration [--glass-only|--full] [--report-only PATH]

Default: glass-only mini-full sweep (1 substrate, all paths/noises/intensities/seeds).
--full: 3-substrate full sweep.
--report-only PATH: skip sweep, run reporter on existing sweep.parquet at PATH.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def main() -> None:
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--glass-only", action="store_true",
                     help="run glass-only mini-full sweep (default)")
    grp.add_argument("--full", action="store_true",
                     help="run full 3-substrate sweep (~hours)")
    grp.add_argument("--report-only", type=str, default=None,
                     help="path to existing sweep.parquet; run reporter only")
    parser.add_argument("--n-workers", type=int, default=None,
                        help="override worker count (default: cpu_count - 1)")
    args = parser.parse_args()

    if args.report_only:
        from conformer.calibration.report import report
        report(Path(args.report_only))
        return

    from conformer.calibration.sweep import SweepConfig, run_sweep
    from conformer.calibration.report import report

    if args.full:
        cfg = SweepConfig(n_workers=args.n_workers)
        label = "full-3sub"
    else:
        cfg = SweepConfig(substrates=("glass",), n_workers=args.n_workers)
        label = "glass-only"

    parquet_path = run_sweep(cfg, label=label)
    report(parquet_path)


if __name__ == "__main__":
    main()
