# Backend/services/charging_stations.py

import httpx
from core.config import settings # Assuming you have a core/config.py with settings
from api.v1.models.route_response import Coordinate, ChargingStation # Import the models used here
from typing import List, Optional, Dict, Any

async def find_charging_stations(
    latitude: float,
    longitude: float,
    distance_km: int = 50, # Search radius
    max_results: int = 10,  # Max number of stations to return
    min_power_kw: Optional[float] = None # Filter by minimum power
) -> List[ChargingStation]: # Type hint for the return value
    url = "https://api.openchargemap.io/v3/poi"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance_km,
        "distanceunit": "KM",
        "maxresults": max_results,
        "compact": True,
        "key": settings.OPEN_CHARGE_MAP_API_KEY # Using the API key from settings
    }
    async with httpx.AsyncClient() as client:
        try:
            #print(f"DEBUG: Making OCM request to {url} with params: {params}")
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            data = response.json()
            #print(f"DEBUG: Received OCM response. Number of POIs: {len(data)}")

            stations = []
            for i, poi in enumerate(data):
                if poi is None:
                    print(f"WARNING: POI at index {i} is None. Skipping.")
                    continue

                address_info = poi.get('AddressInfo')
                if address_info is None:
                    print(f"WARNING: POI {poi.get('ID', 'Unknown ID')} has no AddressInfo. Skipping.")
                    continue

                title = address_info.get('Title', 'Unknown Station')
                lat = address_info.get('Latitude')
                lon = address_info.get('Longitude')

                if lat is None or lon is None:
                    print(f"WARNING: POI {title} has missing Latitude/Longitude. Skipping.")
                    continue

                country_info = address_info.get('Country')
                country_title = country_info.get('Title', '') if country_info else ''

                address_str = f"{address_info.get('AddressLine1', '')}, {address_info.get('Town', '')}, {address_info.get('StateOrProvince', '')} {address_info.get('Postcode', '')}, {country_title}".strip(', ')

                coords = Coordinate(lat=lat, lon=lon)

                connections_list = [] # Renamed to avoid conflict with `connections` for filtering
                station_power_kw_overall = 0.0

                raw_connections = poi.get('Connections')
                if raw_connections is not None:
                    for j, conn in enumerate(raw_connections):
                        if conn is None:
                            print(f"WARNING: Connection at POI {title} index {j} is None. Skipping.")
                            continue

                        conn_power = conn.get('PowerKW')
                        if conn_power:
                            station_power_kw_overall = max(station_power_kw_overall, conn_power)

                        conn_type_info = conn.get('ConnectionType')
                        conn_type_title = conn_type_info.get('Title', '') if conn_type_info else ''

                        current_type_info = conn.get('CurrentType')
                        current_type_title = current_type_info.get('Title', '') if current_type_info else ''

                        connections_list.append({
                            "connection_type_id": conn.get('ConnectionTypeID'),
                            "connection_type_title": conn_type_title,
                            "power_kw": conn_power,
                            "current_type": current_type_title
                        })

                if min_power_kw and station_power_kw_overall < min_power_kw:
                    print(f"DEBUG: Skipping POI {title} due to insufficient power ({station_power_kw_overall} KW < {min_power_kw} KW).")
                    continue

                stations.append(ChargingStation(
                    id=str(poi.get('ID')),
                    name=title,
                    address=address_str,
                    coordinates=coords,
                    connection_types=connections_list, # Use connections_list
                    power_kw=station_power_kw_overall,
                    is_free=poi.get('UsageCost') == "Free" # Assuming 'UsageCost' indicates if it's free
                ))
            return stations
        except httpx.RequestError as e:
            print(f"OCM request error: An error occurred while requesting {e.request.url!r}.")
            print(f"{e.__class__.__name__}: {e}")
            raise e
        except httpx.HTTPStatusError as e:
            print(f"OCM HTTP error: {e.response.status_code} - {e.response.text}")
            raise e
        except Exception as e:
            print(f"UNEXPECTED ERROR DURING OCM DATA PROCESSING: {e}")
            import traceback
            traceback.print_exc()
            raise e