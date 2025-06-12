# ev-route-optimizer-backend/services/routing.py
import httpx
from core.config import settings
from api.v1.models.route_response import Coordinate
from typing import List, Dict, Any, Optional

async def get_detailed_route_from_ors(
    start_coord: Coordinate,
    end_coord: Coordinate,
    profile: str = "driving-car" # ORS supports 'driving-car', 'cycling-regular', 'foot-walking' etc.
) -> Optional[Dict[str, Any]]:
    """
    Calculates a detailed route from OpenRouteService (ORS), returning the raw response
    which includes geometry and detailed segments/steps.
    """
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    headers = {
        "Accept": "application/json",
        "Authorization": settings.ORS_API_KEY
    }
    body = {
        "coordinates": [
            [start_coord.lon, start_coord.lat],
            [end_coord.lon, end_coord.lat]
        ],
        "options": {
            # Request detailed segments, steps, and waypoints for finer control over route parsing
            "route_attributes": ["segments", "steps", "way_points"] 
        },
        "geometry_format": "geojson" # Request GeoJSON for easier parsing of polyline
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=body, timeout=20.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"ORS request error: An error occurred while requesting {e.request.url!r}.")
            print(f"{e.__class__.__name__}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"ORS HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error in ORS routing: {e}")
            return None

def parse_ors_geometry_to_coords(ors_geometry: List[List[float]]) -> List[Coordinate]:
    """
    Parses ORS geometry (list of [lon, lat] pairs) into a list of Coordinate objects.
    """
    return [Coordinate(lat=lat, lon=lon) for lon, lat in ors_geometry]