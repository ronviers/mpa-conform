"""Result image for laser_ro_pump_sweep_v2 — band + per-curve fits + FDR locus."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
sys.path.insert(0, r"H:\mpa-conform\blockin")
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from view_header import figure_with_header, timestamped_view_path

CSV = r"H:\mpa-conform\blockin\workspace\laser_ro_pump_sweep_v2.data.csv"
WS = r"H:\mpa-conform\blockin\workspace"
raw = np.genfromtxt(CSV, delimiter=",", names=True)
res = json.load(open(r"H:\mpa-conform\blockin\workspace\_fit_results.json"))

def C_model(t, zeta, wn):
    if zeta < 1.0:
        wd = wn * np.sqrt(1 - zeta**2)
        return np.exp(-zeta*wn*t)*(np.cos(wd*t) + (zeta*wn/wd)*np.sin(wd*t))
    s = wn*np.sqrt(zeta**2-1); r1=-zeta*wn+s; r2=-zeta*wn-s
    A=-r2/(r1-r2); B=r1/(r1-r2)
    return A*np.exp(r1*t)+B*np.exp(r2*t)

curves = {}
for c in (1,2,3,4):
    m = raw["curve"]==c
    t=raw["tau"][m]; C=raw["C"][m]; chi=raw["chi"][m]
    o=np.argsort(t)
    curves[c]=(t[o],C[o],chi[o])

zetas = [res[str(c)]["zeta"] for c in (1,2,3,4)]
wds   = [res[str(c)]["wd"]   for c in (1,2,3,4)]
overs = [res[str(c)]["overshoot"] for c in (1,2,3,4)]
colors = {1:"#7a4fa3", 2:"#2c7fb8", 3:"#d95f0e", 4:"#cc1111"}

fig, axes = figure_with_header(
    n_plots=4,
    slug="laser_ro_pump_sweep_v2",
    date="STAMP_PLACEHOLDER",
    phase="DEV/blind",
    question=("Four settling curves across the full pump range (1=barely lasing/sluggish, "
              "middle=clean crisp ring, 4=driven hard/rings a touch less crisp). Where is "
              "the response healthiest, and which way is the room — is more drive really "
              "buying stability margin, or is there a sweet spot I'm driving past?"),
    minimal_structure=("one driven, damped mode exchanging energy with a single reservoir — "
                       "one thing and its bath; no second oscillator, no loop."),
    verdict=("Response quality (damping ratio zeta) is NON-MONOTONIC along drive 1->4: "
             "2.67 -> 0.90 -> 0.28 -> 0.55. Healthiest at the moderate end (curve 2, zeta~0.9, "
             "near the well-damped sweet spot); curve 4 has recovered toward it. The "
             "perceptually-crispest MIDDLE curve (3, zeta~0.28) is actually the LOWEST-margin "
             "point — biggest overshoot, most ring, nearest the underdamped limit. Low-end "
             "limit = overdamped/sluggish wall (curve 1: ring=0, ~10x slower). High-end: NOT a "
             "wall — driving past the curve-3 dip RECOVERS margin & speed. 'More drive = more "
             "margin' is wrong: margin dips in the interior; the safe-fast zone is curves 2 & 4, "
             "not the ringy middle."),
    grounded=[
        "per-curve zeta/wn/ring-wd/overshoot/RMSE: independent single-curve damped-mode fits (placement, traversal s3)",
        "curve 1 overdamped, ring=0 BY REGIME (zeta>1, C never crosses 0, RMSE 8e-4) — regime-zero, not a kill (s5)",
        "band dip in zeta at curve 3 + recovery at 4: read off the 4 independent placements (stitched I2 + band readout)",
        "single-mode structure, no loop: one damped mode per curve; FDR-locus linear for curves 1,2,4 (R2>=0.92)",
        "low-end headroom = overdamped wall: curve 1 wd=0 and ~10x longer settling window",
    ],
    not_grounded=[
        "absolute pump values / where the sweet spot sits in physical drive units — packet gives ORDER ONLY",
        "exact location of the zeta~0.7 optimum between sampled curves — 4 samples bracket but cannot resolve it",
        "what happens beyond curve 4 (keeps recovering, or turns over?) — only 4 curves; high-end is a trend not a ceiling",
        "absolute distance-to-instability in native units — no externally-anchored threshold; margin is relative across curves",
        "identifiability error bars — dev ledger n_boot=0; zeta ordering robust by eye, not bootstrap-certified",
    ],
    placement="curve1 zeta=2.67 wd=0(regime) | curve2 zeta=0.90 wd=0.038 | curve3 zeta=0.28 wd=0.343 ovr=0.39 | curve4 zeta=0.55 wd=1.13",
)
ax_band, ax_fits, ax_norm, ax_fdr = axes

# --- BOX 1: THE BAND — response-quality (zeta) vs ordered curve index ---
idx = [1,2,3,4]
ax_band.plot(idx, zetas, "-o", color="#111111", lw=2, ms=9, zorder=3)
for c in idx:
    ax_band.plot(c, zetas[c-1], "o", color=colors[c], ms=11, zorder=4)
ax_band.axhline(0.7, ls="--", color="#0a5d00", lw=1.3)
ax_band.text(4.05, 0.7, " sweet spot\n zeta~0.7", color="#0a5d00", fontsize=7, va="center")
ax_band.axhline(1.0, ls=":", color="#7a4fa3", lw=1.1)
ax_band.text(1.0, 1.02, "overdamped wall (zeta>=1)", color="#7a4fa3", fontsize=7, va="bottom")
ax_band.annotate("lowest margin\n(ringiest)", xy=(3, zetas[2]), xytext=(2.5, 1.5),
                 fontsize=7.5, color="#d95f0e",
                 arrowprops=dict(arrowstyle="->", color="#d95f0e"))
ax_band.set_title("THE BAND — response quality (damping ratio zeta) vs drive", fontsize=9, fontweight="bold")
ax_band.set_xlabel("curve index (drive, low -> high)")
ax_band.set_ylabel("zeta  (higher = more damped/sluggish)")
ax_band.set_xticks(idx)
ax_band.grid(alpha=0.3)

# --- BOX 2: per-curve C(tau) fits, normalized tau so each is legible ---
for c in idx:
    t,C,chi = curves[c]
    z=res[str(c)]["zeta"]; wn=res[str(c)]["wn"]
    tn = t/t[-1]
    ax_fits.plot(tn, C, ".", color=colors[c], ms=3, alpha=0.6)
    tt = np.linspace(t[0], t[-1], 600)
    ax_fits.plot(tt/t[-1], [C_model(x,z,wn) for x in tt], "-", color=colors[c], lw=1.6,
                 label=f"c{c}: zeta={z:.2f}")
ax_fits.axhline(0, color="#999", lw=0.8)
ax_fits.set_title("per-curve C(tau) fits (tau normalized per curve)", fontsize=9, fontweight="bold")
ax_fits.set_xlabel("tau / tau_settle  (per-curve)")
ax_fits.set_ylabel("C  (autocorrelation)")
ax_fits.legend(fontsize=7, loc="upper right")
ax_fits.grid(alpha=0.3)

# --- BOX 3: ring frequency & overshoot vs drive (the regime story) ---
axb = ax_norm.twinx()
ax_norm.plot(idx, wds, "-s", color="#cc1111", lw=1.8, ms=8, label="ring freq wd")
axb.plot(idx, overs, "-^", color="#d95f0e", lw=1.8, ms=8, label="overshoot")
ax_norm.set_title("ring frequency & overshoot vs drive", fontsize=9, fontweight="bold")
ax_norm.set_xlabel("curve index (drive)")
ax_norm.set_ylabel("ring freq wd", color="#cc1111")
axb.set_ylabel("peak overshoot", color="#d95f0e")
ax_norm.set_xticks(idx)
ax_norm.annotate("curve 1: ring=0\n(by regime,\noverdamped)", xy=(1, 0), xytext=(1.1, max(wds)*0.4),
                 fontsize=7, color="#7a4fa3",
                 arrowprops=dict(arrowstyle="->", color="#7a4fa3"))
ax_norm.grid(alpha=0.3)

# --- BOX 4: FDR locus cross-check chi vs C0-C(tau) ---
for c in idx:
    t,C,chi = curves[c]
    x = C[0]-C
    ax_fdr.plot(x, chi, ".", color=colors[c], ms=3, alpha=0.7, label=f"c{c}")
ax_fdr.set_title("FDR-locus cross-check: chi vs C(0)-C(tau)", fontsize=9, fontweight="bold")
ax_fdr.set_xlabel("C(0) - C(tau)")
ax_fdr.set_ylabel("chi (integrated response)")
ax_fdr.legend(fontsize=7, loc="lower right")
ax_fdr.grid(alpha=0.3)

out, STAMP = timestamped_view_path(WS)
# stamp the header to match filename: rebuild header text would be heavy; instead set via fig text replace
# Re-render header date by editing the first header line text object.
for txt in fig.axes[0].texts:
    if "STAMP_PLACEHOLDER" in txt.get_text():
        txt.set_text(txt.get_text().replace("STAMP_PLACEHOLDER", STAMP))
        break
fig.savefig(out, dpi=150)
print("WROTE", out)
print("STAMP", STAMP)
