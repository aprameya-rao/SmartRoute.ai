# Backend/main.py
from fastapi import FastAPI
from api.v1.endpoints import route # Import your API router
from core.config import settings # Import your settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
)


origins = [
    "http://localhost",
    "http://localhost:5173",  
    "http://127.0.0.1:3000",  # Alternative localhost IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],            # Allow all headers in the request
)


# Include your API router
app.include_router(route.router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SmartRoute.ai EV Optimizer API"}