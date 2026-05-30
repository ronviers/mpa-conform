# Character deformation-apparatus — construction log (session 2026-05-29)

A record of how the middle of character got fitted with parts: each piece of apparatus, what it
tested, what it found (with numbers), the corrections made along the way (kept in — they are the
integrity), and the established home each result landed on. Chronological. Scripts under
`mpa-conform/scripts/`, figures under `mpa-conform/output/calibration/`. Stops at the apparatus
culmination; the conceptual synthesis that followed is deliberately out of scope here.

Operating point throughout: base triad `M = −γI + g·A_CYC`, γ=1, g=0.6 (so ω₀=√3·g≈1.039),
meta-coupling κ=0.3, noise D=0.1 — the `banach_frustrated` reference point.

---

## Part 0 — the baton

`frustration-ascent` arrived at calibration grade: the b₁-growth leg instanced
(`frustration_ascent.py`: +1 protected cycle per frustrated ascent, reciprocal-bond kill clean) but
*fitted* — the meta-frustration A_CYC was hand-drawn each level. The chaos legs had returned honest
pushbacks, not chaos. The reframe carried in: a **forced-not-fitted** derivation (a meta-triad that
*emerges* rather than being drawn) would convert the test from calibration to vindication-capable.

## Part 1 — the chiral-bonding spec, corrected

The handoff's first spec was self-contradictory ("balanced blocks + bond their chiral modes" — a
balanced block has no chiral mode). Resolved: **internally-frustrated (chiral) sub-triads** (the
seed) + a **provably even-parity (symmetric)** meta-coupling (the part forbidden to frustrate).
Forced route: Schur-complement elimination of the chiral sub-modes hands the collective meta-triad
an antisymmetric `M_eff ∝ sub-chirality`, because R⁻¹ carries an antisymmetric `−ωJ/(γ²+ω²)` piece.
Certifier: the meta-coupling is provably symmetric (not "blocks balanced"). Teeth: the emergent
cycle must survive drive-titration sign-invariant (a drive-set rotation is a kill).

## Part 2 — `chiral_bonding.py`: the conditional bootstrap

First run: **total kill** — 0% seeding, including a 64-draw random ensemble. The clean zero was the
tell: a *uniform* even-parity coupling (same bond on every edge) forces `wJwᵀ ≡ 0` — a structural
cancellation (same in/out rotating direction). Correction: **pair-distinguishable** even-parity
bonds (each still symmetric) *do* seed — `b₁(M_eff): 0→1`, ω_meta=0.0118; micro spectrum 3→4 pairs
(a genuine new slow pair at ω≈0.030).

The finding that held: **sub-chirality always propagates to the coarse description** — antisym
`M_eff` ≠ 0, forced, tracking the closed form `√3·g/(γ²+3g²)` (corr 0.93), → 0 as g→0 (the
no-creation-from-balance certifier). **But it closes a *protected* cycle only when a collective
degeneracy is symmetry-protected:** the seed enters at **O(κ²)**, a generic even-parity coupling
splits the collective levels at **O(κ)** ≫ seed. Three regimes, all verified: C3-covariant (seeds),
C3-invariant uniform (`wJwᵀ=0`, no propagation), generic C3-broken (propagates but ~2% close — the
degeneracy split overwhelms the seed). Degeneracy-gating confirmed directly: break the doublet by ε,
the cycle dies when the gap crosses the O(κ²) seed.

**Correction (integrity):** the chirality sign was first read from `sign(Im λ)` of `M_eff` — wrong,
because complex eigenvalues are conjugate pairs (±i|Im|), so that read numpy's ordering, not
chirality. Fixed to `sign(axial(antisym M_eff)·(1,1,1))` — which flips correctly with the subs.

## Part 3 — `chiral_selffield.py`: the chimeric normal as self-field

Generic fact used: for any 3×3 antisymmetric matrix the axial vector (rotation axis) **is** the
kernel = the real eigenvector. So the triad's `(1,1,1)` is at once the collective mode (polar) and
the chirality axis (axial) — one direction, two natures. Used the ensemble mean of these normals as
a self-consistent mean field (`ṡₖ = K⟨s⟩ − c·sₖ − sₖ³`, reflection-symmetric → no drawn direction).
Result: above a **Curie threshold K_c=c** the symmetric state goes unstable and the subs
spontaneously commit to one handedness (200-IC ensemble +54%/−45% — no bias), and that self-lit
state closes the meta-cycle — orientation and cycle ignite together at the threshold. Established the
**arena-vs-orientation split:** parasitic on a substrate-supplied symmetric *arena*; generative of
the field's *orientation*. Honest scope flagged: the self-field is posited (φ⁴ mean-field), not
derived; the normal's axis is frozen (1-D handedness, not S²).

## Part 4 — `chiral_tilt.py`: tilting the normal until it breaks

Pre-registered prediction before running: symmetric (cone) tilt robust; asymmetric (generic) tilt
brittle, breaking at θ_c ≈ seed/κ ≈ 4°, with θ_c ∝ κ. Result: **asymmetric (generic) tilt is brittle
— true death at ~9°** (≈2× my estimate, within the stated hedge) **and stays dead**; the symmetric
cone **survives the range** but passes through a **sign-reversing node at ~39°** (the collective gap
stays 0 to machine precision — degeneracy preserved — and the induced chirality flips −→+ then
revives). **θ_c ∝ κ confirmed** (weaker coupling more brittle). Mechanism = the degeneracy-gating
of Part 2, in tilt language: a symmetry-breaking tilt splits the doublet at O(κθ), the cycle dies
when that gap crosses the O(κ²) seed.

**Correction (integrity):** the first detector flagged the 39° node as a "break"; a `true_break`
detector (stays dead vs revives) distinguished the genuine asymmetric death from the symmetric
sign-flip node. The node is a glimpse of geometric (Berry-like) handedness winding.

## Part 5 — `tilt_rescue.py`: the fail angle, ground precise; the pull-rescue

θ_c is a **direction-dependent band**, not a point (brittleness is anisotropic). Generic ensemble
(n≈370, κ=0.3): **worst-case 5.8°, median 9.8°, 90th pct 25°**. The reusable number: a stream
survives any generic normal-tilt up to ~5.8° at κ=0.3, scaling ∝κ. **Pull rescue:** θ_c ≈ 33°·κ
(representative direction), linear — doubling the downstream coupling doubles the survivable tilt;
a stream parked past death at base κ is **pulled back to life once κ ≳ θ/33°** (demo: a 13° stream
revives at κ≥0.42). 2-D (θ,κ) phase map produced.

**Correction (integrity):** a "single-sub" canonical θ_c was azimuth-noisy (16°±14°) — demoted; the
generic ensemble + a fixed representative direction used instead.

## Part 6 — framework edits (frontier)

`frustration-ascent` moved steeping→sharpening with a rewritten verdict (conditional bootstrap;
forced-not-fitted but symmetry-gated; brittle to tilt), **superseding** the old over-claim
("balanced cluster ejects current upward / parasitic→generative / stop living downstream").
`wall-as-type-boundary` sharpened with the Curie ignition-Wall + the holonomy node. Held in the
working tree for review.

## Part 7 — `establishment_compare.py`: our numbers ON the closed forms

After the outbound research returned the literature map, each finding was verified against the
canonical closed form:

- **Exceptional point (non-Hermitian):** ω² = Γ² − (δ/2)² — regress ω² on δ²: **R²=1.0000**, slope
  −0.253 (predicted −¼), intercept = Γ² exactly; onset exponent 0.48 (≈½). The tilt-death *is* an EP
  collision at δ=2Γ. Home: `nonhermitian-ep`.
- **Arnold tongue / Adler:** the pull-rescue θ_c ∝ κ is the linear locking-range boundary. Home:
  `adler-locking` (added to prior-art; Adler 1946 / Pikovsky–Rosenblum–Kurths).
- **Pitchfork / Curie:** the self-field K_c=c and order-parameter √(K−K_c) are the mean-field
  pitchfork with exponent β=½. Home: `bifurcation-normal-forms`, `frank-autocatalysis`, `kondepudi`.
- **Reservoir-induced non-reciprocity:** the Schur antisym √3·g/(γ²+3g²) is the canonical g/ω_f form
  × the √3 geometric factor (corr 0.933 with the closed form). Home: `nonreciprocal-transition`
  (Fruchart–Vitelli), `slaving`, `mz-projection`.
- **Open cell:** the ~39° symmetric-cone node is **model-specific** — Berry would predict 60°
  (Ω=2π(1−cosθ)=π); it matched neither 60° nor the magic angle 54.7°.

Net: the recursion apparatus reads as a *composition/instance of already-imported results*; only
`adler-locking` was a genuinely new import. MPA added no new object — the reading.

## Part 8 — `character_primitives.py`: the generator basis

Enumerated the elementary deformations of the triad and computed each one's normal/coupling-pull
response, allowing sign flips and sampling topological basins. Pre-registered predictions — **all
held:** damping (no flip, trivial); chirality-through-zero (sign-flip locus at g=0); splitting
(EP, no flip); anisotropic drive (drift sign fixed); tilt (EP + node); coupling (Arnold rescue).
**Two genuinely new sign-flip channels, both Z2:** the self-field SSB Z2 (2 basins, 50/50) and the
**rotating-squeeze parametric Z2** (principal Floquet tongue at Ω=2ω₀, critical squeeze a_c=1.037≈γ).
Three kills clean (balanced subs / uniform coupling / isotropic Q).

**Correction (integrity):** the squeeze basin detector first read phase **mod π** and reported 1
basin — wrong, because the two parametric basins are the state `u` and `−u` (phases π apart), which
are identical mod π; the detector was collapsing the Z2 it was built to find. Fixed to a sign /
mod-2π readout → 2 clusters exactly π apart. (`weak` and `strong` modes; strong = dense Floquet
tongue + ε-swept secondary tongues + basin maps + node map, ~hundreds of PNGs.)

## Part 9 — `squeeze_dynamics.py`: the rotating squeeze, after two wrong model classes

Three predictions were on the table for the rotating non-uniform squeeze: (a) precipitous falloff in
chimeric circulation; (b) mean amplitude constant while internal rate varies; (c) swirls → bursty
"mysterious fluctuations." Getting there required correcting the model class **twice**:

- **Dissipative parametric squeeze** (a·e^{iΩt}z̄ − γ): wrong — amplitude *grows* at threshold, rate
  stays ≈ω₀. Only confirmed (c), via a 28-line sideband comb.
- **Conservative parametric squeeze** at Ω=2ω₀: wrong — hyperbolic for any s₀>0; no bounded regime.
- **Correction:** "constant amplitude, varying rate" is unambiguously a **phase** deformation, not
  an amplitude one → the **Adler phase oscillator** (φ̇ = ω₀ − K·f(φ−Ωt); |z|=1 by construction).

On the phase model all three held: **(a)** relative winding = √(Δ²−K²) → precipitously 0 at the
phase-locking threshold K=Δ (SNIC cliff; corr 1.000 with the closed form); **(b)** amplitude CV=0,
internal-rate CV=0.24 (the treadmill); **(c)** near lock the phase creeps through a bottleneck then
slips — type-I (SNIC) intermittency (rate kurtosis 9.2) + a devil's staircase of p:q lockings = the
deterministic "mysterious fluctuations." Home: `adler-locking` / Arnold tongue / circle map / SNIC —
the same family as the coupling-pull, now in the phase channel.

**Correction (integrity):** the (b)/(c) regime was first set with ε=0.5, which pushed K into a
locking tongue (phase locked → rate CV and burstiness both 0); fixed by selecting the unlocked,
near-threshold regime (clean Adler, K just below Δ).

---

## Where this leaves the apparatus

Seven runnable specs now characterize the deformation generators of the triad and their forced
responses, each landing on an established universal form (exceptional point, Adler/Arnold tongue,
pitchfork, reservoir non-reciprocity, Floquet/Mathieu parametric, NESS currents), with the
correspondence verified on synthetic data (the EP square-root law at R²=1.0000) and the receipts in
prior-art. Two model-class corrections and three detector-bug corrections were made and kept in the
record. Two cells remain model-specific / open (the ~39° tilt node; the non-uniform-squeeze
secondary-tongue structure). The structural deformation-algebra this assembles is the object the
`battery:character-primitives` spec proposes to derive toward engine promotion
(`mpa-atlas/docs/battery_character_primitives.md`).

**Part C landed (same session, synthesis — see `mpa-atlas/docs/character_closure_derivation.md`,
`scripts/character_closure.py`):** the linear deformation space is **gl(3,ℝ)**, Cartan-decomposed
into damping (ℝ·I) ⊕ chirality (so(3)) ⊕ splitting (Sym₀) — exhaustive (1+3+5=9) and closed (bracket
residual 3·10⁻¹⁶); closure is **autonomous** (no symmetry required), so the protecting symmetry is a
substrate boundary condition (strict-K3, route (b)) that suppresses the O(κ) Sym₀ channel — verified
ω_meta∝κ^1.94 (covariant, cycle lives) vs real-split∝κ^1.00 (generic, cycle killed); the protected
lift is the complex branch of the same 2×2 normal form whose other branch is the EP (R²=1.0000).
