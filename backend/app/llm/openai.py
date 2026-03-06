"""
OpenAI LLM provider.
Uses openai SDK. Supports GPT-4o, GPT-4o-mini, o1, etc.
Swap in via LLM_PROVIDER=openai env var.
"""

import json
import logging
import time

from openai import OpenAI

from app.config import settings
from app.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI provider using the openai SDK."""

    provider_name = "openai"

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a text completion using OpenAI."""
        start = time.perf_counter()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        choice = response.choices[0]
        content = choice.message.content or ""
        result = LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=response.usage.prompt_tokens if response.usage else None,
            output_tokens=response.usage.completion_tokens if response.usage else None,
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
        """Generate structured JSON output using OpenAI's JSON mode."""
        start = time.perf_counter()

        json_system = system
        if json_system:
            json_system += "\n\nRespond ONLY with valid JSON. No other text."
        else:
            json_system = "Respond ONLY with valid JSON. No other text."

        if response_schema:
            json_system += f"\n\nResponse schema:\n{json.dumps(response_schema, indent=2)}"

        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        choice = response.choices[0]
        content = choice.message.content or "{}"
        llm_response = LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=response.usage.prompt_tokens if response.usage else None,
            output_tokens=response.usage.completion_tokens if response.usage else None,
        )
        self._log_call("complete_structured", prompt, llm_response)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("OpenAI returned invalid JSON: %s", content[:500])
            raise ValueError(f"OpenAI returned invalid JSON: {content[:200]}")
