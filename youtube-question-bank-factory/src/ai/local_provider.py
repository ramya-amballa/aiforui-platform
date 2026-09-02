"""Fully offline, zero-cost AI provider.

This is the default (AI_PROVIDER=local). It requires no API key and no
network access. It composes explanations and narration deterministically
from the question's own fields (question text, options, correct answer,
notes, source).

Known limitation (documented in README/SETUP): because it has no external
knowledge, its "why is this wrong" reasoning is generic rather than
subject-matter-expert quality. It is provided so the full pipeline -
including the explanation/narration/TTS/video stages - is provably
runnable end-to-end with zero cost and zero API keys. For production-grade
explanations, configure AI_PROVIDER=claude|openai|gemini with an API key.
"""
from __future__ import annotations

from src.ai.base import AIClient


class LocalTemplateProvider(AIClient):
    @property
    def model_version(self) -> str:
        return "local-template-v1"

    def generate_structured(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                             context: dict | None = None) -> dict:
        context = context or {}
        kind = context.get("kind")
        if kind == "explanation":
            return self._explanation(context)
        if kind == "validation":
            return self._validation(context)
        raise ValueError(f"local provider: unsupported structured kind '{kind}'")

    def generate_narration(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                            context: dict | None = None) -> str:
        # Narration composition for the local provider lives entirely in
        # src/narration/narrator.py's template engine (it needs no AI call
        # at all). This method exists to satisfy the interface if a caller
        # asks the local provider for freeform narration text directly.
        context = context or {}
        return context.get("fallback_text", "")

    # -- explanation --------------------------------------------------

    def _explanation(self, context: dict) -> dict:
        q = context["question"]
        correct = q["correct_answer"]
        options = q["options"]
        notes = (q.get("notes") or "").strip()
        source = (q.get("source") or "").strip()

        basis = notes or source
        if basis:
            why_correct = (
                f"{options[correct]} is correct. Based on the supplied reference "
                f"({basis}), this option directly satisfies what the question is asking."
            )
        else:
            why_correct = (
                f"{options[correct]} is the correct answer as specified in the source "
                f"question bank for this topic."
            )

        why_options = {}
        for key, text in options.items():
            if key == correct:
                why_options[key] = why_correct
            else:
                why_options[key] = (
                    f"{text} does not correctly address what the question asks. "
                    f"It is a plausible-sounding option but is not the best answer here; "
                    f"{options[correct]} is more precise for this scenario."
                )

        topic = q.get("topic") or "this topic"
        takeaway = (
            f"When working through questions on {topic}, focus on what is specifically "
            f"being asked and match it to the option that most precisely satisfies it -- "
            f"here, that is {options[correct]}."
        )

        return {
            "correct_answer": correct,
            "why_correct": why_correct,
            "why_options": why_options,
            "key_takeaway": takeaway,
            "exam_tip": f"Watch for distractors that sound related to {topic} but answer a different question.",
        }

    # -- validation -----------------------------------------------------

    def _validation(self, context: dict) -> dict:
        q = context["question"]
        options = q["options"]
        correct = q["correct_answer"]

        # The local provider has no external knowledge to second-guess the
        # supplied answer with, so it can only run structural sanity
        # checks -- never a confident "the answer is actually X" claim.
        flags = []
        distinct_options = {v.strip().lower() for v in options.values() if v.strip()}
        if len(distinct_options) < 4:
            flags.append("duplicate_or_overlapping_options")
        if any(len(v.strip()) < 2 for v in options.values()):
            flags.append("malformed_option")
        if options.get(correct, "").strip().lower() in ("all of the above", "none of the above"):
            flags.append("ambiguous_meta_option")

        status = "NEEDS_REVIEW" if flags else "PASS"
        confidence = 0.55 if flags else 0.6  # local provider is never highly confident either way

        return {
            "status": status,
            "confidence": confidence,
            "supplied_answer": correct,
            "suspected_answer": None,
            "reason": (
                "Structural checks only (local provider has no external subject-matter "
                "knowledge to verify factual correctness): " + (", ".join(flags) if flags else "no issues found")
            ),
            "flags": flags,
        }
