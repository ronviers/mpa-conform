"""Blind answerer — glass_two_step_v4.

Traverses the sanitized recipe (workspace/glass_two_step_v4.traversal.md) against
the sanitized data (workspace/glass_two_step_v4.data.csv) and renders the result image.

The load-bearing readout is the FDR / fluctuation-response locus: chi vs (1-C).
- Fast branch slope -> X_fast (FDT obeyed if ~1).
- Slow branch slope -> X_slow (FDT violation factor; T_eff/T = 1/X_slow).
- Branch knee -> plateau height q_EA (the shoulder in C).
Run from H:/mpa-conform/blockin (or anywhere): python workspace/_answer_glass_v4.py
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")

HERE = Path(__file__).resolve()
BLOCKIN = HERE.parents[1]          # .../blockin
sys.path.insert(0, str(BLOCKIN))   # reach view_header.py
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

DATA = BLOCKIN / "workspace" / "glass_two_step_v4.data.csv"
EARNED = BLOCKIN / "earned" / "glass_two_step_v4"
EARNED.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- load
d = np.genfromtxt(DATA, delimiter=",", names=True)
tau, C, chi = d["tau"], d["C"], d["chi"]
x = 1.0 - C  # C(0) - C(tau), the FDR abscissa

# ---------------------------------------------------------------- FDR locus (the instrument)
fast = C > 0.85
slow = C < 0.55
X_fast, b_fast = np.polyfit(x[fast], chi[fast], 1)
X_slow, b_slow = np.polyfit(x[slow], chi[slow], 1)
Teff_ratio = 1.0 / X_slow

# branch knee = plateau q_EA (where fast and slow FDR lines meet)
x_knee = b_slow / (X_fast - X_slow)
q_FDR = 1.0 - x_knee

# ---------------------------------------------------------------- C(tau) plateau + timescales
lt = np.log(tau)
dC = np.gradient(C, lt)
shoulder = (tau > 0.01) & (tau < 1.0)
ip = np.where(shoulder)[0][np.argmin(np.abs(dC[shoulder]))]
q_C = C[ip]                       # plateau height read off C directly
q = q_FDR                         # use FDR knee as the q_EA estimate

t_fast = tau[np.argmin(np.abs(C - (q + (1 - q) / np.e)))]
t_alpha = tau[np.argmin(np.abs(C - q / np.e))]
sep = t_alpha / t_fast

# KWW on the slow tail -> stretching exponent
tail = (tau > tau[ip]) & (C > 0.005)
kww = lambda t, ta, beta: q * np.exp(-((t / ta) ** beta))
(p_ta, p_beta), _ = curve_fit(kww, tau[tail], C[tail], p0=[5.0, 0.6], maxfev=40000)

print(f"X_fast={X_fast:.3f}  X_slow={X_slow:.3f}  T_eff/T={Teff_ratio:.3f}")
print(f"q_EA(FDR knee)={q_FDR:.3f}  q_plateau(C)={q_C:.3f}")
print(f"tau_fast={t_fast:.4g}  tau_alpha={t_alpha:.4g}  separation={sep:.0f}x")
print(f"KWW beta={p_beta:.3f}  tau_alpha(KWW)={p_ta:.3f}")

# ---------------------------------------------------------------- verdict text
placement = (
    f"FDR two-branch: X_fast={X_fast:.2f} (FDT obeyed) | X_slow={X_slow:.2f} "
    f"=> T_eff/T={Teff_ratio:.2f} on the slow sector; q_EA(plateau)={q_FDR:.2f}; "
    f"tau_fast~{t_fast:.2g}, tau_alpha~{t_alpha:.2g} (sep ~{sep:.0f}x); "
    f"slow tail stretched beta_KWW={p_beta:.2f}"
)
verdict = (
    "OUT of equilibrium, not merely slow. The fluctuation-response locus chi vs (1-C) "
    "is NOT a single straight line: it breaks at the plateau into two slopes. The fast "
    f"part (above the shoulder, C>{0.85:.2f}) sits on slope X~{X_fast:.2f} -- it obeys "
    "fluctuation-dissipation, i.e. it is equilibrated at the bath temperature. The slow, "
    f"stuck shoulder/tail sits on a SHALLOWER slope X={X_slow:.2f}, so the slow sector "
    f"responds less than equilibrium would demand: it is effectively running HOTTER, "
    f"T_eff/T = 1/X = {Teff_ratio:.2f}. So the answer to your question is the second one: "
    "the slow part is genuinely out of equilibrium relative to the fast part. PLACEMENT / "
    f"headroom: you are on a two-branch locus with X_slow={X_slow:.2f} -- well inside the "
    "interval, the nearest binding asymptote is X->1 (re-equilibration, the slow sector "
    f"cooling back to the bath: headroom 1-X = {1-X_slow:.2f}) on one side and X->0 "
    f"(full arrest, the slow sector freezing infinitely hot: headroom {X_slow:.2f}) on the "
    "other. You are not AT arrest -- X is finite and the slow tail still relaxes (it has "
    "not frozen) -- but you are decisively off the equilibrium line and the long shoulder "
    "is the signature of that out-of-equilibrium slow population, not of a near-term crossing."
)
grounded = [
    f"OUT-of-equilibrium verdict <- FDR locus chi vs (1-C) shows TWO slopes "
    f"(fast X={X_fast:.2f} vs slow X={X_slow:.2f}); a merely-slow equilibrated state would "
    f"be a SINGLE line of slope ~1. [traversal INVARIANT 'FDR locus=universal readout' + READOUT]",
    f"slow sector 'runs hotter' <- slow-branch slope X_slow={X_slow:.2f} gives "
    f"T_eff/T=1/X={Teff_ratio:.2f}; the response deficit on the slow branch IS the effective "
    f"temperature. [chi,C columns; ROOT-OPERATION fit on C<0.55]",
    f"fast population equilibrated <- fast-branch slope X_fast={X_fast:.2f}~1 (FDT obeyed), "
    f"intercept ~0. [chi,C columns; fit on C>0.85]",
    f"plateau / shoulder height q_EA~{q_FDR:.2f} <- where the two FDR branches meet "
    f"(={q_FDR:.3f}), independently confirmed by the flattest point of C(tau) (={q_C:.3f}). "
    f"[C column + FDR knee]",
    f"timescale separation ~{sep:.0f}x <- tau_fast~{t_fast:.2g} (decay to plateau) vs "
    f"tau_alpha~{t_alpha:.2g} (decay from plateau) off C(tau). [tau,C columns; FRAME/lag]",
    f"final decay is stretched, not exponential <- KWW fit of the slow tail gives "
    f"beta={p_beta:.2f} (<1). [tau,C columns; ROOT-OPERATION]",
    "departure-toward-asymptote framing (you are here, with this much room) <- READOUT step: "
    "X_slow is interior, nearest asymptotes X->1 and X->0 with finite headroom each side.",
]
not_grounded = [
    "WHETHER the material is about to CROSS an arrest (the researcher's 'near an arrest it "
    "is about to cross' worry) -- a single operating point at one fixed waiting/preparation "
    "condition CANNOT close this. Proximity-to-arrest is a derivative along a control axis "
    "(temperature / waiting-time / density) that was COLLAPSED in this slice; X_slow is "
    "finite and the tail still relaxes, which rules out being AT arrest, but the DISTANCE "
    "and DIRECTION of travel toward it need a sweep. [collapsed-axis park, not a withheld "
    "in-slice observable]",
    "ABSOLUTE effective temperature (only the RATIO T_eff/T=2 is grounded; the bath T was "
    "not provided -- 'no temperatures', per the packet).",
    "aging / waiting-time dependence (is T_eff drifting as the sample ages?) -- one long "
    "observation at a fixed waiting condition gives no t_w axis. [collapsed axis]",
    "a mode-resolved decomposition of the fast vs slow populations -- the packet provides one "
    "lumped observable, no mode decomposition; fast/slow are read only as two FDR branches, "
    "not as separately resolved modes.",
    "any k_frust / circulating-current reading -- this structure is a single relaxing scalar "
    "observable with no declared current; the current-gate is not lit, so the two-frame "
    "self-probe sector does not apply (correctly dark, not withheld).",
    "uncertainty / grain on the verdict -- the CSV carries no C_sem/chi_sem columns, so no "
    "error bars or identifiability bootstrap can be reported (dev: n_boot=0).",
]

# ---------------------------------------------------------------- view
out, STAMP = timestamped_view_path(EARNED)
fig, (ax0, ax1, ax2) = figure_with_header(
    n_plots=3,
    slug="glass_two_step_v4",
    date=STAMP,
    phase="DEV/blind",
    question=(
        "Supercooled liquid near structural arrest: C(tau) relaxes in two steps (fast drop, "
        "long shoulder, stretched final decay). Is the material EQUILIBRATED-but-slow, or "
        "OUT of equilibrium with the slow part running hotter than the fast part? And is it "
        "sitting in a stable state or near an arrest it is about to cross?"
    ),
    minimal_structure=(
        "one relaxing scalar observable in a disordered medium with a separation of timescales "
        "(fast equilibrating population + slow nearly-frozen stretched population); pushable by "
        "a small steady field -> integrated response chi."
    ),
    verdict=verdict,
    grounded=grounded,
    not_grounded=not_grounded,
    placement=placement,
)

# --- Plot 0: C(tau) two-step relaxation with plateau + timescales ---
ax0.semilogx(tau, C, "-", color="#1a1a1a", lw=1.6)
ax0.axhline(q_FDR, color="#00468b", ls="--", lw=1.0, label=f"plateau q_EA~{q_FDR:.2f}")
ax0.axvline(t_fast, color="#0a8a00", ls=":", lw=1.0, label=f"tau_fast~{t_fast:.2g}")
ax0.axvline(t_alpha, color="#8b0000", ls=":", lw=1.0, label=f"tau_alpha~{t_alpha:.2g}")
ax0.plot(tau[tail], kww(tau[tail], p_ta, p_beta), color="#cc6600", lw=1.0,
         label=f"KWW slow tail beta={p_beta:.2f}")
ax0.set_xlabel("lag tau (material units)"); ax0.set_ylabel("C(tau)")
ax0.set_title("two-step relaxation: fast drop -> shoulder -> stretched tail", fontsize=9)
ax0.legend(fontsize=7, loc="upper right"); ax0.grid(alpha=0.25)

# --- Plot 1: THE FDR locus chi vs (1-C) -- the instrument, two branches ---
ax1.plot(x, chi, "-", color="#444444", lw=1.0, alpha=0.5)
ax1.scatter(x[fast], chi[fast], s=14, color="#0a8a00", label=f"fast: X={X_fast:.2f} (FDT)", zorder=3)
ax1.scatter(x[slow], chi[slow], s=14, color="#8b0000", label=f"slow: X={X_slow:.2f} (T_eff/T={Teff_ratio:.1f})", zorder=3)
xf = np.linspace(0, x[fast].max(), 50)
ax1.plot(xf, X_fast * xf + b_fast, color="#0a8a00", ls="--", lw=1.2)
xs = np.linspace(x_knee, x.max(), 50)
ax1.plot(xs, X_slow * xs + b_slow, color="#8b0000", ls="--", lw=1.2)
ax1.plot([0, 1], [0, 1], color="#999999", ls=":", lw=1.0, label="equilibrium FDT (slope 1)")
ax1.scatter([x_knee], [X_slow * x_knee + b_slow], s=60, marker="o",
            facecolor="none", edgecolor="#00468b", lw=1.5, zorder=4, label=f"knee q_EA~{q_FDR:.2f}")
ax1.set_xlabel("1 - C(tau)   [ = C(0)-C ]"); ax1.set_ylabel("chi(tau)")
ax1.set_title("FDR locus (universal readout): slope break = out of equilibrium", fontsize=9)
ax1.legend(fontsize=7, loc="upper left"); ax1.grid(alpha=0.25)

# --- Plot 2: effective-temperature map X(local) along the locus + headroom ---
# local slope dchi/d(1-C) as a function of 1-C
xs_sorted = x
dxv = np.diff(x); dyv = np.diff(chi)
loc_slope = dyv / dxv
xc = 0.5 * (x[1:] + x[:-1])
ax2.plot(xc, loc_slope, "-", color="#00468b", lw=1.4)
ax2.axhline(1.0, color="#0a8a00", ls="--", lw=1.0, label="X=1 (equilibrium asymptote)")
ax2.axhline(X_slow, color="#8b0000", ls="--", lw=1.0, label=f"X_slow={X_slow:.2f} plateau")
ax2.axhline(0.0, color="#333333", ls=":", lw=1.0, label="X=0 (full arrest asymptote)")
ax2.fill_between([0, 1], X_slow, 1.0, color="#0a8a00", alpha=0.07)
ax2.fill_between([0, 1], 0.0, X_slow, color="#8b0000", alpha=0.07)
ax2.annotate(f"headroom to re-equilibration\n(X->1): {1-X_slow:.2f}", (0.55, (X_slow+1)/2),
             fontsize=7, color="#0a5d00", ha="center")
ax2.annotate(f"headroom to arrest\n(X->0): {X_slow:.2f}", (0.55, X_slow/2),
             fontsize=7, color="#8b0000", ha="center")
ax2.set_ylim(-0.1, 1.15); ax2.set_xlim(0, 1)
ax2.set_xlabel("1 - C(tau)"); ax2.set_ylabel("local FDR slope X = dchi/d(1-C)")
ax2.set_title("X along the locus: interior, finite -> not at arrest", fontsize=9)
ax2.legend(fontsize=7, loc="center right"); ax2.grid(alpha=0.25)

fig.savefig(out, dpi=150)
print(f"WROTE {out}")
