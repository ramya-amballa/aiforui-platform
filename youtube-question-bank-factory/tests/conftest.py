from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from src.config import Config

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def cfg(tmp_path):
    """A Config pointing at an isolated tmp_path so tests never touch the
    project's real data/ directory or on-disk cache."""
    data = {
        "ai": {"provider": "local", "model": "", "temperature": 0.3, "max_retries": 1,
               "retry_backoff_seconds": 0, "timeout_seconds": 5},
        "tts": {
            "provider": "kokoro", "fallback_provider": "piper", "voice": "af_heart", "speed": 1.0,
            "sample_rate": 24000, "lang": "en-us", "model_dir": "models",
            "audio_format": "mp3", "mp3_bitrate": "128k",
            "pause_ms": {"after_question": 100, "after_option": 50, "before_reveal": 100,
                         "after_reveal": 50, "between_explanations": 50},
        },
        "concurrency": {"tts_concurrency": 2, "ai_concurrency": 2, "render_concurrency": 1},
        "video": {"template": "default", "resolution": [320, 180], "fps": 10,
                  "questions_per_video": 2, "countdown_seconds": 1, "reveal_seconds": 1,
                  "transition_seconds": 0.2, "show_explanation_text": False},
        "pipeline": {"max_retries_per_stage": 1, "retry_backoff_seconds": 0, "stop_on_error": False},
        "review": {"min_confidence_to_auto_pass": 0.75, "allow_video_for_needs_review": False},
        "paths": {
            "input_dir": "data/input", "normalized_dir": "data/normalized",
            "processed_dir": "data/processed", "jobs_dir": "data/jobs",
            "videos_dir": "data/videos", "reports_dir": "data/reports",
            "logs_dir": "data/logs", "cache_dir": "data/cache",
        },
        "logging": {"level": "WARNING", "json_logs": False},
    }
    c = Config(data, tmp_path)
    for key in ("input_dir", "normalized_dir", "processed_dir", "jobs_dir", "videos_dir", "reports_dir", "logs_dir", "cache_dir"):
        c.path(f"paths.{key}").mkdir(parents=True, exist_ok=True)
    return c


@pytest.fixture
def sample_xlsx():
    return FIXTURES_DIR / "sample_questions.xlsx"
