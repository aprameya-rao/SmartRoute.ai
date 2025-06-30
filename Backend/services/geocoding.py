# Backend/services/geocoding.py
import httpx
from core.config import settings
from api.v1.models.route_response import Coordinate
from typing import Optional, Dict, Any
import traceback # Import for detailed error logging

async def get_coordinates(address: str) -> Optional[Coordinate]:
    """
    Geocodes an address string to geographical coordinates using Google Geocoding API.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": settings.Maps_API_KEY, # Use the new Google API key
    }

    async with httpx.AsyncClient() as client:
        try:
            #print(f"DEBUG: Google Geocoding Request URL: {url}")
            #print(f"DEBUG: Google Geocoding Request Params: {params}")
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            data = response.json()
            #print(f"DEBUG: Raw Google Geocoding Response: {data}")

            if data and data.get('results'):
                # Google Geocoding API response structure: results[0]['geometry']['location']['lat'], results[0]['geometry']['location']['lng']
                location = data['results'][0]['geometry']['location']
                lat = location.get('lat')
                lon = location.get('lng') # Google uses 'lng' for longitude

                if lat is not None and lon is not None:
                    return Coordinate(lat=lat, lon=lon)
                else:
                    print(f"Google Geocoding: Latitude or longitude missing in response for {address}.")
                    return None
            elif data and data.get('status') == 'ZERO_RESULTS':
                print(f"Google Geocoding: No results found for address: {address}")
                return None
            else:
                print(f"Google Geocoding: Unexpected response status for {address}: {data.get('status', 'No status')}. Message: {data.get('error_message', 'No error message')}")
                return None

        except httpx.RequestError as e:
            print(f"Google Geocoding request error: An error occurred while requesting {e.request.url!r}. Details: {e}")
            traceback.print_exc()
            return None
        except httpx.HTTPStatusError as e:
            print(f"Google Geocoding HTTP error: {e.response.status_code} - {e.response.text}")
            print(f"Response content: {e.response.text}") # Print the response content for more detail on HTTP errors
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"Unexpected error in Google geocoding for {address}: {e}")
            traceback.print_exc() # Print full traceback for unexpected errors
            return None