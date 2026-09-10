"""Professional CLI for the question-bank video factory.

    python main.py ingest questions.xlsx
    python main.py produce --input questions.xlsx --video-size 60
    python main.py resume
    python main.py status
    python main.py retry-failed
    ...

Every stage command (validate/explain/narrate/voice) and `produce` share
the same batch pipeline underneath -- they only differ in how far through
the pipeline they run and whether they render/QA a video afterwards. This
is what makes "process one question" and "process a thousand questions"
literally the same code path.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import click

from src.cli.context import Runtime, get_runtime, load_questions_for_job, resolve_job
from src.job.batch import BatchProcessor
from src.models import StageName, StageStatus
from src.qa.audio_qa import run_audio_qa
from src.qa.report import write_failed_items_csv, write_production_report, write_review_queue_csv
from src.qa.video_qa import run_video_qa
from src.video.assembler import VideoAssembler, chunk_question_ids, load_curated_manifest
from src.video.renderer import VideoRenderer


def _configure_logging(cfg) -> None:
    level = getattr(logging, str(cfg.get("logging.level", "INFO")).upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _progress_printer(res: dict) -> None:
    qid = res.get("question_id")
    status = res.get("status")
    if status == "failed":
        click.echo(f"  [FAILED]       {qid}  stage={res.get('stage')}  {res.get('error', '')[:120]}")
    elif status == "needs_review":
        click.echo(f"  [NEEDS_REVIEW] {qid}  {res.get('reason', '')[:120]}")
    elif res.get("skipped"):
        click.echo(f"  [SKIPPED]      {qid}  (already complete)")
    else:
        click.echo(f"  [OK]           {qid}")


def _print_summary(summary: dict) -> None:
    click.echo("")
    click.echo("Summary: " + "  ".join(f"{k}={v}" for k, v in summary.items()))


@click.group()
def cli():
    """Local, unlimited-batch YouTube question-bank video factory."""


# -- ingest ---------------------------------------------------------------

@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def ingest(input_file):
    """Read, normalize and validate a question bank file (xlsx/csv/json)."""
    rt = get_runtime()
    _configure_logging(rt.cfg)
    from src.cli.context import ingest_and_persist

    questions, report = ingest_and_persist(rt.cfg, Path(input_file))
    click.echo(f"Rows read:      {report.total_rows}")
    click.echo(f"Accepted:       {report.accepted}")
    click.echo(f"Rejected:       {report.rejected}")
    click.echo(f"Duplicate IDs:  {len(report.duplicate_ids)}")
    click.echo(f"Duplicate text: {len(report.duplicate_questions)}")
    if report.issues:
        click.echo(f"See reports/validation_report.csv for the full issue list ({len(report.issues)} entries).")


# -- stage commands ---------------------------------------------------------

def _run_stage(input_file, batch, include_needs_review, stop_after):
    rt = get_runtime()
    _configure_logging(rt.cfg)
    job, questions = resolve_job(rt, input_file, None)
    if batch:
        questions = questions[:batch]
    bp = BatchProcessor(rt.cfg, rt.cache, rt.ai_client, rt.voice_agent, job)
    out = bp.run(questions, include_needs_review=include_needs_review, progress_cb=_progress_printer, stop_after=stop_after)
    _print_summary(out["summary"])
    return job, out


@cli.command()
@click.option("--input", "input_file", default=None, help="Question bank file (xlsx/csv/json)")
@click.option("--batch", type=int, default=None, help="Process only the first N eligible questions")
def validate(input_file, batch):
    """Run the Answer Validation Agent over the question bank."""
    _run_stage(input_file, batch, include_needs_review=True, stop_after="validate")


@cli.command()
@click.option("--input", "input_file", default=None)
@click.option("--batch", type=int, default=None)
def explain(input_file, batch):
    """Generate explanations (validate -> explain)."""
    _run_stage(input_file, batch, include_needs_review=True, stop_after="explain")


@cli.command()
@click.option("--input", "input_file", default=None)
@click.option("--batch", type=int, default=None)
def narrate(input_file, batch):
    """Generate narration scripts (validate -> explain -> narrate)."""
    _run_stage(input_file, batch, include_needs_review=True, stop_after="narrate")


@cli.command()
@click.option("--input", "input_file", default=None)
@click.option("--batch", type=int, default=None)
@click.option("--include-needs-review", is_flag=True, default=False,
              help="Also synthesize audio for questions flagged NEEDS_REVIEW")
def voice(input_file, batch, include_needs_review):
    """Synthesize local TTS audio (the full pipeline through audio)."""
    _run_stage(input_file, batch, include_needs_review=include_needs_review, stop_after=None)


# -- render -----------------------------------------------------------------

@cli.command()
@click.option("--input", "input_file", default=None)
@click.option("--job-id", default=None)
@click.option("--video-size", type=int, default=None, help="Questions per video (default from config)")
@click.option("--manifest", "manifest_path", type=click.Path(exists=True), default=None,
              help="Curated video manifest JSON ({\"title\":..., \"questions\": [ids]})")
@click.option("--template", default=None, help="Template name (default/minimal/exam)")
def render(input_file, job_id, video_size, manifest_path, template):
    """Render finished audio into one or more final MP4 videos."""
    rt = get_runtime()
    _configure_logging(rt.cfg)
    job, questions = resolve_job(rt, input_file, job_id)
    by_id = {q.question_id: q for q in questions}

    audios = _load_completed_audio(job, questions)
    if not audios:
        raise click.ClickException(
            "No completed audio found for this job. Run 'voice' or 'produce' first."
        )

    renderer = VideoRenderer(rt.cfg, template)
    assembler = VideoAssembler(rt.cfg, renderer)
    segments_dir = job.dir / "video_segments"
    videos_dir = rt.cfg.path("paths.videos_dir")

    batches = _resolve_video_batches(job, questions, manifest_path, video_size, rt.cfg)
    reports = []
    for video_id, qids, title in batches:
        ordered = [by_id[qid] for qid in qids if qid in by_id]
        click.echo(f"Rendering {video_id} ({len(ordered)} questions)...")
        report = assembler.build_video(video_id, ordered, audios, segments_dir, videos_dir, title=title)
        _mark_video_stage(job, report)
        reports.append(report)
        status = "OK" if report["final_path"] and not report["failed"] else "PARTIAL"
        click.echo(f"  [{status}] -> {report['final_path']}  included={len(report['included'])} failed={len(report['failed'])}")
    return reports


def _resolve_video_batches(job, questions, manifest_path, video_size, cfg):
    if manifest_path:
        m = load_curated_manifest(Path(manifest_path))
        video_id = Path(manifest_path).stem
        return [(video_id, m["questions"], m.get("title", video_id))]

    size = video_size or int(cfg.get("video.questions_per_video", 60))
    ids = [q.question_id for q in questions]
    chunks = chunk_question_ids(ids, size)
    return [
        (f"video_{i + 1:03d}", chunk, f"{job.job_id} part {i + 1}")
        for i, chunk in enumerate(chunks)
    ]


def _mark_video_stage(job, report: dict) -> None:
    for qid in report.get("included", []):
        job.mark(qid, StageName.VIDEO, StageStatus.COMPLETE)
    for qid in report.get("failed", []):
        job.mark(qid, StageName.VIDEO, StageStatus.FAILED, error="video segment render failed")
    job.save()


def _load_completed_audio(job, questions):
    from src.models import AudioResult

    audios = {}
    for q in questions:
        p = job.audio_dir(q.question_id) / f"{q.question_id}.json"
        if p.exists():
            data = json.loads(p.read_text())
            wav_path = job.audio_dir(q.question_id) / f"{q.question_id}.wav"
            data["wav_path"] = str(wav_path)
            audios[q.question_id] = AudioResult.from_dict(data)
    return audios


# -- qa -----------------------------------------------------------------

@cli.command()
@click.option("--input", "input_file", default=None)
@click.option("--job-id", default=None)
def qa(input_file, job_id):
    """Run audio + video QA and write the production report."""
    rt = get_runtime()
    _configure_logging(rt.cfg)
    job, questions = resolve_job(rt, input_file, job_id)
    qids = [q.question_id for q in questions]

    audio_report = run_audio_qa(job.dir, qids)
    click.echo(f"Audio QA: {audio_report['passed']}/{audio_report['total']} passed")

    video_reports = []
    reports_dir = rt.cfg.path("paths.reports_dir")

    audio_qa_path = reports_dir / "audio_qa_report.json"
    audio_qa_path.write_text(json.dumps(audio_report, indent=2))

    n_review = write_review_queue_csv(job, reports_dir / "review_queue.csv")
    n_failed = write_failed_items_csv(job, reports_dir / "failed_items.csv")
    click.echo(f"Review queue: {n_review} question(s) -> reports/review_queue.csv")
    click.echo(f"Failed items: {n_failed} question(s) -> reports/failed_items.csv")

    report = write_production_report(job, reports_dir / "production_report.json", audio_qa=audio_report, video_qa_results=video_reports)
    click.echo(f"Production report -> reports/production_report.json")
    return report


# -- produce (the one-command flow) -----------------------------------------

def _build_intro_segment(rt, job, renderer, title: str, subtitle: str, introduction: str):
    """Synthesizes the intro's spoken audio (title + subtitle only -- the
    introduction is never passed to TTS, see build_intro_narration) through
    the existing VoiceAgent, then renders the intro video segment (title +
    subtitle + introduction, all displayed) held for that audio's own
    duration -- the same "one frame held for the audio's duration" pattern
    already used for the answer-reveal frame.
    """
    from src.narration.title_narrator import build_intro_narration

    pause_cfg = rt.cfg.get("tts.pause_ms", {})
    field_pause_ms = int(pause_cfg.get("after_intro_field", 600))
    final_pause_ms = int(pause_cfg.get("after_intro", 1800))
    segment_id = f"{job.job_id}_intro"

    narration = build_intro_narration(segment_id, title, subtitle,
                                       field_pause_ms=field_pause_ms, final_pause_ms=final_pause_ms)
    audio = rt.voice_agent.synthesize_narration(narration, job.audio_dir(segment_id))
    return renderer.render_intro_segment(segment_id, title, subtitle, introduction, audio, job.dir / "video_segments")


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True))
@click.option("--video-size", type=int, default=None, help="Questions per video (default from config)")
@click.option("--manifest", "manifest_path", type=click.Path(exists=True), default=None)
@click.option("--include-needs-review", is_flag=True, default=False)
@click.option("--batch", type=int, default=None, help="Process only the first N questions this run")
@click.option("--template", default=None)
@click.option("--skip-video", is_flag=True, default=False, help="Only run audio production, skip rendering")
@click.option("--title", "video_title", default=None,
              help="Video title -- displayed on the intro screen and spoken (asked interactively if omitted)")
@click.option("--subtitle", "video_subtitle", default=None,
              help="Video subtitle -- displayed on the intro screen and spoken (asked interactively if omitted)")
@click.option("--intro-text", "video_intro_text", default=None,
              help="Short introduction -- displayed on the intro screen only, never spoken "
                   "(asked interactively if omitted)")
def produce(input_file, video_size, manifest_path, include_needs_review, batch, template, skip_video,
            video_title, video_subtitle, video_intro_text):
    """One command: ingest -> validate -> explain -> narrate -> voice ->
    render -> QA -> production report. A single question's failure never
    stops the rest of the batch."""
    rt = get_runtime()
    _configure_logging(rt.cfg)

    job, questions = resolve_job(rt, input_file, None)
    if batch:
        questions = questions[:batch]

    click.echo(f"\n== Producing {len(questions)} question(s) for job {job.job_id} ==\n")
    bp = BatchProcessor(rt.cfg, rt.cache, rt.ai_client, rt.voice_agent, job)
    out = bp.run(questions, include_needs_review=include_needs_review, progress_cb=_progress_printer)
    _print_summary(out["summary"])

    if not skip_video:
        if video_title is None:
            video_title = click.prompt("Title")
        if video_subtitle is None:
            video_subtitle = click.prompt("Subtitle")
        if video_intro_text is None:
            video_intro_text = click.prompt("Short Introduction")

        click.echo("\n== Rendering video(s) ==\n")
        audios = _load_completed_audio(job, questions)
        if audios:
            renderer = VideoRenderer(rt.cfg, template)
            assembler = VideoAssembler(rt.cfg, renderer)
            segments_dir = job.dir / "video_segments"
            videos_dir = rt.cfg.path("paths.videos_dir")
            by_id = {q.question_id: q for q in questions}
            intro_segment = _build_intro_segment(rt, job, renderer, video_title, video_subtitle, video_intro_text)
            batches = _resolve_video_batches(job, questions, manifest_path, video_size, rt.cfg)
            for video_id, qids, title in batches:
                ordered = [by_id[qid] for qid in qids if qid in by_id and qid in audios]
                if not ordered:
                    continue
                report = assembler.build_video(video_id, ordered, audios, segments_dir, videos_dir,
                                                 title=title, intro_segment=intro_segment)
                _mark_video_stage(job, report)
                click.echo(f"  {video_id}: {report['final_path']} (included={len(report['included'])}, failed={len(report['failed'])})")
        else:
            click.echo("  No completed audio yet - nothing to render.")

    click.echo("\n== QA + production report ==\n")
    qids = [q.question_id for q in questions]
    audio_report = run_audio_qa(job.dir, qids)
    reports_dir = rt.cfg.path("paths.reports_dir")
    (reports_dir / "audio_qa_report.json").write_text(json.dumps(audio_report, indent=2))
    write_review_queue_csv(job, reports_dir / "review_queue.csv")
    write_failed_items_csv(job, reports_dir / "failed_items.csv")
    video_metadata = None
    if not skip_video:
        video_metadata = {"title": video_title, "subtitle": video_subtitle, "introduction": video_intro_text}
    write_production_report(job, reports_dir / "production_report.json", audio_qa=audio_report,
                             video_metadata=video_metadata)
    click.echo(f"Audio QA: {audio_report['passed']}/{audio_report['total']} passed")
    click.echo(f"Reports written to {reports_dir}")
    click.echo(f"\nDone. Job ID: {job.job_id}")


# -- resume / status / retry-failed / review / clean-cache ----------------

@cli.command()
@click.option("--job-id", default=None, help="Defaults to the most recently touched job")
@click.option("--include-needs-review", is_flag=True, default=False)
def resume(job_id, include_needs_review):
    """Continue an interrupted job from wherever it left off."""
    rt = get_runtime()
    _configure_logging(rt.cfg)
    job, questions = resolve_job(rt, None, job_id)
    click.echo(f"Resuming job {job.job_id} ({len(questions)} question(s))")
    bp = BatchProcessor(rt.cfg, rt.cache, rt.ai_client, rt.voice_agent, job)
    out = bp.run(questions, include_needs_review=include_needs_review, progress_cb=_progress_printer)
    _print_summary(out["summary"])


@cli.command()
@click.option("--job-id", default=None)
def status(job_id):
    """Show progress for a job (or list all jobs if none specified)."""
    rt = get_runtime()
    if job_id:
        job = rt.job_store.load(job_id)
        _print_job_status(job)
        return
    jobs = rt.job_store.list_jobs()
    if not jobs:
        click.echo("No jobs found.")
        return
    for jid in jobs:
        job = rt.job_store.load(jid)
        marker = " (latest)" if jid == rt.job_store.latest_job_id() else ""
        click.echo(f"\n{jid}{marker}  [{job.input_file}]")
        _print_job_status(job, indent="  ")


def _print_job_status(job, indent=""):
    summary = job.summary()
    click.echo(f"{indent}Questions: {len(job.question_ids)}   " + "  ".join(f"{k}={v}" for k, v in summary.items()))
    failed = job.question_ids_by_state("failed")
    review = job.question_ids_by_state("needs_review")
    if failed:
        click.echo(f"{indent}Failed: {', '.join(failed[:20])}" + (" ..." if len(failed) > 20 else ""))
    if review:
        click.echo(f"{indent}Needs review: {', '.join(review[:20])}" + (" ..." if len(review) > 20 else ""))


@cli.command(name="retry-failed")
@click.option("--job-id", default=None)
@click.option("--include-needs-review", is_flag=True, default=False)
def retry_failed(job_id, include_needs_review):
    """Re-run only the questions currently in a FAILED state."""
    rt = get_runtime()
    _configure_logging(rt.cfg)
    job, questions = resolve_job(rt, None, job_id)
    failed_ids = set(job.question_ids_by_state("failed"))
    if not failed_ids:
        click.echo("No failed questions to retry.")
        return
    targets = [q for q in questions if q.question_id in failed_ids]
    click.echo(f"Retrying {len(targets)} failed question(s) in job {job.job_id}...")
    bp = BatchProcessor(rt.cfg, rt.cache, rt.ai_client, rt.voice_agent, job)
    out = bp.run(targets, include_needs_review=include_needs_review, progress_cb=_progress_printer, force=True)
    _print_summary(out["summary"])


@cli.command()
@click.option("--job-id", default=None)
def review(job_id):
    """Print the human review queue (questions flagged NEEDS_REVIEW)."""
    rt = get_runtime()
    job, questions = resolve_job(rt, None, job_id)
    from src.qa.report import build_review_queue

    rows = build_review_queue(job)
    if not rows:
        click.echo("Review queue is empty.")
        return
    for row in rows:
        click.echo(
            f"{row['question_id']}: supplied={row['supplied_answer']} "
            f"suspected={row['suspected_answer'] or '-'} confidence={row['confidence']} "
            f"reason={row['reason']}"
        )
    reports_dir = rt.cfg.path("paths.reports_dir")
    write_review_queue_csv(job, reports_dir / "review_queue.csv")
    click.echo(f"\n{len(rows)} question(s) -> reports/review_queue.csv")


@cli.command(name="clean-cache")
@click.option("--namespace", default=None, help="Only clear one cache namespace (validation/explanation/narration/audio)")
@click.option("--yes", is_flag=True, default=False, help="Skip confirmation")
def clean_cache(namespace, yes):
    """Clear the content-addressed cache (regenerable derived data only)."""
    rt = get_runtime()
    target = namespace or "ALL namespaces"
    if not yes and not click.confirm(f"Clear cache for {target}? This forces regeneration on the next run."):
        click.echo("Cancelled.")
        return
    removed = rt.cache.clear(namespace)
    click.echo(f"Removed {removed} cached file(s) from {target}.")


if __name__ == "__main__":
    cli()
