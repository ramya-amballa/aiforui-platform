"""Deterministic FFmpeg-based video renderer.

For each question this builds a short sequence of static/near-static
frames (question+options, an animated countdown, then the answer
revealed) sized exactly to the audio's own timing cues, and muxes them
with the narration audio via ffmpeg. No LLM is involved in generating the
video -- only the template's own configured visuals and the question's
own text.

Per-question segments are cached by a hash of (question, template,
resolution, fps, audio content hash), the same pattern used for audio, so
re-rendering with a different template does not require regenerating the
narration, and re-running an unfinished batch does not re-render segments
that already exist.
"""
from __future__ import annotations

import logging
import math
import subprocess
from pathlib import Path

from src.cache import compute_hash
from src.models import AudioResult, NormalizedQuestion
from src.video.frames import render_question_frame

log = logging.getLogger(__name__)


class RenderError(Exception):
    pass


def _run_ffmpeg(args: list) -> None:
    proc = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RenderError(f"ffmpeg failed (exit {proc.returncode}): {proc.stderr.strip()[-2000:]}")


class VideoRenderer:
    def __init__(self, cfg, template_name: str | None = None):
        from src.video.templates import load_template

        self.cfg = cfg
        self.template_name = template_name or cfg.get("video.template", "default")
        self.template = load_template(self.template_name)
        self.resolution = tuple(cfg.get("video.resolution", [1920, 1080]))
        self.fps = int(cfg.get("video.fps", 30))
        self.countdown_seconds = float(cfg.get("video.countdown_seconds", 5))

    def segment_hash(self, q: NormalizedQuestion, audio: AudioResult) -> str:
        return compute_hash(
            q.to_dict(), self.template, self.resolution, self.fps, audio.narration_hash
        )

    def render_question_segment(self, q: NormalizedQuestion, audio: AudioResult, out_dir: Path) -> Path:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        seg_hash = self.segment_hash(q, audio)
        out_path = out_dir / f"{q.question_id}.mp4"
        marker = out_dir / f"{q.question_id}.hash"

        if out_path.exists() and marker.exists() and marker.read_text().strip() == seg_hash:
            log.info("Video segment for %s unchanged - skipping re-render", q.question_id)
            return out_path

        frames_dir = out_dir / f"_frames_{q.question_id}"
        frames_dir.mkdir(parents=True, exist_ok=True)
        try:
            plan = self._build_frame_plan(q, audio)
            list_path = self._write_frames(plan, frames_dir)
            self._encode(list_path, Path(audio.wav_path), out_path)
        finally:
            for f in frames_dir.glob("*"):
                f.unlink()
            frames_dir.rmdir()

        marker.write_text(seg_hash)
        return out_path

    # -- internals ----------------------------------------------------

    def _cue(self, audio: AudioResult, label: str):
        for c in audio.cues:
            if c.label == label:
                return c
        return None

    def _build_frame_plan(self, q: NormalizedQuestion, audio: AudioResult) -> list:
        """Returns [(PIL.Image, duration_seconds), ...] covering the full
        audio duration with no gaps."""
        countdown_cue = self._cue(audio, "countdown")
        reveal_cue = self._cue(audio, "reveal")
        total = audio.duration_seconds

        countdown_start = countdown_cue.end_seconds if countdown_cue else total * 0.4
        reveal_start = reveal_cue.start_seconds if reveal_cue else countdown_start + self.countdown_seconds

        plan = []

        question_frame = render_question_frame(self.template, self.resolution, q)
        plan.append((question_frame, max(countdown_start, 0.1)))

        countdown_gap = max(reveal_start - countdown_start, 0.0)
        n_ticks = max(1, math.ceil(countdown_gap))
        for i in range(n_ticks):
            remaining = max(1, round(self.countdown_seconds) - i)
            tick_frame = render_question_frame(self.template, self.resolution, q, timer_text=str(remaining))
            tick_duration = countdown_gap / n_ticks if n_ticks else countdown_gap
            plan.append((tick_frame, max(tick_duration, 0.05)))

        reveal_frame = render_question_frame(
            self.template, self.resolution, q, highlight_key=q.correct_answer, show_banner=True
        )
        reveal_duration = max(total - reveal_start, 0.5)
        plan.append((reveal_frame, reveal_duration))

        return plan

    def _write_frames(self, plan: list, frames_dir: Path) -> Path:
        list_path = frames_dir / "list.txt"
        lines = []
        for i, (image, duration) in enumerate(plan):
            fname = f"frame_{i:04d}.png"
            image.save(frames_dir / fname)
            lines.append(f"file '{fname}'")
            lines.append(f"duration {duration:.3f}")
        # ffmpeg's concat demuxer ignores the final duration unless the
        # last file is repeated once more without one.
        if plan:
            last_fname = f"frame_{len(plan) - 1:04d}.png"
            lines.append(f"file '{last_fname}'")
        list_path.write_text("\n".join(lines))
        return list_path

    def _encode(self, list_path: Path, audio_path: Path, out_path: Path) -> None:
        w, h = self.resolution
        _run_ffmpeg([
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-i", str(audio_path),
            "-vf", f"fps={self.fps},scale={w}:{h},format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k",
            "-shortest",
            str(out_path),
        ])
