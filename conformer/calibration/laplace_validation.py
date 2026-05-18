"""laplace_validation.py — Laplace-width confidence: sigma = 1/sqrt(d^2 S / dchit^2)

Computed at the already-found fit_chit from the tier 1 bootstrap parquet.
The score function is the same gFDR locus residual that the solver paths
already use; we evaluate it at chit +/- delta directly (NOT through the
solver), which is exactly why this bypasses the solver constraints that
killed the bootstrap.

Single-threaded by design: ~3 score evals per cell across ~1,000 cells is
a few thousand evals total. Process-pool overhead would dominate.

Primary validation test: does Laplace sigma increase monotonically with
noise intensity within each (substrate, path, noise_model) stratum? If
yes, sigma measures data informativeness in a calibration-free way.

Secondary test: does sigma correlate with gt_error on the rare cells
where gt_error > 0? (Tier 1 had 19 such cells out of 1,095.)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


LIBRARY_ROOT = Path("H:/mpa-central/library/data")
DEFAULT_DELTA = 0.05
HESSIAN_FLOOR = 1e-8

# Polish wrapper: scipy minimize_scalar in [fit_chit - W, fit_chit + W],
# converges grid-snapped / bracketed fits to true continuous-space minima
# so the Laplace approximation applies. W is tight enough to not cross
# regime boundaries (~0.3 half-width).
POLISH_BRACKET_HALFWIDTH = 0.1
POLISH_XATOL = 1e-6


# --- score-function dispatch --------------------------------------------

def _score_two_stage(rows: list[dict], chit: float) -> float:
    from conformer.compute import gfdr_model
    return float(gfdr_model.locus_residual(rows, float(chit)))


def _score_lens_solver(rows: list[dict], chit: float) -> float:
    from mpa_scale_solver.gfdr_model import locus_residual
    return float(locus_residual(rows, float(chit)))


_SCORE_FN: dict[str, Callable[[list[dict], float], float]] = {
    "two_stage_inversion": _score_two_stage,
    "lens_solver_prior": _score_lens_solver,
    "lens_solver_bootstrap": _score_lens_solver,
}


# --- cell + noise reapplication (must match sweep.py exactly) ----------

def _cell_rows(cell: dict) -> list[dict]:
    samples = cell.get("results", {}).get("all_samples", [])
    rows = []
    for s in samples:
        tau, C, chi = s.get("t"), s.get("C_mean"), s.get("chi_mean")
        if tau is None or C is None or chi is None:
            continue
        rows.append({"tau": float(tau), "C": float(C), "chi": float(chi)})
    return rows


def _per_cell_noise_seed(substrate: str, path: str, noise_model: str,
                         intensity: float, seed_idx: int, cell_id: str,
                         cfg_seed: int = 0) -> int:
    """Matches sweep.py::_per_cell_noise_seed and
    bootstrap_validation.py::_per_cell_noise_seed."""
    return abs(hash((
        substrate, path, noise_model,
        float(intensity), int(seed_idx), cell_id, int(cfg_seed),
    ))) % (2**31 - 1)


# --- Hessian -----------------------------------------------------------

@dataclass(frozen=True)
class LaplaceOutcome:
    substrate: str
    path: str
    noise_model: str
    intensity: float
    seed_idx: int
    cell_id: str
    fit_chit: float
    polished_chit: Optional[float]
    polish_drift: Optional[float]      # |polished - fit_chit|
    gt_error: Optional[float]
    S_center: Optional[float]
    S_plus: Optional[float]
    S_minus: Optional[float]
    hessian: Optional[float]
    laplace_sigma: Optional[float]
    status: str
    error_msg: str = ""


def _polish(rows: list[dict], fit_chit: float, score_fn: Callable,
            halfwidth: float = POLISH_BRACKET_HALFWIDTH,
            xatol: float = POLISH_XATOL) -> tuple[float, bool]:
    """Converge fit_chit to the local continuous-space minimum of score_fn
    within [fit_chit +/- halfwidth]. Returns (polished_chit, converged).
    Does nothing if scipy.optimize fails — returns fit_chit unchanged."""
    try:
        from scipy.optimize import minimize_scalar
        lo, hi = fit_chit - halfwidth, fit_chit + halfwidth
        result = minimize_scalar(
            lambda c: score_fn(rows, float(c)),
            method="bounded",
            bounds=(lo, hi),
            options={"xatol": xatol},
        )
        if not result.success:
            return float(fit_chit), False
        return float(result.x), True
    except Exception:
        return float(fit_chit), False


def _laplace_sigma(rows: list[dict], fit_chit: float, score_fn: Callable,
                   delta: float = DEFAULT_DELTA) -> tuple[float, float, float, float, float, str]:
    """Central-difference Hessian + Laplace sigma. Returns
    (S_center, S_plus, S_minus, hessian, sigma, status)."""
    try:
        S0 = score_fn(rows, fit_chit)
        Sp = score_fn(rows, fit_chit + delta)
        Sm = score_fn(rows, fit_chit - delta)
    except Exception as e:
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), f"score_eval_error:{e}"

    if not (np.isfinite(S0) and np.isfinite(Sp) and np.isfinite(Sm)):
        return S0, Sp, Sm, float("nan"), float("nan"), "non_finite_score"

    hessian = (Sp - 2.0 * S0 + Sm) / (delta * delta)

    if not np.isfinite(hessian):
        return S0, Sp, Sm, hessian, float("nan"), "non_finite_hessian"
    if hessian <= HESSIAN_FLOOR:
        # Flat or inverted landscape. Negative hessian means we're at a
        # saddle/max, not a minimum — the solver may have ended up off the
        # true minimum, or the landscape genuinely flattens (s-regime).
        if hessian < 0:
            return S0, Sp, Sm, hessian, float("inf"), "negative_hessian"
        return S0, Sp, Sm, hessian, float("inf"), "flat_landscape"

    sigma = 1.0 / float(np.sqrt(hessian))
    return S0, Sp, Sm, float(hessian), float(sigma), "ok"


def _compute_one(row: pd.Series, delta: float, cfg_seed: int = 0) -> LaplaceOutcome:
    substrate = row["substrate"]
    path = row["path"]
    noise_model = row["noise_model"]
    intensity = float(row["intensity"])
    seed_idx = int(row["seed_idx"])
    cell_id = row["cell_id"]
    fit_chit = float(row["central_chit"]) if pd.notna(row["central_chit"]) else None
    gt_error = float(row["gt_error"]) if pd.notna(row["gt_error"]) else None

    if fit_chit is None:
        return LaplaceOutcome(
            substrate=substrate, path=path, noise_model=noise_model,
            intensity=intensity, seed_idx=seed_idx, cell_id=cell_id,
            fit_chit=float("nan"),
            polished_chit=None, polish_drift=None,
            gt_error=gt_error,
            S_center=None, S_plus=None, S_minus=None,
            hessian=None, laplace_sigma=None,
            status="no_fit_chit", error_msg="parquet had no central_chit",
        )

    try:
        from conformer.calibration.noise_models import NOISE_MODELS

        cell_path = LIBRARY_ROOT / substrate / f"{cell_id}.json"
        cell = json.loads(cell_path.read_text(encoding="utf-8"))
        clean_rows = _cell_rows(cell)
        if len(clean_rows) < 2:
            return LaplaceOutcome(
                substrate=substrate, path=path, noise_model=noise_model,
                intensity=intensity, seed_idx=seed_idx, cell_id=cell_id,
                fit_chit=fit_chit, gt_error=gt_error,
                S_center=None, S_plus=None, S_minus=None,
                hessian=None, laplace_sigma=None,
                status="empty_clean_rows",
            )

        noise_fn = NOISE_MODELS[noise_model]
        noise_seed = _per_cell_noise_seed(
            substrate, path, noise_model, intensity, seed_idx, cell_id, cfg_seed,
        )
        noisy_rows = noise_fn(clean_rows, intensity, noise_seed)
        if len(noisy_rows) < 2:
            return LaplaceOutcome(
                substrate=substrate, path=path, noise_model=noise_model,
                intensity=intensity, seed_idx=seed_idx, cell_id=cell_id,
                fit_chit=fit_chit,
                polished_chit=None, polish_drift=None,
                gt_error=gt_error,
                S_center=None, S_plus=None, S_minus=None,
                hessian=None, laplace_sigma=None,
                status="empty_noisy_rows",
            )

        score_fn = _SCORE_FN[path]
        # Polish: converge solver's fit_chit to true continuous minimum of S
        # in a tight bracket around it. Required for Hessian to be positive.
        polished_chit, _polished_ok = _polish(noisy_rows, fit_chit, score_fn)
        drift = float(abs(polished_chit - fit_chit))

        S0, Sp, Sm, hess, sigma, status = _laplace_sigma(
            noisy_rows, polished_chit, score_fn, delta=delta,
        )
        return LaplaceOutcome(
            substrate=substrate, path=path, noise_model=noise_model,
            intensity=intensity, seed_idx=seed_idx, cell_id=cell_id,
            fit_chit=fit_chit,
            polished_chit=polished_chit, polish_drift=drift,
            gt_error=gt_error,
            S_center=S0, S_plus=Sp, S_minus=Sm,
            hessian=hess, laplace_sigma=sigma,
            status=status,
        )
    except Exception as e:
        import traceback
        return LaplaceOutcome(
            substrate=substrate, path=path, noise_model=noise_model,
            intensity=intensity, seed_idx=seed_idx, cell_id=cell_id,
            fit_chit=fit_chit,
            polished_chit=None, polish_drift=None,
            gt_error=gt_error,
            S_center=None, S_plus=None, S_minus=None,
            hessian=None, laplace_sigma=None,
            status="error", error_msg=f"{type(e).__name__}: {e}\n{traceback.format_exc()[:300]}",
        )


# --- top-level: validation against a tier-N bootstrap parquet ------------

def run_validation(bootstrap_parquet: Path, output_dir: Path,
                   delta: float = DEFAULT_DELTA) -> Path:
    df = pd.read_parquet(bootstrap_parquet)
    df = df[df["status"] == "ok"].copy()
    print(f"loaded {len(df)} ok rows from {bootstrap_parquet}")

    t0 = time.perf_counter()
    outcomes = [_compute_one(r, delta=delta) for _, r in df.iterrows()]
    elapsed = time.perf_counter() - t0
    print(f"computed {len(outcomes)} Laplace sigmas in {elapsed:.1f}s")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([asdict(o) for o in outcomes])
    out_df.to_parquet(output_dir / "laplace.parquet")

    _report(out_df, output_dir, delta)
    return output_dir / "laplace.parquet"


def _report(df: pd.DataFrame, out_dir: Path, delta: float) -> None:
    lines: list[str] = []
    lines.append(f"# Laplace-width validation (delta = {delta})\n")
    lines.append(f"Run: {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"Total: {len(df)}\n")

    lines.append("## Status sanity\n")
    lines.append("| status | count |")
    lines.append("|---|---|")
    for k, v in df["status"].value_counts().items():
        lines.append(f"| {k} | {int(v)} |")
    lines.append("")

    # Polish drift summary
    pd_drift = df["polish_drift"].dropna()
    if not pd_drift.empty:
        lines.append("## Polish drift (how far the wrapper moved the solver's fit_chit)\n")
        lines.append("| stat | value |")
        lines.append("|---|---|")
        lines.append(f"| n | {len(pd_drift)} |")
        lines.append(f"| median drift | {float(pd_drift.median()):.5f} |")
        lines.append(f"| p90 drift | {float(pd_drift.quantile(0.9)):.5f} |")
        lines.append(f"| p99 drift | {float(pd_drift.quantile(0.99)):.5f} |")
        lines.append(f"| max drift | {float(pd_drift.max()):.5f} |")
        lines.append(f"| %drift > 0.025 (grid step) | {100.0 * (pd_drift > 0.025).mean():.1f}% |")
        lines.append("")

    ok = df[df["status"] == "ok"].copy()
    if len(ok) == 0:
        lines.append("**No ok rows. Validation cannot proceed.**\n")
        (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
        return

    # Primary test: sigma vs intensity per (substrate, path, noise_model)
    lines.append("## PRIMARY TEST: sigma vs noise intensity (Spearman rank correlation)\n")
    lines.append("Spearman > 0 means sigma increases monotonically with noise. "
                 "Values near +1 = clean monotone relationship; near 0 = no relationship; "
                 "negative = sigma decreases with noise (would be a failure).\n")
    lines.append("| substrate | path | noise_model | n | sigma_median | spearman_vs_intensity |")
    lines.append("|---|---|---|---|---|---|")
    primary_summary: list[tuple[str, str, str, float]] = []
    for (sub, path, nm), grp in ok.groupby(["substrate", "path", "noise_model"]):
        n = len(grp)
        if n < 8:
            lines.append(f"| {sub} | {path} | {nm} | {n} | — | — |")
            continue
        sig_median = float(grp["laplace_sigma"].median())
        # Spearman (rank-based, robust to outliers)
        sr = grp[["intensity", "laplace_sigma"]].dropna()
        sr = sr.replace([np.inf, -np.inf], np.nan).dropna()
        if len(sr) < 8:
            lines.append(f"| {sub} | {path} | {nm} | {n} | {sig_median:.4f} | — (too few finite) |")
            continue
        spearman = sr["intensity"].corr(sr["laplace_sigma"], method="spearman")
        primary_summary.append((sub, path, nm, float(spearman)))
        lines.append(f"| {sub} | {path} | {nm} | {n} | {sig_median:.4f} | {spearman:.3f} |")
    lines.append("")

    # Aggregate by path
    lines.append("## PRIMARY headline: Spearman per path (aggregated over substrate x noise_model)\n")
    lines.append("| path | n_strata | mean_spearman | min_spearman | max_spearman |")
    lines.append("|---|---|---|---|---|")
    if primary_summary:
        df_p = pd.DataFrame(primary_summary, columns=["substrate", "path", "noise_model", "spearman"])
        for path, pg in df_p.groupby("path"):
            spvals = pg["spearman"].dropna()
            if spvals.empty:
                lines.append(f"| {path} | 0 | — | — | — |")
                continue
            lines.append(f"| {path} | {len(spvals)} | {spvals.mean():.3f} | {spvals.min():.3f} | {spvals.max():.3f} |")
    lines.append("")

    # Secondary test: sigma vs gt_error on movers only
    lines.append("## SECONDARY: sigma vs gt_error (only cells where gt_error > 0.01)\n")
    movers = ok[ok["gt_error"].fillna(0) > 0.01].copy()
    lines.append(f"Movers: {len(movers)} of {len(ok)} cells had gt_error > 0.01.\n")
    if len(movers) >= 5:
        lines.append("| path | n_movers | corr(sigma, gt_error) |")
        lines.append("|---|---|---|")
        for path, pg in movers.groupby("path"):
            n = len(pg)
            if n < 3:
                lines.append(f"| {path} | {n} | — |")
                continue
            valid = pg.replace([np.inf, -np.inf], np.nan).dropna(subset=["laplace_sigma", "gt_error"])
            if len(valid) < 3:
                lines.append(f"| {path} | {n} | — (too few finite) |")
                continue
            c = float(valid["laplace_sigma"].corr(valid["gt_error"]))
            lines.append(f"| {path} | {n} | {c:.3f} |")
    lines.append("")

    # Sigma distribution per path
    lines.append("## sigma distribution per (substrate, path)\n")
    lines.append("| substrate | path | n | median | p10 | p50 | p90 | %inf |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for (sub, path), grp in ok.groupby(["substrate", "path"]):
        n = len(grp)
        sig = grp["laplace_sigma"]
        sig_finite = sig.replace([np.inf, -np.inf], np.nan).dropna()
        if sig_finite.empty:
            pct_inf = 100.0
            lines.append(f"| {sub} | {path} | {n} | — | — | — | — | {pct_inf:.1f}% |")
            continue
        pct_inf = 100.0 * (1.0 - len(sig_finite) / n)
        p10, p50, p90 = sig_finite.quantile([0.1, 0.5, 0.9])
        lines.append(f"| {sub} | {path} | {n} | {sig_finite.median():.4f} | {p10:.4f} | {p50:.4f} | {p90:.4f} | {pct_inf:.1f}% |")
    lines.append("")

    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    # Scatter PNGs
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        for path, pg in ok.groupby("path"):
            valid = pg.replace([np.inf, -np.inf], np.nan).dropna(subset=["laplace_sigma"])
            if valid.empty:
                continue
            fig, axes = plt.subplots(1, 2, figsize=(20, 8), dpi=200)
            # Panel 1: sigma vs intensity (primary)
            ax = axes[0]
            for sub, sg in valid.groupby("substrate"):
                ax.scatter(sg["intensity"], sg["laplace_sigma"], s=10, alpha=0.5, label=sub)
            ax.set_xlabel("noise intensity")
            ax.set_ylabel("Laplace sigma (chit units)")
            ax.set_title(f"PRIMARY: sigma vs intensity — {path}")
            ax.set_yscale("symlog", linthresh=1e-3)
            ax.grid(True, alpha=0.3)
            ax.legend()
            # Panel 2: sigma vs gt_error (secondary)
            ax = axes[1]
            mov = valid[valid["gt_error"].fillna(0) > 0.01]
            if not mov.empty:
                for sub, sg in mov.groupby("substrate"):
                    ax.scatter(sg["gt_error"], sg["laplace_sigma"], s=20, alpha=0.6, label=sub)
                mx = max(mov["gt_error"].max(), mov["laplace_sigma"].replace([np.inf], np.nan).max())
                mx = float(mx) if np.isfinite(mx) else 1.0
                ax.plot([0, mx], [0, mx], "k--", alpha=0.3, label="y=x")
            ax.set_xlabel("gt_error (|central - clean|, chit units)")
            ax.set_ylabel("Laplace sigma (chit units)")
            ax.set_title(f"SECONDARY: sigma vs gt_error — {path} (movers only)")
            ax.grid(True, alpha=0.3)
            ax.legend()
            fig.tight_layout()
            fig.savefig(out_dir / f"scatter_{path}.png", bbox_inches="tight")
            plt.close(fig)
    except Exception as e:
        print(f"  scatter PNG render failed: {e}")

    print(f"  report at {out_dir / 'summary.md'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-parquet", type=str,
                        default="H:/mpa-conform/output/calibration/20260518-192213-bootstrap-tier1/bootstrap_tier1.parquet")
    parser.add_argument("--delta", type=float, default=DEFAULT_DELTA)
    parser.add_argument("--output-root", type=str,
                        default="H:/mpa-conform/output/calibration")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.output_root) / f"{timestamp}-laplace"
    run_validation(Path(args.bootstrap_parquet), out_dir, delta=args.delta)


if __name__ == "__main__":
    main()
