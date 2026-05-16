# Asymptotic closure — v9 candidate

A structural commitment in MPA: **no framework-prediction observable
attains exact 0 or 1 at a non-asymptotic operating point.**

Verified by audit across v9 + cdv1. 16 candidates checked; no
counterexample. Falsifiable in principle (find a counterexample);
unfalsifiable in practice (the only conceivable falsifier lives at the
asymptotic boundary of cosmological time).

Target home: `v9_compressed.md` §Asymptotic closure +
`v9_receipts.md` §Asymptotic closure. Thin-RFC discipline applies.

---

## The principle

Every framework-prediction observable in MPA takes values in an open
interval whose boundaries are 0, 1, or ∞. No prediction attains these
boundary values exactly at any non-asymptotic operating point. Boundary
values exist only as limits:

- `M_2` at `D → ∞`
- `ε → 1` at the Complexity Wall
- `chit = 0` as critical limit
- `X_c → 0` in deep `c`
- `X_r → 1` in deep `r` (and at thermodynamic equilibrium)
- `u_n → 1` at Cobham blocking
- `η → 0` at the Hopfield ceiling
- `β_mem → 1` at the Markovian limit

Categorical labels (`⊤`, `⊥`, `k_frust`) exist only at the `M_2`
boundary or as discrete derivatives of continuous parameters with the
boundary itself ill-defined (`k_frust` singular at `γ_AB → 0`).

---

## Survey

| Candidate | Source | Resolution |
|---|---|---|
| `X_c = 0` | cdv1 §gFDR table | Asymptotic (`X_c ≪ 1` in compressed text) |
| `X_r = 1` | cdv1 §gFDR table | Asymptotic (equilibrium limit; never reached in finite time) |
| `ε < 1` | v9 Banach contraction | Asymptotic at both ends (Complexity Wall as `ε → 1`; `ε → 0` perfect compression) |
| `chit = 0` | cdv1 §chit unit | Asymptotic (explicit "*critical limit, not an attainable operating state*") |
| `u_n = 1` | cdv1 Cobham | Asymptotic (Cobham wait diverges as `u → 1`) |
| `η = 1` at `ρ = 0` | v9 §Capacity Erlang-B | Edge case: `ρ = 0` (no demand) itself asymptotic for any real substrate |
| `η → 0` at Hopfield ceiling | v9 §Capacity | Asymptotic (open lower bound) |
| `γ_AB ≈ 0` (orthogonal) | v9 §Three typed objects | Asymptotic (explicit `≈`) |
| `c committed ≈ 1`, `r reset ≈ 0` | v9 §Three typed objects | Asymptotic (explicit `≈`) |
| `β_mem = 1` (Markovian) | cdv1 §Universal two-mode kernel | Asymptotic in framework; implementation conventions may snap |
| `D → ∞` Boolean limit | v9 §Setting | Asymptotic (explicit limit) |
| `⊤`, `⊥` Boolean operators | v9 §Boolean section | Exist only at `M_2` boundary (asymptotic) |
| `λ_A = 0` at threshold | cdv1 §Bridge to v9 | Asymptotic (same limit as `chit = 0`) |
| `N` persistence depth (integer) | v9 §Compression Axiom | Discrete snapshot of continuous flow `ν` |
| `χ(0)/χ(0) = 1` | normalization at `τ = 0` | Normalization convention, not framework prediction |
| `k_frust` Boolean | v9 §Three typed objects | Categorical, singular at `γ_AB → 0` |

No counterexample found across the audit.

---

## Falsifier

A framework-prediction observable shown to attain exactly 0 or 1 at a
finite, non-degenerate operating point. The only conceivable instance is
the exact equilibrium of cosmic heat death — where equilibrium FDR
predicts `X_r = 1` exactly. Standard cosmology places heat death at
`t → ∞`, never exactly reached, so the falsifier is itself asymptotic.
MPA is therefore falsifiable in principle and unfalsifiable in practice
within cosmic time: the framework's continuous-physics identity is
preserved by the universe's own continuous-time structure.

---

## Paste-ready: `v9_compressed.md`

**Insert after `§Compression Axiom`, before `§Capacity`.**

```markdown
## Asymptotic closure

Every framework-prediction observable in MPA takes values in an open interval whose boundaries are 0, 1, or $\infty$. No prediction attains 0, 1, or $\infty$ exactly at any non-asymptotic operating point. Boundary values exist only as limits: $\mathcal{M}_2$ at $D \to \infty$; $\varepsilon \to 1$ at the Complexity Wall; $\text{chit} = 0$ as critical limit; $X_c \to 0$ in deep $c$; $X_r \to 1$ in deep $r$ (and at thermodynamic equilibrium); $u_n \to 1$ at Cobham blocking; $\eta \to 0$ at the Hopfield ceiling; $\beta_{\text{mem}} \to 1$ at the Markovian limit. Categorical labels ($\top$, $\bot$, $k_{\text{frust}}$) exist only at the $\mathcal{M}_2$ boundary or as discrete derivatives of continuous parameters with the boundary itself ill-defined ($k_{\text{frust}}$ singular at $\gamma_{AB} \to 0$).

**Falsifier.** A framework-prediction observable shown to attain exactly 0 or 1 at a finite, non-degenerate operating point. The only conceivable instance is the exact equilibrium of cosmic heat death — where equilibrium FDR predicts $X_r = 1$ exactly. Standard cosmology places heat death at $t \to \infty$, never exactly reached, so the falsifier is itself asymptotic. MPA is therefore falsifiable in principle and unfalsifiable in practice within cosmic time: the framework's continuous-physics identity is preserved by the universe's own continuous-time structure.

**Reading.** MPA is a continuous-physics framework. The structural commitment that boundary values are asymptotic-only is what makes the framework continuous across observables, not just within any one. Falsification routes through any observable whose predicted value can be shown to attain 0 or 1 (or $\infty$) at a finite, non-degenerate operating point.
```

---

## `v9_receipts.md` — already landed

The §Asymptotic closure entry is already in `v9_receipts.md` (lines
62–65 as of 2026-05-16). Content matches what was drafted. **One stale
file pointer to fix:** the entry's final sentence references
`mpa-conform/docs/banach-substrate-proposal.md` as the survey-table
archive, but that file was removed in the suite reframe. Replace with
`mpa-conform/docs/asymptotic-closure-proposal.md` (this file — survey
is in §Survey above).

One-line patch:

```
- Survey table archived at `mpa-conform/docs/banach-substrate-proposal.md` addendum.
+ Survey table archived at `mpa-conform/docs/asymptotic-closure-proposal.md` §Survey.
```

---

## `cdv1_receipts.md`

No entry needed. cdv1 compressed already carries the principle's
strongest local instances directly in the text (§The chit unit's
"limit-point status" sentence; §gFDR signatures' per-regime asymptotic
framing; §Universal two-mode kernel's `β_mem → 1` boundary). The v9
receipts entry's cite list reaches into these cdv1 sections; the
pointer flows naturally.

---

## `v9_unabridged.md`

Per the operational discipline at the top of `v9_unabridged.md`, the
unabridged catches up on its own cadence from the compressed source.
The compressed-side addition propagates to the unabridged at the next
refresh.

---

## Suggested follow-up

When the v9 receipts entry lands, surface a one-line cross-reference
from `cdv1_receipts.md` §Universal two-mode kernel pointing at the v9
entry — so the cdv1-side reader finds the framework-wide structural
identity from the cdv1-side instance.
