"""Variable-option-count visual pagination: options never overflow their
box, are never clipped/merged, and a question with more options (or a
very long option) than fit on one page gets extra option pages -- still
the same question, same audio segment, no narration repeated."""
from __future__ import annotations

import dataclasses
import shutil

import pytest
import yaml

from src.ingestion.intake import QuestionIntake
from src.models import AudioResult, TimingCue
from src.video.frames import plan_option_pages, plan_question_pages, render_question_frame
from src.video.renderer import VideoRenderer
from src.video.templates import TEMPLATES_DIR, load_template

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")

_SHORT_OPTIONS_4 = {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta"}
_SHORT_OPTIONS_6 = {**_SHORT_OPTIONS_4, "E": "Epsilon", "F": "Zeta"}

_VERY_LONG_OPTION = (
    "A landing-zone-based hub-and-spoke platform where a central platform team owns shared "
    "networking, identity, policy, and cost-management guardrails while individual product "
    "teams get their own delegated subscriptions with pre-approved Azure AI and machine "
    "learning resource types, allowing them to provision new workloads themselves within "
    "those guardrails instead of filing a ticket and waiting on the central team for every "
    "single new resource request across every subscription and environment."
)


def _fake_audio(q, tmp_path, duration=12.0, name=None):
    import numpy as np
    import soundfile as sf

    sr = 8000
    samples = (0.05 * np.sin(2 * 3.14159 * 220 * (np.arange(int(sr * duration)) / sr))).astype("float32")
    wav_path = tmp_path / f"{name or q.question_id}.wav"
    sf.write(str(wav_path), samples, sr)

    cues = [
        TimingCue("question", 0.0, 4.0),
        TimingCue("countdown", 4.0, 4.5),
        TimingCue("reveal", 9.0, 9.5),
    ]
    return AudioResult(
        question_id=name or q.question_id, wav_path=str(wav_path), mp3_path=None,
        duration_seconds=duration, sample_rate=sr, voice="af_heart", speed=1.0,
        tts_provider="fake", model_version="fake-v1", narration_hash="deadbeef",
        cues=cues,
    )


def _sample_question(sample_xlsx, **overrides):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    return dataclasses.replace(q, **overrides)


# -- plan_option_pages: pure planning logic -----------------------------------

def test_four_short_options_fit_on_one_page():
    tpl = load_template("default")
    pages = plan_option_pages(tpl, _SHORT_OPTIONS_4)
    assert len(pages) == 1
    assert [e["key"] for e in pages[0]] == ["A", "B", "C", "D"]
    assert all(len(e["lines"]) <= 1 for e in pages[0])


def test_six_short_options_split_four_and_two():
    """Matches the example in the spec: A-D on page one, E-F on page
    two -- not an arbitrary fixed count, just however many complete
    options fit in the existing options area."""
    tpl = load_template("default")
    pages = plan_option_pages(tpl, _SHORT_OPTIONS_6)
    assert [e["key"] for e in pages[0]] == ["A", "B", "C", "D"]
    assert [e["key"] for e in pages[1]] == ["E", "F"]


def test_every_option_key_appears_and_text_is_preserved_exactly():
    tpl = load_template("default")
    options = {**_SHORT_OPTIONS_6, "F": _VERY_LONG_OPTION}
    pages = plan_option_pages(tpl, options)

    seen: dict = {}
    for page in pages:
        for entry in page:
            seen.setdefault(entry["key"], []).append(entry["text"])

    assert set(seen.keys()) == set(options.keys())
    for key, chunks in seen.items():
        assert " ".join(chunks).split() == options[key].split()


def test_a_long_option_wraps_without_needing_a_new_page_if_it_still_fits():
    # Only two options, so there's ample vertical budget left for B to
    # grow onto a second line without needing to push anything to a new
    # page.
    tpl = load_template("default")
    options = {"A": "Short.",
               "B": "A somewhat longer option that should wrap onto a second line within its own box."}
    pages = plan_option_pages(tpl, options)
    assert len(pages) == 1
    b_entry = next(e for e in pages[0] if e["key"] == "B")
    assert len(b_entry["lines"]) > 1
    assert b_entry["box_h"] > tpl["layout"]["options"]["box_height"]


def test_a_very_long_option_pushes_later_options_to_a_new_page():
    tpl = load_template("default")
    options = {"A": _VERY_LONG_OPTION, "B": "Short.", "C": "Short.", "D": "Short."}
    pages = plan_option_pages(tpl, options)
    assert len(pages) > 1
    # Option A (grown to multiple lines) is never merged with B/C/D's text.
    a_text = "".join(e["text"] for page in pages for e in page if e["key"] == "A")
    assert a_text.split() == _VERY_LONG_OPTION.split()
    assert "Short." not in a_text


def test_no_option_box_ever_exceeds_the_configured_width():
    """Every wrapped line must fit within the option box's own text
    width -- this is what prevents text from leaving its box."""
    from PIL import Image, ImageDraw

    from src.video.fonts import load_font

    tpl = load_template("default")
    options = {"A": _VERY_LONG_OPTION, "B": "Short.", "C": "Short.", "D": "Short."}
    pages = plan_option_pages(tpl, options)

    text_font = load_font(tpl["fonts"]["option_text"]["family"], tpl["fonts"]["option_text"]["size"])
    label_font = load_font(tpl["fonts"]["option_label"]["family"], tpl["fonts"]["option_label"]["size"])
    opt_layout = tpl["layout"]["options"]
    img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(img)
    label_w = draw.textlength("X.  ", font=label_font)
    max_text_width = opt_layout["box_width"] - 2 * opt_layout["text_padding"] - label_w

    for page in pages:
        for entry in page:
            for line in entry["lines"]:
                assert draw.textlength(line, font=text_font) <= max_text_width + 1  # +1 for float rounding


# -- render_question_frame: options_page param --------------------------------

def test_options_page_param_draws_only_that_pages_options(sample_xlsx):
    q = _sample_question(sample_xlsx)
    tpl = load_template("default")
    pages = plan_option_pages(tpl, _SHORT_OPTIONS_6)

    page1_frame = render_question_frame(tpl, (1920, 1080), q, options_page=pages[0])
    page2_frame = render_question_frame(tpl, (1920, 1080), q, options_page=pages[1])
    assert list(page1_frame.getdata()) != list(page2_frame.getdata())


# -- _build_frame_plan: integration / timing / regression ---------------------

def test_normal_four_option_question_plan_is_unchanged(cfg, sample_xlsx, tmp_path):
    q = _sample_question(sample_xlsx)
    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")
    plan = renderer._build_frame_plan(q, audio)
    assert sum(d for _, d in plan) == pytest.approx(audio.duration_seconds, abs=0.01)
    assert len(plan) >= 3  # head frame + >=1 tick + reveal, no extra pages


def test_six_option_question_produces_extra_frames_same_total_duration(cfg, sample_xlsx, tmp_path):
    q = _sample_question(sample_xlsx, options=_SHORT_OPTIONS_6, correct_answer="F")
    audio = _fake_audio(q, tmp_path, name="six_opt")
    renderer = VideoRenderer(cfg, "default")

    four_opt_q = _sample_question(sample_xlsx, options=_SHORT_OPTIONS_4, correct_answer="A")
    four_opt_audio = _fake_audio(four_opt_q, tmp_path, name="four_opt")

    six_plan = renderer._build_frame_plan(q, audio)
    four_plan = renderer._build_frame_plan(four_opt_q, four_opt_audio)

    assert len(six_plan) > len(four_plan)
    assert sum(d for _, d in six_plan) == pytest.approx(audio.duration_seconds, abs=0.01)


def test_options_are_not_shown_on_question_only_continuation_pages(cfg, tmp_path, sample_xlsx):
    long_question = (
        "In a large multinational organization that operates across multiple Azure subscriptions and "
        "regions, and that must comply with a wide range of regulatory, data residency, and responsible "
        "AI governance requirements while also supporting dozens of independent engineering teams "
        "building and deploying their own custom machine learning models, generative AI copilots, "
        "cognitive search solutions, and document intelligence pipelines, which single architectural "
        "approach would best balance centralized governance, cost visibility, and security controls with "
        "the need for individual teams to move quickly and experiment freely without waiting on a central "
        "platform team for every new resource request?"
    )
    q = _sample_question(sample_xlsx, question=long_question, options=_SHORT_OPTIONS_6, correct_answer="F")
    tpl = load_template("default")
    q_pages, _ = plan_question_pages(tpl, q.question)
    assert len(q_pages) > 1  # precondition

    audio = _fake_audio(q, tmp_path, duration=40.0, name="long_six_opt")
    renderer = VideoRenderer(cfg, "default")
    plan = renderer._build_frame_plan(q, audio)

    n_question_only = len(q_pages) - 1
    for i in range(n_question_only):
        frame = plan[i][0]
        # A question-only page and a fresh no-options render of the same
        # text must match exactly -- proving no option box was drawn.
        expected = render_question_frame(
            renderer.template, renderer.resolution, q, show_options=False,
            question_text_override=q_pages[i], question_font_size=plan_question_pages(tpl, q.question)[1],
        )
        assert list(frame.getdata()) == list(expected.getdata())


def test_reveal_shows_the_options_page_containing_the_correct_answer(cfg, sample_xlsx, tmp_path):
    """Even though the countdown holds on the *last* options page, the
    reveal must show whichever page actually has the correct answer on
    it so it can be highlighted."""
    q = _sample_question(sample_xlsx, options=_SHORT_OPTIONS_6, correct_answer="B")  # B is on page 1, not the last
    tpl = load_template("default")
    opt_pages = plan_option_pages(tpl, q.options)
    assert len(opt_pages) > 1  # precondition
    assert any(e["key"] == "B" for e in opt_pages[0])
    assert not any(e["key"] == "B" for e in opt_pages[-1])

    audio = _fake_audio(q, tmp_path, name="reveal_page_test")
    renderer = VideoRenderer(cfg, "default")
    plan = renderer._build_frame_plan(q, audio)
    reveal_frame = plan[-1][0]

    expected = render_question_frame(
        tpl, renderer.resolution, q, highlight_key="B", show_banner=True,
        question_text_override=q.question, question_font_size=tpl["fonts"]["question"]["size"],
        options_page=opt_pages[0],
    )
    assert list(reveal_frame.getdata()) == list(expected.getdata())


def test_paginated_question_still_renders_as_a_single_video_segment(cfg, sample_xlsx, tmp_path):
    q = _sample_question(sample_xlsx, options=_SHORT_OPTIONS_6, correct_answer="F")
    audio = _fake_audio(q, tmp_path, name=q.question_id)
    renderer = VideoRenderer(cfg, "default")
    out_dir = tmp_path / "segments"
    out_path = renderer.render_question_segment(q, audio, out_dir)
    assert out_path.name == f"{q.question_id}.mp4"
    assert list(out_dir.glob("*.mp4")) == [out_path]


# -- Fix 1: the post-reveal silent hold ---------------------------------------

def test_config_after_reveal_pause_is_approximately_four_seconds():
    data = yaml.safe_load((TEMPLATES_DIR.parent / "config.yaml").read_text())
    after_reveal_ms = data["tts"]["pause_ms"]["after_reveal"]
    assert after_reveal_ms == pytest.approx(4000, abs=500)


def test_reveal_frame_hold_duration_matches_the_audios_trailing_silence(cfg, sample_xlsx, tmp_path):
    """The reveal frame's own on-screen duration is derived directly from
    the audio's total duration minus the reveal cue's start -- so a ~4s
    trailing silence baked into the narration audio holds the reveal
    frame on screen for ~4s, with no repeated narration."""
    q = _sample_question(sample_xlsx)
    audio = _fake_audio(q, tmp_path, duration=13.0)  # reveal cue starts at 9.0 -> exactly 4s trailing hold
    renderer = VideoRenderer(cfg, "default")
    plan = renderer._build_frame_plan(q, audio)
    reveal_duration = plan[-1][1]
    assert reveal_duration == pytest.approx(4.0, abs=0.05)
