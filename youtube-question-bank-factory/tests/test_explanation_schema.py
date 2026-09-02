import pytest

from src.ai.base import AIProviderError
from src.ai.local_provider import LocalTemplateProvider
from src.explanation.explainer import ExplanationAgent
from src.ingestion.intake import QuestionIntake
from src.models import VALID_OPTION_KEYS


def test_explanation_has_all_required_fields(sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions
    agent = ExplanationAgent(LocalTemplateProvider())
    for q in questions:
        exp = agent.explain(q)
        assert exp.question_id == q.question_id
        assert exp.correct_answer == q.correct_answer
        assert exp.why_correct
        assert exp.key_takeaway
        assert set(exp.why_options.keys()) == set(VALID_OPTION_KEYS)
        for key in VALID_OPTION_KEYS:
            assert exp.why_options[key].strip()
        assert exp.is_complete()


def test_incomplete_explanation_raises_instead_of_silently_passing():
    class BrokenProvider(LocalTemplateProvider):
        def generate_structured(self, prompt, *, system="", max_tokens=1500, context=None):
            return {"why_correct": "", "why_options": {}, "key_takeaway": ""}

    q = QuestionIntake().process("tests/fixtures/sample_questions.xlsx").questions[0]
    agent = ExplanationAgent(BrokenProvider())
    with pytest.raises(AIProviderError):
        agent.explain(q)
