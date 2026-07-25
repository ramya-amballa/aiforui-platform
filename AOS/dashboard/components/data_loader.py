"""
Safe, read-only loaders for existing AOS output files.

Every function here is defensive by design: a missing file is an honest
"no data yet" state, never a crash and never fabricated placeholder
content — consistent with the "never fabricate data" convention used
throughout every AOS runtime. The dashboard only ever reads; it never
writes to any business data file.
"""

import json
from datetime import date, datetime
from pathlib import Path

from utils.paths import aos_path


def today_str() -> str:
    return date.today().isoformat()


def load_json_safe(relpath: str):
    """Returns (data, exists). data is None if the file is missing or invalid."""
    path = aos_path(relpath)
    if not path.exists():
        return None, False
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), True
    except (json.JSONDecodeError, OSError):
        return None, False


def load_text_safe(relpath: str):
    """Returns (text, exists)."""
    path = aos_path(relpath)
    if not path.exists():
        return None, False
    try:
        return path.read_text(encoding="utf-8"), True
    except OSError:
        return None, False


def resolve_dated(relpath_template: str, on_date: str = None) -> str:
    """Substitutes {date} in a manifest path template with an ISO date (today by default)."""
    return relpath_template.replace("{date}", on_date or today_str())


def latest_file_in(dir_relpath: str, suffix: str = None):
    """Returns the most recently modified file in an AOS-relative directory, or None."""
    dir_path = aos_path(dir_relpath)
    if not dir_path.is_dir():
        return None
    candidates = [p for p in dir_path.iterdir() if p.is_file() and not p.name.startswith(".")]
    if suffix:
        candidates = [p for p in candidates if p.suffix == suffix]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def list_data_records(dataFile_relpath: str, collection_key: str):
    """Loads a schema-style JSON file (schema + a named list, e.g. 'opportunities') and
    returns just the list, empty if the file or key is missing."""
    data, exists = load_json_safe(dataFile_relpath)
    if not exists or not isinstance(data, dict):
        return []
    records = data.get(collection_key, [])
    return records if isinstance(records, list) else []


def extract_markdown_section(markdown_text: str, heading: str) -> str:
    """Returns the body text under a '## <heading>' line, up to the next '## ' heading
    (or end of document). Returns '' if the heading isn't found. Purely textual —
    never reinterprets or recomputes what the report already says."""
    if not markdown_text:
        return ""
    lines = markdown_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().lstrip("#").strip() == heading.lower() and stripped.startswith("#"):
            start = i + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if line.strip().startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def file_last_modified(relpath: str):
    path = aos_path(relpath)
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime)
