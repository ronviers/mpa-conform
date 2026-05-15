"""Universal two-mode kernel + Lamb stationary closure.

cdv1 §Universal two-mode kernel:

    drho_A/dt = (G_0,A^eff - L_A) * rho_A - gamma_AB * rho_A * rho_B
    drho_B/dt = (G_0,B^eff - L_B) * rho_B - gamma_AB * rho_A * rho_B  (symmetric)

with Lamb closure:

    G_0,A^eff = G_0,A / (1 + rho_B / rho_sat)
    G_0,B^eff = G_0,B / (1 + rho_A / rho_sat)

Sign convention: gamma_AB < 0 contributes positively to drho_A/dt
(cooperative); gamma_AB > 0 is competitive.

The auditor's `mapToSolverParams` uses G_0 = exp(chit), L = 1, rho_sat = 1.
Matches the v0 Lamb path of mpa-solver (which is bit-preserved per its v2
backward-compat test gate).

Vectorized over the ensemble axis: state shape is (N_ensemble, 2). The
single-trajectory case is N_ensemble=1.

Positivity clamping at every step: rho >= 0 (mpa-solver/CLAUDE.md says
this is caller responsibility).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class KernelParams:
    G0_A: float
    G0_B: float
    L_A: float = 1.0
    L_B: float = 1.0
    gamma_AB: float = 0.0
    rho_sat: float = 1.0


def from_chit_gamma(chit: float, gamma_AB: float) -> KernelParams:
    """Auditor convention: chit = ln(G_0/L), reference L = 1."""
    G0 = float(np.exp(chit))
    return KernelParams(G0_A=G0, G0_B=G0, gamma_AB=float(gamma_AB))


def drift(state: np.ndarray, p: KernelParams) -> np.ndarray:
    """state: (..., 2) -> drift: (..., 2)."""
    rho_A = state[..., 0]
    rho_B = state[..., 1]
    G0_A_eff = p.G0_A / (1.0 + rho_B / p.rho_sat)
    G0_B_eff = p.G0_B / (1.0 + rho_A / p.rho_sat)
    cross = p.gamma_AB * rho_A * rho_B
    drho_A = (G0_A_eff - p.L_A) * rho_A - cross
    drho_B = (G0_B_eff - p.L_B) * rho_B - cross
    return np.stack([drho_A, drho_B], axis=-1)


def rk4_step(state: np.ndarray, p: KernelParams, dt: float) -> np.ndarray:
    k1 = drift(state, p)
    k2 = drift(state + 0.5 * dt * k1, p)
    k3 = drift(state + 0.5 * dt * k2, p)
    k4 = drift(state + dt * k3, p)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def em_step(
    state: np.ndarray,
    p: KernelParams,
    dt: float,
    noise_scale: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Euler-Maruyama with additive Gaussian noise."""
    f = drift(state, p)
    dW = rng.standard_normal(size=state.shape) * np.sqrt(dt)
    return state + f * dt + noise_scale * dW


def integrate_deterministic(
    initial: tuple[float, float],
    p: KernelParams,
    t_max: float,
    dt: float,
    sample_every: int = 1,
) -> dict:
    """Single-trajectory RK4 integration. Returns {t, rho_A, rho_B}."""
    n_steps = int(round(t_max / dt))
    state = np.array([initial[0], initial[1]], dtype=np.float64)
    ts: list[float] = []
    rhoA: list[float] = []
    rhoB: list[float] = []
    for step in range(n_steps + 1):
        if step % sample_every == 0:
            ts.append(step * dt)
            rhoA.append(state[0])
            rhoB.append(state[1])
        if step < n_steps:
            state = rk4_step(state, p, dt)
            np.maximum(state, 0.0, out=state)
    return {"t": np.array(ts), "rho_A": np.array(rhoA), "rho_B": np.array(rhoB)}


def integrate_ensemble(
    initial: tuple[float, float],
    p: KernelParams,
    t_max: float,
    dt: float,
    n_ensemble: int,
    d_noise: float,
    sample_every: int = 1,
    seed: int = 0,
) -> dict:
    """Ensemble Euler-Maruyama. Returns {t, rho_A, rho_B} where rho_*
    arrays have shape (n_samples, n_ensemble)."""
    rng = np.random.default_rng(seed)
    noise_scale = float(np.sqrt(max(d_noise, 0.0)))
    n_steps = int(round(t_max / dt))
    state = np.tile(
        np.array([initial[0], initial[1]], dtype=np.float64),
        (n_ensemble, 1),
    )
    ts: list[float] = []
    rhoA_samples: list[np.ndarray] = []
    rhoB_samples: list[np.ndarray] = []
    for step in range(n_steps + 1):
        if step % sample_every == 0:
            ts.append(step * dt)
            rhoA_samples.append(state[:, 0].copy())
            rhoB_samples.append(state[:, 1].copy())
        if step < n_steps:
            if noise_scale > 0.0:
                state = em_step(state, p, dt, noise_scale, rng)
            else:
                state = rk4_step(state, p, dt)
            np.maximum(state, 0.0, out=state)
    return {
        "t": np.array(ts),
        "rho_A": np.stack(rhoA_samples, axis=0),
        "rho_B": np.stack(rhoB_samples, axis=0),
    }


def linearize(
    state: tuple[float, float],
    p: KernelParams,
    eps: float = 1e-6,
) -> dict:
    """Numerical linearization at `state`. Returns eigenvalues + named
    invariants (omega_RO, gamma_RO, zeta, Q) per mpa-solver's v2
    convention. Q = omega_RO / (2*gamma_RO) if gamma_RO > 0 else 0."""
    s = np.array(state, dtype=np.float64)
    f0 = drift(s, p)
    J = np.zeros((2, 2), dtype=np.float64)
    for j in range(2):
        s_plus = s.copy()
        s_plus[j] += eps
        f_plus = drift(s_plus, p)
        J[:, j] = (f_plus - f0) / eps
    eigvals = np.linalg.eigvals(J)
    idx = int(np.argmax(eigvals.real))
    lam = eigvals[idx]
    omega_RO = float(abs(lam.imag))
    gamma_RO = float(-lam.real)
    if gamma_RO > 0.0:
        Q = float(omega_RO / (2.0 * gamma_RO))
        zeta = float(gamma_RO / np.sqrt(omega_RO ** 2 + gamma_RO ** 2)) if (omega_RO ** 2 + gamma_RO ** 2) > 0 else 1.0
    else:
        Q = 0.0
        zeta = 0.0
    return {
        "eigenvalues": [{"re": float(v.real), "im": float(v.imag)} for v in eigvals],
        "omega_RO": omega_RO,
        "gamma_RO": gamma_RO,
        "zeta": zeta,
        "Q": Q,
    }
