"""Production reporting: the human-facing summary of a batch run.

Writes reports/production_report.json (machine-readable full summary),
reports/review_queue.csv (questions a human needs to look at, with why),
and reports/failed_items.csv (questions that hard-failed, with the stage
and error, so `retry-failed` has something concrete to act on).
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from src.job.manifest import JobManifest


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def build_review_queue(job: JobManifest) -> list:
    rows = []
    for qid in job.question_ids_by_state("needs_review"):
        validation = _load_json(job.question_dir(qid) / "validation.json")
        rows.append({
            "question_id": qid,
            "supplied_answer": validation.get("supplied_answer", ""),
            "suspected_answer": validation.get("suspected_answer", ""),
            "confidence": validation.get("confidence", ""),
            "reason": validation.get("reason", ""),
            "flags": ";".join(validation.get("flags", [])),
        })
    return rows


def build_failed_items(job: JobManifest) -> list:
    rows = []
    for qid in job.question_ids_by_state("failed"):
        state = job.state_for(qid)
        for stage_name, rec in state.stages.items():
            if rec.status == "failed":
                rows.append({
                    "question_id": qid,
                    "stage": stage_name,
                    "attempts": rec.attempts,
                    "error": rec.last_error or "",
                })
    return rows


def write_review_queue_csv(job: JobManifest, out_path: Path) -> int:
    rows = build_review_queue(job)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question_id", "supplied_answer", "suspected_answer", "confidence", "reason", "flags",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_failed_items_csv(job: JobManifest, out_path: Path) -> int:
    rows = build_failed_items(job)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question_id", "stage", "attempts", "error"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def build_production_report(job: JobManifest, audio_qa: dict | None = None, video_qa_results: list | None = None,
                             video_metadata: dict | None = None) -> dict:
    return {
        "job_id": job.job_id,
        "input_file": job.input_file,
        "generated_at": time.time(),
        "question_count": len(job.question_ids),
        "summary": job.summary(),
        "audio_qa": audio_qa,
        "video_qa": video_qa_results or [],
        "video_metadata": video_metadata,
    }


def write_production_report(job: JobManifest, out_path: Path, audio_qa: dict | None = None,
                             video_qa_results: list | None = None, video_metadata: dict | None = None) -> dict:
    report = build_production_report(job, audio_qa, video_qa_results, video_metadata)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str))
    return report
