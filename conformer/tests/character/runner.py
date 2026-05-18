"""Character test runner: renders all registered shots, generates HTML report.

Usage:
    python -m conformer.tests.character.runner
    python -m conformer.tests.character.runner --filter ck-glassy

Output: output/tests/character/<timestamp>/ with one shot per test plus
index.html (the dailies report) and results.json (machine-readable).
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .registry import CharacterTestResult, all_tests


REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_ROOT = REPO_ROOT / "output" / "tests" / "character"


def _extract_first_frame_png(shot_dir: Path, out_dir: Path) -> Path | None:
    """Pull frame 0 of the shot's EXR sequence to PNG via ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return None
    frames = sorted((shot_dir / "frames").glob("frame_*.exr"))
    if not frames:
        return None
    png_out = out_dir / "first_frame.png"
    proc = subprocess.run(
        [ffmpeg, "-y", "-i", str(frames[0]), "-update", "1", "-frames:v", "1",
         "-gamma", "2.2", str(png_out)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return png_out


def render_report(results: list[CharacterTestResult], out_dir: Path) -> Path:
    """Generate index.html: a grid of test cards with embedded mp4 previews."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []
    passed_count = sum(1 for r in results if r.passed_mechanical)

    for r in results:
        status_class = "pass" if r.passed_mechanical else "fail"
        status_label = "PASS" if r.passed_mechanical else "FAIL"
        preview_html = ""
        if r.preview_mp4 and r.preview_mp4.exists():
            rel = r.preview_mp4.resolve().as_uri()
            preview_html = (
                f'<video src="{rel}" controls loop muted '
                f'style="width:100%; max-width:560px; background:#000;"></video>'
            )
        first_frame_html = ""
        if r.first_frame_png and r.first_frame_png.exists():
            rel = r.first_frame_png.resolve().as_uri()
            first_frame_html = (
                f'<img src="{rel}" alt="frame 0" '
                f'style="width:100%; max-width:560px;"/>'
            )
        failures_html = ""
        if r.failed_assertions:
            items = "".join(f"<li>{html.escape(f)}</li>" for f in r.failed_assertions)
            failures_html = f'<details open><summary>failures</summary><ul>{items}</ul></details>'
        stats_html = ""
        if r.data_channel_stats:
            rows = "".join(
                f"<tr><td>{html.escape(k)}</td><td>{v['min']:.4g}</td>"
                f"<td>{v['mean']:.4g}</td><td>{v['max']:.4g}</td></tr>"
                for k, v in r.data_channel_stats.items()
            )
            stats_html = (
                "<details><summary>data channels</summary>"
                "<table><tr><th>channel</th><th>min</th><th>mean</th><th>max</th></tr>"
                f"{rows}</table></details>"
            )
        expected_html = ""
        if r.spec.expected_character:
            expected_html = (
                f'<details><summary>expected character</summary>'
                f'<p>{html.escape(r.spec.expected_character)}</p></details>'
            )

        cards.append(f"""
        <div class="card {status_class}">
          <header>
            <span class="status">{status_label}</span>
            <span class="id">{html.escape(r.spec.test_id)}</span>
            <span class="runtime">{r.runtime_s:.1f}s</span>
          </header>
          <p class="desc">{html.escape(r.spec.description)}</p>
          {preview_html or first_frame_html}
          {expected_html}
          {failures_html}
          {stats_html}
        </div>""")

    style = """
    body { font-family: -apple-system, sans-serif; margin: 20px; background: #f6f7f9; color: #222; }
    h1 { margin: 0 0 4px 0; }
    .summary { color: #555; margin-bottom: 18px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(560px, 1fr)); gap: 16px; }
    .card { background: white; border-radius: 6px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .card.pass { border-left: 4px solid #2a8f4a; }
    .card.fail { border-left: 4px solid #b13a3a; }
    .card header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
    .card .status { font-weight: 700; }
    .card.pass .status { color: #2a8f4a; }
    .card.fail .status { color: #b13a3a; }
    .card .id { font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: #444; }
    .card .runtime { font-size: 12px; color: #888; }
    .desc { margin: 4px 0 10px 0; font-size: 13px; color: #333; }
    details { margin-top: 8px; font-size: 12px; }
    table { border-collapse: collapse; margin-top: 4px; }
    th, td { padding: 2px 8px; border: 1px solid #ddd; text-align: right; font-family: ui-monospace, monospace; font-size: 11px; }
    th { background: #f0f0f0; }
    """

    body = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>character test dailies</title>
<style>{style}</style></head><body>
<h1>character test dailies</h1>
<p class="summary">{passed_count}/{len(results)} mechanical · rendered {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="grid">{''.join(cards)}</div>
</body></html>"""

    index = out_dir / "index.html"
    index.write_text(body, encoding="utf-8")
    return index


def run(filter_substring: str | None = None) -> Path:
    timestamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    run_dir = RESULTS_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    specs = all_tests()
    if filter_substring:
        specs = [s for s in specs if filter_substring in s.test_id
                 or filter_substring in s.substrate_class]

    results: list[CharacterTestResult] = []
    for spec in specs:
        print(f"\n== {spec.test_id} ({spec.substrate_class}) ==", flush=True)
        try:
            r = spec.fn(spec)
        except Exception as e:
            r = CharacterTestResult(
                spec=spec, passed_mechanical=False,
                failed_assertions=[f"test fn raised: {e}"], error=str(e),
            )
        per_test_dir = run_dir / spec.test_id
        per_test_dir.mkdir(parents=True, exist_ok=True)
        if r.shot_dir is not None:
            r.first_frame_png = _extract_first_frame_png(r.shot_dir, per_test_dir)
        status = "PASS" if r.passed_mechanical else "FAIL"
        print(f"  {status}  ({r.runtime_s:.1f}s)", flush=True)
        for fail in r.failed_assertions:
            print(f"    - {fail}", flush=True)
        results.append(r)

    # Machine-readable results.
    results_json = run_dir / "results.json"
    results_json.write_text(json.dumps([{
        "test_id": r.spec.test_id,
        "substrate_class": r.spec.substrate_class,
        "passed_mechanical": r.passed_mechanical,
        "failed_assertions": r.failed_assertions,
        "shot_dir": str(r.shot_dir) if r.shot_dir else None,
        "preview_mp4": str(r.preview_mp4) if r.preview_mp4 else None,
        "first_frame_png": str(r.first_frame_png) if r.first_frame_png else None,
        "runtime_s": r.runtime_s,
        "data_channel_stats": r.data_channel_stats,
        "expected_character": r.spec.expected_character,
        "error": r.error,
    } for r in results], indent=2), encoding="utf-8")

    index = render_report(results, run_dir)

    passed = sum(1 for r in results if r.passed_mechanical)
    print(f"\n{passed}/{len(results)} passed mechanical assertions", flush=True)
    print(f"dailies report: {index.resolve().as_uri()}", flush=True)
    return index


def main() -> None:
    ap = argparse.ArgumentParser(prog="conformer.tests.character.runner")
    ap.add_argument("--filter", dest="filter_substring", default=None,
                    help="run only tests whose id or substrate_class contains this substring")
    args = ap.parse_args()
    run(filter_substring=args.filter_substring)


if __name__ == "__main__":
    main()
