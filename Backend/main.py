# ev-route-optimizer-backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import route # Import your API router
from core.config import settings   # Import your application settings

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # URL for OpenAPI spec
    docs_url="/docs", # URL for interactive API documentation (Swagger UI)
    redoc_url="/redoc" # URL for alternative API documentation (ReDoc)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(route.router, prefix=settings.API_V1_STR, tags=["Route Optimization"])

# Basic root endpoint for health check or welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to the SmartRoute.ai Backend! Visit /docs for API documentation."}

# Main entry point to run the application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)