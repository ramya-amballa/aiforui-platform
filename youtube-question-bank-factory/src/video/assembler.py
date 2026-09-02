"""Video batching: turn a set of per-question segments into one final MP4.

Two ways to group questions into a video, per spec section 15:
  - size-based split of the whole question pool (Q001-060, Q061-120, ...)
  - a curated manifest naming specific question_ids and a title

Neither duplicates question data -- a video is just an ordered list of
question_ids resolved against the same normalized question bank and the
same cached audio/video segments.
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from src.video.renderer import RenderError, VideoRenderer

log = logging.getLogger(__name__)


def chunk_question_ids(question_ids: list, size: int) -> list:
    return [question_ids[i:i + size] for i in range(0, len(question_ids), size)]


def load_curated_manifest(path: Path) -> dict:
    data = json.loads(Path(path).read_text())
    if "questions" not in data:
        raise ValueError(f"Curated manifest {path} is missing a 'questions' list")
    return data


class VideoAssembler:
    def __init__(self, cfg, renderer: VideoRenderer):
        self.cfg = cfg
        self.renderer = renderer

    def build_video(self, video_id: str, questions: list, audios: dict,
                     segments_dir: Path, videos_dir: Path, title: str = "") -> dict:
        """questions: list[NormalizedQuestion] in the desired order.
        audios: {question_id: AudioResult}.
        Returns a report dict with per-question outcomes and the final path.
        """
        segment_paths = []
        failed = []
        for q in questions:
            audio = audios.get(q.question_id)
            if audio is None:
                failed.append(q.question_id)
                continue
            try:
                seg_path = self.renderer.render_question_segment(q, audio, segments_dir)
                segment_paths.append(seg_path)
            except RenderError as exc:
                log.error("Video segment render failed for %s: %s", q.question_id, exc)
                failed.append(q.question_id)

        out_dir = videos_dir / video_id
        out_dir.mkdir(parents=True, exist_ok=True)
        final_path = out_dir / "final.mp4"

        if not segment_paths:
            return {"video_id": video_id, "final_path": None, "included": [], "failed": failed}

        list_path = out_dir / "segments.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in segment_paths))

        proc = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(final_path)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            # Fall back to re-encoding if a stream-copy concat fails
            # (e.g. segments produced by an older template/codec settings).
            proc2 = subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-f", "concat", "-safe", "0", "-i", str(list_path),
                 "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac",
                 str(final_path)],
                capture_output=True, text=True,
            )
            if proc2.returncode != 0:
                raise RenderError(f"Final video assembly failed: {proc2.stderr.strip()[-2000:]}")

        return {
            "video_id": video_id,
            "title": title,
            "final_path": str(final_path),
            "included": [q.question_id for q in questions if q.question_id not in failed],
            "failed": failed,
        }
