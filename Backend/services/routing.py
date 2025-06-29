# Backend/services/routing.py

import httpx
from typing import List, Dict, Any, Optional
import polyline # Still useful for decoding Google's polylines
from core.config import settings
from api.v1.models.route_response import Coordinate, RouteStep, RouteDetails
import re # For stripping HTML tags
import traceback # Import for detailed error logging


async def get_detailed_route_from_google(
    start_coord: Coordinate,
    end_coord: Coordinate,
    mode: str = "driving" # Google Directions API uses 'driving', 'walking', 'bicycling', 'transit'
) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed route information from the Google Directions API.
    Returns the raw JSON response or None on error.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        "origin": f"{start_coord.lat},{start_coord.lon}",
        "destination": f"{end_coord.lat},{end_coord.lon}",
        "mode": mode,
        "units": "metric", # For kilometers and meters
        "key": settings.Maps_API_KEY,
        "alternatives": "false", # We usually want a single best route for optimization
        "overview_polyline": "true" # Request overview polyline for the whole route
    }

    print(f"DEBUG: Google Directions Request URL: {url}")
    print(f"DEBUG: Google Directions Request Params: {params}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            data = response.json()
            print(f"DEBUG: Raw Google Directions Response: {data}")

            if data.get("status") == "OK":
                return data
            elif data.get("status") == "ZERO_RESULTS":
                print(f"Google Directions API returned ZERO_RESULTS for route from {start_coord} to {end_coord}.")
                return None
            else:
                # Log any other non-OK status with its message
                print(f"Google Directions API Error: {data.get('status')}. Error message: {data.get('error_message', 'No error message')}")
                return None

        except httpx.RequestError as e:
            print(f"Google Directions request error: An error occurred while requesting {e.request.url!r}. Details: {e}")
            traceback.print_exc()
            return None
        except httpx.HTTPStatusError as e:
            print(f"Google Directions HTTP error: {e.response.status_code} - {e.response.text}")
            print(f"Response content: {e.response.text}")
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"Unexpected error in Google Directions routing for {start_coord} to {end_coord}: {e}")
            traceback.print_exc()
            return None

def parse_google_directions_response(google_response: Optional[Dict[str, Any]]) -> 'RouteDetails':
    """
    Parses the Google Directions API JSON response into a structured RouteDetails object.
    """
    if not google_response or not google_response.get('routes'):
        print("Invalid, empty, or None Google Directions response. Returning default RouteDetails.")
        return RouteDetails()

    # Assuming we take the first route
    route = google_response['routes'][0]
    
    total_distance_meters = 0
    total_duration_seconds = 0
    route_segments: List[RouteStep] = []
    all_route_geometry: List[Coordinate] = []

    # Google Directions API provides legs (segments between waypoints/origin/destination)
    # And steps within each leg
    for leg in route.get('legs', []):
        if 'distance' in leg and 'value' in leg['distance']:
            total_distance_meters += leg['distance']['value']
        if 'duration' in leg and 'value' in leg['duration']:
            total_duration_seconds += leg['duration']['value']

        for step in leg.get('steps', []):
            step_distance_meters = step.get('distance', {}).get('value', 0)
            step_duration_seconds = step.get('duration', {}).get('value', 0)
            
            # Google provides HTML instructions, convert to text
            instruction_html = step.get('html_instructions', '')
            instruction_text = strip_html_tags(instruction_html)

            # Google does not typically provide a 'name' for each step like some other APIs.
            # You can derive a name from the `html_instructions` or `maneuver` if needed,
            # or leave it empty as per your model.
            step_name = "" 

            # Decode step-specific polyline (if available)
            step_geometry: List[Coordinate] = []
            if 'polyline' in step and 'points' in step['polyline']:
                try:
                    decoded_step_coords = polyline.decode(step['polyline']['points'])
                    step_geometry = [Coordinate(lat=lat, lon=lon) for lat, lon in decoded_step_coords]
                except Exception as e:
                    print(f"Error decoding step polyline for step: {instruction_text}. Error: {e}")
                    traceback.print_exc()

            route_segments.append(RouteStep(
                distance_km=step_distance_meters / 1000.0,
                duration_s=step_duration_seconds,
                instruction=instruction_text,
                name=step_name,
                geometry=step_geometry # Include step geometry
            ))
    
    # Get the overall route geometry from overview_polyline for the entire route
    overview_polyline_points = route.get('overview_polyline', {}).get('points')
    if overview_polyline_points:
        try:
            decoded_overall_coords = polyline.decode(overview_polyline_points)
            all_route_geometry = [Coordinate(lat=lat, lon=lon) for lat, lon in decoded_overall_coords]
        except Exception as e:
            print(f"Error decoding overview polyline: {e}")
            traceback.print_exc()

    return RouteDetails(
        total_distance_km=total_distance_meters / 1000.0,
        total_duration_s=total_duration_seconds,
        route_segments=route_segments,
        route_geometry=all_route_geometry
    )

# Helper function to strip HTML tags (Google Directions instructions can be HTML)
def strip_html_tags(text: str) -> str:
    """Strips HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()