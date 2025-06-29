# Backend/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # You can remove OPEN_ROUTE_SERVICE_API_KEY and GEOAPIFY_API_KEY if they are no longer used
    # or keep them for now if you might revert or have other uses.
    OPEN_ROUTE_SERVICE_API_KEY: str # Keep for now if not explicitly told to remove
    GEOAPIFY_API_KEY: str # Keep for now if not explicitly told to remove

    APP_NAME: str = "SmartRoute.ai"
    Maps_API_KEY: str # <--- NEW: Your Google Cloud API Key

    OPEN_CHARGE_MAP_API_KEY: str # This remains as is, for charging stations
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./ev_optimizer.db"

    # Pydantic settings config model
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()