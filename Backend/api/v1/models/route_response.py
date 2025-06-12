# ev-route-optimizer-backend/api/v1/models/route_response.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

class Coordinate(BaseModel):
    """Represents a geographical coordinate (latitude, longitude)."""
    lat: float = Field(..., example=12.9716)
    lon: float = Field(..., example=77.5946)

class RouteSegment(BaseModel):
    """
    Represents a segment of the optimized route, which can be either driving or a charging stop.
    """
    type: Literal["driving", "charging_stop"] = Field(..., description="Type of segment: 'driving' or 'charging_stop'.")
    start_coord: Coordinate = Field(..., description="Starting coordinates of the segment.")
    end_coord: Coordinate = Field(..., description="Ending coordinates of the segment.")
    distance_km: float = Field(default=0.0, description="Distance covered in this segment in kilometers.")
    duration_minutes: float = Field(default=0.0, description="Duration of this segment in minutes (driving time or charging time).")

    # Fields specific to driving segments
    start_soc_percent: Optional[float] = Field(None, description="State of Charge (%) at the beginning of a driving segment.")
    end_soc_percent: Optional[float] = Field(None, description="State of Charge (%) at the end of a driving segment.")
    energy_consumption_kwh: Optional[float] = Field(None, description="Energy consumed (kWh) during a driving segment.")

    # Fields specific to charging stop segments
    station_id: Optional[str] = Field(None, description="ID of the charging station if this is a charging stop.")
    station_name: Optional[str] = Field(None, description="Name of the charging station.")
    charge_added_kwh: Optional[float] = Field(None, description="Amount of energy added (kWh) during the charging stop.")
    charge_added_percent: Optional[float] = Field(None, description="Percentage of battery charged during the stop.")

class ChargingStation(BaseModel):
    """
    Detailed information about a charging station.
    This model is primarily for displaying individual station details if needed,
    but the essential info is embedded in RouteSegment for stops.
    """
    id: str
    name: str
    address: str
    coordinates: Coordinate
    connection_types: List[Dict[str, Any]] = Field(default_factory=list, description="List of available connector types and their details.")
    power_kw: Optional[float] = Field(None, description="Maximum power (kW) available at this station/connection.")
    usage_cost: Optional[str] = Field(None, description="Cost information for using the station.")
    is_free: Optional[bool] = Field(None, description="True if the station is free to use.")
    operator_info: Optional[Dict[str, Any]] = Field(None, description="Information about the station operator.")
    status_type: Optional[Dict[str, Any]] = Field(None, description="Operational status of the station.")

    # Added by our backend logic for clarity in recommended stops
    recommended_charge_minutes: Optional[int] = Field(None, description="Recommended charging duration at this stop in minutes.")
    estimated_charge_added_kwh: Optional[float] = Field(None, description="Estimated energy added during the recommended charge time.")

class RouteSummary(BaseModel):
    """Summary of the optimized route."""
    total_distance_km: float = Field(..., example=150.5, description="Total distance of the route in kilometers.")
    total_duration_minutes: float = Field(..., example=180, description="Total travel time including driving and charging in minutes.")
    total_driving_minutes: float = Field(..., example=120, description="Total time spent driving in minutes.")
    total_charging_minutes: float = Field(..., example=60, description="Total time spent charging in minutes.")
    estimated_charging_stops: int = Field(..., example=2, description="Number of calculated charging stops.")
    total_energy_consumption_kwh: Optional[float] = Field(None, description="Total net energy consumed (driving minus charged) in kWh.")
    final_charge_percent: Optional[int] = Field(None, description="Estimated battery charge percentage upon arrival at destination.")

class RouteResponse(BaseModel):
    """The complete response for an optimized EV route."""
    message: str = "Route optimized successfully"
    summary: RouteSummary = Field(..., description="Summary of the optimized route.")
    route_segments: List[RouteSegment] = Field(..., description="Ordered list of driving and charging segments.")
    route_geometry: Optional[List[Coordinate]] = Field(None, description="Full polyline coordinates of the optimized route (driving paths only).")
    # recommended_charging_stations: List[ChargingStation] = Field(default_factory=list)
    # Note: Charging station details are now embedded within `route_segments` for simplicity.