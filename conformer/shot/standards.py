"""Project standards for shot-test artifacts.

A 'shot' is a continuous EXR sequence + ffmpeg-encoded mp4 preview.
Defaults align one cell's ~30 grinder sample-times to a 3-second shot
at 10 fps. Full rationale in docs/SHOT_STANDARDS.md.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShotStandards:
    fps: int = 10
    duration_s: float = 3.0
    width: int = 1280
    height: int = 720
    dpi: int = 100
    exr_compression: str = "PIZ"
    preview_codec: str = "libx264"
    preview_crf: int = 18
    preview_pix_fmt: str = "yuv420p"


SHOT_STANDARDS = ShotStandards()


# Five-bucket regime encoding (mpa-scale-solver EXR_CHANNEL_MANIFEST).
REGIME_ENCODING: dict[str, float] = {
    "deep_c": 0.0,
    "c_near_s": 1.0,
    "s_critical": 2.0,
    "r_near_s": 3.0,
    "deep_r": 4.0,
}
