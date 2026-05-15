"""Two-stage inversion fit + phase-locking gamma_AB fit.

Port of mpa-auditor/engines/inversion-engine.js.

Stage 1: analytical grid search over chit (CHIT_STEPS candidates).
Stage 2: ensemble refine around analytical optimum (REFINE_OFFSETS
candidates), scored against ensemble-derived locus where the
cooperative kernel converges, against analytical locus where it
diverges (hybrid path).

gamma_AB fit: grid search against phase-locking observable r, when the
upload carries one. Otherwise gamma_AB is reported unconstrained
(rfc-s-integration-notes.md D1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from . import gfdr_model, observables
from .phase_locking import compute_phase_locking_r


CHIT_MIN, CHIT_MAX, CHIT_STEPS = -2.0, 2.0, 161
REFINE_OFFSETS = [-0.075, -0.05, -0.025, 0.0, 0.025, 0.05, 0.075]
GAMMA_FIT_MIN, GAMMA_FIT_MAX, GAMMA_FIT_STEPS = -1.0, 1.0, 41
DEFAULT_GAMMA = -0.3
SCORING_N_ENSEMBLE = 64


# Stage logger: a callable (event_kind: str, payload: dict) -> None.
# CLI wires rich/stdout; tests pass a no-op. Keeps activity logging out
# of the math.
Logger = Callable[[str, dict], None]


def _noop_logger(kind: str, payload: dict) -> None:
    pass


@dataclass
class FitResult:
    chit: float
    gamma_AB: float
    regime: str
    locus_residual: float
    gamma_residual: Optional[float]
    chit_observable: str          # 'gfdr-locus-analytical' | '...-ensemble' | '...-hybrid'
    gamma_observable: str         # 'phase-locking-r' | 'none'
    gamma_constrained: bool
    stage1_chit: float            # analytical-only chit before stage 2
    stage2_n_ensemble: int        # how many refine candidates scored via ensemble
    stage2_n_analytical: int      # how many fell back to analytical
    notes: list[str] = field(default_factory=list)


def fit_chit_analytical(rows: list[dict]) -> tuple[float, float]:
    grid = np.linspace(CHIT_MIN, CHIT_MAX, CHIT_STEPS)
    best_chit = 0.0
    best_res = float("inf")
    for chit in grid:
        res = gfdr_model.locus_residual(rows, float(chit))
        if res < best_res:
            best_res = res
            best_chit = float(chit)
    return best_chit, best_res


def _score_chit_candidate_ensemble(chit: float, gamma: float, rows: list[dict]) -> tuple[float, str]:
    """Score one chit candidate via ensemble locus; fall back to analytical
    on divergence. Returns (residual, scored_via)."""
    try:
        locus = observables.gfdr_locus(
            chit, gamma,
            n_ensemble=SCORING_N_ENSEMBLE,
        )
        return gfdr_model.residual_vs_ensemble_locus(rows, locus), "ensemble"
    except Exception:
        return gfdr_model.locus_residual(rows, chit), "analytical"


def refine_chit(
    center_chit: float,
    gamma: float,
    rows: list[dict],
    log: Logger,
) -> tuple[float, float, str, int, int]:
    """Stage 2 ensemble refine. Returns
    (chit, residual, observable_label, n_ensemble, n_analytical)."""
    candidates = sorted(set(
        round(max(CHIT_MIN, min(CHIT_MAX, center_chit + off)), 6)
        for off in REFINE_OFFSETS
    ))
    log("stage2_start", {"center_chit": center_chit, "gamma": gamma, "n_candidates": len(candidates)})

    n_ens = 0
    n_ana = 0
    best_chit, best_res, best_via = candidates[0], float("inf"), "analytical"
    for i, chit in enumerate(candidates):
        res, via = _score_chit_candidate_ensemble(chit, gamma, rows)
        if via == "ensemble":
            n_ens += 1
        else:
            n_ana += 1
        log("stage2_candidate", {
            "i": i + 1, "n": len(candidates), "chit": chit,
            "residual": res, "scored_via": via,
        })
        if res < best_res:
            best_res = res
            best_chit = chit
            best_via = via

    if n_ens > 0 and n_ana > 0:
        label = "gfdr-locus-hybrid"
    elif n_ens > 0:
        label = "gfdr-locus-ensemble"
    else:
        label = "gfdr-locus-analytical"
    return best_chit, best_res, label, n_ens, n_ana


def fit_gamma(chit: float, empirical_r: float, log: Logger) -> tuple[float, float, dict]:
    """Grid search gamma_AB against an empirical phase-locking r. Returns
    (gamma, residual, raw_r_result). Raises if no candidate is finite."""
    grid = np.linspace(GAMMA_FIT_MIN, GAMMA_FIT_MAX, GAMMA_FIT_STEPS)
    best: Optional[tuple[float, float, dict]] = None
    log("gamma_fit_start", {"chit": chit, "n_candidates": len(grid), "empirical_r": empirical_r})
    for i, gamma in enumerate(grid):
        try:
            r_res = compute_phase_locking_r(float(chit), float(gamma))
        except Exception:
            continue
        r_pred = r_res.get("r")
        if r_pred is None or not np.isfinite(r_pred):
            continue
        residual = abs(r_pred - empirical_r)
        log("gamma_candidate", {
            "i": i + 1, "n": len(grid), "gamma": float(gamma),
            "r_pred": r_pred, "residual": residual,
        })
        if best is None or residual < best[1]:
            best = (float(gamma), float(residual), r_res)
    if best is None:
        raise RuntimeError("no finite phase-locking candidate across the gamma_AB grid")
    return best


def invert(
    rows: list[dict],
    *,
    initial_gamma: float = DEFAULT_GAMMA,
    empirical_r: Optional[float] = None,
    skip_stage2: bool = False,
    log: Logger = _noop_logger,
) -> FitResult:
    """Run the full two-stage fit + optional gamma_AB fit.

    `rows`: list of {"tau", "C", "chi", ...} (the observable.data of a
    declaration_bundle).
    `initial_gamma`: gamma_AB carried through unconstrained when no
    phase-locking observable is supplied.
    `empirical_r`: if not None, drive the gamma_AB fit against it.
    `skip_stage2`: if True, skip ensemble refine (analytical-only fit;
    useful for fast smoke tests).
    `log`: activity logger.
    """
    finite_rows = [
        r for r in rows
        if all(k in r for k in ("tau", "C", "chi"))
        and all(np.isfinite(float(r[k])) for k in ("tau", "C", "chi"))
    ]
    if len(finite_rows) < 2:
        raise ValueError(f"need at least 2 usable (tau, C, chi) rows, got {len(finite_rows)}")

    log("stage1_start", {"n_rows": len(finite_rows), "n_chit_candidates": CHIT_STEPS})
    chit_analytical, res_analytical = fit_chit_analytical(finite_rows)
    log("stage1_done", {"chit": chit_analytical, "residual": res_analytical})

    chit = chit_analytical
    locus_residual = res_analytical
    chit_observable = "gfdr-locus-analytical"
    n_ens = 0
    n_ana = CHIT_STEPS  # Stage 1 is fully analytical
    if not skip_stage2:
        try:
            chit, locus_residual, chit_observable, n_ens, n_ana = refine_chit(
                chit_analytical, initial_gamma, finite_rows, log,
            )
            log("stage2_done", {
                "chit": chit, "residual": locus_residual,
                "observable": chit_observable,
                "n_ensemble": n_ens, "n_analytical": n_ana,
            })
        except Exception as e:
            log("stage2_failed", {"error": str(e)})

    gamma = initial_gamma
    gamma_constrained = False
    gamma_observable = "none"
    gamma_residual: Optional[float] = None
    if empirical_r is not None and np.isfinite(empirical_r):
        try:
            gamma_fit, gamma_residual, r_res = fit_gamma(chit, float(empirical_r), log)
            gamma = gamma_fit
            gamma_constrained = True
            gamma_observable = "phase-locking-r"
            log("gamma_fit_done", {
                "gamma_AB": gamma, "residual": gamma_residual,
                "phase_relationship": r_res.get("phase_relationship"),
            })
        except Exception as e:
            log("gamma_fit_failed", {"error": str(e)})

    regime = gfdr_model.vertex_regime(chit)
    return FitResult(
        chit=chit,
        gamma_AB=gamma,
        regime=regime,
        locus_residual=locus_residual,
        gamma_residual=gamma_residual,
        chit_observable=chit_observable,
        gamma_observable=gamma_observable,
        gamma_constrained=gamma_constrained,
        stage1_chit=chit_analytical,
        stage2_n_ensemble=n_ens,
        stage2_n_analytical=n_ana,
    )
