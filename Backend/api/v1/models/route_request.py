# ev-route-optimizer-backend/api/v1/models/route_request.py
from pydantic import BaseModel, Field

class RouteRequest(BaseModel):
    """
    Pydantic model for the incoming route optimization request.
    """
    start_location: str = Field(..., example="Bengaluru, India")
    end_location: str = Field(..., example="Mysuru, India")
    ev_type: str = Field(..., example="Tesla Model 3 Long Range")
    current_charge_percent: int = Field(default=80, ge=0, le=100, description="Initial battery charge percentage (0-100).")
    charging_preference: str = Field(default="standard", example="fast", description="Preferred charging speed (e.g., 'standard', 'fast'). Currently affects charger selection, not a detailed profile.")
    waypoints: list[str] = Field(default_factory=list, example=["Mandya, India"], description="Optional list of intermediate stops.")