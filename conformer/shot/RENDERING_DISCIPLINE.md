# Rendering discipline — the water MPA swims in

Established 2026-05-17. This is not a feature; it is the medium. Every
shot that ships in any MPA repo, today or in any future session, obeys
this discipline. It does not get re-litigated per session.

The phrasing comes from the user: *"we do not decorate. we need to
convey differentiation but that different. it will be the water mpa
swims in."*

## What this renderer is (and is not)

This renderer is **not a simulation.** The substrate's dynamics are
solved upstream — `mpa-solver` integrates the trajectory,
`mpa-scale-solver` projects it to canonical-space states. By the time
the renderer receives data, the physics is *done*.

Particles are a **visual medium** for upstream-computed framework data,
not their own physics. The analogy that holds: a smoke machine
demonstrating airflow. The smoke isn't the air, but it makes the air
visible. Framework data is the air; particles are the smoke.

Concrete consequences:

- **Particles cannot affect each other or framework state.** Remove
  every particle from the buffer and the underlying canonical-space
  point is unchanged. The renderer is downstream-only.
- **Particle motion is rendering, not substrate dynamics.** When a
  particle moves, dies, or fades, it is *reading out* a framework
  quantity (rate, lifespan, opacity), not evolving anything.
- **"Runup" is particle equilibration, not a dynamical transient.**
  The buffer is empty at frame 0; emit/die reaches steady-state density
  after roughly `lifespan_s / dt` frames. Snapshot before that and the
  image is sparse; after that and the framework's steady-state visual
  signature is set. This is buffer filling, not forgetting initial
  conditions.
- **Per-emitter particle count is set by the framework, not by us.**
  Steady-state count per emitter ≈ `rate_per_emitter × lifespan_s`.
  Both inputs come from the channel contract. We do not crank emit
  rate for visual reasons.
- **Million-particle scale is a scene property, not an emitter
  property.** Inflating one substrate's emit rate to hit a target
  count is decoration. Millions arises from multi-emitter scenes
  (basin atlases, chit sweeps, multi-substrate composites), where each
  emitter contributes its framework-set hundreds-to-thousands and the
  scene aggregates.

These consequences are what make the two rules below *self-enforcing*.
Once particles are smoke and the framework is the air, "no decoration"
stops being a rule to remember and becomes the only thing that makes
sense.

## The two rules

### 1. Every visual property maps to framework data.

If a property is visible — color, position, size, rate, lifespan,
opacity, velocity, mass, particle count, surface curvature, anything —
it must derive from a named MPA channel or framework quantity. No
exceptions.

Examples that obey:
- A particle is **cyan** because `regime_label == 1.0` (c_near_s).
- A particle's **lifespan is short** because `|chit|` is small (the
  substrate is near critical).
- A particle's **mass is heavy** because `|gamma_AB|` is large (strong
  cross-mode coupling).
- A particle's **opacity is dim** because `validation_flags` is missing
  bits.
- An emitter is **inactive** because `in_gamut == 0.0`.

Examples that violate (forbidden):
- Particles **rotate** because rotation looks dynamic. (Nothing in cdv1
  rotates.)
- Particles **jitter** because static looks dull. (The framework
  doesn't add noise to canonical states.)
- Surface has **specular highlights** because it looks 3D. (Specularity
  doesn't represent a substrate property.)
- Background is **blue** for atmosphere. (The atmosphere has no MPA
  channel.)
- Particles **trail** with motion blur for stylistic effect. (Motion
  blur isn't in the framework.)

### 2. Differentiation, not decoration.

Substrates must look *distinguishably different* in shots. That
difference is the framework's diagnostic. If two substrates look the
same in a shot, the framework data is the same — or the rendering
is washing out a real difference. Either is a bug.

Differentiation arises from the data flowing through the channel
mappings. It does not arise from artistic choices. *No artistic
choices.*

If a substrate looks the way it looks because the renderer made a
visual choice independent of the data, that choice is decoration and
must be removed. The renderer is downstream of cdv1, not a parallel
artistic interpretation.

## What this rules out, explicitly

- Rotation, spin, angular velocity (nothing in cdv1 rotates).
- Random walks, Perlin noise, procedural jitter beyond what
  framework-emitted noise prescribes.
- View-aligned billboards if alignment doesn't mean anything.
- Specular shading, normal-map lighting, decorative shadows.
- Motion blur, depth of field, lens flares.
- Camera shake (the camera is a kinematic path through canonical
  space; shake is decoration).
- Background atmosphere, gradient skies, ambient color tints.
- Particle trails that exceed what `I_pred` (predictive information)
  prescribes per-emitter.
- Font choices, icon styles, badge ornaments. Frame metadata is text;
  text is type, not visual data.
- Audio (no MPA channel represents sound; if added later, it must map
  to a channel).

## What this rules IN — the channel → property contract (v1)

Binds **EXR Channel Contract v1**
(authoritative spec at
[`mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md`](../../../mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md)).
When that producer contract bumps version, this section and
[`particle_renderer.py`](particle_renderer.py)'s
`channel_to_emitter_params()` bump in **lockstep** in the same change.

Executable spec lives in `channel_to_emitter_params()`. Versioned;
changes are deliberate.

### Per-frame channels (from scale-solver, packed into every EXR frame)

| Channel | Property | Mapping |
|---|---|---|
| `regime_label` | particle color hue | 5-bucket palette: deep_c blue → c_near_s cyan → s_critical green → r_near_s orange → deep_r red |
| `chit` | emit rate, particle lifespan | rate ∝ `1 / (1 + |chit|)` (high near critical); lifespan ∝ `|chit|` (extreme = long-lived) |
| `gamma_AB` | particle mass | `mass = 1 + 2|gamma_AB|`; drag = `1/mass` (heavy = inertial) |
| `in_gamut` | emit activation | rate ∝ `in_gamut` (0 = no emission, 1 = full emission) |
| `validation_flags` | particle opacity | `opacity = popcount(bits) / 3.0` (full validation = opaque, missing bits = ghost) |
| `provenance_hash` | **NOT a visual property** | fingerprint only; would add noise to display if mapped |

### Per-emitter channels (deferred until `fit_invariants` Python port lands)

| Channel | Property | Mapping (target) |
|---|---|---|
| `alpha_s` | per-emitter lifespan decay | particles age faster where Onsager exponent is steeper |
| `P_s` | drag / damping | high plateau = stronger damping |
| `N_f` | particle count multiplier per emitter | effective-modes count amplifies emission |
| `X_c, X_r` | velocity bias direction | cooperative vs random projection sets emit direction |
| `Q` | pulsation / oscillation period | cycles-of-headroom drives rhythmic emission |
| `I_pred` | particle trail length | predictive information sets how much past a particle carries |
| `C_mu` | particle shape complexity | statistical complexity drives shape variation |

When these channels land in the EXR (after the `fit_invariants` port),
extend the mapping here. The same Python renderer + the same WebGL
implementation must adopt them together.

## What's a property of the RENDERING, not the DATA?

Some properties are technical necessities, not data carriers, and
that's OK *as long as they don't pretend to be data*:

- **Frame metadata text** (cell id, sample-time, frame N/M): required
  for reading the shot. Render as text, not as a particle property.
  Document explicitly that text is metadata. Bottom strip, fixed
  position, fixed font. No icons, no badges, no color coding.
- **Splat radius / particle pixel size**: technical resolution choice;
  should be roughly equal across substrates. Document the default.
  Don't vary by class.
- **Background color**: pure black. Always. No gradient, no atmosphere.
- **Reference traces** (predicted, Banach overlays): these *are* data
  (the framework's analytical voice). Their color encodes "predicted"
  vs "Banach"; their alpha encodes their being diagnostic-floor (faint
  enough to read against, opaque enough to see).
- **Camera position**: when 3D rendering lands, the camera path is
  itself the Banach trajectory through canonical space. Not a free
  parameter. See the sequenced single-move plan below.

## Implementation discipline

- **The Python (Taichi) implementation is the executable spec.** The
  eventual auditor viewport (WebGL/JS) reproduces the same physics
  bit-for-bit. Per the Python-as-pseudo-spec pattern used by
  mpa-scale-solver's Rust port.
- **Channel→property changes are versioned.** Bump
  `channel_to_emitter_params` schema version; old shots stay
  reproducible from old code. Document the bump.
- **One single move at a time.** Per
  [`feedback_single_move_design`](../../../C--/Users/ronviers/.claude/projects/H--/memory/feedback_single_move_design.md):
  render one shot, look at it in DJV, decide the next move. Don't
  pre-build mappings the next shot doesn't ask for.

## Sequenced single-move plan for the rendering stack

1. **2D particle renderer (channel → emitter)** — *shipped 2026-05-17*.
   `particle_renderer.py` + `_render_frames_particle` in `builder.py`.
2. **Fix the per-window float-alignment bug** — the 2D renderer
   currently sees only 4 of 31 tau_window emitters because `dict[float]`
   lookup compares exact values. Tolerant nearest-match or index-paired
   lookup. (Open; the 3D path in step 3 does not inherit this — it
   indexes emitters by integer, not float key.)
3. **3D canonical-space rendering + Banach as data source + single-still PNG workflow**
   — *shipped 2026-05-17*. Three new modules:
   `particle_renderer_3d.py` (`ParticleField3D`: 3D positions, fixed 3/4
   perspective camera via lookAt + perspective MVP, additive splat with
   1/clip.w foreshortening, `MAX_PARTICLES_3D = 2_000_000`),
   `png_writer.py` (OIIO scene_linear → sRGB, 8-bit PNG out),
   `banach_shot.py` (orchestrator: sweeps `nu`, emits at
   `BanachSubstrate.state_at(nu)` per the channel→emitter contract,
   equilibrates, snapshots). End-to-end pipeline validated:
   Taichi → particle cache (`.npz`) → EXR → OIIO → 4K PNG.
4. **EXR sequence + ffmpeg + DJV (animated shot) of the same subject**
   — extend the single-still path to a per-frame EXR write loop, then
   wrap with the existing `encoder.encode_preview_from_exr_sequence`
   for mp4 + DJV review. Pick what's animated: discipline-natural
   choice is the Banach trajectory as *camera path* (camera moves
   through canonical space along the RG flow; emitters stay in their
   canonical positions; the viewer travels with the substrate). Simpler
   first move is the nu build-up (camera fixed, emitters appear
   sequentially as nu sweeps, trajectory draws itself over time).
   Infrastructure ~90% in place after step 3 (only the sequence
   orchestrator + camera-path generator are new).
5. **splashsurf surface reconstruction** *(if and when a continuous
   field shot is needed)*. Gamut envelopes, regime manifold
   boundaries. Defer until a single move asks for it.
6. **Multi-substrate composite shots** — glass + quantum + brain
   canonical trajectories in one scene. Visible universality.
7. **WebGL viewport implementation** in mpa-auditor — same physics,
   different runtime. Closes the loop on the destination.

Each step is one shot to look at. Order can shift based on what each
shot reveals. Don't plan past the next single move.

## Workflow: single-still PNG (iteration grade)

Shipped 2026-05-17 (step 3 above). Run from `H:/mpa-conform`:

```
python -m conformer.shot.banach_shot
```

Pipeline: **Taichi → particle cache (`.npz`) → EXR → OIIO → 4K PNG.**
splashsurf remains deferred (step 5); no continuous-field shot has
asked for it yet.

Output at `output/shots/banach/fully_connected/`:
- `particles_cache.npz` — active particles after equilibration
  (positions, velocities, life, color, mass)
- `banach_fully_connected.exr` — multi-channel EXR (RGBA + 6 data
  channels per Channel Contract v1)
- `banach_fully_connected.png` — 4K sRGB PNG via OIIO color convert

Orchestrator parameters: `chit_0`, `gamma_AB_0`, `nu_range`,
`n_emitters`, `width/height`, `equilibration_steps`. Subject in v1 is
the analytical Banach trajectory; for real substrates the same shape
of orchestrator reads inverted canonical-space states from
mpa-scale-solver instead of `BanachSubstrate.state_at`. The renderer
itself is substrate-agnostic — it consumes canonical states and
channel→emitter params, nothing else.

**Why single-still earns its place alongside EXR sequences.** PNG
iteration is faster than full EXR/mp4/DJV review (no ffmpeg encode, no
DJV launch) and is universally inspectable. It's the right grade for
locking visual grammar before committing a sequence; for production
review the EXR + mp4 + DJV path (step 4) is the destination.

## τ_obs and the graphics camera — two modes

[RFC-S §0.2](../../../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md) names
the framework's camera: **"τ_obs is the camera; canonical representation
is observer-relative."** The canonical view of a substrate is what the
observer-at-τ_obs sees.

A render has *two* cameras, and how they relate is a deliberate choice
per shot:

| | Framework camera | Graphics camera |
|---|---|---|
| Reads | τ_obs — observer position in canonical space | eye / target / perspective MVP — screen-space projection |
| Owned by | RFC-S | the renderer |

Two modes for how they relate:

**Mode A — τ_obs as world axis.** The full RG trajectory is laid out
spatially; one emitter per τ_obs value populates a spatial dimension.
The graphics camera is a fixed meta-viewer looking *at* the trajectory.
The viewer sees every observer position simultaneously — the atlas /
memory / map of the substrate across all τ_obs. Faithful to the data
being τ_obs-indexed, but the graphics camera ≠ τ_obs.

  *Used by:* `banach_shot.py` (the shipped single-still PNG). World axes
  are `(gamma_AB, log10(nu), chit)`; ν is the world_y axis;
  graphics camera fixed at 3/4 view.

**Mode B — τ_obs as graphics camera.** The graphics camera *is* τ_obs.
At each frame, the camera position is determined by the substrate's
canonical state at that observer position; the viewer travels with the
substrate through canonical space. RFC-S §0.2 *literally*.

  *Used by:* sequenced plan step 4 (Banach-as-camera-path). At frame
  *t*, graphics camera position is `BanachSubstrate.state_at(nu_t)`;
  emitters stay placed in canonical space; viewer rides the RG flow.

Both modes are valid; the choice maps to what the shot is *about*. Mode
A shows the substrate's atlas — useful for static portraits, comparison
plates, and basin-blending visualizations where seeing all observer
positions at once IS the point. Mode B shows the substrate's
*current view* — useful for sequences, drive-into-the-substrate shots,
and any artifact where the framework-camera-as-graphics-camera mapping
is the load-bearing claim.

Document which mode a shot uses, in the shot's manifest. Modes can
compose (e.g. Mode B graphics-camera with Mode A laid-out reference
overlays in the same scene) but the primary mode should be named.

## Level of detail as scale management

A particle's level of detail (splat radius, opacity, frequency content)
can be driven by *two* distances, and the difference matters:

- **Graphics distance** (`1/clip.w` from the graphics camera): geometric
  perspective foreshortening. Required by any 3D rendering and already
  implemented in `ParticleField3D.render_perspective_additive`. This is
  a property of the rendering, not the data — documented as a
  geometric necessity, not decoration.
- **Framework distance** (`|τ_obs_particle − τ_obs_camera|` in
  canonical space): how far the particle's emitter sits from the
  framework camera in observer-position space. NOT yet implemented;
  flagged here as a future tweak when LOD ergonomics actually ask for it.

The second distance is the discipline-aligned LOD knob:
**level-of-detail IS RG-flow distance from the observer.** Per
[RFC-S §0.6](../../../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md) RG
flow is the foundational scale structure; per v9's Compression Axiom
each τ_obs step compresses canonical structure by `ε`. A particle's
visible detail mapping to its compression depth relative to the
observer is *the same parameter the framework already uses to
characterize the substrate's scale management*. Not a decorative blur
— a faithful rendering of the substrate's coarsening rate.

This is **depth-of-field in canonical space**, not graphics space.
Mode B benefits naturally: particles from past observer positions
(now framework-distant from the camera in τ_obs) fade according to
the framework's own coarsening rate, rather than being indistinguishable
from current-τ_obs particles at the same graphics depth.

**Implementation route (when the tweak lands):**
- Add per-particle `tau_obs_birth` (the emitter's `nu` at emission) as
  a particle field in `ParticleField3D`.
- Per-frame compute `|Δτ_obs|` against the framework camera's `τ_obs`.
- Map to splat properties: splat radius scales with framework distance
  (compression-aware), opacity decays with `Δτ_obs` per the substrate's
  `ε` profile.
- Bumps the channel→emitter contract to v2 (per-particle channel
  alongside per-emitter); contract bump in lockstep across producer
  manifest, this doc, and `channel_to_emitter_params()` per the
  version-bump rule above.

## Where this contract lives

- This file: discipline + channel mappings.
- [`STANDARDS.md`](STANDARDS.md): file layout, resolution, fps,
  compression — the technical envelope this discipline operates within.
- [`particle_renderer.py`](particle_renderer.py): the executable spec.
- [`mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md`](../../../mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md):
  the EXR channel layout (what gets *packed*; this doc says what gets
  *rendered* and how).
- Every sibling repo's CLAUDE.md links here. The discipline is
  cross-repo.

## What "the water MPA swims in" means

The rendering discipline is not a feature of one tool. It is the
substrate every visualization in the MPA suite operates in. A new
session opening any repo inherits this discipline through the
CLAUDE.md pointers — it does not need to be re-decided per session,
per shot, or per substrate.

If a future addition would violate either rule, the addition does not
land; the discipline does not bend. *The water doesn't change because
a new fish swims in it.*
