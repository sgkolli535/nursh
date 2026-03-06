"""
Advanced food search combining trigram similarity, tag matching, and pgvector.
Three strategies, usable independently or combined.
"""

from supabase import Client


async def fuzzy_search(db: Client, query: str, limit: int = 10) -> list[dict]:
    """Fuzzy search using pg_trgm word_similarity.

    word_similarity is better than similarity() for our use case because
    "dal" matches "dal makhani" even though full-string similarity is low.

    Requires an RPC function in Supabase:
    CREATE OR REPLACE FUNCTION search_foods_fuzzy(query_text text, result_limit int DEFAULT 10)
    RETURNS TABLE(id uuid, name text, cuisine_region text, similarity float)
    AS $$
      SELECT id, name, cuisine_region,
             GREATEST(word_similarity(query_text, name), similarity(query_text, name)) as sim
      FROM foods
      WHERE word_similarity(query_text, name) > 0.3
         OR query_text % ANY(aliases)
      ORDER BY sim DESC
      LIMIT result_limit;
    $$ LANGUAGE sql;
    """
    result = db.rpc(
        "search_foods_fuzzy",
        {"query_text": query.lower(), "result_limit": limit},
    ).execute()
    return result.data


async def tag_search(
    db: Client, tags: list[str], limit: int = 10
) -> list[dict]:
    """Multi-attribute tag search via GIN index.

    Answers queries like "high iron vegetarian Indian foods":
    tags = ['iron_rich', 'vegetarian', 'indian']

    Uses the @> (contains) operator which hits the GIN index.
    """
    result = (
        db.table("foods")
        .select("id, name, aliases, tags, cuisine_region, source, source_id")
        .contains("tags", tags)
        .limit(limit)
        .execute()
    )
    return result.data


async def nutrient_similarity_search(
    db: Client,
    food_id: str,
    exclude_cuisine: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Find nutritionally similar foods via pgvector cosine similarity.

    Powers cross-cultural food discovery:
    "You enjoy dal (South Indian). Here are similar foods from other cuisines."

    Requires an RPC function in Supabase:
    CREATE OR REPLACE FUNCTION find_similar_foods(
      target_food_id uuid,
      exclude_cuisine_region text DEFAULT NULL,
      result_limit int DEFAULT 5
    )
    RETURNS TABLE(id uuid, name text, cuisine_region text, similarity float)
    AS $$
      SELECT f.id, f.name, f.cuisine_region,
             1 - (f.nutrient_vector <=> t.nutrient_vector) as similarity
      FROM foods f, foods t
      WHERE t.id = target_food_id
        AND f.id != target_food_id
        AND f.nutrient_vector IS NOT NULL
        AND (exclude_cuisine_region IS NULL OR f.cuisine_region != exclude_cuisine_region)
      ORDER BY f.nutrient_vector <=> t.nutrient_vector
      LIMIT result_limit;
    $$ LANGUAGE sql;
    """
    result = db.rpc(
        "find_similar_foods",
        {
            "target_food_id": food_id,
            "exclude_cuisine_region": exclude_cuisine,
            "result_limit": limit,
        },
    ).execute()
    return result.data


async def combined_search(
    db: Client,
    query: str | None = None,
    tags: list[str] | None = None,
    cuisine: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Combined search: fuzzy name + tags + optional cuisine filter."""
    if query and tags:
        # Both: fuzzy search filtered by tags
        fuzzy_results = await fuzzy_search(db, query, limit=50)
        fuzzy_ids = [r["id"] for r in fuzzy_results]
        if not fuzzy_ids:
            return []
        tag_result = (
            db.table("foods")
            .select("*")
            .in_("id", fuzzy_ids)
            .contains("tags", tags)
            .limit(limit)
            .execute()
        )
        return tag_result.data
    elif query:
        results = await fuzzy_search(db, query, limit)
        if cuisine:
            return [r for r in results if r.get("cuisine_region") == cuisine]
        return results
    elif tags:
        results = await tag_search(db, tags, limit)
        if cuisine:
            return [r for r in results if r.get("cuisine_region") == cuisine]
        return results
    else:
        # No filters: return recent/popular
        result = db.table("foods").select("*").limit(limit).execute()
        return result.data
