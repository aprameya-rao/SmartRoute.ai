import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API Keys for external services
    # OPEN_ROUTE_SERVICE_API_KEY: str = os.getenv("OPEN_ROUTE_SERVICE_API_KEY", "") # REMOVED THIS LINE
    OPEN_CHARGE_MAP_API_KEY: str = os.getenv("OPEN_CHARGE_MAP_API_KEY", "")
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    GRAPH_HOPPER_API_KEY: str = os.getenv("GRAPH_HOPPER_API_KEY", "")
    GRAPHHOPPER_API_BASE_URL: str = os.getenv("GRAPHHOPPER_API_BASE_URL", "https://graphhopper.com/api/1/route")

    # Other general application settings
    APP_NAME: str = "SmartRoute.ai Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
    PROJECT_NAME: str = "SmartRoute.ai"

settings = Settings()

print(f"DEBUG: GraphHopper API Key loaded: '{settings.GRAPH_HOPPER_API_KEY}'")
print(f"DEBUG: GraphHopper Base URL loaded: '{settings.GRAPHHOPPER_API_BASE_URL}'")
