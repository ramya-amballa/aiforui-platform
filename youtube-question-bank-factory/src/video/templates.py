"""Video template loading. Templates are pure data (YAML) so a new visual
design never requires touching the renderer's code -- see templates/.
"""
from __future__ import annotations

from pathlib import Path

import yaml

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


class TemplateNotFoundError(Exception):
    pass


def load_template(name: str) -> dict:
    path = TEMPLATES_DIR / name / "template.yaml"
    if not path.exists():
        available = [p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir()]
        raise TemplateNotFoundError(f"Template '{name}' not found. Available: {available}")
    return yaml.safe_load(path.read_text())


def list_templates() -> list:
    return sorted(p.name for p in TEMPLATES_DIR.iterdir() if (p / "template.yaml").exists())
