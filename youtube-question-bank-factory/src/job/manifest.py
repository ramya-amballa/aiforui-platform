"""Persistent job state: the thing that makes the batch resumable.

A "job" is one run of the pipeline over a set of question IDs drawn from
one input file. Its manifest.json on disk is the single source of truth
for what stage every question has reached. Re-running the same input file
(same filename + same question IDs) resolves to the *same* job_id, so
`python main.py process --input questions.xlsx` is naturally idempotent:
run it, kill it, run it again -- it picks up where it left off with no
extra flags and no re-work on already-completed questions.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Iterable, Optional

from src.cache import compute_hash
from src.models import QuestionJobState, StageName, StageStatus


class JobManifest:
    def __init__(
        self,
        job_id: str,
        jobs_dir: Path,
        input_file: str,
        question_ids: list,
        created_at: Optional[float] = None,
    ):
        self.job_id = job_id
        self.jobs_dir = Path(jobs_dir)
        self.dir = self.jobs_dir / job_id
        self.input_file = input_file
        self.question_ids = list(question_ids)
        self.created_at = created_at or time.time()
        self.updated_at = self.created_at
        self.questions: dict = {qid: QuestionJobState(question_id=qid) for qid in question_ids}
        self._lock = threading.RLock()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        (self.dir / "content").mkdir(parents=True, exist_ok=True)
        (self.dir / "audio").mkdir(parents=True, exist_ok=True)

    def question_dir(self, question_id: str) -> Path:
        d = self.dir / "content" / question_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def audio_dir(self, question_id: str) -> Path:
        d = self.dir / "audio" / question_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def state_for(self, question_id: str) -> QuestionJobState:
        if question_id not in self.questions:
            self.questions[question_id] = QuestionJobState(question_id=question_id)
        return self.questions[question_id]

    def mark(self, question_id: str, stage: StageName, status: StageStatus,
             content_hash: Optional[str] = None, error: Optional[str] = None) -> None:
        with self._lock:
            state = self.state_for(question_id)
            rec = state.get(stage)
            rec.status = status.value
            rec.updated_at = time.time()
            if content_hash is not None:
                rec.content_hash = content_hash
            if status == StageStatus.FAILED:
                rec.attempts += 1
                rec.last_error = error
            elif status == StageStatus.COMPLETE:
                rec.last_error = None
            self.updated_at = time.time()

    def stage_status(self, question_id: str, stage: StageName) -> str:
        return self.state_for(question_id).get(stage).status

    def is_stage_done(self, question_id: str, stage: StageName, content_hash: Optional[str] = None) -> bool:
        rec = self.state_for(question_id).get(stage)
        if rec.status != StageStatus.COMPLETE.value:
            return False
        if content_hash is not None and rec.content_hash != content_hash:
            return False
        return True

    def question_ids_by_state(self, state: str) -> list:
        return [qid for qid, qs in self.questions.items() if qs.overall_state() == state]

    def summary(self) -> dict:
        counts = {"completed": 0, "failed": 0, "needs_review": 0, "skipped": 0, "pending": 0}
        for qs in self.questions.values():
            counts[qs.overall_state()] = counts.get(qs.overall_state(), 0) + 1
        return counts

    # -- persistence ---------------------------------------------------

    def manifest_path(self) -> Path:
        return self.dir / "manifest.json"

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "input_file": self.input_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "question_ids": self.question_ids,
            "questions": {qid: qs.to_dict() for qid, qs in self.questions.items()},
        }

    def save(self) -> None:
        with self._lock:
            self.updated_at = time.time()
            tmp = self.manifest_path().with_suffix(".tmp")
            tmp.write_text(json.dumps(self.to_dict(), indent=2, default=str))
            tmp.replace(self.manifest_path())

    @staticmethod
    def load(path: Path) -> "JobManifest":
        data = json.loads(Path(path).read_text())
        jm = JobManifest(
            job_id=data["job_id"],
            jobs_dir=Path(path).parent.parent,
            input_file=data["input_file"],
            question_ids=data["question_ids"],
            created_at=data.get("created_at"),
        )
        jm.updated_at = data.get("updated_at", jm.created_at)
        jm.questions = {
            qid: QuestionJobState.from_dict(qd) for qid, qd in data.get("questions", {}).items()
        }
        return jm


class JobStore:
    def __init__(self, jobs_dir: Path):
        self.jobs_dir = Path(jobs_dir)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_job_id(input_file: Path, question_ids: Iterable[str]) -> str:
        return "job_" + compute_hash(Path(input_file).name, sorted(question_ids))

    def find_or_create(self, input_file: Path, question_ids: list) -> tuple:
        """Returns (JobManifest, created: bool)."""
        job_id = self.compute_job_id(input_file, question_ids)
        manifest_path = self.jobs_dir / job_id / "manifest.json"
        if manifest_path.exists():
            jm = JobManifest.load(manifest_path)
            # Grow the job if new question IDs were added to the input file.
            new_ids = [qid for qid in question_ids if qid not in jm.questions]
            if new_ids:
                for qid in new_ids:
                    jm.questions[qid] = QuestionJobState(question_id=qid)
                jm.question_ids = list(jm.questions.keys())
            self._set_latest(job_id)
            return jm, False
        jm = JobManifest(job_id, self.jobs_dir, str(input_file), question_ids)
        jm.save()
        self._set_latest(job_id)
        return jm, True

    def _set_latest(self, job_id: str) -> None:
        (self.jobs_dir / "LATEST").write_text(job_id)

    def latest_job_id(self) -> Optional[str]:
        p = self.jobs_dir / "LATEST"
        return p.read_text().strip() if p.exists() else None

    def load(self, job_id: str) -> JobManifest:
        return JobManifest.load(self.jobs_dir / job_id / "manifest.json")

    def list_jobs(self) -> list:
        return sorted(
            [p.name for p in self.jobs_dir.iterdir() if p.is_dir() and (p / "manifest.json").exists()]
        )
