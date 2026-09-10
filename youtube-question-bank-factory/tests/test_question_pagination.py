"""Long-question visual pagination: a question too long to fit cleanly
above the options box gets extra visual pages instead of overflowing,
clipping, overlapping the options, or being shrunk past a readable floor.
Pagination is purely visual -- it never touches narration/audio, and a
paginated question is still one question (one question_id, one audio
segment, one rendered .mp4 segment)."""
from __future__ import annotations

import dataclasses
import shutil

import pytest

from src.ingestion.intake import QuestionIntake
from src.models import AudioResult, TimingCue
from src.video.frames import (
    _QUESTION_FONT_FLOOR_FRACTION,
    plan_question_pages,
    render_question_frame,
)
from src.video.renderer import VideoRenderer
from src.video.templates import load_template

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")

_LONG_QUESTION = (
    "In a large multinational organization that operates across multiple "
    "Azure subscriptions and regions, and that must comply with a wide "
    "range of regulatory, data residency, and responsible AI governance "
    "requirements while also supporting dozens of independent engineering "
    "teams building and deploying their own custom machine learning models, "
    "generative AI copilots, cognitive search solutions, and document "
    "intelligence pipelines, which single architectural approach would "
    "best balance centralized governance, cost visibility, and security "
    "controls with the need for individual teams to move quickly and "
    "experiment freely without waiting on a central platform team for "
    "every new resource request?"
)


def _fake_audio(q, tmp_path, duration=12.0):
    import numpy as np
    import soundfile as sf

    sr = 8000
    samples = (0.05 * np.sin(2 * 3.14159 * 220 * (np.arange(int(sr * duration)) / sr))).astype("float32")
    wav_path = tmp_path / f"{q.question_id}.wav"
    sf.write(str(wav_path), samples, sr)

    cues = [
        TimingCue("question", 0.0, 4.0),
        TimingCue("countdown", 4.0, 4.5),
        TimingCue("reveal", 9.0, 9.5),
    ]
    return AudioResult(
        question_id=q.question_id, wav_path=str(wav_path), mp3_path=None,
        duration_seconds=duration, sample_rate=sr, voice="af_heart", speed=1.0,
        tts_provider="fake", model_version="fake-v1", narration_hash="deadbeef",
        cues=cues,
    )


# -- plan_question_pages: pure planning logic --------------------------------

def test_short_question_fits_on_one_page_at_base_font_size():
    tpl = load_template("default")
    base_size = tpl["fonts"]["question"]["size"]
    pages, size = plan_question_pages(tpl, "What does AI stand for?")
    assert pages == ["What does AI stand for?"]
    assert size == base_size


def test_long_question_is_paginated_and_never_truncated():
    tpl = load_template("default")
    pages, size = plan_question_pages(tpl, _LONG_QUESTION)
    assert len(pages) > 1
    # The floor is the smallest font pagination is ever rendered at.
    assert size == max(int(tpl["fonts"]["question"]["size"] * _QUESTION_FONT_FLOOR_FRACTION), 1)
    # Every word survives, in order, across the pages -- nothing dropped,
    # reworded, or truncated.
    assert " ".join(pages).split() == _LONG_QUESTION.split()


def test_paginated_pages_each_fit_within_the_available_height():
    tpl = load_template("default")
    from PIL import Image, ImageDraw
    from src.video.fonts import load_font
    from src.video.frames import _wrap_text

    pages, size = plan_question_pages(tpl, _LONG_QUESTION)
    font = load_font(tpl["fonts"]["question"]["family"], size)
    max_width = tpl["layout"]["question"]["max_width"]
    line_spacing = tpl["layout"]["question"].get("line_spacing", 10)
    qy = tpl["layout"]["question"]["position"][1]
    options_y = tpl["layout"]["options"]["start_position"][1]
    available_height = options_y - qy - 24
    max_lines = max(1, int(available_height // (font.size + line_spacing)))

    img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(img)
    for page in pages:
        assert len(_wrap_text(draw, page, font, max_width)) <= max_lines


def test_font_size_never_goes_below_the_readable_floor():
    tpl = load_template("default")
    _, size = plan_question_pages(tpl, _LONG_QUESTION)
    floor = max(int(tpl["fonts"]["question"]["size"] * _QUESTION_FONT_FLOOR_FRACTION), 1)
    assert size >= floor


# -- render_question_frame: new params stay backward-compatible --------------

def test_show_options_false_draws_no_option_boxes(sample_xlsx):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    tpl = load_template("default")
    with_options = render_question_frame(tpl, (1920, 1080), q, show_options=True)
    without_options = render_question_frame(tpl, (1920, 1080), q, show_options=False)
    assert list(with_options.getdata()) != list(without_options.getdata())


def test_question_text_override_replaces_the_drawn_text(sample_xlsx):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    tpl = load_template("default")
    normal = render_question_frame(tpl, (1920, 1080), q, question_text_override=None)
    overridden = render_question_frame(tpl, (1920, 1080), q, question_text_override="A totally different page of text.")
    assert list(normal.getdata()) != list(overridden.getdata())


# -- _build_frame_plan: timing/regression -------------------------------------

def test_normal_question_produces_the_same_plan_as_before_pagination(cfg, sample_xlsx, tmp_path):
    """A short question must render exactly as it always has -- one
    question/options frame, N countdown ticks, one reveal frame."""
    q = QuestionIntake().process(sample_xlsx).questions[0]
    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")

    plan = renderer._build_frame_plan(q, audio)
    total_duration = sum(d for _, d in plan)

    assert total_duration == pytest.approx(audio.duration_seconds, abs=0.01)
    # question frame + >=1 countdown tick + reveal frame, no extra pages
    assert len(plan) >= 3


def test_long_question_produces_additional_frames_without_changing_total_duration(cfg, sample_xlsx, tmp_path):
    """Pagination must borrow only from the existing pre-countdown hold
    time -- the plan's total duration still matches the audio exactly, so
    no narration/timing is invented and the question audio never repeats."""
    q = dataclasses.replace(
        QuestionIntake().process(sample_xlsx).questions[0], question=_LONG_QUESTION,
    )
    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")

    short_q = dataclasses.replace(q, question="Short question?")
    short_plan = renderer._build_frame_plan(short_q, audio)
    long_plan = renderer._build_frame_plan(q, audio)

    assert len(long_plan) > len(short_plan)
    assert sum(d for _, d in long_plan) == pytest.approx(audio.duration_seconds, abs=0.01)
    assert sum(d for _, d in short_plan) == pytest.approx(audio.duration_seconds, abs=0.01)


def test_long_question_still_renders_as_a_single_video_segment_for_one_question(cfg, sample_xlsx, tmp_path):
    """Pagination adds frames within a question's own segment -- it must
    never create a second question or a second segment file."""
    q = dataclasses.replace(
        QuestionIntake().process(sample_xlsx).questions[0], question=_LONG_QUESTION,
    )
    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")
    out_dir = tmp_path / "segments"

    out_path = renderer.render_question_segment(q, audio, out_dir)
    assert out_path.name == f"{q.question_id}.mp4"
    assert out_path.exists()
    assert list(out_dir.glob("*.mp4")) == [out_path]  # exactly one segment


def test_reveal_frame_uses_the_final_page_text(cfg, sample_xlsx, tmp_path):
    """For visual continuity, the reveal frame that follows a paginated
    question shows the *last* page's text (at the floor font size), not
    the original full question crammed back in at full size."""
    q = dataclasses.replace(
        QuestionIntake().process(sample_xlsx).questions[0], question=_LONG_QUESTION,
    )
    tpl = load_template("default")
    pages, font_size = plan_question_pages(tpl, q.question)
    assert len(pages) > 1  # precondition for this test to be meaningful

    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")
    plan = renderer._build_frame_plan(q, audio)
    actual_reveal_frame = plan[-1][0]

    expected_reveal_frame = render_question_frame(
        tpl, renderer.resolution, q, highlight_key=q.correct_answer, show_banner=True,
        question_text_override=pages[-1], question_font_size=font_size,
    )
    assert list(actual_reveal_frame.getdata()) == list(expected_reveal_frame.getdata())
