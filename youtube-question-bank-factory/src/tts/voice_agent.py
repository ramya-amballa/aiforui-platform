"""The Voice Agent: the stable interface the rest of the app talks to.

    VoiceAgent(cfg, cache).synthesize_narration(narration, out_dir)

Nothing else in the codebase imports kokoro_onnx or piper directly. Swapping
TTS_PROVIDER never touches ingestion, validation, explanation, narration,
video rendering, or QA.

Responsibilities implemented here (per spec section 9):
  - batch synthesis (called once per question by the batch pipeline)
  - WAV output + MP3 conversion
  - configurable voice / speed / sample rate
  - pauses between narration segments
  - retry on transient synthesis failure
  - content-hash based caching so unchanged narration+voice+speed+model
    is never re-synthesized
  - deterministic filenames (Q001.wav / Q001.mp3 / Q001.json)
  - resume after interruption (a completed, hash-matching file is reused)
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np

from src.cache import compute_hash
from src.config import Config
from src.models import AudioResult, Narration, TimingCue
from src.tts.audio_utils import duration_seconds, silence, wav_to_mp3, write_wav
from src.tts.base import TTSProvider, TTSProviderError
from src.tts.factory import build_tts_provider

log = logging.getLogger(__name__)


class VoiceAgent:
    def __init__(self, cfg: Config, provider: TTSProvider | None = None):
        self.cfg = cfg
        self._provider = provider
        self.max_retries = int(cfg.get("pipeline.max_retries_per_stage", 2))
        self.retry_backoff = float(cfg.get("pipeline.retry_backoff_seconds", 3))

    def provider(self) -> TTSProvider:
        if self._provider is None:
            self._provider = build_tts_provider(self.cfg)
        return self._provider

    def _synthesize_segment(self, text: str, voice: str, speed: float) -> tuple:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                return self.provider().synthesize(text, voice, speed)
            except TTSProviderError as exc:
                last_exc = exc
                log.warning("TTS synthesis attempt %d failed: %s", attempt, exc)
                if attempt <= self.max_retries:
                    time.sleep(self.retry_backoff * attempt)
        raise TTSProviderError(f"TTS synthesis failed after retries: {last_exc}") from last_exc

    def narration_hash(self, narration: Narration, voice: str, speed: float) -> str:
        seg_fingerprint = [(s.kind, s.text, s.pause_ms) for s in narration.segments]
        return compute_hash(
            narration.full_text, seg_fingerprint, voice, speed, self.provider().model_version
        )

    def synthesize_narration(self, narration: Narration, out_dir: Path, write_mp3: bool = True) -> AudioResult:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        qid = narration.question_id
        voice = self.cfg.get("tts.voice", "af_heart")
        speed = float(self.cfg.get("tts.speed", 1.0))

        wav_path = out_dir / f"{qid}.wav"
        mp3_path = out_dir / f"{qid}.mp3"
        timing_path = out_dir / f"{qid}.json"

        target_hash = self.narration_hash(narration, voice, speed)

        cached = self._load_cached(timing_path, wav_path, target_hash)
        if cached is not None:
            log.info("Audio for %s unchanged (hash match) - skipping re-synthesis", qid)
            return cached

        all_chunks: list = []
        cues: list = []
        cursor = 0.0
        sample_rate = int(self.cfg.get("tts.sample_rate", 24000))

        for seg in narration.segments:
            samples, sr = self._synthesize_segment(seg.text, voice, speed)
            sample_rate = sr
            seg_dur = duration_seconds(samples, sr)
            cues.append(TimingCue(label=self._cue_label(seg), start_seconds=cursor, end_seconds=cursor + seg_dur))
            all_chunks.append(samples)
            cursor += seg_dur

            if seg.pause_ms:
                pause = silence(seg.pause_ms, sr)
                all_chunks.append(pause)
                cursor += seg.pause_ms / 1000.0

        full_audio = np.concatenate(all_chunks) if all_chunks else np.zeros(0, dtype=np.float32)
        write_wav(full_audio, sample_rate, wav_path)

        if write_mp3:
            wav_to_mp3(wav_path, mp3_path, bitrate=self.cfg.get("tts.mp3_bitrate", "128k"))

        result = AudioResult(
            question_id=qid,
            wav_path=str(wav_path),
            mp3_path=str(mp3_path) if write_mp3 else None,
            duration_seconds=duration_seconds(full_audio, sample_rate),
            sample_rate=sample_rate,
            voice=voice,
            speed=speed,
            tts_provider=self.provider().engine_name,
            model_version=self.provider().model_version,
            narration_hash=target_hash,
            cues=cues,
        )
        timing_path.write_text(_result_to_json(result))
        return result

    @staticmethod
    def _cue_label(seg) -> str:
        if seg.option_key and seg.kind == "option":
            return f"option_{seg.option_key}"
        if seg.option_key and seg.kind == "explanation":
            return f"explanation_{seg.option_key}"
        return seg.kind

    def _load_cached(self, timing_path: Path, wav_path: Path, target_hash: str) -> AudioResult | None:
        if not timing_path.exists() or not wav_path.exists():
            return None
        try:
            import json
            data = json.loads(timing_path.read_text())
        except (OSError, ValueError):
            return None
        if data.get("narration_hash") != target_hash:
            return None
        return AudioResult.from_dict(data)


def _result_to_json(result: AudioResult) -> str:
    import json
    return json.dumps(result.to_dict(), indent=2, default=str)
