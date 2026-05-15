"""mpa-conform CLI — activity-scroll runner.

Usage:
    python -m conformer.cli invert <bundle.json>
    python -m conformer.cli invert <bundle.json> --skip-stage2
    python -m conformer.cli invert-all
    python -m conformer.cli invert-all --class ck-glassy

Activity log format (dev mode): one event per line, `[stage] kind: payload`.
Suitable for streaming into a window during development; a future version
swaps this for a progress bar once the phase set stabilizes.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from conformer.compute import inversion


REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_CORPUS = REPO_ROOT / "output" / "seed-corpus"


def _fmt_num(x: Any) -> str:
    if x is None:
        return "None"
    if isinstance(x, float):
        if abs(x) >= 1e4 or (abs(x) < 1e-3 and x != 0):
            return f"{x:.3e}"
        return f"{x:.4f}"
    return str(x)


def make_stdout_logger(label: str) -> "inversion.Logger":
    t0 = time.perf_counter()

    def log(kind: str, payload: dict) -> None:
        dt = time.perf_counter() - t0
        parts = [f"{_fmt_num(v) if isinstance(v, float) else v}" for v in [
            f"{k}={_fmt_num(v)}" for k, v in payload.items()
        ]]
        # Render: t+0.123s [label] kind k=v k=v
        body = " ".join(f"{k}={_fmt_num(v)}" for k, v in payload.items())
        print(f"  t+{dt:6.2f}s [{label}] {kind:20s} {body}", flush=True)

    return log


def cmd_invert(bundle_path: Path, skip_stage2: bool = False) -> dict:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    obs = bundle.get("observable", {})
    rows = obs.get("data", [])
    scalar = bundle.get("scalar_observables") or {}
    empirical_r = scalar.get("phase_locking_r")
    initial_gamma = inversion.DEFAULT_GAMMA
    fit_prov = bundle.get("fit_provenance") or {}
    seed_gamma = (fit_prov.get("fitted_params") or {}).get("gamma_AB")
    if isinstance(seed_gamma, (int, float)):
        initial_gamma = float(seed_gamma)

    label = bundle_path.stem
    print(f"\n== invert {label} (n_rows={len(rows)}, initial_gamma={initial_gamma:.3f}, empirical_r={empirical_r}) ==", flush=True)
    log = make_stdout_logger(label)

    t0 = time.perf_counter()
    result = inversion.invert(
        rows,
        initial_gamma=initial_gamma,
        empirical_r=empirical_r,
        skip_stage2=skip_stage2,
        log=log,
    )
    elapsed = time.perf_counter() - t0

    print(
        f"\n  RESULT: chit={result.chit:.4f} ({result.regime}), "
        f"gamma_AB={result.gamma_AB:.4f} ({'constrained' if result.gamma_constrained else 'carried-through'}), "
        f"chit_observable={result.chit_observable}, "
        f"locus_residual={result.locus_residual:.3e}, "
        f"elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "bundle_path": str(bundle_path),
        "bundle_id": bundle.get("bundle_id"),
        "fit_provenance_new": {
            "fitted_params": {
                "chit": result.chit,
                "gamma_AB": result.gamma_AB,
            },
            "regime": result.regime,
            "locus_residual": result.locus_residual,
            "gamma_residual": result.gamma_residual,
            "chit_observable": result.chit_observable,
            "gamma_observable": result.gamma_observable,
            "gamma_constrained": result.gamma_constrained,
            "stage1_chit": result.stage1_chit,
            "stage2_n_ensemble": result.stage2_n_ensemble,
            "stage2_n_analytical": result.stage2_n_analytical,
            "method": "mpa-conform inversion v0.2 (two-stage analytical + ensemble refine, phase-locking gamma)",
            "elapsed_seconds": elapsed,
        },
        "leading_order_seed": (bundle.get("fit_provenance") or {}).get("fitted_params"),
    }


def cmd_invert_all(class_filter: str | None = None, skip_stage2: bool = False) -> dict:
    if not SEED_CORPUS.is_dir():
        raise SystemExit(f"no seed corpus found at {SEED_CORPUS}. Run `python -m conformer.curator.walk_library` first.")
    summary: dict[str, Any] = {"runs": [], "errors": []}
    for class_dir in sorted(SEED_CORPUS.iterdir()):
        if not class_dir.is_dir():
            continue
        if class_filter and class_dir.name != class_filter:
            continue
        for bundle_path in sorted(class_dir.glob("*.bundle.json")):
            try:
                run = cmd_invert(bundle_path, skip_stage2=skip_stage2)
                summary["runs"].append({
                    "class": class_dir.name,
                    "bundle": bundle_path.name,
                    **run["fit_provenance_new"],
                    "leading_order_seed": run["leading_order_seed"],
                })
            except Exception as e:
                summary["errors"].append({"bundle": str(bundle_path), "error": str(e)})
                print(f"  [error] {bundle_path.name}: {e}", file=sys.stderr, flush=True)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(prog="conformer.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_inv = sub.add_parser("invert", help="invert a single bundle")
    p_inv.add_argument("bundle", type=Path)
    p_inv.add_argument("--skip-stage2", action="store_true", help="analytical-only fit (skip ensemble refine)")

    p_all = sub.add_parser("invert-all", help="invert every staged bundle")
    p_all.add_argument("--class", dest="class_filter", default=None)
    p_all.add_argument("--skip-stage2", action="store_true")
    p_all.add_argument("--out", type=Path, default=SEED_CORPUS / "_inversion_summary.json")

    args = ap.parse_args()

    if args.cmd == "invert":
        cmd_invert(args.bundle, skip_stage2=args.skip_stage2)
    elif args.cmd == "invert-all":
        summary = cmd_invert_all(class_filter=args.class_filter, skip_stage2=args.skip_stage2)
        args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote summary -> {args.out.relative_to(SEED_CORPUS.parent)}", flush=True)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
