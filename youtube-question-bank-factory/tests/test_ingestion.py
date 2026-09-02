from pathlib import Path

from src.ingestion.intake import QuestionIntake


def test_ingest_xlsx_accepts_valid_rows_and_rejects_malformed(sample_xlsx):
    result = QuestionIntake().process(sample_xlsx)
    # fixture has 12 rows; Q011 is deliberately missing option_b
    assert result.report.total_rows == 12
    assert result.report.accepted == 11
    assert result.report.rejected == 1
    ids = {q.question_id for q in result.questions}
    assert "Q011" not in ids
    assert "Q001" in ids


def test_normalized_question_has_four_options_and_valid_answer(sample_xlsx):
    result = QuestionIntake().process(sample_xlsx)
    for q in result.questions:
        assert set(q.options.keys()) == {"A", "B", "C", "D"}
        assert q.correct_answer in ("A", "B", "C", "D")
        assert q.question.strip() == q.question  # whitespace normalized


def test_duplicate_question_id_is_flagged_and_second_row_dropped(tmp_path):
    import pandas as pd

    rows = [
        dict(question_id="Q001", question="First version of the question?",
             option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="A"),
        dict(question_id="Q001", question="A different question text entirely for dup id test.",
             option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="B"),
    ]
    path = tmp_path / "dupe_ids.xlsx"
    pd.DataFrame(rows).to_excel(path, index=False)

    result = QuestionIntake().process(path)
    assert len(result.questions) == 1
    assert result.report.duplicate_ids == ["Q001"]


def test_duplicate_question_text_is_flagged_as_warning_not_rejected(tmp_path):
    import pandas as pd

    rows = [
        dict(question_id="Q001", question="Is this the same question repeated?",
             option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="A"),
        dict(question_id="Q002", question="Is this the same question repeated?",
             option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="A"),
    ]
    path = tmp_path / "dupe_text.xlsx"
    pd.DataFrame(rows).to_excel(path, index=False)

    result = QuestionIntake().process(path)
    assert len(result.questions) == 2  # not rejected, only flagged
    assert len(result.report.duplicate_questions) == 1


def test_missing_question_id_gets_stable_auto_id(tmp_path):
    import pandas as pd

    rows = [dict(question_id="", question="A question with no supplied id at all here.",
                  option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="C")]
    path = tmp_path / "no_id.xlsx"
    pd.DataFrame(rows).to_excel(path, index=False)

    r1 = QuestionIntake().process(path)
    r2 = QuestionIntake().process(path)
    assert r1.questions[0].question_id.startswith("AUTO-")
    # stable: re-ingesting the same file assigns the same auto id
    assert r1.questions[0].question_id == r2.questions[0].question_id


def test_csv_and_json_readers_produce_equivalent_results():
    result_xlsx = QuestionIntake().process(Path("tests/fixtures/sample_questions.xlsx"))
    result_csv = QuestionIntake().process(Path("tests/fixtures/sample_questions.csv"))
    result_json = QuestionIntake().process(Path("tests/fixtures/sample_questions.json"))

    ids_xlsx = {q.question_id for q in result_xlsx.questions}
    ids_csv = {q.question_id for q in result_csv.questions}
    ids_json = {q.question_id for q in result_json.questions}
    assert ids_xlsx == ids_csv == ids_json
