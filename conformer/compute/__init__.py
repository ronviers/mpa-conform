"""Compute kernel for mpa-conform.

Port of the auditor's forward physics + inversion stack to Python, per
the program-wide rebalance (H:/mpa-central/SUITE_BLOCK_IN.md). The
viewer layer (mpa-auditor) reads what conform produces; live numerics
live here.

Modules:
- kernel: universal two-mode kernel (cdv1 §Universal two-mode kernel)
  with Lamb stationary closure. Deterministic RK4 + stochastic
  Euler-Maruyama, vectorized over the ensemble axis. Linearization at
  a state.
- observables: correlator C(tau), direct-perturbation response chi(tau),
  Onsager-normalized gFDR locus.
- gfdr_model: leading-order analytical gFDR locus (port of
  math/gfdr-model.js).
- phase_locking: Kuramoto r forward model for gamma_AB inversion (port
  of math/phase-locking-model.js).
- inversion: two-stage fit (analytical localize + ensemble refine) +
  phase-locking gamma_AB fit (port of engines/inversion-engine.js).

Pure-Python via numpy. Vendoring mpa-solver's pybind11 build is a
future optimization once the math parity holds.
"""
