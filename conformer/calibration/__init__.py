"""Diagnostic-vector calibration via noise sweep.

The mpa-lens-solver FitDiagnostics surface (residual_final,
regime_confidence, predictor_gap) is calibrated against ground-truth
error by sweeping noise models, intensities, and seeds across the full
substrate library. Result: a parquet of per-fit (diagnostic, gt_error,
status) rows that the reporter turns into characterization tables and
visual artifacts.

The sweep is the apparatus that decides what numerical thresholds the
diagnostic surface warrants. No downstream consumer should bind to
specific threshold values without referencing a sweep run.
"""
