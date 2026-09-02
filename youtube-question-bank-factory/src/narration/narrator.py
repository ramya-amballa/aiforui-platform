"""Narration Agent.

Converts a NormalizedQuestion + Explanation into natural spoken narration:
a sequence of NarrationSegment objects (each carrying its own pause) plus
the full concatenated text. This is a deterministic local template
composer, not an LLM call -- narration wording varies question-to-question
via a phrase bank seeded by question_id (so re-running the same question
always produces byte-identical narration, which is what makes narration
caching and audio-regeneration-avoidance possible). It requires no AI
provider and no network access, keeping the pipeline's narration step
zero-cost and fully offline by design.
"""
from __future__ import annotations

import random

from src.models import Explanation, Narration, NarrationSegment, NormalizedQuestion, VALID_OPTION_KEYS

_INTROS = [
    "Let's look at this question.",
    "Here's our next question.",
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
_REVEAL_LEAD = [
    "The correct answer is",
    "The right answer here is",
    "The answer is",
]
_WHY_LEAD = [
    "Here's why.",
    "Let's break down why.",
    "Here's the reasoning.",
]
_OTHERS_LEAD = [
    "Now let's quickly look at why the other options aren't correct.",
    "Let's briefly cover why the remaining options don't work.",
    "Here's a quick look at the other choices.",
]
_TAKEAWAY_LEAD = [
    "The key point to remember is",
    "The main takeaway here is",
    "What's worth remembering is",
]


def _pick(seed_rng: random.Random, options: list) -> str:
    return options[seed_rng.randrange(len(options))]


def _lowfirst(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


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

        correct_text = q.options[q.correct_answer]
        segs.append(NarrationSegment(
            "reveal",
            f"{_pick(rng, _REVEAL_LEAD)} {q.correct_answer}, {correct_text}.",
            option_key=q.correct_answer,
            pause_ms=self.pause_ms.get("after_reveal", 500),
        ))

        segs.append(NarrationSegment("explanation", f"{_pick(rng, _WHY_LEAD)} {exp.why_correct}",
                                      option_key=q.correct_answer,
                                      pause_ms=self.pause_ms.get("between_explanations", 400)))

        wrong_keys = [k for k in VALID_OPTION_KEYS if k != q.correct_answer]
        segs.append(NarrationSegment("transition", _pick(rng, _OTHERS_LEAD), pause_ms=300))
        for key in wrong_keys:
            segs.append(NarrationSegment(
                "explanation", f"Option {key}. {exp.why_options.get(key, '')}",
                option_key=key,
                pause_ms=self.pause_ms.get("between_explanations", 400),
            ))

        segs.append(NarrationSegment(
            "takeaway", f"{_pick(rng, _TAKEAWAY_LEAD)} that {_lowfirst(exp.key_takeaway)}",
            pause_ms=300 if exp.exam_tip else 0,
        ))
        if exp.exam_tip:
            segs.append(NarrationSegment("takeaway", f"Exam tip: {exp.exam_tip}", pause_ms=0))

        full_text = " ".join(s.text for s in segs)
        return Narration(question_id=q.question_id, segments=segs, full_text=full_text)
