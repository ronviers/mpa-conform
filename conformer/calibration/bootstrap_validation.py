"""bootstrap_validation.py — validate bootstrap_sigma(chit) as the
calibration-free confidence quantity.

For each sampled cell from a sweep parquet:
  1. Load the library cell + apply the sampled noise (same seed convention
     as sweep.py).
  2. Single-cell fit on CLEAN rows -> reference chit (gt_chit_internal).
  3. Single-cell fit on NOISY rows -> central chit.
  4. B=100 row-bootstrap on the NOISY rows -> distribution of chits.
  5. Record (substrate, path, noise_model, intensity, gt_error, sigma,
     success_rate, skew, bimodality, n_passes, central_chit, ...).

Tiered escalation: tier 1 = 2%, tier 2 = 5%, tier 3 = 15% (stratified
random sample within substrate x path x noise_model).

If bootstrap_sigma correlates monotonically with gt_error across all
substrates with stable slope, the calibration-free framing is validated
and we can drop the diagnostic-vector apparatus.

CLI:
  python -m conformer.calibration.bootstrap_validation \\
      --parquet PATH --frac 0.02 [--B 100] [--workers N]

Wraps the same three paths the sweep tested:
  two_stage_inversion, lens_solver_prior, lens_solver_bootstrap.

Single-cell fits: lens-solver paths run with one-cell lists, so the
predictor is inactive (no trajectory history). This is the proxy
validation for tier 1; batched-mode bootstrap is a follow-up if the
single-cell results warrant escalation.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


LIBRARY_ROOT = Path("H:/mpa-central/library/data")


@dataclass(frozen=True)
class BootstrapJob:
    substrate: str
    path: str
    noise_model: str
    intensity: float
    seed_idx: int
    cell_id: str
    library_root_str: str
    B: int
    cfg_seed: int


@dataclass(frozen=True)
class BootstrapOutcome:
    substrate: str
    path: str
    noise_model: str
    intensity: float
    seed_idx: int
    cell_id: str
    gt_chit_internal: Optional[float]  # single-cell fit on clean rows
    central_chit: Optional[float]      # single-cell fit on noisy rows
    gt_error: Optional[float]          # |central - gt_chit_internal|
    bootstrap_sigma: Optional[float]   # std of B resampled chits
    bootstrap_success_rate: Optional[float]
    bootstrap_skew: Optional[float]
    bootstrap_bimodality: Optional[float]
    n_bootstrap_resamples: int
    wall_time_s: float
    status: str
    error_msg: str = ""


# --- worker-side helpers (imports inside to keep startup lean) -----------

def _cell_rows(cell: dict) -> list[dict]:
    samples = cell.get("results", {}).get("all_samples", [])
    rows = []
    for s in samples:
        tau, C, chi = s.get("t"), s.get("C_mean"), s.get("chi_mean")
        if tau is None or C is None or chi is None:
            continue
        rows.append({"tau": float(tau), "C": float(C), "chi": float(chi)})
    return rows


def _rows_to_samples(rows: list[dict]) -> list[dict]:
    return [{"t": r["tau"], "C_mean": r["C"], "chi_mean": r["chi"]} for r in rows]


def _per_cell_noise_seed(cfg_seed: int, job: BootstrapJob) -> int:
    """Match sweep.py's seed derivation so the noisy rows match what the
    sweep produced for the same (substrate, path, noise_model, intensity,
    seed_idx, cell_id) tuple."""
    return abs(hash((
        job.substrate, job.path, job.noise_model,
        float(job.intensity), int(job.seed_idx), job.cell_id, int(cfg_seed),
    ))) % (2**31 - 1)


def _fit_chit_single_cell(path: str, substrate: str, cell: dict,
                          rows: list[dict], rng_seed: int) -> Optional[float]:
    """Single-cell fit; returns chit or None on failure. Lens-solver paths
    use single-cell lists (predictor inactive)."""
    from mpa_lens_solver import fit_translation_field

    from conformer.compute import inversion

    if not rows or len(rows) < 2:
        return None

    if path == "two_stage_inversion":
        try:
            result = inversion.invert(rows)
            return float(result.chit)
        except Exception:
            return None
    elif path in ("lens_solver_prior", "lens_solver_bootstrap"):
        cell_copy = dict(cell)
        cell_copy["results"] = {"all_samples": _rows_to_samples(rows)}
        xdot = cell.get("xdot_kind") or "unknown"
        try:
            field_obj = fit_translation_field(
                substrate, [cell_copy], xdot,
                max_passes=10, rng_seed=int(rng_seed),
                bootstrap=(path == "lens_solver_bootstrap"),
            )
            return float(field_obj.rule[0].canonical.chit)
        except Exception:
            return None
    else:
        return None


def _bimodality(samples: np.ndarray) -> Optional[float]:
    """Sarle's bimodality coefficient. > 0.555 suggests bimodal.
    https://en.wikipedia.org/wiki/Multimodal_distribution#Bimodality_coefficient"""
    n = len(samples)
    if n < 4:
        return None
    m = samples.mean()
    s = samples.std(ddof=1)
    if s == 0:
        return None
    m3 = ((samples - m) ** 3).mean()
    m4 = ((samples - m) ** 4).mean()
    skew = m3 / (s ** 3)
    kurt_excess = m4 / (s ** 4) - 3.0
    denom = kurt_excess + 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    if denom == 0 or not np.isfinite(denom):
        return None
    return float((skew * skew + 1.0) / denom)


def _skew(samples: np.ndarray) -> Optional[float]:
    if len(samples) < 3:
        return None
    s = samples.std(ddof=1)
    if s == 0:
        return None
    return float(((samples - samples.mean()) ** 3).mean() / (s ** 3))


def _run_bootstrap(job: BootstrapJob) -> BootstrapOutcome:
    """Worker entry. Loads cell, applies noise, runs central + clean fits,
    runs B bootstrap resamples, returns outcome."""
    t_start = time.perf_counter()

    try:
        from conformer.calibration.noise_models import NOISE_MODELS

        library_root = Path(job.library_root_str)
        cell_path = library_root / job.substrate / f"{job.cell_id}.json"
        cell = json.loads(cell_path.read_text(encoding="utf-8"))

        clean_rows = _cell_rows(cell)
        if len(clean_rows) < 2:
            return _empty(job, t_start, "empty_rows")

        noise_fn = NOISE_MODELS[job.noise_model]
        noise_seed = _per_cell_noise_seed(job.cfg_seed, job)
        noisy_rows = noise_fn(clean_rows, float(job.intensity), noise_seed)

        if len(noisy_rows) < 2:
            return _empty(job, t_start, "empty_rows_after_noise")

        # 1. Clean reference fit
        gt_chit = _fit_chit_single_cell(
            job.path, job.substrate, cell, clean_rows, rng_seed=noise_seed,
        )
        if gt_chit is None:
            return _empty(job, t_start, "clean_fit_failed")

        # 2. Central fit on noisy rows
        central_chit = _fit_chit_single_cell(
            job.path, job.substrate, cell, noisy_rows, rng_seed=noise_seed,
        )
        if central_chit is None:
            return _empty(job, t_start, "central_fit_failed",
                          gt_chit=gt_chit)

        # 3. B row-bootstraps
        rng = np.random.default_rng(noise_seed)
        n = len(noisy_rows)
        chits: list[float] = []
        for b in range(job.B):
            idxs = rng.integers(0, n, size=n)
            boot_rows = [noisy_rows[int(i)] for i in idxs]
            c = _fit_chit_single_cell(
                job.path, job.substrate, cell, boot_rows,
                rng_seed=(noise_seed + b + 1),
            )
            if c is not None and np.isfinite(c):
                chits.append(float(c))

        n_succ = len(chits)
        if n_succ < 2:
            return _empty(job, t_start, "bootstrap_all_failed",
                          gt_chit=gt_chit, central_chit=central_chit)

        arr = np.asarray(chits, dtype=float)
        sigma = float(arr.std(ddof=1))
        success_rate = n_succ / job.B
        skew = _skew(arr)
        bim = _bimodality(arr)

        return BootstrapOutcome(
            substrate=job.substrate, path=job.path,
            noise_model=job.noise_model, intensity=float(job.intensity),
            seed_idx=int(job.seed_idx), cell_id=job.cell_id,
            gt_chit_internal=float(gt_chit),
            central_chit=float(central_chit),
            gt_error=float(abs(central_chit - gt_chit)),
            bootstrap_sigma=sigma,
            bootstrap_success_rate=float(success_rate),
            bootstrap_skew=skew,
            bootstrap_bimodality=bim,
            n_bootstrap_resamples=int(n_succ),
            wall_time_s=(time.perf_counter() - t_start),
            status="ok",
        )

    except Exception as e:
        tb = traceback.format_exc()[:400]
        return _empty(job, t_start, "error",
                      error_msg=f"{type(e).__name__}: {e}\n{tb}")


def _empty(job: BootstrapJob, t_start: float, status: str,
           error_msg: str = "",
           gt_chit: Optional[float] = None,
           central_chit: Optional[float] = None) -> BootstrapOutcome:
    return BootstrapOutcome(
        substrate=job.substrate, path=job.path,
        noise_model=job.noise_model, intensity=float(job.intensity),
        seed_idx=int(job.seed_idx), cell_id=job.cell_id,
        gt_chit_internal=gt_chit, central_chit=central_chit,
        gt_error=None,
        bootstrap_sigma=None, bootstrap_success_rate=None,
        bootstrap_skew=None, bootstrap_bimodality=None,
        n_bootstrap_resamples=0,
        wall_time_s=(time.perf_counter() - t_start),
        status=status, error_msg=error_msg,
    )


# --- top-level: sampling, orchestration, reporting -----------------------

def _stratified_sample(sweep_df: pd.DataFrame, frac: float, rng_seed: int) -> pd.DataFrame:
    """Uniform random sample within each (substrate, path, noise_model)
    stratum. Filters to status=='ok' and noise_model != 'clean' first
    (clean rows are phase-A baselines, not useful for validation)."""
    usable = sweep_df[
        (sweep_df["status"] == "ok")
        & (sweep_df["noise_model"] != "clean")
    ].copy()
    rng = np.random.default_rng(rng_seed)

    def _sample(group: pd.DataFrame) -> pd.DataFrame:
        n = max(1, int(round(len(group) * frac)))
        if n >= len(group):
            return group
        idx = rng.choice(len(group), size=n, replace=False)
        return group.iloc[idx]

    sampled = usable.groupby(
        ["substrate", "path", "noise_model"], group_keys=False, sort=False,
    ).apply(_sample)
    return sampled.reset_index(drop=True)


def _execute(jobs: list[BootstrapJob], n_workers: int) -> list[BootstrapOutcome]:
    outcomes: list[BootstrapOutcome] = []
    print(f"  executing {len(jobs)} bootstrap jobs across {n_workers} processes")
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as ex:
        future_to_job = {ex.submit(_run_bootstrap, j): j for j in jobs}
        n_done = 0
        for fut in concurrent.futures.as_completed(future_to_job):
            try:
                outcomes.append(fut.result(timeout=600.0))
            except concurrent.futures.TimeoutError:
                job = future_to_job[fut]
                outcomes.append(_empty(job, time.perf_counter() - 600.0,
                                       "hang", error_msg="timeout > 600s"))
            n_done += 1
            if n_done % 50 == 0 or n_done == len(jobs):
                print(f"    [{n_done}/{len(jobs)}] done")
    return outcomes


def _report(df: pd.DataFrame, out_dir: Path, tier_label: str) -> None:
    """Per-substrate correlation + slope + scatter PNGs."""
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_parquet(out_dir / f"bootstrap_{tier_label}.parquet")

    scored = df[(df["status"] == "ok") & df["gt_error"].notna() & df["bootstrap_sigma"].notna()].copy()

    lines: list[str] = []
    lines.append(f"# Bootstrap-confidence validation — {tier_label}\n")
    lines.append(f"Run: {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"Total jobs: {len(df)}, scored: {len(scored)}\n")
    lines.append("## Per-substrate correlation (sigma vs gt_error)\n")
    lines.append("| substrate | path | n | corr | slope | intercept | R^2 |")
    lines.append("|---|---|---|---|---|---|---|")
    for (sub, path), grp in scored.groupby(["substrate", "path"]):
        n = len(grp)
        if n < 5:
            lines.append(f"| {sub} | {path} | {n} | — | — | — | — |")
            continue
        x = grp["bootstrap_sigma"].to_numpy()
        y = grp["gt_error"].to_numpy()
        corr = float(np.corrcoef(x, y)[0, 1])
        # OLS slope/intercept of gt_error ~ a + b*sigma
        coef = np.polyfit(x, y, 1)
        b, a = float(coef[0]), float(coef[1])
        y_pred = a + b * x
        ss_res = ((y - y_pred) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
        lines.append(f"| {sub} | {path} | {n} | {corr:.3f} | {b:.3f} | {a:.4f} | {r2:.3f} |")
    lines.append("")

    lines.append("## Pooled slope (across substrates, per path)\n")
    lines.append("Stability of slope across substrates is the key test. If the slope is consistent within ~30%, the framing generalizes.\n")
    lines.append("| path | substrates_present | slope_min | slope_max | slope_range |")
    lines.append("|---|---|---|---|---|")
    for path, pg in scored.groupby("path"):
        slopes = []
        subs = []
        for sub, sg in pg.groupby("substrate"):
            if len(sg) < 5:
                continue
            coef = np.polyfit(sg["bootstrap_sigma"], sg["gt_error"], 1)
            slopes.append(float(coef[0]))
            subs.append(sub)
        if len(slopes) < 2:
            lines.append(f"| {path} | {','.join(subs)} | — | — | — |")
            continue
        smin, smax = min(slopes), max(slopes)
        rng = (smax - smin) / max(abs(smin), abs(smax), 1e-9)
        lines.append(f"| {path} | {','.join(subs)} | {smin:.3f} | {smax:.3f} | {rng:.2%} |")
    lines.append("")

    lines.append("## Status sanity\n")
    sc = df["status"].value_counts()
    lines.append("| status | count |")
    lines.append("|---|---|")
    for k, v in sc.items():
        lines.append(f"| {k} | {int(v)} |")
    lines.append("")

    (out_dir / f"summary_{tier_label}.md").write_text("\n".join(lines), encoding="utf-8")

    # Scatter PNGs
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        for path, pg in scored.groupby("path"):
            fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
            for sub, sg in pg.groupby("substrate"):
                ax.scatter(sg["bootstrap_sigma"], sg["gt_error"],
                           s=10, alpha=0.5, label=f"{sub} (n={len(sg)})")
            ax.set_xlabel("bootstrap_sigma (chit units)")
            ax.set_ylabel("gt_error = |central - clean_fit| (chit units)")
            ax.set_title(f"{path} — bootstrap_sigma vs gt_error  [{tier_label}]")
            mx = max(scored["bootstrap_sigma"].max(), scored["gt_error"].max())
            mx = float(mx) if np.isfinite(mx) else 1.0
            ax.plot([0, mx], [0, mx], "k--", alpha=0.3, label="y=x")
            ax.set_xlim(0, mx * 1.05)
            ax.set_ylim(0, mx * 1.05)
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(out_dir / f"scatter_{tier_label}_{path}.png", bbox_inches="tight")
            plt.close(fig)
    except Exception as e:
        print(f"  scatter PNG render failed: {e}")

    print(f"\n  report at {out_dir / f'summary_{tier_label}.md'}")


# --- CLI -----------------------------------------------------------------

def run_tier(parquet_path: Path, frac: float, B: int, n_workers: int,
             rng_seed: int, output_root: Path, tier_label: str) -> Path:
    sweep_df = pd.read_parquet(parquet_path)
    print(f"loaded sweep: {len(sweep_df)} rows from {parquet_path}")

    sampled = _stratified_sample(sweep_df, frac, rng_seed)
    print(f"sampled {len(sampled)} rows ({frac:.1%} stratified)")

    jobs = [
        BootstrapJob(
            substrate=r["substrate"], path=r["path"],
            noise_model=r["noise_model"], intensity=float(r["intensity"]),
            seed_idx=int(r["seed_idx"]), cell_id=r["cell_id"],
            library_root_str=str(LIBRARY_ROOT),
            B=int(B), cfg_seed=0,
        )
        for _, r in sampled.iterrows()
    ]

    t0 = time.perf_counter()
    outcomes = _execute(jobs, n_workers=n_workers)
    elapsed = time.perf_counter() - t0
    print(f"  {len(outcomes)} outcomes in {elapsed:.1f}s")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = output_root / f"{timestamp}-bootstrap-{tier_label}"
    df = pd.DataFrame([asdict(o) for o in outcomes])
    _report(df, out_dir, tier_label)

    manifest = {
        "timestamp_utc": timestamp,
        "tier_label": tier_label,
        "source_parquet": str(parquet_path),
        "sample_frac": frac,
        "B": B,
        "n_workers": n_workers,
        "rng_seed": rng_seed,
        "n_jobs": len(jobs),
        "n_outcomes": len(outcomes),
        "wall_time_s": elapsed,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", type=str,
                        default="H:/mpa-conform/output/calibration/20260518-132746-full-3sub/sweep.parquet",
                        help="path to sweep.parquet")
    parser.add_argument("--frac", type=float, default=0.02,
                        help="sample fraction (0.02=tier 1, 0.05=tier 2, 0.15=tier 3)")
    parser.add_argument("--B", type=int, default=100, help="bootstrap resamples per cell")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--rng-seed", type=int, default=0)
    parser.add_argument("--tier-label", type=str, default=None,
                        help="label for output dir (default: 'tier-{frac}')")
    parser.add_argument("--output-root", type=str,
                        default="H:/mpa-conform/output/calibration")
    args = parser.parse_args()

    n_workers = args.workers or max(1, (os.cpu_count() or 2) - 1)
    label = args.tier_label or f"tier-{args.frac:.0%}"

    run_tier(
        parquet_path=Path(args.parquet),
        frac=args.frac,
        B=args.B,
        n_workers=n_workers,
        rng_seed=args.rng_seed,
        output_root=Path(args.output_root),
        tier_label=label,
    )


if __name__ == "__main__":
    main()
