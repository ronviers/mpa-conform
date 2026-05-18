"""Diagnostic-vector sweep harness.

Worker unit = (substrate, path, noise_model, intensity, seed_idx). Each
worker loads its substrate's cells, applies noise per-cell, runs the path
once over the batched substrate (lens-solver) or per-cell (two-stage),
and returns one FitOutcome per cell.

Substrate-batched workers for lens-solver paths give the predictor real
trajectory history — the bracket/agreement signals only have meaning when
the predictor is active. Per-cell calls would null-out predictor_gap
across most of the matrix, which is a hole in the diagnostic surface we
are calibrating.

Phase A: clean baseline (noise_model="clean", intensity=0) defines
ground-truth chit per (substrate, path, cell). Phase B sweeps noise and
compares against Phase A.

GT mapping (asymmetric on purpose):
    two_stage_inversion   ← own clean fit
    lens_solver_prior     ← own clean fit
    lens_solver_bootstrap ← lens_solver_prior's clean fit
The asymmetry tests whether bootstrap recovers what the prior knows.

Hang detection: per-worker 300s timeout via future.result(timeout=...).
Workers that exceed it are recorded as 'hang' for all their cells; the
worker process may leak (cannot be forcibly killed in ProcessPoolExecutor).
Acceptable trade for harness simplicity given max_passes bounds work per
fit.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


LIBRARY_ROOT = Path("H:/mpa-central/library/data")
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parents[2] / "output" / "calibration"
PER_WORKER_TIMEOUT_S = 300.0

DEFAULT_INTENSITIES: tuple[float, ...] = (0.0, 0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0)
DEFAULT_N_SEEDS = 5
DEFAULT_PATHS: tuple[str, ...] = (
    "two_stage_inversion", "lens_solver_prior", "lens_solver_bootstrap",
)
DEFAULT_NOISE_MODELS: tuple[str, ...] = (
    "gaussian", "drift", "quantization", "row_dropout",
    "calibration_bias", "tau_jitter", "multimodal_contamination",
)
DEFAULT_SUBSTRATES: tuple[str, ...] = ("glass", "quantum", "brain")


@dataclass(frozen=True)
class SweepConfig:
    substrates: tuple[str, ...] = DEFAULT_SUBSTRATES
    paths: tuple[str, ...] = DEFAULT_PATHS
    noise_models: tuple[str, ...] = DEFAULT_NOISE_MODELS
    intensities: tuple[float, ...] = DEFAULT_INTENSITIES
    n_seeds: int = DEFAULT_N_SEEDS
    library_root_str: str = str(LIBRARY_ROOT)
    output_root_str: str = str(DEFAULT_OUTPUT_ROOT)
    per_worker_timeout_s: float = PER_WORKER_TIMEOUT_S
    cell_limit_per_substrate: Optional[int] = None
    max_passes_lens_solver: int = 10
    n_workers: Optional[int] = None
    cfg_seed: int = 0


@dataclass(frozen=True)
class WorkerJob:
    substrate: str
    path: str
    noise_model: str
    intensity: float
    seed_idx: int
    cell_ids: tuple[str, ...]
    library_root_str: str
    max_passes: int
    cfg_seed: int


@dataclass(frozen=True)
class FitOutcome:
    substrate: str
    path: str
    noise_model: str
    intensity: float
    seed_idx: int
    cell_id: str
    fit_chit: Optional[float]
    fit_residual: Optional[float]
    gt_chit: Optional[float]
    gt_error: Optional[float]
    residual_final: Optional[float]
    regime_confidence: Optional[float]
    predictor_gap: Optional[float]
    n_passes: Optional[int]
    source: Optional[str]
    wall_time_s: float
    status: str
    error_msg: str = ""


# --- worker-side code ----------------------------------------------------
# All imports inside worker functions to keep process startup minimal and
# explicit. Top-level imports stay light.

def _per_cell_noise_seed(cfg_seed: int, job: WorkerJob, cell_id: str) -> int:
    return abs(hash((
        job.substrate, job.path, job.noise_model,
        float(job.intensity), int(job.seed_idx), cell_id, int(cfg_seed),
    ))) % (2**31 - 1)


def _per_worker_seed(cfg_seed: int, job: WorkerJob) -> int:
    return abs(hash((
        job.substrate, job.path, job.noise_model,
        float(job.intensity), int(job.seed_idx), int(cfg_seed),
    ))) % (2**31 - 1)


def _load_cells(library_root: Path, substrate: str, cell_ids: tuple[str, ...]) -> list[tuple[str, dict]]:
    out = []
    for cid in cell_ids:
        p = library_root / substrate / f"{cid}.json"
        cell = json.loads(p.read_text(encoding="utf-8"))
        out.append((cid, cell))
    return out


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


def _empty_outcome(job: WorkerJob, cell_id: str, t_start: float, status: str,
                   error_msg: str = "", gt_chit: Optional[float] = None) -> FitOutcome:
    return FitOutcome(
        substrate=job.substrate, path=job.path,
        noise_model=job.noise_model, intensity=float(job.intensity),
        seed_idx=int(job.seed_idx), cell_id=cell_id,
        fit_chit=None, fit_residual=None,
        gt_chit=gt_chit, gt_error=None,
        residual_final=None, regime_confidence=None,
        predictor_gap=None, n_passes=None, source=None,
        wall_time_s=(time.perf_counter() - t_start),
        status=status, error_msg=error_msg,
    )


def _run_worker(job: WorkerJob) -> list[FitOutcome]:
    """Worker entry point. Picklable. Returns one FitOutcome per cell."""
    t_start = time.perf_counter()

    from mpa_lens_solver import FitDiagnostics, fit_translation_field

    from conformer.calibration.noise_models import NOISE_MODELS
    from conformer.compute import inversion

    try:
        library_root = Path(job.library_root_str)
        cells = _load_cells(library_root, job.substrate, job.cell_ids)
        if not cells:
            return []

        # Apply noise per-cell with deterministic per-cell seeds
        noise_fn = NOISE_MODELS[job.noise_model]
        noisy_cells: list[tuple[str, dict, list[dict]]] = []
        for cell_id, cell in cells:
            rows = _cell_rows(cell)
            if not rows:
                noisy_cells.append((cell_id, cell, []))
                continue
            seed = _per_cell_noise_seed(job.cfg_seed, job, cell_id)
            noisy_rows = noise_fn(rows, float(job.intensity), seed)
            noisy_cells.append((cell_id, cell, noisy_rows))

        outcomes: list[FitOutcome] = []

        if job.path == "two_stage_inversion":
            for cell_id, cell, noisy_rows in noisy_cells:
                t_cell = time.perf_counter()
                if len(noisy_rows) < 2:
                    outcomes.append(_empty_outcome(job, cell_id, t_cell, "empty_rows"))
                    continue
                try:
                    result = inversion.invert(noisy_rows)
                    diag = result.fit_diagnostics
                    outcomes.append(FitOutcome(
                        substrate=job.substrate, path=job.path,
                        noise_model=job.noise_model, intensity=float(job.intensity),
                        seed_idx=int(job.seed_idx), cell_id=cell_id,
                        fit_chit=float(result.chit),
                        fit_residual=float(result.locus_residual),
                        gt_chit=None, gt_error=None,
                        residual_final=(diag.residual_final if diag else None),
                        regime_confidence=(diag.regime_confidence if diag else None),
                        predictor_gap=(diag.predictor_gap if diag else None),
                        n_passes=(diag.n_passes if diag else None),
                        source=(diag.source if diag else None),
                        wall_time_s=(time.perf_counter() - t_cell),
                        status="ok",
                    ))
                except Exception as e:
                    outcomes.append(_empty_outcome(
                        job, cell_id, t_cell, "error",
                        error_msg=f"{type(e).__name__}: {e}",
                    ))

        elif job.path in ("lens_solver_prior", "lens_solver_bootstrap"):
            # Substrate-batched call so the predictor sees trajectory history.
            usable: list[tuple[str, dict]] = []
            empty_ids: list[str] = []
            for cell_id, cell, noisy_rows in noisy_cells:
                if len(noisy_rows) < 2:
                    empty_ids.append(cell_id)
                    continue
                cell_copy = dict(cell)
                cell_copy["results"] = {"all_samples": _rows_to_samples(noisy_rows)}
                usable.append((cell_id, cell_copy))

            xdot = (cells[0][1].get("xdot_kind") or "unknown") if cells else "unknown"
            worker_seed = _per_worker_seed(job.cfg_seed, job)

            if usable:
                try:
                    field_obj = fit_translation_field(
                        job.substrate,
                        [c for _, c in usable],
                        xdot,
                        max_passes=job.max_passes,
                        rng_seed=worker_seed,
                        bootstrap=(job.path == "lens_solver_bootstrap"),
                    )
                    # Map rules back to cell_ids via the substrate's natural-
                    # sort order, same as fit_translation_field uses internally.
                    rule_by_label = {r.operating_point.label: r for r in field_obj.rule}
                    for cell_id, cell_copy in usable:
                        op_label = cell_copy["operating_point"]["label"]
                        rule = rule_by_label.get(op_label)
                        t_cell = time.perf_counter()
                        if rule is None:
                            outcomes.append(_empty_outcome(
                                job, cell_id, t_cell, "error",
                                error_msg=f"no rule produced for label {op_label!r}",
                            ))
                            continue
                        extras = rule.canonical.extras
                        diag_dict = extras.get("fit_diagnostics") or {}
                        diag = FitDiagnostics(**diag_dict) if diag_dict else None
                        outcomes.append(FitOutcome(
                            substrate=job.substrate, path=job.path,
                            noise_model=job.noise_model, intensity=float(job.intensity),
                            seed_idx=int(job.seed_idx), cell_id=cell_id,
                            fit_chit=float(rule.canonical.chit),
                            fit_residual=extras.get("residual"),
                            gt_chit=None, gt_error=None,
                            residual_final=(diag.residual_final if diag else None),
                            regime_confidence=(diag.regime_confidence if diag else None),
                            predictor_gap=(diag.predictor_gap if diag else None),
                            n_passes=(diag.n_passes if diag else None),
                            source=(diag.source if diag else None),
                            wall_time_s=0.0,  # batched call; per-cell timing not meaningful
                            status="ok",
                        ))
                except Exception as e:
                    tb = traceback.format_exc()[:500]
                    for cell_id, _ in usable:
                        outcomes.append(_empty_outcome(
                            job, cell_id, t_start, "error",
                            error_msg=f"{type(e).__name__}: {e}\n{tb}",
                        ))

            for cell_id in empty_ids:
                outcomes.append(_empty_outcome(job, cell_id, t_start, "empty_rows"))
        else:
            for cell_id, _, _ in noisy_cells:
                outcomes.append(_empty_outcome(
                    job, cell_id, t_start, "error",
                    error_msg=f"unknown path {job.path!r}",
                ))

        return outcomes
    except Exception as e:
        tb = traceback.format_exc()[:500]
        return [_empty_outcome(
            job, cid, t_start, "error",
            error_msg=f"worker outer: {type(e).__name__}: {e}\n{tb}",
        ) for cid in job.cell_ids]


# --- top-level orchestration ---------------------------------------------

def _list_cell_ids(library_root: Path, substrate: str, limit: Optional[int]) -> tuple[str, ...]:
    d = library_root / substrate
    if not d.is_dir():
        return ()
    paths = sorted(d.glob("*.json"))
    ids = tuple(p.stem for p in paths)
    if limit is not None:
        ids = ids[:limit]
    return ids


def _build_phase_a_jobs(cfg: SweepConfig, cell_ids_by_sub: dict[str, tuple[str, ...]]) -> list[WorkerJob]:
    jobs = []
    for substrate in cfg.substrates:
        cids = cell_ids_by_sub[substrate]
        for path in cfg.paths:
            jobs.append(WorkerJob(
                substrate=substrate, path=path,
                noise_model="clean", intensity=0.0,
                seed_idx=0, cell_ids=cids,
                library_root_str=cfg.library_root_str,
                max_passes=cfg.max_passes_lens_solver,
                cfg_seed=cfg.cfg_seed,
            ))
    return jobs


def _build_phase_b_jobs(cfg: SweepConfig, cell_ids_by_sub: dict[str, tuple[str, ...]]) -> list[WorkerJob]:
    jobs = []
    for substrate in cfg.substrates:
        cids = cell_ids_by_sub[substrate]
        for path in cfg.paths:
            for noise in cfg.noise_models:
                for intensity in cfg.intensities:
                    for seed_idx in range(cfg.n_seeds):
                        jobs.append(WorkerJob(
                            substrate=substrate, path=path,
                            noise_model=noise, intensity=float(intensity),
                            seed_idx=int(seed_idx), cell_ids=cids,
                            library_root_str=cfg.library_root_str,
                            max_passes=cfg.max_passes_lens_solver,
                            cfg_seed=cfg.cfg_seed,
                        ))
    return jobs


def _gt_chit_for(path: str, substrate: str, cell_id: str,
                 gt_lookup: dict[tuple[str, str, str], float]) -> Optional[float]:
    """Bootstrap path's GT is the prior path's clean fit, by design."""
    gt_path = "lens_solver_prior" if path == "lens_solver_bootstrap" else path
    return gt_lookup.get((substrate, gt_path, cell_id))


def _execute(jobs: list[WorkerJob], cfg: SweepConfig, phase_label: str) -> list[FitOutcome]:
    n_workers = cfg.n_workers if cfg.n_workers else max(1, (os.cpu_count() or 2) - 1)
    print(f"  {phase_label}: {len(jobs)} workers x ~{len(jobs[0].cell_ids) if jobs else 0} cells, {n_workers} processes")
    outcomes: list[FitOutcome] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as ex:
        future_to_job = {ex.submit(_run_worker, job): job for job in jobs}
        n_done = 0
        for fut in concurrent.futures.as_completed(future_to_job):
            job = future_to_job[fut]
            try:
                worker_outcomes = fut.result(timeout=cfg.per_worker_timeout_s)
            except concurrent.futures.TimeoutError:
                worker_outcomes = [_empty_outcome(
                    job, cid, time.perf_counter() - cfg.per_worker_timeout_s,
                    "hang", error_msg=f"worker timeout > {cfg.per_worker_timeout_s}s",
                ) for cid in job.cell_ids]
            except Exception as e:
                worker_outcomes = [_empty_outcome(
                    job, cid, time.perf_counter(), "error",
                    error_msg=f"{type(e).__name__}: {e}",
                ) for cid in job.cell_ids]
            outcomes.extend(worker_outcomes)
            n_done += 1
            if n_done % 50 == 0 or n_done == len(jobs):
                print(f"    [{n_done}/{len(jobs)}] workers done; {len(outcomes)} outcomes")
    return outcomes


def run_sweep(cfg: SweepConfig, *, label: str = "sweep") -> Path:
    """Run two-phase sweep, write parquet + manifest, return parquet path."""
    library_root = Path(cfg.library_root_str)
    output_root = Path(cfg.output_root_str)
    output_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = output_root / f"{timestamp}-{label}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cell_ids_by_sub = {
        s: _list_cell_ids(library_root, s, cfg.cell_limit_per_substrate)
        for s in cfg.substrates
    }
    n_cells = {s: len(v) for s, v in cell_ids_by_sub.items()}
    print(f"loaded cell IDs: {n_cells}")

    print("\nPhase A: clean baseline (defines GT chit per substrate-path-cell)")
    phase_a_jobs = _build_phase_a_jobs(cfg, cell_ids_by_sub)
    phase_a = _execute(phase_a_jobs, cfg, "phase A")

    gt_lookup: dict[tuple[str, str, str], float] = {}
    for o in phase_a:
        if o.status == "ok" and o.fit_chit is not None:
            gt_lookup[(o.substrate, o.path, o.cell_id)] = float(o.fit_chit)

    print(f"\nPhase A: {len(gt_lookup)} GT chits resolved")

    print("\nPhase B: noise sweep")
    phase_b_jobs = _build_phase_b_jobs(cfg, cell_ids_by_sub)
    phase_b = _execute(phase_b_jobs, cfg, "phase B")

    # Backfill GT chit + gt_error
    all_outcomes: list[FitOutcome] = []
    for o in phase_a:
        all_outcomes.append(o)  # phase A outcomes have no GT (they define GT)
    for o in phase_b:
        gt = _gt_chit_for(o.path, o.substrate, o.cell_id, gt_lookup)
        gt_err = (
            abs(o.fit_chit - gt)
            if (gt is not None and o.fit_chit is not None) else None
        )
        all_outcomes.append(FitOutcome(
            **{**asdict(o), "gt_chit": gt, "gt_error": gt_err}
        ))

    df = pd.DataFrame([asdict(o) for o in all_outcomes])
    parquet_path = out_dir / "sweep.parquet"
    df.to_parquet(parquet_path)

    manifest = {
        "timestamp_utc": timestamp,
        "label": label,
        "n_cells_by_substrate": n_cells,
        "phase_a_workers": len(phase_a_jobs),
        "phase_b_workers": len(phase_b_jobs),
        "phase_a_outcomes": len(phase_a),
        "phase_b_outcomes": len(phase_b),
        "total_rows": len(df),
        "n_workers_used": cfg.n_workers or max(1, (os.cpu_count() or 2) - 1),
        "config": {
            "substrates": list(cfg.substrates),
            "paths": list(cfg.paths),
            "noise_models": list(cfg.noise_models),
            "intensities": list(cfg.intensities),
            "n_seeds": cfg.n_seeds,
            "max_passes_lens_solver": cfg.max_passes_lens_solver,
            "per_worker_timeout_s": cfg.per_worker_timeout_s,
            "cell_limit_per_substrate": cfg.cell_limit_per_substrate,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"\nwrote {len(df)} rows -> {parquet_path}")
    return parquet_path


if __name__ == "__main__":
    # Direct invocation runs the full default matrix.
    run_sweep(SweepConfig(), label="full")
