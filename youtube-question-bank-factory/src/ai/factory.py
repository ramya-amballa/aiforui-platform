"""AI provider factory. This is the ONLY place that knows which concrete
provider classes exist -- every other module depends solely on AIClient.
"""
from __future__ import annotations

from src.ai.base import AIClient, AIProviderError
from src.ai.local_provider import LocalTemplateProvider
from src.config import Config


def get_ai_client(cfg: Config) -> AIClient:
    provider = cfg.get("ai.provider", "local").lower()
    model = cfg.get("ai.model", "")
    max_retries = int(cfg.get("ai.max_retries", 3))
    backoff = float(cfg.get("ai.retry_backoff_seconds", 2))
    timeout = float(cfg.get("ai.timeout_seconds", 60))
    temperature = float(cfg.get("ai.temperature", 0.3))

    if provider == "local":
        return LocalTemplateProvider()
    if provider == "claude":
        from src.ai.claude_provider import ClaudeProvider
        return ClaudeProvider(model, max_retries, backoff, timeout, temperature)
    if provider == "openai":
        from src.ai.openai_provider import OpenAIProvider
        return OpenAIProvider(model, max_retries, backoff, timeout, temperature)
    if provider == "gemini":
        from src.ai.gemini_provider import GeminiProvider
        return GeminiProvider(model, max_retries, backoff, timeout, temperature)

    raise AIProviderError(f"Unknown AI_PROVIDER '{provider}'. Use local|claude|openai|gemini.")
