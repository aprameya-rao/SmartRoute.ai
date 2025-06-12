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

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your frontend (e.g., running on localhost:5173) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.FRONTEND_ORIGIN)], # List of origins allowed to make requests
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers in requests
)

# Include your API router (all endpoints defined in api/v1/endpoints/route.py)
# They will be prefixed with /api/v1 as defined in settings.API_V1_STR
app.include_router(route.router, prefix=settings.API_V1_STR, tags=["Route Optimization"])

# Basic root endpoint for health check or welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to the SmartRoute.ai Backend! Visit /docs for API documentation."}

# Main entry point to run the application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)