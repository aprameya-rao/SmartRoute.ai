import httpx
from typing import List, Dict, Any, Optional
import polyline 
from core.config import settings
from api.v1.models.route_response import Coordinate, RouteStep, RouteDetails # Ensure RouteDetails is imported

async def get_detailed_route_from_graphhopper(
    start_coord: Coordinate,
    end_coord: Coordinate,
    vehicle: str = "car"
) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed route information from the GraphHopper Directions API.
    Returns the raw JSON response or None on error.
    """
    url = settings.GRAPHHOPPER_API_BASE_URL
    params = {
        "point": [f"{start_coord.lat},{start_coord.lon}", f"{end_coord.lat},{end_coord.lon}"],
        "locale": "en",
        "instructions": "true",
        "calc_points": "true",
        "points_encoded": "true",
        "key": settings.GRAPH_HOPPER_API_KEY,
        "vehicle": vehicle
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"GraphHopper request error: An error occurred while requesting {e.request.url!r}.")
            print(f"{e.__class__.__name__}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"GraphHopper HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error in GraphHopper routing: {e}")
            return None

def parse_graphhopper_response(gh_response: Optional[Dict[str, Any]]) -> RouteDetails:
    """
    Parses a GraphHopper Directions API response into a structured RouteDetails object.
    Handles None input gracefully.
    """
    total_distance_km = 0.0
    total_duration_s = 0.0
    route_geometry: List[Coordinate] = []
    route_segments: List[RouteStep] = []

    # CRITICAL CHANGE: Check if gh_response is None FIRST
    if gh_response is None or not gh_response.get('paths'):
        print("Invalid, empty, or None GraphHopper response. Returning default RouteDetails.")
        return RouteDetails(
            total_distance_km=total_distance_km,
            total_duration_s=total_duration_s,
            route_geometry=route_geometry,
            route_segments=route_segments
        )

    path = gh_response['paths'][0]

    total_distance_km = path.get('distance', 0) / 1000.0
    total_duration_s = path.get('time', 0) / 1000.0

    encoded_polyline_string = path.get('points')
    decoded_coords_tuples = []
    if encoded_polyline_string:
        decoded_coords_tuples = polyline.decode(encoded_polyline_string, precision=5)
        route_geometry = [Coordinate(lat=lat, lon=lon) for lat, lon in decoded_coords_tuples]

    for instruction in path.get('instructions', []):
        text = instruction.get('text', 'No instruction')
        distance_m = instruction.get('distance', 0)
        time_ms = instruction.get('time', 0)
        name = instruction.get('street_name', None)
        interval = instruction.get('interval')

        segment_geometry: List[Coordinate] = []
        if interval and decoded_coords_tuples:
            try:
                segment_coords_raw = decoded_coords_tuples[interval[0] : interval[1] + 1]
                segment_geometry = [Coordinate(lat=lat, lon=lon) for lat, lon in segment_coords_raw]
            except IndexError:
                print(f"Warning: Instruction interval {interval} out of bounds for geometry of length {len(decoded_coords_tuples)}.")
                segment_geometry = []

        route_segments.append(RouteStep(
            distance_km=distance_m / 1000.0,
            duration_s=time_ms / 1000.0,
            instruction=text,
            name=name,
            geometry=segment_geometry
        ))

    return RouteDetails(
        total_distance_km=total_distance_km,
        total_duration_s=total_duration_s,
        route_geometry=route_geometry,
        route_segments=route_segments
    )