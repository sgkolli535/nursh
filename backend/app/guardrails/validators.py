"""
Post-generation validators for LLM output.
Validates recommendations, insights, and parsed results before they reach users.
"""

import json
import logging

from app.guardrails.blocklist import check_blocklist

logger = logging.getLogger(__name__)


def validate_recommendation(recommendation: dict) -> tuple[bool, list[str]]:
    """Validate a single recommendation against all guardrails.

    Returns (is_valid, list_of_violations).
    """
    violations = []
    message = recommendation.get("message", "")

    # 1. Blocklist check
    blocklist_hits = check_blocklist(message)
    violations.extend(blocklist_hits)

    # 2. Tone check: no sentences starting with negative words
    sentences = [s.strip() for s in message.split(".") if s.strip()]
    for sentence in sentences:
        first_word = sentence.split()[0].lower() if sentence.split() else ""
        if first_word in ("don't", "stop", "never", "avoid", "quit", "eliminate"):
            violations.append(f"Sentence starts with negative word: '{first_word}'")

    # 3. Check that message is not empty
    if len(message.strip()) < 10:
        violations.append("Message is too short (< 10 chars)")

    # 4. Check for valid food_group_target
    valid_groups = {
        "dark_leafy_greens", "orange_red_vegetables", "cruciferous", "alliums",
        "citrus_berries", "legumes_pulses", "whole_grains", "nuts_seeds",
        "fermented_foods", "omega3_sources", "iron_rich_proteins",
        "calcium_sources", "herbs_spices",
    }
    target = recommendation.get("food_group_target", "")
    if target and target not in valid_groups:
        violations.append(f"Invalid food_group_target: '{target}'")

    # 5. Check for valid priority
    priority = recommendation.get("priority", "")
    if priority and priority not in ("high", "medium", "low"):
        violations.append(f"Invalid priority: '{priority}'")

    return len(violations) == 0, violations


def validate_recommendations_batch(
    recommendations: list[dict],
) -> tuple[bool, list[dict]]:
    """Validate a batch of recommendations. Returns (all_valid, per_item_results)."""
    results = []
    all_valid = True
    for rec in recommendations:
        is_valid, violations = validate_recommendation(rec)
        if not is_valid:
            all_valid = False
        results.append({
            "recommendation": rec,
            "is_valid": is_valid,
            "violations": violations,
        })
    return all_valid, results


def validate_parse_result(parse_result: dict) -> tuple[bool, list[str]]:
    """Validate NLP parse output for structural correctness."""
    violations = []

    items = parse_result.get("items", [])
    if not isinstance(items, list):
        violations.append("'items' is not a list")
        return False, violations

    for i, item in enumerate(items):
        if not item.get("food_name"):
            violations.append(f"Item {i}: missing food_name")
        if not isinstance(item.get("confidence", 0), (int, float)):
            violations.append(f"Item {i}: confidence is not a number")
        elif not 0 <= item.get("confidence", 0) <= 1:
            violations.append(f"Item {i}: confidence {item['confidence']} out of range [0,1]")

        # Make sure the LLM didn't sneak in nutrient data
        for field in ("nutrients", "calories", "macros", "nutrition"):
            if field in item:
                violations.append(f"Item {i}: contains forbidden field '{field}'")

    return len(violations) == 0, violations


def validate_insight(insight_text: str) -> tuple[bool, list[str]]:
    """Validate a weekly insight narrative."""
    violations = check_blocklist(insight_text)

    if len(insight_text.strip()) < 20:
        violations.append("Insight text is too short")

    return len(violations) == 0, violations
