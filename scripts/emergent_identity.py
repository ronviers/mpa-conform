r"""emergent_identity.py -- the LEGAL Gate-2 demonstration (the run-loop, not the latch).

Companion / corrective to hybrid_generation.py. That script's "GENERATION" verdict rests on an
autonomous upper whose self-gain mu>0 was INSERTED BY HAND -- an inert external-frame constant
(mpa-atlas receipts §amplitude-autonomy) -- and on a handedness s that is HELD (a bistable LATCH,
a STORED bit) after the drive is removed. That is the PARASITIC leg (generative-of-amplitude is
illegal) and the OPPOSITE of a run loop.

This script demonstrates the THREE legal, falsifiable components of character_composite's
emergent-identity node, on a minimal composite -- a 3-state continuous-time Markov cycle, the
Schnakenberg setting of the binding (mpa-atlas receipts §binding):

  MINTING        Two non-frustrated parts couple -> a frustrated UNION CYCLE neither had.
                 part A = the path 0-1-2 (a tree: no cycle -> A=0, J=0 even when driven).
                 part B = the single edge 2-0 (no cycle -> A=0, J=0).
                 couple (all three edges present) + drive F -> cycle affinity A=3F != 0, J != 0.
                 The protected circulation is MINTED by the coupling; absent in either part.

  PROTECTION     sign(A) is a discrete graph-flux invariant. A = sum_cycle ln(k_fwd/k_bwd) = 3F
                 depends ONLY on the drive tilt, NOT on the (symmetric) edge-rate magnitudes:
                 reciprocal/gradient deformations inject ZERO affinity, so sign(A) survives them
                 at ANY amplitude. It flips only by REWIRING (reversing the drive / cycle
                 orientation, F -> -F) -- a discrete change. (This is V-(b) on the minted cycle.)

  SUSTAINED      The minted bit is a NESS RUN LOOP, not a stored state. It exists iff BOTH
  IDENTITY       drive AND coupling are maintained:
                   drive off (F->0, coupling on):  J -> 0  (current decays; nothing latched).
                   coupling off (drop edge 2-0):   J -> 0  (union reverts to the path; bit gone).
                 Contrast the latch: hybrid_generation's held s would stay put. Here, kill either
                 knob and the identity vanishes -- the parts revert, nothing is stored.

Pre-registered (falsification over coverage):
  MINTING    vindicate: A_A=A_B=0 and A_union!=0 (J_union!=0).   kill: union A=0, or a part has A!=0.
  PROTECT    vindicate: 0 sign-flips over reciprocal graph-fixed deformations (any amp); flip on rewire.
             kill: a reciprocal graph-fixed deformation flips sign(A).
  SUSTAINED  vindicate: J->0 on drive-off AND J->0 on coupling-off (both knobs load-bearing).
             kill: J persists after drive removal (a stored/latched bit, not a run loop).

Usage (from mpa-conform root):  python scripts/emergent_identity.py
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
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = REPO_ROOT / "output" / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

# cycle 0->1->2->0 forward; base symmetric rate per edge; drive F tilts fwd/bwd by exp(+-F/2).
FWD = [(0, 1), (1, 2), (2, 0)]
BWD = [(1, 0), (2, 1), (0, 2)]
F_DRIVE = 0.8           # the thermodynamic drive (A = 3F when the cycle is closed)


def triad_rates(F, k0=(1.0, 1.0, 1.0), edges=("01", "12", "20")):
    """rates for the union triad; `edges` selects which of the 3 cycle edges are present (coupling)."""
    r = {}
    present = {"01": (0, 1), "12": (1, 2), "20": (2, 0)}
    for tag, (i, j) in present.items():
        if tag not in edges:
            continue
        k = k0[("01", "12", "20").index(tag)]
        r[(i, j)] = k * np.exp(+F / 2)
        r[(j, i)] = k * np.exp(-F / 2)
    return r


def generator(rates):
    L = np.zeros((3, 3))
    for (i, j), w in rates.items():
        L[j, i] += w
        L[i, i] -= w
    return L


def stationary(L):
    A = np.vstack([L, np.ones(3)])
    b = np.array([0.0, 0.0, 0.0, 1.0])
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    return p


def cycle_current(rates, p):
    """net probability current on edge 0->1 (= the cycle current, equal on every edge in NESS)."""
    if (0, 1) not in rates or (1, 0) not in rates:
        return 0.0
    return float(rates[(0, 1)] * p[0] - rates[(1, 0)] * p[1])


def affinity(rates):
    """Schnakenberg cycle affinity A = ln(prod fwd / prod bwd); 0 if the cycle is not closed."""
    if not all(e in rates for e in FWD + BWD):
        return 0.0
    fwd = np.prod([rates[e] for e in FWD])
    bwd = np.prod([rates[e] for e in BWD])
    return float(np.log(fwd / bwd))


def J_of(rates):
    return cycle_current(rates, stationary(generator(rates)))


# ----------------------------------------------------------------------------- MINTING
def test_minting():
    print("=" * 86)
    print("1. MINTING -- two non-frustrated parts couple into a frustrated union cycle")
    print("=" * 86)
    # part A: the path 0-1-2 (edges 01,12 only -- no closing edge). driven, but a tree: no current.
    rA = triad_rates(F_DRIVE, edges=("01", "12"))
    # part B: the single edge 2-0.
    rB = triad_rates(F_DRIVE, edges=("20",))
    # union: all three edges -> the cycle closes.
    rU = triad_rates(F_DRIVE, edges=("01", "12", "20"))
    AA, AB, AU = affinity(rA), affinity(rB), affinity(rU)
    JA, JB, JU = J_of(rA), J_of(rB), J_of(rU)
    print(f"  part A (path 0-1-2, driven): affinity={AA:+.3e}  current J={JA:+.3e}")
    print(f"  part B (edge 2-0,   driven): affinity={AB:+.3e}  current J={JB:+.3e}")
    print(f"  UNION  (cycle closed, driven): affinity={AU:+.3f}  current J={JU:+.4f}")
    minted = abs(AA) < 1e-9 and abs(AB) < 1e-9 and abs(AU) > 1e-6 and abs(JU) > 1e-6
    print(f"  => A=3F={3*F_DRIVE:.3f} matches union affinity: {np.isclose(AU, 3*F_DRIVE)}")
    print(f"  VINDICATE (parts carry no affinity, union does): {minted}")
    return dict(AA=AA, AB=AB, AU=AU, JA=JA, JB=JB, JU=JU, minted=minted)


# -------------------------------------------------------------------------- PROTECTION
def test_protection(n=400, amp=2.0, seed=0):
    print("\n" + "=" * 86)
    print("2. PROTECTION -- sign(A) is a discrete graph-flux invariant (reciprocal-deformation proof)")
    print("=" * 86)
    rng = np.random.default_rng(seed)
    A0 = affinity(triad_rates(F_DRIVE))
    s0 = np.sign(A0)
    # reciprocal (gradient) graph-fixed deformations: scale each edge's magnitude (fwd & bwd together).
    # these inject ZERO affinity -- the gauge-irremovable drive part is untouched.
    recip_flips, recip_dev = 0, 0.0
    for _ in range(n):
        k0 = np.exp(amp * rng.standard_normal(3))          # huge magnitude swings (amp=2 -> ~e^2 spread)
        Ad = affinity(triad_rates(F_DRIVE, k0=tuple(k0)))
        recip_dev = max(recip_dev, abs(Ad - A0))
        recip_flips += int(np.sign(Ad) != s0)
    # generic ASYMMETRIC deformations inject their own affinity; sign survives until that exceeds 3F
    # (= injecting a counter-drive, i.e. a re-driving / partial rewire). report the crossover, honestly.
    gen_flips = 0
    for _ in range(n):
        r = triad_rates(F_DRIVE)
        for e_f, e_b in zip(FWD, BWD):
            r[e_f] *= np.exp(amp * rng.standard_normal())
            r[e_b] *= np.exp(amp * rng.standard_normal())
        gen_flips += int(np.sign(affinity(r)) != s0)
    # rewire: reverse the drive (cycle orientation) -> sign MUST flip (the discrete bit).
    A_rew = affinity(triad_rates(-F_DRIVE))
    print(f"  A0 = {A0:+.3f}  (sign {s0:+.0f})")
    print(f"  reciprocal graph-fixed deformations (amp={amp}, n={n}): sign-flips = {recip_flips}/{n}; "
          f"max |dA| = {recip_dev:.2e}  (A is EXACTLY drive-set; magnitudes cancel)")
    print(f"  generic asymmetric deformations    (amp={amp}, n={n}): sign-flips = {gen_flips}/{n}  "
          f"(only when injected counter-affinity > 3F = a re-drive)")
    print(f"  REWIRE (F -> -F, reverse cycle orientation): A = {A_rew:+.3f}  -> sign flips: {np.sign(A_rew)!=s0}")
    protected = recip_flips == 0 and recip_dev < 1e-9 and (np.sign(A_rew) != s0)
    print(f"  VINDICATE (reciprocal-invariant, flips only on rewire): {protected}")
    return dict(A0=A0, recip_flips=recip_flips, recip_dev=recip_dev, gen_flips=gen_flips,
                A_rew=A_rew, n=n, amp=amp, protected=protected)


# ------------------------------------------------------------------- SUSTAINED IDENTITY
def relax_current(rates_from, rates_to, T=12.0, dt=0.002):
    """start at the NESS of rates_from, switch to rates_to at t=0, record J(t) under rates_to."""
    p = stationary(generator(rates_from))
    L = generator(rates_to)
    ts, Js = [], []
    n = int(T / dt)
    for k in range(n):
        p = p + (L @ p) * dt
        ts.append(k * dt)
        Js.append(cycle_current(rates_to, p))
    return np.array(ts), np.array(Js)


def test_sustained():
    print("\n" + "=" * 86)
    print("3. SUSTAINED IDENTITY -- a NESS run loop (needs drive AND coupling), not a stored state")
    print("=" * 86)
    rU = triad_rates(F_DRIVE, edges=("01", "12", "20"))         # drive on, coupling on
    rU_nodrive = triad_rates(0.0, edges=("01", "12", "20"))     # drive OFF, coupling on
    rU_nocoup = triad_rates(F_DRIVE, edges=("01", "12"))        # drive on, coupling OFF (path)
    J_on = J_of(rU)
    J_nodrive = J_of(rU_nodrive)
    J_nocoup = J_of(rU_nocoup)
    print(f"  drive ON , coupling ON  : J = {J_on:+.4f}   <- the minted identity")
    print(f"  drive OFF, coupling ON  : J = {J_nodrive:+.4e}   <- decays to 0 (run loop, not latched)")
    print(f"  drive ON , coupling OFF : J = {J_nocoup:+.4e}   <- 0 (union reverts to path; bit gone)")
    t_d, J_d = relax_current(rU, rU_nodrive)        # transient after drive-off
    t_c, J_c = relax_current(rU, rU_nocoup)         # transient after coupling-off
    run_loop = abs(J_on) > 1e-6 and abs(J_nodrive) < 1e-6 and abs(J_nocoup) < 1e-6
    decayed = abs(J_d[-1]) < 1e-4 and abs(J_c[-1]) < 1e-4
    print(f"  transient after drive-off:    J: {J_d[0]:+.4f} -> {J_d[-1]:+.2e}")
    print(f"  transient after coupling-off: J: {J_c[0]:+.4f} -> {J_c[-1]:+.2e}")
    print(f"  VINDICATE (bit needs BOTH knobs; J relaxes to 0, nothing stored): {run_loop and decayed}")
    return dict(J_on=J_on, J_nodrive=J_nodrive, J_nocoup=J_nocoup,
                t_d=t_d, J_d=J_d, t_c=t_c, J_c=J_c, run_loop=run_loop and decayed)


def figure(m, p, s):
    fig, ax = plt.subplots(1, 3, figsize=(16.5, 5), dpi=150)

    # panel 1: minting -- affinity of parts vs union
    labels = ["part A\n(path)", "part B\n(edge)", "union A⊗B\n(cycle)"]
    vals = [abs(m["AA"]), abs(m["AB"]), abs(m["AU"])]
    cols = ["#9e9e9e", "#9e9e9e", "#2e7d32"]
    ax[0].bar(labels, vals, color=cols, edgecolor="black", lw=0.8)
    ax[0].axhline(3 * F_DRIVE, color="#2e7d32", ls=":", lw=1, label=f"3F = {3*F_DRIVE:.1f}")
    ax[0].set_ylabel(r"cycle affinity $|\mathcal{A}|$ (nats)")
    ax[0].set_title("1. MINTING\nneither part is frustrated; the union cycle is\n"
                    r"($\mathcal{A}=0,0 \to 3F$) — minted by coupling")
    ax[0].legend(fontsize=8, frameon=False); ax[0].grid(alpha=0.3, axis="y")

    # panel 2: protection -- reciprocal deformations leave A fixed; rewire flips it
    ax[1].axhline(p["A0"], color="#1565c0", lw=2.0, label=r"$\mathcal{A}$ under recip. deform. (flat)")
    ax[1].scatter(np.arange(40), np.full(40, p["A0"]) + 1e-3 * np.random.default_rng(1).standard_normal(40),
                  s=10, color="#1565c0", alpha=0.5)
    ax[1].axhline(p["A_rew"], color="#c62828", lw=2.0, ls="--", label="rewire (F→−F): sign flips")
    ax[1].axhline(0, color="gray", lw=0.8)
    ax[1].set_ylabel(r"cycle affinity $\mathcal{A}$ (nats)")
    ax[1].set_title(f"2. PROTECTION\nreciprocal deform. (amp={p['amp']}, n={p['n']}): "
                    f"{p['recip_flips']}/{p['n']} flips, max|ΔA|={p['recip_dev']:.0e}\n"
                    "discrete graph-flux bit — flips only on rewire")
    ax[1].legend(fontsize=8, frameon=False); ax[1].grid(alpha=0.3, axis="y")

    # panel 3: sustained -- J decays to 0 when drive (or coupling) removed; the latch counterfactual stays
    ax[2].plot(s["t_d"], s["J_d"], color="#2e7d32", lw=1.8, label="drive removed → J→0 (run loop)")
    ax[2].plot(s["t_c"], s["J_c"], color="#00838f", lw=1.6, ls="-.", label="coupling removed → J→0")
    ax[2].axhline(s["J_on"], color="#c62828", lw=1.6, ls=":",
                  label="stored-state counterfactual (latched, stays)")
    ax[2].axhline(0, color="gray", lw=0.8)
    ax[2].set_xlabel("time after switch"); ax[2].set_ylabel("cycle current J")
    ax[2].set_title("3. SUSTAINED IDENTITY\nkill drive OR coupling → identity vanishes\n"
                    "(a run loop, not a stored state)")
    ax[2].legend(fontsize=8, frameon=False); ax[2].grid(alpha=0.3)

    fig.suptitle("Emergent identity (legal): coupling MINTS a protected NESS run loop neither part had — "
                 "sustained only while drive + coupling hold", fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = OUT / "emergent_identity.png"
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print(f"\nfigure: {path}")


def main():
    print("EMERGENT IDENTITY -- the legal Gate-2 demonstration (run loop, not latch)\n")
    print(f"3-state driven Markov cycle; drive F={F_DRIVE} (=> cycle affinity 3F={3*F_DRIVE:.2f}).\n")
    m = test_minting()
    p = test_protection()
    s = test_sustained()
    figure(m, p, s)
    print("\n" + "=" * 86)
    print("VERDICT")
    print("=" * 86)
    allpass = m["minted"] and p["protected"] and s["run_loop"]
    if allpass:
        print("  ALL THREE legal components demonstrated:")
        print("   - MINTING: coupling closes a union cycle neither part had (A: 0,0 -> 3F).")
        print("   - PROTECTION: sign(A) is reciprocal-deformation-invariant; flips only on rewire.")
        print("   - SUSTAINED IDENTITY: the current is a NESS run loop -- killing the drive OR the")
        print("     coupling sends J->0; nothing is stored. (Contrast hybrid_generation's HELD latch.)")
        print("\n  This is the LEGAL reading of frustration-ascent / character_composite: generative-of-")
        print("  chirality/topology (the minted bit flows with the affinity A, sustained by the drive),")
        print("  NOT generative-of-amplitude-autonomy (the inserted mu>0 latch -- §amplitude-autonomy).")
    else:
        print(f"  NOT all clean: minted={m['minted']} protected={p['protected']} run_loop={s['run_loop']}.")
    print("\n  SCOPE: minimal synthetic composite (3-state CTMC). Demonstrates the three components are")
    print("  jointly coherent and falsifiable; a real EMERGENT substrate carrying them is still owed")
    print("  (the frustration-ascent / Gate-2 joint instance).")


if __name__ == "__main__":
    main()
