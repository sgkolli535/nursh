from fastapi import APIRouter

from app.data_layer.food_search import combined_search, nutrient_similarity_search
from app.db.queries import get_food_by_id
from app.db.supabase import get_supabase_client

router = APIRouter()


@router.get("/search")
async def search_foods(query: str, cuisine: str | None = None, tags: str | None = None):
    """Search the food database using trigram, tag, and vector search."""
    db = get_supabase_client()
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    results = await combined_search(db, query=query, tags=tag_list, cuisine=cuisine)
    return {"results": results, "query": query}


@router.get("/{food_id}")
async def get_food(food_id: str):
    """Get a single food item with full nutrient profile and data source."""
    db = get_supabase_client()
    food = await get_food_by_id(db, food_id)
    if not food:
        return {"error": "Food not found"}
    return food


@router.get("/{food_id}/similar")
async def get_similar_foods(food_id: str, exclude_cuisine: str | None = None):
    """Find nutritionally similar foods via pgvector cosine similarity."""
    db = get_supabase_client()
    similar = await nutrient_similarity_search(db, food_id, exclude_cuisine)
    return {"similar": similar}
