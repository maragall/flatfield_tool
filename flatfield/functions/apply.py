from __future__ import annotations

"""
Batch flat-field correction.

Usage (library):
    >>> from image_stitcher.flatfield.apply import apply_flatfields
    >>> apply_flatfields(Path("…/flatfield_manifest.json"), [Path("/raw1"), Path("/raw2")])
"""

import concurrent.futures
import json
import logging
from pathlib import Path
from typing import Callable, Mapping, Optional
import numpy as np
from skimage.io import imread, imsave
from flatfield.parameters import extract_channel

__all__ = ["apply_flatfields"]


# ─── helpers ────────────────────────────────────────────────────────────────
def _load_profiles(src: Path) -> Mapping[str, np.ndarray]:
    """Return a channel→flatfield mapping from *src* (manifest or folder)."""
    if src.is_file() and src.suffix == ".json":
        meta = json.loads(src.read_text())
        base = src.parent
        return {ch: np.load(base / fname) for ch, fname in meta["files"].items()}
    # Directory case
    return {p.stem.split("_")[-1]: np.load(p) for p in src.glob("flatfield_*.npy")}


# ─── public API ─────────────────────────────────────────────────────────────
def apply_flatfields(
    flatfield_source: Path,
    acq_dirs: list[Path],
    out_dirs: Optional[list[Path]] = None,
    *,
    suffix: str = "_ff",
    progress_cb: Callable[[int, int], None] | None = None,
) -> Path:
    """
    Apply pre-computed flat-field profiles to every TIFF in *acq_dirs*.

    Returns the first output directory (for GUI status).
    """
    ff_map = _load_profiles(flatfield_source)

    # decide output folders
    if out_dirs is not None:
        if len(out_dirs) != len(acq_dirs):
            raise ValueError("out_dirs must match length of acq_dirs")
        target_dirs = out_dirs
    else:
        target_dirs = [acq.with_name(acq.name + suffix) for acq in acq_dirs]

    for out_root in target_dirs:
        out_root.mkdir(parents=True, exist_ok=True)

    for acq, out_root in zip(acq_dirs, target_dirs):
        tifs   = list(Path(acq).rglob("*.tif*"))
        total  = len(tifs)
        logging.info("Correcting %d images in %s → %s", total, acq, out_root)

        def _process(p: Path) -> int:
            img        = imread(p)
            ch         = extract_channel(p.stem)
            ff         = ff_map.get(ch)
            if ff is None:
                logging.warning("No flatfield for channel '%s' (%s) — skipped", ch, p.name)
                return 0

            mean_ff    = ff.mean()
            corrected  = img / ff * mean_ff

            # restore original dtype + safe clipping
            orig_dtype = img.dtype
            if np.issubdtype(orig_dtype, np.integer):
                info = np.iinfo(orig_dtype)
            else:
                info = np.finfo(orig_dtype)
            corrected = np.clip(corrected, info.min, info.max).astype(orig_dtype)

            dst = out_root / p.relative_to(acq)
            dst.parent.mkdir(parents=True, exist_ok=True)
            imsave(dst, corrected, check_contrast=False)
            return 1

        done = 0
        with concurrent.futures.ThreadPoolExecutor() as exe:
            for processed in exe.map(_process, tifs):
                done += processed
                if progress_cb:
                    progress_cb(done, total)

    return target_dirs[0]
