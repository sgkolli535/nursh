"""
Database query functions using supabase-py.
All food data queries are deterministic — no AI touches this layer.
"""

from supabase import Client


# ============ Food Groups ============

async def get_all_food_groups(db: Client) -> list[dict]:
    """Get all 13 food group categories."""
    result = db.table("food_groups").select("*").order("name").execute()
    return result.data


async def get_food_group_by_slug(db: Client, slug: str) -> dict | None:
    """Get a single food group by slug (e.g. 'dark_leafy_greens')."""
    result = db.table("food_groups").select("*").eq("slug", slug).single().execute()
    return result.data


# ============ Food Search ============

async def search_foods_fuzzy(db: Client, query: str, limit: int = 20) -> list[dict]:
    """Fuzzy search using pg_trgm word_similarity on name and aliases."""
    # Uses a Supabase RPC function for word_similarity search
    result = db.rpc("search_foods_fuzzy", {"query_text": query, "result_limit": limit}).execute()
    return result.data


async def search_foods_by_tags(db: Client, tags: list[str], limit: int = 20) -> list[dict]:
    """Search foods by multi-attribute tags via GIN index."""
    result = db.table("foods").select("*").contains("tags", tags).limit(limit).execute()
    return result.data


async def get_similar_foods(
    db: Client, food_id: str, exclude_cuisine: str | None = None, limit: int = 5
) -> list[dict]:
    """Find nutritionally similar foods via pgvector cosine similarity."""
    result = db.rpc(
        "find_similar_foods",
        {
            "target_food_id": food_id,
            "exclude_cuisine_region": exclude_cuisine,
            "result_limit": limit,
        },
    ).execute()
    return result.data


# ============ Food Details ============

async def get_food_by_id(db: Client, food_id: str) -> dict | None:
    """Get food with full nutrient profile and food groups."""
    result = db.table("foods").select(
        "*, food_nutrients(*), food_food_groups(*, food_groups(*))"
    ).eq("id", food_id).single().execute()
    return result.data


async def get_food_by_name(db: Client, name: str) -> dict | None:
    """Exact name match (case-insensitive)."""
    result = db.table("foods").select("*").ilike("name", name).limit(1).execute()
    return result.data[0] if result.data else None


# ============ Journal ============

async def get_journal_entries(
    db: Client, user_id: str, date: str | None = None
) -> list[dict]:
    """Get journal entries with items and food groups."""
    query = db.table("journal_entries").select(
        "*, journal_items(*, journal_item_food_groups(food_group_id))"
    ).eq("user_id", user_id).order("date", desc=True)
    if date:
        query = query.eq("date", date)
    result = query.execute()
    return result.data


async def create_journal_entry(
    db: Client, user_id: str, date: str, meal_type: str
) -> dict:
    """Create a new journal entry."""
    result = db.table("journal_entries").insert({
        "user_id": user_id,
        "date": date,
        "meal_type": meal_type,
    }).execute()
    return result.data[0]


async def add_journal_item(
    db: Client,
    entry_id: str,
    food_id: str | None,
    food_name_raw: str,
    portion_description: str,
    portion_grams_est: float | None,
    confidence_score: float,
    food_group_ids: list[str],
) -> dict:
    """Add a food item to a journal entry with food group associations."""
    # Insert the journal item
    item_result = db.table("journal_items").insert({
        "entry_id": entry_id,
        "food_id": food_id,
        "food_name_raw": food_name_raw,
        "portion_description": portion_description,
        "portion_grams_est": portion_grams_est,
        "confidence_score": confidence_score,
    }).execute()
    item = item_result.data[0]

    # Insert food group associations
    if food_group_ids:
        fg_rows = [
            {"item_id": item["id"], "food_group_id": fg_id}
            for fg_id in food_group_ids
        ]
        db.table("journal_item_food_groups").insert(fg_rows).execute()

    return item


# ============ User Profile ============

async def get_user_health_contexts(db: Client, user_id: str) -> list[str]:
    """Get user's active health conditions."""
    result = db.table("health_contexts").select("condition").eq("user_id", user_id).execute()
    return [row["condition"] for row in result.data]


async def get_user_cuisine_preferences(db: Client, user_id: str) -> list[dict]:
    """Get user's cuisine preferences with affinity levels."""
    result = (
        db.table("cuisine_preferences")
        .select("cuisine_region, affinity_level")
        .eq("user_id", user_id)
        .order("affinity_level", desc=True)
        .execute()
    )
    return result.data


async def get_user_dietary_preferences(db: Client, user_id: str) -> list[str]:
    """Get user's dietary preferences."""
    result = (
        db.table("dietary_preferences")
        .select("preference_type")
        .eq("user_id", user_id)
        .execute()
    )
    return [row["preference_type"] for row in result.data]


# ============ Favorites ============

async def get_favorites(db: Client, user_id: str) -> list[dict]:
    """Get user's saved favorite meals."""
    result = (
        db.table("favorite_meals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


async def add_favorite(
    db: Client, user_id: str, label: str, items: list[dict]
) -> dict:
    """Save a meal as a favorite."""
    import json
    result = db.table("favorite_meals").upsert(
        {"user_id": user_id, "label": label, "items": json.dumps(items)},
        on_conflict="user_id,label",
    ).execute()
    return result.data[0]


async def delete_favorite(db: Client, favorite_id: str) -> None:
    """Delete a favorite meal."""
    db.table("favorite_meals").delete().eq("id", favorite_id).execute()


# ============ Recent Items ============

async def get_recent_items(
    db: Client, user_id: str, limit: int = 10
) -> list[dict]:
    """Get user's most recently logged food items (deduplicated by name)."""
    result = (
        db.table("journal_items")
        .select("food_name_raw, food_id, portion_description, confidence_score, journal_entries!inner(user_id)")
        .eq("journal_entries.user_id", user_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    # Deduplicate by food name
    seen = set()
    unique = []
    for row in result.data:
        name = row["food_name_raw"]
        if name.lower() not in seen:
            seen.add(name.lower())
            unique.append({
                "food_name": name,
                "food_id": row["food_id"],
                "portion": row["portion_description"],
            })
        if len(unique) >= limit:
            break
    return unique


# ============ Gap Analysis (reads from materialized view) ============

async def get_daily_food_groups(
    db: Client, user_id: str, days: int = 7
) -> list[dict]:
    """Get food group consumption data from the materialized view."""
    result = db.rpc(
        "get_user_food_group_summary",
        {"target_user_id": user_id, "num_days": days},
    ).execute()
    return result.data


# ============ Evidence Citations ============

async def get_citations_for_rule(db: Client, rule_key: str) -> list[dict]:
    """Get evidence citations for a specific health rule."""
    result = (
        db.table("evidence_citations")
        .select("*")
        .eq("rule_key", rule_key)
        .execute()
    )
    return result.data
