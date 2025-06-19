from pydantic import BaseModel, Field
from typing import Literal

class RouteRequest(BaseModel):
    start_location: str = Field(..., example="Bengaluru, India")
    end_location: str = Field(..., example="Mysuru, India")
    ev_type: str = Field(..., example="Tesla Model 3 Long Range")
    current_charge_percent: int = Field(default=80, ge=0, le=100, description="Initial battery charge percentage (0-100).")
    charging_preference: Literal["standard", "fast"] = Field(default="standard", example="fast", description="Preferred charging speed ('standard' for any, 'fast' for fast chargers).")
    # Added range_full_charge as a required field
    range_full_charge: float = Field(..., gt=0, description="The full charge range of the EV in kilometers.")