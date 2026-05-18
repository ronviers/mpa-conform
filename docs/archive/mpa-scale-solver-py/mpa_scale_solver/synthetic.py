"""Synthetic driver profile + analytical truth for the migration test.

The synthetic driver supplies a closed-form substrate-conditional translation
field. Because the rule is closed-form, we can compute the analytical canonical
state at any tau_obs *independently of the solver*. The end-to-end test then
compares solver output to analytical truth — two curves that must overlay if
the math is right.

The rule (per operations._apply_parametric / 'aging_log'):

    substrate_chit  = canonical_chit + a * log(1 + tau_obs / tau_aging)
    substrate_gamma = canonical_gamma_AB * (1 + b * log(1 + tau_obs / tau_aging))

For a fixed substrate observation S = (S_chit, S_gamma):

    canonical_chit(tau_obs)    = S_chit - a * log(1 + tau_obs / tau_aging)
    canonical_gamma(tau_obs)   = S_gamma / (1 + b * log(1 + tau_obs / tau_aging))

This is the analytical truth the solver's forward_sweep_invert must recover.
"""

from __future__ import annotations

import math

from .types import TranslationField


# Synthetic substrate parameters that produce a clean c -> s -> r migration
# across a tau_obs sweep with reference chit_0 = 2.0 in c-regime.
DEFAULT_SYNTHETIC_PARAMS = {
    "rule": "aging_log",
    "chit_aging_coeff": 1.0,
    "tau_aging": 1.0,
    "gamma_aging_coeff": 0.0,
}


def make_synthetic_aging_driver(
    chit_aging_coeff: float = 1.0,
    tau_aging: float = 1.0,
    gamma_aging_coeff: float = 0.0,
) -> TranslationField:
    """Build a synthetic driver-profile translation field.

    Parameters mirror the closed-form rule. The defaults are chosen to give
    a clean migration: at chit_0 = 2.0 reference, the sweep covers c (chit~2)
    through s (chit~0) to r (chit<<0) for tau_obs in [0.01, 100].
    """
    return TranslationField(
        form="parametric",
        params={
            "rule": "aging_log",
            "chit_aging_coeff": chit_aging_coeff,
            "tau_aging": tau_aging,
            "gamma_aging_coeff": gamma_aging_coeff,
        },
    )


def analytical_canonical_chit(
    substrate_chit: float,
    tau_obs: float,
    chit_aging_coeff: float = 1.0,
    tau_aging: float = 1.0,
) -> float:
    """Analytical truth: canonical_chit at tau_obs for fixed substrate observation.

    Independent of the solver. The solver's forward_sweep_invert must reproduce
    this for the test to pass.
    """
    return substrate_chit - chit_aging_coeff * math.log1p(tau_obs / tau_aging)


def analytical_canonical_gamma(
    substrate_gamma: float,
    tau_obs: float,
    gamma_aging_coeff: float = 0.0,
    tau_aging: float = 1.0,
) -> float:
    """Analytical truth: canonical_gamma_AB at tau_obs for fixed substrate."""
    drift = math.log1p(tau_obs / tau_aging)
    return substrate_gamma / (1.0 + gamma_aging_coeff * drift)
