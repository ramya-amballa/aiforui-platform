from src.ai.local_provider import LocalTemplateProvider
from src.ingestion.intake import QuestionIntake
from src.validation.validator import AnswerValidationAgent


def test_validator_never_overwrites_supplied_answer(sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions
    agent = AnswerValidationAgent(LocalTemplateProvider(), min_confidence=0.75)
    for q in questions:
        result = agent.validate(q)
        assert result.supplied_answer == q.correct_answer
        assert result.status in ("PASS", "NEEDS_REVIEW", "ERROR")


def test_low_confidence_downgrades_to_needs_review(sample_xlsx):
    # The local provider is never confident enough to clear the default
    # 0.75 threshold, so every question must come back NEEDS_REVIEW -- this
    # is the deliberate "don't ship unverified answers on the free tier"
    # behavior, not a bug.
    q = QuestionIntake().process(sample_xlsx).questions[0]
    agent = AnswerValidationAgent(LocalTemplateProvider(), min_confidence=0.75)
    result = agent.validate(q)
    assert result.status == "NEEDS_REVIEW"
    assert "low_confidence" in result.flags


def test_high_threshold_of_zero_allows_pass(sample_xlsx):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    agent = AnswerValidationAgent(LocalTemplateProvider(), min_confidence=0.0)
    result = agent.validate(q)
    assert result.status == "PASS"


def test_malformed_options_flagged():
    from src.models import NormalizedQuestion

    q = NormalizedQuestion(
        question_id="QX", question="Which of these is correct?",
        options={"A": "All of the above", "B": "x", "C": "y", "D": "z"},
        correct_answer="A",
    )
    agent = AnswerValidationAgent(LocalTemplateProvider(), min_confidence=0.0)
    result = agent.validate(q)
    assert "ambiguous_meta_option" in result.flags
    assert result.status == "NEEDS_REVIEW"
