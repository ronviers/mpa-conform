"""Analytical gFDR forward model — port of mpa-auditor/math/gfdr-model.js.

Pure math. Leading-order forward model for chit -> (tau, C, chi). Used
by the inversion's Stage 1 (analytical localize) and as the fallback
where the cooperative-band ensemble diverges.
"""
from __future__ import annotations

import numpy as np


N_LOCUS_POINTS = 80


def vertex_regime(chit: float) -> str:
    if chit >= 0.7:
        return "deep_c"
    if chit >= 0.2:
        return "c_near_s"
    if chit > -0.2:
        return "s_critical"
    if chit > -0.7:
        return "r_near_s"
    return "deep_r"


def alpha_s(chit: float) -> float:
    return 0.5 + 0.3 * float(np.exp(-abs(chit) * 4))


def plateau_height(chit: float) -> float:
    return max(0.05, 1.0 - float(np.exp(-max(0.0, chit + 0.2) * 1.5)))


def generate_locus(chit: float, regime: str | None = None, n_points: int = N_LOCUS_POINTS) -> dict:
    """Geometric tau-grid analytical locus. Returns {tau, C, chi}."""
    if regime is None:
        regime = vertex_regime(chit)
    tau_min, tau_max = 0.01, 1000.0
    ts = np.linspace(0.0, 1.0, n_points)
    tau = tau_min * np.power(tau_max / tau_min, ts)
    C = np.zeros_like(tau)
    chi = np.zeros_like(tau)

    if regime in ("deep_c", "c_near_s"):
        depth = float(np.exp(-chit * 1.5))
        tau_c = 4.0 + 6.0 / max(0.1, chit)
        dC = 0.18 * depth * (1.0 - np.exp(-tau / tau_c))
        C = 1.0 - dC
        chi = (0.02 if regime == "deep_c" else 0.08) * dC
    elif regime == "s_critical":
        a = alpha_s(chit)
        P_s = plateau_height(chit)
        dC_short = (1.0 - P_s) * (1.0 - np.exp(-tau / 0.5))
        dC_long = P_s * (1.0 - np.power(1.0 + tau / 50.0, -a))
        dC = dC_short + dC_long
        C = 1.0 - dC
        chi = np.where(dC <= (1.0 - P_s), dC, (1.0 - P_s) + a * (dC - (1.0 - P_s)))
    else:  # r_near_s, deep_r
        tau_eq = max(0.5, 1.0 + 0.5 * float(np.exp(chit)))
        dC = 1.0 - np.exp(-tau / tau_eq)
        C = 1.0 - dC
        chi = dC

    return {"tau": tau, "C": C, "chi": chi}


def _interp_log_tau(model: dict, tau_query: float) -> tuple[float, float]:
    """Log-tau linear interpolation of the analytical locus at tau_query."""
    tau = model["tau"]
    C = model["C"]
    chi = model["chi"]
    if tau_query <= tau[0]:
        return float(C[0]), float(chi[0])
    if tau_query >= tau[-1]:
        return float(C[-1]), float(chi[-1])
    idx = int(np.searchsorted(tau, tau_query))
    a, b = idx - 1, idx
    f = (np.log(tau_query) - np.log(tau[a])) / (np.log(tau[b]) - np.log(tau[a]))
    return float(C[a] + f * (C[b] - C[a])), float(chi[a] + f * (chi[b] - chi[a]))


def locus_residual(empirical_rows: list[dict], chit: float) -> float:
    """MSE of empirical (tau, C, chi) against the analytical model at chit."""
    model = generate_locus(chit)
    sse = 0.0
    n = 0
    for row in empirical_rows:
        try:
            t = float(row["tau"])
            ce = float(row["C"])
            che = float(row["chi"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (np.isfinite(t) and np.isfinite(ce) and np.isfinite(che)):
            continue
        cm, chim = _interp_log_tau(model, t)
        sse += (ce - cm) ** 2 + (che - chim) ** 2
        n += 1
    if n == 0:
        return float("inf")
    return sse / n


def residual_vs_ensemble_locus(empirical_rows: list[dict], locus: dict) -> float:
    """MSE against an ensemble-derived locus (linear tau interp, matching
    the auditor's `interpLinear`)."""
    tau = locus["tau"]
    C = locus["C"]
    chi = locus["chi"]
    sse = 0.0
    n = 0
    for row in empirical_rows:
        try:
            t = float(row["tau"])
            ce = float(row["C"])
            che = float(row["chi"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (np.isfinite(t) and np.isfinite(ce) and np.isfinite(che)):
            continue
        if t <= tau[0]:
            cm, chim = float(C[0]), float(chi[0])
        elif t >= tau[-1]:
            cm, chim = float(C[-1]), float(chi[-1])
        else:
            idx = int(np.searchsorted(tau, t))
            a, b = idx - 1, idx
            f = (t - tau[a]) / (tau[b] - tau[a])
            cm = float(C[a] + f * (C[b] - C[a]))
            chim = float(chi[a] + f * (chi[b] - chi[a]))
        sse += (ce - cm) ** 2 + (che - chim) ** 2
        n += 1
    if n == 0:
        return float("inf")
    return sse / n
