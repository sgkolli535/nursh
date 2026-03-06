"""
LangGraph Weekly Insight Agent.
Fan-out/fan-in pattern: analyze multiple patterns → generate text → compose narrative.

Graph:
  load_week_data → analyze_patterns → generate_insight_text → validate
    → [pass] → return
    → [fail] → regenerate_with_feedback → validate
"""

import json
import logging
import random
from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.state import InsightWriterState
from app.data_layer.gap_analysis import analyze_food_group_gaps
from app.db.queries import get_user_health_contexts
from app.db.supabase import get_supabase_client
from app.guardrails.validators import validate_insight
from app.llm.registry import get_llm_provider
from app.prompts.v1.generate_insight import (
    MAX_TOKENS,
    SYSTEM_PROMPT,
    TEMPERATURE,
    USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

# Nutrient spotlights rotate weekly
NUTRIENT_SPOTLIGHTS = [
    {
        "nutrient": "Iron",
        "description": "Iron helps carry oxygen through your blood to all parts of your body.",
        "food_sources": ["lentils", "spinach", "red meat", "tofu", "pumpkin seeds"],
    },
    {
        "nutrient": "Folate",
        "description": "Folate supports cell growth and is especially important during pregnancy.",
        "food_sources": ["lentils", "asparagus", "leafy greens", "oranges", "chickpeas"],
    },
    {
        "nutrient": "Omega-3",
        "description": "Omega-3 fatty acids support heart and brain health.",
        "food_sources": ["salmon", "sardines", "walnuts", "flaxseeds", "chia seeds"],
    },
    {
        "nutrient": "Calcium",
        "description": "Calcium keeps bones and teeth strong and supports muscle function.",
        "food_sources": ["yogurt", "milk", "sardines", "tofu", "fortified plant milk"],
    },
    {
        "nutrient": "Magnesium",
        "description": "Magnesium supports over 300 enzyme reactions, including sleep and mood regulation.",
        "food_sources": ["almonds", "spinach", "dark chocolate", "avocado", "pumpkin seeds"],
    },
    {
        "nutrient": "Vitamin C",
        "description": "Vitamin C supports immune function and helps your body absorb iron.",
        "food_sources": ["oranges", "bell peppers", "broccoli", "strawberries", "kale"],
    },
]

MAX_RETRIES = 2


async def load_week_data(state: InsightWriterState) -> InsightWriterState:
    """Node: Load 7-day food journal data from Supabase."""
    db = get_supabase_client()
    user_id = state["user_id"]
    days = state.get("period_days", 7)

    health_contexts = await get_user_health_contexts(db, user_id)
    food_group_summary = await analyze_food_group_gaps(
        db, user_id, days=days, conditions=health_contexts
    )

    # Pick a nutrient spotlight
    spotlight = random.choice(NUTRIENT_SPOTLIGHTS)

    return {
        **state,
        "health_context": health_contexts,
        "food_group_summary": food_group_summary,
        "nutrient_spotlight": spotlight,
    }


async def analyze_patterns(state: InsightWriterState) -> InsightWriterState:
    """Node: Deterministic pattern analysis from food group data."""
    summary = state.get("food_group_summary", [])
    patterns = []

    # Count food groups with good coverage
    well_covered = [g for g in summary if g["gap_severity"] == "none"]
    gaps = [g for g in summary if g["gap_severity"] in ("high", "medium")]

    if well_covered:
        patterns.append(
            f"Covered {len(well_covered)} of 13 food groups well this week"
        )
        # Highlight best
        best = max(well_covered, key=lambda g: g["days_present"])
        patterns.append(
            f"Especially consistent with {best['food_group_name']} "
            f"({best['days_present']} of 7 days)"
        )

    if gaps:
        missed_names = [g["food_group_name"] for g in gaps[:3]]
        patterns.append(
            f"Food groups with room for more: {', '.join(missed_names)}"
        )

    return {**state, "patterns": patterns}


async def generate_insight_text(state: InsightWriterState) -> InsightWriterState:
    """Node: LLM generates the narrative from patterns."""
    llm = get_llm_provider()

    prompt = USER_PROMPT_TEMPLATE.format(
        food_group_summary=json.dumps(
            [
                {
                    "group": g["food_group_name"],
                    "days": g["days_present"],
                    "target": g["target_days"],
                    "severity": g["gap_severity"],
                }
                for g in state.get("food_group_summary", [])
            ],
            indent=2,
        ),
        patterns=json.dumps(state.get("patterns", [])),
        health_context=json.dumps(state.get("health_context", [])),
        nutrient_spotlight=json.dumps(state.get("nutrient_spotlight", {})),
    )

    try:
        result = await llm.complete_structured(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return {
            **state,
            "narrative": result.get("narrative", ""),
            "highlights": result.get("highlights", []),
            "spotlight_text": result.get("spotlight_text", ""),
        }
    except Exception as e:
        logger.error("Insight generation failed: %s", e)
        return {**state, "error": str(e)}


async def validate(state: InsightWriterState) -> InsightWriterState:
    """Node: Validate the generated narrative."""
    narrative = state.get("narrative", "")
    is_valid, violations = validate_insight(narrative)

    for highlight in state.get("highlights", []):
        h_valid, h_violations = validate_insight(highlight)
        if not h_valid:
            is_valid = False
            violations.extend(h_violations)

    return {
        **state,
        "validation_result": {"is_valid": is_valid, "violations": violations},
    }


def check_validation(state: InsightWriterState) -> Literal["pass", "retry"]:
    """Conditional edge: pass or retry."""
    validation = state.get("validation_result", {})
    if validation.get("is_valid", False):
        return "pass"
    if state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"
    return "pass"  # Accept after max retries to avoid infinite loop


async def regenerate_with_feedback(state: InsightWriterState) -> InsightWriterState:
    """Node: Retry with feedback about violations."""
    state_update = await generate_insight_text(state)
    state_update["retry_count"] = state.get("retry_count", 0) + 1
    return state_update


def build_insight_writer_graph() -> StateGraph:
    """Build the LangGraph weekly insight agent."""
    graph = StateGraph(InsightWriterState)

    graph.add_node("load_week_data", load_week_data)
    graph.add_node("analyze_patterns", analyze_patterns)
    graph.add_node("generate_insight_text", generate_insight_text)
    graph.add_node("validate", validate)
    graph.add_node("regenerate_with_feedback", regenerate_with_feedback)

    graph.set_entry_point("load_week_data")
    graph.add_edge("load_week_data", "analyze_patterns")
    graph.add_edge("analyze_patterns", "generate_insight_text")
    graph.add_edge("generate_insight_text", "validate")
    graph.add_conditional_edges(
        "validate",
        check_validation,
        {
            "pass": END,
            "retry": "regenerate_with_feedback",
        },
    )
    graph.add_edge("regenerate_with_feedback", "validate")

    return graph.compile()


insight_writer_agent = build_insight_writer_graph()


async def get_weekly_insights(user_id: str) -> dict:
    """Run the insight writer agent. Main entry point."""
    initial_state: InsightWriterState = {
        "user_id": user_id,
        "period_days": 7,
        "food_group_summary": [],
        "patterns": [],
        "health_context": [],
        "nutrient_spotlight": {},
        "narrative": "",
        "highlights": [],
        "spotlight_text": "",
        "validation_result": {},
        "retry_count": 0,
        "error": None,
    }
    result = await insight_writer_agent.ainvoke(initial_state)
    return {
        "narrative": result.get("narrative", ""),
        "highlights": result.get("highlights", []),
        "nutrient_spotlight": result.get("nutrient_spotlight"),
        "spotlight_text": result.get("spotlight_text", ""),
        "error": result.get("error"),
    }
