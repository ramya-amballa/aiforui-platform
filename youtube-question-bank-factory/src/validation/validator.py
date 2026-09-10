"""Answer Validation Agent.

The supplied answer is authoritative. This stage never silently changes it.
It only ever flags a question NEEDS_REVIEW with its own suspected answer,
reason and confidence, for a human to look at.
"""
from __future__ import annotations

from src.ai.base import AIClient, AIProviderError
from src.models import NormalizedQuestion, ValidationResult

_SYSTEM_PROMPT = """You are a quality-assurance reviewer for an exam-style question bank. \
You do NOT invent, rewrite or replace questions. You are given ONE question that already \
has a supplied correct answer, and you check it for problems. You must NEVER change the \
supplied answer yourself -- you only report whether you believe it is correct, and if not, \
what you suspect the answer should be and why, with a confidence score."""

_PROMPT_TEMPLATE = """Review this question for validity.

Question: {question}
Option A: {a}
Option B: {b}
Option C: {c}
Option D: {d}
Supplied correct answer: {correct}
Topic: {topic}
Source/reference (may be blank): {source}
Notes (may be blank): {notes}

Check for:
- Does the supplied answer logically make sense for this question?
- Is the question ambiguous or could more than one option be defensible?
- Is any option malformed, empty-sounding, or clearly not a real distractor?
- Is the question likely outdated or does it require current/real-time information \
you cannot verify?
- Does the source/reference need human verification (e.g. it's missing or vague)?

Respond with ONLY a JSON object of this exact shape:
{{
  "status": "PASS" or "NEEDS_REVIEW",
  "confidence": <float 0.0-1.0, your confidence that the SUPPLIED answer is correct>,
  "supplied_answer": "{correct}",
  "suspected_answer": "<A/B/C/D you actually believe is correct, or null if you agree with supplied_answer>",
  "reason": "<one or two sentences explaining your assessment>",
  "flags": [<zero or more of: "ambiguous", "malformed_option", "outdated", "requires_current_info", "source_verification_needed", "multiple_plausible_answers">]
}}"""


class AnswerValidationAgent:
    def __init__(self, ai_client: AIClient, min_confidence: float = 0.75):
        self.ai_client = ai_client
        self.min_confidence = min_confidence

    def validate(self, q: NormalizedQuestion) -> ValidationResult:
        prompt = _PROMPT_TEMPLATE.format(
            question=q.question,
            a=q.options["A"], b=q.options["B"], c=q.options["C"], d=q.options["D"],
            correct=q.correct_answer,
            topic=q.topic or "(none supplied)",
            source=q.source or "(none supplied)",
            notes=q.notes or "(none supplied)",
        )
        context = {"kind": "validation", "question": q.to_dict()}

        try:
            raw = self.ai_client.generate_structured(
                prompt, system=_SYSTEM_PROMPT, max_tokens=500, context=context
            )
        except AIProviderError as exc:
            return ValidationResult(
                question_id=q.question_id,
                status="ERROR",
                confidence=0.0,
                supplied_answer=q.correct_answer,
                reason=f"Validation agent failed: {exc}",
                flags=["validation_error"],
            )

        status = str(raw.get("status", "NEEDS_REVIEW")).upper()
        confidence = float(raw.get("confidence", 0.0) or 0.0)
        flags = list(raw.get("flags", []) or [])

        # The supplied answer is authoritative; we never overwrite it here,
        # we only ever downgrade PASS -> NEEDS_REVIEW based on the model's
        # own confidence or the configured minimum threshold.
        if status == "PASS" and confidence < self.min_confidence:
            status = "NEEDS_REVIEW"
            if "low_confidence" not in flags:
                flags.append("low_confidence")

        return ValidationResult(
            question_id=q.question_id,
            status=status,
            confidence=confidence,
            supplied_answer=q.correct_answer,
            suspected_answer=raw.get("suspected_answer") or None,
            reason=raw.get("reason", ""),
            flags=flags,
        )
