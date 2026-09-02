"""Gemini (Google) provider. Optional - only used if AI_PROVIDER=gemini.

Requires: pip install google-generativeai, and GOOGLE_API_KEY in the environment.
"""
from __future__ import annotations

import os

from src.ai.base import AIClient, AIProviderError
from src.ai.util import extract_json, with_retry


class GeminiProvider(AIClient):
    def __init__(self, model: str, max_retries: int = 3, backoff_seconds: float = 2.0,
                 timeout_seconds: float = 60, temperature: float = 0.3):
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise AIProviderError(
                "AI_PROVIDER=gemini requires the 'google-generativeai' package: "
                "pip install google-generativeai"
            ) from exc

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise AIProviderError("GOOGLE_API_KEY is not set (see .env.example)")

        genai.configure(api_key=api_key)
        self._genai = genai
        self._model_name = model
        self._max_retries = max_retries
        self._backoff = backoff_seconds
        self._temperature = temperature

    @property
    def model_version(self) -> str:
        return f"gemini:{self._model_name}"

    def _call(self, prompt: str, system: str, max_tokens: int, json_mode: bool) -> str:
        def _do():
            model = self._genai.GenerativeModel(self._model_name, system_instruction=system or None)
            cfg = {"temperature": self._temperature, "max_output_tokens": max_tokens}
            if json_mode:
                cfg["response_mime_type"] = "application/json"
            resp = model.generate_content(prompt, generation_config=cfg)
            return resp.text or ""

        return with_retry(_do, max_retries=self._max_retries, backoff_seconds=self._backoff, provider_name="gemini")

    def generate_structured(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                             context: dict | None = None) -> dict:
        text = self._call(prompt, system, max_tokens, json_mode=True)
        return extract_json(text)

    def generate_narration(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                            context: dict | None = None) -> str:
        return self._call(prompt, system, max_tokens, json_mode=False).strip()
