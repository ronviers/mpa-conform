"""mpa-conform CLI — activity-scroll runner.

Usage:
    python -m conformer.cli invert <bundle.json>
    python -m conformer.cli invert <bundle.json> --skip-stage2
    python -m conformer.cli invert-all
    python -m conformer.cli invert-all --class ck-glassy
    python -m conformer.cli compare <bundle.json>
    python -m conformer.cli compare-all --class ck-glassy
    python -m conformer.cli shot <bundle.json> [--duration 3 --fps 10]
    python -m conformer.cli shot-all --class ck-glassy

Activity log format (dev mode): one event per line, `[stage] kind: payload`.
Suitable for streaming into a window during development; a future version
swaps this for a progress bar once the phase set stabilizes.

`compare` renders a three-way (empirical / predicted / Banach) two-panel
C(tau) + chi(tau) PNG per bundle into output/comparisons/. `shot` is the
preferred verification artifact going forward: a continuous EXR sequence
+ mp4 preview showing the substrate evolving across sample-time. See
`conformer/shot/STANDARDS.md` for layout and defaults.
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

    # tau_scale for the 5-vector lives in the curator's preprocessing_log (raw native lag
    # must be divided by it; banach_overlay reads it the same way). Feeding raw tau silently
    # corrupts the 5-vector fit.
    tau_scale = 1.0
    for entry in (obs.get("preprocessing_log") or []):
        ts = (entry.get("parameters") or {}).get("tau_scale")
        if ts:
            tau_scale = float(ts)
    op = bundle.get("operating_point") or {}
    T = float(op.get("temperature") or op.get("T") or 1.0)

    label = bundle_path.stem
    print(f"\n== invert {label} (n_rows={len(rows)}, initial_gamma={initial_gamma:.3f}, empirical_r={empirical_r}, tau_scale={tau_scale:.1f}, T={T:.2f}) ==", flush=True)
    log = make_stdout_logger(label)

    t0 = time.perf_counter()
    result = inversion.invert(
        rows,
        initial_gamma=initial_gamma,
        empirical_r=empirical_r,
        skip_stage2=skip_stage2,
        tau_scale=tau_scale,
        T=T,
        n_boot=24,
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

    fit_prov_new = {
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
    }

    fv = result.five_vector_fit
    if fv is not None:
        gate = "IN" if fv.in_domain else "OUT"
        snr_C = fv.channel_snr.get("C", float("nan"))
        print(f"  5-VECTOR: X={fv.X:.3f}, q_EA={fv.q_EA:.3f}, beta_KWW={fv.beta_KWW:.3f}, "
              f"resid={fv.residual:.4f} [{gate}], C S/N={snr_C:.2f}", flush=True)
        fv_block = {
            "X": fv.X, "q_EA": fv.q_EA, "tau_alpha": fv.tau_alpha,
            "beta_KWW": fv.beta_KWW, "tau_beta": fv.tau_beta, "T": fv.T,
            "residual": fv.residual, "in_domain": fv.in_domain,
            "channel_snr": fv.channel_snr, "channel_floor": fv.channel_floor,
            "notes": fv.notes,
            "method": f"mpa-conform 5-vector (KWW+FDT, per-channel S/N gate {inversion_snr_gate()})",
        }
        ident = getattr(fv, "identifiability", None)
        if ident is not None and getattr(ident, "assessable", False):
            pinned = [p for p in ident.identified if ident.identified[p]]
            mush = [p for p in ident.identified if not ident.identified[p]]
            print(f"  IDENTIFIABILITY (bootstrap n={ident.n_boot}): "
                  f"pinned={pinned or 'none'} | NOT pinned={mush or 'none'}", flush=True)
            fv_block["identifiability"] = {
                "n_boot": ident.n_boot, "identified": ident.identified,
                "spread": ident.spread, "std": ident.std, "railed": ident.railed,
            }
        fit_prov_new["five_vector"] = fv_block

    return {
        "bundle_path": str(bundle_path),
        "bundle_id": bundle.get("bundle_id"),
        "fit_provenance_new": fit_prov_new,
        "leading_order_seed": (bundle.get("fit_provenance") or {}).get("fitted_params"),
    }


def inversion_snr_gate() -> float:
    from conformer.compute import five_vector
    return five_vector.SNR_GATE


def cmd_compare(bundle_path: Path, out_dir: Path | None = None) -> Path:
    from conformer.compare.banach_overlay import load_comparison, render_png

    data = load_comparison(bundle_path)
    if out_dir is None:
        out_dir = REPO_ROOT / "output" / "comparisons" / data.substrate_class
    out_path = out_dir / f"{bundle_path.stem}.png"
    render_png(data, out_path)
    rel = out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path
    print(f"  wrote -> {rel}", flush=True)
    return out_path


def cmd_compare_all(class_filter: str | None = None) -> dict:
    if not SEED_CORPUS.is_dir():
        raise SystemExit(f"no seed corpus found at {SEED_CORPUS}. Run `python -m conformer.curator.walk_library` first.")
    summary: dict[str, Any] = {"figures": [], "errors": []}
    for class_dir in sorted(SEED_CORPUS.iterdir()):
        if not class_dir.is_dir():
            continue
        if class_filter and class_dir.name != class_filter:
            continue
        for bundle_path in sorted(class_dir.glob("*.bundle.json")):
            try:
                p = cmd_compare(bundle_path)
                summary["figures"].append(str(p))
            except Exception as e:
                summary["errors"].append({"bundle": str(bundle_path), "error": str(e)})
                print(f"  [error] {bundle_path.name}: {e}", file=sys.stderr, flush=True)
    return summary


def cmd_shot(
    bundle_path: Path,
    *,
    duration_s: float | None = None,
    fps: int | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict:
    from conformer.shot.builder import build_shot
    from conformer.shot.standards import SHOT_STANDARDS, ShotStandards
    s = SHOT_STANDARDS
    if any(v is not None for v in (duration_s, fps, width, height)):
        s = ShotStandards(
            fps=fps if fps is not None else s.fps,
            duration_s=duration_s if duration_s is not None else s.duration_s,
            width=width if width is not None else s.width,
            height=height if height is not None else s.height,
        )
    print(f"\n== shot {bundle_path.stem} (fps={s.fps}, duration={s.duration_s}s, "
          f"{s.width}x{s.height}) ==", flush=True)
    manifest = build_shot(bundle_path, standards=s)
    out_dir = REPO_ROOT / "output" / "shots" / manifest["substrate_class"] / bundle_path.stem
    print(f"  frames -> {(out_dir / 'frames').relative_to(REPO_ROOT)}", flush=True)
    print(f"  preview -> {(out_dir / 'preview.mp4').relative_to(REPO_ROOT)}", flush=True)
    return manifest


def cmd_shot_all(class_filter: str | None = None) -> dict:
    if not SEED_CORPUS.is_dir():
        raise SystemExit(f"no seed corpus found at {SEED_CORPUS}. "
                         f"Run `python -m conformer.curator.walk_library` first.")
    summary: dict[str, Any] = {"shots": [], "errors": []}
    for class_dir in sorted(SEED_CORPUS.iterdir()):
        if not class_dir.is_dir():
            continue
        if class_filter and class_dir.name != class_filter:
            continue
        for bundle_path in sorted(class_dir.glob("*.bundle.json")):
            try:
                m = cmd_shot(bundle_path)
                summary["shots"].append(m)
            except Exception as e:
                summary["errors"].append({"bundle": str(bundle_path), "error": str(e)})
                print(f"  [error] {bundle_path.name}: {e}", file=sys.stderr, flush=True)
    return summary


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

    p_cmp = sub.add_parser("compare", help="three-way comparison plot (empirical / predicted / Banach RG-flow) for one bundle")
    p_cmp.add_argument("bundle", type=Path)
    p_cmp.add_argument("--out-dir", type=Path, default=None, help="override output directory (defaults to output/comparisons/<class>/)")

    p_cmp_all = sub.add_parser("compare-all", help="compare every staged bundle")
    p_cmp_all.add_argument("--class", dest="class_filter", default=None)

    p_shot = sub.add_parser("shot", help="render a shot (EXR sequence + mp4 preview) for one bundle")
    p_shot.add_argument("bundle", type=Path)
    p_shot.add_argument("--duration", dest="duration_s", type=float, default=None,
                        help="duration in seconds (default: project standard)")
    p_shot.add_argument("--fps", type=int, default=None,
                        help="frames per second (default: project standard)")
    p_shot.add_argument("--width", type=int, default=None)
    p_shot.add_argument("--height", type=int, default=None)

    p_shot_all = sub.add_parser("shot-all", help="render shots for every staged bundle")
    p_shot_all.add_argument("--class", dest="class_filter", default=None)

    p_chr = sub.add_parser(
        "test-character",
        help="run the character test suite (renders shots + generates dailies report)",
    )
    p_chr.add_argument("--filter", dest="filter_substring", default=None)

    args = ap.parse_args()

    if args.cmd == "invert":
        cmd_invert(args.bundle, skip_stage2=args.skip_stage2)
    elif args.cmd == "invert-all":
        summary = cmd_invert_all(class_filter=args.class_filter, skip_stage2=args.skip_stage2)
        args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote summary -> {args.out.relative_to(SEED_CORPUS.parent)}", flush=True)
    elif args.cmd == "compare":
        cmd_compare(args.bundle, out_dir=args.out_dir)
    elif args.cmd == "compare-all":
        summary = cmd_compare_all(class_filter=args.class_filter)
        print(f"\nrendered {len(summary['figures'])} figure(s); {len(summary['errors'])} error(s)", flush=True)
    elif args.cmd == "shot":
        cmd_shot(args.bundle, duration_s=args.duration_s, fps=args.fps,
                 width=args.width, height=args.height)
    elif args.cmd == "shot-all":
        summary = cmd_shot_all(class_filter=args.class_filter)
        print(f"\nrendered {len(summary['shots'])} shot(s); {len(summary['errors'])} error(s)", flush=True)
    elif args.cmd == "test-character":
        from conformer.tests.character.runner import run as run_character_tests
        run_character_tests(filter_substring=args.filter_substring)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
