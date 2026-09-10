"""Single-question pipeline: normalize -> validate -> explain -> narrate -> audio.

Two layers of "don't redo finished work" cooperate here:

1. A JobManifest tracks per-question, per-stage status for THIS run (what
   makes `resume`/`status`/`retry-failed` possible).
2. A content-addressed Cache (src/cache.py) stores the actual artifacts
   (validation/explanation/narration JSON, and audio files) keyed by a
   hash of everything that determines their content. This is shared
   ACROSS jobs, so if the same question_id+question text+model/voice
   config was already processed for a different video batch, it is never
   regenerated -- only copied.

A failure on one question is caught here and recorded on the manifest;
it never propagates up and stops the batch.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

from src.ai.base import AIClient, AIProviderError
from src.cache import Cache, compute_hash
from src.explanation.explainer import ExplanationAgent
from src.job.manifest import JobManifest
from src.models import (
    Explanation,
    Narration,
    NormalizedQuestion,
    StageName,
    StageStatus,
    ValidationResult,
)
from src.narration.narrator import NarrationAgent
from src.tts.base import TTSProviderError
from src.tts.voice_agent import VoiceAgent
from src.validation.validator import AnswerValidationAgent

log = logging.getLogger(__name__)

PROMPT_VERSION = "v1"  # bump to invalidate all cached explanations/validations if prompts change


def _link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


class QuestionPipeline:
    def __init__(self, cfg, cache: Cache, ai_client: AIClient, voice_agent: VoiceAgent, job: JobManifest):
        self.cfg = cfg
        self.cache = cache
        self.ai_client = ai_client
        self.voice_agent = voice_agent
        self.job = job
        self.validator = AnswerValidationAgent(ai_client, min_confidence=float(cfg.get("review.min_confidence_to_auto_pass", 0.75)))
        self.explainer = ExplanationAgent(ai_client)
        self.narrator = NarrationAgent(cfg.get("tts.pause_ms", {}))
        self.include_needs_review = bool(cfg.get("review.allow_video_for_needs_review", False))

    def run_question(self, q: NormalizedQuestion, include_needs_review: bool | None = None,
                      stop_after: str | None = None) -> dict:
        """Run the pipeline for one question up through `stop_after`
        ('validate'|'explain'|'narrate'|'audio'), or the full pipeline
        (including audio) if stop_after is None. Stages before stop_after
        are always run (cache-checked, so already-complete ones are cheap)
        because each stage depends on the previous one's output.
        """
        include_needs_review = self.include_needs_review if include_needs_review is None else include_needs_review
        qid = q.question_id
        qdir = self.job.question_dir(qid)
        self.job.mark(qid, StageName.NORMALIZE, StageStatus.COMPLETE, content_hash=compute_hash(q.to_dict()))
        (qdir / "question.json").write_text(json.dumps(q.to_dict(), indent=2))

        try:
            validation = self._stage_validate(q, qdir)
        except Exception as exc:  # noqa: BLE001
            log.error("Validation failed for %s: %s", qid, exc)
            self.job.mark(qid, StageName.VALIDATE, StageStatus.FAILED, error=str(exc))
            self.job.save()
            return {"question_id": qid, "status": "failed", "stage": "validate", "error": str(exc)}

        needs_review = validation.status == "NEEDS_REVIEW"
        self.job.mark(
            qid, StageName.VALIDATE,
            StageStatus.NEEDS_REVIEW if needs_review else StageStatus.COMPLETE,
            content_hash=compute_hash(q.to_dict(), self.ai_client.model_version, PROMPT_VERSION),
        )
        self.job.save()

        if stop_after == "validate":
            return {"question_id": qid, "status": "needs_review" if needs_review else "completed", "stage": "validate"}

        try:
            explanation = self._stage_explain(q, qdir)
        except Exception as exc:  # noqa: BLE001
            log.error("Explanation failed for %s: %s", qid, exc)
            self.job.mark(qid, StageName.EXPLAIN, StageStatus.FAILED, error=str(exc))
            self.job.save()
            return {"question_id": qid, "status": "failed", "stage": "explain", "error": str(exc)}

        self.job.mark(
            qid, StageName.EXPLAIN, StageStatus.COMPLETE,
            content_hash=compute_hash(q.to_dict(), self.ai_client.model_version, PROMPT_VERSION),
        )
        self.job.save()

        if stop_after == "explain":
            return {"question_id": qid, "status": "needs_review" if needs_review else "completed", "stage": "explain"}

        try:
            narration = self._stage_narrate(q, explanation, qdir)
        except Exception as exc:  # noqa: BLE001
            log.error("Narration failed for %s: %s", qid, exc)
            self.job.mark(qid, StageName.NARRATE, StageStatus.FAILED, error=str(exc))
            self.job.save()
            return {"question_id": qid, "status": "failed", "stage": "narrate", "error": str(exc)}

        narration_content_hash = compute_hash(explanation.to_dict(), self.cfg.get("tts.pause_ms", {}))
        self.job.mark(qid, StageName.NARRATE, StageStatus.COMPLETE, content_hash=narration_content_hash)
        self.job.save()

        if stop_after == "narrate":
            return {"question_id": qid, "status": "needs_review" if needs_review else "completed", "stage": "narrate"}

        if needs_review and not include_needs_review:
            self.job.mark(qid, StageName.AUDIO, StageStatus.SKIPPED)
            self.job.save()
            return {"question_id": qid, "status": "needs_review", "reason": validation.reason}

        try:
            audio = self._stage_audio(narration, qid)
        except Exception as exc:  # noqa: BLE001
            log.error("Audio synthesis failed for %s: %s", qid, exc)
            self.job.mark(qid, StageName.AUDIO, StageStatus.FAILED, error=str(exc))
            self.job.save()
            return {"question_id": qid, "status": "failed", "stage": "audio", "error": str(exc)}

        self.job.mark(qid, StageName.AUDIO, StageStatus.COMPLETE, content_hash=audio.narration_hash)
        self.job.save()
        return {"question_id": qid, "status": "completed", "audio": audio.to_dict()}

    # -- stages -----------------------------------------------------------

    def _stage_validate(self, q: NormalizedQuestion, qdir: Path) -> ValidationResult:
        key = compute_hash(q.to_dict(), self.ai_client.model_version, PROMPT_VERSION)
        cached = self.cache.get("validation", key)
        if cached:
            result = ValidationResult.from_dict(cached)
        else:
            result = self.validator.validate(q)
            if result.status == "ERROR":
                raise AIProviderError(result.reason)
            self.cache.set("validation", key, result.to_dict())
        (qdir / "validation.json").write_text(json.dumps(result.to_dict(), indent=2))
        return result

    def _stage_explain(self, q: NormalizedQuestion, qdir: Path) -> Explanation:
        key = compute_hash(q.to_dict(), self.ai_client.model_version, PROMPT_VERSION)
        cached = self.cache.get("explanation", key)
        if cached:
            exp = Explanation.from_dict(cached)
        else:
            exp = self.explainer.explain(q)
            self.cache.set("explanation", key, exp.to_dict())
        (qdir / "explanation.json").write_text(json.dumps(exp.to_dict(), indent=2))
        return exp

    def _stage_narrate(self, q: NormalizedQuestion, exp: Explanation, qdir: Path) -> Narration:
        key = compute_hash(exp.to_dict(), self.cfg.get("tts.pause_ms", {}))
        cached = self.cache.get("narration", key)
        if cached:
            narration = Narration.from_dict(cached)
        else:
            narration = self.narrator.narrate(q, exp, countdown_seconds=self.cfg.get("video.countdown_seconds", 5))
            self.cache.set("narration", key, narration.to_dict())
        (qdir / "narration.json").write_text(json.dumps(narration.to_dict(), indent=2))
        return narration

    def _stage_audio(self, narration: Narration, qid: str):
        voice = self.cfg.get("tts.voice", "af_heart")
        speed = float(self.cfg.get("tts.speed", 1.0))
        audio_hash = self.voice_agent.narration_hash(narration, voice, speed)
        shared_dir = self.cfg.path("paths.cache_dir") / "audio" / audio_hash

        try:
            result = self.voice_agent.synthesize_narration(narration, shared_dir)
        except TTSProviderError:
            raise

        job_audio_dir = self.job.audio_dir(qid)
        for suffix, attr in ((".wav", "wav_path"), (".mp3", "mp3_path"), (".json", None)):
            src = shared_dir / f"{qid}{suffix}"
            if src.exists():
                _link_or_copy(src, job_audio_dir / f"{qid}{suffix}")
        return result
