"""Audio assembly helpers: silence insertion, concatenation, WAV/MP3 output."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def silence(ms: int, sample_rate: int) -> np.ndarray:
    if ms <= 0:
        return np.zeros(0, dtype=np.float32)
    n = int(sample_rate * ms / 1000)
    return np.zeros(n, dtype=np.float32)


def write_wav(samples: np.ndarray, sample_rate: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), samples, sample_rate)


def wav_to_mp3(wav_path: Path, mp3_path: Path, bitrate: str = "128k") -> None:
    from pydub import AudioSegment

    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    audio = AudioSegment.from_wav(str(wav_path))
    audio.export(str(mp3_path), format="mp3", bitrate=bitrate)


def duration_seconds(samples: np.ndarray, sample_rate: int) -> float:
    return len(samples) / float(sample_rate) if sample_rate else 0.0
