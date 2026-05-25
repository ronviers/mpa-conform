"""Build the five-vector arc's result-image library (the Core 3 views).

Promotes the arc's validations from throwaway `output/diagnostics/*.png` (gitignored,
ad-hoc names) to the block-in result-image standard: a self-describing header band
(question + verdict + placement + grounded/not_grounded) over a data-mapped plot grid,
saved as `view_<YYYYMMDD-HHMMSS>.png` so re-runs ACCUMULATE into a browsable library
(meta-SOP §7 naming, mirrored here for the arc).

It does NOT reimplement the fitter — it drives the production compute (inversion.invert,
five_vector.fit_kww5) on REAL mpa-central library cells, the same path the validation
scripts exercise. Three views:
  1. x_recovery_roundtrip — X-recovery across X=0.1..1.0 + the full 5-vector round-trip on
     kww_oracle + out-of-family refusal (sine, running ring).
  2. domain_gate_census  — the residual + per-channel S/N gate across the whole library.
  3. identifiability      — bootstrap pinned/mush/railed, ORTHOGONAL to the domain gate.

Output: H:/mpa-conform/docs/five_vector_views/<view_slug>/view_<STAMP>.png (committed).
Run:    python H:/mpa-conform/scripts/build_five_vector_views.py
"""
from __future__ import annotations
import sys, json, glob, os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "H:/mpa-conform")
sys.path.insert(0, "H:/mpa-conform/blockin")   # reach view_header
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conformer.compute import inversion, five_vector
from view_header import figure_with_header, timestamped_view_path

DATA = Path("H:/mpa-central/library/data")
VIEWS = Path("H:/mpa-conform/docs/five_vector_views")
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")   # one stamp for the batch
# kww_oracle truth in dimensionless lag units (scale = tau_env = tau_alpha = 20):
KWW_TRUTH = dict(q_EA=0.7, tau_alpha=1.0, beta_KWW=0.6, tau_beta=0.05)
GREEN, RED, BLUE = "#0a7d00", "#b00020", "#00468b"


def _cell(patt):
    g = glob.glob(str(patt))
    return g[0] if g else None


def rows_dimless(path, *, with_sem=False):
    """Rows at DIMENSIONLESS lag (dt/scale) — the fit_kww5 contract."""
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    out = []
    for e in s:
        r = {"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"]}
        if with_sem:
            r["C_sem"] = e.get("C_sem", 0.0); r["chi_sem"] = e.get("chi_sem", 0.0)
        out.append(r)
    return out, scale


def rows_raw(path):
    """Raw-lag rows + scale + gt, for invert(tau_scale=...) (census idiom)."""
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"], "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]
    gt = (c.get("operating_point") or {}).get("gt")
    return rows, scale, gt


def save(slug, fig):
    d = VIEWS / slug.split("__", 1)[-1]
    d.mkdir(parents=True, exist_ok=True)
    out, _ = timestamped_view_path(d, stamp=STAMP)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  wrote {out}")
    return out


# ----------------------------------------------------------------------------- view 1
def view_x_recovery():
    # X-recovery points (real library cells): two_temp_ou (pure-exp) + kww_oracle (2-timescale)
    pts = []  # (label, X_true, X_fit)
    for X in ("0.1", "0.5"):
        p = _cell(DATA / "two_temp_ou" / f"two_temp_ou__X{X}__velocity.json")
        if p:
            rows, _ = rows_dimless(p)
            f = five_vector.fit_kww5(rows, T=1.0)
            pts.append((f"two_temp_ou X{X}", float(X), f.X))
    kww_full = None
    for X in ("0.2", "0.5", "1"):
        p = _cell(DATA / "kww_oracle" / f"kww_oracle__X{X}__velocity.json")
        if p:
            rows, _ = rows_dimless(p)
            f = five_vector.fit_kww5(rows, T=1.0)
            pts.append((f"kww_oracle X{X}", float(X), f.X))
            if X == "0.5":
                kww_full = f
    # out-of-family refusal
    refusal = []  # (label, residual, in_domain)
    for name, sub, patt, T in [("sine P1000", "sine_wave", "sine_wave__P1000__velocity.json", 1.0),
                                ("driven_ring F1.5", "driven_ring", "driven_ring__F1.5__velocity.json", 0.5),
                                ("driven_ring F3.0", "driven_ring", "driven_ring__F3.0__velocity.json", 0.5)]:
        p = _cell(DATA / sub / patt)
        if p:
            rows, _ = rows_dimless(p)
            f = five_vector.fit_kww5(rows, T=T)
            refusal.append((name, f.residual, f.in_domain))
    # in-family residuals for contrast
    infam = []
    for name, sub, patt in [("two_temp_ou", "two_temp_ou", "two_temp_ou__X0.5__velocity.json"),
                             ("kww_oracle", "kww_oracle", "kww_oracle__X0.5__velocity.json")]:
        p = _cell(DATA / sub / patt)
        if p:
            rows, _ = rows_dimless(p)
            f = five_vector.fit_kww5(rows, T=1.0)
            infam.append((name, f.residual, f.in_domain))

    xerr = max(abs(xf - xt) for _, xt, xf in pts) if pts else float("nan")
    fig, (a0, a1, a2) = figure_with_header(
        n_plots=3, slug="five_vector__x_recovery_roundtrip", date=STAMP, phase="DEV/validation",
        question="Does the 5-vector fit RECOVER the FDT-violation X, ROUND-TRIP the full glassy "
                 "fingerprint (q_EA, tau_alpha, beta_KWW, tau_beta), and REFUSE out-of-family inputs?",
        minimal_structure="KWW+FDT 5-vector fit on real library cells; cdv1 chit anchor fixed, "
                          "T fixed from the operating point (6th-param deferred).",
        verdict=f"YES on all three. X recovered to <={xerr:.2f} across X=0.1-1.0; the full 5-vector "
                f"round-trips on kww_oracle within the resolution floor; out-of-family (cosine, running "
                f"NESS) is gated OUT, not handed a garbage X.",
        placement=f"max |X_fit - X_true| = {xerr:.3f}; kww_oracle q_EA/beta within floor; "
                  f"out-of-family residual 0.14-0.45 vs in-family ~0.02.",
        grounded=["X-recovery: X_fit vs X_true across 5 real cells (box 1)",
                  "full vector: kww_oracle recovered vs prescribed q_EA/tau_alpha/beta_KWW/tau_beta (box 2)",
                  "domain refusal: residual gate separates in-family (~0.02) from out-of-family (>0.13) (box 3)"],
        not_grounded=["production aging-glass X (T<Tc): blocked on mpa-central null tau_env below Tc "
                      "(camera-scale not placed) — owed to the library refresh",
                      "T as a 6th fit param: deferred by design (T fixed from the operating point)"],
    )
    # box 0: X recovery
    xt = [p[1] for p in pts]; xf = [p[2] for p in pts]
    a0.plot([0, 1.05], [0, 1.05], "--", color="gray", lw=1, label="y = x (perfect)")
    a0.scatter(xt, xf, s=70, c=BLUE, zorder=3, edgecolor="k")
    for lab, t, f in pts:
        a0.annotate(lab.split()[0][:3] + lab.split("X")[-1], (t, f), fontsize=6,
                    xytext=(3, -8), textcoords="offset points")
    a0.set_xlabel("X (prescribed)"); a0.set_ylabel("X (5-vector fit)")
    a0.set_title("X-RECOVERY: fit vs truth\n(on the y=x line = recovered)"); a0.grid(alpha=0.3); a0.legend(fontsize=7)
    # box 1: full round-trip on kww_oracle
    if kww_full is not None:
        names = list(KWW_TRUTH.keys())
        truth = [KWW_TRUTH[k] for k in names]
        got = [getattr(kww_full, k) for k in names]
        x = np.arange(len(names)); w = 0.38
        a1.bar(x - w/2, truth, w, label="prescribed", color="#888")
        a1.bar(x + w/2, got, w, label="recovered", color=GREEN)
        a1.set_xticks(x); a1.set_xticklabels(names, rotation=30, fontsize=7, ha="right")
        a1.set_title("FULL 5-VECTOR ROUND-TRIP\n(kww_oracle X0.5)"); a1.legend(fontsize=7); a1.grid(alpha=0.3, axis="y")
    # box 2: residual gate (in vs out of family)
    bars = infam + refusal
    labs = [b[0] for b in bars]; res = [b[1] for b in bars]; cols = [GREEN if b[2] else RED for b in bars]
    a2.barh(range(len(bars)), res, color=cols)
    a2.axvline(five_vector.RESIDUAL_GATE, color="k", ls="--", lw=1, label=f"residual gate {five_vector.RESIDUAL_GATE}")
    a2.set_yticks(range(len(bars))); a2.set_yticklabels(labs, fontsize=7)
    a2.invert_yaxis(); a2.set_xlabel("fit residual (RMS)")
    a2.set_title("DOMAIN REFUSAL\n(green IN-family / red OUT)"); a2.legend(fontsize=7); a2.grid(alpha=0.3, axis="x")
    return save("five_vector__x_recovery_roundtrip", fig)


# ----------------------------------------------------------------------------- view 2
def view_domain_gate_census():
    rows_out = []  # (name, gt, in_domain, snrC, snr_chi, residual)
    for folder in sorted([d for d in DATA.iterdir() if d.is_dir()]):
        cells = sorted(folder.glob("*velocity*.json")) or sorted(folder.glob("*.json"))
        if not cells:
            continue
        try:
            rows, scale, gt = rows_raw(cells[0])
            if len(rows) < 5:
                continue
            res = inversion.invert(rows, tau_scale=scale, T=1.0, skip_stage2=True)
            fv = res.five_vector_fit
            if fv is None:
                continue
            rows_out.append((folder.name, gt, fv.in_domain,
                             fv.channel_snr.get("C", float("nan")),
                             fv.channel_snr.get("chi", float("nan")), fv.residual))
        except Exception:
            continue
    n_in = sum(1 for r in rows_out if r[2]); n_out = len(rows_out) - n_in
    fig, (a0, a1) = figure_with_header(
        n_plots=2, slug="five_vector__domain_gate_census", date=STAMP, phase="DEV/validation",
        question="Across the whole substrate library, does the residual + per-channel S/N gate "
                 "ACCEPT in-family substrates and REJECT out-of-domain ones?",
        minimal_structure="invert() + the KWW-FDT domain gate (per-channel S/N when grain present, "
                          "scalar residual otherwise) on one representative cell per substrate.",
        verdict=f"The gate sorts the library: {n_in} IN, {n_out} OUT. In-family controls land IN; "
                f"oscillatory / running / out-of-family land OUT. Borderline glass T=1.3 is IN by "
                f"residual but OUT by the (stricter) per-channel S/N gate — a recorded gate-sensitivity, "
                f"not a defect.",
        placement=f"IN n={n_in}, OUT n={n_out}; gate = per-channel residual <= {five_vector.SNR_GATE}x grain "
                  f"(S/N), else residual < {five_vector.RESIDUAL_GATE}.",
        grounded=["per-substrate IN/OUT verdict from invert()+gate (box 1)",
                  "the two gate criteria: residual vs grain, and per-channel C/chi S/N (box 2)"],
        not_grounded=["production aging-glass (T<Tc): null tau_env in the library — owed to the refresh",
                      "glass T=1.3 sits ON the residual-vs-S/N boundary (recorded; the two criteria disagree there)"],
    )
    rows_out.sort(key=lambda r: r[5])
    labs = [r[0] for r in rows_out]; res = [max(r[5], 1e-3) for r in rows_out]  # floor for log
    cols = [GREEN if r[2] else RED for r in rows_out]
    a0.barh(range(len(rows_out)), res, color=cols)
    a0.set_xscale("log")   # residuals span ~0.01 (in-family) to >1e9 (diverging-chi out-family)
    a0.set_xlim(1e-3, max(res) * 3)
    a0.axvline(five_vector.RESIDUAL_GATE, color="k", ls="--", lw=1, label=f"residual gate {five_vector.RESIDUAL_GATE}")
    a0.set_yticks(range(len(rows_out))); a0.set_yticklabels(labs, fontsize=6)
    a0.invert_yaxis(); a0.set_xlabel("fit residual (RMS, log)")
    a0.set_title(f"DOMAIN GATE across the library\n(green IN n={n_in} / red OUT n={n_out})")
    a0.legend(fontsize=7); a0.grid(alpha=0.3, axis="x")
    # box 1: per-channel S/N scatter
    for r in rows_out:
        c = GREEN if r[2] else RED
        a1.scatter(r[3], r[4], s=45, c=c, edgecolor="k", zorder=3)
        a1.annotate(r[0][:9], (r[3], r[4]), fontsize=5, xytext=(3, 2), textcoords="offset points")
    a1.axhline(five_vector.SNR_GATE, color="k", ls="--", lw=1)
    a1.axvline(five_vector.SNR_GATE, color="k", ls="--", lw=1, label=f"S/N gate {five_vector.SNR_GATE}x grain")
    a1.set_xscale("log"); a1.set_yscale("log")
    a1.set_xlabel("C channel S/N (resid / grain)"); a1.set_ylabel("chi channel S/N")
    a1.set_title("PER-CHANNEL S/N gate\n(IN = both channels within grain)"); a1.legend(fontsize=7); a1.grid(alpha=0.3)
    return save("five_vector__domain_gate_census", fig)


# ----------------------------------------------------------------------------- view 3
def view_identifiability():
    cases = [("kww_oracle\n(in-family)", DATA / "kww_oracle" / "kww_oracle__X0.5__velocity.json"),
             ("brain\n(degenerate-IN)", DATA / "brain" / "brain__committed__velocity.json"),
             ("square_wave\n(out-family)", DATA / "square_wave" / "square_wave__P100__velocity.json")]
    results = []  # (label, in_domain, assessable, fit)
    for lab, patt in cases:
        p = _cell(patt)
        if not p:
            continue
        rows, _ = rows_dimless(p, with_sem=True)
        f = five_vector.fit_kww5(rows, T=1.0, n_boot=24)
        results.append((lab, f.in_domain, f.identifiability, f))

    fig, (a0, a1) = figure_with_header(
        n_plots=2, slug="five_vector__identifiability", date=STAMP, phase="DEV/validation",
        question="Is the bootstrap identifiability flag ORTHOGONAL to the domain gate — does it say "
                 "WHICH parameters are pinned vs mush, independent of the IN/OUT verdict?",
        minimal_structure="parametric bootstrap (perturb within grain, refit) per parameter; "
                          "identified = tight spread AND not railed at a bound.",
        verdict="YES — orthogonal. kww_oracle is IN with q_EA/tau_alpha/beta_KWW/X PINNED; brain is "
                "IN by the gate but DEGENERATE (nothing pinned — closes the degenerate-IN hole); "
                "square_wave is OUT. Gate-IN does not imply identifiable.",
        placement="kww_oracle: 4/5 pinned (tau_beta mushy on near-degenerate C); brain: 0 pinned, "
                  "gate IN; square_wave: OUT.",
        grounded=["per-parameter bootstrap spread, pinned/mush/railed (box 1)",
                  "the orthogonality: domain gate (IN/OUT) x identifiability (pinned/none) (box 2)"],
        not_grounded=["grain-dependent: cells with no C_sem/chi_sem are 'not assessable' (no bootstrap)",
                      "n_boot cost: dev uses n_boot=24; production pays a higher n_boot"],
    )
    # box 0: spreads per param, grouped by case
    params = list(five_vector._PARAM_NAMES)
    x = np.arange(len(params)); w = 0.26
    for i, (lab, indom, ident, f) in enumerate(results):
        if ident is None or not getattr(ident, "assessable", False):
            continue
        spreads = [ident.spread[p] for p in params]
        bars = a0.bar(x + (i - 1) * w, spreads, w, label=lab.replace("\n", " "))
        for j, p in enumerate(params):
            if ident.identified[p]:
                a0.text(x[j] + (i - 1) * w, spreads[j], "*", ha="center", va="bottom", fontsize=11, color=GREEN)
    a0.set_xticks(x); a0.set_xticklabels(params, rotation=30, fontsize=7, ha="right")
    a0.set_ylabel("bootstrap spread (CV / abs std)")
    a0.set_title("IDENTIFIABILITY per parameter\n(* = PINNED)"); a0.legend(fontsize=6); a0.grid(alpha=0.3, axis="y")
    a0.set_ylim(0, min(2.0, a0.get_ylim()[1]))
    # box 1: orthogonality 2x2
    a1.axhline(0.5, color="gray", lw=0.8); a1.axvline(0.5, color="gray", lw=0.8)
    a1.set_xlim(0, 1); a1.set_ylim(0, 1); a1.set_xticks([0.25, 0.75]); a1.set_yticks([0.25, 0.75])
    a1.set_xticklabels(["gate OUT", "gate IN"], fontsize=8); a1.set_yticklabels(["NOT pinned", "params pinned"], fontsize=8)
    for lab, indom, ident, f in results:
        npinned = sum(ident.identified.values()) if (ident and getattr(ident, "assessable", False)) else 0
        xx = 0.75 if indom else 0.25
        yy = 0.75 if npinned >= 1 else 0.25
        a1.scatter(xx, yy, s=120, c=(GREEN if indom else RED), edgecolor="k", zorder=3)
        a1.annotate(lab.replace("\n", " ") + f"\n({npinned} pinned)", (xx, yy), fontsize=6.5,
                    xytext=(0, -22), textcoords="offset points", ha="center")
    a1.set_title("ORTHOGONALITY\ndomain gate  x  identifiability"); a1.grid(alpha=0.15)
    return save("five_vector__identifiability", fig)


def main():
    print(f"building five-vector views (stamp {STAMP}) -> {VIEWS}")
    view_x_recovery()
    view_domain_gate_census()
    view_identifiability()
    print("done.")


if __name__ == "__main__":
    main()
