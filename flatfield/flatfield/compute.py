from __future__ import annotations

"""
Flat-field profile generator (BaSiC based).

Usage (library):
    >>> from image_stitcher.flatfield.compute import compute_flatfields
    >>> manifest = compute_flatfields(Path("/path/to/acq"))
"""

import json
import logging
import random
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from basicpy import BaSiC
from skimage.io import imread
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize

from flatfield.parameters import extract_channel

__all__ = ["compute_flatfields"]

# ─── keep constants identical to the reference logic ─────────────────────────
MAX_FLATFIELD_IMAGES = 48          # total per channel
MAX_FLATFIELD_IMAGES_PER_T = 32    # (retained for API symmetry)

# ─── main API ────────────────────────────────────────────────────────────────
def compute_flatfields(
    acq_dir: Path,
    *,
    max_per_channel: int = MAX_FLATFIELD_IMAGES,
    out_dir: Optional[Path] = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> Path:
    """
    Compute and persist BaSiC flat-field arrays & quick-look PNGs for every
    channel in *acq_dir*.  Returns the manifest path.

    Parameters
    ----------
    acq_dir : Path
        Directory tree of raw TIFF images.
    max_per_channel : int
        Upper bound on images fed to BaSiC per channel.
    out_dir : Path | None
        Override output folder.  Defaults to ``acq_dir/flatfields``.
    progress_cb : callable | None
        Optional ``progress_cb(done, total)`` for UI updates.
    """
    acq_dir = Path(acq_dir)
    out_dir = (out_dir or acq_dir / "flatfields").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── gather TIFFs by channel ────────────────────────────────────────────
    channel_tiles: dict[str, list[Path]] = {}
    for tif in acq_dir.rglob("*.tif*"):
        ch = extract_channel(tif.stem)
        channel_tiles.setdefault(ch, []).append(tif)

    manifest: dict[str, object] = {"channels": [], "files": {}}
    total = len(channel_tiles)
    done = 0

    for ch, all_files in channel_tiles.items():
        random.shuffle(all_files)
        stack_files = all_files[: max_per_channel]

        stack = np.stack([imread(p) for p in stack_files]).astype(np.float32)
        logging.info(
            "BaSiC fit on channel '%s' (n=%d of %d)", ch, len(stack_files), len(all_files)
        )

        basic = BaSiC(get_darkfield=False, smoothness_flatfield=1)
        basic.fit(stack)
        ff = basic.flatfield.astype(np.float32)

        npy_path = out_dir / f"flatfield_{ch}.npy"
        np.save(npy_path, ff)

        # ── quick-look PNG with adaptive, crisp colorbar ──────────────────
        png_path = out_dir / f"flatfield_{ch}.png"
        _write_preview_png(ff, png_path)

        manifest["channels"].append(ch)
        manifest["files"][ch] = npy_path.name

        done += 1
        if progress_cb:
            progress_cb(done, total)

    manifest_path = out_dir / "flatfield_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    logging.info("Wrote manifest → %s", manifest_path)
    return manifest_path


# ─── helpers ────────────────────────────────────────────────────────────────
def _write_preview_png(ff: np.ndarray, png_path: Path) -> None:
    """Save *ff* as a PNG with an adaptive colorbar (crisp @ 300 DPI)."""
    cmap = cm.get_cmap("viridis")
    norm = Normalize(vmin=0, vmax=float(ff.max()))
    rgba = cmap(norm(ff))                       # H×W×4 floats in [0, 1]
    rgb  = (rgba[..., :3] * 255).astype(np.uint8)

    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
    ax.imshow(rgb, interpolation="nearest")
    ax.axis("off")

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(labelsize=8)
    fig.tight_layout(pad=0.5)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)
