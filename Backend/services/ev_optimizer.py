# ev-route-optimizer-backend/services/ev_optimizer.py
import math
from typing import List, Dict, Any, Optional, Tuple
from geopy.distance import geodesic # For accurate distance calculation between two lat/lon points

from api.v1.models.route_request import RouteRequest
from api.v1.models.route_response import Coordinate, RouteSegment, ChargingStation, RouteSummary, RouteResponse
from services.geocoding import get_coordinates
from services.routing import get_detailed_route_from_ors, parse_ors_geometry_to_coords
from services.charging_stations import find_charging_stations

# --- Simplified EV Data (In a real application, this would come from a database) ---
EV_MODELS = {
    "Tesla Model 3 Long Range": {
        "battery_capacity_kwh": 75.0, # Total usable battery capacity
        "consumption_wh_km": 150,     # Average Watt-hours per kilometer
        "usable_soc_min": 10,         # Minimum SoC to never drop below (buffer)
        "usable_soc_max": 90,         # Max SoC to charge to (avoiding very slow top 10%)
        # Simplified charging power profile (kW) based on SoC.
        # Real-world charging curves are more complex.
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 250},   # 0-50% charge at 250 kW
            {"soc_percent": 50, "power_kw": 150},  # 50-80% charge at 150 kW
            {"soc_percent": 80, "power_kw": 50},   # 80-90% charge at 50 kW
            {"soc_percent": 90, "power_kw": 20},   # Above 90% is very slow
        ]
    },
    "Nissan Leaf S": {
        "battery_capacity_kwh": 40.0,
        "consumption_wh_km": 180,
        "usable_soc_min": 10,
        "usable_soc_max": 90,
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 50},
            {"soc_percent": 80, "power_kw": 20},
            {"soc_percent": 90, "power_kw": 10},
        ]
    }
}

# --- Configuration for Optimization Strategy ---
# How often to simulate SoC check along the route polyline (smaller = more granular, slower)
ROUTE_SIMULATION_SEGMENT_LENGTH_KM = 0.5 # Check SoC every 500 meters

# Minimum SoC percentage required upon arrival at the final destination
MIN_CHARGE_AT_DESTINATION_PERCENT = 20

# If SoC drops below this percentage during driving, look for a charger
CHARGE_THRESHOLD_PERCENT = 15

# Target SoC percentage to charge to at a charging stop (avoids overcharging/slow top-up)
TARGET_CHARGE_PERCENT_AT_STOP = 80

# Minimum power of a charger to consider for a stop (kW)
MIN_CHARGER_POWER_KW = 50 

def get_charging_power_for_soc(ev_type_data: Dict[str, Any], current_soc_percent: float) -> float:
    """
    Estimates the EV's maximum charging power based on its SoC and predefined charging profile.
    This simulates the tapering effect where charging slows down as battery fills.
    """
    profile = ev_type_data["charging_profile_kw"]
    # Find the appropriate power segment in the profile
    for i in range(len(profile) - 1):
        if current_soc_percent >= profile[i]["soc_percent"] and current_soc_percent < profile[i+1]["soc_percent"]:
            return profile[i]["power_kw"]

    # If we are at or above the last defined SoC point
    if current_soc_percent >= profile[-1]["soc_percent"]:
        return profile[-1]["power_kw"]

    return 0.0 # Should not happen if profile covers 0-100 adequately

async def optimize_ev_route(request: RouteRequest) -> RouteResponse:
    """
    Main function to optimize the EV route, calculate battery consumption,
    and insert necessary charging stops.
    """
    # 0. Retrieve EV Model Data
    ev_info = EV_MODELS.get(request.ev_type)
    if not ev_info:
        raise ValueError(f"EV type '{request.ev_type}' not found in backend EV models.")

    battery_capacity_kwh = ev_info["battery_capacity_kwh"]
    consumption_wh_km = ev_info["consumption_wh_km"]
    usable_soc_min = ev_info["usable_soc_min"]
    usable_soc_max = ev_info["usable_soc_max"]

    # Adjust thresholds based on usable range
    charge_threshold_for_ev = max(CHARGE_THRESHOLD_PERCENT, usable_soc_min)
    target_charge_for_ev = min(TARGET_CHARGE_PERCENT_AT_STOP, usable_soc_max)
    min_charge_at_destination_for_ev = max(MIN_CHARGE_AT_DESTINATION_PERCENT, usable_soc_min)

    # 1. Geocode Start and End Locations
    start_coord = await get_coordinates(request.start_location)
    end_coord = await get_coordinates(request.end_location)

    if not start_coord:
        raise ValueError(f"Could not geocode start location: {request.start_location}")
    if not end_coord:
        raise ValueError(f"Could not geocode end location: {request.end_location}")

    # 2. Get Detailed Route from ORS
    # We request a route between start and end. Waypoints are not integrated into this single ORS call
    # for simplicity of SoC simulation, but could be added for more complex multi-leg routing.
    ors_raw_route = await get_detailed_route_from_ors(start_coord, end_coord)
    if not ors_raw_route or not ors_raw_route.get('routes'):
        raise RuntimeError("Could not retrieve detailed route from OpenRouteService. Check API key or route validity.")

    ors_route_data = ors_raw_route['routes'][0]
    full_route_geometry = parse_ors_geometry_to_coords(ors_route_data['geometry']['coordinates'])

    # --- Route Simulation and Charging Stop Insertion Logic ---
    current_soc_percent = float(request.current_charge_percent)
    total_route_segments: List[RouteSegment] = [] # Final list of segments (driving + charging)
    total_driving_duration_minutes = 0.0
    total_charging_duration_minutes = 0.0
    total_distance_covered_km = 0.0
    total_energy_consumed_kwh = 0.0 # Net consumption (driving energy - charged energy)
    charging_stops_count = 0

    # Current point in the route simulation. Starts at the true start_coord.
    current_sim_coord = start_coord

    # Iterate through the ORS polyline to simulate the trip in small segments
    # This allows for continuous SoC tracking and dynamic charging decisions.
    for i in range(len(full_route_geometry) - 1):
        next_point_on_polyline = full_route_geometry[i+1]

        # Calculate distance for this very small polyline segment
        segment_distance_km = geodesic(
            (current_sim_coord.lat, current_sim_coord.lon),
            (next_point_on_polyline.lat, next_point_on_polyline.lon)
        ).km

        if segment_distance_km < 0.01: # Skip very tiny or zero-length segments
            current_sim_coord = next_point_on_polyline
            continue 

        # Estimate duration for this small segment (very rough: assume average speed ~60km/h)
        # ORS usually provides step-by-step durations, but for micro-segments, a simple speed assumption is common.
        segment_duration_minutes = (segment_distance_km / 60.0) * 60.0 # Distance / speed (km/min)

        # Calculate energy consumption for this small segment
        energy_consumed_kwh_this_segment = (segment_distance_km * consumption_wh_km) / 1000.0

        # Record SoC *before* consumption for this segment
        soc_before_segment = current_soc_percent

        # Update SoC after consumption
        current_soc_percent -= (energy_consumed_kwh_this_segment / battery_capacity_kwh) * 100.0
        total_energy_consumed_kwh += energy_consumed_kwh_this_segment

        # Add to total driving duration and distance
        total_driving_duration_minutes += segment_duration_minutes
        total_distance_covered_km += segment_distance_km

        # Create a driving segment for the response
        driving_segment_for_response = RouteSegment(
            type="driving",
            start_coord=current_sim_coord,
            end_coord=next_point_on_polyline,
            distance_km=segment_distance_km,
            duration_minutes=segment_duration_minutes,
            start_soc_percent=soc_before_segment,
            end_soc_percent=current_soc_percent,
            energy_consumption_kwh=energy_consumed_kwh_this_segment
        )
        total_route_segments.append(driving_segment_for_response)

        current_sim_coord = next_point_on_polyline # Move to the end of the current micro-segment

        # --- Charging Decision Logic ---
        # Check if charging is needed:
        # 1. If current SoC drops below the safe threshold, OR
        # 2. If it's near the end of the journey and SoC will be insufficient to reach the destination
        is_last_point_on_polyline = (i == len(full_route_geometry) - 2) 

        # Calculate estimated remaining distance from current point to destination
        # This is a simplification; a more accurate model would use ORS for remaining segments.
        # For this example, we assume the rest of the polyline is the remaining route.
        remaining_distance_to_end_polyline_km = 0.0
        for j in range(i + 1, len(full_route_geometry) - 1):
             remaining_distance_to_end_polyline_km += geodesic(
                (full_route_geometry[j].lat, full_route_geometry[j].lon),
                (full_route_geometry[j+1].lat, full_route_geometry[j+1].lon)
            ).km

        # Calculate required SoC to reach destination (assuming linear consumption)
        kwh_needed_to_destination = (remaining_distance_to_end_polyline_km * consumption_wh_km) / 1000.0
        soc_needed_to_destination = (kwh_needed_to_destination / battery_capacity_kwh) * 100.0

        charge_needed = False
        if current_soc_percent <= charge_threshold_for_ev:
            # print(f"DEBUG: SoC ({current_soc_percent:.1f}%) <= threshold ({charge_threshold_for_ev:.1f}%)")
            charge_needed = True
        elif is_last_point_on_polyline and current_soc_percent < min_charge_at_destination_for_ev:
            # print(f"DEBUG: Last point and SoC ({current_soc_percent:.1f}%) < min arrival ({min_charge_at_destination_for_ev:.1f}%)")
            charge_needed = True
        elif current_soc_percent - soc_needed_to_destination < min_charge_at_destination_for_ev:
            # print(f"DEBUG: Not enough range (SoC {current_soc_percent:.1f}%) to arrive with {min_charge_at_destination_for_ev:.1f}%")
            charge_needed = True

        if charge_needed:
            # Find charging stations near the current location
            print(f"SoC low ({current_soc_percent:.1f}%) at {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f}. Searching for chargers...")
            nearby_chargers = await find_charging_stations(
                latitude=current_sim_coord.lat,
                longitude=current_sim_coord.lon,
                distance_km=15, # Search within 15 km radius
                max_results=5,
                min_power_kw=MIN_CHARGER_POWER_KW # Only consider faster chargers
            )

            suitable_charger: Optional[ChargingStation] = None
            # Prioritize faster chargers
            nearby_chargers.sort(key=lambda x: x.power_kw if x.power_kw else 0, reverse=True)

            for charger in nearby_chargers:
                # You could add more sophisticated selection logic here (e.g., connector type, network)
                if charger.power_kw and charger.power_kw >= MIN_CHARGER_POWER_KW: 
                    suitable_charger = charger
                    break

            if suitable_charger:
                print(f"Found suitable charger: {suitable_charger.name} ({suitable_charger.power_kw}kW)")
                charging_stops_count += 1

                # Calculate charge amount needed
                # Charge up to TARGET_CHARGE_PERCENT_AT_STOP (or usable_soc_max if lower)
                target_soc_kwh = (target_charge_for_ev / 100.0) * battery_capacity_kwh
                current_soc_kwh = (current_soc_percent / 100.0) * battery_capacity_kwh

                charge_needed_kwh = target_soc_kwh - current_soc_kwh

                if charge_needed_kwh < 0.1: # Already sufficiently charged
                    print("Already sufficiently charged at this point, skipping stop.")
                    continue

                # Calculate charging time based on EV's charging profile and station's power
                # The EV's charging power (tapering) is often the limiting factor at higher SoCs
                # The station's power is the limiting factor if EV can charge faster than station supplies
                ev_max_power_at_current_soc = get_charging_power_for_soc(ev_info, current_soc_percent)
                effective_charging_power_kw = min(ev_max_power_at_current_soc, suitable_charger.power_kw or 0.0)

                if effective_charging_power_kw <= 0:
                    print(f"Warning: No effective charging power for {suitable_charger.name}. Skipping stop.")
                    continue

                estimated_charge_time_hours = charge_needed_kwh / effective_charging_power_kw
                estimated_charge_time_minutes = round(estimated_charge_time_hours * 60)

                # Update SoC after charging
                current_soc_before_charge_stop = current_soc_percent
                current_soc_percent = (target_soc_kwh / battery_capacity_kwh) * 100.0
                total_charging_duration_minutes += estimated_charge_time_minutes
                total_energy_consumed_kwh -= charge_needed_kwh # Charging adds energy back, so it's a "negative consumption"

                # Add charging stop segment to the route
                charging_stop_segment = RouteSegment(
                    type="charging_stop",
                    start_coord=current_sim_coord,
                    end_coord=current_sim_coord, # End at same location as it's a stop
                    distance_km=0.0,
                    duration_minutes=float(estimated_charge_time_minutes),
                    station_id=suitable_charger.id,
                    station_name=suitable_charger.name,
                    charge_added_kwh=charge_needed_kwh,
                    charge_added_percent=(charge_needed_kwh / battery_capacity_kwh) * 100.0,
                    start_soc_percent=current_soc_before_charge_stop, # SoC before charging
                    end_soc_percent=current_soc_percent # SoC after charging
                )
                total_route_segments.append(charging_stop_segment)

                # Update the suitable_charger object with recommended time/added for response
                suitable_charger.recommended_charge_minutes = estimated_charge_time_minutes
                suitable_charger.estimated_charge_added_kwh = charge_needed_kwh
            else:
                print(f"No suitable charger found near {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f}. Continuing with low SoC!")
                # In a real app, you might stop here, raise an error, or issue a strong warning to the user.

    # --- Final Summary Calculation ---
    # Ensure final SoC is within bounds [0, 100]
    final_charge_percent = max(0, min(100, int(current_soc_percent))) 

    # Calculate total duration including driving and charging
    total_duration_minutes = total_driving_duration_minutes + total_charging_duration_minutes

    summary = RouteSummary(
        total_distance_km=total_distance_covered_km,
        total_duration_minutes=total_duration_minutes,
        total_driving_minutes=total_driving_duration_minutes,
        total_charging_minutes=total_charging_duration_minutes,
        estimated_charging_stops=charging_stops_count,
        total_energy_consumption_kwh=total_energy_consumed_kwh,
        final_charge_percent=final_charge_percent
    )

    return RouteResponse(
        message="Route optimized successfully with charging stops",
        summary=summary,
        route_segments=total_route_segments,
        route_geometry=full_route_geometry
    )