from fastapi import APIRouter

from app.agents.recommender import get_recommendations

router = APIRouter()


@router.get("/")
async def get_recommendations_endpoint(user_id: str):
    """Get personalized food recommendations via LangGraph recommendation agent."""
    result = await get_recommendations(user_id)
    return result
