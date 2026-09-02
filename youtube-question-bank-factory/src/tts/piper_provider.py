"""Piper local TTS provider (fallback engine).

Used automatically if Kokoro cannot be loaded on the current machine.
Model weights are downloaded once via scripts/download_models.py.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.tts.base import TTSProvider, TTSProviderError


class PiperProvider(TTSProvider):
    def __init__(self, model_dir: Path, voice: str):
        piper_dir = Path(model_dir) / "piper"
        model_path = piper_dir / f"{voice}.onnx"
        config_path = piper_dir / f"{voice}.onnx.json"
        if not model_path.exists() or not config_path.exists():
            raise TTSProviderError(
                f"Piper voice '{voice}' not found in {piper_dir}. Run "
                f"'python scripts/download_models.py --engine piper --piper-voice {voice}' first."
            )
        try:
            from piper import PiperVoice
        except ImportError as exc:
            raise TTSProviderError("piper-tts is not installed: pip install piper-tts") from exc

        try:
            self._voice_model = PiperVoice.load(model_path, config_path)
        except Exception as exc:  # noqa: BLE001
            raise TTSProviderError(f"Failed to load Piper voice: {exc}") from exc

        self._voice_id = voice
        self._model_path = model_path

    @property
    def engine_name(self) -> str:
        return "piper"

    @property
    def model_version(self) -> str:
        return f"piper:{self._model_path.name}"

    def synthesize(self, text: str, voice: str, speed: float) -> tuple:
        from piper import SynthesisConfig

        length_scale = 1.0 / speed if speed > 0 else 1.0
        syn_cfg = SynthesisConfig(length_scale=length_scale)
        try:
            chunks = list(self._voice_model.synthesize(text, syn_config=syn_cfg))
        except Exception as exc:  # noqa: BLE001
            raise TTSProviderError(f"Piper synthesis failed: {exc}") from exc

        if not chunks:
            return np.zeros(0, dtype=np.float32), 22050

        sr = chunks[0].sample_rate
        samples = np.concatenate([c.audio_float_array.astype(np.float32) for c in chunks])
        return samples, int(sr)
