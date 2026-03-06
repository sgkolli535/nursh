"""
Abstract LLM Provider interface.
Enables swapping between Gemini Flash (dev), Claude (production), and OpenAI via env var.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""
    content: str
    model: str
    provider: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    metadata: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    provider_name: str = "base"

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a text completion."""
        ...

    @abstractmethod
    async def complete_structured(
        self,
        prompt: str,
        system: str = "",
        response_schema: dict | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        """Generate a structured JSON response.

        Uses each provider's native JSON/structured output mode.
        Returns parsed dict, not raw text.
        """
        ...

    def _log_call(
        self,
        method: str,
        prompt_preview: str,
        response: LLMResponse,
    ) -> None:
        """Log LLM calls for eval analysis and debugging."""
        logger.info(
            "LLM call | provider=%s model=%s method=%s latency=%dms tokens_in=%s tokens_out=%s prompt=%s",
            response.provider,
            response.model,
            method,
            response.latency_ms,
            response.input_tokens,
            response.output_tokens,
            prompt_preview[:100],
        )


def timed(func):
    """Decorator to measure LLM call latency."""
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if isinstance(result, LLMResponse):
            result.latency_ms = elapsed_ms
        return result
    return wrapper
