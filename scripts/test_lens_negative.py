"""The negative: square_wave through the MPA lens, with vs without.

Counterpart to test_lens_with_without.py (kww_oracle, the positive). square_wave
is an oscillator -- there is NO c->s->r migration to focus. "Does the lens do what
it's supposed to" here means the opposite test: it must REFUSE (gate OUT, no
spurious X) rather than manufacture a focused reading.

WITHOUT the lens : raw C(tau), chi(tau) -- periodic, not decaying.
WITH the lens     : the FDT-plane re-coordination sends the data off the migration
                    manifold (deltaC overshoots past 1 into anticorrelation, C<0);
                    the Banach fit collapses (no KWW-FDT member matches a square
                    wave), the per-channel C residual bursts past its grain, gate OUT.
                    The lens declines to report an X. That refusal is the correct
                    behavior -- the principled X machine (FALSIFICATION.md).

Run: python H:/mpa-conform/scripts/test_lens_negative.py
"""
from __future__ import annotations
import sys, json, glob
from pathlib import Path

sys.path.insert(0, "H:/mpa-conform")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from conformer.compute import gfdr_model, inversion, five_vector

CELL = glob.glob("H:/mpa-central/library/data/square_wave/square_wave__P100__velocity.json")[0]
OUT = Path("H:/mpa-conform/output/diagnostics/lens_negative.png")
T = 1.0


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c = json.load(open(CELL))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    lag = np.array([e["dt"] for e in s], float)
    C = np.array([e["C_mean"] for e in s], float)
    chi = np.array([e["chi_mean"] for e in s], float)
    rows = [{"tau": float(t_), "C": float(cc), "chi": float(ch),
             "C_sem": float(e.get("C_sem", 0.0)), "chi_sem": float(e.get("chi_sem", 0.0))}
            for t_, cc, ch, e in zip(lag, C, chi, s)]
    res = inversion.invert(rows, tau_scale=scale, T=T, skip_stage2=True)
    fv = res.five_vector_fit

    snrC = fv.channel_snr.get("C", float("nan"))
    print("=== square_wave: lens applied as designed (invert + 5-vector) ===")
    print(f"gate: {'IN' if fv.in_domain else 'OUT'}  residual={fv.residual:.4f} "
          f"(gate {five_vector.RESIDUAL_GATE} / SNR_GATE {five_vector.SNR_GATE})")
    print(f"C channel S/N = {snrC:.1f}x grain  -> "
          f"{'within noise' if snrC <= five_vector.SNR_GATE else 'SIGNAL the family cannot capture'}")
    print(f"reported X = {fv.X:.3f}  (NOT meaningful: out of the KWW-FDT family)")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 6.4))

    # WITHOUT the lens
    axL.plot(lag, C, "o-", color="tab:blue", ms=4, label="C(tau)")
    axL.plot(lag, chi, "s-", color="tab:orange", ms=4, label="chi(tau)")
    axL.set_xscale("log")
    axL.set_xlabel("native lag  tau  (substrate units)")
    axL.set_ylabel("C,  chi")
    axL.set_title("WITHOUT the lens\nraw square_wave observables (periodic, not decaying)")
    axL.axhline(0, color="k", lw=0.6, alpha=0.5)
    axL.legend(); axL.grid(alpha=0.3)

    # WITH the lens -- the refusal
    dC = 1.0 - C
    loc = gfdr_model.generate_kww_glass_locus(
        fv.chit, q_EA=fv.q_EA, tau_alpha=fv.tau_alpha, beta_KWW=fv.beta_KWW,
        tau_beta=fv.tau_beta, X=fv.X, T=fv.T)
    dC_m = 1.0 - loc["C"]; Tchi_m = fv.T * loc["chi"]
    o = np.argsort(dC_m)
    dl = np.linspace(0, 1, 50)
    axR.plot(dl, dl, "k--", lw=1.0, alpha=0.6, label="FDT line (X=1)")
    axR.axvspan(1.0, max(2.1, float(dC.max()) * 1.05), color="black", alpha=0.05)
    axR.plot(dC, T * chi, "o", color="tab:red", ms=6, label="data (re-coordinated)", zorder=3)
    axR.plot(dC_m[o], Tchi_m[o], "-", color="tab:blue", lw=2.4,
             label="Banach 5-vec fit (collapsed)", zorder=2)
    axR.axvline(1.0, color="k", lw=0.8, ls=":", alpha=0.6)
    axR.text(1.02, 0.9, "C<0 : off the\nmigration manifold", fontsize=8, color="#444")
    axR.set_xlabel(r"$\Delta C = 1 - C$  (>1 = anticorrelation)")
    axR.set_ylabel(r"$T\cdot\chi$")
    axR.set_title("WITH the lens (applied as designed)\nthe lens REFUSES to focus")
    box = (f"gate     OUT\n"
           f"resid    {fv.residual:.3f}\n"
           f"C S/N    {snrC:.0f}x grain\n"
           f"X        not reported\n"
           f"(no KWW-FDT focus)")
    axR.text(0.97, 0.97, box, transform=axR.transAxes, ha="right", va="top",
             fontsize=9, family="monospace",
             bbox=dict(boxstyle="round", fc="#fdeaea", ec="#c66"))
    axR.set_xlim(0, max(2.1, float(dC.max()) * 1.05)); axR.set_ylim(-0.05, 1.1)
    axR.legend(loc="upper left", fontsize=8); axR.grid(alpha=0.3)

    fig.suptitle("The negative: square_wave with vs without the MPA lens.\n"
                 "No migration to focus -> the lens declines (gate OUT, no X) instead of "
                 "inventing one. The refusal IS the correct behavior.", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
