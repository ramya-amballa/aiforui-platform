"""Shared helpers for LLM-backed providers: JSON extraction + retry."""
from __future__ import annotations

import json
import re
import time
from typing import Callable

from src.ai.base import AIProviderError

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise AIProviderError(f"Could not parse JSON from model response: {text[:300]!r}")


def with_retry(fn: Callable, *, max_retries: int, backoff_seconds: float, provider_name: str):
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - re-raised as AIProviderError below
            last_exc = exc
            if attempt < max_retries:
                time.sleep(backoff_seconds * attempt)
    raise AIProviderError(f"{provider_name} failed after {max_retries} attempts: {last_exc}") from last_exc
