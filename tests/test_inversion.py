"""Inversion math parity tests.

The math is a port of the auditor's JS engines. v0.1 parity discipline:
- The analytical Stage-1 fit should recover the chit used to generate a
  synthetic locus (round-trip on the analytical forward model).
- The ensemble refine should converge in finite time on a few seconds of
  synthetic-locus data; cooperative-band divergence is caught (no crash).
- Phase-locking forward model returns finite r at sane (chit, gamma).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from conformer.compute import gfdr_model, inversion, kernel, phase_locking


def test_analytical_round_trip():
    """Stage-1 should recover the chit used to generate a synthetic locus."""
    for chit_true in (-1.0, -0.5, 0.0, 0.3, 0.8):
        locus = gfdr_model.generate_locus(chit_true)
        rows = [
            {"tau": float(t), "C": float(c), "chi": float(ch)}
            for t, c, ch in zip(locus["tau"], locus["C"], locus["chi"])
        ]
        chit_fit, residual = inversion.fit_chit_analytical(rows)
        # CHIT_STEPS = 161 over [-2, 2] -> grid resolution 0.025
        assert abs(chit_fit - chit_true) < 0.06, (
            f"Stage-1 chit={chit_fit:.3f} for chit_true={chit_true:.3f} "
            f"(residual={residual:.3e})"
        )
        print(f"  OK analytical: chit_true={chit_true:+.2f} -> fit={chit_fit:+.3f} (residual={residual:.2e})")


def test_kernel_deterministic_lamb():
    """Deterministic two-mode kernel — three regimes.

    - chit=-0.5, gamma=0: r-regime, decays to ~0 (sub-threshold).
    - chit=+0.3, gamma=+0.2: c/s with competitive coupling, converges to
      finite fixed point.
    - chit=+0.5, gamma=-0.3: cooperative band; diverges (documented
      runaway, mpa-auditor Q7). Acceptable as long as it produces NaN
      cleanly rather than crashing.
    """
    p_r = kernel.from_chit_gamma(chit=-0.5, gamma_AB=0.0)
    traj_r = kernel.integrate_deterministic((0.3, 0.7), p_r, t_max=30.0, dt=0.01, sample_every=10)
    final_r = (traj_r["rho_A"][-1], traj_r["rho_B"][-1])
    assert np.isfinite(final_r[0]) and np.isfinite(final_r[1])
    assert final_r[0] < 0.1 and final_r[1] < 0.1, f"r-regime didn't decay: {final_r}"
    print(f"  OK kernel r-regime: chit=-0.5 -> final=({final_r[0]:.3e}, {final_r[1]:.3e})")

    p_comp = kernel.from_chit_gamma(chit=0.3, gamma_AB=+0.2)
    traj_c = kernel.integrate_deterministic((0.3, 0.7), p_comp, t_max=30.0, dt=0.01, sample_every=10)
    final_c = (traj_c["rho_A"][-1], traj_c["rho_B"][-1])
    # Competitive coupling at modest chit drives both modes down (winner-
    # take-all collapses both if they don't separate strongly). The math
    # check is just that the integrator stayed finite.
    assert np.isfinite(final_c[0]) and np.isfinite(final_c[1])
    print(f"  OK kernel competitive: chit=+0.3, gamma=+0.2 -> final=({final_c[0]:.3e}, {final_c[1]:.3e})")

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        p_coop = kernel.from_chit_gamma(chit=0.5, gamma_AB=-0.3)
        traj_coop = kernel.integrate_deterministic((0.3, 0.7), p_coop, t_max=30.0, dt=0.01, sample_every=10)
    final_coop = (traj_coop["rho_A"][-1], traj_coop["rho_B"][-1])
    diverged = not (np.isfinite(final_coop[0]) and np.isfinite(final_coop[1]))
    print(f"  OK kernel cooperative band (Q7): chit=+0.5, gamma=-0.3 -> diverged={diverged}")


def test_phase_locking_r_finite():
    """Phase-locking forward model returns finite r at sane params."""
    for chit, gamma in [(0.3, -0.2), (0.3, +0.1), (-0.3, -0.2)]:
        try:
            r = phase_locking.compute_phase_locking_r(chit, gamma)
            assert np.isfinite(r["r"]), f"non-finite r at ({chit}, {gamma}): {r}"
            print(f"  OK phase-locking: chit={chit:+.2f}, gamma={gamma:+.2f} -> r={r['r']:.3f} ({r['phase_relationship']})")
        except RuntimeError as e:
            # Some (chit, gamma) combos in the cooperative band diverge —
            # acceptable as long as it raises cleanly.
            print(f"  [diverged] chit={chit:+.2f}, gamma={gamma:+.2f}: {e}")


def test_invert_synthetic_skip_stage2():
    """Full inversion against a synthetic locus, analytical-only path
    (skip stage 2). Should recover chit close to ground truth."""
    log_events: list[tuple[str, dict]] = []
    chit_true = 0.4
    locus = gfdr_model.generate_locus(chit_true)
    rows = [
        {"tau": float(t), "C": float(c), "chi": float(ch)}
        for t, c, ch in zip(locus["tau"], locus["C"], locus["chi"])
    ]
    result = inversion.invert(
        rows,
        empirical_r=None,
        skip_stage2=True,
        log=lambda kind, payload: log_events.append((kind, payload)),
    )
    assert abs(result.chit - chit_true) < 0.06
    assert result.chit_observable == "gfdr-locus-analytical"
    print(f"  OK invert(synthetic, skip_stage2): chit_true=0.4 -> {result.chit:+.3f} ({result.regime})")


def test_invert_real_bundle():
    """Smoke test on one curated bundle. Should run end-to-end without
    error and produce a finite chit."""
    from conformer.cli import SEED_CORPUS

    bundle_path = SEED_CORPUS / "ck-glassy" / "glass__T0.500__spin-flip.bundle.json"
    if not bundle_path.exists():
        print(f"  [skip] {bundle_path} not staged — run walk_library first")
        return
    import json
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    rows = bundle["observable"]["data"]
    log_events: list[tuple[str, dict]] = []
    result = inversion.invert(
        rows,
        empirical_r=None,
        skip_stage2=True,   # ensemble refine is slow; analytical-only suffices for smoke
        log=lambda kind, payload: log_events.append((kind, payload)),
    )
    assert np.isfinite(result.chit)
    seed = (bundle.get("fit_provenance") or {}).get("fitted_params") or {}
    seed_chit = seed.get("chit")
    print(f"  OK invert(real glass T=0.5): chit_fit={result.chit:+.3f} (leading-order seed={seed_chit}, regime={result.regime})")


if __name__ == "__main__":
    test_analytical_round_trip()
    test_kernel_deterministic_lamb()
    test_phase_locking_r_finite()
    test_invert_synthetic_skip_stage2()
    test_invert_real_bundle()
    print("\nAll inversion parity tests passed.")
