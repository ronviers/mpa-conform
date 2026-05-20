"""Five-vector (KWW + FDT-violation) inversion — FIRST-CUT SCAFFOLD.

Owed work, blocked-in 2026-05-19. See
[`docs/five_vector_inversion_blockin.md`](../../docs/five_vector_inversion_blockin.md)
for the design and the validation contract, and
[`H:/mpa-central/FALSIFICATION.md`](H:/mpa-central/FALSIFICATION.md)
"KEY FINDING" / "FINDING 2" for why this is the keystone owed item
(X-recovery AND a domain-of-validity gate both depend on it).

The 1-param production inversion (`inversion.invert`) fits only the cdv1
`chit`. It cannot recover the substrate-thermodynamic refinement
(q_EA, tau_alpha, beta_KWW, tau_beta, X) that `gfdr_model.
generate_kww_glass_locus` *generates*. This module inverts that generator.

Stage shape (mirrors v0.2 two-stage; see blockin doc §Algorithm):
  Stage 1  cdv1 anchor: chit from `inversion.fit_chit_analytical` (reused,
           not reimplemented). Fixed during stage 2.
  Stage 2  numerical refine: least-squares the 5 glass params against
           `generate_kww_glass_locus(chit, ...)`, evaluated at the cell's
           dimensionless lag tau. T is fixed per substrate (sets the FDT
           slope 1/T); it is NOT a free parameter.

STATUS: first cut. Runs and recovers X on `two_temp_ou` (see test at
bottom). Known-incomplete — see blockin doc §"What's left" before relying
on it: param identifiability on degenerate C-shapes, seeding strategy,
integration into `invert()` / the bundle schema, and the residual-gate
that turns this into a domain-of-validity check.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

from . import gfdr_model
from . import inversion


@dataclass
class FiveVectorFit:
    chit: float          # cdv1 anchor (stage 1, fixed through stage 2)
    q_EA: float
    tau_alpha: float
    beta_KWW: float
    tau_beta: float
    X: float
    T: float
    residual: float      # RMS of the joint (C, chi) residual
    success: bool
    n_eval: int
    notes: list = field(default_factory=list)


# Param order: (q_EA, tau_alpha, beta_KWW, tau_beta, X). chit + T are fixed.
_LOWER = np.array([0.01, 1e-3, 0.10, 1e-4, 0.0])
_UPPER = np.array([1.00, 1e3,  1.00, 1e2,  1.0])
_SEED  = np.array([0.70, 1.0,  0.70, 0.10, 0.5])


def _model_at(params, chit: float, T: float, tau_query: np.ndarray):
    q_EA, tau_alpha, beta_KWW, tau_beta, X = params
    locus = gfdr_model.generate_kww_glass_locus(
        chit, q_EA=q_EA, tau_alpha=tau_alpha, beta_KWW=beta_KWW,
        tau_beta=tau_beta, X=X, T=T,
    )
    Cs = np.array([gfdr_model._interp_log_tau(locus, float(t))[0] for t in tau_query])
    chis = np.array([gfdr_model._interp_log_tau(locus, float(t))[1] for t in tau_query])
    return Cs, chis


def fit_kww5(
    rows: list[dict],
    *,
    chit_prior: Optional[float] = None,
    T: float = 1.0,
    seed: Optional[Sequence[float]] = None,
) -> FiveVectorFit:
    """First-cut 5-vector fit. `rows`: [{"tau","C","chi"}] in dimensionless
    lag (lag / tau_scale). `chit_prior`: cdv1 anchor; if None, fit it via
    stage 1. `T`: fixed FDT-slope temperature (NOT a free param)."""
    from scipy.optimize import least_squares

    finite = [
        r for r in rows
        if all(k in r for k in ("tau", "C", "chi"))
        and all(np.isfinite(float(r[k])) for k in ("tau", "C", "chi"))
    ]
    if len(finite) < 5:
        raise ValueError(f"need >=5 usable rows for a 5-param fit, got {len(finite)}")

    if chit_prior is None:
        chit_prior, _ = inversion.fit_chit_analytical(finite)

    tau = np.array([float(r["tau"]) for r in finite])
    C = np.array([float(r["C"]) for r in finite])
    chi = np.array([float(r["chi"]) for r in finite])

    def resid(p):
        Cm, chim = _model_at(p, float(chit_prior), float(T), tau)
        return np.concatenate([C - Cm, chi - chim])

    p0 = _SEED.copy() if seed is None else np.asarray(seed, dtype=float)
    res = least_squares(resid, p0, bounds=(_LOWER, _UPPER), max_nfev=4000)
    q_EA, tau_alpha, beta_KWW, tau_beta, X = res.x
    rms = float(np.sqrt(np.mean(res.fun ** 2)))
    return FiveVectorFit(
        chit=float(chit_prior), q_EA=float(q_EA), tau_alpha=float(tau_alpha),
        beta_KWW=float(beta_KWW), tau_beta=float(tau_beta), X=float(X), T=float(T),
        residual=rms, success=bool(res.success), n_eval=int(res.nfev),
        notes=["first-cut scaffold; see five_vector_inversion_blockin.md"],
    )
