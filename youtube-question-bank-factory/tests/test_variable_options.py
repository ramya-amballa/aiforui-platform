"""A question is not assumed to have exactly four options -- 4, 5, 6 (or
more) must all be preserved as independent options, never merged into
the last of a fixed A-D set, across ingestion, narration, QA, and the
correct-answer mapping."""
from __future__ import annotations

import pandas as pd

from src.ai.local_provider import LocalTemplateProvider
from src.explanation.explainer import ExplanationAgent
from src.ingestion.intake import QuestionIntake
from src.models import MIN_OPTION_COUNT, option_keys
from src.narration.narrator import NarrationAgent
from src.qa.audio_qa import check_question


def _write_xlsx(tmp_path, rows, name="questions.xlsx"):
    path = tmp_path / name
    pd.DataFrame(rows).to_excel(path, index=False)
    return path


PAUSE_MS = {"after_question": 100, "after_option": 50, "before_reveal": 100,
            "after_reveal": 50, "between_explanations": 50}


# -- ingestion / parsing -----------------------------------------------------

def test_four_option_question_is_unchanged(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Normal four-option question?",
        option_a="A text", option_b="B text", option_c="C text", option_d="D text",
        correct_answer="B",
    )])
    q = QuestionIntake().process(path).questions[0]
    assert set(q.options.keys()) == {"A", "B", "C", "D"}
    assert q.correct_answer == "B"


def test_five_option_question_preserves_a_through_e_separately(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Five-option question?",
        option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta", option_e="Epsilon",
        correct_answer="E",
    )])
    q = QuestionIntake().process(path).questions[0]
    assert q.options == {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta", "E": "Epsilon"}
    assert q.correct_answer == "E"


def test_six_option_question_preserves_a_through_f_separately(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Six-option question?",
        option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta",
        option_e="Epsilon", option_f="Zeta",
        correct_answer="F",
    )])
    q = QuestionIntake().process(path).questions[0]
    assert list(q.options.keys()) == ["A", "B", "C", "D", "E", "F"]
    assert q.options["F"] == "Zeta"
    assert q.correct_answer == "F"


def test_options_are_never_merged_into_the_fourth_option(tmp_path):
    """Option D must stay exactly its own text -- E and F must never get
    concatenated onto the end of it."""
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Six-option question?",
        option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta text only",
        option_e="Epsilon text only", option_f="Zeta text only",
        correct_answer="A",
    )])
    q = QuestionIntake().process(path).questions[0]
    assert q.options["D"] == "Delta text only"
    assert "Epsilon" not in q.options["D"]
    assert "Zeta" not in q.options["D"]
    assert q.options["E"] == "Epsilon text only"
    assert q.options["F"] == "Zeta text only"


def test_row_with_only_four_options_is_unaffected_by_other_rows_having_more(tmp_path):
    """A sheet with option_e/option_f columns (because some other row uses
    them) must not force a 4-option row to gain phantom options."""
    path = _write_xlsx(tmp_path, [
        dict(question_id="Q001", question="Four-option question?",
             option_a="A", option_b="B", option_c="C", option_d="D",
             option_e="", option_f="", correct_answer="A"),
        dict(question_id="Q002", question="Six-option question?",
             option_a="A", option_b="B", option_c="C", option_d="D",
             option_e="E", option_f="F", correct_answer="F"),
    ])
    result = QuestionIntake().process(path)
    by_id = {q.question_id: q for q in result.questions}
    assert set(by_id["Q001"].options.keys()) == {"A", "B", "C", "D"}
    assert set(by_id["Q002"].options.keys()) == {"A", "B", "C", "D", "E", "F"}


def test_correct_answer_e_is_not_remapped_to_d(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Five-option question?",
        option_a="A", option_b="B", option_c="C", option_d="D", option_e="E",
        correct_answer="E",
    )])
    q = QuestionIntake().process(path).questions[0]
    assert q.correct_answer == "E"
    assert q.correct_answer != "D"


def test_fewer_than_four_options_is_rejected(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Only three options?",
        option_a="A", option_b="B", option_c="C", option_d="",
        correct_answer="A",
    )])
    result = QuestionIntake().process(path)
    assert result.report.accepted == 0
    assert result.report.rejected == 1


def test_correct_answer_must_be_one_of_the_questions_own_options(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Four-option question?",
        option_a="A", option_b="B", option_c="C", option_d="D",
        correct_answer="E",  # E doesn't exist on this (4-option) row
    )])
    result = QuestionIntake().process(path)
    assert result.report.accepted == 0
    assert any("own options" in issue.message for issue in result.report.issues)


# -- models.option_keys -------------------------------------------------------

def test_option_keys_returns_sorted_letters_regardless_of_dict_order():
    assert option_keys({"C": "c", "A": "a", "B": "b"}) == ["A", "B", "C"]
    assert option_keys({"F": "f", "A": "a", "D": "d"}) == ["A", "D", "F"]


def test_min_option_count_is_four():
    assert MIN_OPTION_COUNT == 4


# -- narration: every option gets narrated, correct answer mapping holds -----

def _narrate(q):
    exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
    return NarrationAgent(PAUSE_MS).narrate(q, exp, countdown_seconds=1)


def test_narration_includes_every_option_for_a_six_option_question(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Six-option question?",
        option_a="Alpha choice", option_b="Beta choice", option_c="Gamma choice",
        option_d="Delta choice", option_e="Epsilon choice", option_f="Zeta choice",
        correct_answer="F",
    )])
    q = QuestionIntake().process(path).questions[0]
    narration = _narrate(q)

    option_segs = [s for s in narration.segments if s.kind == "option"]
    assert [s.option_key for s in option_segs] == ["A", "B", "C", "D", "E", "F"]
    for text in q.options.values():
        assert text in narration.full_text


def test_reveal_says_f_when_correct_answer_is_f(tmp_path):
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Six-option question?",
        option_a="A", option_b="B", option_c="C", option_d="D", option_e="E", option_f="F choice",
        correct_answer="F",
    )])
    q = QuestionIntake().process(path).questions[0]
    narration = _narrate(q)
    reveal = next(s for s in narration.segments if s.kind == "reveal")
    assert reveal.text == "Option F."
    assert reveal.option_key == "F"


def test_narration_lead_in_never_claims_a_specific_option_count(tmp_path):
    """The old phrasing said 'the four options' -- with a variable option
    count that claim would be wrong for a 5/6-option question."""
    path = _write_xlsx(tmp_path, [dict(
        question_id="Q001", question="Six-option question?",
        option_a="A", option_b="B", option_c="C", option_d="D", option_e="E", option_f="F",
        correct_answer="A",
    )])
    q = QuestionIntake().process(path).questions[0]
    narration = _narrate(q)
    transition = next(s for s in narration.segments if s.kind == "transition")
    assert "four" not in transition.text.lower()


# -- QA: no hard-coded exactly-four-options assumption ------------------------

def test_audio_qa_accepts_a_six_option_question(tmp_path):
    from src.job.manifest import JobManifest
    import json

    job = JobManifest("job_qa", tmp_path / "jobs", "bank.xlsx", ["Q001"])
    content_dir = job.question_dir("Q001")
    audio_dir = job.audio_dir("Q001")

    q_dict = {
        "question_id": "Q001", "question": "Six-option question?",
        "options": {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F"},
        "correct_answer": "F",
    }
    (content_dir / "question.json").write_text(json.dumps(q_dict))
    exp_dict = {
        "question_id": "Q001", "correct_answer": "F", "why_correct": "because",
        "why_options": {"A": "x", "B": "x", "C": "x", "D": "x"}, "key_takeaway": "takeaway",
    }
    (content_dir / "explanation.json").write_text(json.dumps(exp_dict))
    (content_dir / "narration.json").write_text(json.dumps({"segments": [{"kind": "question", "text": "hi"}]}))

    import numpy as np
    import soundfile as sf
    sr = 8000
    samples = (0.05 * np.sin(2 * 3.14159 * 220 * (np.arange(sr) / sr))).astype("float32")
    sf.write(str(audio_dir / "Q001.wav"), samples, sr)
    (audio_dir / "Q001.json").write_text(json.dumps({"duration_seconds": 1.0}))

    result = check_question(job.dir, "Q001")
    assert "fewer than 4 options" not in " ".join(result["issues"])
    assert "correct_answer is not one of this question's own options" not in " ".join(result["issues"])
