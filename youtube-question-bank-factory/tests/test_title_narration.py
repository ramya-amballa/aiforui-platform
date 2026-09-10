"""Intro narration: Title and Subtitle are spoken (and displayed); the
Short Introduction is displayed only and must never reach TTS."""
from __future__ import annotations

from src.models import Narration
from src.narration.title_narrator import build_intro_narration


def test_title_and_subtitle_are_two_separate_spoken_segments_in_order():
    n = build_intro_narration("i", "AI-300 Practice Questions", "Azure AI Fundamentals")
    assert [s.kind for s in n.segments] == ["intro_title", "intro_subtitle"]
    assert n.segments[0].text == "AI-300 Practice Questions."
    assert n.segments[1].text == "Azure AI Fundamentals."


def test_returns_a_real_narration_object():
    n = build_intro_narration("i", "Title", "Subtitle")
    assert isinstance(n, Narration)
    assert n.question_id == "i"


def test_introduction_is_never_part_of_the_spoken_narration():
    """build_intro_narration doesn't even accept an introduction argument
    -- it structurally cannot leak into TTS. This is the guarantee the
    video renderer's intro frame relies on when it displays the
    introduction separately, without ever passing it to VoiceAgent."""
    intro_text = "Test your knowledge with 30 practice questions. Choose your answer before the timer ends."
    n = build_intro_narration("i", "Title", "Subtitle")
    assert intro_text not in n.full_text
    assert all(intro_text not in s.text for s in n.segments)


def test_pause_separates_title_from_subtitle_and_a_longer_one_follows():
    n = build_intro_narration("i", "Title", "Subtitle", field_pause_ms=600, final_pause_ms=1800)
    assert n.segments[0].pause_ms == 600   # after title
    assert n.segments[1].pause_ms == 1800  # after subtitle -- the pause before Question 1


def test_missing_subtitle_is_skipped_but_the_final_pause_still_lands_correctly():
    n = build_intro_narration("i", "Title", "", field_pause_ms=600, final_pause_ms=1800)
    assert [s.kind for s in n.segments] == ["intro_title"]
    assert n.segments[0].pause_ms == 1800


def test_field_trailing_punctuation_is_not_doubled():
    n = build_intro_narration("i", "Title!", "Subtitle?")
    assert [s.text for s in n.segments] == ["Title!", "Subtitle?"]


def test_field_missing_punctuation_gets_a_period():
    n = build_intro_narration("i", "Title", "Subtitle")
    assert [s.text for s in n.segments] == ["Title.", "Subtitle."]


def test_full_text_concatenates_both_segments():
    n = build_intro_narration("i", "Title", "Subtitle")
    assert n.full_text == "Title. Subtitle."


def test_intro_narration_synthesizes_through_the_real_voice_agent(tmp_path):
    from src.config import Config
    from src.tts.voice_agent import VoiceAgent
    from tests.fakes import FakeTTSProvider

    provider = FakeTTSProvider()
    cfg = Config({"pipeline": {"max_retries_per_stage": 1, "retry_backoff_seconds": 0},
                  "tts": {"voice": "af_heart", "speed": 1.0, "sample_rate": 8000}}, tmp_path)
    agent = VoiceAgent(cfg, provider=provider)

    narration = build_intro_narration("intro_seg", "AI-300 Practice Questions", "Azure AI Fundamentals",
                                       field_pause_ms=100, final_pause_ms=500)
    result = agent.synthesize_narration(narration, tmp_path / "audio")

    assert result.duration_seconds > 0
    assert provider.calls == 2  # title, subtitle -- never a third call for the introduction


def test_intro_pause_extends_the_synthesized_audio_duration(tmp_path):
    from src.config import Config
    from src.tts.voice_agent import VoiceAgent
    from tests.fakes import FakeTTSProvider

    provider = FakeTTSProvider()
    cfg = Config({"pipeline": {"max_retries_per_stage": 1, "retry_backoff_seconds": 0},
                  "tts": {"voice": "af_heart", "speed": 1.0, "sample_rate": 8000}}, tmp_path)
    agent = VoiceAgent(cfg, provider=provider)

    text = ("Title", "Subtitle")
    no_pause = agent.synthesize_narration(
        build_intro_narration("i0", *text, field_pause_ms=0, final_pause_ms=0), tmp_path / "a"
    )
    with_pause = agent.synthesize_narration(
        build_intro_narration("i1", *text, field_pause_ms=0, final_pause_ms=1800), tmp_path / "b"
    )
    import pytest
    assert with_pause.duration_seconds - no_pause.duration_seconds == pytest.approx(1.8, abs=0.05)
