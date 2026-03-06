"""
Claude LLM provider — production model.
Uses anthropic SDK. Swap in via LLM_PROVIDER=claude env var.
"""

import json
import logging
import time

import anthropic

from app.config import settings
from app.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class ClaudeProvider(LLMProvider):
    """Claude provider using anthropic SDK."""

    provider_name = "claude"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = settings.claude_model

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a text completion using Claude."""
        start = time.perf_counter()

        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system if system else anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        content = message.content[0].text if message.content else ""
        result = LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        self._log_call("complete", prompt, result)
        return result

    async def complete_structured(
        self,
        prompt: str,
        system: str = "",
        response_schema: dict | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        """Generate structured JSON output using Claude.

        Appends JSON instruction to system prompt and parses response.
        """
        start = time.perf_counter()

        json_system = system
        if json_system:
            json_system += "\n\nRespond ONLY with valid JSON. No other text."
        else:
            json_system = "Respond ONLY with valid JSON. No other text."

        if response_schema:
            json_system += f"\n\nResponse schema:\n{json.dumps(response_schema, indent=2)}"

        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=json_system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        content = message.content[0].text if message.content else "{}"
        llm_response = LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        self._log_call("complete_structured", prompt, llm_response)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Claude returned invalid JSON: %s", content[:500])
            raise ValueError(f"Claude returned invalid JSON: {content[:200]}")
