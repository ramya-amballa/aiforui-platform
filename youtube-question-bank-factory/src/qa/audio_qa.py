"""Per-question QA: is this question actually production-complete?

Checked before a question is considered done, per spec section 18:
question/options/answer exist, explanation exists and agrees in shape
with the answer (all four options addressed), narration exists, audio
exists with a real playable duration, no assets are missing.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.models import Explanation, MIN_OPTION_COUNT


def check_question(job_dir: Path, question_id: str) -> dict:
    issues = []
    content_dir = job_dir / "content" / question_id
    audio_dir = job_dir / "audio" / question_id

    question_path = content_dir / "question.json"
    if not question_path.exists():
        issues.append("missing question.json")
        return {"question_id": question_id, "passed": False, "issues": issues}
    q = json.loads(question_path.read_text())

    # A question may have more than four options (E, F, ...) -- only a
    # minimum of four (A-D) is required, never an exact-four cap.
    if len(q.get("options", {})) < MIN_OPTION_COUNT:
        issues.append(f"question has fewer than {MIN_OPTION_COUNT} options")
    if q.get("correct_answer") not in q.get("options", {}):
        issues.append("correct_answer is not one of this question's own options")

    exp_path = content_dir / "explanation.json"
    if not exp_path.exists():
        issues.append("missing explanation.json")
    else:
        exp = Explanation.from_dict(json.loads(exp_path.read_text()))
        if not exp.is_complete():
            issues.append("explanation is incomplete (missing why_correct/key_takeaway/why_options)")
        elif exp.correct_answer != q.get("correct_answer"):
            issues.append("explanation.correct_answer does not match question.correct_answer")

    narration_path = content_dir / "narration.json"
    if not narration_path.exists():
        issues.append("missing narration.json")
    else:
        narration = json.loads(narration_path.read_text())
        if not narration.get("segments"):
            issues.append("narration has no segments")

    wav_path = audio_dir / f"{question_id}.wav"
    mp3_path = audio_dir / f"{question_id}.mp3"
    timing_path = audio_dir / f"{question_id}.json"
    if not wav_path.exists() and not mp3_path.exists():
        issues.append("no audio file (wav or mp3) found")
    if not timing_path.exists():
        issues.append("missing audio timing manifest")
    else:
        timing = json.loads(timing_path.read_text())
        duration = timing.get("duration_seconds", 0)
        if not duration or duration <= 0:
            issues.append("audio duration is zero or missing")
        if not _is_audio_playable(wav_path if wav_path.exists() else mp3_path):
            issues.append("audio file failed to open/decode")

    return {"question_id": question_id, "passed": len(issues) == 0, "issues": issues}


def _is_audio_playable(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        import soundfile as sf
        info = sf.info(str(path))
        return info.frames > 0
    except Exception:
        # mp3 support in libsndfile varies by build; fall back to ffprobe.
        return _ffprobe_playable(path)


def _ffprobe_playable(path: Path) -> bool:
    import subprocess
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return proc.returncode == 0 and float(proc.stdout.strip() or 0) > 0
    except Exception:
        return False


def run_audio_qa(job_dir: Path, question_ids: list) -> dict:
    results = [check_question(job_dir, qid) for qid in question_ids]
    return {
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
