"""Content-addressed cache shared by every expensive pipeline stage.

Design: every cacheable artifact (normalized question, validation result,
explanation, narration, TTS audio) is stored under a hash derived from
*everything that determines its content* -- the inputs plus the
configuration that produced it (model id, voice, speed, prompt version...).
If none of those inputs changed, the stage is skipped entirely. This is
what makes "change the voice, don't regenerate the explanation" and
"resume after a crash without redoing finished work" work for free: the
hash for finished stages already matches, so they're skipped again.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional


def compute_hash(*parts: Any) -> str:
    """Stable hash over an arbitrary sequence of hashable/JSON-able parts."""
    h = hashlib.sha256()
    for part in parts:
        if isinstance(part, (dict, list, tuple)):
            h.update(json.dumps(part, sort_keys=True, default=str).encode("utf-8"))
        else:
            h.update(str(part).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:24]


class Cache:
    """Namespaced on-disk JSON cache: data/cache/<namespace>/<key>.json"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str, key: str) -> Path:
        ns_dir = self.cache_dir / namespace
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{key}.json"

    def get(self, namespace: str, key: str) -> Optional[dict]:
        p = self._path(namespace, key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, namespace: str, key: str, value: dict) -> None:
        p = self._path(namespace, key)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(value, indent=2, default=str))
        tmp.replace(p)

    def has(self, namespace: str, key: str) -> bool:
        return self._path(namespace, key).exists()

    def clear(self, namespace: Optional[str] = None) -> int:
        """Delete cached entries. Returns count removed."""
        targets = [self.cache_dir / namespace] if namespace else list(self.cache_dir.glob("*"))
        removed = 0
        for target in targets:
            if not target.exists():
                continue
            for f in target.glob("*.json"):
                f.unlink()
                removed += 1
        return removed
