"""Real CLI (`produce`) integration tests for the intro Title/Subtitle/
Introduction flow: interactive prompting, what reaches the voice, and
what does/doesn't end up on the intro screen."""
from __future__ import annotations

import json
import shutil

import pytest
from click.testing import CliRunner

from src.cli.context import Runtime
from src.cli.main import cli
from src.tts.voice_agent import VoiceAgent
from tests.fakes import FakeTTSProvider

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe not installed",
)


def _fake_runtime(cfg, provider=None) -> Runtime:
    rt = Runtime(cfg)
    rt._voice_agent = VoiceAgent(cfg, provider=provider or FakeTTSProvider())
    return rt


def test_title_subtitle_and_introduction_are_all_requested_interactively(cfg, sample_xlsx, monkeypatch):
    rt = _fake_runtime(cfg)
    monkeypatch.setattr("src.cli.main.get_runtime", lambda: rt)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["produce", "--input", str(sample_xlsx), "--batch", "1", "--include-needs-review"],
        input="My Title\nMy Subtitle\nMy short intro.\n",
    )
    assert result.exit_code == 0, result.output
    assert "Title" in result.output
    assert "Subtitle" in result.output
    assert "Introduction" in result.output


def test_title_subtitle_and_introduction_are_all_spoken(cfg, sample_xlsx, monkeypatch):
    """Per the corrected requirement, the introduction IS part of the
    spoken narration/audio -- it must reach the TTS provider just like
    title and subtitle do."""
    provider = FakeTTSProvider()
    rt = _fake_runtime(cfg, provider)
    monkeypatch.setattr("src.cli.main.get_runtime", lambda: rt)

    intro_text = "Test your knowledge with 30 practice questions. Choose your answer before the timer ends."
    runner = CliRunner()
    result = runner.invoke(cli, [
        "produce", "--input", str(sample_xlsx), "--batch", "1", "--include-needs-review",
        "--title", "AI-300 Practice Questions",
        "--subtitle", "Azure AI Fundamentals",
        "--intro-text", intro_text,
    ])
    assert result.exit_code == 0, result.output

    spoken_texts = provider.texts
    assert any(t == "AI-300 Practice Questions." for t in spoken_texts), spoken_texts
    assert any(t == "Azure AI Fundamentals." for t in spoken_texts), spoken_texts
    assert any(intro_text in t for t in spoken_texts), \
        "the introduction must reach the TTS provider"

    report = json.loads((cfg.path("paths.reports_dir") / "production_report.json").read_text())
    assert report["video_metadata"]["title"] == "AI-300 Practice Questions"
    assert report["video_metadata"]["subtitle"] == "Azure AI Fundamentals"
    assert report["video_metadata"]["introduction"] == intro_text


def test_introduction_reaches_tts_but_cannot_be_drawn_on_screen(cfg, sample_xlsx, monkeypatch):
    """render_title_frame has no parameter for the introduction at all --
    it is structurally incapable of drawing it, rather than relying on a
    caller to simply not pass it through."""
    from src.video.frames import render_title_frame

    with pytest.raises(TypeError):
        render_title_frame({}, (1920, 1080), "Title", "Subtitle", "Introduction")


def test_title_and_subtitle_frames_are_visually_distinct(cfg):
    """Two separate visual states exist -- title-only, then subtitle-only
    -- so the intro screen never shows all fields (or the introduction)
    simultaneously."""
    from src.video.frames import render_title_frame
    from src.video.templates import load_template

    tpl = load_template("default")
    title_frame = render_title_frame(tpl, (1920, 1080), title="My Title")
    subtitle_frame = render_title_frame(tpl, (1920, 1080), subtitle="My Subtitle")

    assert list(title_frame.getdata()) != list(subtitle_frame.getdata())

    # A blank/background-only frame would be a single solid color; drawn
    # text guarantees more than one distinct pixel color is present in each.
    assert len(title_frame.getcolors(maxcolors=1_000_000)) > 1
    assert len(subtitle_frame.getcolors(maxcolors=1_000_000)) > 1


def test_produce_end_to_end_includes_an_intro_segment_with_a_pause_before_question_1(cfg, sample_xlsx, monkeypatch):
    rt = _fake_runtime(cfg)
    monkeypatch.setattr("src.cli.main.get_runtime", lambda: rt)

    runner = CliRunner()
    result = runner.invoke(cli, [
        "produce", "--input", str(sample_xlsx), "--batch", "2", "--include-needs-review",
        "--title", "T", "--subtitle", "S", "--intro-text", "I",
    ])
    assert result.exit_code == 0, result.output

    job_line = next(l for l in result.output.splitlines() if l.startswith("Job "))
    job_id = job_line.split()[1]
    final_mp4 = cfg.path("paths.videos_dir") / "video_001" / "final.mp4"
    assert final_mp4.exists()
    assert final_mp4.stat().st_size > 1000

    intro_segment = cfg.path("paths.jobs_dir") / job_id / "video_segments" / f"{job_id}_intro.mp4"
    assert intro_segment.exists()

    # The intro's own synthesized audio ends with the configured
    # after_intro pause, holding the intro segment on screen that long
    # before Question 1 begins.
    intro_timing = json.loads(
        (cfg.path("paths.jobs_dir") / job_id / "audio" / f"{job_id}_intro" / f"{job_id}_intro.json").read_text()
    )
    body_cue = next(c for c in intro_timing["cues"] if c["label"] == "intro_body")
    assert intro_timing["duration_seconds"] - body_cue["end_seconds"] > 1.0


def test_skip_video_never_prompts_for_intro_fields(cfg, sample_xlsx, monkeypatch):
    """--skip-video means no video is produced this run, so there's
    nothing to ask about -- the intro fields must not be prompted for."""
    rt = _fake_runtime(cfg)
    monkeypatch.setattr("src.cli.main.get_runtime", lambda: rt)

    runner = CliRunner()
    result = runner.invoke(cli, [
        "produce", "--input", str(sample_xlsx), "--batch", "1", "--include-needs-review", "--skip-video",
    ])
    assert result.exit_code == 0, result.output
    assert "Title" not in result.output
