"""Batch processing: run the pipeline over many questions at once.

This is the module that makes "10 questions" and "1000 questions" the same
code path. Concurrency is bounded (default from concurrency.tts_concurrency,
since local TTS synthesis is the dominant cost) so a big batch does not
launch hundreds of simultaneous jobs. One question's failure is caught
inside QuestionPipeline.run_question and never stops the rest of the batch.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from src.ai.base import AIClient
from src.cache import Cache
from src.job.manifest import JobManifest
from src.job.pipeline import QuestionPipeline
from src.models import NormalizedQuestion
from src.tts.voice_agent import VoiceAgent

log = logging.getLogger(__name__)


class BatchProcessor:
    def __init__(self, cfg, cache: Cache, ai_client: AIClient, voice_agent: VoiceAgent, job: JobManifest):
        self.cfg = cfg
        self.job = job
        self.pipeline = QuestionPipeline(cfg, cache, ai_client, voice_agent, job)
        self.concurrency = max(1, int(cfg.get("concurrency.tts_concurrency", 2)))

    def run(self, questions: list, include_needs_review: Optional[bool] = None,
            progress_cb: Optional[Callable] = None, stop_after: Optional[str] = None,
            force: bool = False) -> dict:
        results = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_qid = {
                executor.submit(self._run_one, q, include_needs_review, stop_after, force): q.question_id
                for q in questions
            }
            for future in as_completed(future_to_qid):
                qid = future_to_qid[future]
                try:
                    res = future.result()
                except Exception as exc:  # noqa: BLE001 - guarantees one bad question never kills the batch
                    log.exception("Unexpected error processing %s", qid)
                    res = {"question_id": qid, "status": "failed", "error": str(exc)}
                results.append(res)
                if progress_cb:
                    progress_cb(res)

        return {"results": results, "summary": self.job.summary()}

    def _run_one(self, q: NormalizedQuestion, include_needs_review: Optional[bool],
                 stop_after: Optional[str], force: bool) -> dict:
        if not force:
            state = self.job.state_for(q.question_id)
            if state.overall_state() == "completed":
                return {"question_id": q.question_id, "status": "completed", "skipped": True}
        return self.pipeline.run_question(q, include_needs_review=include_needs_review, stop_after=stop_after)
