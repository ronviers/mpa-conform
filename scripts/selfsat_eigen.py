"""selfsat_eigen.py -- the complex-eigenvalue (bias-free amplitude) read.

The two faces are Re/Im of the relaxation eigenvalue: Re(lambda) -> damping
gamma_RO (amplitude face, chit-driven), Im(lambda) -> oscillation omega_RO.
Q = omega_RO / (2 gamma_RO) is the chit-conjugate -- the engine predicts it
peaks at chit = ln2 (chit_ch = 1, the Q-peak), underdamped only in a mid-chit
band, Q->0 at both chit->0 and chit->inf.

This reads (gamma_RO, omega_RO, Q) from linearize() at the held fixed point of
the self-saturating kernel (fork b), across chit_ch. It is a fit to the
RELAXATION dynamics, not the chi-vs-C slope -- so it carries none of the
single-slope-X bias. Test: does Q peak at chit_ch = 1?

Run from repo root:  python scripts/selfsat_eigen.py
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
SCRIPTS = Path(__file__).resolve().parent
for p in (str(REPO_ROOT), str(SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from selfsat_check import integrate, linearize  # noqa: E402

LN2 = float(np.log(2.0))
GAMMA = -0.2          # the held coexistence sweet spot (mild cooperative)
IC = (0.3, 0.7)


def ro_at(chit_ch: float):
    G0 = 2.0 ** chit_ch
    with np.errstate(all="ignore"):
        _, A, B = integrate(IC, G0, GAMMA, t_max=200.0)
    fa, fb = A[-1], B[-1]
    if not (np.isfinite(fa) and np.isfinite(fb) and abs(fa) < 1e3 and abs(fb) < 1e3):
        return np.nan, np.nan, np.nan, False, "runaway"   # no held NESS here
    eigs = linearize((fa, fb), G0, GAMMA)
    re, im = eigs.real, eigs.imag
    idx = int(np.argmax(re))                 # dominant (least-damped) mode
    gamma_RO = -float(re[idx])
    omega_RO = float(abs(im[idx]))
    Q = omega_RO / (2.0 * gamma_RO) if gamma_RO > 1e-9 else 0.0
    complex_pair = bool(abs(im[idx]) > 1e-9)
    return gamma_RO, omega_RO, Q, complex_pair, (fa, fb)


def main() -> None:
    chit_chs = np.linspace(0.25, 3.0, 23)
    gRO, wRO, Qs, cplx = [], [], [], []
    for cb in chit_chs:
        g, w, q, c, fp = ro_at(float(cb))
        gRO.append(g); wRO.append(w); Qs.append(q); cplx.append(c)
    gRO, wRO, Qs = np.array(gRO), np.array(wRO), np.array(Qs)

    q_at_peak = Qs[int(np.argmin(np.abs(chit_chs - 1.0)))]
    finite_q = np.isfinite(Qs)
    q_argmax_ch = float(chit_chs[int(np.nanargmax(np.where(finite_q, Qs, -np.inf)))]) if finite_q.any() else float("nan")
    any_ringing = bool(np.any(np.array(cplx)))
    hold_hi = float(np.nanmax(np.where(finite_q, chit_chs, np.nan))) if finite_q.any() else float("nan")
    qmax = float(np.nanmax(Qs)) if finite_q.any() else 0.0

    fig, (axq, axr) = plt.subplots(1, 2, figsize=(13, 5), dpi=170)

    axq.plot(chit_chs, Qs, "o-", color="#2b6cb0", lw=1.8, ms=4)
    axq.axvline(1.0, ls="--", color="#c53030", lw=1.2)
    if np.isfinite(hold_hi):
        axq.axvspan(hold_hi, chit_chs[-1], color="#ececec", alpha=0.7)
        axq.text(hold_hi, qmax * 0.5 if qmax > 0 else 0.5, " runaway (no held NESS) ->",
                 color="#666", fontsize=8, va="center")
    axq.text(1.0, max(qmax, 0.1) * 0.95, " chit_ch=1 (predicted Q-peak)",
             color="#c53030", fontsize=9, va="top")
    axq.set_xlabel("chit_ch"); axq.set_ylabel("Q = omega_RO / 2 gamma_RO")
    axq.set_title(f"Q(chit_ch)  -- peak at {q_argmax_ch:.2f}"
                  + ("" if abs(q_argmax_ch - 1.0) < 0.2 else "  (NOT at 1)"))

    axr.plot(chit_chs, gRO, "o-", color="#dd8b1a", lw=1.6, ms=3, label="gamma_RO (damping)")
    axr.plot(chit_chs, wRO, "s-", color="#2f855a", lw=1.6, ms=3, label="omega_RO (oscillation)")
    axr.axvline(1.0, ls="--", color="#c53030", lw=1)
    axr.set_xlabel("chit_ch"); axr.set_ylabel("rate")
    axr.set_title("eigenvalue parts: Re=-gamma_RO, Im=omega_RO")
    axr.legend(fontsize=9, frameon=False)

    fig.suptitle(f"complex-eigenvalue (bias-free amplitude) read -- self-sat held NESS, gamma={GAMMA}",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = REPO_ROOT / "output" / "selfsat" / "selfsat_eigen_Q.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    print(f"self-sat held NESS, gamma={GAMMA}, IC={IC}")
    print(f"{'chit_ch':>7} {'gamma_RO':>9} {'omega_RO':>9} {'Q':>7} {'ringing?':>9}")
    for cb, g, w, q, c in zip(chit_chs, gRO, wRO, Qs, cplx):
        mark = "  <- Q-peak?" if abs(cb - 1.0) < 0.07 else ""
        print(f"{cb:7.2f} {g:9.4f} {w:9.4f} {q:7.4f} {str(c):>9}{mark}")
    print(f"\nany complex (ringing) eigenvalues across the sweep? {any_ringing}")
    print(f"Q at chit_ch=1: {q_at_peak:.4f};  Q argmax at chit_ch={q_argmax_ch:.2f}")
    print(f"figure: {out}")


if __name__ == "__main__":
    main()
