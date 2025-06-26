from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class Coordinate(BaseModel):
    """Represents a geographical coordinate (latitude, longitude)."""
    lat: float
    lon: float

class RouteStep(BaseModel):
    """
    Represents a single instruction or maneuver within a route segment.
    This is often what comes directly from routing APIs for turn-by-turn.
    """
    distance_km: float = Field(..., description="Distance of this step in kilometers.")
    duration_s: float = Field(..., description="Duration of this step in seconds.")
    instruction: str = Field(..., description="Text instruction for this step (e.g., 'Turn left').")
    name: Optional[str] = Field(None, description="Name of the street/road for this step.")
    geometry: Optional[List[Coordinate]] = Field(None, description="Geometry (polyline) for this specific step.")


class RouteSegment(BaseModel):
    """
    Represents a segment of the overall route, which can be driving or charging.
    This is a more abstract segment defined by your optimizer, not necessarily
    a single step from a routing API.
    """
    type: str = Field(..., description="Type of segment (e.g., 'driving', 'charging_stop').")
    start_coord: Coordinate = Field(..., description="Start coordinate of the segment.")
    end_coord: Coordinate = Field(..., description="End coordinate of the segment.")
    distance_km: float = Field(..., description="Distance of the segment in kilometers.")
    duration_minutes: float = Field(..., description="Duration of the segment in minutes (driving or charging).")
    start_soc_percent: float = Field(..., description="SoC at the start of this segment.")
    end_soc_percent: float = Field(..., description="SoC at the end of this segment.")
    energy_consumption_kwh: Optional[float] = Field(None, description="Energy consumed in kWh for driving segments.")

    # Fields specific to charging stops
    station_id: Optional[str] = Field(None, description="ID of the charging station, if applicable.")
    station_name: Optional[str] = Field(None, description="Name of the charging station, if applicable.")
    charge_added_kwh: Optional[float] = Field(None, description="Amount of charge added in kWh, if applicable.")
    charge_added_percent: Optional[float] = Field(None, description="Amount of charge added in percentage, if applicable.")


class ChargingStation(BaseModel):
    """Represents a charging station."""
    id: str = Field(..., description="Unique identifier for the charging station.")
    name: str = Field(..., description="Name of the charging station.")
    coordinates: Coordinate = Field(..., description="Geographical coordinates of the station.")
    power_kw: Optional[float] = Field(None, description="Charging power in kilowatts (kW).")
    
    # NEW FIELDS ADDED HERE TO MATCH charging_stations.py OUTPUT
    address: Optional[str] = Field(None, description="Full address of the charging station.")
    connection_types: List[Dict[str, Any]] = Field([], description="List of available connection types at the station.")
    is_free: Optional[bool] = Field(None, description="Indicates if the charging station offers free charging.")

    # These fields are added dynamically in ev_optimizer, so they are Optional
    recommended_charge_minutes: Optional[int] = Field(None, description="Recommended charging duration at this station in minutes for the current trip.")
    estimated_charge_added_kwh: Optional[float] = Field(None, description="Estimated energy added in kWh at this stop.")


class RouteSummary(BaseModel):
    """Summarizes the planned route."""
    total_distance_km: float = Field(..., description="Total distance of the route in kilometers.")
    total_duration_minutes: float = Field(..., description="Total duration (driving + charging) in minutes.")
    total_driving_minutes: float = Field(..., description="Total driving duration in minutes.")
    total_charging_minutes: float = Field(..., description="Total charging duration in minutes.")
    estimated_charging_stops: int = Field(..., description="Number of estimated charging stops.")
    total_energy_consumption_kwh: float = Field(..., description="Total energy consumed (driving) in kWh.")
    final_charge_percent: int = Field(..., description="Estimated final SoC at the destination in percent.")

# ADDED THIS CLASS: RouteDetails
class RouteDetails(BaseModel):
    """
    Represents the detailed parsed response from a routing API (like GraphHopper).
    This is what parse_graphhopper_response should return.
    """
    total_distance_km: float
    total_duration_s: float
    route_geometry: List[Coordinate]
    route_segments: List[RouteStep]


class RouteResponse(BaseModel):
    """The complete response for an EV route planning request."""
    message: str = Field(..., description="A message regarding the route planning status.")
    summary: RouteSummary = Field(..., description="Summary of the planned route.")
    route_segments: List[RouteStep] = Field(..., description="List of detailed route steps/instructions. (NOTE: This now represents ALL steps from the full optimized route, combining driving and charging.)")
    route_geometry: List[Coordinate] = Field(..., description="Full geographical geometry of the route as a list of coordinates.")
    charging_locations: List[ChargingStation] = Field(..., description="Details of recommended charging stations along the route.")

# You might have an input request model here too, like RouteRequest
class RouteRequest(BaseModel):
    start_location: str = Field(..., description="Starting address or location name.")
    end_location: str = Field(..., description="Destination address or location name.")
    ev_type: str = Field(..., description="Type of EV (e.g., 'Tesla Model 3 Long Range', 'Tata Nexon EV').")
    current_charge_percent: int = Field(..., ge=0, le=100, description="Current State of Charge (SoC) in percentage (0-100).")
    range_full_charge: float = Field(..., gt=0, description="Manufacturer's claimed full range in km for the EV type.")
    charging_preference: str = Field("standard", description="Charging preference: 'standard' or 'fast'.")