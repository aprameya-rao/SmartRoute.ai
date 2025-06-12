# ev-route-optimizer-backend/services/geocoding.py
import httpx
from core.config import settings
from api.v1.models.route_response import Coordinate
from typing import Optional

async def get_coordinates(address: str) -> Optional[Coordinate]:
    """
    Geocodes an address string to geographical coordinates using Geoapify API.
    """
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": address,
        "apiKey": settings.GEOAPIFY_API_KEY,
        "limit": 1
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()  # Raise HTTPStatusError for bad responses (4xx or 5xx)
            data = response.json()
            if data and data.get('features'):
                lon, lat = data['features'][0]['geometry']['coordinates']
                return Coordinate(lat=lat, lon=lon)
            return None
        except httpx.RequestError as e:
            print(f"Geoapify request error: An error occurred while requesting {e.request.url!r}.")
            print(f"{e.__class__.__name__}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Geoapify HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error in geocoding: {e}")
            return None