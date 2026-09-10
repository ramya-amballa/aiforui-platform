"""OpenAI provider. Optional - only used if AI_PROVIDER=openai.

Requires: pip install openai, and OPENAI_API_KEY in the environment.
"""
from __future__ import annotations

import os

from src.ai.base import AIClient, AIProviderError
from src.ai.util import extract_json, with_retry


class OpenAIProvider(AIClient):
    def __init__(self, model: str, max_retries: int = 3, backoff_seconds: float = 2.0,
                 timeout_seconds: float = 60, temperature: float = 0.3):
        try:
            import openai
        except ImportError as exc:
            raise AIProviderError(
                "AI_PROVIDER=openai requires the 'openai' package: pip install openai"
            ) from exc

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise AIProviderError("OPENAI_API_KEY is not set (see .env.example)")

        self._client = openai.OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self._max_retries = max_retries
        self._backoff = backoff_seconds
        self._temperature = temperature

    @property
    def model_version(self) -> str:
        return f"openai:{self._model}"

    def _call(self, prompt: str, system: str, max_tokens: int, json_mode: bool) -> str:
        def _do():
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            kwargs = {}
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            resp = self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=self._temperature,
                messages=messages,
                **kwargs,
            )
            return resp.choices[0].message.content or ""

        return with_retry(_do, max_retries=self._max_retries, backoff_seconds=self._backoff, provider_name="openai")

    def generate_structured(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                             context: dict | None = None) -> dict:
        text = self._call(prompt, system, max_tokens, json_mode=True)
        return extract_json(text)

    def generate_narration(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                            context: dict | None = None) -> str:
        return self._call(prompt, system, max_tokens, json_mode=False).strip()
