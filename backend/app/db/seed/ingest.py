"""
Master ingestion script — seeds all food data, food groups, and citations into Supabase.
Run: python -m app.db.seed.ingest

This populates the food database with:
- 13 food groups
- ~40 curated foods (US + Indian) with full nutrient profiles
- Evidence citations for health rules
- Nutrient vectors for pgvector similarity search

All data includes transparency metadata (source, source_id, source_url, verified_date).
"""

import asyncio
import logging
import math
from datetime import date

from app.db.supabase import get_supabase_client
from app.db.seed.food_groups_data import FOOD_GROUPS
from app.db.seed.us_foods_data import US_FOODS
from app.db.seed.indian_foods_data import INDIAN_FOODS
from app.db.seed.international_ingredients_data import INTERNATIONAL_INGREDIENTS
from app.db.seed.composite_dishes_data import (
    WEST_AFRICAN_DISHES,
    EAST_ASIAN_DISHES,
    LATIN_AMERICAN_DISHES,
    MIDDLE_EASTERN_DISHES,
)
from app.db.seed.citations_data import EVIDENCE_CITATIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 20 nutrient dimensions for pgvector (order matters — must match everywhere)
NUTRIENT_VECTOR_KEYS = [
    "iron", "calcium", "vitamin_c", "fiber", "zinc", "folate", "b12",
    "magnesium", "potassium", "selenium", "vitamin_d", "vitamin_a",
    "vitamin_e", "omega_3_ala", "omega_3_dha", "omega_3_epa", "protein",
    "vitamin_k", "choline", "iodine",
]


def compute_nutrient_vector(nutrients: dict) -> list[float]:
    """Compute a normalized 20-dimensional nutrient vector for pgvector."""
    raw = [nutrients.get(key, 0.0) for key in NUTRIENT_VECTOR_KEYS]
    magnitude = math.sqrt(sum(v * v for v in raw))
    if magnitude == 0:
        return [0.0] * 20
    return [v / magnitude for v in raw]


def seed_food_groups(db):
    """Insert the 13 food group categories."""
    logger.info("Seeding %d food groups...", len(FOOD_GROUPS))
    for fg in FOOD_GROUPS:
        try:
            db.table("food_groups").upsert(fg, on_conflict="slug").execute()
        except Exception as e:
            logger.warning("Food group '%s' failed: %s", fg["name"], e)
    logger.info("Food groups seeded.")


def seed_foods(db, foods: list[dict], label: str):
    """Insert foods with nutrients, food group associations, and nutrient vectors."""
    logger.info("Seeding %d %s foods...", len(foods), label)

    # Get food group slug → id mapping
    fg_result = db.table("food_groups").select("id, slug").execute()
    fg_map = {row["slug"]: row["id"] for row in fg_result.data}

    for food_data in foods:
        food_groups = food_data.pop("food_groups", [])
        nutrients = food_data.pop("nutrients", {})

        # Compute nutrient vector
        food_data["nutrient_vector"] = str(compute_nutrient_vector(nutrients))
        food_data["verified_date"] = str(date.today())

        # Set source_url if not provided
        if not food_data.get("source_url"):
            food_data["source_url"] = None

        try:
            # Insert food
            result = db.table("foods").insert(food_data).execute()
            food_id = result.data[0]["id"]

            # Insert nutrients
            nutrient_rows = [
                {
                    "food_id": food_id,
                    "nutrient_name": name,
                    "amount_per_100g": amount,
                    "unit": "mg" if name not in ("protein", "fiber") else "g",
                }
                for name, amount in nutrients.items()
            ]
            if nutrient_rows:
                db.table("food_nutrients").insert(nutrient_rows).execute()

            # Insert food group associations
            for i, fg_slug in enumerate(food_groups):
                fg_id = fg_map.get(fg_slug)
                if fg_id:
                    db.table("food_food_groups").insert({
                        "food_id": food_id,
                        "food_group_id": fg_id,
                        "is_primary": i == 0,
                    }).execute()
                else:
                    logger.warning("Unknown food group slug: %s", fg_slug)

        except Exception as e:
            logger.warning("Food '%s' failed: %s", food_data.get("name"), e)

    logger.info("%s foods seeded.", label)


def seed_citations(db):
    """Insert evidence citations for health rules."""
    logger.info("Seeding %d evidence citations...", len(EVIDENCE_CITATIONS))
    for citation in EVIDENCE_CITATIONS:
        try:
            db.table("evidence_citations").upsert(
                citation, on_conflict="rule_key"
            ).execute()
        except Exception as e:
            logger.warning("Citation '%s' failed: %s", citation["rule_key"], e)
    logger.info("Evidence citations seeded.")


def main():
    """Run the full ingestion pipeline."""
    logger.info("Starting Nursh food database ingestion...")
    db = get_supabase_client()

    seed_food_groups(db)
    seed_foods(db, US_FOODS, "US")
    seed_foods(db, INDIAN_FOODS, "Indian")
    seed_foods(db, INTERNATIONAL_INGREDIENTS, "International Ingredients")
    seed_foods(db, WEST_AFRICAN_DISHES, "West African")
    seed_foods(db, EAST_ASIAN_DISHES, "East Asian")
    seed_foods(db, LATIN_AMERICAN_DISHES, "Latin American")
    seed_foods(db, MIDDLE_EASTERN_DISHES, "Middle Eastern")
    seed_citations(db)

    # Summary
    food_count = db.table("foods").select("id", count="exact").execute()
    fg_count = db.table("food_groups").select("id", count="exact").execute()
    citation_count = db.table("evidence_citations").select("id", count="exact").execute()

    logger.info(
        "Ingestion complete: %d foods, %d food groups, %d citations",
        food_count.count or 0,
        fg_count.count or 0,
        citation_count.count or 0,
    )


if __name__ == "__main__":
    main()
