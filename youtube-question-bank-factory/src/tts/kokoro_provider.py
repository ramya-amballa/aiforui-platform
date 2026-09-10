"""Kokoro local TTS provider (primary engine).

Uses kokoro-onnx, a lightweight ONNX runtime build of Kokoro that avoids
the heavier PyTorch install path. Model weights are downloaded once via
scripts/download_models.py and never touched over the network again.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.tts.base import TTSProvider, TTSProviderError

DEFAULT_MODEL_FILE = "kokoro-v1.0.onnx"
DEFAULT_VOICES_FILE = "voices-v1.0.bin"


class KokoroProvider(TTSProvider):
    def __init__(self, model_dir: Path, lang: str = "en-us"):
        model_path = Path(model_dir) / DEFAULT_MODEL_FILE
        voices_path = Path(model_dir) / DEFAULT_VOICES_FILE
        if not model_path.exists() or not voices_path.exists():
            raise TTSProviderError(
                f"Kokoro model files not found in {model_dir}. Run "
                f"'python scripts/download_models.py --engine kokoro' first."
            )
        try:
            from kokoro_onnx import Kokoro
        except ImportError as exc:
            raise TTSProviderError(
                "kokoro-onnx is not installed: pip install kokoro-onnx"
            ) from exc

        try:
            self._kokoro = Kokoro(str(model_path), str(voices_path))
        except Exception as exc:  # noqa: BLE001
            raise TTSProviderError(f"Failed to load Kokoro model: {exc}") from exc

        self._lang = lang
        self._model_path = model_path

    @property
    def engine_name(self) -> str:
        return "kokoro"

    @property
    def model_version(self) -> str:
        return f"kokoro-onnx:{self._model_path.name}"

    def synthesize(self, text: str, voice: str, speed: float) -> tuple:
        try:
            samples, sr = self._kokoro.create(text, voice=voice, speed=speed, lang=self._lang)
        except Exception as exc:  # noqa: BLE001
            raise TTSProviderError(f"Kokoro synthesis failed: {exc}") from exc
        return np.asarray(samples, dtype=np.float32), int(sr)
