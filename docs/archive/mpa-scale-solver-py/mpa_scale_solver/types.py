"""Plain dataclasses for the scale-solver's data shapes.

Conventions for native-port readiness:
- Stateless. No methods that mutate.
- Plain data, no class hierarchy. Direct port to Rust structs / C++ POD.
- Type-hinted. numpy arrays only for vectorized operations, not stored state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal


# Canonical state lives at a particular tau_obs camera frame.
# Per RFC-S §1: this is a position on the RG-flow trajectory.
@dataclass
class CanonicalState:
    """Substrate-neutral state at observer position p = tau_obs.

    Per RFC-S §1: the canonical representation at p is the fixed-point set
    of the Compression Axiom's RG flow at level n, restricted to the
    substrate's reachable trajectory.

    chit: log gain/loss ratio (cdv1 §The chit unit). Regime axis.
    gamma_AB: signed shear (v9 §Three typed objects). Cooperativity axis.
    tau_obs: observer position the state is referenced to.
    k_frust: optional topological invariant (v9 §Three typed objects);
        RG-invariant when carried.
    """

    chit: float
    gamma_AB: float
    tau_obs: float
    k_frust: Optional[int] = None


# Substrate state shape is driver-profile-dependent in general.
# For the v0 reference and the synthetic driver: scalar (chit, gamma_AB)
# in substrate-native units. Real driver profiles will carry richer shape
# (e.g., raw correlator data, syndrome streams, fluctuation traces).
@dataclass
class SubstrateState:
    """Substrate-native observation. Driver-profile-conditional shape.

    For the v0 Python reference: scalar (chit, gamma_AB) as the substrate
    would report them through its calibration. A non-trivial translation
    field can make substrate-native (chit, gamma_AB) differ from canonical.
    """

    chit: float
    gamma_AB: float


@dataclass
class TranslationField:
    """Driver-profile-supplied substrate <-> canonical map (RFC-S §4).

    The translation field is parametrized by tau_obs. Three supported forms;
    the solver dispatches on form, does NOT inspect substrate-specific content.

    form='parametric': params carries a 'rule' name + rule-specific params.
        v0 rules:
          - 'trivial_baseline': Wilson-Kadanoff fixed-point identity.
            Produces NO migration.
          - 'aging_log': synthetic substrate-conditional flow.
            substrate_chit = canonical_chit + a*log(1 + tau_obs/tau_aging).
            Produces a c->s->r migration when canonical state is inverted
            at fixed substrate observation across a tau_obs sweep.

    form='lookup': params carries a tabulated map. Not implemented in v0
        Python reference.

    form='learned': params carries fitted-family parameters. Not implemented
        in v0 Python reference.
    """

    form: Literal["parametric", "lookup", "learned"]
    params: dict


@dataclass
class GamutSpec:
    """Substrate gamut: image of the RG trajectory in canonical space (RFC-S §2).

    v0 Python reference: scalar axis ranges. Real driver profiles will carry
    structured per-axis content (trail-class structure, persistence depth,
    contraction-rate envelopes).
    """

    chit_range: tuple[float, float]
    gamma_AB_range: tuple[float, float]
    tau_obs_range: tuple[float, float]
    persistence_depth: int = 0


@dataclass
class RegimeReading:
    """Vertex regime at tau_obs (v9 §Scale-relativity).

    regime: one of 'c' (committed), 's' (visible strain), 'r' (reset).
    k_frust: topological invariant if the substrate carries it.
    """

    regime: Literal["c", "s", "r"]
    k_frust: Optional[int] = None
