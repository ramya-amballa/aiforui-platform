"""Per-video QA: is this assembled video actually production-complete?

Checked per spec section 18: every expected question is included, all
audio existed for them, the video file exists and renders, its duration
is plausible, and ffmpeg reported no fatal errors during assembly (a
RenderError raised during assembly already surfaces that; this re-verifies
the output file independently via ffprobe).
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _ffprobe_duration(path: Path) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        return 0.0
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def run_video_qa(video_report: dict, expected_question_ids: list, min_seconds_per_question: float = 5.0) -> dict:
    issues = []
    final_path = video_report.get("final_path")

    missing = [qid for qid in expected_question_ids if qid not in video_report.get("included", [])]
    if missing:
        issues.append(f"{len(missing)} expected question(s) not included: {', '.join(missing[:10])}")

    if video_report.get("failed"):
        issues.append(f"{len(video_report['failed'])} question(s) failed to render: {', '.join(video_report['failed'][:10])}")

    if not final_path or not Path(final_path).exists():
        issues.append("final video file does not exist")
        return {"video_id": video_report.get("video_id"), "passed": False, "issues": issues, "duration_seconds": 0}

    duration = _ffprobe_duration(Path(final_path))
    if duration <= 0:
        issues.append("ffprobe could not read a valid duration (video may be corrupt)")

    expected_min = len(video_report.get("included", [])) * min_seconds_per_question
    if duration < expected_min:
        issues.append(
            f"video duration ({duration:.1f}s) is implausibly short for "
            f"{len(video_report.get('included', []))} questions (expected at least {expected_min:.0f}s)"
        )

    return {
        "video_id": video_report.get("video_id"),
        "passed": len(issues) == 0,
        "issues": issues,
        "duration_seconds": duration,
        "included_count": len(video_report.get("included", [])),
    }
