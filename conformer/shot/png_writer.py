"""EXR (linear float) -> PNG (sRGB 8-bit) via OpenImageIO.

OIIO is the canonical pipeline tool for color-space handling (see
RENDERING_DISCIPLINE.md and the conform/auditor file-import boundary).
This module is a thin wrapper that does the linear->sRGB encoding and
writes a PNG suitable for direct viewing or for the dailies HTML index.

No tonemapping in v1 -- just clamp + sRGB EOTF. HDR pileups from the
additive splat get clipped at white. Document when a tonemap pass earns
its way in.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np


def _linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    """Apply the sRGB encoding transfer function (piecewise, not the
    gamma-2.2 approximation)."""
    clipped = np.clip(linear, 0.0, 1.0)
    return np.where(
        clipped <= 0.0031308,
        12.92 * clipped,
        1.055 * np.power(clipped, 1.0 / 2.4) - 0.055,
    )


def write_png_from_rgba_linear(
    rgba_linear: np.ndarray,
    out_path: Path,
    *,
    backend: str = "auto",
) -> dict:
    """Write 8-bit sRGB PNG from linear RGBA float.

    Parameters
    ----------
    rgba_linear : (H, W, 4) float32 array, linear scene-referred.
    out_path : path to write the PNG (parent created if needed).
    backend : "auto" (default; OIIO if available, manual fallback otherwise),
              "oiio" (force OIIO), or "manual" (force the numpy sRGB encoder).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if backend in ("auto", "oiio"):
        try:
            import OpenImageIO as oiio
            h, w, c = rgba_linear.shape
            if c != 4:
                raise ValueError(f"expected 4 channels, got {c}")
            spec = oiio.ImageSpec(w, h, 4, "float")
            spec.attribute("oiio:ColorSpace", "scene_linear")
            buf = oiio.ImageBuf(spec)
            buf.set_pixels(
                oiio.ROI(0, w, 0, h, 0, 1, 0, 4),
                rgba_linear.astype(np.float32, copy=False),
            )
            # Convert scene_linear -> sRGB color space.
            srgb_buf = oiio.ImageBufAlgo.colorconvert(
                buf, "scene_linear", "sRGB"
            )
            # Write as 8-bit PNG.
            out_spec = oiio.ImageSpec(w, h, 4, "uint8")
            out_spec.attribute("oiio:ColorSpace", "sRGB")
            wrote = srgb_buf.write(str(out_path), "uint8")
            if not wrote:
                raise RuntimeError(
                    f"OIIO write failed: {srgb_buf.geterror()}"
                )
            return {"backend": "oiio", "path": str(out_path),
                    "size": (w, h)}
        except ImportError:
            if backend == "oiio":
                raise
            # Fall through to manual.

    # Manual fallback: numpy sRGB encoding + PNG via PyOpenEXR's sibling
    # (we keep this minimal; OIIO is the expected backend).
    srgb = _linear_to_srgb(rgba_linear[..., :3])
    alpha = np.clip(rgba_linear[..., 3], 0.0, 1.0)
    rgba_srgb = np.dstack([srgb, alpha])
    rgba_u8 = (rgba_srgb * 255.0).astype(np.uint8)
    # PNG write without imageio: use OIIO for the write step too if reachable,
    # else raise -- we keep the codepath honest.
    try:
        import OpenImageIO as oiio
        h, w, _ = rgba_u8.shape
        spec = oiio.ImageSpec(w, h, 4, "uint8")
        spec.attribute("oiio:ColorSpace", "sRGB")
        buf = oiio.ImageBuf(spec)
        buf.set_pixels(oiio.ROI(0, w, 0, h, 0, 1, 0, 4), rgba_u8)
        wrote = buf.write(str(out_path), "uint8")
        if not wrote:
            raise RuntimeError(f"OIIO write failed: {buf.geterror()}")
        return {"backend": "manual+oiio_writer", "path": str(out_path),
                "size": (w, h)}
    except ImportError:
        raise RuntimeError(
            "OpenImageIO not available and no PNG writer fallback installed; "
            "the canonical pipeline expects OIIO."
        )
