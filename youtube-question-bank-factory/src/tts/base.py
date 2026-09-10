"""Local Voice Agent provider interface.

Every TTS engine (Kokoro, Piper, ...) implements this. Nothing outside
src/tts/ knows or cares which engine produced the audio -- that is the
whole point of making Kokoro a replaceable provider rather than something
hard-coded through the application.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class TTSProviderError(Exception):
    """Raised when a local TTS engine cannot load or synthesize."""


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str, speed: float) -> tuple:
        """Return (samples: np.ndarray float32 mono, sample_rate: int)."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Included in the narration/audio content hash so a model change
        (e.g. swapping voice packs) correctly invalidates cached audio."""
