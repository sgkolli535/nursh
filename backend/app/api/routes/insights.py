from fastapi import APIRouter

from app.agents.insight_writer import get_weekly_insights
from app.data_layer.gap_analysis import analyze_food_group_gaps
from app.db.queries import get_user_health_contexts
from app.db.supabase import get_supabase_client

router = APIRouter()


@router.get("/weekly")
async def get_weekly_insights_endpoint(user_id: str):
    """Get weekly insight narrative via LangGraph insight writer agent."""
    result = await get_weekly_insights(user_id)
    return result


@router.get("/food-groups")
async def get_food_group_summary(user_id: str, days: int = 7):
    """Get food group consumption summary from materialized view."""
    db = get_supabase_client()
    health_contexts = await get_user_health_contexts(db, user_id)
    gaps = await analyze_food_group_gaps(db, user_id, days=days, conditions=health_contexts)
    return {"food_groups": gaps, "days": days}
