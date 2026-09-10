"""Explanation Agent.

Its job is NOT to create the question -- the question is fixed input.
Its job is to teach it: why the supplied answer is correct, and why each
of the other three options is wrong, plus a takeaway and an optional exam
tip. It must not invent citations or sources.
"""
from __future__ import annotations

from src.ai.base import AIClient, AIProviderError
from src.models import Explanation, NormalizedQuestion

_SYSTEM_PROMPT = """You are an experienced subject-matter instructor writing the answer \
explanation for one exam-style question. The question and its correct answer are already \
fixed and given to you -- you do not change them. Be factually rigorous. Do not invent \
citations, statistics, or sources that were not given to you. If you are not confident you \
can correctly explain why the supplied answer is right, say so plainly in why_correct \
rather than fabricating a justification."""

_PROMPT_TEMPLATE = """Write the teaching explanation for this question.

Question: {question}
Option A: {a}
Option B: {b}
Option C: {c}
Option D: {d}
Correct answer: {correct} ({correct_text})
Topic: {topic}
Difficulty: {difficulty}
Reference/source (may be blank - do not invent one if blank): {source}
Notes (may be blank): {notes}

Respond with ONLY a JSON object of this exact shape:
{{
  "why_correct": "<why {correct} is correct, 2-4 sentences>",
  "why_options": {{
    "A": "<why A is right or wrong, 1-2 sentences>",
    "B": "<why B is right or wrong, 1-2 sentences>",
    "C": "<why C is right or wrong, 1-2 sentences>",
    "D": "<why D is right or wrong, 1-2 sentences>"
  }},
  "key_takeaway": "<one concise conceptual takeaway sentence>",
  "exam_tip": "<one short practical exam tip, or empty string if none>"
}}"""


class ExplanationAgent:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def explain(self, q: NormalizedQuestion) -> Explanation:
        prompt = _PROMPT_TEMPLATE.format(
            question=q.question,
            a=q.options["A"], b=q.options["B"], c=q.options["C"], d=q.options["D"],
            correct=q.correct_answer,
            correct_text=q.options[q.correct_answer],
            topic=q.topic or "(none supplied)",
            difficulty=q.difficulty or "(none supplied)",
            source=q.source or "(none supplied)",
            notes=q.notes or "(none supplied)",
        )
        context = {"kind": "explanation", "question": q.to_dict()}

        raw = self.ai_client.generate_structured(
            prompt, system=_SYSTEM_PROMPT, max_tokens=1200, context=context
        )

        why_options = {k: str(v).strip() for k, v in (raw.get("why_options") or {}).items()}
        exp = Explanation(
            question_id=q.question_id,
            correct_answer=q.correct_answer,
            why_correct=str(raw.get("why_correct", "")).strip(),
            why_options=why_options,
            key_takeaway=str(raw.get("key_takeaway", "")).strip(),
            exam_tip=str(raw.get("exam_tip", "")).strip(),
        )

        if not exp.is_complete():
            raise AIProviderError(
                f"Explanation for {q.question_id} is incomplete (missing why_correct, "
                f"key_takeaway, or one or more why_options entries) -- flagging for review "
                f"rather than accepting a partial explanation."
            )
        return exp
