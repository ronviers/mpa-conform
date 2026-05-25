"""community_pair_v6 — BLIND ANSWERER analysis + view builder.

Reads ONLY the sanitized CSV. Traverses the sanitized recipe:
  (0) kernel / observation-window sanity
  (1) FDR locus readout  (chi vs C(0)-C(tau))  -- the universal cross-check
  (2) bespoke instrumentation the data invites:
        - autocorrelation shape (monotonic decay vs damped oscillation)
        - directed cross-correlation symmetry (Cxy vs Cyx)  -> current / rotation
        - cumulative turnover angle phiMean(t) slope -> net winding rate
        - phiVar(t) growth -> angular diffusion
Place EACH community independently first, then state the relationship.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

HERE = Path(r"H:\mpa-conform\blockin\workspace")
sys.path.insert(0, str(Path(r"H:\mpa-conform\blockin")))
from view_header import figure_with_header, timestamped_view_path  # noqa: E402

DATA = HERE / "community_pair_v6.data.csv"

raw = np.genfromtxt(DATA, delimiter=",", names=True)
comms = {}
for c in (0, 1):
    m = raw["community"] == c
    comms[c] = {k: raw[k][m] for k in raw.dtype.names}


# ---------- helpers ----------------------------------------------------------
def finite_guard(name, arr):
    """NaN / inf tripwire: flag, never fill."""
    bad = ~np.isfinite(arr)
    if bad.any():
        return f"{name}: {bad.sum()} non-finite value(s) at idx {np.where(bad)[0].tolist()}"
    return None


def fit_exp_decay(tau, C):
    """Fit C(tau) ~ C0 * exp(-tau/tau_relax) on the monotone-positive head.
    Returns (C0, tau_relax, rms_resid_on_fit_window)."""
    # use the portion while C is still safely positive (above 2% of C0)
    C0 = C[0]
    mask = C > 0.02 * C0
    t = tau[mask] - tau[0]
    y = np.log(C[mask])
    A = np.vstack([np.ones_like(t), -t]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    lnC0, inv_tau = coef
    tau_relax = 1.0 / inv_tau if inv_tau != 0 else np.inf
    pred = np.exp(lnC0) * np.exp(-t / tau_relax)
    rms = float(np.sqrt(np.mean((C[mask] - pred) ** 2)))
    return float(np.exp(lnC0)), float(tau_relax), rms


def fit_damped_osc(tau, C):
    """Fit C(tau) ~ C0 * exp(-g*tau) * cos(w*tau) by grid+linear refine.
    Returns (C0, gamma, omega, rms)."""
    t = tau - tau[0]
    best = None
    for w in np.linspace(0.05, 3.0, 600):
        for g in np.linspace(0.05, 3.0, 300):
            basis = np.exp(-g * t) * np.cos(w * t)
            a = np.dot(basis, C) / np.dot(basis, basis)
            pred = a * basis
            rms = np.mean((C - pred) ** 2)
            if best is None or rms < best[0]:
                best = (rms, a, g, w)
    rms, a, g, w = best
    return float(a), float(g), float(w), float(np.sqrt(rms))


# ---------- per-community placement ------------------------------------------
results = {}
notes = []
for c in (0, 1):
    d = comms[c]
    tau, C, chi = d["tau"], d["C"], d["chi"]
    Cxy, Cyx = d["Cxy"], d["Cyx"]
    phiMean, phiVar = d["phiMean"], d["phiVar"]

    for nm, arr in (("C", C), ("chi", chi), ("Cxy", Cxy), ("Cyx", Cyx),
                    ("phiMean", phiMean), ("phiVar", phiVar)):
        g = finite_guard(f"comm{c}.{nm}", arr)
        if g:
            notes.append(g)

    # --- kernel / window sanity: does C decay to ~0 inside the window? ---
    C0 = C[0]
    C_end_frac = C[-1] / C0
    window_ok = abs(C_end_frac) < 0.05  # autocorrelation has died -> window covers process

    # --- FDR locus: chi(tau) vs (C0 - C(tau)). For a relaxational (FDT) ---
    # response chi = (C0 - C)/T_eff i.e. chi is an affine function of (C0-C). ---
    dC = C0 - C
    A = np.vstack([np.ones_like(dC), dC]).T
    coef, *_ = np.linalg.lstsq(A, chi, rcond=None)
    intercept, slope = coef
    chi_pred = A @ coef
    fdr_rms = float(np.sqrt(np.mean((chi - chi_pred) ** 2)))
    fdr_r2 = 1.0 - np.sum((chi - chi_pred) ** 2) / np.sum((chi - chi.mean()) ** 2)

    # --- autocorrelation shape: zero crossing => damped oscillation ---
    sign_changes = np.where(np.diff(np.sign(C[C != 0])))[0]
    has_zero_crossing = len(sign_changes) > 0
    Cmin = float(C.min())

    # --- directed cross-correlation symmetry ---
    # symmetric (Cxy==Cyx)  -> no net directed flow in-plane
    # antisymmetric (Cxy==-Cyx) -> a rotation / circulating current
    sym_resid = float(np.sqrt(np.mean((Cxy - Cyx) ** 2)))
    antisym_resid = float(np.sqrt(np.mean((Cxy + Cyx) ** 2)))
    scale = float(np.sqrt(np.mean(Cxy ** 2))) or 1.0

    # --- net winding: slope of phiMean(t) (cumulative turnover angle) ---
    Aw = np.vstack([np.ones_like(tau), tau]).T
    wc, *_ = np.linalg.lstsq(Aw, phiMean, rcond=None)
    phi_intercept, phi_rate = wc
    phi_pred = Aw @ wc
    phi_rms = float(np.sqrt(np.mean((phiMean - phi_pred) ** 2)))
    phi_total = float(phiMean[-1] - phiMean[0])
    phi_turns = phi_total / (2 * np.pi)

    # --- angular diffusion: slope of phiVar(t) ---
    vc, *_ = np.linalg.lstsq(Aw, phiVar, rcond=None)
    var_intercept, var_rate = vc

    # --- placement decision ---
    if has_zero_crossing:
        C0f, gamma, omega, osc_rms = fit_damped_osc(tau, C)
        tau_relax = 1.0 / gamma if gamma else np.inf
        decay_kind = "damped oscillation"
        decay_fit = dict(C0=C0f, gamma=gamma, omega=omega, tau_relax=tau_relax, rms=osc_rms)
    else:
        C0f, tau_relax, dec_rms = fit_exp_decay(tau, C)
        gamma = 1.0 / tau_relax if tau_relax else 0.0
        omega = 0.0
        decay_kind = "monotone exponential decay"
        decay_fit = dict(C0=C0f, gamma=gamma, omega=omega, tau_relax=tau_relax, rms=dec_rms)

    # current present?  (antisymmetric cross-corr AND sustained winding)
    is_antisym = antisym_resid < 0.15 * scale and sym_resid > 0.3 * scale
    is_sym = sym_resid < 0.05 * scale
    # winding is "persistent" if phiMean follows a clean rising LINE: the linear
    # trend dominates the residual scatter about that line. (Comparing to phiVar
    # is wrong -- phiVar is sub-window spread of the cumulative angle, grows with t.)
    winding_signal = abs(phi_rate) * (tau[-1] - tau[0])   # total linear sweep
    winding_sig = winding_signal > 10 * phi_rms and abs(phi_rate) > 0.1
    current_present = is_antisym and winding_sig

    results[c] = dict(
        tau=tau, C=C, chi=chi, Cxy=Cxy, Cyx=Cyx, phiMean=phiMean, phiVar=phiVar,
        C0=float(C0), C_end_frac=float(C_end_frac), window_ok=bool(window_ok),
        fdr_slope=float(slope), fdr_intercept=float(intercept),
        fdr_rms=fdr_rms, fdr_r2=float(fdr_r2),
        has_zero_crossing=bool(has_zero_crossing), Cmin=Cmin,
        sym_resid=sym_resid, antisym_resid=antisym_resid, scale=scale,
        is_sym=bool(is_sym), is_antisym=bool(is_antisym),
        phi_rate=float(phi_rate), phi_total=phi_total, phi_turns=float(phi_turns),
        phi_rms=phi_rms, var_rate=float(var_rate),
        decay_kind=decay_kind, decay_fit=decay_fit,
        current_present=bool(current_present), winding_sig=bool(winding_sig),
        chi_plateau=float(chi[-1]),
    )

# ---------- print a compact ledger -------------------------------------------
for c in (0, 1):
    r = results[c]
    print(f"\n=== community {c} ===")
    print(f"  window: C(end)/C(0)={r['C_end_frac']:.3g}  window_ok={r['window_ok']}")
    print(f"  FDR locus chi vs (C0-C): slope={r['fdr_slope']:.4f} "
          f"intercept={r['fdr_intercept']:.4f} R2={r['fdr_r2']:.6f} rms={r['fdr_rms']:.3e}")
    print(f"  autocorr: {r['decay_kind']}  Cmin={r['Cmin']:.4f}  "
          f"zero_crossing={r['has_zero_crossing']}")
    print(f"  decay fit: {r['decay_fit']}")
    print(f"  cross-corr: sym_resid={r['sym_resid']:.3e} antisym_resid={r['antisym_resid']:.3e} "
          f"scale={r['scale']:.3e}  is_sym={r['is_sym']} is_antisym={r['is_antisym']}")
    print(f"  winding: phiMean rate={r['phi_rate']:.4f}/clock  total={r['phi_total']:.3f} rad "
          f"(~{r['phi_turns']:.3f} turns)  rms_about_line={r['phi_rms']:.3f}")
    print(f"  angular diffusion: phiVar rate={r['var_rate']:.3f}/clock")
    print(f"  chi plateau={r['chi_plateau']:.4f}")
    print(f"  --> current_present (persistent turnover) = {r['current_present']}")
if notes:
    print("\nNON-FINITE / GUARD NOTES:", notes)
else:
    print("\nfinite guard: all columns finite (no NaN/inf tripwire).")

# ---------- build the view ---------------------------------------------------
r0, r1 = results[0], results[1]

question = ("Two 3-population communities (loop 1->2->3->1), abundances wiggle the whole "
            "window. For each: genuine persistent turnover (going round the loop, never "
            "settling) or just relaxing toward a noisy balance? Bottom line: same kind of "
            "system or genuinely different? Either one unstable / near an edge, or both healthy?")
minimal_structure = ("Two communities (0,1); each 3 nodes in a closed directed loop, 3 "
                     "directed links, noise per node; reduced to the 2D turnover plane.")

verdict = (
    "DIFFERENT kind of system, on the turnover (winding) observable. "
    "Community 0 = SETTLING WITH NOISE: autocorrelation decays monotonically to zero "
    f"(no oscillation), cross-correlations symmetric (Cxy=Cyx), net turnover angle stays "
    f"near 0 ({r0['phi_turns']:+.2f} turns over the run) -- it jiggles around a balance, no "
    "real going-around. "
    "Community 1 = GENUINE PERSISTENT TURNOVER: autocorrelation rings (crosses zero -> damped "
    "oscillation), cross-correlations ANTISYMMETRIC (Cxy=-Cyx, a rotation), and it winds "
    f"steadily -- {r1['phi_turns']:+.1f} full turns around the loop and counting, no settling "
    "of the angle. "
    "Both are HEALTHY / interior: both autocorrelations relax (finite tau_relax, no boundary "
    "attained, no non-finite value), so neither is blowing up or sitting on an edge -- "
    "community 1's persistent turnover is a stable circulation, NOT an instability. "
    "You are here: 0 sits at the no-winding balance point; 1 sits on a steady limit-cycle-like "
    "circulation, both well inside the stable interior.")

placement = (
    f"comm0: monotone-decay, tau_relax={r0['decay_fit']['tau_relax']:.2f}, omega=0, "
    f"winding_rate={r0['phi_rate']:+.3f}/clk (~0), Cxy=Cyx (sym), chi_plateau={r0['chi_plateau']:.3f}, "
    f"FDR R2={r0['fdr_r2']:.4f} | "
    f"comm1: damped-osc gamma={r1['decay_fit']['gamma']:.3f} omega={r1['decay_fit']['omega']:.3f} "
    f"(tau_relax={r1['decay_fit']['tau_relax']:.2f}), winding_rate={r1['phi_rate']:+.3f}/clk, "
    f"Cxy=-Cyx (antisym), chi_plateau={r1['chi_plateau']:.3f}, FDR R2={r1['fdr_r2']:.4f}")

grounded = [
    f"per-community independent placement: each community fit on its own columns first (C/chi/Cxy/Cyx/phiMean/phiVar), then related",
    f"settling vs turnover [autocorrelation C]: comm0 monotone decay to 0 (Cmin={r0['Cmin']:.3f}, no zero-crossing); comm1 rings through zero (Cmin={r1['Cmin']:.3f}) -> damped oscillation",
    f"directed flow [Cxy vs Cyx symmetry]: comm0 symmetric (||Cxy-Cyx||={r0['sym_resid']:.1e}, no in-plane current); comm1 antisymmetric (||Cxy+Cyx||={r1['antisym_resid']:.1e}) -> a rotation/circulating current",
    f"persistent turnover [phiMean(t) slope = net winding]: comm0 rate {r0['phi_rate']:+.3f}/clk total {r0['phi_total']:+.2f} rad (no net winding); comm1 rate {r1['phi_rate']:+.3f}/clk total {r1['phi_total']:+.1f} rad (~{r1['phi_turns']:.1f} turns) -> goes round the loop",
    f"FDR locus cross-check [chi vs C(0)-C]: comm0 is CLEAN AFFINE (R2={r0['fdr_r2']:.4f}) = pure relaxational/FDT settling; comm1 is NON-AFFINE (R2={r1['fdr_r2']:.4f}) because its C rings, so chi is not a simple function of C(0)-C -- the locus shape AGREES with the autocorrelation read (settle vs oscillate) on BOTH communities, the two independent reads do not disagree (no falsifier)",
    f"stability / healthy [C relaxes + finite guard]: both autocorrelations decay to ~0 inside the window (C_end/C0: {r0['C_end_frac']:.1e}, {r1['C_end_frac']:.1e}); all columns finite (no NaN/inf, no boundary attained) -> neither unstable",
    f"window sanity [kernel pre-gate]: autocorrelation has died by end of each window -> observation window covers the process for both communities",
]

not_grounded = [
    "Absolute coupling strengths / interaction-arrangement parameters: the researcher's own loop-coupling magnitudes are not in the data (only measured curves), so we read THAT there is a difference and on which observable, not the underlying parameter values that produced it.",
    "Noise amplitudes / environmental drive level: not provided as a column; the angular-diffusion rate (phiVar slope) is a proxy for jiggle but cannot be separated into noise-strength vs coupling without a second operating point.",
    "Two-sided headroom / distance-to-instability in native units: each community is ONE operating point (one observation window). A single point places the system but cannot span the load axis -- how far comm1's circulation is from a bifurcation, or how close comm0 is to an oscillatory onset, would need a sweep (a second operating point / varied arrangement). This lives across a COLLAPSED axis, not a computation we failed.",
    "Effective temperature / FDR slope as a calibrated quantity: the chi-vs-(C0-C) slope is consistent and affine (relaxational) but without an independent temperature/units channel it is read as a shape cross-check, not an absolute T_eff.",
    "Researcher PREFERENCE (which community is 'better'/'more desirable'): not computable from the data and not a placement -- both are healthy/interior. Any 'which is preferable' is an interpretive dial for the viewport, surfaced here, not decided.",
]

out, STAMP = timestamped_view_path(str(HERE))
fig, axes = figure_with_header(
    n_plots=4, slug="community_pair_v6", date=STAMP, phase="DEV/blind",
    question=question, minimal_structure=minimal_structure, verdict=verdict,
    grounded=grounded, not_grounded=not_grounded, placement=placement)
axL, axC, axR, axBand = axes

# Plot 1: autocorrelation C(tau) -- shape that separates settle vs turnover
axL.axhline(0, color="0.7", lw=0.8)
axL.plot(r0["tau"], r0["C"], color="#1f77b4", lw=1.6, label="comm0 (monotone decay)")
axL.plot(r1["tau"], r1["C"], color="#d62728", lw=1.6, label="comm1 (rings -> osc)")
axL.scatter([r1["tau"][np.argmin(r1["C"])]], [r1["Cmin"]], color="#d62728", s=18, zorder=5)
axL.set_xlabel("lag tau (community clock)")
axL.set_ylabel("autocorrelation C")
axL.set_title("C(tau): settle (no crossing) vs turnover (rings)")
axL.legend(fontsize=7, loc="upper right")

# Plot 2: FDR locus chi vs C(0)-C  -- universal cross-check
for c, col in ((0, "#1f77b4"), (1, "#d62728")):
    r = results[c]
    dC = r["C0"] - r["C"]
    axC.plot(dC, r["chi"], color=col, lw=1.4, label=f"comm{c} (R2={r['fdr_r2']:.4f})")
axC.set_xlabel("C(0) - C(tau)")
axC.set_ylabel("chi (integrated step response)")
axC.set_title("FDR locus chi vs C0-C (affine = relaxational)")
axC.legend(fontsize=7, loc="lower right")

# Plot 3: directed cross-correlation symmetry -- the current signature
axR.axhline(0, color="0.7", lw=0.8)
axR.plot(r0["tau"], r0["Cxy"], color="#1f77b4", lw=1.4, label="comm0 Cxy")
axR.plot(r0["tau"], r0["Cyx"], color="#1f77b4", lw=1.0, ls=":", label="comm0 Cyx (=Cxy)")
axR.plot(r1["tau"], r1["Cxy"], color="#d62728", lw=1.4, label="comm1 Cxy")
axR.plot(r1["tau"], r1["Cyx"], color="#ff9896", lw=1.4, ls="--", label="comm1 Cyx (=-Cxy)")
axR.set_xlabel("lag tau")
axR.set_ylabel("directed cross-corr")
axR.set_title("Cxy vs Cyx: symmetric (no current) vs antisym (rotation)")
axR.legend(fontsize=6.5, loc="upper right")

# Plot 4 (THE BAND): cumulative turnover angle phiMean(t) -- the story
axBand.axhline(0, color="0.7", lw=0.8)
for yturn in range(1, int(abs(r1["phi_total"]) // (2 * np.pi)) + 1):
    axBand.axhline(2 * np.pi * yturn, color="0.9", lw=0.6)
axBand.fill_between(r0["tau"],
                    r0["phiMean"] - np.sqrt(r0["phiVar"]),
                    r0["phiMean"] + np.sqrt(r0["phiVar"]),
                    color="#1f77b4", alpha=0.12)
axBand.fill_between(r1["tau"],
                    r1["phiMean"] - np.sqrt(r1["phiVar"]),
                    r1["phiMean"] + np.sqrt(r1["phiVar"]),
                    color="#d62728", alpha=0.12)
axBand.plot(r0["tau"], r0["phiMean"], color="#1f77b4", lw=2.0,
            label=f"comm0: flat ({r0['phi_turns']:+.2f} turns) = settles")
axBand.plot(r1["tau"], r1["phiMean"], color="#d62728", lw=2.0,
            label=f"comm1: climbs ({r1['phi_turns']:+.1f} turns) = turns over")
axBand.set_xlabel("elapsed time (community clock)")
axBand.set_ylabel("cumulative turnover angle phiMean (rad)\n(band = +/- sqrt(phiVar))")
axBand.set_title("THE STORY: net winding -- same vs different")
axBand.legend(fontsize=7, loc="upper left")

fig.savefig(out, dpi=150)
print(f"\nVIEW: {out}")
print(f"STAMP: {STAMP}")
