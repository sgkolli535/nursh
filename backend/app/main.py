from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import food, insights, journal, parse, profile, recommend
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="A health-focused food journal API — nutrient balance over calorie counting",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(food.router, prefix="/api/food", tags=["food"])
app.include_router(parse.router, prefix="/api/parse", tags=["parse"])
app.include_router(recommend.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}
