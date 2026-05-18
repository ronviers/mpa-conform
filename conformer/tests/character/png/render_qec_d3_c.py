"""Surface-code QEC (d=3 rotated memory-Z), c-regime — second character PNG.

Same single-coherence framing as banach_c_001, with QEC-specific glyphs that
map to substrate-class data per cdv1:

  altitude       <- chit (deeper than Banach: low p_phys -> high G_0/L)
  3x3 grid       <- d=3 surface-code qubit lattice (discrete spatial structure)
  sharp cell edges <- hard-wall substrate (one error breaks code; not Erlang-B)
  discrete pulses <- syndrome-extraction cycles (G_0 quantized in time)
  discrete drops <- physical error events (L quantized in time)
  ring-down rings <- Q natural-oscillation cycles (continuous; kernel property)
  bath plane     <- noise floor (physical error process)

Per cdv1: surface-code QEC distance-3 rotated memory-Z syndrome streams are the
load-bearing positive instance for cross-substrate empirical content (gFDR §).
Hard-wall capacity character: eta = 1[|Gamma*| >= c], abrupt at threshold —
not Erlang-B soft edge.

Framing tweak from banach_c_001: tighter bath extent + larger structure,
targeting ~25-30% canvas occupancy (was ~5%).
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
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# --- cdv1 QEC d=3 c-regime parameters --------------------------------------
# Physical: p_phys = 5e-4 well below surface-code threshold p_th ~ 1e-2.
# Logical: p_L per cycle ~ 1e-6 (d=3, optimal decoder approximation).
# Normalized so L = 1 (logical-error timescale = 1).
p_phys   = 5e-4
p_th     = 1e-2
distance = 3
chit     = 4.0                              # deep c (deeper than Banach's 2.0)
L        = 1.0                              # normalized logical error rate
G_0      = L * np.exp(chit)                 # syndrome-cycle correction rate
gamma_s  = 2.0                              # syndrome decoding turnover (fast)

omega_RO = np.sqrt(2 * gamma_s * L * (np.exp(chit) - 1))
Q        = np.sqrt(2 * L * (np.exp(chit) - 1) / gamma_s)
gamma_RO = omega_RO / (2 * Q)
zeta     = gamma_RO / omega_RO


# --- 4K canvas -------------------------------------------------------------
DPI = 240
W_IN, H_IN = 16, 9
BG = "#08080f"

fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI, facecolor=BG)
ax  = fig.add_subplot(111, projection="3d", facecolor=BG)


# --- Bath plane: noise floor (physical error process) ---------------------
# Framing tweak: smaller extent so structure dominates the frame.
bath_extent = 2.6
xb = np.linspace(-bath_extent, bath_extent, 80)
yb = np.linspace(-bath_extent, bath_extent, 80)
Xb, Yb = np.meshgrid(xb, yb)
rng = np.random.default_rng(7)
Zb = 0.022 * rng.standard_normal(Xb.shape)
ax.plot_surface(Xb, Yb, Zb, color="#10182c", alpha=0.65,
                edgecolor="none", rstride=2, cstride=2, antialiased=True)


# --- Coherence: d=3 surface-code lattice (3x3 grid of cubes at altitude) --
altitude  = chit
cell_size = 0.50                            # half-edge of each qubit cube
cell_gap  = 0.20
pitch     = 2 * cell_size + cell_gap


def cube_faces(cx, cy, cz, h):
    """Six faces of an axis-aligned cube centered at (cx, cy, cz) with half-edge h.

    Returns list of (vertex_array, shade_factor) where shade_factor in [0,1] models
    the pump-vs-leak axis (top brighter, bottom darker)."""
    s = h
    v = np.array([
        [cx - s, cy - s, cz - s], [cx + s, cy - s, cz - s],
        [cx + s, cy + s, cz - s], [cx - s, cy + s, cz - s],
        [cx - s, cy - s, cz + s], [cx + s, cy - s, cz + s],
        [cx + s, cy + s, cz + s], [cx - s, cy + s, cz + s],
    ])
    return [
        ([v[0], v[1], v[2], v[3]], 0.30),   # bottom (leak-facing)
        ([v[4], v[5], v[6], v[7]], 1.00),   # top (pump-facing)
        ([v[0], v[1], v[5], v[4]], 0.58),
        ([v[1], v[2], v[6], v[5]], 0.58),
        ([v[2], v[3], v[7], v[6]], 0.58),
        ([v[3], v[0], v[4], v[7]], 0.58),
    ]


for i in range(distance):
    for j in range(distance):
        cx = (i - 1) * pitch
        cy = (j - 1) * pitch
        cz = altitude
        for face_verts, shade in cube_faces(cx, cy, cz, cell_size):
            color = cm.inferno(0.40 + 0.50 * shade)
            poly = Poly3DCollection(
                [face_verts],
                facecolors=[color],
                edgecolors="#ffb060",        # hard-wall: visible cell boundaries
                linewidths=1.0,
                alpha=0.96,
            )
            ax.add_collection3d(poly)


# --- Q ring-down envelope (continuous; kernel property) -------------------
n_rings = max(3, int(np.floor(Q)))
T_RO    = 2 * np.pi / omega_RO
ring_t  = np.linspace(0, 2 * np.pi, 360)
lattice_radius = 1.6 * pitch                # rings outside the 3x3 grid

for i in range(n_rings):
    n_periods = (i + 1)
    decay     = np.exp(-gamma_RO * n_periods * T_RO)
    r_ring    = lattice_radius * (1.00 + 0.20 * n_periods)
    z_offset  = -0.06 * n_periods
    xr = r_ring * np.cos(ring_t)
    yr = r_ring * np.sin(ring_t)
    zr = np.full_like(ring_t, altitude + z_offset)
    ax.plot(xr, yr, zr, color="#ff9933",
            alpha=float(decay) * 0.85, linewidth=1.8)


# --- Pump: DISCRETE syndrome-cycle pulses (vs Banach continuous cone) -----
# Each pulse is a thin ring descending toward the lattice top.
# Discreteness = measurement-based quantum operations are cycle-quantized.
n_pulses    = 9
pulse_top   = altitude + 2.3
pulse_bot   = altitude + cell_size + 0.05
pulse_frac  = np.linspace(0, 1, n_pulses)
for frac in pulse_frac:
    z_p   = pulse_top - frac * (pulse_top - pulse_bot)
    alpha = 0.22 + 0.55 * frac              # newer cycles brighter
    r_p   = 0.10 + 0.18 * (z_p - pulse_bot) / (pulse_top - pulse_bot + 1e-6)
    t     = np.linspace(0, 2 * np.pi, 80)
    ax.plot(r_p * np.cos(t), r_p * np.sin(t),
            np.full_like(t, z_p),
            color="#7fdcff", alpha=alpha, linewidth=1.8)


# --- Leak: DISCRETE error events (vs Banach continuous wisps) -------------
# Each event is a short vertical drop emanating from a random lattice cell.
# Discreteness = physical errors are discrete events (bit flips, phase flips).
rng2 = np.random.default_rng(42)
n_events = 16
for _ in range(n_events):
    i = rng2.integers(0, distance)
    j = rng2.integers(0, distance)
    cx = (i - 1) * pitch + rng2.uniform(-cell_size * 0.4, cell_size * 0.4)
    cy = (j - 1) * pitch + rng2.uniform(-cell_size * 0.4, cell_size * 0.4)
    progress = rng2.uniform(0.10, 0.95)
    z_start = altitude - cell_size
    z_end   = 0.02
    z_now   = z_start - progress * (z_start - z_end)
    seg_h   = 0.16
    z_seg   = np.linspace(z_now - seg_h, z_now + seg_h, 14)
    z_seg   = np.clip(z_seg, z_end, z_start)
    x_seg   = np.full_like(z_seg, cx)
    y_seg   = np.full_like(z_seg, cy)
    alphas  = (1 - np.abs(np.linspace(-1, 1, len(z_seg)))) * 0.70
    for k in range(len(z_seg) - 1):
        ax.plot(x_seg[k:k + 2], y_seg[k:k + 2], z_seg[k:k + 2],
                color="#e85a5a", alpha=float(alphas[k]), linewidth=2.4)


# --- 3/4 camera ------------------------------------------------------------
ax.view_init(elev=22, azim=42)
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
fig.text(0.04, 0.945, "Surface-code QEC (d=3) — c-regime",
         color="white", fontsize=20, weight="bold", family="monospace")
fig.text(0.04, 0.910,
         "cdv1 character, hard-wall substrate, single tau_obs frame",
         color="#9aa0c8", fontsize=11, family="monospace")

data_plate = (
    f"p_phys     = {p_phys:.2e}\n"
    f"p_th       = {p_th:.2e}\n"
    f"distance   = {distance}\n"
    f"chit       = {chit:.3f}\n"
    f"G_0 / L    = {np.exp(chit):.3f}\n"
    f"L          = {L:.3f}\n"
    f"omega_RO   = {omega_RO:.3f}\n"
    f"Q          = {Q:.3f}\n"
    f"gamma_RO   = {gamma_RO:.3f}\n"
    f"zeta       = {zeta:.3f}  (deep underdamped)"
)
fig.text(0.78, 0.06, data_plate, color="#c8c8ff", fontsize=10,
         family="monospace", verticalalignment="bottom")

glyph_legend = (
    "GLYPH MAPPING\n"
    "  altitude     -> chit headroom\n"
    "  3x3 grid     -> d=3 qubit lattice\n"
    "  sharp edges  -> hard-wall substrate\n"
    "  pulse rings  -> syndrome cycles (G_0)\n"
    "  red drops    -> physical errors (L)\n"
    "  orange rings -> Q ring-down cycles\n"
    "  dark plane   -> noise floor"
)
fig.text(0.04, 0.06, glyph_legend, color="#9aa0c8", fontsize=10,
         family="monospace", verticalalignment="bottom")


# --- Save 4K ---------------------------------------------------------------
out_dir = Path(__file__).parent
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "qec_d3_c_001.png"

plt.savefig(out_path, dpi=DPI, facecolor=BG)
plt.close(fig)

w_px, h_px = int(W_IN * DPI), int(H_IN * DPI)
print(f"wrote {out_path} ({w_px}x{h_px})")
