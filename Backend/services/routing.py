import httpx
from typing import List, Dict, Any, Optional
import polyline 
from core.config import settings
from api.v1.models.route_response import Coordinate, RouteStep # Assuming RouteStep is defined

async def get_detailed_route_from_graphhopper(
    start_coord: Coordinate,
    end_coord: Coordinate,
    vehicle: str = "car" # You can make this dynamic if needed
) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed route information from the GraphHopper Directions API.
    """
    url = settings.GRAPHHOPPER_API_BASE_URL
    params = {
        "point": [f"{start_coord.lat},{start_coord.lon}", f"{end_coord.lat},{end_coord.lon}"],
        "locale": "en",
        "instructions": "true",
        "calc_points": "true",
        "points_encoded": "true", # GraphHopper usually defaults to encoded polylines
        "key": settings.GRAPH_HOPPER_API_KEY,
        "vehicle": vehicle # e.g., 'car', 'bike', 'foot'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()  # Raise HTTPStatusError for bad responses (4xx or 5xx)
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

def parse_graphhopper_response(gh_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a GraphHopper Directions API response into a standardized format.
    Assumes 'points' in the response contains an encoded polyline string.
    """
    parsed_data = {
        "total_distance_km": 0.0,
        "total_duration_s": 0.0,
        "route_geometry": [],
        "route_segments": [] # Using route_segments to align with ev_optimizer's expectations
    }

    if not gh_response or not gh_response.get('paths'):
        print("Invalid or empty GraphHopper response.")
        return parsed_data

    # GraphHopper responses can have multiple paths, usually we take the first one
    path = gh_response['paths'][0]

    # Convert distance from meters to km, time from milliseconds to seconds
    parsed_data['total_distance_km'] = path.get('distance', 0) / 1000.0
    parsed_data['total_duration_s'] = path.get('time', 0) / 1000.0

    # Decode the encoded polyline geometry
    encoded_polyline_string = path.get('points')
    if encoded_polyline_string:
        # GraphHopper typically uses precision 5 or 6. Let's assume 5 for broader compatibility,
        # but check your GH configuration if coordinates seem off.
        decoded_coords_tuples = polyline.decode(encoded_polyline_string, precision=5)
        parsed_data['route_geometry'] = [Coordinate(lat=lat, lon=lon) for lat, lon in decoded_coords_tuples]

    # Parse instructions into RouteStep objects
    # Note: GraphHopper instructions contain 'interval' [start_point_idx, end_point_idx]
    # which maps to the decoded_coords_tuples.
    for instruction in path.get('instructions', []):
        text = instruction.get('text', 'No instruction')
        distance_m = instruction.get('distance', 0)
        time_ms = instruction.get('time', 0)
        name = instruction.get('street_name', None) # GraphHopper often provides street_name
        interval = instruction.get('interval') # [start_point_index, end_point_index]

        segment_geometry: List[Coordinate] = []
        if interval and decoded_coords_tuples:
            try:
                # Slice the main decoded geometry based on the instruction interval
                # +1 because slice end is exclusive
                segment_coords_raw = decoded_coords_tuples[interval[0] : interval[1] + 1]
                segment_geometry = [Coordinate(lat=lat, lon=lon) for lat, lon in segment_coords_raw]
            except IndexError:
                print(f"Warning: Instruction interval {interval} out of bounds for geometry of length {len(decoded_coords_tuples)}.")
                segment_geometry = [] # Fallback to empty if interval is invalid

        parsed_data['route_segments'].append(RouteStep(
            distance_km=distance_m / 1000.0,
            duration_s=time_ms / 1000.0,
            instruction=text,
            name=name,
            geometry=segment_geometry # Attach relevant geometry to each step
        ))
    
    return parsed_data