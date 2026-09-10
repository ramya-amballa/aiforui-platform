"""Question Intake: read -> normalize -> validate -> dedupe.

This module NEVER generates, searches for, or invents question content.
It only reads what the user supplied and turns it into the normalized
internal representation the rest of the pipeline depends on. The original
source data is preserved as-is in the `source`/`notes` fields and the raw
row is never mutated -- only copied and cleaned into a new object.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.cache import compute_hash
from src.ingestion.readers import read_question_bank
from src.models import MIN_OPTION_COUNT, IngestionIssue, IngestionReport, NormalizedQuestion

# Option columns are read dynamically (option_a, option_b, option_c, ...)
# rather than a fixed list -- a question bank may supply 4, 5, 6, or more
# options, and every one of them must survive as its own independent
# option, never merged into the last of a fixed set.
_ALL_OPTION_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_WS_RE = re.compile(r"\s+")


def _clean_text(v) -> str:
    if v is None:
        return ""
    return _WS_RE.sub(" ", str(v).strip())


def _extract_options(row: dict) -> dict:
    """Reads option_a, option_b, option_c, ... in order, stopping at the
    first letter whose column is absent or empty for this row -- so a
    question bank whose sheet has option_e/option_f columns still yields
    exactly 4 options for a row that only filled in A-D, and 6 options
    for a row that filled in all six. Nothing is ever capped at D."""
    options: dict = {}
    for letter in _ALL_OPTION_LETTERS:
        col = f"option_{letter.lower()}"
        if col not in row:
            break
        value = _clean_text(row.get(col))
        if not value:
            break
        options[letter] = value
    return options


def _normalize_for_dedupe(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _stable_auto_id(question_text: str) -> str:
    return "AUTO-" + compute_hash(_normalize_for_dedupe(question_text))[:10].upper()


@dataclass
class IntakeResult:
    questions: list  # list[NormalizedQuestion], accepted only
    report: IngestionReport


class QuestionIntake:
    """Reads a question bank file and produces validated NormalizedQuestion objects."""

    def process(self, path: Path) -> IntakeResult:
        raw_rows = read_question_bank(path)

        issues: list = []
        accepted: list = []
        seen_ids: dict = {}          # question_id -> row_number of first occurrence
        seen_text: dict = {}         # normalized text -> question_id of first occurrence
        duplicate_ids: list = []
        duplicate_questions: list = []

        for row in raw_rows:
            row_number = row.get("_row_number")
            qid_raw = _clean_text(row.get("question_id"))
            question = _clean_text(row.get("question"))
            options = _extract_options(row)
            correct_answer = _clean_text(row.get("correct_answer")).upper()
            topic = _clean_text(row.get("topic"))
            difficulty = _clean_text(row.get("difficulty"))
            source = _clean_text(row.get("source"))
            notes = _clean_text(row.get("notes"))

            row_issues: list = []

            if not question:
                row_issues.append(IngestionIssue(row_number, qid_raw or None, "error", "Missing question text"))

            if len(options) < MIN_OPTION_COUNT:
                have = ", ".join(sorted(options)) or "none"
                row_issues.append(
                    IngestionIssue(
                        row_number, qid_raw or None, "error",
                        f"At least {MIN_OPTION_COUNT} options (A-D) are required; found only: {have}",
                    )
                )

            if not correct_answer:
                row_issues.append(IngestionIssue(row_number, qid_raw or None, "error", "Missing correct_answer"))
            elif correct_answer not in options:
                row_issues.append(
                    IngestionIssue(
                        row_number, qid_raw or None, "error",
                        f"correct_answer must be one of this question's own options "
                        f"({', '.join(sorted(options)) or 'none'}), got '{correct_answer}'",
                    )
                )

            if any(issue.severity == "error" for issue in row_issues):
                issues.extend(row_issues)
                continue

            question_id = qid_raw or _stable_auto_id(question)
            if not qid_raw:
                row_issues.append(
                    IngestionIssue(row_number, question_id, "warning", f"question_id missing; assigned {question_id}")
                )

            if question_id in seen_ids:
                duplicate_ids.append(question_id)
                row_issues.append(
                    IngestionIssue(
                        row_number, question_id, "error",
                        f"Duplicate question_id '{question_id}' (first seen at row {seen_ids[question_id]}); row skipped",
                    )
                )
                issues.extend(row_issues)
                continue

            norm_text = _normalize_for_dedupe(question)
            if norm_text in seen_text:
                duplicate_questions.append(
                    {"question_id": question_id, "duplicate_of": seen_text[norm_text], "row_number": row_number}
                )
                row_issues.append(
                    IngestionIssue(
                        row_number, question_id, "warning",
                        f"Question text appears to duplicate '{seen_text[norm_text]}'",
                    )
                )
            else:
                seen_text[norm_text] = question_id

            seen_ids[question_id] = row_number

            nq = NormalizedQuestion(
                question_id=question_id,
                question=question,
                options=options,
                correct_answer=correct_answer,
                topic=topic,
                difficulty=difficulty,
                source=source,
                notes=notes,
                row_number=row_number,
            )
            accepted.append(nq)
            issues.extend(row_issues)

        report = IngestionReport(
            total_rows=len(raw_rows),
            accepted=len(accepted),
            rejected=len(raw_rows) - len(accepted),
            duplicate_ids=duplicate_ids,
            duplicate_questions=duplicate_questions,
            issues=issues,
        )
        return IntakeResult(questions=accepted, report=report)

    @staticmethod
    def write_normalized(questions: list, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [q.to_dict() for q in questions]
        out_path.write_text(json.dumps(payload, indent=2))

    @staticmethod
    def load_normalized(path: Path) -> list:
        data = json.loads(Path(path).read_text())
        return [NormalizedQuestion.from_dict(d) for d in data]

    @staticmethod
    def write_error_report(report: IngestionReport, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["row_number", "question_id", "severity", "message"])
            for issue in report.issues:
                writer.writerow([issue.row_number, issue.question_id or "", issue.severity, issue.message])
