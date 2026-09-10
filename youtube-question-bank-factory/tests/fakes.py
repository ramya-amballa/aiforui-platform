"""Test doubles. FakeTTSProvider avoids loading a real Kokoro/Piper model
in unit tests (slow, multi-hundred-MB) while still exercising the real
VoiceAgent/pipeline/caching code paths. Real-model integration is covered
separately (verified manually against the actual downloaded Kokoro model;
see SETUP.md)."""
from __future__ import annotations

import numpy as np

from src.tts.base import TTSProvider


class FakeTTSProvider(TTSProvider):
    """Deterministic, near-instant 'synthesis': duration scales with text
    length so audio-QA duration checks and timing cues behave realistically."""

    def __init__(self, sample_rate: int = 8000, fail_on: set | None = None):
        self.sample_rate = sample_rate
        self.calls = 0
        self.fail_on = fail_on or set()
        self.texts: list = []  # every text string handed to synthesize(), in call order

    def synthesize(self, text: str, voice: str, speed: float) -> tuple:
        self.calls += 1
        self.texts.append(text)
        if text in self.fail_on:
            from src.tts.base import TTSProviderError
            raise TTSProviderError(f"simulated failure for: {text!r}")
        duration = max(0.05, len(text) / 40.0 / speed)
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        samples = (0.05 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
        return samples, self.sample_rate

    @property
    def engine_name(self) -> str:
        return "fake"

    @property
    def model_version(self) -> str:
        return "fake-v1"
