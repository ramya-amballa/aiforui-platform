"""Raw file readers for the question bank. XLSX, CSV, JSON.

Every reader returns the same shape: a list of plain dicts with the raw
column values plus a 1-based `_row_number` for error reporting. No
validation or normalization happens here -- that's the intake module's job.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

EXPECTED_COLUMNS = [
    "question_id",
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
    "topic",
    "difficulty",
    "source",
    "notes",
]


def _clean_header(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_")


def read_xlsx(path: Path) -> list:
    import pandas as pd

    df = pd.read_excel(path, dtype=str, keep_default_na=False)
    df.columns = [_clean_header(c) for c in df.columns]
    rows = []
    for i, row in df.iterrows():
        d = {col: row.get(col, "") for col in df.columns}
        d["_row_number"] = i + 2  # header is row 1
        rows.append(d)
    return rows


def read_csv(path: Path) -> list:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [_clean_header(c) for c in (reader.fieldnames or [])]
        for i, row in enumerate(reader):
            d = dict(row)
            d["_row_number"] = i + 2
            rows.append(d)
    return rows


def read_json(path: Path) -> list:
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        # allow {"questions": [...]} wrapper
        data = data.get("questions", [])
    rows = []
    for i, item in enumerate(data):
        d = {_clean_header(k): v for k, v in item.items()}
        d["_row_number"] = i + 2
        rows.append(d)
    return rows


READERS = {
    ".xlsx": read_xlsx,
    ".xlsm": read_xlsx,
    ".csv": read_csv,
    ".json": read_json,
}


def read_question_bank(path: Path) -> list:
    path = Path(path)
    ext = path.suffix.lower()
    if ext not in READERS:
        raise ValueError(
            f"Unsupported input format '{ext}'. Supported: {', '.join(READERS)}"
        )
    return READERS[ext](path)
