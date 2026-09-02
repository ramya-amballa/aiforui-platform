"""Cross-platform font resolution for the Pillow-based frame renderer.

Templates reference fonts by friendly family name (e.g. "DejaVu Sans Bold").
This resolves that name to an actual .ttf/.otf file on whatever OS the
renderer is running on, searching common system font directories, and
falls back to Pillow's built-in bitmap font (with a warning) rather than
crashing if nothing matches -- video rendering must never hard-fail just
because a font isn't installed.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

log = logging.getLogger(__name__)

_SEARCH_DIRS = [
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path("/Library/Fonts"),          # macOS
    Path("/System/Library/Fonts"),   # macOS
    Path("C:/Windows/Fonts"),        # Windows
]

_NAME_HINTS = {
    "DejaVu Sans Bold": ["DejaVuSans-Bold.ttf"],
    "DejaVu Sans": ["DejaVuSans.ttf"],
    "DejaVu Serif Bold": ["DejaVuSerif-Bold.ttf"],
    "DejaVu Serif": ["DejaVuSerif.ttf"],
}


@lru_cache(maxsize=None)
def _find_font_file(family: str) -> str | None:
    p = Path(family)
    if p.exists():
        return str(p)

    filenames = _NAME_HINTS.get(family, [family.replace(" ", "") + ".ttf"])
    for root in _SEARCH_DIRS:
        if not root.exists():
            continue
        for filename in filenames:
            for match in root.rglob(filename):
                return str(match)
    return None


@lru_cache(maxsize=None)
def load_font(family: str, size: int):
    path = _find_font_file(family)
    if path:
        return ImageFont.truetype(path, size)
    log.warning("Font '%s' not found on this system; falling back to default bitmap font", family)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()
