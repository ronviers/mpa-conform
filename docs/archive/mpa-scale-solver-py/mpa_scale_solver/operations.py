"""The seven core scale-solver operations (bootstrap §4).

Per the revised §7 caveat 1: the v0 baseline is the Wilson-Kadanoff
fixed-point rule (time rescaling only, gamma and chit identity). Non-trivial
RG flow content arrives via driver-profile-supplied translation fields.

All operations are stateless free functions on plain dataclasses. Direct
port shape for a native (Rust/C++) build.
"""

from __future__ import annotations

import math
from typing import Optional, Union

import numpy as np

from .types import (
    CanonicalState,
    SubstrateState,
    TranslationField,
    GamutSpec,
    RegimeReading,
)


# Default chit thresholds for regime classification (cdv1 §The chit unit).
# - chit >> 0  : c (committed)
# - |chit| <= S_WINDOW_HALF_WIDTH : s (visible strain)
# - chit < -S_WINDOW_HALF_WIDTH : r (reset)
# Width is substrate-conditional; driver profile can override.
S_WINDOW_HALF_WIDTH_DEFAULT = 0.30


# ---------------------------------------------------------------------------
# Operation 1: apply_translation
# ---------------------------------------------------------------------------

def apply_translation(
    canonical: CanonicalState,
    field: TranslationField,
    tau_obs: float,
) -> SubstrateState:
    """Forward map: canonical state -> substrate-native observation at tau_obs.

    Per RFC-S §1 forward direction; per mpa-auditor §Q13 the forward map is
    the only well-defined direction (backward goes through forward_sweep_invert).

    Dispatches on field.form. The v0 trivial baseline applies the
    Wilson-Kadanoff fixed-point rule (gamma and chit identity); driver-profile-
    supplied rules can augment with substrate-conditional flow.
    """
    if field.form == "parametric":
        return _apply_parametric(canonical, field.params, tau_obs)
    if field.form == "lookup":
        raise NotImplementedError("lookup translation form deferred to v1")
    if field.form == "learned":
        raise NotImplementedError("learned translation form deferred to v2")
    raise ValueError(f"unknown translation field form: {field.form!r}")


def _apply_parametric(
    canonical: CanonicalState,
    params: dict,
    tau_obs: float,
) -> SubstrateState:
    """Parametric form dispatcher. Driver profile names the rule in params['rule']."""
    rule = params.get("rule", "trivial_baseline")

    if rule == "trivial_baseline":
        # Wilson-Kadanoff fixed-point rule: gamma and chit identity.
        # Time rescaling (tau_canonical = tau_substrate / tau_obs) is upstream
        # in the canonical-state construction; this map is on (chit, gamma) only.
        return SubstrateState(
            chit=canonical.chit,
            gamma_AB=canonical.gamma_AB,
        )

    if rule == "aging_log":
        # Synthetic substrate-conditional flow.
        # Driver-profile-supplied. NOT a solver default — the driver carries it.
        #
        #   substrate_chit = canonical_chit + a * log(1 + tau_obs/tau_aging)
        #   substrate_gamma_AB = canonical_gamma_AB * (1 + b * log(1 + tau_obs/tau_aging))
        #
        # Reading: at fixed substrate observation, canonical chit migrates
        # downward (c -> s -> r) as tau_obs grows. This is cdv1's
        # primary cross-substrate test signature in synthetic form.
        a = params["chit_aging_coeff"]
        tau_aging = params["tau_aging"]
        b = params.get("gamma_aging_coeff", 0.0)

        drift = math.log1p(tau_obs / tau_aging)
        return SubstrateState(
            chit=canonical.chit + a * drift,
            gamma_AB=canonical.gamma_AB * (1.0 + b * drift),
        )

    raise ValueError(f"unknown parametric rule: {rule!r}")


# ---------------------------------------------------------------------------
# Operation 2: forward_sweep_invert
# ---------------------------------------------------------------------------

def forward_sweep_invert(
    substrate: SubstrateState,
    field: TranslationField,
    tau_obs: float,
    canonical_grid: np.ndarray,
    return_residual_field: bool = False,
) -> Union[
    tuple[CanonicalState, float],
    tuple[CanonicalState, float, np.ndarray],
]:
    """Substrate observation -> canonical state at tau_obs by forward sweep.

    Per mpa-auditor §Q13: replaces the ill-posed backward map.

    canonical_grid: numpy array of shape (N, 2) with columns [chit, gamma_AB].

    return_residual_field: if True, return the full per-grid-point residual
    array alongside the best point. The bootstrap §7 caveat to ship the
    residual field (not just argmin) lives here; consumers compute
    conditioning estimates from this.

    The v0 implementation is brute-force grid search. v2 will add adaptive
    refinement and Bayesian primitives.
    """
    n = canonical_grid.shape[0]
    residuals = np.empty(n, dtype=np.float64)

    # NOTE for native port: this loop is the obvious vectorization target.
    # For v0 Python we keep it readable; numpy SIMD on simple parametric
    # rules is fast enough at the library-cell scale we need.
    for i in range(n):
        chit_c = float(canonical_grid[i, 0])
        gamma_c = float(canonical_grid[i, 1])
        candidate = CanonicalState(chit=chit_c, gamma_AB=gamma_c, tau_obs=tau_obs)
        predicted = apply_translation(candidate, field, tau_obs)
        d_chit = predicted.chit - substrate.chit
        d_gamma = predicted.gamma_AB - substrate.gamma_AB
        residuals[i] = d_chit * d_chit + d_gamma * d_gamma

    best_idx = int(np.argmin(residuals))
    best_state = CanonicalState(
        chit=float(canonical_grid[best_idx, 0]),
        gamma_AB=float(canonical_grid[best_idx, 1]),
        tau_obs=tau_obs,
    )
    best_residual = float(math.sqrt(residuals[best_idx]))

    if return_residual_field:
        return best_state, best_residual, residuals
    return best_state, best_residual


# ---------------------------------------------------------------------------
# Operation 3: tau_obs_sweep
# ---------------------------------------------------------------------------

def tau_obs_sweep(
    substrate_observation: SubstrateState,
    field: TranslationField,
    tau_obs_grid: np.ndarray,
    canonical_search_grid: np.ndarray,
) -> list[CanonicalState]:
    """Walk the RG-flow trajectory across tau_obs at fixed substrate observation.

    Per RFC-S §1: cross-position structure is the flow trajectory itself.

    Note: under the trivial_baseline rule, the trajectory is degenerate
    (canonical state identical at every frame). The migration content
    requires a substrate-conditional translation field.

    Returns a list of CanonicalState, one per tau_obs in the grid.
    """
    trajectory: list[CanonicalState] = []
    for tau_obs in tau_obs_grid:
        state, _ = forward_sweep_invert(
            substrate_observation, field, float(tau_obs), canonical_search_grid
        )
        trajectory.append(state)
    return trajectory


# ---------------------------------------------------------------------------
# Operation 4: regime_at
# ---------------------------------------------------------------------------

def regime_at(
    canonical: CanonicalState,
    tau_obs: float,
    s_window_half_width: float = S_WINDOW_HALF_WIDTH_DEFAULT,
) -> RegimeReading:
    """Classify vertex regime (v9 §Scale-relativity, cdv1 §The chit unit).

    chit > +s_window : c (committed)
    |chit| <= s_window : s (visible strain)
    chit < -s_window : r (reset)

    k_frust is RG-invariant; passed through unchanged.
    """
    chit = canonical.chit
    if chit > s_window_half_width:
        regime = "c"
    elif chit < -s_window_half_width:
        regime = "r"
    else:
        regime = "s"
    return RegimeReading(regime=regime, k_frust=canonical.k_frust)


# ---------------------------------------------------------------------------
# Operation 5: gamut_classify
# ---------------------------------------------------------------------------

def gamut_classify(
    canonical: CanonicalState,
    tau_obs: float,
    gamut: GamutSpec,
) -> dict:
    """Classify in/out of gamut per RFC-S §2.

    Returns {'in_gamut': bool, 'diagnoses': list of {axis, value, range}}.
    """
    diagnoses = []

    if not (gamut.chit_range[0] <= canonical.chit <= gamut.chit_range[1]):
        diagnoses.append({
            "axis": "chit",
            "value": canonical.chit,
            "range": gamut.chit_range,
            "distance": min(
                abs(canonical.chit - gamut.chit_range[0]),
                abs(canonical.chit - gamut.chit_range[1]),
            ),
        })
    if not (gamut.gamma_AB_range[0] <= canonical.gamma_AB <= gamut.gamma_AB_range[1]):
        diagnoses.append({
            "axis": "gamma_AB",
            "value": canonical.gamma_AB,
            "range": gamut.gamma_AB_range,
            "distance": min(
                abs(canonical.gamma_AB - gamut.gamma_AB_range[0]),
                abs(canonical.gamma_AB - gamut.gamma_AB_range[1]),
            ),
        })
    if not (gamut.tau_obs_range[0] <= tau_obs <= gamut.tau_obs_range[1]):
        diagnoses.append({
            "axis": "tau_obs",
            "value": tau_obs,
            "range": gamut.tau_obs_range,
            "distance": min(
                abs(tau_obs - gamut.tau_obs_range[0]),
                abs(tau_obs - gamut.tau_obs_range[1]),
            ),
        })

    return {"in_gamut": len(diagnoses) == 0, "diagnoses": diagnoses}


# ---------------------------------------------------------------------------
# Operation 6: intent_map (I5 only at v0)
# ---------------------------------------------------------------------------

def intent_map(
    out_of_gamut: CanonicalState,
    gamut: GamutSpec,
    intent_id: str,
) -> tuple[CanonicalState, dict]:
    """Map an out-of-gamut canonical state to in-gamut per the chosen intent.

    Per RFC-S §3: "scale uniformly along the gamut to fit, preserving the
    named invariant." One operation, intent-parameterized.

    v0 reference: only I5 (signature-preserving) is implemented. I1-I4 raise.
    """
    if intent_id not in {"I1", "I2", "I3", "I4", "I5"}:
        raise ValueError(f"unknown intent: {intent_id!r}")

    if intent_id != "I5":
        raise NotImplementedError(
            f"intent {intent_id} not implemented in v0 reference (I5-only)"
        )

    # I5 signature-preserving: preserve the regime partition (the FDR-signature
    # universality class). Simplest implementation that preserves regime:
    # clamp to gamut, but if clamping would cross the chit=0 axis (regime
    # boundary), report the partition flip as a sacrifice.
    original_regime = regime_at(out_of_gamut, out_of_gamut.tau_obs).regime

    chit = float(np.clip(
        out_of_gamut.chit, gamut.chit_range[0], gamut.chit_range[1]
    ))
    gamma = float(np.clip(
        out_of_gamut.gamma_AB, gamut.gamma_AB_range[0], gamut.gamma_AB_range[1]
    ))

    mapped = CanonicalState(
        chit=chit,
        gamma_AB=gamma,
        tau_obs=out_of_gamut.tau_obs,
        k_frust=out_of_gamut.k_frust,
    )
    mapped_regime = regime_at(mapped, mapped.tau_obs).regime

    sacrifice = {
        "intent": "I5",
        "delta_chit": chit - out_of_gamut.chit,
        "delta_gamma_AB": gamma - out_of_gamut.gamma_AB,
        "regime_preserved": original_regime == mapped_regime,
        "original_regime": original_regime,
        "mapped_regime": mapped_regime,
    }
    return mapped, sacrifice


# ---------------------------------------------------------------------------
# Operation 7: validate_driver_profile (RFC-S §5 round-trip)
# ---------------------------------------------------------------------------

def validate_driver_profile(
    field: TranslationField,
    reference_dataset: list[dict],
    canonical_search_grid: np.ndarray,
    intent_id: str = "I5",
) -> dict:
    """RFC-S §5 round-trip validation.

    Each reference entry: {
        'canonical_state': CanonicalState,
        'expected_substrate': SubstrateState,
        'tau_obs': float,
    }

    Returns forward + round-trip residuals per entry, plus aggregate stats.
    v0 reference: I5 metric is L2 on canonical state (universality-class
    agreement collapses to regime + chit-distance at scalar shape).
    """
    if intent_id != "I5":
        raise NotImplementedError(
            f"validate_driver_profile intent {intent_id} not implemented in v0"
        )

    forward_residuals: list[float] = []
    round_trip_residuals: list[float] = []
    regime_agreements: list[bool] = []

    for entry in reference_dataset:
        canonical = entry["canonical_state"]
        expected_substrate = entry["expected_substrate"]
        tau_obs = entry["tau_obs"]

        # Forward
        predicted_substrate = apply_translation(canonical, field, tau_obs)
        forward_err = math.sqrt(
            (predicted_substrate.chit - expected_substrate.chit) ** 2
            + (predicted_substrate.gamma_AB - expected_substrate.gamma_AB) ** 2
        )
        forward_residuals.append(forward_err)

        # Round-trip via forward_sweep_invert
        recovered, _ = forward_sweep_invert(
            predicted_substrate, field, tau_obs, canonical_search_grid
        )
        round_trip_err = math.sqrt(
            (recovered.chit - canonical.chit) ** 2
            + (recovered.gamma_AB - canonical.gamma_AB) ** 2
        )
        round_trip_residuals.append(round_trip_err)

        # I5 signature check: regime agreement
        orig_regime = regime_at(canonical, tau_obs).regime
        rec_regime = regime_at(recovered, tau_obs).regime
        regime_agreements.append(orig_regime == rec_regime)

    return {
        "intent": intent_id,
        "forward_residuals": forward_residuals,
        "round_trip_residuals": round_trip_residuals,
        "regime_agreements": regime_agreements,
        "forward_mean": float(np.mean(forward_residuals)),
        "round_trip_mean": float(np.mean(round_trip_residuals)),
        "regime_agreement_rate": float(np.mean(regime_agreements)),
    }
