# Backend/main.py
from fastapi import FastAPI
from api.v1.endpoints import route # Import your API router
from core.config import settings # Import your settings

app = FastAPI(
    title=settings.APP_NAME,
)

# Include your API router
app.include_router(route.router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SmartRoute.ai EV Optimizer API"}