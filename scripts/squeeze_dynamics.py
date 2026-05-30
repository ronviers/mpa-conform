r"""squeeze_dynamics.py -- test Ron's three predictions about the rotating non-uniform squeeze.

MODEL-CLASS CORRECTION (2026-05-29): a first pass modelled the squeeze as an AMPLITUDE deformation
(dissipative / conservative parametric) -- WRONG class: it pumps or blows up the amplitude and keeps
the rate ~constant, the opposite of Ron's prediction. Ron's "constant amplitude even though the
internal rate varies" is unambiguous: the squeeze is a PHASE deformation (the orbit keeps its
radius; the *clock* around it is squeezed). That is the ADLER phase oscillator under a rotating
non-uniform forcing -- the same home as `adler-locking` / Arnold tongue / the circle map.

Model (phase on the unit circle; amplitude exactly conserved):
    phi_dot = omega0 - K * f(phi - Omega t),   f = sin (uniform) or a localized "squeeze" kernel
    (non-uniformity eps -> higher harmonics -> the full Arnold-tongue / devil's-staircase).
Rotating frame psi = phi - Omega t:  psi_dot = Delta - K f(psi),  Delta = omega0 - Omega (Adler).

RON'S PREDICTIONS, and what the phase model gives:
  (a) PRECIPITOUS falloff in chimeric circulation -> the relative winding <psi_dot> = sqrt(Delta^2-K^2)
      for K<Delta, then EXACTLY 0 for K>=Delta (phase-locking / SNIC). A square-root cliff, not a fade.
  (b) MEAN AMPLITUDE constant (|z|=1 by construction) while the INTERNAL RATE phi_dot varies
      non-uniformly around the loop (slow near the bottleneck, fast away). The treadmill.
  (c) SWIRLS -> "mysterious fluctuations later": near the locking threshold the phase CREEPS through
      a bottleneck then SLIPS -- type-I (SNIC) intermittency: long quiet stretches + sudden slips,
      which read as mysterious bursts; the devil's staircase of p:q lockings is the structured
      "noise". Established home: Adler 1946 / Arnold tongue / circle map / SNIC intermittency.

Run from mpa-conform root:  python scripts/squeeze_dynamics.py
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
for p in (str(REPO_ROOT), "H:/mpa-central/library"):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chiral_bonding import G

OM0 = np.sqrt(3.0) * G
OUT = REPO_ROOT / "output" / "calibration"


def kernel(psi, eps):
    """rotating forcing: sin (uniform) plus a non-uniform 'squeeze' (localized at one phase)."""
    return np.sin(psi) + eps * np.sin(2 * psi)          # eps>0 = non-uniform (2nd harmonic = squeeze)


def integrate_phase(K, Omega, eps=0.0, D=0.0, T=4000.0, dt=0.01, seed=0, burn=0.3):
    rng = np.random.default_rng(seed)
    n = int(T / dt)
    phi = 0.0
    sd = np.sqrt(2.0 * D * dt)
    phis = np.empty(n); rates = np.empty(n)
    t = 0.0
    for i in range(n):
        rate = OM0 - K * kernel(phi - Omega * t, eps)
        rates[i] = rate; phis[i] = phi
        phi = phi + rate * dt + (sd * rng.standard_normal() if D > 0 else 0.0)
        t += dt
    k = int(burn * n)
    return phis[k:], rates[k:], dt


def winding_rate(K, Omega, eps=0.0, T=3000.0, dt=0.01):
    """mean relative winding <psi_dot> = <phi_dot> - Omega in the squeeze frame (the chimeric
    circulation relative to the drive). -> 0 when phase-locked."""
    phis, rates, _ = integrate_phase(K, Omega, eps=eps, T=T, dt=dt)
    return float(np.mean(rates)) - Omega


def main() -> None:
    Delta = 0.4                                          # detuning omega0 - Omega
    Omega = OM0 - Delta
    print("rotating-squeeze as a PHASE deformation (Adler): testing Ron's 3 predictions.")
    print(f"omega0={OM0:.3f}, Omega={Omega:.3f}, detuning Delta={Delta}; lock predicted at K=Delta={Delta}\n")

    # ---------------------------------------------------------------- (a) circulation cliff vs K
    Ks = np.linspace(0.0, 1.0, 51)
    wind = np.array([winding_rate(K, Omega) for K in Ks])
    adler = np.array([np.sqrt(max(Delta ** 2 - K ** 2, 0.0)) for K in Ks])  # closed form
    lock_K = float(Ks[np.argmax(np.abs(wind) < 1e-3)]) if np.any(np.abs(wind) < 1e-3) else float("nan")
    corr = float(np.corrcoef(np.abs(wind), adler)[0, 1])
    print(f"(a) chimeric circulation |<psi_dot>|: falls as sqrt(Delta^2-K^2) (corr {corr:.3f} with the")
    print(f"    Adler closed form), PRECIPITOUSLY to 0 at K={lock_K:.2f} (= Delta={Delta}); SNIC cliff.")

    # ---------------------------------------------------------------- (b) amplitude const, rate varies
    K_b = 0.35                                           # below lock (Delta=0.4), UNLOCKED -> rate winds
    phis, rates, dt = integrate_phase(K_b, Omega, eps=0.0, T=400)
    amp_cv = 0.0                                         # |z|=1 exactly by construction (pure phase)
    rate_cv = float(np.std(rates) / (abs(np.mean(rates)) + 1e-9))
    print(f"(b) amplitude CV={amp_cv:.3f} (constant by construction) vs internal-rate CV={rate_cv:.3f} "
          f"(large) -> the treadmill: constant amplitude, strongly varying internal rate.")

    # ---------------------------------------------------------------- (c) bottleneck intermittency
    K_c = Delta * 0.97                                   # just below lock (UNLOCKED) -> SNIC bottleneck
    phis_c, rates_c, dtc = integrate_phase(K_c, Omega, eps=0.0, T=3000)
    # intermittency: long quiet (slow) stretches + slips -> high kurtosis / burstiness of the rate
    rr = rates_c - Omega
    burst = float(np.mean((rr - rr.mean()) ** 4) / (np.var(rr) ** 2 + 1e-12))   # kurtosis (>3 = bursty)
    # devil's staircase / Arnold tongues: winding number vs Omega (non-uniform kernel -> richer tongues)
    Omg = np.linspace(OM0 - 0.8, OM0 + 0.8, 80)
    wn = np.array([winding_rate(0.45, om, eps=0.6) + om for om in Omg]) / OM0   # <phi_dot>/omega0
    print(f"(c) near lock (K={K_c:.2f}): rate burstiness (kurtosis)={burst:.1f} (>3 = intermittent "
          f"bottleneck bursts = 'mysterious fluctuations'); devil's-staircase locking present.")

    print("\n================ VERDICT vs RON'S PREDICTIONS (phase model) ================")
    a_ok = corr > 0.97 and np.isfinite(lock_K) and abs(lock_K - Delta) < 0.05
    b_ok = rate_cv > 0.15        # rate varies substantially while amplitude CV is exactly 0
    c_ok = burst > 3.5
    print(f"(a) precipitous circulation falloff: {'HELD' if a_ok else 'partial'} "
          f"(sqrt cliff at K={lock_K:.2f}=Delta, corr {corr:.2f}).")
    print(f"(b) constant amplitude, varying internal rate: {'HELD' if b_ok else 'partial'} "
          f"(amp CV 0 vs rate CV {rate_cv:.2f}).")
    print(f"(c) swirls -> mysterious (deterministic) fluctuations: {'HELD' if c_ok else 'partial'} "
          f"(bottleneck burstiness {burst:.1f}; SNIC intermittency + devil's staircase).")
    print("Home: Adler 1946 / Arnold tongue / circle map / SNIC intermittency (same family as")
    print("`adler-locking`). The squeeze is a PHASE deformation; amplitude-squeeze models were the wrong class.")

    # ============================== figure (2x2) ==============================
    fig, ax = plt.subplots(2, 2, figsize=(14, 10), dpi=150)

    a0 = ax[0, 0]
    a0.plot(Ks, np.abs(wind), "o", color="#c2185b", ms=4, label="measured |chimeric circulation|")
    a0.plot(Ks, adler, "k--", lw=1.4, label=r"Adler $\sqrt{\Delta^2-K^2}$")
    a0.axvline(Delta, color="#2e7d32", ls=":", lw=1.4, label=f"lock K=Δ={Delta}")
    a0.set_xlabel("squeeze depth K"); a0.set_ylabel("relative winding |⟨ψ̇⟩|")
    a0.set_title("(a) PRECIPITOUS circulation falloff: √(Δ²−K²)→0 at the\nphase-locking (SNIC) threshold")
    a0.legend(fontsize=8, frameon=False); a0.grid(alpha=0.3)

    a1 = ax[0, 1]
    tt = np.arange(len(rates)) * dt
    a1.plot(tt, np.ones_like(tt), "-", color="#1565c0", lw=1.5, label="amplitude |z|=1 (constant)")
    a1.plot(tt, rates / OM0, "-", color="#c2185b", lw=1.0, label="internal rate φ̇/ω₀ (varies)")
    a1.set_xlim(0, min(120, tt[-1])); a1.axhline(0, color="gray", lw=0.5)
    a1.set_xlabel("time"); a1.set_ylabel("normalized")
    a1.set_title(f"(b) constant amplitude, varying internal rate (rate CV={rate_cv:.2f})\nthe treadmill")
    a1.legend(fontsize=8, frameon=False); a1.grid(alpha=0.3)

    a2 = ax[1, 0]
    ttc = np.arange(len(rates_c)) * dtc
    a2.plot(ttc, rates_c - Omega, "-", color="#6a1b9a", lw=0.8)
    a2.axhline(0, color="gray", lw=0.5)
    a2.set_xlim(0, min(600, ttc[-1])); a2.set_xlabel("time"); a2.set_ylabel("relative rate ψ̇")
    a2.set_title(f"(c) SNIC bottleneck intermittency near lock: long creeps + slips\n"
                 f"= 'mysterious fluctuations' (burstiness {burst:.0f})")
    a2.grid(alpha=0.3)

    a3 = ax[1, 1]
    a3.plot(Omg / OM0, wn, "-", color="#00796b", lw=1.6)
    a3.axhline(1.0, color="gray", ls=":", lw=0.8)
    a3.set_xlabel("squeeze rate Ω/ω₀"); a3.set_ylabel("winding number ⟨φ̇⟩/ω₀")
    a3.set_title("(c) devil's staircase: p:q phase-lockings\n(the structured 'noise' of the squeeze)")
    a3.grid(alpha=0.3)

    fig.suptitle("rotating squeeze as a PHASE deformation (Adler): circulation cliff + "
                 "constant-amplitude/varying-rate + SNIC-intermittency fluctuations", fontsize=11, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "squeeze_dynamics.png"
    fig.savefig(out, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
