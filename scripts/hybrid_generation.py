r"""hybrid_generation.py -- TRANSDUCTION vs GENERATION (the outside-model's decisive distinction).

hybrid_cascade.py showed a splay base drives a chiral circulation in the upper -- but the upper there was
a PURE DAMPED FOCUS (dz = -gamma z + kappa*drive): its circulation belonged entirely to the FORCING.
Remove the drive and it decays. That is the WEAK interpretation (passive transduction) -- nothing new is
generated. (And note: ALL our chiral substrates -- RPS, homochiral, Banach -- are noise-driven NESS
circulations around stable FOCI; strip the drive and they decay. They are all "weak" by this criterion.
Only the splay and Stuart-Landau limit cycles are autonomous.)

THE STRONG interpretation (closer to frustration-ascent's generative idea): the upper is an AUTONOMOUS
oscillator -- it possesses its OWN limit cycle (complex pair) -- and the base only BIASES/SELECTS its
handedness. Then the upper is a new autonomous dynamical register; the cascade GENERATES a level, it does
not merely mirror the base.

THE DECISIVE TEST (the outside model's): give the upper its own limit cycle, let the base select its
handedness, then REMOVE the drive. Does the oscillation belong to the upper (persists, handedness held)
or to the forcing (decays)?

  UPPER (autonomous): complex z,  dz/dt = (mu + i*Omega*s) z - |z|^2 z   (mu>0 -> own limit cycle, radius
    sqrt(mu); s in {-1,+1} = the rotation SENSE / handedness).
  HANDEDNESS s (bistable, Z2): ds/dt = a(s - s^3) + b*h_base   (the base biases s toward its chirality).
  PHASE 1 (lock): base on (b>0) -> s commits to the base's handedness, upper limit-cycles with it.
  PHASE 2 (remove): b=0 AND base removed -> does the upper KEEP oscillating with the committed handedness?

  GENERATION  : autonomous upper survives drive removal (|z|~sqrt(mu)), handedness HELD -> a new register.
  TRANSDUCTION: a weak upper (mu<0, pure damping, the hybrid_cascade case) DECAYS to 0 on removal.

Usage (from mpa-conform root):  python scripts/hybrid_generation.py
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
MU, OMEGA = 1.0, 1.5            # upper Hopf: mu>0 -> autonomous limit cycle radius sqrt(mu)
A_S, B_S = 0.6, 0.5            # handedness bistability rate / base-bias strength


def base_field(th):
    d = np.zeros(3)
    for i in range(3):
        d[i] = WB + (KB / 3.0) * np.sum(np.sin(th - th[i] - ALPHA))
    return d


def base_chirality(th):
    return int(np.sign(np.sin(th[1] - th[0]) + np.sin(th[2] - th[1]) + np.sin(th[0] - th[2])))


def settle_base(seed, T=300.0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, 3)
    for _ in range(int(T / DT)):
        th = th + base_field(th) * DT
    return th


def run(seed, autonomous=True, T_lock=200.0, T_free=200.0):
    """phase 1: base biases the upper's handedness s; phase 2: base removed -- does the upper persist?"""
    rng = np.random.default_rng(seed + 11)
    th = settle_base(seed)
    chi = base_chirality(th)
    z = 0.05 * (rng.standard_normal() + 1j * rng.standard_normal())
    s = 0.0
    mu_eff = MU if autonomous else -1.0            # weak case: mu<0 (pure damping, the hybrid_cascade upper)
    h_base = float(chi)                            # the base's handedness (its Z2 chirality)
    amps, ss, phase = [], [], []
    # ---- phase 1: LOCK (base biases s) ----
    for _ in range(int(T_lock / DT)):
        th = th + base_field(th) * DT
        s = s + (A_S * (s - s ** 3) + B_S * h_base) * DT
        z = z + ((mu_eff + 1j * OMEGA * s) * z - (abs(z) ** 2) * z) * DT
        amps.append(abs(z)); ss.append(s); phase.append(np.angle(z))
    amp_lock, s_lock = abs(z), s
    # ---- phase 2: REMOVE the base (b=0, base gone) ----
    for _ in range(int(T_free / DT)):
        s = s + (A_S * (s - s ** 3)) * DT          # no base bias
        z = z + ((mu_eff + 1j * OMEGA * s) * z - (abs(z) ** 2) * z) * DT
        amps.append(abs(z)); ss.append(s); phase.append(np.angle(z))
    return dict(chi=chi, amp_lock=float(amp_lock), s_lock=float(s_lock),
                amp_free=float(abs(z)), s_free=float(s),
                amps=np.array(amps), ss=np.array(ss), phase=np.unwrap(np.array(phase)))


def winding_rate(phase, n_tail):
    """mean phase-advance rate over the last n_tail steps (the autonomous rotation, post-removal)."""
    tail = phase[-n_tail:]
    return float((tail[-1] - tail[0]) / (n_tail * DT))


def main():
    print("TRANSDUCTION vs GENERATION -- does the upper oscillation belong to the upper, or to the forcing?\n")
    print(f"upper Hopf: mu={MU} (autonomous limit cycle r=sqrt(mu)={np.sqrt(MU):.2f}), Omega={OMEGA};")
    print(f"handedness s bistable (a={A_S}), base bias b={B_S}. PHASE1 lock (base on) -> PHASE2 remove base.\n")
    n_free = int(200.0 / DT)

    # ---- AUTONOMOUS upper (the strong test) ----
    print("=" * 84)
    print("AUTONOMOUS upper (mu>0, own limit cycle): does it SURVIVE drive removal + HOLD handedness?")
    print("=" * 84)
    rows = []
    for s in range(12):
        r = run(s, autonomous=True)
        wr = winding_rate(r["phase"], n_free // 2)
        held = (np.sign(r["s_free"]) == np.sign(r["s_lock"])) and abs(r["s_free"]) > 0.8
        alive = r["amp_free"] > 0.5 * np.sqrt(MU)
        rows.append((r["chi"], r["amp_lock"], r["amp_free"], r["s_lock"], r["s_free"], wr, alive, held))
        print(f"  IC {s:>2}: chi_base={r['chi']:+d} | locked |z|={r['amp_lock']:.3f} s={r['s_lock']:+.2f} | "
              f"AFTER-REMOVAL |z|={r['amp_free']:.3f} s={r['s_free']:+.2f} wind={wr:+.2f} | "
              f"alive={alive} held={held}")
    alive_frac = np.mean([row[6] for row in rows])
    held_frac = np.mean([row[7] for row in rows])
    # transduction of handedness: is s_lock a consistent function of chi_base?
    prods = [int(np.sign(row[3])) * row[0] for row in rows]
    sel_consistent = max(prods.count(1), prods.count(-1)) / len(prods)
    print(f"\n  survives removal (|z|>0.5*sqrt(mu)): {100*alive_frac:.0f}% of ICs")
    print(f"  handedness HELD after removal: {100*held_frac:.0f}% of ICs")
    print(f"  base SELECTS handedness: sign(s_lock) consistent function of chi_base in {100*sel_consistent:.0f}% of ICs")

    # ---- WEAK upper (mu<0, the hybrid_cascade case): must DECAY on removal ----
    print("\n" + "=" * 84)
    print("WEAK upper (mu<0, pure damped focus = the hybrid_cascade upper): control -- must DECAY")
    print("=" * 84)
    rw = run(0, autonomous=False)
    print(f"  locked |z|={rw['amp_lock']:.3f} -> after removal |z|={rw['amp_free']:.4f}  "
          f"(decays to ~0: the circulation belonged to the forcing = TRANSDUCTION)")
    weak_decays = bool(rw["amp_free"] < 0.1)

    figure(run(0, autonomous=True), rw)

    generation = bool(alive_frac > 0.9 and held_frac > 0.9 and sel_consistent > 0.9 and weak_decays)
    print("\n" + "=" * 84)
    print("VERDICT -- transduction or GENERATION?")
    print("=" * 84)
    if generation:
        print("  ==> GENERATION. The autonomous upper SURVIVES drive removal (keeps limit-cycling at |z|~sqrt(mu))")
        print("      and HOLDS the handedness the base selected (s stays committed, bistable). The base only")
        print("      SELECTS the handedness (sign(s) is a consistent function of the base's chirality); the")
        print("      OSCILLATION belongs to the UPPER. The weak control (mu<0) decays to 0 -- that is the")
        print("      passive-transduction case (hybrid_cascade). So the heterogeneous cascade GENERATES a new")
        print("      autonomous dynamical register (the upper limit cycle), with the base self-lighting + ")
        print("      selecting its handedness -- the frustration-ascent generative idea, by stratification.")
        print("      (The upper, being an autonomous gapped chiral oscillator, can itself platform a further")
        print("      level -- the recursion continues, each level's handedness selected from below.)")
    else:
        print(f"  ==> NOT clean generation: alive={100*alive_frac:.0f}% held={100*held_frac:.0f}% "
              f"select={100*sel_consistent:.0f}% weak-decays={weak_decays}. Read honestly.")
    print("\n  SCOPE: minimal model (Hopf upper + bistable handedness + splay base). It shows the STRONG case")
    print("  is reachable (autonomous upper, base selects handedness), distinguishing it from passive")
    print("  transduction. Full end-to-end (3 such upper registers + meta-arena) + a real instance remain.")


def figure(ra, rw):
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), dpi=150)
    n_lock = int(200.0 / DT)
    t = np.arange(len(ra["amps"])) * DT
    ax[0].plot(t, ra["amps"], color="#2e7d32", lw=1.4, label="autonomous upper |z| (mu>0)")
    ax[0].plot(t, rw["amps"], color="#c62828", lw=1.4, label="weak upper |z| (mu<0, transduction)")
    ax[0].axvline(n_lock * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[0].axhline(np.sqrt(MU), color="#2e7d32", ls=":", lw=1, label=r"$\sqrt{\mu}$ (autonomous radius)")
    ax[0].set_xlabel("time"); ax[0].set_ylabel("upper amplitude |z|")
    ax[0].set_title("drive-removal test: autonomous upper SURVIVES (generation);\nweak upper DECAYS (transduction)")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    ax[1].plot(t, ra["ss"], color="#1565c0", lw=1.6, label="handedness s (autonomous)")
    ax[1].axvline(n_lock * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[1].axhline(0, color="gray", lw=0.6)
    ax[1].set_xlabel("time"); ax[1].set_ylabel("handedness s")
    ax[1].set_title("the base SELECTS the handedness; it is HELD after removal\n(s stays committed -- the upper's own bistable register)")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    fig.suptitle("transduction vs GENERATION — an autonomous upper register (base selects handedness, "
                 "oscillation is the upper's own)", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = OUT / "hybrid_generation.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
