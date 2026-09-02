"""TTS provider factory with automatic primary -> fallback failover.

TTS_PROVIDER=kokoro (default) or piper. If the primary engine cannot be
loaded on this machine (missing model files, missing package, unsupported
platform), the fallback engine is used automatically and a warning is
logged -- the batch keeps moving instead of hard-failing.
"""
from __future__ import annotations

import logging

from src.config import Config
from src.tts.base import TTSProvider, TTSProviderError

log = logging.getLogger(__name__)

_BUILDERS = {}


def _build(name: str, cfg: Config) -> TTSProvider:
    model_dir = cfg.path("tts.model_dir")
    if name == "kokoro":
        from src.tts.kokoro_provider import KokoroProvider
        return KokoroProvider(model_dir, lang=cfg.get("tts.lang", "en-us"))
    if name == "piper":
        from src.tts.piper_provider import PiperProvider
        return PiperProvider(model_dir, voice=cfg.get("tts.piper_voice", cfg.get("tts.voice", "en_US-lessac-medium")))
    raise TTSProviderError(f"Unknown TTS provider '{name}'. Use kokoro|piper.")


def build_tts_provider(cfg: Config) -> TTSProvider:
    primary = cfg.get("tts.provider", "kokoro")
    fallback = cfg.get("tts.fallback_provider", "piper")

    try:
        return _build(primary, cfg)
    except TTSProviderError as exc:
        log.warning("Primary TTS provider '%s' unavailable (%s); falling back to '%s'", primary, exc, fallback)

    if fallback and fallback != primary:
        try:
            return _build(fallback, cfg)
        except TTSProviderError as exc:
            raise TTSProviderError(
                f"Both primary TTS provider '{primary}' and fallback '{fallback}' failed to load. "
                f"Last error: {exc}. Run scripts/download_models.py to fetch model weights."
            ) from exc

    raise TTSProviderError(f"TTS provider '{primary}' failed to load and no fallback is configured.")
