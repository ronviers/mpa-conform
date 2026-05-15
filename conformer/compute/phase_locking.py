"""Phase-locking forward model — port of mpa-auditor/math/phase-locking-model.js.

cdv1 §Phase-locking two-mode phase reduction:
    K_AB = -gamma_AB * sqrt(rho_A * rho_B) / [rho_sat * sqrt(1 + 4*Q^2)]

Lock criterion: |K_AB| >= Delta_omega_ref.

Used by the inversion's gamma_AB fit against an empirical Kuramoto r.
"""
from __future__ import annotations

import math

import numpy as np

from .kernel import KernelParams, from_chit_gamma, integrate_deterministic, linearize


SOLVER_T_MAX = 30.0
SOLVER_DT = 0.01
SOLVER_SAMPLE_EVERY = 10
SOLVER_INITIAL = (0.3, 0.7)
DELTA_OMEGA_REF = 0.15
RHO_SAT = 1.0


def _phase_locking_r(gamma: float, final_state: tuple[float, float], Q: float) -> dict:
    rho_A = max(0.0, final_state[0])
    rho_B = max(0.0, final_state[1])
    q_eff = Q if (Q is not None and math.isfinite(Q) and Q > 0) else 0.0
    K_AB = -gamma * math.sqrt(rho_A * rho_B) / (RHO_SAT * math.sqrt(1.0 + 4.0 * q_eff * q_eff))
    abs_K = abs(K_AB)
    if abs_K >= DELTA_OMEGA_REF:
        psi_lock = math.asin(min(1.0, DELTA_OMEGA_REF / abs_K))
        psi = psi_lock if K_AB >= 0 else (math.pi - psi_lock)
        return {
            "r": abs(math.cos(psi / 2.0)),
            "K_AB": K_AB,
            "locked": True,
            "phase_relationship": "in_phase" if K_AB >= 0 else "anti_phase",
        }
    return {
        "r": (1.0 / math.sqrt(2.0)) * (abs_K / DELTA_OMEGA_REF),
        "K_AB": K_AB,
        "locked": False,
        "phase_relationship": "drift",
    }


def compute_phase_locking_r(chit: float, gamma: float) -> dict:
    """Forward model: predicted Kuramoto r at (chit, gamma_AB).

    Runs deterministic ODE to a settled state for (rho_A, rho_B), then
    linearizes for Q. Returns {r, K_AB, locked, phase_relationship}.
    Raises RuntimeError if the kernel diverges (non-finite final state).
    """
    params = from_chit_gamma(chit, gamma)
    traj = integrate_deterministic(
        SOLVER_INITIAL, params, SOLVER_T_MAX, SOLVER_DT, SOLVER_SAMPLE_EVERY,
    )
    final = (float(traj["rho_A"][-1]), float(traj["rho_B"][-1]))

    if not (math.isfinite(final[0]) and math.isfinite(final[1])):
        raise RuntimeError("phase-locking forward model: solver final state non-finite (kernel diverged)")

    try:
        lin = linearize(final, params)
        Q = float(lin.get("Q", 0.0))
    except Exception:
        Q = 0.0

    return _phase_locking_r(gamma, final, Q)
