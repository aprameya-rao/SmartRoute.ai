# ev-route-optimizer-backend/core/config.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "SmartRoute.ai"
    API_V1_STR: str = "/api/v1"

    # --- IMPORTANT: Obtain these API keys from their respective providers ---
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    ORS_API_KEY: str = os.getenv("ORS_API_KEY", "")
    # Open Charge Map key is optional for basic usage, but good to have for rate limits
    OPEN_CHARGE_MAP_API_KEY: str = os.getenv("OPEN_CHARGE_MAP_API_KEY", "")

    # Frontend origin for CORS. Adjust if your frontend runs on a different port/domain.
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173") 

settings = Settings()