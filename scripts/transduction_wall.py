r"""transduction_wall.py -- THE layer-2 wall test: can the splay's TOPOLOGICAL (Z2) gain AMPLITUDE-DRIVE a
continuous register (generation), or only SELECT its handedness (the wall)?

emergent_gain.py showed: the splay has no collective AMPLITUDE gain (a<=0); its gain is TOPOLOGICAL -- the Z2
firing-order sector self-lights. The remaining layer-2 question (Ron, 2026-05-31): can that topological gain
be TRANSDUCED into the amplitude gain of a continuous register?

THE HYPOTHESIS (sharp): topological gain is the ENERGY OF A ONE-TIME SSB COMMITMENT. Once the splay commits
its Z2, the chirality is a STATIC +/-1 sign. A static sign can SELECT (set handedness; persists on removal)
but carries no ongoing flux to DRIVE an amplitude. The base's ongoing rotating firing (its m=1 mode rotates,
sense = the committed chirality) CAN parametrically pump the upper -- but that gain is the BASE's ongoing
drive, so it vanishes when the base is removed. Only an upper with its OWN mu>0 survives. => SELECTION
transduces and PERSISTS; DRIVE/GAIN transduces only WHILE CONNECTED (borrowed, decays). The cascade cannot
MINT continuous gain -- it borrows the substrate's ongoing drive or holds a committed bit. That is the
bootstrap constraint (drive supplied, never minted) at the transduction boundary.

FOUR coupling modes, upper register z (complex), handedness s (Z2), base = the splay (reused):
  SELECT    : dz = (0      + i*Omega*s) z - |z|^2 z         (mu=0; base only biases s)        -> no amplitude
  ADDITIVE  : dz = (0      + i*Omega*s) z - |z|^2 z + k*D    (forced; hybrid_cascade)          -> decays on rm
  PARAMETRIC: dz = (0 + k*p(t) + i*Omega*s) z - |z|^2 z      (p=Re D, zero-mean osc @ ~2*Omega) -> decays on rm
  INSERTED  : dz = (mu>0  + i*Omega*s) z - |z|^2 z           (its OWN gain; base only selects s) -> SURVIVES
D(t) = base m=1 mode (rotates @ omega_d, sense = chirality); p(t)=Re D(t) (zero-mean -> no DC gain inserted,
so any parametric growth is TRUE resonance from the base's ongoing rotation, not a hidden gain term).

VERDICT: if only INSERTED survives base removal (SELECT holds the bit but |z|->0; ADDITIVE & PARAMETRIC decay),
the wall is real: topological/committed gain SELECTS (persists) + ongoing drive BORROWS (decays); neither MINTS
continuous gain. Generation of a self-driven register needs the gain OWNED/inserted = drive supplied, not minted.

Usage (from mpa-conform root):  python scripts/transduction_wall.py
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

WB, KB, ALPHA, DT = 1.0, 1.0, 0.9 * np.pi, 0.01
A_S, B_S = 0.6, 0.5
MU_INSERT = 1.0
K_ADD, K_PAR = 0.30, 1.2
ROOTS3 = np.exp(-1j * 2 * np.pi * np.arange(3) / 3.0)   # m=1 projection weights


def base_field(th):
    d = np.zeros(3)
    for i in range(3):
        d[i] = WB + (KB / 3.0) * np.sum(np.sin(th - th[i] - ALPHA))
    return d


def base_chirality(th):
    return int(np.sign(np.sin(th[1] - th[0]) + np.sin(th[2] - th[1]) + np.sin(th[0] - th[2])))


def base_m1(th):
    return np.sum(np.exp(1j * th) * ROOTS3) / 3.0


def settle_base(seed, T=300.0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, 3)
    for _ in range(int(T / DT)):
        th = th + base_field(th) * DT
    return th


def measure_omega_d(th, T=40.0):
    """rotation rate of the base m=1 mode (the ongoing drive frequency)."""
    phases = []
    for _ in range(int(T / DT)):
        th = th + base_field(th) * DT
        phases.append(np.angle(base_m1(th)))
    ph = np.unwrap(np.array(phases))
    return float((ph[-1] - ph[0]) / (len(ph) * DT))


def run(seed, mode, Omega, T_lock=200.0, T_free=200.0):
    rng = np.random.default_rng(seed + 11)
    th = settle_base(seed)
    chi = base_chirality(th)
    z = 0.05 * (rng.standard_normal() + 1j * rng.standard_normal())
    s = 0.0
    h_base = float(chi)
    mu = MU_INSERT if mode == "inserted" else 0.0
    amps, ss = [], []

    def upper_step(use_base):
        nonlocal z
        D = base_m1(th) if use_base else 0.0
        gain = mu
        force = 0.0
        if mode == "parametric" and use_base:
            force = K_PAR * float(np.real(D)) * np.conj(z)   # degenerate-parametric (squeeze) @ ~2*Omega:
            #   phase-sensitive -> genuinely amplifies one quadrature (Re D oscillates at omega_d ~ 2*Omega).
            #   This is the MOST GENEROUS transduction; gain is borrowed from the base's ongoing rotation.
        if mode == "additive" and use_base:
            force = K_ADD * D
        z = z + ((gain + 1j * Omega * s) * z - (abs(z) ** 2) * z + force) * DT

    for _ in range(int(T_lock / DT)):
        th = th + base_field(th) * DT
        s = s + (A_S * (s - s ** 3) + B_S * h_base) * DT
        upper_step(True)
        amps.append(abs(z)); ss.append(s)
    amp_lock, s_lock = abs(z), s
    n0 = len(amps)
    for _ in range(int(T_free / DT)):
        th = th + base_field(th) * DT          # base keeps running internally, but DECOUPLED from the upper
        s = s + (A_S * (s - s ** 3)) * DT       # no base bias
        upper_step(False)                       # base removed from the upper's equation
        amps.append(abs(z)); ss.append(s)
    return dict(chi=chi, mode=mode, amp_lock=float(amp_lock), s_lock=float(s_lock),
                amp_free=float(abs(z)), s_free=float(s), amps=np.array(amps), ss=np.array(ss), n0=n0)


def main():
    th0 = settle_base(0)
    omega_d = measure_omega_d(th0.copy())
    Omega = abs(omega_d) / 2.0 if abs(omega_d) > 1e-3 else 0.75   # parametric principal tongue: drive ~ 2*Omega
    print("Layer-2 WALL test -- can the splay's TOPOLOGICAL (Z2) gain AMPLITUDE-DRIVE a continuous register?\n")
    print(f"base m=1 drive rotates at omega_d={omega_d:+.3f}; set upper Omega={Omega:.3f} (parametric @ ~2*Omega).")
    print(f"upper mu=0 for SELECT/ADDITIVE/PARAMETRIC (no own gain); mu={MU_INSERT} only for INSERTED control.\n")

    modes = ["select", "additive", "parametric", "inserted"]
    summary = {}
    reps = {}
    for mode in modes:
        amp_l, amp_f, held, persist = [], [], [], []
        for s in range(8):
            r = run(s, mode, Omega)
            amp_l.append(r["amp_lock"]); amp_f.append(r["amp_free"])
            held.append((np.sign(r["s_free"]) == np.sign(r["s_lock"])) and abs(r["s_free"]) > 0.8)
            persist.append(r["amp_free"] > 0.3 * max(r["amp_lock"], 1e-9) and r["amp_free"] > 0.2)
            if s == 0:
                reps[mode] = r
        summary[mode] = dict(amp_lock=np.mean(amp_l), amp_free=np.mean(amp_f),
                             held=np.mean(held), persist=np.mean(persist))

    print("=" * 92)
    print(f"{'mode':<12}{'|z| locked':>12}{'|z| free':>12}{'amp persists':>15}{'bit s held':>13}")
    print("=" * 92)
    for mode in modes:
        d = summary[mode]
        print(f"{mode:<12}{d['amp_lock']:>12.3f}{d['amp_free']:>12.3f}"
              f"{100*d['persist']:>13.0f}%{100*d['held']:>12.0f}%")

    figure(reps, Omega)

    only_inserted = bool(summary["inserted"]["persist"] > 0.9
                         and summary["select"]["persist"] < 0.1
                         and summary["additive"]["persist"] < 0.1
                         and summary["parametric"]["persist"] < 0.1)
    select_holds_bit = bool(summary["select"]["held"] > 0.9)
    print("\n" + "=" * 92)
    print("VERDICT -- does topological gain DRIVE a continuous register, or only SELECT?")
    print("=" * 92)
    if only_inserted and select_holds_bit:
        print("  ==> THE WALL IS REAL. Across every transduction mode the upper amplitude COLLAPSES when the")
        print("      base is removed -- SELECT (committed bit held, but |z|->0: a static sign carries no flux),")
        print("      ADDITIVE (forced response decays), PARAMETRIC (borrowed resonance gain decays). Only the")
        print("      INSERTED mu>0 upper -- its OWN gain -- survives. So topological/committed gain can SELECT a")
        print("      persistent bit and the base's ongoing rotation can BORROW-DRIVE amplitude WHILE CONNECTED,")
        print("      but NEITHER MINTS continuous gain: removing the base removes the drive. Generation of a")
        print("      self-driven continuous register requires the gain to be OWNED (inserted) -- which is the")
        print("      bootstrap constraint at the transduction boundary: the cascade metabolizes drive, never")
        print("      mints it. The layer-2 'generative' bet is CONDITIONAL: select/borrow yes, create-gain no.")
    else:
        print(f"  ==> Read honestly: only_inserted_survives={only_inserted}, select_holds_bit={select_holds_bit}.")
        for mode in modes:
            d = summary[mode]
            print(f"      {mode:<11} persist={100*d['persist']:.0f}% held={100*d['held']:.0f}% "
                  f"|z|_lock={d['amp_lock']:.3f} |z|_free={d['amp_free']:.3f}")
    print("\n  SCOPE: minimal model (splay base + marginal/own-gain upper + Z2 bit). The PARAMETRIC mode is the")
    print("  most generous transduction (zero-mean modulation -> any growth is true resonance, not inserted")
    print("  DC gain); its decay on removal is the load-bearing negative. A real emergent instance + the")
    print("  option-b reconciling base remain; this pins the *transduction* boundary, not every conceivable one.")


def figure(reps, Omega):
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), dpi=150)
    colors = {"select": "#9e9e9e", "additive": "#1565c0", "parametric": "#ef6c00", "inserted": "#2e7d32"}
    n0 = reps["inserted"]["n0"]
    for mode, r in reps.items():
        t = np.arange(len(r["amps"])) * DT
        ax[0].plot(t, r["amps"], color=colors[mode], lw=1.5, label=f"{mode}")
    ax[0].axvline(n0 * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[0].axhline(np.sqrt(MU_INSERT), color="#2e7d32", ls=":", lw=0.8, label=r"$\sqrt{\mu}$ (own-gain radius)")
    ax[0].set_xlabel("time"); ax[0].set_ylabel("upper amplitude |z|")
    ax[0].set_title("only the INSERTED (own-gain) upper survives removal;\nselect/additive/parametric all collapse")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    for mode in ("select", "inserted"):
        r = reps[mode]
        t = np.arange(len(r["ss"])) * DT
        ax[1].plot(t, r["ss"], color=colors[mode], lw=1.6, label=f"bit s ({mode})")
    ax[1].axvline(n0 * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[1].axhline(0, color="gray", lw=0.6)
    ax[1].set_xlabel("time"); ax[1].set_ylabel("selected bit s")
    ax[1].set_title("the committed BIT persists (selection transduces + holds)\n-- but a static bit carries no drive")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    fig.suptitle("Layer-2 transduction WALL -- topological gain SELECTS a persistent bit + ongoing drive "
                 "BORROWS amplitude, but neither MINTS continuous gain", fontsize=10.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = OUT / "transduction_wall.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
