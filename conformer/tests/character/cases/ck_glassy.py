"""Character tests for the ck-glassy substrate class.

ck-glassy character (cdv1 expectation):
  - Below Tc: aging regime. Substrate evolves slowly on observation
    timescale. Looks frozen at natural cadence; speed up to see
    slow relaxation.
  - Above Tc: r regime. Substrate decorrelates quickly within the
    window. Looks settled by mid-shot.
  - Near Tc: critical slowing. Intermediate cadence.

Tests cover three temperatures spanning these three behaviors. The
shot is the verification; the assertions ride along as sanity.
"""
from __future__ import annotations

from pathlib import Path

from conformer.shot.builder import build_shot
from conformer.shot.standards import SHOT_STANDARDS

from ..assertions import check_shot
from ..registry import CharacterTestResult, CharacterTestSpec, character_test


SEED = Path("output/seed-corpus/ck-glassy")


def _run_and_assert(spec: CharacterTestSpec) -> CharacterTestResult:
    """Default test body: build the shot, then run mechanical assertions."""
    import time as _time
    t0 = _time.perf_counter()
    try:
        manifest = build_shot(spec.bundle_path, standards=SHOT_STANDARDS)
    except Exception as e:
        return CharacterTestResult(
            spec=spec,
            passed_mechanical=False,
            failed_assertions=[f"build_shot raised: {e}"],
            runtime_s=_time.perf_counter() - t0,
            error=str(e),
        )

    from conformer.shot.builder import SHOT_OUT_ROOT
    shot_dir = SHOT_OUT_ROOT / spec.substrate_class / spec.bundle_path.stem
    preview = shot_dir / "preview.mp4"
    first_frame = next(iter(sorted((shot_dir / "frames").glob("frame_*.exr"))), None)

    passed, failures, stats = check_shot(shot_dir)
    return CharacterTestResult(
        spec=spec,
        passed_mechanical=passed,
        failed_assertions=failures,
        shot_dir=shot_dir,
        preview_mp4=preview if preview.exists() else None,
        first_frame_png=None,  # populated by runner via ffmpeg extraction
        runtime_s=_time.perf_counter() - t0,
        data_channel_stats=stats,
    )


@character_test(
    substrate_class="ck-glassy",
    bundle_path=SEED / "glass__T0.500__spin-flip.bundle.json",
    description="Below Tc (aging regime); expect slow evolution across shot.",
    expected_character=(
        "Substrate observations evolve gradually frame-to-frame. "
        "At natural cadence (10 fps) the shot will appear nearly static; "
        "speed up to perceive aging relaxation."
    ),
)
def test_ck_glassy_below_tc(spec):
    return _run_and_assert(spec)


@character_test(
    substrate_class="ck-glassy",
    bundle_path=SEED / "glass__T1.000__spin-flip.bundle.json",
    description="Near Tc (s_critical / k boundary); expect critical slowing.",
    expected_character=(
        "Substrate observations show intermediate evolution: faster than "
        "below-Tc, slower than above-Tc. Critical slowing visible across "
        "the shot."
    ),
)
def test_ck_glassy_near_tc(spec):
    return _run_and_assert(spec)


@character_test(
    substrate_class="ck-glassy",
    bundle_path=SEED / "glass__T1.500__spin-flip.bundle.json",
    description="Above Tc (r regime); expect quick decorrelation.",
    expected_character=(
        "Substrate observations settle within the first portion of the shot. "
        "Visible early decorrelation, then plateau."
    ),
)
def test_ck_glassy_above_tc(spec):
    return _run_and_assert(spec)
