"""Shared setup helpers for every CLI command: load config, resolve the
question bank + job, build the (cached, lazily-loaded) runtime services.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from src.ai.base import AIClient
from src.ai.factory import get_ai_client
from src.cache import Cache
from src.config import Config, load_config
from src.ingestion.intake import QuestionIntake
from src.job.manifest import JobManifest, JobStore
from src.models import NormalizedQuestion
from src.tts.voice_agent import VoiceAgent


class Runtime:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.cache = Cache(cfg.path("paths.cache_dir"))
        self._ai_client: Optional[AIClient] = None
        self._voice_agent: Optional[VoiceAgent] = None
        self.job_store = JobStore(cfg.path("paths.jobs_dir"))

    @property
    def ai_client(self) -> AIClient:
        if self._ai_client is None:
            self._ai_client = get_ai_client(self.cfg)
        return self._ai_client

    @property
    def voice_agent(self) -> VoiceAgent:
        if self._voice_agent is None:
            self._voice_agent = VoiceAgent(self.cfg)
        return self._voice_agent


def get_runtime() -> Runtime:
    return Runtime(load_config())


def normalized_path(cfg: Config, input_file: Path) -> Path:
    return cfg.path("paths.normalized_dir") / f"{Path(input_file).stem}.json"


def ingest_and_persist(cfg: Config, input_file: Path) -> tuple:
    """Ingest an input file and persist the normalized questions + error
    report to disk, so later commands (resume/status/render/qa) can find
    the question bank again without the caller re-passing --input.
    """
    result = QuestionIntake().process(input_file)
    QuestionIntake.write_normalized(result.questions, normalized_path(cfg, input_file))
    QuestionIntake.write_error_report(result.report, cfg.path("paths.reports_dir") / "validation_report.csv")

    issues_path = cfg.path("paths.processed_dir") / f"{Path(input_file).stem}_ingestion_report.json"
    issues_path.parent.mkdir(parents=True, exist_ok=True)
    issues_path.write_text(json.dumps(result.report.to_dict(), indent=2, default=str))

    return result.questions, result.report


def load_questions_for_job(cfg: Config, job: JobManifest) -> list:
    """Reload NormalizedQuestion objects for a job from its cached
    normalized-question snapshot (works even if the original input file
    has since moved or been deleted -- resume never depends on that)."""
    np = normalized_path(cfg, Path(job.input_file))
    if not np.exists():
        raise click.ClickException(
            f"No normalized question snapshot found for job {job.job_id} at {np}. "
            f"Re-run with --input pointing at the original question bank file."
        )
    all_qs = {q.question_id: q for q in QuestionIntake.load_normalized(np)}
    return [all_qs[qid] for qid in job.question_ids if qid in all_qs]


def resolve_job(rt: Runtime, input_file: Optional[str], job_id: Optional[str]) -> tuple:
    """Returns (job, questions). Resolves in priority order: explicit
    --job-id, else --input (creating/resuming the matching job), else the
    most recently touched job."""
    if job_id:
        job = rt.job_store.load(job_id)
        return job, load_questions_for_job(rt.cfg, job)

    if input_file:
        path = Path(input_file)
        if not path.exists():
            raise click.ClickException(f"Input file not found: {input_file}")
        questions, report = ingest_and_persist(rt.cfg, path)
        if report.rejected:
            click.echo(
                f"WARNING: {report.rejected} of {report.total_rows} rows were rejected "
                f"(see reports/validation_report.csv)", err=True,
            )
        job, created = rt.job_store.find_or_create(path, [q.question_id for q in questions])
        click.echo(f"Job {job.job_id} ({'created' if created else 'resumed'}) - {len(questions)} question(s)")
        return job, questions

    latest = rt.job_store.latest_job_id()
    if not latest:
        raise click.ClickException("No --input given and no previous job found. Run 'ingest' or pass --input.")
    job = rt.job_store.load(latest)
    return job, load_questions_for_job(rt.cfg, job)
