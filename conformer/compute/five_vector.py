"""Five-vector (KWW + FDT-violation) inversion.

Blocked-in 2026-05-19; multi-start + domain-of-validity gate added and validated
2026-05-21. See
[`docs/five_vector_inversion_blockin.md`](../../docs/five_vector_inversion_blockin.md)
for the design and the validation contract, and
[`H:/mpa-central/FALSIFICATION.md`](H:/mpa-central/FALSIFICATION.md)
"KEY FINDING" / "FINDING 2" for why this is the keystone owed item
(X-recovery AND a domain-of-validity gate both depend on it).

The 1-param production inversion (`inversion.invert`) fits only the cdv1
`chit`. It cannot recover the substrate-thermodynamic refinement
(q_EA, tau_alpha, beta_KWW, tau_beta, X) that `gfdr_model.
generate_kww_glass_locus` *generates*. This module inverts that generator.

Stage shape (mirrors v0.2 two-stage; see blockin doc §Algorithm):
  Stage 1  cdv1 anchor: chit from `inversion.fit_chit_analytical` (reused,
           not reimplemented). Fixed during stage 2.
  Stage 2  numerical refine: least-squares the 5 glass params against
           `generate_kww_glass_locus(chit, ...)`, evaluated at the cell's
           dimensionless lag tau. T is fixed per substrate (sets the FDT
           slope 1/T); it is NOT a free parameter.

STATUS (2026-05-21): validated on the control ladder via
`scripts/test_five_vector_fit.py`.
  - X-recovery: `two_temp_ou` X=0.5/0.1 recovered to <=0.01.
  - FULL 5-vector round-trip: `kww_oracle` (genuine two-timescale) recovers
    (q_EA, tau_alpha, beta_KWW, tau_beta, X) within the resolution floor.
  - Multi-start (`_SEEDS`) removes the local-minimum risk the first cut had.
  - DOMAIN GATE (`RESIDUAL_GATE`, `FiveVectorFit.in_domain`) closes
    FALSIFICATION.md FINDING 2: `sine_wave` (cosine) and the running
    `driven_ring` NESS fit at RMS ~0.14-0.45 -> flagged OUT (their X is not a
    meaningful KWW-FDT violation); in-family cells (controls, r-regime glass)
    fit at RMS ~0.01-0.02 -> IN. This is how X-recovery "comes along for the
    ride": recovered where the family applies, gated where it does not.
REMAINING (blockin doc §"What's left"): integration into `invert()` + the
bundle schema (#4); production aging-glass validation (#6) is blocked on the
library's null tau_env below Tc (camera-scale not placed — see the
substrate-inversion finding); T-as-6th-param is deferred (fixed from the
operating point).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

from . import gfdr_model
from . import inversion


@dataclass
class FiveVectorFit:
    chit: float          # cdv1 anchor (stage 1, fixed through stage 2)
    q_EA: float
    tau_alpha: float
    beta_KWW: float
    tau_beta: float
    X: float
    T: float
    residual: float      # RMS of the joint (C, chi) residual
    success: bool
    n_eval: int
    in_domain: bool = True   # domain gate: is the cell in the KWW-FDT family?
    channel_snr: dict = field(default_factory=dict)    # {"C","chi"}: RMS resid / RMS sem (inf if floor~0)
    channel_floor: dict = field(default_factory=dict)  # {"C","chi"}: RMS sem (the grain) per channel
    identifiability: object = None   # Identifiability (bootstrap per-param confidence) or None
    notes: list = field(default_factory=list)


@dataclass
class Identifiability:
    """Per-parameter bootstrap confidence. `identified[p]` is the verdict that matters:
    True means the data pins parameter p; False means it's mush (wide spread) or railed
    at a bound, even if the overall fit is in-domain."""
    n_boot: int
    std: dict          # {param: bootstrap std}
    spread: dict       # {param: CV for timescales, abs std for bounded} -- the gated quantity
    identified: dict   # {param: bool}
    railed: dict       # {param: bool} -- point fit sits at a parameter bound
    notes: list = field(default_factory=list)

    @property
    def assessable(self) -> bool:
        return self.n_boot > 0


# Param order: (q_EA, tau_alpha, beta_KWW, tau_beta, X). chit + T are fixed.
_LOWER = np.array([0.01, 1e-3, 0.10, 1e-4, 0.0])
_UPPER = np.array([1.00, 1e3,  1.00, 1e2,  1.0])

# Multi-start seeds: span short/long timescales and low/high plateau so the fit does
# not stick in a local minimum on genuine two-timescale cells (blockin "what's left" #2).
_SEEDS = [
    np.array([0.70, 1.0,  0.70, 0.05, 0.5]),
    np.array([0.50, 0.3,  0.60, 0.02, 0.5]),
    np.array([0.85, 5.0,  0.50, 0.10, 0.5]),
    np.array([0.40, 1.0,  0.80, 0.01, 0.8]),
    np.array([0.90, 0.5,  0.60, 0.05, 0.2]),
    np.array([0.65, 2.0,  0.65, 0.20, 0.5]),
]

# Domain-of-validity gate (closes FALSIFICATION.md FINDING 2). Calibrated on the control
# ladder: in-family cells (two_temp_ou, kww_oracle) fit to RMS ~0.02; a cosine (sine_wave,
# not in the KWW-FDT family) sticks at ~0.4. The threshold sits an order of magnitude above
# the in-family floor and well below the out-of-family residual. Production glass should be
# re-checked against this floor when it lands (blockin "what's left" #6).
RESIDUAL_GATE = 0.10

# Per-channel signal-to-noise gate (the principled successor to the scalar RESIDUAL_GATE):
# a channel's fit residual must stay within SNR_GATE x its own noise floor (RMS SEM). A cell
# is in-domain iff every channel that carries grain passes; channels reporting ~zero noise
# (e.g. an analytic oracle's chi) cannot be whitened and are excluded, not divided by. Used
# only when the rows carry C_sem/chi_sem; otherwise the scalar RESIDUAL_GATE applies.
# Calibrated on the control ladder: in-family C lands ~0.8x grain, out-of-family C ~20x.
SNR_GATE = 2.0
_FLOOR_EPS = 1e-9


def _rms(a: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(a, float) ** 2)))


# Identifiability gate -- ORTHOGONAL to the domain gate. The domain gate asks "is this in the
# KWW-FDT family?" (residual vs grain). Identifiability asks "is each parameter actually pinned
# by the data?" A fit can be IN-family with X pinned but the timescales mush -- goodness-of-fit
# is not identifiability. Signal: parametric-bootstrap spread per parameter (perturb the data
# within its grain, refit, measure the spread). A parameter is "identified" only if its spread
# is tight AND it isn't railed at a bound (a railed param has zero spread but is unconstrained,
# not pinned). Bounded params (q_EA, beta_KWW, X in [0,1]) use absolute bootstrap std; timescales
# (tau_alpha, tau_beta) use coefficient of variation. Calibrated on the kww_oracle noise sweep:
# X/q_EA/beta land at std <0.10; tau_beta blows past CV 0.25 where the fast relaxation is
# below resolution.
BOUNDED_STD_GATE = 0.10
TIMESCALE_CV_GATE = 0.25
_PARAM_NAMES = ("q_EA", "tau_alpha", "beta_KWW", "tau_beta", "X")
_BOUNDED = ("q_EA", "beta_KWW", "X")
_TIMESCALE = ("tau_alpha", "tau_beta")


def _model_at(params, chit: float, T: float, tau_query: np.ndarray):
    q_EA, tau_alpha, beta_KWW, tau_beta, X = params
    locus = gfdr_model.generate_kww_glass_locus(
        chit, q_EA=q_EA, tau_alpha=tau_alpha, beta_KWW=beta_KWW,
        tau_beta=tau_beta, X=X, T=T,
    )
    Cs = np.array([gfdr_model._interp_log_tau(locus, float(t))[0] for t in tau_query])
    chis = np.array([gfdr_model._interp_log_tau(locus, float(t))[1] for t in tau_query])
    return Cs, chis


def fit_kww5(
    rows: list[dict],
    *,
    chit_prior: Optional[float] = None,
    T: float = 1.0,
    seed: Optional[Sequence[float]] = None,
    n_boot: int = 0,
) -> FiveVectorFit:
    """First-cut 5-vector fit. `rows`: [{"tau","C","chi"}] in dimensionless
    lag (lag / tau_scale). `chit_prior`: cdv1 anchor; if None, fit it via
    stage 1. `T`: fixed FDT-slope temperature (NOT a free param). `n_boot`:
    if > 0, run a parametric bootstrap (perturb the data within its grain,
    refit) to assess per-parameter identifiability; needs SEM in the rows."""
    from scipy.optimize import least_squares

    finite = [
        r for r in rows
        if all(k in r for k in ("tau", "C", "chi"))
        and all(np.isfinite(float(r[k])) for k in ("tau", "C", "chi"))
    ]
    if len(finite) < 5:
        raise ValueError(f"need >=5 usable rows for a 5-param fit, got {len(finite)}")

    if chit_prior is None:
        chit_prior, _ = inversion.fit_chit_analytical(finite)

    tau = np.array([float(r["tau"]) for r in finite])
    C = np.array([float(r["C"]) for r in finite])
    chi = np.array([float(r["chi"]) for r in finite])

    def resid(p):
        Cm, chim = _model_at(p, float(chit_prior), float(T), tau)
        return np.concatenate([C - Cm, chi - chim])

    starts = [np.asarray(seed, dtype=float)] if seed is not None else _SEEDS
    best = None
    n_eval = 0
    for p0 in starts:
        res = least_squares(resid, p0, bounds=(_LOWER, _UPPER), max_nfev=4000)
        n_eval += int(res.nfev)
        rms = float(np.sqrt(np.mean(res.fun ** 2)))
        if best is None or rms < best[0]:
            best = (rms, res)
    rms, res = best
    q_EA, tau_alpha, beta_KWW, tau_beta, X = res.x
    notes = [f"multi-start ({len(starts)} seeds); best RMS {rms:.4f}"]

    # Per-channel signal-to-noise gate, when the cell carries grain (C_sem/chi_sem).
    C_sem = np.array([float(r.get("C_sem", 0.0) or 0.0) for r in finite])
    chi_sem = np.array([float(r.get("chi_sem", 0.0) or 0.0) for r in finite])
    Cm, chim = _model_at(res.x, float(chit_prior), float(T), tau)
    floor = {"C": _rms(C_sem), "chi": _rms(chi_sem)}
    snr = {
        "C": (_rms(C - Cm) / floor["C"]) if floor["C"] > _FLOOR_EPS else float("inf"),
        "chi": (_rms(chi - chim) / floor["chi"]) if floor["chi"] > _FLOOR_EPS else float("inf"),
    }
    whitenable = [ch for ch in ("C", "chi") if floor[ch] > _FLOOR_EPS]

    if whitenable:
        in_domain = all(snr[ch] <= SNR_GATE for ch in whitenable)
        deterministic = [ch for ch in ("C", "chi") if floor[ch] <= _FLOOR_EPS]
        notes.append("per-channel S/N gate: "
                     + ", ".join(f"{ch} {snr[ch]:.1f}x grain" for ch in whitenable)
                     + (f"; {','.join(deterministic)} deterministic (excluded)" if deterministic else ""))
        if not in_domain:
            loud = [ch for ch in whitenable if snr[ch] > SNR_GATE]
            notes.append(f"OUT OF DOMAIN: {','.join(loud)} residual exceeds {SNR_GATE}x its grain "
                         "— signal the KWW-FDT family can't capture; X is not a meaningful "
                         "FDT-violation here.")
    else:
        in_domain = rms < RESIDUAL_GATE   # no grain in the rows -> fall back to the scalar gate
        notes.append(f"no SEM in rows; scalar gate RMS {rms:.3f} vs {RESIDUAL_GATE}")
        if not in_domain:
            notes.append(f"OUT OF DOMAIN: residual {rms:.3f} >= gate {RESIDUAL_GATE} — "
                         "not in the KWW-FDT family; X is not a meaningful FDT-violation here.")

    result = FiveVectorFit(
        chit=float(chit_prior), q_EA=float(q_EA), tau_alpha=float(tau_alpha),
        beta_KWW=float(beta_KWW), tau_beta=float(tau_beta), X=float(X), T=float(T),
        residual=rms, success=bool(res.success), n_eval=n_eval,
        in_domain=bool(in_domain), channel_snr=snr, channel_floor=floor, notes=notes,
    )
    if n_boot > 0:
        result.identifiability = bootstrap_identifiability(
            finite, chit_prior=float(chit_prior), T=float(T),
            point_params=(q_EA, tau_alpha, beta_KWW, tau_beta, X), n_boot=n_boot,
        )
        if result.identifiability.assessable:
            unid = [p for p in _PARAM_NAMES if not result.identifiability.identified[p]]
            notes.append("identifiable: "
                         + ", ".join(p for p in _PARAM_NAMES if result.identifiability.identified[p])
                         + (f"; NOT identified: {', '.join(unid)}" if unid else "; all params pinned"))
    return result


def bootstrap_identifiability(
    finite_rows: list[dict],
    *,
    chit_prior: float,
    T: float,
    point_params: Sequence[float],
    n_boot: int = 24,
    seed: int = 0,
) -> "Identifiability":
    """Parametric bootstrap: perturb (C, chi) within the rows' grain (C_sem/chi_sem),
    refit, and measure the per-parameter spread. A parameter is `identified` only if its
    spread is below threshold AND the point fit isn't railed at a bound. Needs SEM in the
    rows; without grain, identifiability is not assessable (n_boot reported as 0)."""
    tau = np.array([float(r["tau"]) for r in finite_rows])
    C = np.array([float(r["C"]) for r in finite_rows])
    chi = np.array([float(r["chi"]) for r in finite_rows])
    C_sem = np.array([float(r.get("C_sem", 0.0) or 0.0) for r in finite_rows])
    chi_sem = np.array([float(r.get("chi_sem", 0.0) or 0.0) for r in finite_rows])

    if _rms(C_sem) <= _FLOOR_EPS and _rms(chi_sem) <= _FLOOR_EPS:
        return Identifiability(0, {}, {}, {}, {},
                               ["no grain (no SEM in rows) -> identifiability not assessable"])

    # railed: point fit sits at a parameter bound -> unconstrained, not pinned. Bounded params
    # ([0,1]) use a linear margin; timescales (wide multiplicative bounds 1e-3..1e3) use a factor.
    railed = {}
    for i, p in enumerate(_PARAM_NAMES):
        lo, hi = float(_LOWER[i]), float(_UPPER[i])
        v = float(point_params[i])
        if p in _TIMESCALE:
            railed[p] = (v <= lo * 3.0) or (v >= hi / 3.0)
        else:
            span = hi - lo
            railed[p] = (v - lo) < 0.01 * span or (hi - v) < 0.01 * span

    rng = np.random.default_rng(seed)
    cols = {p: [] for p in _PARAM_NAMES}
    for _ in range(n_boot):
        Cb = C + rng.normal(0.0, C_sem)
        chib = chi + rng.normal(0.0, chi_sem)
        boot = [{"tau": float(t), "C": float(cc), "chi": float(xx)}
                for t, cc, xx in zip(tau, Cb, chib)]
        f = fit_kww5(boot, chit_prior=chit_prior, T=T)   # n_boot=0 -> no recursion
        for i, p in enumerate(_PARAM_NAMES):
            cols[p].append(getattr(f, p))

    std = {p: float(np.std(cols[p])) for p in _PARAM_NAMES}
    mean = {p: float(np.mean(cols[p])) for p in _PARAM_NAMES}
    spread, identified = {}, {}
    for p in _PARAM_NAMES:
        if p in _TIMESCALE:
            cv = std[p] / abs(mean[p]) if abs(mean[p]) > 1e-9 else float("inf")
            spread[p] = cv
            identified[p] = (cv < TIMESCALE_CV_GATE) and not railed[p]
        else:
            spread[p] = std[p]
            identified[p] = (std[p] < BOUNDED_STD_GATE) and not railed[p]

    return Identifiability(n_boot, std, spread, identified, railed,
                           [f"parametric bootstrap n={n_boot} at the cell grain"])
