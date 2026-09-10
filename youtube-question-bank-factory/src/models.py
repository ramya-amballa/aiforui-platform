"""Core data structures shared across the pipeline.

Kept deliberately dependency-free (stdlib dataclasses only) so every stage
-- ingestion, validation, explanation, narration, TTS, video -- can import
this module without pulling in another stage's dependencies.
"""
from __future__ import annotations

import dataclasses
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------

VALID_OPTION_KEYS = ("A", "B", "C", "D")


@dataclass
class NormalizedQuestion:
    """The internal representation every downstream stage consumes.

    This is produced once by the ingestion module and is never mutated by
    later stages -- validation/explanation/narration/TTS all read it but
    write their own separate artifacts.
    """

    question_id: str
    question: str
    options: dict  # {"A": str, "B": str, "C": str, "D": str}
    correct_answer: str  # "A" | "B" | "C" | "D"
    topic: str = ""
    difficulty: str = ""
    source: str = ""
    notes: str = ""
    row_number: Optional[int] = None  # original row in the input file, for error reports

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "NormalizedQuestion":
        return NormalizedQuestion(
            question_id=d["question_id"],
            question=d["question"],
            options=dict(d["options"]),
            correct_answer=d["correct_answer"],
            topic=d.get("topic", ""),
            difficulty=d.get("difficulty", ""),
            source=d.get("source", ""),
            notes=d.get("notes", ""),
            row_number=d.get("row_number"),
        )


@dataclass
class IngestionIssue:
    row_number: Optional[int]
    question_id: Optional[str]
    severity: str  # "error" | "warning"
    message: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class IngestionReport:
    total_rows: int
    accepted: int
    rejected: int
    duplicate_ids: list
    duplicate_questions: list
    issues: list  # list[IngestionIssue]

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationStatus(str, Enum):
    PASS = "PASS"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    ERROR = "ERROR"


@dataclass
class ValidationResult:
    question_id: str
    status: str  # ValidationStatus value
    confidence: float
    supplied_answer: str
    suspected_answer: Optional[str] = None
    reason: str = ""
    flags: list = field(default_factory=list)  # e.g. ["ambiguous", "outdated", "source_verification_needed"]
    checked_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "ValidationResult":
        return ValidationResult(**d)


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------

@dataclass
class Explanation:
    question_id: str
    correct_answer: str
    why_correct: str
    why_options: dict  # {"A": str, "B": str, "C": str, "D": str}
    key_takeaway: str
    exam_tip: str = ""
    generated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Explanation":
        return Explanation(**d)

    def is_complete(self) -> bool:
        if not self.why_correct or not self.key_takeaway:
            return False
        for key in VALID_OPTION_KEYS:
            if not self.why_options.get(key):
                return False
        return True


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------

@dataclass
class NarrationSegment:
    kind: str  # "question" | "option" | "pause" | "reveal" | "explanation" | "takeaway"
    text: str
    option_key: Optional[str] = None
    pause_ms: int = 0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class Narration:
    question_id: str
    segments: list  # list[NarrationSegment]
    full_text: str
    generated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Narration":
        segs = [NarrationSegment(**s) for s in d["segments"]]
        return Narration(
            question_id=d["question_id"],
            segments=segs,
            full_text=d["full_text"],
            generated_at=d.get("generated_at", time.time()),
        )


# ---------------------------------------------------------------------------
# Audio / timing
# ---------------------------------------------------------------------------

@dataclass
class TimingCue:
    label: str  # "question" | "option_A" | ... | "countdown" | "reveal" | "explanation" | "takeaway"
    start_seconds: float
    end_seconds: float

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class AudioResult:
    question_id: str
    wav_path: str
    mp3_path: Optional[str]
    duration_seconds: float
    sample_rate: int
    voice: str
    speed: float
    tts_provider: str
    model_version: str
    narration_hash: str
    cues: list  # list[TimingCue]
    generated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d

    @staticmethod
    def from_dict(d: dict) -> "AudioResult":
        cues = [TimingCue(**c) for c in d.get("cues", [])]
        d2 = dict(d)
        d2["cues"] = cues
        return AudioResult(**d2)


# ---------------------------------------------------------------------------
# Pipeline / job state
# ---------------------------------------------------------------------------

class StageName(str, Enum):
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    EXPLAIN = "explain"
    NARRATE = "narrate"
    AUDIO = "audio"
    VIDEO = "video"
    QA = "qa"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    SKIPPED = "skipped"


ALL_STAGES = [
    StageName.NORMALIZE,
    StageName.VALIDATE,
    StageName.EXPLAIN,
    StageName.NARRATE,
    StageName.AUDIO,
]


@dataclass
class StageRecord:
    status: str = StageStatus.PENDING.value
    attempts: int = 0
    last_error: Optional[str] = None
    content_hash: Optional[str] = None
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "StageRecord":
        return StageRecord(**d)


@dataclass
class QuestionJobState:
    question_id: str
    stages: dict = field(default_factory=dict)  # stage_name -> StageRecord

    def get(self, stage: StageName) -> StageRecord:
        key = stage.value if isinstance(stage, StageName) else stage
        if key not in self.stages:
            self.stages[key] = StageRecord()
        return self.stages[key]

    def overall_state(self) -> str:
        vals = [r.status for r in self.stages.values()]
        if any(v == StageStatus.FAILED.value for v in vals):
            return "failed"
        if any(v == StageStatus.NEEDS_REVIEW.value for v in vals):
            return "needs_review"
        if vals and all(v == StageStatus.COMPLETE.value for v in vals):
            return "completed"
        if any(v == StageStatus.SKIPPED.value for v in vals):
            return "skipped"
        return "pending"

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
        }

    @staticmethod
    def from_dict(d: dict) -> "QuestionJobState":
        stages = {k: StageRecord.from_dict(v) for k, v in d.get("stages", {}).items()}
        return QuestionJobState(question_id=d["question_id"], stages=stages)
