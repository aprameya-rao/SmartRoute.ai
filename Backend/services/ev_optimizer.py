import math
import asyncio
from typing import List, Tuple, Dict, Any, Optional

from api.v1.models.route_response import Coordinate, RouteResponse, RouteStep, ChargingStation, RouteRequest, RouteSummary, RouteSegment
from services.routing import get_detailed_route_from_graphhopper, parse_graphhopper_response
from services.charging_stations import find_charging_stations
from services.geocoding import get_coordinates

MIN_CHARGE_AT_DESTINATION_PERCENT = 20
CHARGE_THRESHOLD_PERCENT = 15 # Consider charging if SOC drops below this
TARGET_CHARGE_PERCENT_AT_STOP = 80 # Target SOC after a charging stop
MIN_CHARGER_POWER_KW_FAST = 50
MIN_CHARGER_POWER_KW_ANY = 22

# MANUAL DATABASE: EV_MODELS
EV_MODELS = {
    "tata nexon ev": {
        "battery_capacity_kwh": 30.2,
        "consumption_wh_km": 156,
        "usable_soc_min": 10,
        "usable_soc_max": 90,
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 25},
            {"soc_percent": 80, "power_kw": 15},
            {"soc_percent": 90, "power_kw": 8},
        ]
    },
    "tesla model 3 long range": {
        "battery_capacity_kwh": 75.0,
        "consumption_wh_km": 150,
        "usable_soc_min": 10,
        "usable_soc_max": 90,
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 250},
            {"soc_percent": 50, "power_kw": 150},
            {"soc_percent": 80, "power_kw": 50},
            {"soc_percent": 90, "power_kw": 20},
        ]
    },
    "hyundai kona electric": {
        "battery_capacity_kwh": 39.2,
        "consumption_wh_km": 140, # Example consumption
        "usable_soc_min": 10,
        "usable_soc_max": 90,
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 50},
            {"soc_percent": 80, "power_kw": 25},
            {"soc_percent": 90, "power_kw": 10},
        ]
    },
    "mg zs ev": {
        "battery_capacity_kwh": 50.3,
        "consumption_wh_km": 160, # Example consumption
        "usable_soc_min": 10,
        "usable_soc_max": 90,
        "charging_profile_kw": [
            {"soc_percent": 0, "power_kw": 80},
            {"soc_percent": 80, "power_kw": 30},
            {"soc_percent": 90, "power_kw": 15},
        ]
    }
}


class UnfeasibleRouteError(Exception):
    """Custom exception raised when a route cannot be planned due to insufficient charging options."""
    pass

def get_charging_power_for_soc(ev_type_data: Dict[str, Any], current_soc_percent: float) -> float:
    """
    Determines the charging power (kW) an EV can receive at a given State of Charge (SoC).
    """
    profile = ev_type_data["charging_profile_kw"]
    # Sort the profile to ensure ascending order by soc_percent
    profile.sort(key=lambda x: x["soc_percent"])

    # If current_soc_percent is below the first defined point, use the first power
    if current_soc_percent < profile[0]["soc_percent"]:
        return profile[0]["power_kw"]
    
    for i in range(len(profile) - 1):
        if current_soc_percent >= profile[i]["soc_percent"] and current_soc_percent < profile[i+1]["soc_percent"]:
            # Linear interpolation or just take the lower bound power
            # For simplicity, taking the power at the lower bound of the interval
            return profile[i]["power_kw"]
    
    if current_soc_percent >= profile[-1]["soc_percent"]:
        return profile[-1]["power_kw"]
    
    return 0.0 # Should not happen if profile is well-defined

def calculate_consumption_wh_km_from_range(battery_capacity_kwh: float, range_km: float) -> float:
    """
    Calculates the energy consumption rate (Wh/km) of an EV based on its battery capacity and estimated range.
    """
    if range_km <= 0:
        # Default to a reasonable value if range_km is invalid, to prevent division by zero
        return 150 # Wh/km as a default, adjust if needed
    return (battery_capacity_kwh * 1000) / range_km


async def plan_ev_route(request: RouteRequest) -> RouteResponse:
    """
    Plans an optimized EV route, including identifying necessary charging stops.
    The core algorithm is modified to handle multi-leg journeys by simulating segments
    within the car's drivable range.
    """                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    ev_key = request.ev_type.lower().strip()
    ev_info = EV_MODELS.get(ev_key)
    if not ev_info:
        raise ValueError(f"EV type '{request.ev_type}' not found in database. Cannot determine battery capacity or charging profile.")

    battery_capacity_kwh = ev_info["battery_capacity_kwh"]
    consumption_wh_km = calculate_consumption_wh_km_from_range(battery_capacity_kwh, request.range_full_charge)
    
    usable_soc_min = ev_info["usable_soc_min"]
    usable_soc_max = ev_info["usable_soc_max"]
    
    # Ensure thresholds respect usable battery range
    charge_threshold_for_ev = max(CHARGE_THRESHOLD_PERCENT, usable_soc_min)
    target_charge_for_ev = min(TARGET_CHARGE_PERCENT_AT_STOP, usable_soc_max)
    min_charge_at_destination_for_ev = max(MIN_CHARGE_AT_DESTINATION_PERCENT, usable_soc_min)
    
    charging_preference = getattr(request, 'charging_preference', 'standard').lower()
    min_charger_power = MIN_CHARGER_POWER_KW_FAST if charging_preference == 'fast' else MIN_CHARGER_POWER_KW_ANY

    # Geocode start and end locations
    start_coord = await get_coordinates(request.start_location)
    end_coord = await get_coordinates(request.end_location)

    if not start_coord:
        raise ValueError(f"Could not geocode start location: {request.start_location}")
    if not end_coord:
        raise ValueError(f"Could not geocode end location: {request.end_location}")

    # Initialize simulation variables
    current_sim_coord = start_coord
    current_soc_percent = float(request.current_charge_percent)
    
    total_optimized_distance_km = 0.0
    total_optimized_duration_s = 0.0 # Total driving and charging duration in seconds
    total_charging_duration_minutes = 0.0
    total_energy_consumed_kwh = 0.0 # Tracks net energy consumed (driving - charging)

    all_route_geometry: List[Coordinate] = []
    all_route_segments_parsed: List[RouteStep] = []
    charging_locations: List[ChargingStation] = []
    
    # Loop to simulate journey and add charging stops
    max_iterations =50# Safety break for infinite loops, increased for longer trips
    current_iteration = 0

    while current_sim_coord != end_coord and current_iteration < max_iterations:
        current_iteration += 1
        
        # Calculate maximum drivable distance for the current SOC before hitting CHARGE_THRESHOLD_PERCENT
        # or going below usable_soc_min
        available_soc_for_driving = current_soc_percent - charge_threshold_for_ev
        if available_soc_for_driving <= 0:
            # If current SOC is already at or below threshold, we NEED to charge ASAP
            # Set drivable_range_km to a small value to force a charger search
            drivable_range_km = 1.0 # Minimal range to initiate search
            print(f"DEBUG: SOC {current_soc_percent:.1f}% <= Threshold {charge_threshold_for_ev}%. Forcing immediate charge search.")
        else:
            kwh_available_for_driving = (available_soc_for_driving / 100.0) * battery_capacity_kwh
            drivable_range_km = (kwh_available_for_driving * 1000.0) / consumption_wh_km
            print(f"DEBUG: Current SOC: {current_soc_percent:.1f}%. Drivable range to threshold ({charge_threshold_for_ev}%): {drivable_range_km:.2f} km.")

        # 1. Get route to the final destination to check total distance and determine next segment
        gh_response_to_final_dest = await get_detailed_route_from_graphhopper(current_sim_coord, end_coord)
        route_to_final_dest_parsed = parse_graphhopper_response(gh_response_to_final_dest)

        # CHANGE: Access properties using dot notation
        if not route_to_final_dest_parsed or not route_to_final_dest_parsed.route_geometry:
            raise RuntimeError(f"Could not retrieve route from {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f} to final destination.")

        # CHANGE: Access properties using dot notation
        distance_remaining_to_final_dest = route_to_final_dest_parsed.total_distance_km
        
        # Calculate energy needed to reach destination from current point with buffer
        kwh_needed_to_destination = (distance_remaining_to_final_dest * consumption_wh_km) / 1000.0
        soc_needed_to_destination = (kwh_needed_to_destination / battery_capacity_kwh) * 100.0
        
        can_reach_final_destination_with_buffer = (current_soc_percent - soc_needed_to_destination) >= min_charge_at_destination_for_ev

        # Decide whether to find a charger or drive directly to destination
        if not can_reach_final_destination_with_buffer:
            print(f"DEBUG: Cannot reach final destination with required SOC. Current SOC {current_soc_percent:.1f}%, needed {soc_needed_to_destination:.1f}% to arrive at {min_charge_at_destination_for_ev}%. Looking for charging station.")
            
            # Search for chargers *ahead* within drivable range + a small buffer
            # This search needs to be more intelligent, potentially along the route segment.
            # For simplicity, we'll search near the current location, but a more advanced
            # algorithm would find chargers along the projected path.
            # Let's use a slightly larger search radius here, but not too far.
            search_radius_km = max(25, min(drivable_range_km + 50, 100)) # Search up to 100km or drivable_range + 50km
            
            # To simulate searching along the route, we can take a point partway along the route to destination
            # This is a simplification; ideally, you'd iterate along the route geometry.
            # For now, let's just search from the current_sim_coord.
            
            nearby_chargers = await find_charging_stations(
                latitude=current_sim_coord.lat,
                longitude=current_sim_coord.lon,
                distance_km=search_radius_km, # Search further for a charger
                max_results=20, # Get more results to find a suitable one
                min_power_kw=min_charger_power
            )
            
            # Filter chargers that are actually "on the way" or at least not too far off
            # This is a critical point: how do you pick the *best* charger?
            # For simplicity, we'll take the closest one that meets power requirements and is somewhat forward.
            
            suitable_charger: Optional[ChargingStation] = None
            if nearby_chargers:
                # Sort by distance (closest first)
                nearby_chargers.sort(key=lambda x: x.distance_km if x.distance_km is not None else float('inf'))
                
                for charger in nearby_chargers:
                    if charger.power_kw and charger.power_kw >= min_charger_power:
                        # Before selecting, quickly check if we can even reach *this charger*
                        # This avoids selecting a charger that's beyond the current effective range
                        temp_gh_response = await get_detailed_route_from_graphhopper(current_sim_coord, charger.coordinates)
                        temp_route_parsed = parse_graphhopper_response(temp_gh_response)
                        
                        # CHANGE: Access properties using dot notation
                        if temp_route_parsed and temp_route_parsed.total_distance_km < (drivable_range_km + 10): # Add a small buffer for driving to charger
                            suitable_charger = charger
                            break
                        else:
                            # CHANGE: Access properties using dot notation
                            print(f"DEBUG: Charger {charger.title} at {charger.coordinates.lat:.4f},{charger.coordinates.lon:.4f} is too far ({temp_route_parsed.total_distance_km:.2f} km) to reach with current SOC, skipping.")
            
            if not suitable_charger:
                raise UnfeasibleRouteError(
                    f"No suitable charging station found near {current_sim_coord.lat:.4f}, "
                    f"{current_sim_coord.lon:.4f} with min power {min_charger_power}kW "
                    f"within {search_radius_km}km. Current SOC: {current_soc_percent:.1f}%. Route cannot be completed."
                )
            
            # Set the next segment's end to the chosen charger
            segment_end_coord = suitable_charger.coordinates
            print(f"DEBUG: Found suitable charger: {suitable_charger.title} at {suitable_charger.coordinates.lat:.4f}, {suitable_charger.coordinates.lon:.4f}. Planning segment to charger.")
            
        else:
            # Can reach final destination with current SOC
            print(f"DEBUG: Can reach final destination ({distance_remaining_to_final_dest:.2f} km) with sufficient SOC. Planning final segment.")
            segment_end_coord = end_coord


        # 2. Route the *current segment* (either to charger or to final destination)
        gh_response_segment = await get_detailed_route_from_graphhopper(current_sim_coord, segment_end_coord)
        segment_parsed = parse_graphhopper_response(gh_response_segment)

        # CHANGE: Access properties using dot notation
        if not segment_parsed or not segment_parsed.route_geometry:
            raise RuntimeError(f"Could not retrieve route segment from {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f} to {segment_end_coord.lat:.4f},{segment_end_coord.lon:.4f}.")

        # CHANGE: Access properties using dot notation
        drive_distance_km = segment_parsed.total_distance_km
        # CHANGE: Access properties using dot notation
        drive_duration_s = segment_parsed.total_duration_s
        energy_consumed_drive_kwh = (drive_distance_km * consumption_wh_km) / 1000.0

        # Simulate driving this segment
        soc_before_driving = current_soc_percent
        current_soc_percent -= (energy_consumed_drive_kwh / battery_capacity_kwh) * 100.0
        total_energy_consumed_kwh += energy_consumed_drive_kwh

        # Add this driving segment to overall route
        # CHANGE: Access properties using dot notation
        if all_route_geometry and segment_parsed.route_geometry and all_route_geometry[-1] == segment_parsed.route_geometry[0]:
            all_route_geometry.extend(segment_parsed.route_geometry[1:])
        else:
            all_route_geometry.extend(segment_parsed.route_geometry)
        # CHANGE: Access properties using dot notation
        all_route_segments_parsed.extend(segment_parsed.route_segments)
        
        total_optimized_distance_km += drive_distance_km
        total_optimized_duration_s += drive_duration_s

        current_sim_coord = segment_end_coord # Update current location to end of segment
        print(f"DEBUG: Drove {drive_distance_km:.2f} km. SOC: {soc_before_driving:.1f}% -> {current_soc_percent:.1f}%. New position: {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f}")

        # --- Handle Charging if arrived at a Charging Station ---
        if current_sim_coord != end_coord and suitable_charger and current_sim_coord == suitable_charger.coordinates:
            print(f"DEBUG: Arrived at charging station {suitable_charger.title}.")
            # Simulate charging at the station
            target_soc_kwh = (target_charge_for_ev / 100.0) * battery_capacity_kwh
            current_soc_kwh = (current_soc_percent / 100.0) * battery_capacity_kwh
            charge_needed_kwh = target_soc_kwh - current_soc_kwh

            if charge_needed_kwh < 0.5: # Don't charge if almost full or negligible amount
                charge_needed_kwh = 0.0 # Set to 0 if negligible
                print(f"DEBUG: Negligible charge needed ({charge_needed_kwh:.2f} kWh). Skipping charge at {suitable_charger.title}.")

            if charge_needed_kwh > 0:
                ev_max_power = get_charging_power_for_soc(ev_info, current_soc_percent)
                effective_charger_power = suitable_charger.power_kw if suitable_charger.power_kw else 0.0
                effective_charging_rate_kw = min(ev_max_power, effective_charger_power)

                if effective_charging_rate_kw <= 0: # Ensure positive power
                    raise UnfeasibleRouteError(f"Effective charging power at {suitable_charger.title} is 0kW or less. Cannot charge.")
                
                charge_time_hours = charge_needed_kwh / effective_charging_rate_kw
                charge_time_minutes = round(charge_time_hours * 60)
                
                # Update SOC after charging
                current_soc_before_charge = current_soc_percent
                current_soc_percent = (target_soc_kwh / battery_capacity_kwh) * 100.0
                current_soc_percent = min(current_soc_percent, usable_soc_max) # Don't exceed max usable SOC

                total_charging_duration_minutes += charge_time_minutes
                total_energy_consumed_kwh -= charge_needed_kwh # Energy is added back to battery

                # Add charging segment (no distance, just duration)
                charging_segment_step = RouteStep(
                    distance_km=0.0,
                    duration_s=float(charge_time_minutes * 60), # Convert minutes to seconds
                    geometry=[current_sim_coord, current_sim_coord], # No movement
                    instruction=f"Charge at {suitable_charger.title} for {charge_time_minutes} minutes."
                )
                all_route_segments_parsed.append(charging_segment_step)

                suitable_charger.recommended_charge_minutes = charge_time_minutes
                suitable_charger.estimated_charge_added_kwh = charge_needed_kwh
                charging_locations.append(suitable_charger)
                print(f"DEBUG: Charged at {suitable_charger.title} for {charge_time_minutes} min. SOC: {current_soc_before_charge:.1f}% -> {current_soc_percent:.1f}%.")
            else:
                print(f"DEBUG: No significant charge needed at {suitable_charger.title}. Proceeding.")
            
            # Reset suitable_charger so it doesn't try to charge at the same place repeatedly if not needed
            suitable_charger = None
            
        # The loop will re-evaluate conditions for the next segment from the new current_sim_coord.

    # Final checks
    if current_sim_coord != end_coord:
        raise UnfeasibleRouteError("Could not reach destination within maximum iterations. Route might be too long or unfeasible with given parameters.")

    if current_soc_percent < min_charge_at_destination_for_ev:
        print(f"WARNING: Arrived at destination with {current_soc_percent:.1f}% SOC, which is below desired minimum {min_charge_at_destination_for_ev}%.")

    final_charge_percent = max(0, min(100, int(current_soc_percent)))
    total_duration_minutes = (total_optimized_duration_s / 60.0) + total_charging_duration_minutes
    total_driving_minutes = total_optimized_duration_s / 60.0

    summary = RouteSummary(
        total_distance_km=total_optimized_distance_km,
        total_duration_minutes=total_duration_minutes,
        total_driving_minutes=total_driving_minutes,
        total_charging_minutes=total_charging_duration_minutes,
        estimated_charging_stops=len(charging_locations),
        total_energy_consumption_kwh=total_energy_consumed_kwh,
        final_charge_percent=final_charge_percent
    )

    return RouteResponse(
        message="Route planned successfully with charging locations",
        summary=summary,
        route_segments=all_route_segments_parsed,
        route_geometry=all_route_geometry,
        charging_locations=charging_locations
    )

optimize_ev_route = plan_ev_route