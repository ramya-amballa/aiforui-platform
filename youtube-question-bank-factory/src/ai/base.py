"""AI provider abstraction.

The rest of the application never imports anthropic/openai/google-generativeai
directly -- it only talks to this interface. That is what lets AI_PROVIDER
be swapped (or set to "local", which needs no network and no API key) without
touching the explanation or narration agents.

Claude Code (the tool building this project) is a development-time tool and
is NOT assumed to be available as a runtime API for the shipped application.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class AIProviderError(Exception):
    """Raised when a provider fails after exhausting retries."""


class AIClient(ABC):
    """Structured-generation interface every AI provider implements."""

    @abstractmethod
    def generate_structured(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                             context: dict | None = None) -> dict:
        """Return a parsed JSON object matching what `prompt` asked for.

        `context` carries the raw structured input (e.g. the normalized
        question) alongside the natural-language `prompt`. Real LLM
        providers use `prompt`; the offline `local` provider uses
        `context` directly to compose a deterministic answer without
        needing to parse free text.

        Implementations must raise AIProviderError if the response cannot
        be parsed as valid JSON after retries -- callers must never receive
        a silently-wrong or partially-filled structure.
        """

    @abstractmethod
    def generate_narration(self, prompt: str, *, system: str = "", max_tokens: int = 1500,
                            context: dict | None = None) -> str:
        """Return natural-language narration text (not JSON)."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Identifier used in cache keys so a model change invalidates the cache."""
