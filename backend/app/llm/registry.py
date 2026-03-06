"""
LLM Provider Registry.
Selects provider based on LLM_PROVIDER env var.
Singleton pattern ensures one provider instance per process.
"""

import logging

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """Get or create the LLM provider singleton based on config."""
    global _provider
    if _provider is not None:
        return _provider

    provider_name = settings.llm_provider.lower()

    if provider_name == "gemini":
        from app.llm.gemini import GeminiProvider
        _provider = GeminiProvider()
        logger.info("LLM provider initialized: Gemini Flash (%s)", settings.gemini_model)
    elif provider_name == "claude":
        from app.llm.claude import ClaudeProvider
        _provider = ClaudeProvider()
        logger.info("LLM provider initialized: Claude (%s)", settings.claude_model)
    elif provider_name == "openai":
        from app.llm.openai import OpenAIProvider
        _provider = OpenAIProvider()
        logger.info("LLM provider initialized: OpenAI (%s)", settings.openai_model)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. Use 'gemini', 'claude', or 'openai'."
        )

    return _provider


def reset_provider() -> None:
    """Reset the provider singleton (useful for testing)."""
    global _provider
    _provider = None
