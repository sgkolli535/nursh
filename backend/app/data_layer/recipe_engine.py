"""
Recipe Decomposition Engine.
Uses recursive CTE to walk the recipe_components DAG and compute
total nutrients for composite dishes.

Example: "garam masala" is a sub-recipe used in 50 dishes.
The DAG prevents redundant nutrient data.
"""

from supabase import Client


async def compute_recipe_nutrients(
    db: Client, food_id: str
) -> dict[str, float]:
    """Compute total nutrients for a composite dish by walking its recipe DAG.

    Uses a recursive CTE in PostgreSQL:

    WITH RECURSIVE ingredients AS (
      SELECT child_food_id, amount_grams, yield_factor, retention_factor
      FROM recipe_components WHERE parent_food_id = :food_id
      UNION ALL
      SELECT rc.child_food_id, rc.amount_grams * i.yield_factor,
             rc.yield_factor, rc.retention_factor
      FROM recipe_components rc
      JOIN ingredients i ON rc.parent_food_id = i.child_food_id
    )
    SELECT fn.nutrient_name,
           SUM(fn.amount_per_100g * i.amount_grams / 100.0 * i.retention_factor)
    FROM ingredients i
    JOIN food_nutrients fn ON fn.food_id = i.child_food_id
    GROUP BY fn.nutrient_name

    For MVP, we call this via an RPC function in Supabase.
    """
    result = db.rpc(
        "compute_recipe_nutrients",
        {"target_food_id": food_id},
    ).execute()

    nutrients: dict[str, float] = {}
    for row in (result.data or []):
        nutrients[row["nutrient_name"]] = round(row["total_amount"], 2)
    return nutrients


async def get_recipe_components(
    db: Client, food_id: str
) -> list[dict]:
    """Get the ingredient tree for a composite dish."""
    result = (
        db.table("recipe_components")
        .select("*, child:child_food_id(name, source, source_id)")
        .eq("parent_food_id", food_id)
        .execute()
    )
    return result.data


async def is_composite_dish(db: Client, food_id: str) -> bool:
    """Check if a food has recipe components (is a composite dish)."""
    result = (
        db.table("recipe_components")
        .select("id", count="exact")
        .eq("parent_food_id", food_id)
        .execute()
    )
    return (result.count or 0) > 0
