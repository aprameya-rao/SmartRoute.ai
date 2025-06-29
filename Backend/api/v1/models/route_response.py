# Backend/api/v1/models/route_response.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Define Coordinate first, as it's used by other models
class Coordinate(BaseModel):
    lat: float
    lon: float

# Define ChargingStation, as it's used by the charging station lookup function
class ChargingStation(BaseModel):
    id: str
    name: str
    address: str
    coordinates: Coordinate
    connection_types: List[Dict[str, Any]] # A list of dictionaries for connections
    power_kw: float # Max power available at the station
    is_free: bool

# Define RouteStep, which uses Coordinate
class RouteStep(BaseModel):
    distance_km: float
    duration_s: int
    instruction: str
    name: str
    geometry: List[Coordinate]

# Define RouteDetails, which uses Coordinate and RouteStep
class RouteDetails(BaseModel):
    total_distance_km: float
    total_duration_s: int
    route_segments: List[RouteStep]
    route_geometry: List[Coordinate]

# Define RouteSummary with camelCase fields for consistent API output (Pydantic validation fix)
class RouteSummary(BaseModel):
    totalDistanceKm: float
    totalDurationMinutes: float
    totalDrivingMinutes: float
    totalChargingMinutes: float
    estimatedChargingStops: int
    totalEnergyConsumptionKwh: float
    finalChargePercent: float

# Define RouteResponse, the main response model for your API
class RouteResponse(BaseModel):
    success: bool
    message: str
    route_summary: Optional[RouteSummary] = None
    route_details: Optional[RouteDetails] = None
    # If you want the route response to optionally include a list of charging stations, uncomment this:
    # charging_stations: Optional[List[ChargingStation]] = None