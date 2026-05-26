# queue_load_sweep_v12 — BLIND ANSWERER VERDICT (as returned)

phase: DEV/blind · view: `view_20260526-020751.png` · analysis: `answer.py`

**In balance at every load. No breakdown. The queue near capacity is slower-and-noisier-but-fine,
not stuck.** Method: each load placed as an independent single-point fit first, then the band.

## placement (the numbers)

| level | util_rel | C(0) (fluct size) | τ_relax (C=C0/e) | FDR slope X | χ∞/C0 | C shape |
|---|---|---|---|---|---|---|
| 0 | 1.0× | 3.75 | 19.7 | 1.0000 | 0.99999 | single monotone decay |
| 1 | 2.67× | 20.0 | 89.9 | 1.0000 | 0.99999 | single monotone decay |
| 2 | 6.0× | 90.0 | 380 | 1.0000 | 0.99999 | single monotone decay |
| 3 | 12.67× | 380 | 1562 | 1.0000 | 0.99999 | single monotone decay |
| 4 | 32.67× | 2450 | 9915 | 1.0000 | 0.99999 | single monotone decay |

**Band:** the FDR locus (χ vs C0−C) is a single straight line through the origin of slope 1 at every
load — max|locus − y=x|/C0 < 3×10⁻⁸, early- and late-segment slopes BOTH 1 (no shallow tail, never
bends). Meanwhile C(0) grows **653×** (log-log slope ≈1.86 vs util_rel) and τ_relax grows **503×**
(log-log slope ≈1.79). C is a single monotone relaxation to zero at every level — no plateau/shoulder
(not two-step/glassy), no negative excursion (no oscillation/current).

## verdict in the researcher's terms
1. **Response matched to fluctuations at each load?** Yes — at every load incl. the heaviest. X=1 (FDT
   holds exactly); the response stays in proportion to the queue's own fluctuations. Nothing falls out
   of balance.
2. **What diverges toward the limit?** Both the timescale (critical slowing, ~500×) and the fluctuation
   size (line-length variance, ~650×) diverge together as steep power laws in the relative load. But
   balance does not — the divergence is of a system that stays reversible/in-balance. "Slower-and-
   noisier-but-fine," not a tip into a stuck/aging state. The breakdown flag (a bent FDR locus, X<1)
   does not happen.
3. **How close to the limit?** Level 4 is the closest of the five; nothing pathological at it. Native
   distance to the limit is not in the data (see below).

## grounded[]
- in balance at every load ← FDR locus single straight slope-1 line through origin at all 5 levels; χ∞/C0=1.0000 (X=1)
- no aging/bending ← early- and late-segment FDR slopes both = 1 at every level; locus never bends
- fluctuation size diverges ← C(0): 3.75→2450 (≈653×), log-log slope ≈1.86 vs util_rel
- timescale diverges (critical slowing) ← τ_relax: 19.7→9915 (≈503×), log-log slope ≈1.79 vs util_rel
- simple reversible relaxation, not glassy ← C single monotone decay to 0; no plateau, no negative excursion
- slower-and-noisier-but-fine, not breakdown ← the breakdown invariant (FDR slope X) stays pinned at 1; only the diverging parameterizations (timescale, amplitude) blow up

## not_grounded[] (the honest limits — findings)
- native utilization / arrival & service rates (only relative util_rel given; no native distance-to-capacity)
- divergence exponent in NATIVE load units (the ~1.8–1.9 power laws are vs util_rel, not vs (1−ρ); the true critical exponent + singularity location not recoverable)
- behaviour exactly at the capacity limit (heaviest point still interior; no point at/past the limit)
- one-sided headroom as a native number (only "closest of the five, nothing pathological")
- behaviour past each τ window (curves truncated where C≈0; a slower second process not excludable)
- true critical point vs smooth steep blow-up (5 points fit a power law but can't distinguish a finite-load singularity from monotone steepening)

Blinding held: only the four permitted files read. **Self-graded MATCH.**
