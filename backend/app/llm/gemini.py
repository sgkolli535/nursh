"""
Gemini Flash LLM provider — free tier for development.
Uses google-generativeai SDK with JSON mode for structured output.
"""

import json
import logging
import time

import google.generativeai as genai

from app.config import settings
from app.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Gemini Flash provider using google-generativeai SDK."""

    provider_name = "gemini"

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a text completion using Gemini."""
        start = time.perf_counter()

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system if system else None,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )

        response = model.generate_content(prompt)
        elapsed_ms = (time.perf_counter() - start) * 1000

        result = LLMResponse(
            content=response.text,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=response.usage_metadata.prompt_token_count
            if response.usage_metadata
            else None,
            output_tokens=response.usage_metadata.candidates_token_count
            if response.usage_metadata
            else None,
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
        """Generate structured JSON output using Gemini's JSON mode."""
        start = time.perf_counter()

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system if system else None,
            generation_config=generation_config,
        )

        response = model.generate_content(prompt)
        elapsed_ms = (time.perf_counter() - start) * 1000

        llm_response = LLMResponse(
            content=response.text,
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=elapsed_ms,
            input_tokens=response.usage_metadata.prompt_token_count
            if response.usage_metadata
            else None,
            output_tokens=response.usage_metadata.candidates_token_count
            if response.usage_metadata
            else None,
        )
        self._log_call("complete_structured", prompt, llm_response)

        # Parse JSON response
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.error("Gemini returned invalid JSON: %s", response.text[:500])
            raise ValueError(f"Gemini returned invalid JSON: {response.text[:200]}")
