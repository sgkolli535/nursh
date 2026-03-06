"""
Food group gap analysis.
Reads from the user_daily_food_groups materialized view for performance.
Deterministic — NO AI.
"""

from datetime import date, timedelta

from supabase import Client

from app.data_layer.food_groups import ALL_FOOD_GROUPS


# Default target: each food group should appear at least N days per week
DEFAULT_TARGETS = {slug: 3 for slug in ALL_FOOD_GROUPS}
# Some food groups are more critical than others
DEFAULT_TARGETS.update({
    "dark_leafy_greens": 5,
    "legumes_pulses": 5,
    "whole_grains": 6,
    "citrus_berries": 4,
    "fermented_foods": 4,
    "omega3_sources": 3,
    "iron_rich_proteins": 4,
    "calcium_sources": 5,
})


def get_targets_for_conditions(
    conditions: list[str], base_targets: dict | None = None
) -> dict[str, int]:
    """Adjust food group targets based on health conditions.

    Each condition can increase the priority (target days) for specific groups.
    """
    targets = dict(base_targets or DEFAULT_TARGETS)

    for condition in conditions:
        if condition == "iron_deficiency_anemia":
            targets["iron_rich_proteins"] = 7
            targets["dark_leafy_greens"] = 7
            targets["citrus_berries"] = 6  # Vitamin C for absorption
            targets["legumes_pulses"] = 6
        elif condition == "pcos":
            targets["omega3_sources"] = 5
            targets["dark_leafy_greens"] = 6
            targets["nuts_seeds"] = 5  # Magnesium
            targets["herbs_spices"] = 5  # Anti-inflammatory
        elif condition == "hypothyroidism":
            targets["nuts_seeds"] = 5  # Selenium (Brazil nuts)
            targets["omega3_sources"] = 4
        elif condition in ("pregnancy_t1", "pregnancy_t2", "pregnancy_t3"):
            targets["dark_leafy_greens"] = 7  # Folate
            targets["iron_rich_proteins"] = 6
            targets["calcium_sources"] = 7
            targets["omega3_sources"] = 5  # DHA
            targets["legumes_pulses"] = 6
        elif condition == "perimenopause":
            targets["calcium_sources"] = 7
            targets["legumes_pulses"] = 5  # Phytoestrogens
            targets["nuts_seeds"] = 5  # Magnesium
        elif condition == "type2_diabetes":
            targets["legumes_pulses"] = 7  # High fiber, low GI
            targets["whole_grains"] = 6
            targets["dark_leafy_greens"] = 6
        elif condition in ("celiac", "gluten_sensitivity"):
            # Whole grains target stays but should be gluten-free options
            targets["whole_grains"] = 5
        elif condition in ("vegetarian", "vegan"):
            targets["legumes_pulses"] = 7  # Protein + iron
            targets["nuts_seeds"] = 6  # Omega-3, zinc
            targets["dark_leafy_greens"] = 6

    return targets


async def analyze_food_group_gaps(
    db: Client,
    user_id: str,
    days: int = 7,
    conditions: list[str] | None = None,
) -> list[dict]:
    """Analyze which food groups are missing over the past N days.

    Returns a list of {food_group_slug, food_group_name, days_present,
    target_days, gap_severity} sorted by gap severity.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # Query materialized view for user's food group data
    result = db.rpc(
        "get_user_food_group_summary",
        {
            "target_user_id": user_id,
            "start_date": str(start_date),
            "end_date": str(end_date),
        },
    ).execute()

    # Build presence map: {food_group_slug: days_present}
    presence: dict[str, int] = {}
    for row in (result.data or []):
        slug = row.get("slug") or row.get("food_group_slug", "")
        presence[slug] = row.get("days_present", 0)

    # Get food group names
    fg_result = db.table("food_groups").select("slug, name").execute()
    slug_to_name = {row["slug"]: row["name"] for row in fg_result.data}

    # Compute targets adjusted for health conditions
    targets = get_targets_for_conditions(conditions or [])

    # Build gap analysis
    gaps = []
    for slug in ALL_FOOD_GROUPS:
        days_present = presence.get(slug, 0)
        target = targets.get(slug, 3)
        gap = max(0, target - days_present)

        if gap == 0:
            severity = "none"
        elif gap <= 1:
            severity = "low"
        elif gap <= 3:
            severity = "medium"
        else:
            severity = "high"

        gaps.append({
            "food_group_slug": slug,
            "food_group_name": slug_to_name.get(slug, slug),
            "days_present": days_present,
            "target_days": target,
            "gap": gap,
            "gap_severity": severity,
        })

    # Sort by gap severity (high first)
    severity_order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    gaps.sort(key=lambda g: (severity_order[g["gap_severity"]], -g["gap"]))

    return gaps
