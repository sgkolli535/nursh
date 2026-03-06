from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.meal_parser import parse_meal

router = APIRouter()


class ParseRequest(BaseModel):
    text: str
    user_id: str | None = None


@router.post("/")
async def parse_meal_endpoint(request: ParseRequest):
    """Parse natural language meal description into structured food items via LangGraph agent."""
    result = await parse_meal(request.text)
    return result
