"""Mechanical assertions on a character test shot.

These are sanity checks. They do NOT certify that the shot shows the
right character -- that judgment lives in the dailies (human review
of the rendered preview in DJV).
"""
from __future__ import annotations

from pathlib import Path

import OpenEXR
import numpy as np


REQUIRED_DATA_CHANNELS = (
    "chit", "gamma_AB", "regime_label",
    "in_gamut", "provenance_hash", "validation_flags",
)

# Plausible ranges per channel (post-fit, for any substrate class).
CHANNEL_RANGES: dict[str, tuple[float, float]] = {
    "chit": (-3.0, 3.0),
    "gamma_AB": (-1.0, 1.0),
    "regime_label": (0.0, 4.0),
    "in_gamut": (0.0, 1.0),
    "provenance_hash": (0.0, 1.0),
    "validation_flags": (0.0, 7.0),
}


def check_shot(
    shot_dir: Path,
    *,
    expected_frame_count: int | None = None,
) -> tuple[bool, list[str], dict[str, dict[str, float]]]:
    """Run mechanical assertions on a rendered shot directory.

    Returns (passed, failures, channel_stats).
    """
    failures: list[str] = []
    stats: dict[str, list[float]] = {ch: [] for ch in REQUIRED_DATA_CHANNELS}

    frames_dir = shot_dir / "frames"
    preview = shot_dir / "preview.mp4"

    if not frames_dir.is_dir():
        failures.append(f"no frames/ directory at {frames_dir}")
        return False, failures, {}
    frame_files = sorted(frames_dir.glob("frame_*.exr"))
    if not frame_files:
        failures.append("no frame_*.exr files in frames/")
    if expected_frame_count is not None and len(frame_files) != expected_frame_count:
        failures.append(
            f"frame count {len(frame_files)} != expected {expected_frame_count}"
        )

    if not preview.exists():
        failures.append("preview.mp4 missing")
    elif preview.stat().st_size < 1024:
        failures.append(f"preview.mp4 suspiciously small ({preview.stat().st_size} bytes)")

    # Sample a subset of frames for channel checks (first, middle, last).
    if frame_files:
        sample_idxs = sorted(set([0, len(frame_files) // 2, len(frame_files) - 1]))
        for idx in sample_idxs:
            fpath = frame_files[idx]
            try:
                f = OpenEXR.File(str(fpath))
                ch_names = list(f.channels())
                for required in REQUIRED_DATA_CHANNELS:
                    if required not in ch_names:
                        failures.append(f"frame {idx}: missing channel '{required}' (saw {ch_names})")
                        continue
                    arr = np.asarray(f.channels()[required].pixels)
                    val = float(arr.flat[0])  # data channels are constant per frame in v1
                    stats[required].append(val)
                    lo, hi = CHANNEL_RANGES[required]
                    if not (lo <= val <= hi):
                        failures.append(
                            f"frame {idx}: channel '{required}' value {val} outside [{lo}, {hi}]"
                        )
                # Render channels: RGBA should be present and non-degenerate.
                rgba_names = {n for n in ch_names if n in ("R", "G", "B", "A") or n == "RGBA"}
                if not rgba_names:
                    failures.append(f"frame {idx}: no RGBA channels present")
            except Exception as e:
                failures.append(f"frame {idx}: failed to read EXR: {e}")

    channel_stats: dict[str, dict[str, float]] = {}
    for ch, vals in stats.items():
        if vals:
            channel_stats[ch] = {
                "min": float(min(vals)),
                "max": float(max(vals)),
                "mean": float(sum(vals) / len(vals)),
                "samples": len(vals),
            }

    return len(failures) == 0, failures, channel_stats
