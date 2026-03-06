"""
Shared state schemas for LangGraph agents.
All agent state is typed with Pydantic-compatible TypedDicts.
"""

from typing import Any, TypedDict


class ParsedItem(TypedDict, total=False):
    food_name: str
    raw_text: str
    portion: str
    portion_grams_est: float | None
    confidence: float
    alternatives: list[str]
    cuisine_hint: str | None
    food_id: str | None
    food_groups: list[str]


class MealParserState(TypedDict, total=False):
    """State for the Meal Parser Agent graph."""
    raw_text: str
    parsed_items: list[ParsedItem]
    db_matches: dict[str, Any]  # food_name → DB result
    needs_disambiguation: bool
    disambiguation_items: list[dict]
    final_items: list[ParsedItem]
    meal_context: str | None
    error: str | None


class RecommendationItem(TypedDict, total=False):
    message: str
    food_group_target: str
    priority: str
    recommendation_type: str
    trace: dict


class RecommenderState(TypedDict, total=False):
    """State for the Recommendation Agent graph."""
    user_id: str
    gap_analysis: list[dict]
    health_contexts: list[str]
    cuisine_prefs: list[dict]
    dietary_prefs: list[str]
    suggested_foods: list[str]
    pairings: list[dict]
    recommendations: list[RecommendationItem]
    validation_result: dict
    retry_count: int
    error: str | None


class InsightWriterState(TypedDict, total=False):
    """State for the Weekly Insight Agent graph."""
    user_id: str
    period_days: int
    food_group_summary: list[dict]
    patterns: list[str]
    health_context: list[str]
    nutrient_spotlight: dict
    narrative: str
    highlights: list[str]
    spotlight_text: str
    validation_result: dict
    retry_count: int
    error: str | None
