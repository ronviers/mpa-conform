"""gFDR observables: correlator C(tau), response chi(tau), and the
Onsager-normalized gFDR locus.

Match the auditor's `math/ensemble-locus.js` pipeline:
  1. ensemble: N stochastic trajectories with D_noise > 0
  2. correlator: connected autocorrelation C_AA(tau) from the post-
     equilibration ensemble
  3. responseDirect: IC-perturbation propagator chi_AA(tau) (re-
     integrates with rho_A(0) += pert, returns the difference)
  4. gfdrLocus: pairs DeltaC = C_AA(0) - C_AA(tau) with chi_AA(tau)
  5. Onsager normalization for plotting:
         DeltaC_norm = DeltaC / C_AA(0)        (grows 0 -> 1)
         chi_norm    = 1 - chi_AA(tau) / chi_AA(0)  (grows 0 -> 1 in eq)

Throws if the cooperative kernel runs away (caller falls back to
analytical, per the auditor's M-Inversion proper design).
"""
from __future__ import annotations

import numpy as np

from .kernel import KernelParams, integrate_ensemble


SANE_LO, SANE_HI = -0.5, 1.5


def connected_correlator(
    rho_A_ensemble: np.ndarray,
    equilibration: int,
    n_tau: int,
) -> np.ndarray:
    """Connected autocorrelation C_AA(tau) over (n_samples, n_ensemble).
    Returns array of length n_tau, where C_AA[k] = <delta_rho_A(t)
    delta_rho_A(t+k*dt_sample)> averaged over both time and ensemble.
    """
    post = rho_A_ensemble[equilibration:, :]
    n_samples, n_ensemble = post.shape
    mean_t = post.mean(axis=0, keepdims=True)
    delta = post - mean_t
    max_lag = min(n_tau, n_samples)
    C = np.zeros(max_lag, dtype=np.float64)
    for k in range(max_lag):
        if k == 0:
            C[k] = (delta * delta).mean()
        else:
            C[k] = (delta[:n_samples - k] * delta[k:]).mean()
    if max_lag < n_tau:
        C = np.concatenate([C, np.zeros(n_tau - max_lag)])
    return C


def response_direct(
    initial: tuple[float, float],
    params: KernelParams,
    t_max: float,
    dt: float,
    equilibration: int,
    n_tau: int,
    n_ensemble: int,
    d_noise: float,
    perturbation: float,
    seed: int = 0,
) -> np.ndarray:
    """Direct-perturbation response: chi_AA(tau) = <rho_A_perturbed(tau)
    - rho_A_unperturbed(tau)> / pert. Two ensembles with the same RNG
    seed differing only in rho_A(0)."""
    sample_every = 1
    unp = integrate_ensemble(
        initial, params, t_max, dt, n_ensemble, d_noise,
        sample_every=sample_every, seed=seed,
    )
    perturbed_initial = (initial[0] + perturbation, initial[1])
    per = integrate_ensemble(
        perturbed_initial, params, t_max, dt, n_ensemble, d_noise,
        sample_every=sample_every, seed=seed,
    )
    delta = (per["rho_A"] - unp["rho_A"]) / perturbation
    post = delta[equilibration:, :]
    n_post = post.shape[0]
    max_lag = min(n_tau, n_post)
    chi = post.mean(axis=1)[:max_lag]
    if max_lag < n_tau:
        chi = np.concatenate([chi, np.zeros(n_tau - max_lag)])
    return chi


def gfdr_locus(
    chit: float,
    gamma_AB: float,
    n_ensemble: int = 64,
    t_max: float = 30.0,
    dt: float = 0.01,
    equilibration: int = 300,
    n_tau: int = 1500,
    d_noise: float = 0.01,
    perturbation: float = 1e-3,
    initial: tuple[float, float] = (0.3, 0.7),
    seed: int = 0,
) -> dict:
    """Ensemble-derived Onsager-normalized gFDR locus at (chit, gamma_AB).

    Returns {"tau", "C", "chi"} arrays (length n_tau) in the same
    (1 - DeltaC_norm, chi_norm) coordinates the auditor's
    `computeEnsembleLocus` returns. Raises RuntimeError if the
    cooperative kernel runs away.
    """
    from .kernel import from_chit_gamma  # local import; avoid cycle

    params = from_chit_gamma(chit, gamma_AB)
    ens = integrate_ensemble(
        initial, params, t_max, dt, n_ensemble, d_noise,
        sample_every=1, seed=seed,
    )
    C_AA = connected_correlator(ens["rho_A"], equilibration, n_tau)
    chi_AA = response_direct(
        initial, params, t_max, dt, equilibration, n_tau, n_ensemble,
        d_noise, perturbation, seed=seed + 1,
    )

    C0 = C_AA[0]
    chi0 = chi_AA[0]
    if not np.isfinite(C0) or C0 <= 1e-9:
        raise RuntimeError("ensemble correlator degenerate (C(0) not positive-finite)")
    if not np.isfinite(chi0) or abs(chi0) < 1e-12:
        raise RuntimeError("ensemble response degenerate (chi(0) ~ 0)")
    if not np.all(np.isfinite(C_AA)) or not np.all(np.isfinite(chi_AA)):
        raise RuntimeError("ensemble locus diverged (non-finite values)")

    tau = np.arange(n_tau) * dt
    deltaC = C0 - C_AA
    C_plot = 1.0 - deltaC / C0
    chi_plot = 1.0 - chi_AA / chi0

    if not (
        np.all(C_plot >= SANE_LO) and np.all(C_plot <= SANE_HI)
        and np.all(chi_plot >= SANE_LO) and np.all(chi_plot <= SANE_HI)
    ):
        raise RuntimeError("ensemble locus out of sane bounds (cooperative-band runaway)")

    return {"tau": tau, "C": C_plot, "chi": chi_plot}
