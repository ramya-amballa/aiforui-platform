"""Narration Agent.

Converts a NormalizedQuestion into natural spoken narration: a sequence of
NarrationSegment objects (each carrying its own pause) plus the full
concatenated text. This is a deterministic local template composer, not
an LLM call -- narration wording varies question-to-question via a phrase
bank seeded by question_id (so re-running the same question always
produces byte-identical narration, which is what makes narration caching
and audio-regeneration-avoidance possible). It requires no AI provider and
no network access, keeping the pipeline's narration step zero-cost and
fully offline by design.

Narration follows one fixed structure, always:
  1. the question
  2. all four options, A through D
  3. the existing countdown/timer pause
  4. the reveal -- ONLY the correct option's letter ("Option B."), never
     the option text again, never a lead-in phrase, never a reason

No answer explanation is generated or read at this stage (the
Explanation object is still produced and cached by the earlier explain
stage for other consumers -- e.g. review/QA -- but this agent never reads
from it). The correct option letter comes straight from the already-
validated NormalizedQuestion.correct_answer -- this module never infers,
reinterprets, or generates one.
"""
from __future__ import annotations

import random

from src.models import Explanation, Narration, NarrationSegment, NormalizedQuestion, VALID_OPTION_KEYS

_INTROS = [
    # Deliberately sequence-neutral -- none of these implies a previous
    # question already happened, since this same phrase bank is used for
    # every question including a video's actual first one (narration is
    # generated and cached per-question, independent of which position it
    # ends up in within any particular batch).
    "Let's look at this question.",
    "Here's a question for you.",
    "Take a look at this one.",
    "Let's work through this question together.",
]
_OPTIONS_LEAD = [
    "Here are your options.",
    "Here's what you can choose from.",
    "Take a look at the four options.",
]
_THINK = [
    "Take a few seconds to think about it.",
    "Go ahead and think it over.",
    "See if you can work it out before the answer.",
]


def _pick(seed_rng: random.Random, options: list) -> str:
    return options[seed_rng.randrange(len(options))]


class NarrationAgent:
    def __init__(self, pause_ms: dict):
        self.pause_ms = pause_ms

    def narrate(self, q: NormalizedQuestion, exp: Explanation, countdown_seconds: float = 5.0) -> Narration:
        rng = random.Random(q.question_id)
        segs: list = []

        segs.append(NarrationSegment("question", f"{_pick(rng, _INTROS)} {q.question}",
                                      pause_ms=self.pause_ms.get("after_question", 600)))

        segs.append(NarrationSegment("transition", _pick(rng, _OPTIONS_LEAD), pause_ms=250))
        for key in VALID_OPTION_KEYS:
            segs.append(NarrationSegment("option", f"Option {key}. {q.options[key]}.",
                                          option_key=key,
                                          pause_ms=self.pause_ms.get("after_option", 350)))

        segs.append(NarrationSegment("countdown", _pick(rng, _THINK),
                                      pause_ms=int(countdown_seconds * 1000)))

        # Reveal: the option letter only -- straight from the already-
        # validated q.correct_answer (one of VALID_OPTION_KEYS), never the
        # option text again, never "The correct answer is...", never a
        # reason. The trailing pause_ms is silent dead air (not spoken),
        # giving the viewer a moment to register the answer before the
        # next question begins.
        segs.append(NarrationSegment(
            "reveal", f"Option {q.correct_answer}.",
            option_key=q.correct_answer,
            pause_ms=self.pause_ms.get("after_reveal", 1800),
        ))

        full_text = " ".join(s.text for s in segs)
        return Narration(question_id=q.question_id, segments=segs, full_text=full_text)
