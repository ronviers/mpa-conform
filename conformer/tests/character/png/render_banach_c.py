"""Banach substrate, c-regime — first character PNG iteration.

Single coherence held above bath at altitude = chit. Every visual property
maps to cdv1 framework data:

  altitude       <- chit = ln(G_0 / L)                    [headroom above threshold]
  structure size <- saturated amplitude (G_0 - L)         [presence]
  ring-down rings <- Q natural-oscillation cycles         [§Stability]
  ring decay     <- gamma_RO                              [§Stability]
  pump cone      <- G_0 (maintenance budget descending)   [§Setting]
  leak filaments <- L (decay rate dissolving into bath)   [§Setting]
  bath plane     <- the thing held against                [§Setting]

Per rendering discipline: differentiation, not decoration.
First iteration; expected to be trash. Matplotlib 3D, 4K, single still.
"""

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm


# --- cdv1 Banach c-regime parameters --------------------------------------
chit    = 2.0                              # ln(G_0/L), deeply above threshold
L       = 1.0                              # decay rate
G_0     = L * np.exp(chit)                 # = e^2 ~ 7.389
gamma_s = 0.5                              # slow-resource turnover

# Derived from cdv1 §Stability
omega_RO = np.sqrt(2 * gamma_s * L * (np.exp(chit) - 1))
Q        = np.sqrt(2 * L * (np.exp(chit) - 1) / gamma_s)
gamma_RO = omega_RO / (2 * Q)
zeta     = gamma_RO / omega_RO


# --- 4K canvas ------------------------------------------------------------
DPI = 240
W_IN, H_IN = 16, 9                           # 16*240 = 3840, 9*240 = 2160
BG = "#08080f"

fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI, facecolor=BG)
ax  = fig.add_subplot(111, projection="3d", facecolor=BG)


# --- Bath plane: the thing being held against -----------------------------
bath_extent = 4.0
xb = np.linspace(-bath_extent, bath_extent, 80)
yb = np.linspace(-bath_extent, bath_extent, 80)
Xb, Yb = np.meshgrid(xb, yb)
rng = np.random.default_rng(0)
Zb = 0.015 * rng.standard_normal(Xb.shape)           # faint thermal noise
ax.plot_surface(Xb, Yb, Zb, color="#10182c", alpha=0.55,
                edgecolor="none", rstride=2, cstride=2, antialiased=True)


# --- Coherence structure at altitude = chit -------------------------------
altitude  = chit
R_struct  = 0.40 + 0.05 * (G_0 - L) / G_0            # amplitude-modulated radius
phi   = np.linspace(0, np.pi, 64)
theta = np.linspace(0, 2 * np.pi, 64)
PHI, THETA = np.meshgrid(phi, theta)
Xs = R_struct * np.sin(PHI) * np.cos(THETA)
Ys = R_struct * np.sin(PHI) * np.sin(THETA)
Zs = altitude + R_struct * np.cos(PHI)

# Bright at pump-facing pole (top), warm-down toward leak-facing pole (bottom)
shade = 0.5 + 0.5 * np.cos(PHI)
colors = cm.inferno(0.40 + 0.55 * shade)
ax.plot_surface(Xs, Ys, Zs, facecolors=colors, alpha=0.96,
                edgecolor="none", antialiased=True, shade=True)


# --- Q ring-down envelope -------------------------------------------------
# Number of visible rings = floor(Q); each ring decays with gamma_RO over
# one natural period T_RO = 2 pi / omega_RO
n_rings = max(3, int(np.floor(Q)))
T_RO    = 2 * np.pi / omega_RO
ring_t  = np.linspace(0, 2 * np.pi, 360)

for i in range(n_rings):
    n_periods = (i + 1)
    decay     = np.exp(-gamma_RO * n_periods * T_RO)
    r_ring    = R_struct * (1.25 + 0.32 * n_periods)
    z_offset  = -0.06 * n_periods
    xr = r_ring * np.cos(ring_t)
    yr = r_ring * np.sin(ring_t)
    zr = np.full_like(ring_t, altitude + z_offset)
    ax.plot(xr, yr, zr, color="#ff9933",
            alpha=float(decay) * 0.85, linewidth=1.6)


# --- Pump cone from above: G_0 descending ---------------------------------
n_pump_rings = 28
for i in range(n_pump_rings):
    frac = i / n_pump_rings
    z_p  = altitude + 2.4 * (1.0 - frac)
    r_p  = 0.05 + 0.30 * (z_p - altitude) / 2.4
    t    = np.linspace(0, 2 * np.pi, 48)
    ax.plot(r_p * np.cos(t), r_p * np.sin(t),
            np.full_like(t, z_p),
            color="#7fdcff", alpha=0.08, linewidth=0.9)


# --- Leak filaments: L dissolving to bath ---------------------------------
n_tendrils = 10
for j in range(n_tendrils):
    phi_t = 2 * np.pi * j / n_tendrils
    z_t   = np.linspace(altitude - R_struct, 0.02, 40)
    drop  = (altitude - z_t) / altitude
    spiral = 1.4 * drop
    r_t   = R_struct * (1 - 0.55 * drop) + 0.08 * spiral
    x_t   = r_t * np.cos(phi_t + spiral)
    y_t   = r_t * np.sin(phi_t + spiral)
    alphas = np.linspace(0.45, 0.04, len(z_t) - 1)
    for k in range(len(z_t) - 1):
        ax.plot(x_t[k:k + 2], y_t[k:k + 2], z_t[k:k + 2],
                color="#d96666", alpha=float(alphas[k]), linewidth=1.1)


# --- 3/4 camera -----------------------------------------------------------
ax.view_init(elev=22, azim=38)

ax.set_xlim(-bath_extent, bath_extent)
ax.set_ylim(-bath_extent, bath_extent)
ax.set_zlim(-0.3, altitude + 2.6)

ax.set_xticks([]); ax.set_yticks([])
ax.set_zticks([0, altitude])
ax.set_zticklabels(["bath", f"chit = {chit:.2f}"], color="white", fontsize=11)

for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor("#222244")
ax.grid(False)


# --- Title + data plate + glyph legend ------------------------------------
fig.text(0.04, 0.945, "Banach substrate — c-regime",
         color="white", fontsize=20, weight="bold", family="monospace")
fig.text(0.04, 0.910,
         "cdv1 character, single coherence, single tau_obs frame",
         color="#9aa0c8", fontsize=11, family="monospace")

data_plate = (
    f"chit       = {chit:.3f}\n"
    f"G_0 / L    = {np.exp(chit):.3f}\n"
    f"L          = {L:.3f}\n"
    f"omega_RO   = {omega_RO:.3f}\n"
    f"Q          = {Q:.3f}\n"
    f"gamma_RO   = {gamma_RO:.3f}\n"
    f"zeta       = {zeta:.3f}  (< 1, underdamped)"
)
fig.text(0.78, 0.06, data_plate, color="#c8c8ff", fontsize=10,
         family="monospace", verticalalignment="bottom")

glyph_legend = (
    "GLYPH MAPPING\n"
    "  altitude   -> chit headroom\n"
    "  rings      -> Q ring-down cycles\n"
    "  cyan cone  -> G_0 pump\n"
    "  red wisps  -> L leak to bath\n"
    "  dark plane -> bath"
)
fig.text(0.04, 0.06, glyph_legend, color="#9aa0c8", fontsize=10,
         family="monospace", verticalalignment="bottom")


# --- Save 4K --------------------------------------------------------------
out_dir = Path(__file__).parent
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "banach_c_001.png"

plt.savefig(out_path, dpi=DPI, facecolor=BG)
plt.close(fig)

w_px, h_px = int(W_IN * DPI), int(H_IN * DPI)
print(f"wrote {out_path} ({w_px}x{h_px})")
