"""Multi-channel EXR frame writer (PyOpenEXR 3.x modern API).

Channel layout per mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md v1:
RGBA + scale-solver data channels. mpa-solver channels and trajectory
channels are deferred to future moves; the writer accepts arbitrary
extra channels in `data_channels` so adding them later is additive.
"""
from __future__ import annotations

from pathlib import Path

import OpenEXR
import numpy as np


COMPRESSION_LOOKUP = {
    "NO": OpenEXR.NO_COMPRESSION,
    "PIZ": OpenEXR.PIZ_COMPRESSION,
    "PXR24": OpenEXR.PXR24_COMPRESSION,
    "DWAA": OpenEXR.DWAA_COMPRESSION,
    "DWAB": OpenEXR.DWAB_COMPRESSION,
    "B44": OpenEXR.B44_COMPRESSION,
    "B44A": OpenEXR.B44A_COMPRESSION,
}


def write_frame(
    path: Path,
    *,
    rgba_linear: np.ndarray,
    data_channels: dict[str, float],
    compression: str = "PIZ",
) -> None:
    """Write one EXR frame.

    rgba_linear: (H, W, 4) array, linear scene-referred float in [0, 1].
    data_channels: scalar values broadcast to (H, W) float32 planes,
        one per named channel (e.g. {'chit': 0.3, 'gamma_AB': 0.0}).
    """
    if rgba_linear.ndim != 3 or rgba_linear.shape[2] != 4:
        raise ValueError(f"rgba must be (H, W, 4); got shape={rgba_linear.shape}")
    h, w, _ = rgba_linear.shape
    rgba_f = rgba_linear.astype(np.float32, copy=False)

    channels: dict[str, np.ndarray] = {
        "R": np.ascontiguousarray(rgba_f[:, :, 0]),
        "G": np.ascontiguousarray(rgba_f[:, :, 1]),
        "B": np.ascontiguousarray(rgba_f[:, :, 2]),
        "A": np.ascontiguousarray(rgba_f[:, :, 3]),
    }
    for name, value in data_channels.items():
        channels[name] = np.full((h, w), float(value), dtype=np.float32)

    header = {
        "compression": COMPRESSION_LOOKUP.get(
            compression.upper(), OpenEXR.PIZ_COMPRESSION
        ),
        "type": OpenEXR.scanlineimage,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    OpenEXR.File(header, channels).write(str(path))


def srgb_to_linear(srgb_u8: np.ndarray) -> np.ndarray:
    """Convert sRGB-encoded uint8 (matplotlib output) to linear float32.

    Inverse of the sRGB transfer function. EXR stores scene-linear data;
    matplotlib renders sRGB; this bridges them so the mp4 preview from
    ffmpeg reads back the colors the matplotlib renderer drew.
    """
    s = srgb_u8.astype(np.float32) / 255.0
    cutoff = 0.04045
    low = s / 12.92
    high = np.power((s + 0.055) / 1.055, 2.4)
    return np.where(s <= cutoff, low, high)
