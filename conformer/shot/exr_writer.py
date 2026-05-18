"""Multi-channel EXR frame writer (PyOpenEXR 3.x modern API).

Channel layout per mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md v1:
  - RGBA: matplotlib render (linear float in [0, 1])
  - Scale-solver channels: chit, gamma_AB, regime_label, in_gamut,
    provenance_hash, validation_flags
  - mpa-solver channels and trajectory channels: deferred to future moves
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
    rgba: np.ndarray,
    data_channels: dict[str, float],
    compression: str = "PIZ",
) -> None:
    """Write one EXR frame.

    rgba: shape (H, W, 4), float32 or convertible, in [0, 1].
    data_channels: scalar per-frame values broadcast to (H, W) planes.
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError(f"rgba must be (H, W, 4); got {rgba.shape}")
    h, w, _ = rgba.shape
    rgba_f = rgba.astype(np.float32, copy=False)

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
