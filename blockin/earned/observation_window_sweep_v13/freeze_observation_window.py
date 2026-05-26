"""freeze — observation_window_sweep_v13  (bespoke, one substrate, brittle by design)
   *** CORRECTED v2 (2026-05-26): independent-response Monte Carlo. ***

The Cat-5 (Kernel / camera / tau_obs) landing. Cat 5 is the kernel pre-gate's own job
(WORKFLOW S.E; RFC-S S.0.2: tau_obs IS the camera): is an apparent character a property of the
SUBSTRATE or of the OBSERVATION WINDOW? The swept axis is the CAMERA (tau_obs), not a substrate
knob, across 32 windows. The substrate is one fixed two-timescale EQUILIBRIUM signal; at short
windows the slow mode hasn't decayed -> an apparent frozen plateau that mimics a glass q_EA; as
the window opens the plateau MELTS to full relaxation. The two teeth that separate a Cat-5 camera
artifact from a Cat-8 intrinsic glass: (1) the plateau MELTS with the window (a real glass q_EA
would not), and (2) the FDR locus is slope 1 (X=1, equilibrium) at every window (a glass is X<1).

*** WHY THIS WAS REBUILT (the imposed-FDT flaw, caught by Ron 2026-05-26). ***
The first v13 oracle set the response ANALYTICALLY as chi(tau) = C(0) - C(tau) -- i.e. it IMPOSED
the equilibrium FDT relation. That made chi the algebraic mirror of C, so the FDR locus chi vs
(C0-C) was the IDENTITY line by construction: the "X=1 / FDT holds" reading was TAUTOLOGICAL, not
a tested fact. It violated data-path independence (WORKFLOW S.1: "the sim makes the data, analytics
makes the truth; conform is the examinee, never the answer key"). The tell: in real data C (a
fluctuation measurement) and chi (a perturbation/response measurement) are TWO SEPARATE
experiments that satisfy FDT only emergently/approximately -- they cannot be exact mirrors.

THE FIX (data-path independence restored): C and chi are now TWO INDEPENDENT Monte-Carlo
measurements of the SAME equilibrium substrate:
  - substrate: two independent Ornstein-Uhlenbeck modes at ONE temperature T=1,
        x_f: tau_f=1  (fast),  stationary var_f = T*tau_f = 1
        x_s: tau_s=1000 (slow), stationary var_s = T*tau_s = 1000
    observed via y = c_f*x_f + c_s*x_s, with c_f=sqrt(a_f/var_f), c_s=sqrt(a_s/var_s) so that the
    weights come out a_f=0.4, a_s=0.6 (decoupled from the timescales). Then by construction the
    TRUE autocorrelation is C_y(tau) = 0.4*exp(-tau/1) + 0.6*exp(-tau/1000), C_y(0)=1.
  - C is MEASURED from a FLUCTUATION ensemble (seed A): C(tau) = <y(0) y(tau)> over n_real
    realizations started at stationarity. (MC noise ~ 1/sqrt(n_real).)
  - chi is MEASURED from a SEPARATE PERTURBATION ensemble (seed B): a small step field h conjugate
    to y is switched on at t=0, and chi(tau) = <y(tau)>/h (the integrated step response). (OU is
    linear, so the response is exactly linear for any h -> h=1 is fine; MC noise ~ 1/sqrt(n_real).)
  - The equilibrium FDT (chi = (C0-C)/T, hence X=1) therefore EMERGES: the two independent MC
    measurements agree to within MC noise (a few %), they are NOT identical. The blind answerer
    reading slope ~ 1 is reading a genuine emergent FDT, not an imposed identity.
Exact OU stepping is used (x(t+dt)=mu+(x-mu)e^{-dt/tau}+sqrt(var(1-e^{-2dt/tau})) eta), so a single
exact jump spans each lag increment -> O(n_lags) steps, no discretization error, fast.

THE CAMERA: tau_obs = the observation-window length (max lag), swept across 32 levels log-spaced
from 3 to 30000. Sampling is fixed-fine (min lag << tau_f). Physically one master process is
measured; window-level k reports C, chi at lags <= tau_obs_k (a longer measurement of the same
process contains the shorter -- the camera truncates). The slow mode is FROZEN (under-resolved) at
short tau_obs and fully resolved at long tau_obs -- in BOTH C and chi independently.

INVARIANT (must NOT migrate): the intrinsic tau_f, tau_s, a_s, and the equilibrium character (X=1).
MIGRATES: only the apparent non-ergodicity plateau q(tau_obs). FOIL to v4 (kww glass): there the
plateau is intrinsic q_EA with X<1 and does NOT melt; here it is a camera artifact with X=1 (now
emergent, not imposed) and melts.

BLINDING: the emitted CSV carries ONLY (level, window_rel, tau, C, chi). No tau_f/tau_s/a_s, no
tau_obs, no T/h, no X, no framework token. A researcher who measures one signal's autocorrelation
+ step-response over 32 observation durations yields exactly these (noisy) curves.

Run:  python H:/mpa-conform/blockin/questions/observation_window_sweep_v13/freeze_observation_window.py
Emits: data/observation_window_sweep_v13.frozen.csv  + prints the SEALED ground truth (the melt
       band; the EMERGENT FDR slope ~1 with its MC scatter; the C-vs-chi independence check). CSV none.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "observation_window_sweep_v13.frozen.csv"

# ----- the FIXED substrate (the SEAL; none reaches the CSV) -----------------------
TAU_F, TAU_S = 1.0, 1000.0      # fast / slow intrinsic times (3 decades)
A_F, A_S     = 0.40, 0.60       # weights in y (decoupled from timescales via c_f, c_s); C(0)=1
T            = 1.0              # single equilibrium temperature -> FDT holds, X=1
VAR_F, VAR_S = T * TAU_F, T * TAU_S        # OU stationary variances (= T*tau)
C_F, C_S     = np.sqrt(A_F / VAR_F), np.sqrt(A_S / VAR_S)   # observable coefficients
H_FIELD      = 1.0              # step-field amplitude (OU linear -> any h is exact-linear)
N_REAL       = 8000            # realizations per ensemble (MC noise ~ 1/sqrt(N) ~ 1.1%)
SEED_C, SEED_CHI = 13, 1300     # INDEPENDENT seeds: C ensemble vs chi ensemble

# ----- the CAMERA: 32 observation windows log-spaced 3 .. 30000 -------------------
N_LEVELS = 32
TAU_OBS  = np.geomspace(3.0, 30000.0, N_LEVELS)
MIN_LAG  = 0.05
N_TAU    = 40                   # lags emitted per window
N_MASTER = 260                  # master lag grid resolution


def C_true(tau):
    return A_F * np.exp(-tau / TAU_F) + A_S * np.exp(-tau / TAU_S)


def measure_C(master_lags, rng):
    """C(tau) = <y(0) y(tau)> from a FLUCTUATION ensemble started at stationarity (exact OU)."""
    xf = rng.standard_normal(N_REAL) * np.sqrt(VAR_F)
    xs = rng.standard_normal(N_REAL) * np.sqrt(VAR_S)
    y0 = C_F * xf + C_S * xs
    C = np.empty_like(master_lags)
    C[0] = float(np.mean(y0 * y0))
    for k in range(1, len(master_lags)):
        d = master_lags[k] - master_lags[k - 1]
        af, as_ = np.exp(-d / TAU_F), np.exp(-d / TAU_S)
        xf = xf * af + rng.standard_normal(N_REAL) * np.sqrt(VAR_F * (1 - af * af))
        xs = xs * as_ + rng.standard_normal(N_REAL) * np.sqrt(VAR_S * (1 - as_ * as_))
        y = C_F * xf + C_S * xs
        C[k] = float(np.mean(y0 * y))
    return C


def measure_chi(master_lags, rng):
    """chi(tau) = <y(tau)>/h from a SEPARATE PERTURBATION ensemble: zero-mean stationary start, a
    step field h conjugate to y switched on at t=0 (force h*c_f on x_f, h*c_s on x_s). Exact OU
    relaxation toward the field-shifted mean mu = (force)*tau. INDEPENDENT of measure_C (own seed,
    a response experiment not a fluctuation one) -> FDT is emergent, not imposed."""
    xf = rng.standard_normal(N_REAL) * np.sqrt(VAR_F)
    xs = rng.standard_normal(N_REAL) * np.sqrt(VAR_S)
    mu_f = H_FIELD * C_F * TAU_F          # steady-state mean of x_f under the field
    mu_s = H_FIELD * C_S * TAU_S
    chi = np.empty_like(master_lags)
    chi[0] = float(np.mean(C_F * xf + C_S * xs)) / H_FIELD     # ~0 (zero-mean start)
    for k in range(1, len(master_lags)):
        d = master_lags[k] - master_lags[k - 1]
        af, as_ = np.exp(-d / TAU_F), np.exp(-d / TAU_S)
        xf = mu_f + (xf - mu_f) * af + rng.standard_normal(N_REAL) * np.sqrt(VAR_F * (1 - af * af))
        xs = mu_s + (xs - mu_s) * as_ + rng.standard_normal(N_REAL) * np.sqrt(VAR_S * (1 - as_ * as_))
        chi[k] = float(np.mean(C_F * xf + C_S * xs)) / H_FIELD
    return chi


def fdr_slope(C, chi):
    drop = C[0] - C
    if np.dot(drop, drop) < 1e-12:
        return float("nan"), float("nan")
    m = float(np.dot(drop, chi) / np.dot(drop, drop))
    pred = m * drop
    r2 = 1.0 - float(np.sum((chi - pred) ** 2) / max(np.sum((chi - chi.mean()) ** 2), 1e-30))
    return m, r2


def main():
    master = np.concatenate(([0.0], np.geomspace(MIN_LAG, 30000.0, N_MASTER - 1)))
    C_master = measure_C(master, np.random.default_rng(SEED_C))
    chi_master = measure_chi(master, np.random.default_rng(SEED_CHI))

    lines, per = [], []
    win_base = float(TAU_OBS[0])
    for lvl, tobs in enumerate(TAU_OBS):
        tobs = float(tobs)
        taus = np.concatenate(([0.0], np.geomspace(MIN_LAG, tobs, N_TAU - 1)))
        C = np.interp(taus, master, C_master)
        chi = np.interp(taus, master, chi_master)
        window_rel = tobs / win_base
        per.append(dict(level=lvl, tau_obs=tobs, window_rel=window_rel, taus=taus, C=C, chi=chi))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{window_rel:.6g},{t:.6g},{c:.8g},{x:.8g}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# observation_window_sweep_v13 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# ONE fluctuating signal, measured at 32 observation-window lengths (level 0 shortest watch\n"
        "# -> level 31 longest). tau is the signal's own clock (a lag). Columns: level, window_rel\n"
        "# (relative observation-window length, normalized to the shortest run = 1.0x), tau, C\n"
        "# (autocorrelation), chi (integrated step-response). Both C and chi are MEASURED (noisy);\n"
        "# they are SEPARATE measurements. No times, no model parameters. Sampling fixed-fine; only\n"
        "# the observation DURATION (max lag) differs across levels.\n"
        "level,window_rel,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    # ---- independence + emergent-FDT diagnostics (master grid) ----
    fdt_resid = chi_master - (C_master[0] - C_master)      # 0 only if FDT imposed; here ~ MC noise
    resid_max = float(np.max(np.abs(fdt_resid)))
    resid_rms = float(np.sqrt(np.mean(fdt_resid ** 2)))
    slope_all, r2_all = fdr_slope(C_master, chi_master)

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  FIXED substrate (two-mode OU, ONE temperature T={T}): tau_f={TAU_F}, tau_s={TAU_S}, "
          f"a_f={A_F}, a_s={A_S}; C and chi are INDEPENDENT Monte-Carlo measurements (n_real={N_REAL}).")
    print(f"  *** FDT is EMERGENT, not imposed: chi (response ensemble) vs C0-C (fluctuation ensemble)")
    print(f"      differ by MC noise -- max|chi-(C0-C)|={resid_max:.4f}, rms={resid_rms:.4f} (NONZERO ->")
    print(f"      they are genuinely separate measurements; if this were 0, FDT was typed in). ***")
    print(f"  whole-curve FDR slope (chi vs C0-C, master grid): {slope_all:.4f}  R2={r2_all:.4f}  -> ~1 (X=1, emergent)")
    print(f"  {len(per)} windows, tau_obs log-spaced {TAU_OBS[0]:.2f} .. {TAU_OBS[-1]:.0f}. Sample rows:")
    print(f"  {'lvl':>3} {'tau_obs':>9} {'window_rel':>10} {'app. plateau q':>14} {'FDR slope':>9} {'R2':>6} {'slow mode':>18}")
    qs, slopes = [], []
    for L in per:
        m, r2 = fdr_slope(L["C"], L["chi"])
        q_app = float(L["C"][-1])
        qs.append(q_app); slopes.append(m)
    for i, L in enumerate(per):
        if i % 4 != 0 and i != len(per) - 1:
            continue
        q_app = qs[i]
        res = "frozen (under-res)" if q_app > 0.5 * A_S else ("melting" if q_app > 0.05 else "fully resolved")
        print(f"  {L['level']:>3} {L['tau_obs']:>9.1f} {L['window_rel']:>10.1f} {q_app:>14.4f} "
              f"{slopes[i]:>9.4f} {r2_all if np.isnan(slopes[i]) else fdr_slope(L['C'],L['chi'])[1]:>6.3f} {res:>18}")
    print(f"  apparent-plateau band q [{len(qs)} levels]: first {round(qs[0],3)} ... mid {round(qs[len(qs)//2],3)} "
          f"... last {round(qs[-1],3)}; melts ~a_s={A_S} -> 0 monotonically (modulo MC noise)")
    sl = np.array([s for s in slopes if np.isfinite(s)])
    print(f"  per-window FDR slope: mean {sl.mean():.4f}, range {sl.min():.4f}..{sl.max():.4f} -> ~1 (X=1) EMERGENT")
    print(f"  THE READ: apparent frozen plateau = a CAMERA artifact (melts as the window opens), NOT")
    print(f"      intrinsic non-ergodicity. The signal is one fixed two-timescale EQUILIBRIUM relaxation")
    print(f"      (X=1 -- now an EMERGENT FDT from two independent MC measurements, not an imposed identity).")

    # self-consistency assertions
    assert resid_max > 0.003, f"chi must DIFFER from C0-C (independence); got max resid {resid_max} (FDT imposed?)"
    assert resid_max < 0.10, f"chi-(C0-C) too large ({resid_max}); FDT should emerge within MC noise"
    assert 0.9 < sl.mean() < 1.1, f"emergent FDR slope must be ~1 (X=1); got {sl.mean()}"
    assert qs[0] > 0.45 and qs[-1] < 0.05, "apparent plateau must be frozen at short window and melt at long"
    # melt is monotone modulo MC noise:
    assert qs[0] - qs[-1] > 0.4, "plateau must melt substantially across the window sweep"
    assert np.all(np.isfinite(C_master)) and np.all(np.isfinite(chi_master)), "no NaN"
    print("\nself-consistent: C & chi INDEPENDENT MC (resid nonzero, <10%) + emergent FDR slope ~1 + "
          "plateau melts + no NaN. OK.")
    print(f"wrote {OUT}  ({len(lines)} rows, {N_LEVELS} levels)")


if __name__ == "__main__":
    main()
