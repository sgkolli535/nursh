"""
LangGraph Recommendation Agent.
Self-correcting pipeline: gather context → generate → validate → retry/fallback.

Graph:
  gather_context → generate_recommendations → validate_guardrails
    → [pass] → attach_traces → return
    → [fail + retries < 3] → regenerate_with_feedback → validate_guardrails
    → [fail + retries >= 3] → template_fallback → return
"""

import json
import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.state import RecommenderState
from app.data_layer.gap_analysis import analyze_food_group_gaps
from app.data_layer.health_rules import get_rules_for_conditions, get_suggested_foods
from app.data_layer.pairings import detect_pairings_in_meal
from app.data_layer.transparency import build_recommendation_trace
from app.db.queries import get_user_cuisine_preferences, get_user_health_contexts
from app.db.supabase import get_supabase_client
from app.guardrails.fallback import get_condition_fallback, get_gap_fallback
from app.guardrails.validators import validate_recommendations_batch
from app.llm.registry import get_llm_provider
from app.prompts.v1.generate_recommendation import (
    MAX_TOKENS,
    SYSTEM_PROMPT,
    TEMPERATURE,
    USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def gather_context(state: RecommenderState) -> RecommenderState:
    """Node: Gather all Data Layer context needed for recommendations."""
    db = get_supabase_client()
    user_id = state["user_id"]

    # Parallel data gathering (all deterministic)
    health_contexts = await get_user_health_contexts(db, user_id)
    cuisine_prefs = await get_user_cuisine_preferences(db, user_id)
    gap_analysis = await analyze_food_group_gaps(
        db, user_id, days=7, conditions=health_contexts
    )
    suggested_foods = get_suggested_foods(health_contexts)

    return {
        **state,
        "health_contexts": health_contexts,
        "cuisine_prefs": cuisine_prefs,
        "gap_analysis": gap_analysis,
        "suggested_foods": suggested_foods,
        "pairings": [],  # Will be populated when we have meal data
        "retry_count": 0,
    }


async def generate_recommendations(state: RecommenderState) -> RecommenderState:
    """Node: Call LLM to generate recommendations from Data Layer context."""
    llm = get_llm_provider()

    # Format context for prompt
    prompt = USER_PROMPT_TEMPLATE.format(
        gap_analysis=json.dumps(
            [g for g in state.get("gap_analysis", []) if g["gap_severity"] != "none"],
            indent=2,
        ),
        health_contexts=json.dumps(state.get("health_contexts", [])),
        cuisine_prefs=json.dumps(state.get("cuisine_prefs", [])),
        suggested_foods=json.dumps(state.get("suggested_foods", [])),
        pairings=json.dumps(state.get("pairings", [])),
    )

    try:
        result = await llm.complete_structured(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        recommendations = result if isinstance(result, list) else result.get("recommendations", [])
    except Exception as e:
        logger.error("Recommendation generation failed: %s", e)
        return {**state, "error": str(e), "recommendations": []}

    return {**state, "recommendations": recommendations}


async def validate_guardrails(state: RecommenderState) -> RecommenderState:
    """Node: Run blocklist, hallucination, and tone checks."""
    recommendations = state.get("recommendations", [])
    all_valid, results = validate_recommendations_batch(recommendations)

    return {
        **state,
        "validation_result": {
            "all_valid": all_valid,
            "results": results,
        },
    }


def check_validation(state: RecommenderState) -> Literal["pass", "retry", "fallback"]:
    """Conditional edge: route based on validation result."""
    validation = state.get("validation_result", {})
    if validation.get("all_valid", False):
        return "pass"
    retry_count = state.get("retry_count", 0)
    if retry_count < MAX_RETRIES:
        return "retry"
    return "fallback"


async def regenerate_with_feedback(state: RecommenderState) -> RecommenderState:
    """Node: Retry generation with specific feedback about what went wrong."""
    llm = get_llm_provider()
    validation = state.get("validation_result", {})

    # Collect all violations for feedback
    violations = []
    for result in validation.get("results", []):
        violations.extend(result.get("violations", []))

    feedback = "Your previous response was rejected for these reasons:\n"
    for v in violations[:5]:  # Cap at 5 to avoid prompt bloat
        feedback += f"- {v}\n"
    feedback += "\nPlease regenerate, carefully avoiding these issues."

    # Re-generate with feedback appended
    prompt = USER_PROMPT_TEMPLATE.format(
        gap_analysis=json.dumps(
            [g for g in state.get("gap_analysis", []) if g["gap_severity"] != "none"],
            indent=2,
        ),
        health_contexts=json.dumps(state.get("health_contexts", [])),
        cuisine_prefs=json.dumps(state.get("cuisine_prefs", [])),
        suggested_foods=json.dumps(state.get("suggested_foods", [])),
        pairings=json.dumps(state.get("pairings", [])),
    )
    prompt += f"\n\n{feedback}"

    try:
        result = await llm.complete_structured(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            temperature=max(0.2, TEMPERATURE - 0.1 * state.get("retry_count", 0)),
            max_tokens=MAX_TOKENS,
        )
        recommendations = result if isinstance(result, list) else result.get("recommendations", [])
    except Exception as e:
        logger.error("Regeneration failed: %s", e)
        recommendations = []

    return {
        **state,
        "recommendations": recommendations,
        "retry_count": state.get("retry_count", 0) + 1,
    }


async def template_fallback(state: RecommenderState) -> RecommenderState:
    """Node: Use pre-written templates when LLM can't self-correct."""
    logger.warning("Falling back to templates after %d retries", state.get("retry_count", 0))

    gap_analysis = state.get("gap_analysis", [])
    health_contexts = state.get("health_contexts", [])
    suggested_foods = state.get("suggested_foods", [])

    recommendations = []
    for gap in gap_analysis[:3]:  # Top 3 gaps
        if gap["gap_severity"] == "none":
            continue
        food = suggested_foods[0] if suggested_foods else "whole foods"
        slug = gap["food_group_slug"]

        # Try condition-specific template first
        if health_contexts:
            message = get_condition_fallback(health_contexts[0], food)
        else:
            message = get_gap_fallback(slug, food)

        recommendations.append({
            "message": message,
            "food_group_target": slug,
            "priority": gap["gap_severity"],
        })

    return {**state, "recommendations": recommendations}


async def attach_traces(state: RecommenderState) -> RecommenderState:
    """Node: Attach transparency traces to each recommendation."""
    db = get_supabase_client()
    recommendations = state.get("recommendations", [])
    health_contexts = state.get("health_contexts", [])
    gap_analysis = {g["food_group_slug"]: g for g in state.get("gap_analysis", [])}

    for rec in recommendations:
        target = rec.get("food_group_target", "")
        gap_info = gap_analysis.get(target, {})

        # Determine rule_key from health context rules
        rules = get_rules_for_conditions(health_contexts)
        rule_key = None
        for rule in rules:
            if target in rule.priority_food_groups:
                rule_key = rule.rule_key
                break

        trace = await build_recommendation_trace(
            db=db,
            food_id=None,  # Could resolve from suggested_foods
            food_name=rec.get("message", "").split()[-1] if rec.get("message") else "",
            gap_info=gap_info,
            rule_key=rule_key,
            health_conditions=health_contexts,
            recommendation_type="ai_generated",
        )
        rec["trace"] = {
            "logic_chain": trace.logic_chain,
            "data_source": {
                "food": trace.data_source.food if trace.data_source else "",
                "source": trace.data_source.source if trace.data_source else "",
                "source_id": trace.data_source.source_id if trace.data_source else "",
                "source_url": trace.data_source.source_url if trace.data_source else "",
                "verified_date": trace.data_source.verified_date if trace.data_source else "",
            } if trace.data_source else None,
            "evidence": {
                "claim": trace.evidence.claim,
                "citation": trace.evidence.citation,
                "display_text": trace.evidence.display_text,
            } if trace.evidence else None,
            "recommendation_type": trace.recommendation_type,
        }
        rec["recommendation_type"] = trace.recommendation_type

    return {**state}


def build_recommender_graph() -> StateGraph:
    """Build the LangGraph recommendation agent."""
    graph = StateGraph(RecommenderState)

    graph.add_node("gather_context", gather_context)
    graph.add_node("generate_recommendations", generate_recommendations)
    graph.add_node("validate_guardrails", validate_guardrails)
    graph.add_node("regenerate_with_feedback", regenerate_with_feedback)
    graph.add_node("template_fallback", template_fallback)
    graph.add_node("attach_traces", attach_traces)

    graph.set_entry_point("gather_context")
    graph.add_edge("gather_context", "generate_recommendations")
    graph.add_edge("generate_recommendations", "validate_guardrails")
    graph.add_conditional_edges(
        "validate_guardrails",
        check_validation,
        {
            "pass": "attach_traces",
            "retry": "regenerate_with_feedback",
            "fallback": "template_fallback",
        },
    )
    graph.add_edge("regenerate_with_feedback", "validate_guardrails")
    graph.add_edge("template_fallback", "attach_traces")
    graph.add_edge("attach_traces", END)

    return graph.compile()


recommender_agent = build_recommender_graph()


async def get_recommendations(user_id: str) -> dict:
    """Run the recommendation agent. Main entry point."""
    initial_state: RecommenderState = {
        "user_id": user_id,
        "gap_analysis": [],
        "health_contexts": [],
        "cuisine_prefs": [],
        "dietary_prefs": [],
        "suggested_foods": [],
        "pairings": [],
        "recommendations": [],
        "validation_result": {},
        "retry_count": 0,
        "error": None,
    }
    result = await recommender_agent.ainvoke(initial_state)
    return {
        "recommendations": result.get("recommendations", []),
        "error": result.get("error"),
    }
