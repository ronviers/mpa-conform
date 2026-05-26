"""freeze — queue_load_sweep_v12  (bespoke, one substrate, brittle by design)

The Cat-9 (Queueing) closing, REFRAMED. mm1_queue is the corpus's flagship self-named
falsifier, but its named test is a CATEGORY ERROR (mpa-central/FALSIFICATION.md FINDING 3):
the README equates "alpha_s (the FDR effective-temperature slope, in the chi-vs-C plane)"
with "the heavy-traffic exponent 1/2 (the reflected-Brownian-motion / Hurst time-scaling, in
the C-vs-lag plane)." These are DIFFERENT objects in DIFFERENT planes:
  - 1/2 governs how FAST C(tau) decays — the queue relaxation time ~ (1-rho)^-2 (C-vs-lag plane).
  - alpha_s is the FDR slope chi vs C — the effective-temperature / FDT-violation read (chi-vs-C plane).
Testing "alpha_s != 1/2 -> BROKE" measures the wrong plane. AND the raw library cells are
window-limited: at rho->1 the relaxation ~(1-rho)^-2 outruns the sampling window (at rho=0.999
C decorrelates only ~3.5%), so the slope is unresolvable off the raw cells — a blind read there
would not isolate conform. So this vertical does what v8 did for ising_equilibrium: BUILD A
CLEAN ORACLE where the truth is blind-readable, and pose the REFRAME.

THE PHYSICS (the honest sealed answer — REVERSIBLE CRITICAL SLOWING, X=1):
M/M/1 is a reversible birth-death process (detailed balance holds for every 1D birth-death
chain) -> the equilibrium fluctuation-dissipation theorem holds -> X = T/T_eff = 1 EXACTLY, at
every utilization rho, including rho->1. (FALSIFICATION FINDING 3: "M/M/1 reversibility forces
X=1.") What DIVERGES as the load rho approaches the capacity wall rho=1 is the relaxation TIME
and the fluctuation SIZE — not the FDT class:
  - relaxation rate (the exact M/M/1 spectral gap):  lambda(rho) = mu * (1 - sqrt(rho))^2
        -> relaxation time 1/lambda ~ (1-rho)^-2 as rho->1 (the heavy-traffic 1/2 scaling lives HERE).
  - stationary queue-length variance:  Var(rho) = rho / (1-rho)^2   -> diverges (fluctuations grow).
  - mean queue length:  <n> = rho/(1-rho)                            -> diverges.
So as rho->1 the queue gets SLUGGISH (long relaxation) and WILDLY VARIABLE (large fluctuations)
— the trap is reading this as glassy AGING (X<1) or testing the mis-specified alpha_s=1/2. The
correct read: REVERSIBLE CRITICAL SLOWING (X=1, FDR locus a single straight line of slope 1
through the origin at every rho), approaching the rho=1 CAPACITY asymptote. The 1/2 heavy-traffic
exponent is the C-decay-TIME scaling vs (1-rho), NOT the FDR slope.

THE ORACLE (the v8 equilibrium-criticality pattern, on the queueing substrate): per load rho the
queue-length fluctuation correlator is a single reversible relaxational mode,
  C(tau)   = Var(rho) * exp(-lambda(rho) * tau)          # C(0) = Var(rho) (fluctuation size grows)
  chi(tau) = Var(rho) * (1 - exp(-lambda(rho) * tau))    # equilibrium FDT, T=1 -> X=1
so the FDR locus chi vs (C(0)-C(tau)) is the IDENTITY line (slope 1, R^2=1, through the origin)
at EVERY rho — reversible, X=1 by construction (the construction encodes the M/M/1 reversibility
theorem; it does not impose a free parameter). The band: relaxation time 1/lambda and variance
Var BOTH diverge toward rho=1 (critical slowing + growing fluctuations), while the FDR slope
stays pinned at 1 (reversible, NOT aging). This CLOSES the mis-specified falsifier with the
FINDING-3 reframe, and is the QUEUEING counterpart to v8's thermodynamic-criticality X=1.

STRUCTURAL TENSION (logged, NOT adjudicated here — a framework/cdv1 matter, not a conform call):
cdv1 Load-handling maps heavy-traffic M/M/1 (chit = -ln rho -> 0+) into the s-regime, whose FDR
signature is aging (X<1). But M/M/1 reversibility forces X=1. So either that mapping over-claims,
or s admits X=1 critical slowing. This conform pass establishes the substrate truth (X=1
reversible critical slowing); the cdv1 reconciliation is parked to FALSIFICATION (the sharp
version was the ising_equilibrium test, closed by v8). NOT in scope for the blind pass.

WHY AN ORACLE (not the library mm1_queue cells): window-limited near rho->1 (FINDING 3) — the
slope is unresolvable, so a blind read off the raw cells would not isolate conform. The oracle
encodes the exact M/M/1 spectral gap (1-sqrt(rho))^2 and variance rho/(1-rho)^2 and the
reversibility X=1 directly, with the window set per-rho (~12/lambda) so the relaxation sheds and
the FDR slope is blind-readable. (A real single-server queue under load is the external physics
this idealizes.)

ANCHOR: FIRST CONTACT on this oracle — no prior earned mm1 operating point. Conceptual kinship to
v8 (same X=1 reversible critical-slowing reading; different substrate). No hard anchor.

BLINDING: the emitted CSV carries ONLY (level, util_rel, tau, C, chi). util_rel is the
researcher's OWN load knob — the relative traffic intensity they dialed, normalized to a baseline
run (level 0 = 1.0x... actually level-mid; see below). It carries NO rho, mu, lambda, Var, the
spectral gap, the FDR slope, the 1/2 exponent, or any framework token. A queueing researcher who
dials the load and measures queue-length fluctuation autocorrelation + response yields exactly
these curves. The level index is a neutral 0..4 (light load -> near capacity); native utilization
withheld (v7/v8/v9: absolute distance-in-native-units is not blind-closeable).

Run:  python H:/mpa-conform/blockin/questions/queue_load_sweep_v12/freeze_mm1_critical_slowing.py

Emits: data/queue_load_sweep_v12.frozen.csv  (level,util_rel,tau,C,chi — the blind artifact)
       prints the SEALED ground truth (per-level rho, lambda, relaxation time, Var, FDR slope; the
       diverging-timescale + diverging-variance band at fixed X=1) for the author/human. CSV none.
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
OUT = HERE / "data" / "queue_load_sweep_v12.frozen.csv"

# ----- oracle parameters (the SEAL; none of this reaches the CSV) -----------------
# ONE single-server queue, FIVE loads (utilizations) climbing toward the capacity wall rho=1.
MU       = 1.0                                  # service rate (sets the clock)
RHO      = np.array([0.60, 0.80, 0.90, 0.95, 0.98])   # utilization (level 0..4 -> toward saturation)
BASE_IDX = 0                                    # level 0 = the baseline load (util_rel = 1.0x)
N_TAU    = 40                                   # log-spaced lags per level
WIN_MULT = 12.0                                 # window out to ~12/lambda so C sheds (FDR slope readable)


def lam_of(rho):      # exact M/M/1 spectral gap (relaxation rate)
    return MU * (1.0 - np.sqrt(rho)) ** 2


def var_of(rho):      # exact M/M/1 stationary queue-length variance
    return rho / (1.0 - rho) ** 2


def mean_of(rho):     # exact M/M/1 mean queue length
    return rho / (1.0 - rho)


def C_chi(tau, rho):
    lam = lam_of(rho)
    var = var_of(rho)
    C = var * np.exp(-lam * tau)                  # C(0) = Var (fluctuation size)
    chi = var * (1.0 - np.exp(-lam * tau))        # equilibrium FDT, T=1 -> X=1
    return C, chi


def fdr_slope(C, chi):
    """Slope of chi vs (C(0)-C(tau)) through the origin. = 1 exactly for the reversible
    construction (X=1). Computed here, not via conform — the answer-key is X=1."""
    drop = C[0] - C
    # least-squares slope through origin
    m = float(np.dot(drop, chi) / np.dot(drop, drop))
    pred = m * drop
    ss = float(np.sum((chi - pred) ** 2) / max(np.sum((chi - chi.mean()) ** 2), 1e-30))
    return m, 1.0 - ss


def materialize():
    lines, per = [], []
    base = float(RHO[BASE_IDX])
    util_base = base / (1.0 - base)               # use offered-load-ish knob: rho/(1-rho) ratio
    for lvl, rho in enumerate(RHO):
        rho = float(rho)
        lam = lam_of(rho)
        tau_max = WIN_MULT / lam
        taus = np.concatenate(([0.0], np.geomspace(tau_max / 800.0, tau_max, N_TAU - 1)))
        C, chi = C_chi(taus, rho)
        # researcher's relative load knob: ratio of offered load to baseline (monotone in rho, neutral)
        util_rel = (rho / (1.0 - rho)) / util_base
        per.append(dict(level=lvl, rho=rho, lam=lam, tau_relax=1.0 / lam, var=var_of(rho),
                        mean=mean_of(rho), util_rel=util_rel, C=C, chi=chi, taus=taus))
        for t, c, x in zip(taus, C, chi):
            lines.append(f"{lvl},{util_rel:.6g},{t:.6g},{c:.8g},{x:.8g}")
    return lines, per


def main():
    lines, per = materialize()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# queue_load_sweep_v12 -- BLIND artifact (provenance below stripped by pose.py).\n"
        "# One single-server queue at FIVE loads (level 0..4, light load -> near capacity).\n"
        "# tau is the queue's own clock (a lag). Columns: level, util_rel (relative offered\n"
        "# load, normalized to the baseline level 0 = 1.0x), tau, C (queue-length fluctuation\n"
        "# autocorrelation), chi (integrated response to a small steady load bump). No utilization\n"
        "# values, no rates, no model parameters. Each load has its own settling window, so tau\n"
        "# ranges differ (the heavily-loaded settings relax far more slowly).\n"
        "level,util_rel,tau,C,chi\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    print("SEALED ground truth (NONE of this is in the CSV):")
    print(f"  substrate: M/M/1 single-server queue, mu={MU}; SWEEP over load rho -> capacity wall rho=1")
    print(f"  reversible birth-death -> equilibrium FDT -> X=1 EXACTLY at every rho (FINDING 3 reframe)")
    print(f"  {'lvl':>3} {'rho':>5} {'util_rel':>8} {'lambda':>9} {'tau_relax':>10} {'<n>':>7} "
          f"{'Var':>9} {'FDR slope':>9} {'R2':>6} {'X':>4}")
    for L in per:
        m, r2 = fdr_slope(L["C"], L["chi"])
        print(f"  {L['level']:>3} {L['rho']:>5.2f} {L['util_rel']:>8.2f} {L['lam']:>9.5f} "
              f"{L['tau_relax']:>10.1f} {L['mean']:>7.1f} {L['var']:>9.1f} {m:>9.4f} {r2:>6.3f} {1.0:>4.1f}")
    tau_band = [float(round(L["tau_relax"], 1)) for L in per]
    var_band = [float(round(L["var"], 1)) for L in per]
    util_band = [float(round(L["util_rel"], 2)) for L in per]
    print(f"  util_rel band:    {util_band}  (relative offered load, the swept axis)")
    print(f"  relaxation time:  {tau_band}  -> DIVERGES toward capacity ~ (1-rho)^-2 (CRITICAL SLOWING;")
    print(f"                     the heavy-traffic 1/2 exponent lives in THIS C-decay scaling, not the FDR slope)")
    print(f"  variance Var:     {var_band}  -> DIVERGES ~ (1-rho)^-2 (fluctuations grow toward the wall)")
    print(f"  FDR slope:        ALL = 1.000 (R2=1.000) -> X=1 at every load (REVERSIBLE critical slowing,")
    print(f"                     NOT glassy aging X<1; the FDR locus is a single straight line thru origin)")
    print(f"  THE READ: pushing the load toward capacity makes the queue SLUGGISH (relaxation time")
    print(f"      diverges) and WILDLY VARIABLE (variance diverges) — but it stays IN BALANCE (X=1,")
    print(f"      response matches fluctuations): reversible critical slowing toward the rho=1 capacity")
    print(f"      wall, NOT a stuck/aging regime. The 1/2 heavy-traffic exponent is the relaxation-TIME")
    print(f"      scaling (C-decay plane), a DIFFERENT plane from the FDR slope (=1) — closing FINDING 3.")

    # self-consistency assertions (author-side)
    for L in per:
        m, r2 = fdr_slope(L["C"], L["chi"])
        assert abs(m - 1.0) < 1e-6, f"FDR slope must be 1 (X=1) at rho={L['rho']}; got {m}"
        assert r2 > 1.0 - 1e-9, "FDR locus must be an exact straight line through origin"
        assert np.all(np.isfinite(L["C"])) and np.all(np.isfinite(L["chi"])), "no NaN"
    taus_relax = np.array([L["tau_relax"] for L in per])
    vars_ = np.array([L["var"] for L in per])
    assert np.all(np.diff(taus_relax) > 0), "relaxation time must diverge monotonically toward capacity"
    assert np.all(np.diff(vars_) > 0), "variance must diverge monotonically toward capacity"
    # check the (1-rho)^-2 heavy-traffic scaling of the relaxation time (the 1/2 exponent's plane)
    one_minus_rho = 1.0 - RHO
    # tau_relax ~ (1-rho)^-2 only asymptotically; check the exact gap formula instead:
    for L in per:
        assert abs(L["lam"] - MU * (1.0 - np.sqrt(L["rho"])) ** 2) < 1e-12, "exact M/M/1 spectral gap"
    print("\nself-consistent: FDR slope=1 / R2=1 (X=1) at every load + relaxation time & variance "
          "diverge toward capacity + exact M/M/1 spectral gap + no NaN. OK.")
    print(f"wrote {OUT}  ({len(lines)} rows, {len(RHO)} levels)")


if __name__ == "__main__":
    main()
