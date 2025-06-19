# ev-route-optimizer-backend/services/charging_stations.py
import httpx
from core.config import settings
from api.v1.models.route_response import Coordinate, ChargingStation
from typing import List, Optional, Dict, Any

async def find_charging_stations(
    latitude: float,
    longitude: float,
    distance_km: int = 50, # Search radius
    max_results: int = 10,  # Max number of stations to return
    min_power_kw: Optional[float] = None # Filter by minimum power
) -> List[ChargingStation]:
    """
    Finds charging stations near a given coordinate using Open Charge Map API.
    """
    url = "https://api.openchargemap.io/v3/poi"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance_km,
        "distanceunit": "KM",
        "maxresults": max_results,
        "compact": True, # Get a more compact response
        "key": settings.OPEN_CHARGE_MAP_API_KEY # If you have an OCM API Key, UNCOMMENT this line
                                                # and ensure the key is in your .env file.
                                                # Otherwise, keep it commented out.
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()

            stations = []
            for poi in data:
                station_id = str(poi.get('ID'))
                title = poi.get('AddressInfo', {}).get('Title', 'Unknown Station')
                address_info = poi.get('AddressInfo', {})
                address_str = f"{address_info.get('AddressLine1', '')}, {address_info.get('Town', '')}, {address_info.get('StateOrProvince', '')} {address_info.get('Postcode', '')}, {address_info.get('Country', {}).get('Title', '')}".strip(', ')

                coords = Coordinate(
                    lat=address_info.get('Latitude'),
                    lon=address_info.get('Longitude')
                )

                connections = []
                station_power_kw_overall = 0.0 # Track max power of connections at this station
                for conn in poi.get('Connections', []):
                    conn_power = conn.get('PowerKW')
                    if conn_power:
                        station_power_kw_overall = max(station_power_kw_overall, conn_power)

                    connections.append({
                        "connection_type_id": conn.get('ConnectionTypeID'),
                        "connection_type_title": conn.get('ConnectionType', {}).get('Title'),
                        "power_kw": conn_power,
                        "current_type": conn.get('CurrentType', {}).get('Title')
                    })

                # Filter by minimum power if specified
                if min_power_kw and station_power_kw_overall < min_power_kw:
                    continue # Skip this station if it doesn't meet min power requirement

                stations.append(ChargingStation(
                    id=station_id,
                    name=title,
                    address=address_str,
                    coordinates=coords,
                    connection_types=connections,
                    power_kw=station_power_kw_overall,
                    is_free=poi.get('UsageCost') == "Free"
                ))
            return stations
        except httpx.RequestError as e:
            print(f"OCM request error: An error occurred while requesting {e.request.url!r}.")
            print(f"{e.__class__.__name__}: {e}")
            return []
        except httpx.HTTPStatusError as e:
            print(f"OCM HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"Unexpected error in charging station lookup: {e}")
            return []