r"""palm_self_probe_current.py -- STEP 2 (calibration): which current is the self-probe current?

The `palm-self-probe` crux (mpa-atlas/framework/character_frontier.md). For the Palm/time-average
two-frame to reinstantiate the iff-chain in the queueing domain, the self-probe current must be
the GAUGE-IRREMOVABLE routing-cycle affinity -- NOT the always-present arrival/throughput rate.
The tell that this matters: M/G/1 shows PASTA (arrival-frame coincidence) WITHOUT reversibility,
so "do the frames coincide" cannot be the diagnostic; the state-space cycle affinity must be.

Minimal discriminator: a 3-station cyclic routing CTMC (the queueing analog of banach_frustrated
/ the Harary triad). States 0,1,2 on a cycle; forward rate a (i -> i+1), backward rate b (i -> i-1).
By rotational symmetry pi = (1/3,1/3,1/3) for all a,b. Exact, no simulation:

    throughput (event rate)  = a + b                    (the arrival/departure analog)
    net cycle current   J    = (a - b) / 3              (the gauge-irremovable circulation)
    routing affinity    A    = 3 * ln(a/b)              (Kolmogorov on the 3-cycle)
    entropy production <sigma> = (a - b) * ln(a/b) = J * A
    self-probe tightness defined iff J != 0  (a != b)

We HOLD throughput a+b constant and sweep the bias a/b from 1 (reversible) upward:
  - throughput stays FLAT and nonzero throughout  -> it is NOT the topological diagnostic
  - J, A, <sigma> rise from exactly 0 at a=b      -> THEY are the self-probe diagnostic
  - the iff-chain holds in the routing graph:  J != 0  <=>  A != 0  <=>  directed routing cycle

a = b is the reversible case: A = 0, no protected current, self-probe UNDEFINED -- the queueing
analog of v12's reversible M/M/1 (X = 1). a != b is the Cat-10 queueing triad.

Run from mpa-conform root:  python scripts/palm_self_probe_current.py
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

THROUGHPUT = 2.0   # a + b held constant across the sweep (the arrival/departure rate)


def cycle3(a: float, b: float) -> dict:
    """Exact stationary quantities of the symmetric 3-state cyclic CTMC (forward a, backward b)."""
    pi = np.array([1.0, 1.0, 1.0]) / 3.0           # rotational symmetry
    throughput = float(pi.sum() * (a + b))         # total event (transition) rate = a + b
    J = float(pi[0] * a - pi[1] * b)               # net current per edge = (a - b)/3
    A = 3.0 * np.log(a / b) if (a > 0 and b > 0) else float("nan")   # Kolmogorov affinity, nats
    # Schnakenberg EP on the single 3-cycle: sum over edges of (J_fwd - J_bwd) ln(J_fwd/J_bwd)
    Jf, Jb = pi[0] * a, pi[1] * b
    sigma = float(3.0 * (Jf - Jb) * np.log(Jf / Jb)) if (Jf > 0 and Jb > 0) else 0.0
    selfprobe_defined = abs(J) > 1e-12
    return dict(a=a, b=b, throughput=throughput, J=J, A=A, sigma=sigma,
                JA=J * A, selfprobe=selfprobe_defined)


def main() -> None:
    print("STEP 2 -- palm-self-probe: the self-probe current is the routing-cycle affinity, NOT the throughput.")
    print(f"3-state cyclic routing CTMC; throughput a+b held = {THROUGHPUT} across the bias sweep.\n")

    # bias a/b swept from 1 (reversible) upward, at fixed a+b
    ratios = [1.0, 1.25, 1.5, 2.0, 3.0, 5.0]
    rows = []
    for r in ratios:
        a = THROUGHPUT * r / (1.0 + r)
        b = THROUGHPUT - a
        rows.append(cycle3(a, b))

    hdr = (f"{'a/b':>5} {'a':>6} {'b':>6} | {'throughput':>10} | {'J (current)':>11} "
           f"{'A (nats)':>9} {'<sigma>':>9} {'J*A':>8} | self-probe")
    print(hdr); print("-" * len(hdr))
    for r, m in zip(ratios, rows):
        sp = "DEFINED" if m["selfprobe"] else "undefined"
        print(f"{r:>5.2f} {m['a']:>6.3f} {m['b']:>6.3f} | {m['throughput']:>10.3f} | "
              f"{m['J']:>11.4f} {m['A']:>9.4f} {m['sigma']:>9.4f} {m['JA']:>8.4f} | {sp}")

    tp = np.array([m["throughput"] for m in rows])
    print("\n================ VERDICT ================")
    print(f"THROUGHPUT is FLAT at {tp.mean():.3f} (spread {100*tp.std()/tp.mean():.1g}%) and NONZERO at every bias,")
    print("including the reversible a=b point. So throughput cannot be the self-probe current --")
    print("keying the self-probe to it would WRONGLY define a self-probe for the reversible queue")
    print("(the M/M/1 / v12 X=1 case). The current that switches on with broken reversibility is J:")
    print("  J = 0, A = 0, <sigma> = 0 at a=b (reversible)  ->  self-probe UNDEFINED  (= v12 M/M/1, X=1)")
    print("  J != 0  <=>  A != 0  <=>  directed routing cycle (a != b)  ->  self-probe DEFINED (Cat-10 triad)")
    print("  and <sigma> = J * A holds exactly (the bridge), so the self-probe current is the")
    print("  GAUGE-IRREMOVABLE routing-cycle circulation.")
    print("\nM/G/1 subtlety resolved: PASTA = ARRIVAL-frame coincidence, which can hold without")
    print("reversibility -- so frame-coincidence is NOT the diagnostic. The self-probe keys to the")
    print("STATE-SPACE cycle affinity A (Kolmogorov), which is 0 exactly when the routing is reversible.")
    print("This de-risks `palm-self-probe`'s up-gate: the protected current = routing-cycle affinity.")

    # ---- figure: throughput flat vs J/A/sigma switching on ----
    biases = np.linspace(1.0, 5.0, 60)
    aa = THROUGHPUT * biases / (1.0 + biases)
    bb = THROUGHPUT - aa
    Js = (aa - bb) / 3.0
    As = 3.0 * np.log(aa / bb)
    sig = (aa - bb) * np.log(aa / bb)
    tput = aa + bb

    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
    ax[0].plot(biases, tput, color="#dd8b1a", lw=2.2, label="throughput a+b (event rate)")
    ax[0].plot(biases, Js, color="#2b6cb0", lw=2.0, label="J  (net cycle current)")
    ax[0].plot(biases, As, color="#2f855a", lw=2.0, label="A  (routing affinity, nats)")
    ax[0].plot(biases, sig, color="#c53030", lw=2.0, ls="--", label=r"$\langle\sigma\rangle = J\cdot A$")
    ax[0].axvline(1.0, color="gray", lw=1, ls=":")
    ax[0].annotate("reversible (a=b): J=A=<sigma>=0\nself-probe undefined  (= v12 M/M/1, X=1)",
                   xy=(1.0, 0.0), xytext=(1.6, 1.05), fontsize=8, color="#555",
                   arrowprops=dict(arrowstyle="->", color="#999"))
    ax[0].set_xlabel("routing bias  a/b"); ax[0].set_ylabel("rate / nats")
    ax[0].set_title("throughput FLAT & nonzero; J, A, <sigma> switch on with broken reversibility")
    ax[0].legend(fontsize=9, frameon=False); ax[0].grid(alpha=0.3)

    ax[1].plot(As, Js, color="#6b46c1", lw=2.2)
    ax[1].scatter([0], [0], s=80, color="gray", zorder=3)
    ax[1].annotate("reversible: A=0, J=0\n(self-probe undefined)", (0, 0), textcoords="offset points",
                   xytext=(40, 20), fontsize=8, color="#555",
                   arrowprops=dict(arrowstyle="->", color="#999"))
    ax[1].set_xlabel("routing affinity A (nats)"); ax[1].set_ylabel("net cycle current J")
    ax[1].set_title("the iff-chain in the routing graph:\nJ != 0  <=>  A != 0  <=>  directed cycle")
    ax[1].grid(alpha=0.3)

    fig.suptitle("STEP 2 -- palm-self-probe: self-probe current = routing-cycle affinity, not throughput",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out_dir = REPO_ROOT / "output" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "step2_palm_self_probe_current.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    main()
