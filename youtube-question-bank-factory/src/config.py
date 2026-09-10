"""Configuration loading: config.yaml + environment variable overrides.

Precedence (highest wins): environment variable > .env file > config.yaml > default.
No secrets ever live in config.yaml; only .env / real environment variables.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Never let a .env value clobber a real environment variable.
        os.environ.setdefault(key, value)


def _dig(d: dict, dotted: str) -> Any:
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _set(d: dict, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


# Env var name -> dotted config path, and a caster.
_ENV_OVERRIDES = {
    "AI_PROVIDER": ("ai.provider", str),
    "AI_MODEL": ("ai.model", str),
    "TTS_PROVIDER": ("tts.provider", str),
    "TTS_FALLBACK_PROVIDER": ("tts.fallback_provider", str),
    "TTS_VOICE": ("tts.voice", str),
    "TTS_SPEED": ("tts.speed", float),
    "TTS_CONCURRENCY": ("concurrency.tts_concurrency", int),
    "AI_CONCURRENCY": ("concurrency.ai_concurrency", int),
    "RENDER_CONCURRENCY": ("concurrency.render_concurrency", int),
    "VIDEO_TEMPLATE": ("video.template", str),
    "QUESTIONS_PER_VIDEO": ("video.questions_per_video", int),
    "LOG_LEVEL": ("logging.level", str),
}


class Config:
    def __init__(self, data: dict, root: Path):
        self._data = data
        self.root = root

    def get(self, dotted: str, default: Any = None) -> Any:
        val = _dig(self._data, dotted)
        return default if val is None else val

    def path(self, dotted: str) -> Path:
        raw = self.get(dotted)
        p = Path(raw)
        return p if p.is_absolute() else self.root / p

    def as_dict(self) -> dict:
        return self._data

    def __getitem__(self, dotted: str) -> Any:
        return self.get(dotted)


def load_config(config_path: Path | None = None, env_path: Path | None = None) -> Config:
    root = PROJECT_ROOT
    config_path = config_path or (root / "config.yaml")
    env_path = env_path or (root / ".env")

    _load_dotenv(env_path)

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    for env_name, (dotted, caster) in _ENV_OVERRIDES.items():
        raw = os.environ.get(env_name)
        if raw is not None and raw != "":
            _set(data, dotted, caster(raw))

    cfg = Config(data, root)

    for key in ("input_dir", "normalized_dir", "processed_dir", "jobs_dir", "videos_dir", "reports_dir", "logs_dir", "cache_dir"):
        cfg.path(f"paths.{key}").mkdir(parents=True, exist_ok=True)

    return cfg


_default_config: Config | None = None


def get_config() -> Config:
    global _default_config
    if _default_config is None:
        _default_config = load_config()
    return _default_config
