"""
LangGraph Meal Parser Agent.
Multi-step pipeline: parse text → DB lookup → confidence check → disambiguate/return.

Graph:
  parse_text → lookup_foods → check_confidence
    → [all high confidence] → return_results
    → [low confidence items] → generate_alternatives → return_with_disambiguation
    → [no DB match] → fuzzy_search → merge or flag_unknown
"""

import json
import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.state import MealParserState, ParsedItem
from app.db.supabase import get_supabase_client
from app.llm.registry import get_llm_provider
from app.prompts.v1.parse_meal import (
    MAX_TOKENS,
    RESPONSE_SCHEMA,
    SYSTEM_PROMPT,
    TEMPERATURE,
    USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7


async def parse_text(state: MealParserState) -> MealParserState:
    """Node: Call LLM to parse natural language meal description."""
    llm = get_llm_provider()
    prompt = USER_PROMPT_TEMPLATE.format(user_text=state["raw_text"])

    try:
        result = await llm.complete_structured(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            response_schema=RESPONSE_SCHEMA,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        items = result.get("items", [])
        meal_context = result.get("meal_context")
    except Exception as e:
        logger.error("Parse failed: %s", e)
        return {**state, "error": str(e), "parsed_items": []}

    return {**state, "parsed_items": items, "meal_context": meal_context}


async def lookup_foods(state: MealParserState) -> MealParserState:
    """Node: Look up each parsed item in the Supabase food database."""
    db = get_supabase_client()
    matches = {}

    for item in state.get("parsed_items", []):
        food_name = item.get("food_name", "")
        # Try exact match
        result = db.table("foods").select("id, name, aliases, tags, cuisine_region, source, source_id").ilike("name", food_name).limit(1).execute()
        if result.data:
            matches[food_name] = result.data[0]
            item["food_id"] = result.data[0]["id"]
        else:
            # Try alias match
            result = db.table("foods").select("id, name, aliases, tags, cuisine_region, source, source_id").contains("aliases", [food_name.lower()]).limit(1).execute()
            if result.data:
                matches[food_name] = result.data[0]
                item["food_id"] = result.data[0]["id"]
            else:
                item["food_id"] = None

    return {**state, "db_matches": matches}


def check_confidence(state: MealParserState) -> Literal["all_high", "needs_disambiguation", "needs_fuzzy"]:
    """Conditional edge: route based on confidence scores and DB matches."""
    items = state.get("parsed_items", [])
    if not items:
        return "all_high"  # Nothing to check

    has_low_confidence = any(
        item.get("confidence", 1.0) < CONFIDENCE_THRESHOLD for item in items
    )
    has_no_match = any(item.get("food_id") is None for item in items)

    if has_no_match:
        return "needs_fuzzy"
    elif has_low_confidence:
        return "needs_disambiguation"
    else:
        return "all_high"


async def fuzzy_search(state: MealParserState) -> MealParserState:
    """Node: Try trigram fuzzy search for unmatched items."""
    db = get_supabase_client()
    items = state.get("parsed_items", [])

    for item in items:
        if item.get("food_id") is not None:
            continue
        food_name = item.get("food_name", "")
        # Try fuzzy search via RPC (word_similarity)
        try:
            result = db.rpc(
                "search_foods_fuzzy",
                {"query_text": food_name.lower(), "result_limit": 3},
            ).execute()
            if result.data:
                best = result.data[0]
                item["food_id"] = best["id"]
                item["confidence"] = min(item.get("confidence", 0.5), 0.75)
                if len(result.data) > 1:
                    item["alternatives"] = [r["name"] for r in result.data[1:]]
        except Exception as e:
            logger.warning("Fuzzy search failed for '%s': %s", food_name, e)

    return {**state}


async def generate_alternatives(state: MealParserState) -> MealParserState:
    """Node: For low-confidence items, generate disambiguation options."""
    db = get_supabase_client()
    disambiguation_items = []

    for item in state.get("parsed_items", []):
        if item.get("confidence", 1.0) < CONFIDENCE_THRESHOLD:
            food_name = item.get("food_name", "")
            # Search for similar foods
            try:
                result = db.rpc(
                    "search_foods_fuzzy",
                    {"query_text": food_name.lower(), "result_limit": 4},
                ).execute()
                options = [r["name"] for r in (result.data or [])]
            except Exception:
                options = item.get("alternatives", [])

            disambiguation_items.append({
                "food_name": food_name,
                "options": options,
                "original_item": item,
            })

    return {
        **state,
        "needs_disambiguation": bool(disambiguation_items),
        "disambiguation_items": disambiguation_items,
    }


async def finalize_results(state: MealParserState) -> MealParserState:
    """Node: Prepare final items with food group information."""
    db = get_supabase_client()
    items = state.get("parsed_items", [])
    final_items = []

    for item in items:
        food_id = item.get("food_id")
        food_groups = []
        if food_id:
            result = (
                db.table("food_food_groups")
                .select("food_groups(slug)")
                .eq("food_id", food_id)
                .execute()
            )
            food_groups = [r["food_groups"]["slug"] for r in (result.data or [])]

        final_items.append({**item, "food_groups": food_groups})

    return {**state, "final_items": final_items}


def build_meal_parser_graph() -> StateGraph:
    """Build the LangGraph meal parser agent."""
    graph = StateGraph(MealParserState)

    # Add nodes
    graph.add_node("parse_text", parse_text)
    graph.add_node("lookup_foods", lookup_foods)
    graph.add_node("fuzzy_search", fuzzy_search)
    graph.add_node("generate_alternatives", generate_alternatives)
    graph.add_node("finalize_results", finalize_results)

    # Add edges
    graph.set_entry_point("parse_text")
    graph.add_edge("parse_text", "lookup_foods")
    graph.add_conditional_edges(
        "lookup_foods",
        check_confidence,
        {
            "all_high": "finalize_results",
            "needs_disambiguation": "generate_alternatives",
            "needs_fuzzy": "fuzzy_search",
        },
    )
    graph.add_edge("fuzzy_search", "generate_alternatives")
    graph.add_edge("generate_alternatives", "finalize_results")
    graph.add_edge("finalize_results", END)

    return graph.compile()


# Compiled agent — reusable across requests
meal_parser_agent = build_meal_parser_graph()


async def parse_meal(text: str) -> dict:
    """Run the meal parser agent on user text. Main entry point."""
    initial_state: MealParserState = {
        "raw_text": text,
        "parsed_items": [],
        "db_matches": {},
        "needs_disambiguation": False,
        "disambiguation_items": [],
        "final_items": [],
        "meal_context": None,
        "error": None,
    }
    result = await meal_parser_agent.ainvoke(initial_state)
    return {
        "items": result.get("final_items", []),
        "meal_context": result.get("meal_context"),
        "needs_disambiguation": result.get("needs_disambiguation", False),
        "disambiguation_items": result.get("disambiguation_items", []),
        "error": result.get("error"),
    }
