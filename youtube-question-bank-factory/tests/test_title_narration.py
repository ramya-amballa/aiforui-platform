"""Intro narration: Title, Subtitle, and Introduction are all spoken, in
order. Title and Subtitle are also displayed on the intro screen; the
Introduction is voice-only -- it reaches TTS but is never drawn (see
tests/test_produce_cli.py for the display side of that guarantee)."""
from __future__ import annotations

import pytest

from src.models import Narration
from src.narration.title_narrator import build_intro_narration


def test_title_subtitle_and_introduction_are_three_separate_spoken_segments_in_order():
    n = build_intro_narration(
        "i", "AI-300 Practice Questions", "Azure AI Fundamentals",
        "Test your knowledge with 30 practice questions.",
    )
    assert [s.kind for s in n.segments] == ["intro_title", "intro_subtitle", "intro_body"]
    assert n.segments[0].text == "AI-300 Practice Questions."
    assert n.segments[1].text == "Azure AI Fundamentals."
    assert n.segments[2].text == "Test your knowledge with 30 practice questions."


def test_returns_a_real_narration_object():
    n = build_intro_narration("i", "Title", "Subtitle", "Introduction")
    assert isinstance(n, Narration)
    assert n.question_id == "i"


def test_introduction_is_spoken_verbatim_not_paraphrased():
    exact_text = "Test your knowledge with 30 practice questions. Choose your answer before the timer ends."
    n = build_intro_narration("i", "Title", "Subtitle", exact_text)
    body = next(s for s in n.segments if s.kind == "intro_body")
    assert exact_text.rstrip(".") in body.text


def test_pause_separates_each_field_and_a_longer_one_follows_the_introduction():
    n = build_intro_narration("i", "Title", "Subtitle", "Introduction", field_pause_ms=600, final_pause_ms=1800)
    assert n.segments[0].pause_ms == 600   # after title
    assert n.segments[1].pause_ms == 600   # after subtitle
    assert n.segments[2].pause_ms == 1800  # after introduction -- the pause before Question 1


def test_missing_subtitle_is_skipped_but_the_final_pause_still_lands_correctly():
    n = build_intro_narration("i", "Title", "", "Introduction", field_pause_ms=600, final_pause_ms=1800)
    assert [s.kind for s in n.segments] == ["intro_title", "intro_body"]
    assert n.segments[0].pause_ms == 600
    assert n.segments[1].pause_ms == 1800


def test_field_trailing_punctuation_is_not_doubled():
    n = build_intro_narration("i", "Title!", "Subtitle?", "Intro.")
    assert [s.text for s in n.segments] == ["Title!", "Subtitle?", "Intro."]


def test_field_missing_punctuation_gets_a_period():
    n = build_intro_narration("i", "Title", "Subtitle", "Introduction")
    assert [s.text for s in n.segments] == ["Title.", "Subtitle.", "Introduction."]


def test_full_text_concatenates_all_three_segments():
    n = build_intro_narration("i", "Title", "Subtitle", "Introduction")
    assert n.full_text == "Title. Subtitle. Introduction."


def test_intro_narration_synthesizes_through_the_real_voice_agent(tmp_path):
    from src.config import Config
    from src.tts.voice_agent import VoiceAgent
    from tests.fakes import FakeTTSProvider

    provider = FakeTTSProvider()
    cfg = Config({"pipeline": {"max_retries_per_stage": 1, "retry_backoff_seconds": 0},
                  "tts": {"voice": "af_heart", "speed": 1.0, "sample_rate": 8000}}, tmp_path)
    agent = VoiceAgent(cfg, provider=provider)

    narration = build_intro_narration(
        "intro_seg", "AI-300 Practice Questions", "Azure AI Fundamentals",
        "Test your knowledge with 30 practice questions.",
        field_pause_ms=100, final_pause_ms=500,
    )
    result = agent.synthesize_narration(narration, tmp_path / "audio")

    assert result.duration_seconds > 0
    assert provider.calls == 3  # title, subtitle, AND the introduction
    assert any("Test your knowledge" in t for t in provider.texts)


def test_intro_pause_extends_the_synthesized_audio_duration(tmp_path):
    from src.config import Config
    from src.tts.voice_agent import VoiceAgent
    from tests.fakes import FakeTTSProvider

    provider = FakeTTSProvider()
    cfg = Config({"pipeline": {"max_retries_per_stage": 1, "retry_backoff_seconds": 0},
                  "tts": {"voice": "af_heart", "speed": 1.0, "sample_rate": 8000}}, tmp_path)
    agent = VoiceAgent(cfg, provider=provider)

    text = ("Title", "Subtitle", "Introduction")
    no_pause = agent.synthesize_narration(
        build_intro_narration("i0", *text, field_pause_ms=0, final_pause_ms=0), tmp_path / "a"
    )
    with_pause = agent.synthesize_narration(
        build_intro_narration("i1", *text, field_pause_ms=0, final_pause_ms=1800), tmp_path / "b"
    )
    assert with_pause.duration_seconds - no_pause.duration_seconds == pytest.approx(1.8, abs=0.05)
