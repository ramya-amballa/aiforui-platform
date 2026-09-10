from src.ai.local_provider import LocalTemplateProvider
from src.explanation.explainer import ExplanationAgent
from src.ingestion.intake import QuestionIntake
from src.narration.narrator import NarrationAgent

PAUSE_MS = {"after_question": 100, "after_option": 50, "before_reveal": 100,
            "after_reveal": 50, "between_explanations": 50}


def _narrate_first(sample_xlsx):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
    return q, exp


def test_narration_is_deterministic_for_caching(sample_xlsx):
    q, exp = _narrate_first(sample_xlsx)
    agent = NarrationAgent(PAUSE_MS)
    n1 = agent.narrate(q, exp, countdown_seconds=5)
    n2 = agent.narrate(q, exp, countdown_seconds=5)
    assert n1.full_text == n2.full_text
    assert [s.text for s in n1.segments] == [s.text for s in n2.segments]


def test_narration_mentions_question_and_all_options(sample_xlsx):
    q, exp = _narrate_first(sample_xlsx)
    narration = NarrationAgent(PAUSE_MS).narrate(q, exp, countdown_seconds=5)
    assert q.question in narration.full_text
    for opt_text in q.options.values():
        assert opt_text in narration.full_text
    assert q.options[q.correct_answer] in narration.full_text


def test_narration_segments_carry_pauses(sample_xlsx):
    q, exp = _narrate_first(sample_xlsx)
    narration = NarrationAgent(PAUSE_MS).narrate(q, exp, countdown_seconds=5)
    kinds = [s.kind for s in narration.segments]
    assert "question" in kinds
    assert kinds.count("option") == 4
    assert "reveal" in kinds


def test_different_questions_get_varied_phrasing(sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions[:5]
    agent = NarrationAgent(PAUSE_MS)
    intros = set()
    for q in questions:
        exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
        n = agent.narrate(q, exp, countdown_seconds=5)
        intros.add(n.segments[0].text.split(q.question)[0].strip())
    assert len(intros) > 1  # not every question gets the exact same opening line


# ---------------------------------------------------------------------------
# Reveal rule: only "Option X." -- no explanation, no takeaway, no repeated
# answer text, no lead-in phrase like "The correct answer is...".
# ---------------------------------------------------------------------------

def test_reveal_says_only_the_option_letter(sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions
    agent = NarrationAgent(PAUSE_MS)
    for q in questions:
        exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
        n = agent.narrate(q, exp, countdown_seconds=5)
        reveal = next(s for s in n.segments if s.kind == "reveal")
        assert reveal.text == f"Option {q.correct_answer}."
        assert reveal.option_key == q.correct_answer


def test_no_explanation_or_takeaway_segments_are_generated(sample_xlsx):
    q, exp = _narrate_first(sample_xlsx)
    narration = NarrationAgent(PAUSE_MS).narrate(q, exp, countdown_seconds=5)
    kinds = [s.kind for s in narration.segments]
    assert "explanation" not in kinds
    assert "takeaway" not in kinds
    assert exp.why_correct not in narration.full_text
    assert exp.key_takeaway not in narration.full_text


def test_reveal_pause_is_present_before_the_next_question(sample_xlsx):
    """A silent pause (not spoken text) follows the reveal, holding the
    reveal frame on screen before the next question begins."""
    q, exp = _narrate_first(sample_xlsx)
    pause_ms = dict(PAUSE_MS)
    pause_ms["after_reveal"] = 1800
    narration = NarrationAgent(pause_ms).narrate(q, exp, countdown_seconds=5)
    reveal = next(s for s in narration.segments if s.kind == "reveal")
    assert reveal.pause_ms == 1800


# ---------------------------------------------------------------------------
# Question 1 (or any question, regardless of its position in a batch --
# narration is cached per-question, independent of batch position) must
# never be introduced as if a previous question already happened.
# ---------------------------------------------------------------------------

def test_no_question_is_ever_introduced_as_the_next_question(sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions
    agent = NarrationAgent(PAUSE_MS)
    for q in questions:
        exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
        n = agent.narrate(q, exp, countdown_seconds=5)
        opener = n.segments[0].text.split(q.question)[0].strip().lower()
        assert "next question" not in opener
        assert "next" not in opener
