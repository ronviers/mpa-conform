"""mpa-scale-solver — Python reference implementation (pre-build).

This package is the math-first Python reference for the scale-management kernel.
It exists to validate the seven operations in the bootstrap §4 against the
framework's primary cross-substrate test (cdv1 §gFDR signatures: chit reading
of the s → r migration) BEFORE a native (Rust/C++) build is committed.

Authority chain:
- Spec: H:/mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md (RFC-S §§0-5)
- Anchors: v9 §Foundational principles + §Scale-relativity + §Compression Axiom
- Load-bearing prediction: cdv1 §gFDR signatures (c → s → r migration)
- Build bootstrap: mpa-scale-solver-bootstrap.md (this package fills §5)

The v0 baseline rule is the Wilson-Kadanoff fixed-point rule: time rescaling
only, with gamma and chit identity. Non-trivial RG flow content (gamma flow,
chit flow under coarse-graining) is supplied by driver profiles via the
substrate-conditional translation field. The solver dispatches; the driver
carries the physics.
"""

from .types import (
    CanonicalState,
    SubstrateState,
    TranslationField,
    GamutSpec,
    RegimeReading,
)
from .operations import (
    apply_translation,
    forward_sweep_invert,
    tau_obs_sweep,
    regime_at,
    gamut_classify,
    intent_map,
    validate_driver_profile,
)
from .synthetic import (
    make_synthetic_aging_driver,
    analytical_canonical_chit,
)

__all__ = [
    "CanonicalState",
    "SubstrateState",
    "TranslationField",
    "GamutSpec",
    "RegimeReading",
    "apply_translation",
    "forward_sweep_invert",
    "tau_obs_sweep",
    "regime_at",
    "gamut_classify",
    "intent_map",
    "validate_driver_profile",
    "make_synthetic_aging_driver",
    "analytical_canonical_chit",
]
