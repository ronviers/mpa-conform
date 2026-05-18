"""Cross-path disagreement: |chit_two_stage - chit_lens_solver_prior| per cell.

When the curator runs a substrate batch, two independent paths produce
chit per cell (the existing two_stage_inversion via inversion.invert, and
the lens_solver_prior via fit_translation_field). Their disagreement is
a chit-unit confidence signal that requires no calibration: if two
independent fits agree, both are likely right; if they disagree, at
least one is wrong.

This module computes the disagreement given the two-stage chits already
computed by walk_library and a batched lens_solver_prior call.

No threshold here — the disagreement is a chit-unit distance the auditor
interprets directly.
"""
from __future__ import annotations

from typing import Optional

from mpa_lens_solver import fit_translation_field


def lens_solver_prior_chits_for_batch(
    substrate: str,
    cells: list[dict],
    xdot_kind: str,
    *,
    max_passes: int = 10,
    rng_seed: int = 0,
) -> dict[str, float]:
    """Run lens_solver_prior on the substrate batch (predictor active).
    Returns {operating_point_label: chit}.

    Batched form: a single fit_translation_field call sees the whole
    trajectory so the predictor is active. Single-cell calls would
    disable the predictor (no history); the disagreement signal is most
    meaningful when both paths used their production setup.
    """
    if not cells:
        return {}
    field_obj = fit_translation_field(
        substrate, cells, xdot_kind,
        max_passes=max_passes, rng_seed=rng_seed, bootstrap=False,
    )
    return {
        rule.operating_point.label: float(rule.canonical.chit)
        for rule in field_obj.rule
    }


def cross_path_disagreement(
    two_stage_chit: Optional[float],
    lens_solver_chit: Optional[float],
) -> Optional[float]:
    """|chit_two_stage - chit_lens_solver_prior| in chit units.

    Returns None when either path's chit is None — be honest that we
    don't have a cross-path signal for cells where one path didn't fit.
    """
    if two_stage_chit is None or lens_solver_chit is None:
        return None
    return float(abs(float(two_stage_chit) - float(lens_solver_chit)))


def cross_path_disagreements_for_batch(
    substrate: str,
    cells: list[dict],
    xdot_kind: str,
    two_stage_chits_by_label: dict[str, Optional[float]],
    *,
    max_passes: int = 10,
    rng_seed: int = 0,
) -> dict[str, Optional[float]]:
    """Convenience: run lens_solver_prior in batch + compute per-cell
    disagreement against the supplied two_stage_chits_by_label.

    Returns {operating_point_label: disagreement_or_None}.
    """
    lens_chits = lens_solver_prior_chits_for_batch(
        substrate, cells, xdot_kind,
        max_passes=max_passes, rng_seed=rng_seed,
    )
    out: dict[str, Optional[float]] = {}
    for label, ts_chit in two_stage_chits_by_label.items():
        out[label] = cross_path_disagreement(ts_chit, lens_chits.get(label))
    return out
