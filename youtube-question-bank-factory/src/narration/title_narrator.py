"""Intro narration: Title, Subtitle, and Introduction are all spoken, in
that order. Title and Subtitle are also displayed on the intro screen (see
render_title_frame); the Introduction is voice-only -- it reaches TTS like
any other field here, but the video renderer never draws its text (see
VideoRenderer.render_intro_segment, which only ever passes title/subtitle
to render_title_frame).

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


def build_intro_narration(segment_id: str, title: str, subtitle: str, introduction: str,
                           field_pause_ms: int = 600, final_pause_ms: int = 1800) -> Narration:
    """Title, subtitle, and introduction, as three separate spoken
    segments in order -- never concatenated into one narration block. A
    short pause (field_pause_ms) separates each field from the next; a
    longer pause (final_pause_ms) follows the introduction (the last
    field), before Question 1 begins. A field left empty is simply
    skipped, and the trailing pause still lands on whichever field ends
    up last.
    """
    fields = [("intro_title", title), ("intro_subtitle", subtitle), ("intro_body", introduction)]
    spoken_fields = [(kind, _as_spoken_sentence(text)) for kind, text in fields]
    spoken_fields = [(kind, text) for kind, text in spoken_fields if text]

    segments = [
        NarrationSegment(kind, text, pause_ms=(final_pause_ms if i == len(spoken_fields) - 1 else field_pause_ms))
        for i, (kind, text) in enumerate(spoken_fields)
    ]
    full_text = " ".join(s.text for s in segments)
    return Narration(question_id=segment_id, segments=segments, full_text=full_text)
