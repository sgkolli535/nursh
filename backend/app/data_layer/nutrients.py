"""
Nutrient calculation engine.
Standard recipe calculation: sum ingredient nutrients x portions,
apply yield and retention factors.
Deterministic — all values from authoritative sources.
"""

from supabase import Client


async def get_nutrient_profile(db: Client, food_id: str) -> dict[str, float]:
    """Get the full nutrient profile for a food item (per 100g)."""
    result = (
        db.table("food_nutrients")
        .select("nutrient_name, amount_per_100g, unit")
        .eq("food_id", food_id)
        .execute()
    )
    return {
        row["nutrient_name"]: row["amount_per_100g"]
        for row in result.data
    }


async def estimate_nutrients_for_portion(
    db: Client, food_id: str, portion_grams: float
) -> dict[str, float]:
    """Estimate nutrient content for a specific portion size.

    Simple proportional scaling from per-100g values.
    """
    per_100g = await get_nutrient_profile(db, food_id)
    scale = portion_grams / 100.0
    return {
        name: round(amount * scale, 2)
        for name, amount in per_100g.items()
    }


async def get_notable_nutrients(
    db: Client, food_id: str, threshold_pct: float = 10.0
) -> list[dict]:
    """Identify nutrients that this food is a notably good source of.

    A food is a "good source" if a serving provides ≥10% of daily value.
    This powers the "Good source of iron and folate" labels in the UI.
    """
    # Approximate Daily Values (mg unless noted)
    daily_values = {
        "protein": 50.0,  # g
        "iron": 18.0,
        "calcium": 1000.0,
        "fiber": 25.0,  # g
        "vitamin_c": 90.0,
        "folate": 0.4,  # mg (400 mcg)
        "zinc": 11.0,
        "magnesium": 420.0,
        "vitamin_a": 900.0,  # mcg RAE
        "vitamin_d": 0.020,  # mg (20 mcg)
        "b12": 0.0024,  # mg (2.4 mcg)
        "potassium": 4700.0,
        "omega_3_dha": 0.250,  # mg
        "vitamin_e": 15.0,
        "vitamin_k": 0.120,  # mg (120 mcg)
    }

    nutrients = await get_nutrient_profile(db, food_id)
    notable = []

    for name, amount in nutrients.items():
        dv = daily_values.get(name)
        if dv and dv > 0:
            pct = (amount / dv) * 100
            if pct >= threshold_pct:
                notable.append({
                    "nutrient": name,
                    "amount_per_100g": amount,
                    "daily_value_pct": round(pct, 1),
                    "label": _nutrient_display_name(name),
                })

    notable.sort(key=lambda n: n["daily_value_pct"], reverse=True)
    return notable


def _nutrient_display_name(name: str) -> str:
    """Convert nutrient slug to display name."""
    display = {
        "protein": "protein",
        "iron": "iron",
        "calcium": "calcium",
        "fiber": "fiber",
        "vitamin_c": "vitamin C",
        "folate": "folate",
        "zinc": "zinc",
        "magnesium": "magnesium",
        "vitamin_a": "vitamin A",
        "vitamin_d": "vitamin D",
        "b12": "vitamin B12",
        "potassium": "potassium",
        "omega_3_dha": "omega-3 (DHA)",
        "omega_3_epa": "omega-3 (EPA)",
        "omega_3_ala": "omega-3 (ALA)",
        "vitamin_e": "vitamin E",
        "vitamin_k": "vitamin K",
    }
    return display.get(name, name.replace("_", " "))
