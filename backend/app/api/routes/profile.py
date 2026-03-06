from fastapi import APIRouter
from pydantic import BaseModel

from app.db.queries import (
    get_user_cuisine_preferences,
    get_user_dietary_preferences,
    get_user_health_contexts,
)
from app.db.supabase import get_supabase_client

router = APIRouter()


@router.get("/{user_id}")
async def get_profile(user_id: str):
    """Get user profile with health contexts, dietary and cuisine preferences."""
    db = get_supabase_client()
    health = await get_user_health_contexts(db, user_id)
    dietary = await get_user_dietary_preferences(db, user_id)
    cuisines = await get_user_cuisine_preferences(db, user_id)

    # Get display name from profiles table
    profile = db.table("profiles").select("display_name").eq("id", user_id).single().execute()
    display_name = profile.data.get("display_name", "") if profile.data else ""

    return {
        "id": user_id,
        "display_name": display_name,
        "health_contexts": health,
        "dietary_preferences": dietary,
        "cuisine_preferences": cuisines,
    }


class HealthContextUpdate(BaseModel):
    conditions: list[str]


@router.put("/{user_id}/health-context")
async def update_health_context(user_id: str, body: HealthContextUpdate):
    """Update user's health conditions."""
    db = get_supabase_client()

    # Clear existing and re-insert
    db.table("health_contexts").delete().eq("user_id", user_id).execute()
    if body.conditions:
        rows = [{"user_id": user_id, "condition": c} for c in body.conditions]
        db.table("health_contexts").insert(rows).execute()

    return {"conditions": body.conditions}


class PreferencesUpdate(BaseModel):
    dietary: list[str] | None = None
    cuisines: list[str] | None = None


@router.put("/{user_id}/preferences")
async def update_preferences(user_id: str, body: PreferencesUpdate):
    """Update dietary and cuisine preferences."""
    db = get_supabase_client()

    if body.dietary is not None:
        db.table("dietary_preferences").delete().eq("user_id", user_id).execute()
        if body.dietary:
            rows = [
                {"user_id": user_id, "preference_type": p, "value": "true"}
                for p in body.dietary
            ]
            db.table("dietary_preferences").insert(rows).execute()

    if body.cuisines is not None:
        db.table("cuisine_preferences").delete().eq("user_id", user_id).execute()
        if body.cuisines:
            rows = [
                {"user_id": user_id, "cuisine_region": c, "affinity_level": 5}
                for c in body.cuisines
            ]
            db.table("cuisine_preferences").insert(rows).execute()

    return {"dietary": body.dietary, "cuisines": body.cuisines}
