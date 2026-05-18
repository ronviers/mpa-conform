"""ffmpeg subprocess wrapper: EXR sequence -> mp4 preview.

ffmpeg has an EXR demuxer but no EXR encoder. Pipeline is:
  Python writes EXR per-frame (data substrate)
  -> ffmpeg reads EXR sequence (exr_pipe demuxer)
  -> emits mp4 preview (h264 yuv420p)

EXR files remain canonical; mp4 is throwaway preview for review.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def encode_preview_from_exr_sequence(
    *,
    exr_pattern: Path,
    out_mp4: Path,
    fps: int,
    codec: str = "libx264",
    crf: int = 18,
    pix_fmt: str = "yuv420p",
) -> dict:
    """Encode an EXR image sequence to mp4 via ffmpeg.

    exr_pattern: e.g. .../frames/frame_%05d.exr (ffmpeg-style sprintf).
    Returns the ffmpeg invocation dict (command, returncode, stderr tail).
    """
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH")
    cmd = [
        ffmpeg,
        "-y",
        "-framerate", str(fps),
        "-i", str(exr_pattern),
        # EXR is scene-linear; tag input as such and let ffmpeg convert
        # to sRGB-on-encode for visually-correct mp4 preview.
        "-vf", "zscale=transfer=linear:matrix=709:primaries=709:range=full,"
               "zscale=transfer=iec61966-2-1:matrix=709:primaries=709:range=full,"
               "format=yuv420p",
        "-c:v", codec,
        "-crf", str(crf),
        "-pix_fmt", pix_fmt,
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        # Fall back to a simpler pipeline if zscale isn't available.
        cmd_fallback = [
            ffmpeg,
            "-y",
            "-framerate", str(fps),
            "-gamma", "2.2",
            "-i", str(exr_pattern),
            "-c:v", codec,
            "-crf", str(crf),
            "-pix_fmt", pix_fmt,
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-movflags", "+faststart",
            str(out_mp4),
        ]
        proc = subprocess.run(cmd_fallback, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed (rc={proc.returncode}):\n{proc.stderr[-2000:]}"
            )
        return {"cmd": cmd_fallback, "returncode": proc.returncode,
                "stderr_tail": proc.stderr[-400:], "fallback": True}
    return {"cmd": cmd, "returncode": proc.returncode,
            "stderr_tail": proc.stderr[-400:], "fallback": False}
