"""Claude (Anthropic) provider. Optional - only used if AI_PROVIDER=claude.

Requires: pip install anthropic, and ANTHROPIC_API_KEY in the environment.
"""
from __future__ import annotations

import os

from src.ai.base import AIClient, AIProviderError
from src.ai.util import extract_json, with_retry


class ClaudeProvider(AIClient):
    def __init__(self, model: str, max_retries: int = 3, backoff_seconds: float = 2.0,
                 timeout_seconds: float = 60, temperature: float = 0.3):
        try:
            import anthropic
        except ImportError as exc:
            raise AIProviderError(
                "AI_PROVIDER=claude requires the 'anthropic' package: pip install anthropic"
            ) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise AIProviderError("ANTHROPIC_API_KEY is not set (see .env.example)")

        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self._max_retries = max_retries
        self._backoff = backoff_seconds
        self._temperature = temperature

    @property
    def model_version(self) -> str:
        return f"claude:{self._model}"

    def _call(self, prompt: str, system: str, max_tokens: int) -> str:
        def _do():
            resp = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=self._temperature,
                system=system or None,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")

        return with_retry(_do, max_retries=self._max_retries, backoff_seconds=self._backoff, provider_name="claude")

    def generate_structured(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                             context: dict | None = None) -> dict:
        sys_prompt = (system + "\n\nRespond with ONLY a single valid JSON object, no prose, no markdown fences.").strip()
        text = self._call(prompt, sys_prompt, max_tokens)
        return extract_json(text)

    def generate_narration(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                            context: dict | None = None) -> str:
        return self._call(prompt, system, max_tokens).strip()
