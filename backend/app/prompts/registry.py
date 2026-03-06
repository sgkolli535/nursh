"""
Prompt Registry — versioned prompts as first-class engineering artifacts.

Every prompt is registered with metadata: name, version, author, eval suite.
The registry enables A/B testing, version rollback, and eval tracking.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """A versioned prompt configuration."""
    name: str
    version: str
    system_prompt: str
    user_prompt_template: str
    temperature: float
    max_tokens: int
    response_schema: dict | None = None
    metadata: dict = field(default_factory=dict)


# Global prompt registry
_registry: dict[str, dict[str, PromptConfig]] = {}  # name → {version → PromptConfig}
_active_versions: dict[str, str] = {}  # name → active version


def register_prompt(config: PromptConfig) -> None:
    """Register a prompt version."""
    if config.name not in _registry:
        _registry[config.name] = {}
    _registry[config.name][config.version] = config
    # Set as active if first version
    if config.name not in _active_versions:
        _active_versions[config.name] = config.version
    logger.info("Registered prompt: %s v%s", config.name, config.version)


def get_prompt(name: str, version: str | None = None) -> PromptConfig:
    """Get a prompt by name and optional version. Defaults to active version."""
    if name not in _registry:
        raise KeyError(f"Prompt '{name}' not found in registry")
    if version:
        if version not in _registry[name]:
            raise KeyError(f"Prompt '{name}' version '{version}' not found")
        return _registry[name][version]
    active = _active_versions.get(name)
    if not active:
        raise KeyError(f"No active version for prompt '{name}'")
    return _registry[name][active]


def set_active_version(name: str, version: str) -> None:
    """Set the active version for a prompt."""
    if name not in _registry or version not in _registry[name]:
        raise KeyError(f"Prompt '{name}' version '{version}' not found")
    _active_versions[name] = version
    logger.info("Active version for '%s' set to '%s'", name, version)


def list_prompts() -> dict[str, dict[str, Any]]:
    """List all registered prompts with their versions and active status."""
    result = {}
    for name, versions in _registry.items():
        result[name] = {
            "versions": list(versions.keys()),
            "active": _active_versions.get(name),
        }
    return result


# === Auto-register v1 prompts on import ===

def _register_v1_prompts():
    from app.prompts.v1 import parse_meal, generate_recommendation, generate_insight, disambiguate

    register_prompt(PromptConfig(
        name="parse_meal",
        version="v1",
        system_prompt=parse_meal.SYSTEM_PROMPT,
        user_prompt_template=parse_meal.USER_PROMPT_TEMPLATE,
        temperature=parse_meal.TEMPERATURE,
        max_tokens=parse_meal.MAX_TOKENS,
        response_schema=parse_meal.RESPONSE_SCHEMA,
        metadata={"category": "input_layer", "eval_suite": "parsing_accuracy", "author": "sumikolli"},
    ))

    register_prompt(PromptConfig(
        name="generate_recommendation",
        version="v1",
        system_prompt=generate_recommendation.SYSTEM_PROMPT,
        user_prompt_template=generate_recommendation.USER_PROMPT_TEMPLATE,
        temperature=generate_recommendation.TEMPERATURE,
        max_tokens=generate_recommendation.MAX_TOKENS,
        response_schema=generate_recommendation.RESPONSE_SCHEMA,
        metadata={"category": "output_layer", "eval_suite": "health_safety,tone", "author": "sumikolli"},
    ))

    register_prompt(PromptConfig(
        name="generate_insight",
        version="v1",
        system_prompt=generate_insight.SYSTEM_PROMPT,
        user_prompt_template=generate_insight.USER_PROMPT_TEMPLATE,
        temperature=generate_insight.TEMPERATURE,
        max_tokens=generate_insight.MAX_TOKENS,
        metadata={"category": "output_layer", "eval_suite": "tone", "author": "sumikolli"},
    ))

    register_prompt(PromptConfig(
        name="disambiguate",
        version="v1",
        system_prompt=disambiguate.SYSTEM_PROMPT,
        user_prompt_template=disambiguate.USER_PROMPT_TEMPLATE,
        temperature=disambiguate.TEMPERATURE,
        max_tokens=disambiguate.MAX_TOKENS,
        metadata={"category": "input_layer", "author": "sumikolli"},
    ))


_register_v1_prompts()
