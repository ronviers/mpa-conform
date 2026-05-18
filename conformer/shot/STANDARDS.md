# Shot standards — mpa-conform

The verification artifact for mpa-conform work is a **shot** (a time
sequence), not a still PNG. A still cannot show character; character is
*how* the substrate moves through canonical state space over time.

Established 2026-05-17 in response to the user's "grabs are not story"
framing.

> **Upstream of this doc:**
> [`RENDERING_DISCIPLINE.md`](RENDERING_DISCIPLINE.md) — the water MPA
> swims in. Every visual property in every shot maps to framework data;
> differentiation, not decoration. This STANDARDS.md is the technical
> envelope (resolution, fps, compression, file layout) that the
> discipline operates within.

## Defaults

| Knob | Default | Rationale |
|---|---|---|
| Frame rate (encoding) | 10 fps | Matches the grinder's ~30 sample times per cell at the 3-second standard. Use 24 fps for slower-natural-cadence substrates, 60 fps for analysis speed-up. |
| Duration | 3 seconds | Long enough to perceive motion, short enough to render fast and review iteratively. |
| Resolution | 1280×720 | HD-ish, fits review monitors, fast to render. Bump to 1920×1080 for "production" shots. |
| Color space (EXR) | linear, scene-referred | EXR's native expectation. matplotlib output is sRGB; we apply inverse-sRGB before writing the EXR. |
| EXR compression | PIZ | Lossless, fast, VFX-standard for floating-point image data. |
| Preview codec | libx264, yuv420p, CRF 18 | h264 yuv420p plays everywhere; CRF 18 is visually lossless for review. |
| Frame name pattern | `frame_%05d.exr` | 5 digits gives headroom past 99,999 frames; sortable. |

## EXR channel layout

Per [`mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md`](../../../mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md).
Channels in v1 of the shot workflow:

| Channel | Source | Provenance |
|---|---|---|
| R, G, B, A | matplotlib render (sRGB→linear) | per-frame |
| chit | bundle fit_provenance | constant per bundle in v1; per-snapshot inversion is a follow-up |
| gamma_AB | bundle fit_provenance | constant per bundle in v1 |
| regime_label | scale-solver `regime_at` (5-bucket float enum) | constant per bundle in v1 |
| in_gamut | scale-solver `gamut_classify` (1.0 / 0.0) | constant per bundle in v1 |
| provenance_hash | scale-solver `provenance_hash` | constant per bundle in v1 |
| validation_flags | scale-solver `validation_flags_bitfield` (0..7) | constant per bundle in v1 |

Deferred to follow-up moves:
- mpa-solver channels (X_c, X_r, α_s, P_s, N_f, β_mem, Q, I_pred, C_mu) —
  wait for `fit_invariants` Python port.
- Per-snapshot inversion — gives chit, gamma_AB that actually vary across
  the shot. The single move that ships this changes "constant per bundle"
  rows above to "per-frame."
- Trajectory channels — pack into multipart EXR (one 1D image part per
  trajectory observable). Requires multipart-EXR support; deferred until
  a downstream consumer asks.

## What a frame contains (v1)

For a substrate measurement: one frame per **sample time** in the raw
grind cell's `all_samples[]`. The matplotlib render at frame N shows the
substrate observed at sample time t_N — specifically the per-window
C(τ_window) and χ(τ_window) across the 31 tau_windows the grinder
sweeps. As N advances, the substrate's measurement ages; the per-window
shape evolves; that motion *is* the substrate's character.

Glass below Tc: nearly-frozen frame-to-frame at natural cadence; speed
up to see slow aging relaxation. Glass above Tc: rapidly settles. QEC:
flickering. Brain: scenario-shaped. The shot makes this visible.

## Output layout

```
output/shots/<class>/<bundle_stem>/
  frames/frame_00001.exr
  frames/frame_00002.exr
  ...
  preview.mp4
  shot_manifest.json     # per-shot metadata: bundle_id, duration, fps, channels, ffmpeg invocation
```

`output/shots/` is gitignored; shots are regenerated on demand.

## CLI

```
python -m conformer.cli shot <bundle> [--duration 3] [--fps 10] [--width 1280] [--height 720]
python -m conformer.cli shot-all [--class ck-glassy]
```

## Discipline

- **Ship-then-look.** Render one shot, watch the mp4, then iterate.
  Standards above are defaults — change them when looking at the
  artifact reveals a real reason.
- **EXR is the data substrate; mp4 is throwaway preview.** Never edit
  the mp4; regenerate from EXR. Never lose the EXR.
- **One move per session.** Don't pre-build features the next shot
  doesn't ask for.
