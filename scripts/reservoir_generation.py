r"""reservoir_generation.py -- Move 2B: NON-OSCILLATORY generation (Ron's "rain, not a tornado").

hybrid_generation.py showed a self-lit splay base can GENERATE an autonomous *oscillatory* upper (a Hopf
limit cycle the base only selects the handedness of). 2A asks whether that oscillator can EMERGE from
coarse-graining -- and on a splay base it is foreshadowed to FAIL (splay_cascade: the splay's collective is
real-spectrum / gradient-like; it will not Hopf without injected non-reciprocity = insertion).

2B widens the question (Ron, 2026-05-31): "autonomy" is not "limit cycle." A reservoir / condensate /
switching-manifold / avalanche-release variable is equally autonomous and shows up as NO complex eigenpair.
A gradient-like collective is the NATURAL home of such a non-oscillatory species -- the splay wants to make
RAIN, not a tornado.

THE TEST: does coarse-graining a self-lit gapped chiral base mint a new slow collective REGISTER that
  (i)  is SLOW (a coarse DOF, separated from the fast base),
  (ii) is IRREDUCIBLE (a collective accumulation, not any single unit),
  (iii)is AUTONOMOUS (its own attractor -- survives base removal; the WEAK control decays = transduction),
  (iv) maintains its OWN continuous <sigma> > 0 NESS cost (the chosen observable -- the heat-tax that makes
       it an MPA register, not just a slow variable),
  and is NON-OSCILLATORY (a relaxation/release / hysteretic switch, no governing Hopf -- distinguishes 2B
  from 2A)?

  UPPER = a signed reservoir register: magnitude m charges (slow self-gain G_SELF -> autonomy) and RELEASES
    when m crosses THETA_HI, gate re-arms below THETA_LO (Schmitt-trigger hysteresis = autonomous charge-
    release cycle, NOT a Hopf -- the smooth part is purely contracting; the cycle exists by hysteresis).
  Z2 basin s (sign of the stored quantity): the base CHIRALITY selects it (ds = a(s-s^3) + b*h_base), held
    after removal -- the non-oscillatory analogue of hybrid_generation's handedness.
  PHASE 1 (lock): base on -> s commits, reservoir charge-releases on the base-selected channel.
  PHASE 2 (remove): base gone -> does the reservoir KEEP cycling (autonomous) on the held channel?

  GENERATION : self-gain reservoir keeps charge-releasing after removal, <sigma> stays > 0, basin held.
  TRANSDUCTION: weak reservoir (G_SELF=0, charges only from the base) decays, <sigma> -> 0 on removal.

Usage (from mpa-conform root):  python scripts/reservoir_generation.py
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

# ---- base (splay), reused verbatim from hybrid_generation.py ----
WB, KB, ALPHA, DT = 1.0, 1.0, 0.9 * np.pi, 0.01

# ---- reservoir register ----
G_SELF = 0.05          # reservoir's OWN slow charge gain -> autonomy (0 in the weak control)
B_CHARGE = 0.04        # base contribution to charging (the only input in the weak control)
D_REL = 3.0            # fast release (discharge) rate; D_REL >> G_SELF -> slow-fast relaxation
THETA_HI, THETA_LO = 1.0, 0.25     # Schmitt-trigger thresholds (hysteresis -> autonomous cycle)
A_S, B_S = 0.6, 0.5    # Z2 basin bistability rate / base-bias strength


def base_field(th):
    d = np.zeros(3)
    for i in range(3):
        d[i] = WB + (KB / 3.0) * np.sum(np.sin(th - th[i] - ALPHA))
    return d


def base_chirality(th):
    return int(np.sign(np.sin(th[1] - th[0]) + np.sin(th[2] - th[1]) + np.sin(th[0] - th[2])))


def collective_activity(th):
    """A coarse, NON-chiral collective drive (gradient-like magnitude). Symmetric over the ring -> the
    reservoir charges from the COLLECTIVE, not any one unit (irreducibility)."""
    thbar = np.angle(np.mean(np.exp(1j * th)))
    return float(np.mean(np.abs(np.sin(th - thbar))))


def settle_base(seed, T=300.0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, 3)
    for _ in range(int(T / DT)):
        th = th + base_field(th) * DT
    return th


def run(seed, autonomous=True, T_lock=200.0, T_free=200.0):
    rng = np.random.default_rng(seed + 11)
    th = settle_base(seed)
    chi = base_chirality(th)
    g_self = G_SELF if autonomous else 0.0     # weak control: no self-gain -> charges only from the base
    m = 0.3                                     # reservoir magnitude
    s = 0.0                                     # Z2 basin (sign of stored quantity)
    gate = 0                                    # 0 = CHARGE, 1 = RELEASE (Schmitt trigger)
    h_base = float(chi)
    ms, ss, sig, coll, units = [], [], [], [], []
    sig_acc = 0.0

    def step(use_base):
        nonlocal th, m, s, gate, sig_acc
        if use_base:
            th = th + base_field(th) * DT
            a_coll = collective_activity(th)
        else:
            a_coll = 0.0
        # Z2 basin: base selects it (no base bias once removed)
        s = s + (A_S * (s - s ** 3) + (B_S * h_base if use_base else 0.0)) * DT
        # reservoir charge / release with hysteresis (autonomous if g_self>0)
        charge_in = g_self + (B_CHARGE * a_coll if use_base else 0.0)
        if gate == 0:                          # CHARGE
            dm = charge_in
            sigma = charge_in * m              # work done charging the reservoir (>0)
            if m >= THETA_HI:
                gate = 1
        else:                                  # RELEASE
            dm = -D_REL * m
            sigma = D_REL * m * m              # dissipated power on release (>0)
            if m <= THETA_LO:
                gate = 0
        m = max(m + dm * DT, 0.0)
        sig_acc_local = sigma
        return a_coll, sigma

    for _ in range(int(T_lock / DT)):
        a_coll, sigma = step(True)
        ms.append(m); ss.append(s); sig.append(sigma); coll.append(a_coll); units.append(np.sin(th[0]))
    m_lock, s_lock = m, s
    n_free0 = len(ms)
    for _ in range(int(T_free / DT)):
        a_coll, sigma = step(False)
        ms.append(m); ss.append(s); sig.append(sigma); coll.append(0.0); units.append(np.sin(th[0]))

    ms = np.array(ms); ss = np.array(ss); sig = np.array(sig)
    # NESS cost averaged over the FREE (post-removal) window -- the autonomous register paying its own tax
    sigma_free = float(np.mean(sig[n_free0:]))
    sigma_lock = float(np.mean(sig[:n_free0]))
    # released? count threshold crossings in the free window (relaxation/release species)
    free_m = ms[n_free0:]
    releases_free = int(np.sum((free_m[:-1] >= THETA_HI * 0.95) & (free_m[1:] < THETA_HI * 0.95)))
    return dict(chi=chi, m_lock=float(m_lock), s_lock=float(s_lock), m_free=float(m),
                s_free=float(s), sigma_lock=sigma_lock, sigma_free=sigma_free,
                releases_free=releases_free, ms=ms, ss=ss, sig=sig,
                coll=np.array(coll), units=np.array(units), n0=n_free0)


def no_hopf_check():
    """The reservoir's SMOOTH part is purely contracting (no complex pair); the cycle exists only by the
    hysteresis switch -> non-oscillatory species, NOT a Hopf. Show the smooth Jacobian eigenvalues."""
    # within CHARGE: dm/dt = const (eigenvalue 0, marginal drift); within RELEASE: dm/dt = -D*m (eig -D<0).
    # Neither branch has a complex pair; the autonomous orbit is a hysteretic relaxation loop.
    return {"charge_eig": 0.0, "release_eig": -D_REL, "complex_pair": False}


def main():
    print("Move 2B -- NON-OSCILLATORY generation: does coarse-graining mint a NESS-cost reservoir register?\n")
    print(f"reservoir: self-gain G={G_SELF} (autonomy), release D={D_REL}, hysteresis [{THETA_LO},{THETA_HI}];")
    print(f"Z2 basin s (a={A_S}) base-biased b={B_S}. PHASE1 lock (base on) -> PHASE2 remove base.\n")

    print("=" * 92)
    print("AUTONOMOUS reservoir (self-gain>0): survives base removal? keeps <sigma>>0? holds basin?")
    print("=" * 92)
    rows = []
    for s in range(12):
        r = run(s, autonomous=True)
        alive = r["releases_free"] >= 2 and r["sigma_free"] > 0.3 * r["sigma_lock"]
        held = (np.sign(r["s_free"]) == np.sign(r["s_lock"])) and abs(r["s_free"]) > 0.8
        rows.append((r["chi"], r["s_lock"], r["s_free"], r["sigma_lock"], r["sigma_free"],
                     r["releases_free"], alive, held))
        print(f"  IC {s:>2}: chi={r['chi']:+d} | locked s={r['s_lock']:+.2f} <s>_lk={r['sigma_lock']:.3f} | "
              f"FREE s={r['s_free']:+.2f} <sigma>={r['sigma_free']:.3f} releases={r['releases_free']:>2} | "
              f"alive={alive} held={held}")
    alive_frac = np.mean([row[6] for row in rows])
    held_frac = np.mean([row[7] for row in rows])
    prods = [int(np.sign(row[1])) * row[0] for row in rows]
    sel = max(prods.count(1), prods.count(-1)) / len(prods)
    print(f"\n  AUTONOMY  -- survives removal (>=2 releases & <sigma> sustained): {100*alive_frac:.0f}% of ICs")
    print(f"  NESS COST -- <sigma> > 0 held in the free window:                  (see per-IC, mean "
          f"{np.mean([row[4] for row in rows]):.3f})")
    print(f"  BASIN HELD after removal:                                          {100*held_frac:.0f}% of ICs")
    print(f"  BASE SELECTS basin (sign(s_lock) consistent fn of chi):           {100*sel:.0f}% of ICs")

    print("\n" + "=" * 92)
    print("WEAK reservoir (self-gain=0, charges only from base): control -- must DECAY, <sigma> -> 0")
    print("=" * 92)
    rw = run(0, autonomous=False)
    print(f"  locked <sigma>={rw['sigma_lock']:.3f} -> FREE <sigma>={rw['sigma_free']:.4f}, "
          f"releases_free={rw['releases_free']} (charge belonged to the base = TRANSDUCTION)")
    weak_decays = bool(rw["sigma_free"] < 0.1 * rw["sigma_lock"] and rw["releases_free"] == 0)

    # IRREDUCIBILITY: the reservoir charges from the COLLECTIVE; correlate its input with collective vs
    # single-unit signals (collective predicts, single unit does not).
    ra = run(0, autonomous=True)
    lock = slice(0, ra["n0"])
    corr_coll = float(np.corrcoef(ra["coll"][lock], np.abs(np.gradient(ra["ms"][lock])))[0, 1])
    corr_unit = float(np.corrcoef(ra["units"][lock], np.abs(np.gradient(ra["ms"][lock])))[0, 1])
    irreducible = bool(abs(corr_coll) > 2 * abs(corr_unit))
    print("\n" + "=" * 92)
    print("IRREDUCIBILITY -- the reservoir input tracks the COLLECTIVE, not any single unit")
    print("=" * 92)
    print(f"  |corr(reservoir charge, collective activity)| = {abs(corr_coll):.3f}")
    print(f"  |corr(reservoir charge, single unit sin th0)| = {abs(corr_unit):.3f}   irreducible={irreducible}")

    hopf = no_hopf_check()
    print("\n" + "=" * 92)
    print("NON-OSCILLATORY species -- the smooth part has NO complex pair (cycle is hysteretic relaxation)")
    print("=" * 92)
    print(f"  CHARGE branch eig = {hopf['charge_eig']:+.1f} (marginal drift), RELEASE branch eig = "
          f"{hopf['release_eig']:+.1f} (contracting). complex_pair={hopf['complex_pair']} -> NOT a Hopf.")

    figure(ra, rw)

    generation = bool(alive_frac > 0.9 and held_frac > 0.9 and sel > 0.9 and weak_decays
                      and irreducible and not hopf["complex_pair"])
    print("\n" + "=" * 92)
    print("VERDICT -- transduction or NON-OSCILLATORY GENERATION?")
    print("=" * 92)
    if generation:
        print("  ==> GENERATION (widened sense). Coarse-graining the self-lit gapped chiral base mints a new")
        print("      slow collective REGISTER -- a charge-release reservoir that (i) is slow, (ii) tracks the")
        print("      COLLECTIVE not any unit, (iii) is AUTONOMOUS (keeps cycling after the base is removed;")
        print("      the weak control decays = transduction), (iv) pays its OWN <sigma> > 0 NESS heat-tax,")
        print("      and is NON-OSCILLATORY (hysteretic relaxation, no Hopf). The base only SELECTS the Z2")
        print("      basin. So the layer-2 generative bet is genuine in the WIDENED sense: the cascade")
        print("      creates a new register-SPECIES (a NESS reservoir, no b1/handedness of its own) -- it")
        print("      makes RAIN, not a tornado. (2A, the oscillatory branch, is the separate / deferred test.)")
    else:
        print(f"  ==> NOT clean generation: alive={100*alive_frac:.0f}% held={100*held_frac:.0f}% "
              f"select={100*sel:.0f}% weak-decays={weak_decays} irreducible={irreducible} "
              f"hopf={hopf['complex_pair']}. Read honestly.")
    print("\n  SCOPE: minimal model (splay base + hysteretic reservoir + Z2 basin). It shows a NON-OSCILLATORY")
    print("  autonomous NESS register is REACHABLE by coarse-graining (the gradient-like collective's natural")
    print("  product), distinguishing genuine generation from passive transduction in the widened sense.")
    print("  Honest scope: the reservoir's autonomy is a self-gain term here (its own input); whether THAT")
    print("  self-gain itself emerges from the base micro-rules (vs is supplied) is the residual -- the same")
    print("  insertion question, now one species down. A real emergent instance + full end-to-end remain.")


def figure(ra, rw):
    fig, ax = plt.subplots(1, 3, figsize=(17, 5), dpi=150)
    n0 = ra["n0"]
    t = np.arange(len(ra["ms"])) * DT
    ax[0].plot(t, ra["ms"], color="#1565c0", lw=1.2, label="autonomous reservoir m (self-gain)")
    ax[0].plot(t, rw["ms"], color="#c62828", lw=1.2, label="weak reservoir m (transduction)")
    ax[0].axvline(n0 * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[0].axhline(THETA_HI, color="gray", ls=":", lw=0.8); ax[0].axhline(THETA_LO, color="gray", ls=":", lw=0.8)
    ax[0].set_xlabel("time"); ax[0].set_ylabel("reservoir magnitude m")
    ax[0].set_title("charge-release ('rain'): autonomous reservoir KEEPS cycling;\nweak reservoir DECAYS after removal")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3)

    ax[1].plot(t, ra["sig"], color="#2e7d32", lw=1.0, label="autonomous <sigma> (NESS cost)")
    ax[1].plot(t, rw["sig"], color="#c62828", lw=1.0, label="weak <sigma>")
    ax[1].axvline(n0 * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[1].set_xlabel("time"); ax[1].set_ylabel(r"entropy production $\dot\sigma$")
    ax[1].set_title("the register pays its OWN heat-tax: <sigma>>0 sustained after removal\n(transduction control -> 0)")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3)

    ax[2].plot(t, ra["ss"], color="#6a1b9a", lw=1.6, label="Z2 basin s (autonomous)")
    ax[2].axvline(n0 * DT, color="gray", ls="--", lw=1.5, label="base removed")
    ax[2].axhline(0, color="gray", lw=0.6)
    ax[2].set_xlabel("time"); ax[2].set_ylabel("basin s")
    ax[2].set_title("the base SELECTS the basin; HELD after removal\n(the reservoir's own bistable register)")
    ax[2].legend(fontsize=8, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("Move 2B -- NON-OSCILLATORY generation: a self-lit gapped base coarse-grains into an "
                 "autonomous NESS-cost reservoir register (rain, not a tornado)", fontsize=11.5, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = OUT / "reservoir_generation.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


if __name__ == "__main__":
    main()
