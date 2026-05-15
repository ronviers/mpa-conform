"""Substrate-class translation field — forward half, leading order.

Maps library cell (substrate, operating_point) tuples to canonical MPA
parameters (chit, gamma_AB) at the operating point. This is the *forward*
half of the translation field per mpa-auditor §Q13 (forward-only audit):
canonical -> substrate-native is built; substrate-native -> canonical is
never built. The values here are leading-order placeholders; they refine
as substrate-side measurement lands (same posture as tau_env_analytic).

Convention follows cdv1 §Bridge to v9:
- chit >> 0   -> c (committed / saturated holding)
- chit ~ 0+   -> s (suspended / aging diagonal, CK universality)
- chit < 0    -> r (reset / sub-threshold decay)
- gamma_AB < 0 cooperative; ~ 0 orthogonal; > 0 conflicting (k_frust signal)
"""
from __future__ import annotations

import math
from typing import Optional

# Substrate -> mpa-auditor corpus class id (corpus/substrate-classes.json).
# Brain uses 'neural-population' (closest match in the seeded 12-class
# roster). Surface this choice in the README + next-session handoff for
# user review; an alternative would be to coin 'mpa-brain-langevin' as a
# new class, but that is a class-genesis decision deferred to a foundational
# session.
SUBSTRATE_TO_CLASS_ID = {
    "glass": "ck-glassy",
    "quantum": "surface-code-qec",
    "brain": "neural-population",
}

# Glass critical temperature for the library's 3D EA Ising model.
# Library T grid spans 0.20-1.80 around Tc~0.95-1.00; cdv1 reads the
# s-regime as the aging-CK window near Tc. Using Tc=1.0 as the leading-
# order placeholder (LIBRARY_SPEC.md notes T grid is "spanning Tc~0.95").
_TC_GLASS = 1.0

# Surface-code distance-3 threshold. Library p_base grid spans 1e-4..5e-2
# around the ~1% threshold for distance-3 rotated memory-Z.
_P_THRESHOLD_QEC = 1e-2

# Brain scenario -> (chit, gamma_AB) at leading order. Bootstrap §5:
# committed -> c; suspended -> s; conflict -> k_frust; reset -> r.
_BRAIN_SCENARIO_TABLE = {
    "committed": {"chit": +1.0, "gamma_AB": -0.5, "k_frust": False},
    "suspended": {"chit": +0.05, "gamma_AB": 0.0, "k_frust": False},
    "conflict":  {"chit": 0.0,   "gamma_AB": +0.5, "k_frust": True},
    "reset":     {"chit": -1.0,  "gamma_AB": 0.0, "k_frust": False},
}


def canonical_params(substrate: str, operating_point: dict) -> dict:
    """Return {chit, gamma_AB, k_frust, method} for a library cell's op point.

    Note on the cdv1/bootstrap glass sign convention. The bootstrap §5 reads
    "T < Tc -> chit << 0 (s-aging)"; cdv1 reads chit < 0 as r-regime, chit
    ~ 0+ as s-regime. The cdv1 convention is the canonical one (chit =
    ln(G_0/L), positive chit = above threshold). EA glass below Tc is the
    aging-CK phase, which is the s-regime in MPA terms. Below Tc, the
    library cells have gt='s' in their operating_point (a confirming
    receipt). So we use chit = (Tc - T), which gives chit > 0 below Tc
    (saturated/aging side) and chit < 0 above Tc (paramagnetic/r side).
    See docs/foundational-questions.md Q-glass-chit-sign for the open note.
    """
    if substrate == "glass":
        T = operating_point.get("T")
        if T is None:
            raise ValueError(f"glass cell missing T in operating_point: {operating_point}")
        chit = _TC_GLASS - float(T)
        return {
            "chit": chit,
            "gamma_AB": 0.0,
            "k_frust": False,
            "method": f"leading_order: chit = Tc - T, Tc={_TC_GLASS}",
        }

    if substrate == "quantum":
        p = operating_point.get("p_base")
        if p is None or p <= 0:
            raise ValueError(f"quantum cell missing p_base in operating_point: {operating_point}")
        chit = math.log(_P_THRESHOLD_QEC / float(p))
        return {
            "chit": chit,
            "gamma_AB": 0.0,
            "k_frust": False,
            "method": f"leading_order: chit = ln(p_threshold / p_base), p_threshold={_P_THRESHOLD_QEC}",
        }

    if substrate == "brain":
        scenario = operating_point.get("scenario") or operating_point.get("label")
        row = _BRAIN_SCENARIO_TABLE.get(scenario)
        if row is None:
            raise ValueError(f"brain cell unknown scenario: {scenario}")
        return {
            "chit": row["chit"],
            "gamma_AB": row["gamma_AB"],
            "k_frust": row["k_frust"],
            "method": f"leading_order: brain scenario table -> ({scenario})",
        }

    raise ValueError(f"unknown substrate: {substrate}")


def class_id_for(substrate: str) -> str:
    cid = SUBSTRATE_TO_CLASS_ID.get(substrate)
    if cid is None:
        raise ValueError(f"unknown substrate: {substrate}")
    return cid


def tau_obs_aggregated_note(substrate: str) -> Optional[str]:
    """The curator path reads all_samples' top-level C_mean / chi_mean, which
    is window-aggregated across the 31 tau_obs windows. Document the choice
    so the auditor's tau_obs.method = 'aggregated' carries the why.
    """
    return (
        "Curator path: top-level C_mean/chi_mean from grind cell's "
        "all_samples — aggregated across the 31 tau_obs windows the cell "
        "carries. Per-window slicing is deferred (bootstrap §5 step 2)."
    )
