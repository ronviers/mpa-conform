"""Sensitivity check: run the visual test with a deliberate bug to confirm
the test catches it. Writes out/broken_compare.png alongside the good one
so the user can see them side-by-side.

The bug: a sign flip in the synthetic driver's chit drift term. This is a
subtle one-character error of the type that would actually happen during
a Rust port. The two curves should now visibly miss.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math

sys.path.insert(0, str(Path(__file__).parent))

from mpa_scale_solver import (
    CanonicalState,
    apply_translation,
    forward_sweep_invert,
    analytical_canonical_chit,
)
from mpa_scale_solver.types import TranslationField


# --- Build a "buggy" version of the driver. Same as aging_log but with the
# --- sign of the drift term flipped. The analytical truth is unchanged (it
# --- represents what the math SHOULD do); the solver now computes against
# --- the buggy forward map.

class BuggyTranslationField:
    """Wraps a normal TranslationField; the forward map flips the chit-drift sign."""
    form = "parametric"
    def __init__(self, params):
        self.params = params


def _buggy_apply(canonical, field, tau_obs):
    """Same as aging_log but with -drift instead of +drift on chit. A sign bug."""
    a = field.params["chit_aging_coeff"]
    tau_aging = field.params["tau_aging"]
    drift = math.log1p(tau_obs / tau_aging)
    from mpa_scale_solver.types import SubstrateState
    return SubstrateState(
        chit=canonical.chit - a * drift,   # BUG: should be + a * drift
        gamma_AB=canonical.gamma_AB,
    )


# Patch the operations module's apply_translation to use the buggy version.
# This simulates a port that silently broke the chit-drift sign.
import mpa_scale_solver.operations as ops
_ORIGINAL_APPLY = ops.apply_translation
ops.apply_translation = _buggy_apply


def run_buggy():
    # Same setup as the good test
    CHIT_AGING_COEFF = 1.0
    TAU_AGING = 1.0
    CHIT_REF = 2.0
    GAMMA_REF = -0.5
    TAU_OBS_REF = 1.0
    TAU_OBS_GRID = np.logspace(-2, 2, 80)

    CHIT_SEARCH_AXIS = np.linspace(-5.0, 5.0, 1001)
    GAMMA_SEARCH_AXIS = np.linspace(-1.0, 0.0, 11)
    cg, gg = np.meshgrid(CHIT_SEARCH_AXIS, GAMMA_SEARCH_AXIS, indexing="ij")
    SEARCH_GRID = np.column_stack([cg.ravel(), gg.ravel()])

    driver = BuggyTranslationField(params={
        "rule": "aging_log",
        "chit_aging_coeff": CHIT_AGING_COEFF,
        "tau_aging": TAU_AGING,
    })

    # Substrate observation computed against the BUGGY forward map
    canonical_ref = CanonicalState(chit=CHIT_REF, gamma_AB=GAMMA_REF, tau_obs=TAU_OBS_REF)
    substrate = ops.apply_translation(canonical_ref, driver, TAU_OBS_REF)

    # Analytical truth: same closed-form as before (what the math should produce)
    # But we have to use the GOOD analytical for the GOOD substrate observation.
    # Let's compute the analytical as it would be against the good math:
    # If the good forward map were used, substrate_chit_good = 2.0 + log(2) ~ 2.693
    # The good analytical: canonical_chit(tau) = 2.693 - log(1 + tau)
    good_substrate_chit = CHIT_REF + CHIT_AGING_COEFF * math.log1p(TAU_OBS_REF / TAU_AGING)

    analytical = np.array([
        analytical_canonical_chit(good_substrate_chit, float(t), CHIT_AGING_COEFF, TAU_AGING)
        for t in TAU_OBS_GRID
    ])
    numerical = np.empty(len(TAU_OBS_GRID))
    for i, tau in enumerate(TAU_OBS_GRID):
        state, _ = forward_sweep_invert(substrate, driver, float(tau), SEARCH_GRID)
        numerical[i] = state.chit

    return TAU_OBS_GRID, analytical, numerical


def main():
    print("Running BUGGY test (sign-flipped chit drift in the solver) ...")
    tau_obs_grid, analytical, numerical = run_buggy()

    residuals = numerical - analytical
    max_abs_residual = np.max(np.abs(residuals))
    print(f"  max |residual| = {max_abs_residual:.4f}")
    print(f"  tolerance      = 0.0100")
    print(f"  passes:        = {max_abs_residual <= 0.01}")

    # Plot side-by-side
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    log_tau = np.log10(tau_obs_grid)

    s_width = 0.30
    chit_min = min(analytical.min(), numerical.min(), -2.5)
    chit_max = max(analytical.max(), numerical.max(), 3.0)
    ax.axhspan(s_width, chit_max, color=(0.85, 1.00, 0.85), alpha=0.55, zorder=0)
    ax.axhspan(-s_width, s_width, color=(1.00, 0.95, 0.80), alpha=0.55, zorder=0)
    ax.axhspan(chit_min, -s_width, color=(1.00, 0.85, 0.85), alpha=0.55, zorder=0)

    ax.plot(log_tau, analytical, color=(0.20, 0.40, 0.85), linewidth=4.0, alpha=0.85,
            label="analytical (what math SHOULD do)", zorder=3)
    ax.plot(log_tau, numerical, color=(0.85, 0.20, 0.20), linewidth=1.5, linestyle="--",
            marker="o", markersize=5, label="numerical (BUG: sign flip in solver)", zorder=4)

    ax.set_xlim(log_tau.min(), log_tau.max())
    ax.set_ylim(chit_min, chit_max)
    ax.set_xlabel(r"$\log_{10}(\tau_{obs})$", fontsize=13)
    ax.set_ylabel(r"canonical $\chi$ (chit)", fontsize=13)
    ax.grid(True, alpha=0.25, linestyle=":")
    ax.axhline(0, color=(0.4, 0.4, 0.4), linewidth=0.8, alpha=0.6)
    ax.set_title(
        f"SENSITIVITY CHECK: deliberate sign-flip bug in solver\n"
        f"max |residual| = {max_abs_residual:.4f}   tolerance = 0.0100   [FAIL — curves visibly diverge]",
        fontsize=13, color=(0.75, 0.15, 0.15)
    )
    ax.legend(loc="upper right", fontsize=11, framealpha=0.85)

    out_path = Path(__file__).parent / "out" / "broken_compare.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"\nwrote {out_path}")
    print("compare this to out/migration_compare.png — the good run.")


if __name__ == "__main__":
    main()
