"""Intro narration: the video's Title and Subtitle are spoken (and, per
the video renderer's own intro frame, also displayed) -- the Short
Introduction is displayed only and is never synthesized to speech.

This reuses the exact same Narration/NarrationSegment shape and the same
VoiceAgent.synthesize_narration() pipeline that question narration goes
through -- no separate TTS path, no new synthesis mechanism.
"""
from __future__ import annotations

from src.models import Narration, NarrationSegment


def _as_spoken_sentence(text: str) -> str:
    """Normalizes one intro field into a properly-punctuated spoken
    sentence, without paraphrasing or altering the wording itself."""
    text = (text or "").strip()
    if not text:
        return ""
    if text[-1] not in ".!?":
        text += "."
    return text


def build_intro_narration(segment_id: str, title: str, subtitle: str,
                           field_pause_ms: int = 600, final_pause_ms: int = 1800) -> Narration:
    """Title then subtitle, as two separate spoken segments -- the Short
    Introduction is deliberately excluded here; it is rendered on the
    intro screen by the video renderer but never passed to TTS. A short
    pause (field_pause_ms) separates title from subtitle; a longer pause
    (final_pause_ms) follows the last spoken field, before Question 1
    begins. A field left empty is simply skipped, and the trailing pause
    still lands on whichever field ends up last.
    """
    fields = [("intro_title", title), ("intro_subtitle", subtitle)]
    spoken_fields = [(kind, _as_spoken_sentence(text)) for kind, text in fields]
    spoken_fields = [(kind, text) for kind, text in spoken_fields if text]

    segments = [
        NarrationSegment(kind, text, pause_ms=(final_pause_ms if i == len(spoken_fields) - 1 else field_pause_ms))
        for i, (kind, text) in enumerate(spoken_fields)
    ]
    full_text = " ".join(s.text for s in segments)
    return Narration(question_id=segment_id, segments=segments, full_text=full_text)
