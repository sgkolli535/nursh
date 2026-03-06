"""
Food Group mapping and classification.
Deterministic — NO AI. Every food in the DB is pre-tagged with food groups.
"""

from supabase import Client


# Canonical food group slugs (must match food_groups table)
ALL_FOOD_GROUPS = [
    "dark_leafy_greens", "orange_red_vegetables", "cruciferous", "alliums",
    "citrus_berries", "legumes_pulses", "whole_grains", "nuts_seeds",
    "fermented_foods", "omega3_sources", "iron_rich_proteins",
    "calcium_sources", "herbs_spices",
]


async def get_food_groups_for_food(db: Client, food_id: str) -> list[str]:
    """Get food group slugs for a specific food item."""
    result = (
        db.table("food_food_groups")
        .select("food_groups(slug)")
        .eq("food_id", food_id)
        .execute()
    )
    return [row["food_groups"]["slug"] for row in result.data]


async def get_food_groups_for_items(
    db: Client, food_ids: list[str]
) -> dict[str, list[str]]:
    """Get food group slugs for multiple food items. Returns {food_id: [slugs]}."""
    if not food_ids:
        return {}
    result = (
        db.table("food_food_groups")
        .select("food_id, food_groups(slug)")
        .in_("food_id", food_ids)
        .execute()
    )
    mapping: dict[str, list[str]] = {}
    for row in result.data:
        fid = row["food_id"]
        slug = row["food_groups"]["slug"]
        mapping.setdefault(fid, []).append(slug)
    return mapping


async def classify_food_groups_from_name(
    db: Client, food_name: str
) -> tuple[str | None, list[str]]:
    """Try to match a food name to the DB and return (food_id, food_group_slugs).

    Uses fuzzy search if exact match fails. Returns (None, []) if no match.
    """
    # Try exact match first
    result = db.table("foods").select("id").ilike("name", food_name).limit(1).execute()
    if result.data:
        food_id = result.data[0]["id"]
        groups = await get_food_groups_for_food(db, food_id)
        return food_id, groups

    # Try alias match
    result = db.table("foods").select("id").contains("aliases", [food_name.lower()]).limit(1).execute()
    if result.data:
        food_id = result.data[0]["id"]
        groups = await get_food_groups_for_food(db, food_id)
        return food_id, groups

    return None, []
