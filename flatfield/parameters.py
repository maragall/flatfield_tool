"""
Flat-field branch — minimal helpers only.

Anything related to stitching, pyramids, scan patterns, or Pydantic CLI
is removed.  We just need:

  • extract_channel(filename)   – shared across compute/apply

If later we discover extra helpers are needed we’ll add them here,
but keep this module < 50 lines.
"""

from __future__ import annotations
from pathlib import Path


# -------------------------------------------------------------------------
# Utilities shared by flatfield.compute / flatfield.apply
# -------------------------------------------------------------------------

def extract_channel(stem: str) -> str:
    """
    Parse a filename stem like ``R0_3_0_Fluorescence_488_nm_Ex`` and return a
    short channel token: ``'488'``, ``'R'``, ``'G'``, ``'B'``, etc.
    Falls back to ``'unknown'`` if nothing obvious is found.
    """
    parts = stem.split("_")
    for token in reversed(parts):
        if token.isdigit() or token.upper() in {"R", "G", "B"}:
            return token
    return "unknown"
