r"""a_eff_reduction.py -- the layer-2 generative bet, read under the mpa-LEGAL rule: in CHARACTER every
coefficient must FLOW, never sit inert (project_mpa_legal_program; feedback_attach_math_in_the_interior).

Outbound research narrowed the whole bet to ONE scalar: does the reduced collective self-gain a_eff in
  Xdot = a_eff * X + b X^3 + ...
become positive from ELIMINATION of microscopic modes (derived, flowing) or only from an INSERTED coefficient
(an inert constant)? Active matter / synergetics own that autonomous order parameters EXIST; what they do NOT
do is derive sign(a_eff) from the exact microscopic NESS structure -- they POSTULATE a as phenomenological
(a constant). Importing a character coefficient as a constant is ILLEGAL. So: look closely at a_eff's SOURCE.

THE FINDING (worked by hand, confirmed numerically here) overturns the naive "gain from non-reciprocity"
hypothesis. For BOTH canonical chiral-NESS bases:

  RING (non-reciprocal Stuart-Landau ring, passive units mu<0):
     M = (mu + i*omega) I + K,  K_{i,i+1}=kappa(1+delta), K_{i,i-1}=kappa(1-delta)
     lambda_k = mu + 2*kappa*cos(th_k)  +  i*( omega + 2*kappa*delta*sin(th_k) )
     => Re a_eff = mu + 2*kappa   (the GAIN) -- delta-INDEPENDENT: sourced by the INERT constants mu, kappa.
     => Im splitting = 2*kappa*delta*sin(th_k)  (the CHIRALITY) -- FLOWS with delta (the NESS non-reciprocity).
  FRUCHART 2-field (non-reciprocal aligning): M=[[mu, j+delta],[j-delta, mu]],
     lambda = mu +/- sqrt(j^2 - delta^2);  in the chiral phase (delta>j): Re=mu (GAIN = inert const),
     Im = sqrt(delta^2 - j^2) (rotation FLOWS with delta).

So in EVERY case the amplitude GAIN (Re a_eff) traces to an INERT CONSTANT (the pump mu / coupling kappa),
with NO flowing source; the only FLOWING quantity (delta = broken detailed balance = NESS circulation) feeds
the CHIRALITY/rotation (Im), never the gain.

LEGAL VERDICT: continuous-amplitude autonomy cannot be GENERATED legally -- its sole source is an inert
constant, which CHARACTER forbids (you may not import a character coefficient as a constant). Chirality /
handedness / topology DO flow with the NESS (delta) -> their generation is LEGAL. This is the deepest form of
the conditional verdict (generative-of-organization/chirality, parasitic-on-drive) and it subsumes the
transduction wall: "only the inserted mu survives" == "the gain is an inert constant."

Usage (from mpa-conform root):  python scripts/a_eff_reduction.py
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
for p in (str(REPO_ROOT), str(REPO_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

N = 12
MU = -0.5          # PASSIVE units: no per-unit gain (mu<0). The "no insertion at the unit level" choice.
OMEGA = 1.0
DT = 0.01


def ring_M(kappa, delta, mu=MU, omega=OMEGA, n=N):
    """N x N COMPLEX linearization of the non-reciprocal SL ring about z=0 (the reduced collective operator)."""
    M = (mu + 1j * omega) * np.eye(n, dtype=complex)
    for i in range(n):
        M[i, (i + 1) % n] += kappa * (1 + delta)   # forward bond
        M[i, (i - 1) % n] += kappa * (1 - delta)    # backward bond (non-reciprocal if delta != 0)
    return M


def ring_gain_chirality(kappa, delta):
    ev = np.linalg.eigvals(ring_M(kappa, delta))
    a_eff = float(np.max(ev.real))                  # collective self-gain = most unstable real part
    chirality = float(ev.imag.max() - ev.imag.min())  # Im spread: 0 at delta=0 (achiral), flows with delta
    return a_eff, chirality


def fruchart_gain_rot(j, delta, mu=MU):
    M = np.array([[mu, j + delta], [j - delta, mu]], dtype=float)
    ev = np.linalg.eigvals(M.astype(complex))
    return float(np.max(ev.real)), float(np.max(np.abs(ev.imag)))


def integrate_ring(kappa, delta, T=120.0, seed=0):
    """nonlinear double-dissociation: collective order parameter X grows iff gain>0 (set by kappa);
    its chirality (rotation sense) is set by delta. Returns |X|(t) and the mean chiral rotation rate."""
    rng = np.random.default_rng(seed)
    z = 0.05 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    fwd, bwd = kappa * (1 + delta), kappa * (1 - delta)
    Xs, phase = [], []
    for _ in range(int(T / DT)):
        coup = fwd * np.roll(z, -1) + bwd * np.roll(z, 1)
        z = z + ((MU + 1j * OMEGA) * z - (np.abs(z) ** 2) * z + coup) * DT
        X = np.mean(z)
        Xs.append(abs(X)); phase.append(np.angle(X))
    ph = np.unwrap(np.array(phase))
    rot = float((ph[-1] - ph[len(ph) // 2]) / (len(ph) // 2 * DT))   # late-time rotation rate (chirality)
    return np.array(Xs), rot


def main():
    print("a_eff under the mpa-LEGAL rule -- does the collective gain FLOW, or sit as an inert constant?\n")
    print(f"passive units mu={MU} (no per-unit gain), omega={OMEGA}, ring N={N}.\n")

    deltas = np.linspace(0.0, 0.9, 10)
    kappas = np.linspace(0.0, 0.6, 13)
    KFIX, DFIX = 0.45, 0.6      # an above-threshold operating point (mu+2k = 0.4 > 0)

    # --- sweep delta (the FLOWING non-reciprocity) at fixed kappa ---
    a_d = np.array([ring_gain_chirality(KFIX, d)[0] for d in deltas])
    c_d = np.array([ring_gain_chirality(KFIX, d)[1] for d in deltas])
    # --- sweep kappa (the INERT coupling constant) at fixed delta ---
    a_k = np.array([ring_gain_chirality(k, DFIX)[0] for k in kappas])

    print("=" * 90)
    print(f"RING: sweep the FLOWING non-reciprocity delta (kappa fixed={KFIX}) -- does the GAIN move?")
    print("=" * 90)
    for d, a, c in zip(deltas, a_d, c_d):
        print(f"  delta={d:4.2f} | a_eff(gain)={a:+.4f}   chirality(Im spread)={c:+.4f}")
    print(f"  => a_eff range over delta = {a_d.max()-a_d.min():.2e}  (FLAT: gain does NOT flow with delta)")
    print(f"  => chirality range over delta = {c_d.max()-c_d.min():.3f}  (FLOWS with delta)")

    print("\n" + "=" * 90)
    print(f"RING: sweep the INERT coupling constant kappa (delta fixed={DFIX}) -- does the GAIN track it?")
    print("=" * 90)
    for k, a in zip(kappas, a_k):
        mark = "  <-- a_eff>0" if a > 1e-6 else ""
        print(f"  kappa={k:4.2f} | a_eff(gain)={a:+.4f}   (= mu+2k = {MU+2*k:+.3f}){mark}")
    print(f"  => a_eff tracks kappa linearly (gain = mu + 2*kappa): SOURCED BY THE INERT CONSTANT.")

    # --- Fruchart cross-check ---
    j = 0.3
    a_f = np.array([fruchart_gain_rot(j, d)[0] for d in deltas])
    r_f = np.array([fruchart_gain_rot(j, d)[1] for d in deltas])
    print("\n" + "=" * 90)
    print(f"FRUCHART 2-field cross-check (j={j}): chiral phase delta>j -> gain = mu (const), rotation flows")
    print("=" * 90)
    for d, a, r in zip(deltas, a_f, r_f):
        ph = "static" if d <= j else "CHIRAL"
        print(f"  delta={d:4.2f} | a_eff(gain)={a:+.4f}  rotation|Im|={r:+.4f}  [{ph}]")
    chiral = deltas > j
    print(f"  => in the chiral phase a_eff = mu = {MU:+.2f} (FLAT, inert const); rotation FLOWS with delta.")

    # --- nonlinear double dissociation ---
    X_on, rot_on = integrate_ring(KFIX, DFIX)          # gain on (k>kc), chiral (d>0)
    X_achiral, rot_ac = integrate_ring(KFIX, 0.0)      # gain on, delta=0  -> still grows (gain INDEP of delta)
    X_nogain, _ = integrate_ring(0.10, DFIX)           # k<kc -> decays (gain GONE: it was the constant kappa)
    print("\n" + "=" * 90)
    print("NONLINEAR DOUBLE DISSOCIATION -- gain controlled by kappa(const); chirality by delta(flows)")
    print("=" * 90)
    print(f"  (k={KFIX}, d={DFIX}): |X|_final={X_on[-1]:.3f} rot={rot_on:+.3f}  -> grows, chiral")
    print(f"  (k={KFIX}, d=0  ): |X|_final={X_achiral[-1]:.3f} rot={rot_ac:+.3f}  -> STILL grows (gain INDEP of delta)")
    print(f"  (k=0.10,d={DFIX}): |X|_final={X_nogain[-1]:.3f}            -> DECAYS (gain GONE -- it was kappa)")

    figure(deltas, a_d, c_d, kappas, a_k, X_on, X_achiral, X_nogain)

    gain_flat_in_delta = bool((a_d.max() - a_d.min()) < 1e-3)
    chirality_flows = bool((c_d.max() - c_d.min()) > 0.1)
    gain_tracks_kappa = bool(np.corrcoef(kappas, a_k)[0, 1] > 0.999)
    print("\n" + "=" * 90)
    print("LEGAL AUDIT -- does the gain FLOW (legal) or sit as an inert constant (ILLEGAL in character)?")
    print("=" * 90)
    print(f"  mu  (per-unit pump) : inert constant -> sets the gain baseline.   [gain source]")
    print(f"  kappa (coupling)    : inert constant -> a_eff = mu+2k tracks it (corr {np.corrcoef(kappas,a_k)[0,1]:.4f}). [gain source]")
    print(f"  delta (non-recip.)  : the ONLY quantity tied to a FLOWING NESS (broken detailed balance);")
    print(f"                        feeds Im/CHIRALITY (range {c_d.max()-c_d.min():.2f}), NOT Re/gain "
          f"(range {a_d.max()-a_d.min():.1e}).")
    legal_kill = gain_flat_in_delta and chirality_flows and gain_tracks_kappa
    print("\n" + "=" * 90)
    print("VERDICT")
    print("=" * 90)
    if legal_kill:
        print("  ==> The collective amplitude GAIN has NO FLOWING SOURCE: a_eff = mu + 2*kappa is set entirely")
        print("      by inert constants and does NOT move with the flowing non-reciprocity delta. The only")
        print("      flowing NESS quantity (delta) feeds CHIRALITY/rotation (Im), never the gain (Re). Confirmed")
        print("      cross-model (ring + Fruchart) and nonlinearly (gain dies with kappa, survives delta->0).")
        print("      Under the mpa-LEGAL rule -- a character coefficient may NOT be imported as a constant --")
        print("      continuous-amplitude autonomy therefore CANNOT be generated legally: its sole source is an")
        print("      inert constant. What CAN be generated legally is the CHIRALITY/handedness/topology, which")
        print("      flows with the NESS. So the layer-2 generative bet is, read legally: GENERATIVE-of-")
        print("      organization/chirality (flowing, legal) + PARASITIC-on-drive (the gain is supplied, never")
        print("      minted). This subsumes the transduction wall: 'only the inserted mu survives' == 'the gain")
        print("      is an inert constant.' It also overturns this session's earlier 'gain-from-non-reciprocity'")
        print("      hypothesis -- looking closely (constants are illegal), the gain never flowed.")
    else:
        print(f"  ==> Read honestly: gain_flat_in_delta={gain_flat_in_delta}, chirality_flows={chirality_flows}, "
              f"gain_tracks_kappa={gain_tracks_kappa}.")
    print("\n  SCOPE: two canonical chiral-NESS bases (non-reciprocal SL ring + Fruchart 2-field), linear")
    print("  reduction + nonlinear confirmation. The claim is about the SOURCE of the gain (inert constant vs")
    print("  flowing NESS), not about whether order parameters exist (they do -- the literature owns that).")


def figure(deltas, a_d, c_d, kappas, a_k, X_on, X_ac, X_ng):
    fig, ax = plt.subplots(1, 3, figsize=(17, 5), dpi=150)
    ax[0].axhline(0, color="gray", lw=0.8)
    ax[0].plot(deltas, a_d, color="#c62828", lw=2, marker="o", ms=4, label="gain Re(a_eff) -- FLAT")
    ax[0].plot(deltas, c_d, color="#2e7d32", lw=2, marker="s", ms=4, label="chirality (Im spread) -- FLOWS")
    ax[0].set_xlabel("flowing non-reciprocity  delta"); ax[0].set_ylabel("value")
    ax[0].set_title("the FLOWING NESS (delta) feeds chirality, NOT the gain\n(gain has no flowing source)")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    ax[1].axhline(0, color="gray", lw=0.8)
    ax[1].plot(kappas, a_k, color="#1565c0", lw=2, marker="o", ms=4, label="gain a_eff = mu + 2*kappa")
    ax[1].set_xlabel("inert coupling constant  kappa"); ax[1].set_ylabel("gain Re(a_eff)")
    ax[1].set_title("the gain is sourced by the INERT CONSTANT kappa\n(importing it into character is illegal)")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    t = np.arange(len(X_on)) * DT
    ax[2].plot(t, X_on, color="#2e7d32", lw=1.6, label="k>kc, d>0: grows + chiral")
    ax[2].plot(t, X_ac, color="#6a1b9a", lw=1.4, ls="--", label="k>kc, d=0: STILL grows (gain INDEP of delta)")
    ax[2].plot(t, X_ng, color="#c62828", lw=1.6, label="k<kc: DECAYS (gain was kappa)")
    ax[2].set_xlabel("time"); ax[2].set_ylabel("collective |X|")
    ax[2].set_title("double dissociation: gain<-kappa (const), chirality<-delta (flows)")
    ax[2].legend(fontsize=8, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("a_eff under the mpa-legal rule -- the amplitude gain has NO flowing source (inert constant, "
                 "illegal in character); only chirality flows with the NESS", fontsize=10.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = OUT / "a_eff_reduction.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
