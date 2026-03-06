from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.queries import (
    add_favorite,
    add_journal_item,
    create_journal_entry,
    delete_favorite,
    get_favorites,
    get_journal_entries,
    get_recent_items,
)
from app.db.supabase import get_supabase_client

router = APIRouter()


class JournalItemInput(BaseModel):
    food_id: str | None = None
    food_name_raw: str
    portion_description: str = "1 serving"
    portion_grams_est: float | None = None
    confidence_score: float = 1.0
    food_group_ids: list[str] = []


class CreateEntryRequest(BaseModel):
    user_id: str
    meal_type: str
    date: str | None = None  # defaults to today
    items: list[JournalItemInput]


@router.get("/")
async def get_journal(user_id: str, date: str | None = None):
    """Get journal entries for a user, optionally filtered by date."""
    db = get_supabase_client()
    entries = await get_journal_entries(db, user_id, date)
    return {"entries": entries, "date": date}


@router.post("/")
async def create_entry(request: CreateEntryRequest):
    """Create a new journal entry with parsed food items."""
    db = get_supabase_client()
    entry_date = request.date or str(date.today())

    # Create or get the journal entry for this meal
    try:
        entry = await create_journal_entry(
            db, request.user_id, entry_date, request.meal_type
        )
    except Exception:
        # Entry might already exist for this user/date/meal — fetch it
        result = (
            db.table("journal_entries")
            .select("*")
            .eq("user_id", request.user_id)
            .eq("date", entry_date)
            .eq("meal_type", request.meal_type)
            .single()
            .execute()
        )
        entry = result.data

    # Add each food item
    saved_items = []
    for item in request.items:
        saved = await add_journal_item(
            db,
            entry_id=entry["id"],
            food_id=item.food_id,
            food_name_raw=item.food_name_raw,
            portion_description=item.portion_description,
            portion_grams_est=item.portion_grams_est,
            confidence_score=item.confidence_score,
            food_group_ids=item.food_group_ids,
        )
        saved_items.append(saved)

    return {
        "id": entry["id"],
        "date": entry_date,
        "meal_type": request.meal_type,
        "items": saved_items,
    }


# ============ Recent Items ============


@router.get("/recent")
async def get_recent(user_id: str, limit: int = 10):
    """Get recently logged food items (deduplicated)."""
    db = get_supabase_client()
    items = await get_recent_items(db, user_id, limit)
    return {"items": items}


# ============ Favorites ============


class FavoriteInput(BaseModel):
    user_id: str
    label: str
    items: list[dict]


@router.get("/favorites")
async def list_favorites(user_id: str):
    """Get user's saved favorite meals."""
    db = get_supabase_client()
    favorites = await get_favorites(db, user_id)
    return {"favorites": favorites}


@router.post("/favorites")
async def save_favorite(body: FavoriteInput):
    """Save a meal as a favorite for quick re-logging."""
    db = get_supabase_client()
    fav = await add_favorite(db, body.user_id, body.label, body.items)
    return fav


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(favorite_id: str):
    """Delete a saved favorite."""
    db = get_supabase_client()
    await delete_favorite(db, favorite_id)
    return {"deleted": True}
