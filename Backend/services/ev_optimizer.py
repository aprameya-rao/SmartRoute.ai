import math
import asyncio
from typing import List, Tuple, Dict, Any, Optional

from api.v1.models.route_response import Coordinate, RouteResponse, RouteStep, ChargingStation, RouteRequest, RouteSummary, RouteSegment
from services.routing import get_detailed_route_from_graphhopper, parse_graphhopper_response
from services.charging_stations import find_charging_stations # Corrected import name
from services.geocoding import get_coordinates

MIN_CHARGE_AT_DESTINATION_PERCENT = 20
CHARGE_THRESHOLD_PERCENT = 15
TARGET_CHARGE_PERCENT_AT_STOP = 80
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
    for i in range(len(profile) - 1):
        if current_soc_percent >= profile[i]["soc_percent"] and current_soc_percent < profile[i+1]["soc_percent"]:
            return profile[i]["power_kw"]
    
    if current_soc_percent >= profile[-1]["soc_percent"]:
        return profile[-1]["power_kw"]
    
    return 0.0

def calculate_consumption_wh_km_from_range(battery_capacity_kwh: float, range_km: float) -> float:
    """
    Calculates the energy consumption rate (Wh/km) of an EV based on its battery capacity and estimated range.
    """
    if range_km <= 0:
        raise ValueError("Range on full charge must be a positive value.")
    return (battery_capacity_kwh * 1000) / range_km


async def plan_ev_route(request: RouteRequest) -> RouteResponse:
    """
    Plans an optimized EV route, including identifying necessary charging stops.
    """
    ev_key = request.ev_type.lower().strip()
    ev_info = EV_MODELS.get(ev_key)
    if not ev_info:
        raise ValueError(f"EV type '{request.ev_type}' not found in database. Cannot determine battery capacity or charging profile.")

    battery_capacity_kwh = ev_info["battery_capacity_kwh"]
    consumption_wh_km = calculate_consumption_wh_km_from_range(battery_capacity_kwh, request.range_full_charge)
    
    usable_soc_min = ev_info["usable_soc_min"]
    usable_soc_max = ev_info["usable_soc_max"]
    
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
    all_route_segments_parsed: List[RouteStep] = [] # Use RouteStep for consistency with API models
    charging_locations: List[ChargingStation] = []
    
    # Loop to simulate journey and add charging stops
    max_iterations = 10 # Safety break for infinite loops
    current_iteration = 0

    while current_sim_coord != end_coord and current_iteration < max_iterations:
        current_iteration += 1
        
        # 1. Get route for the current leg (from current_sim_coord to final destination)
        # This leg is used to evaluate if a charge is needed BEFORE driving it.
        gh_response_current_leg = await get_detailed_route_from_graphhopper(current_sim_coord, end_coord)
        current_leg_parsed = parse_graphhopper_response(gh_response_current_leg)

        if not current_leg_parsed or not current_leg_parsed.get('route_geometry'):
            raise RuntimeError(f"Could not retrieve route for leg from {current_sim_coord.lat:.4f},{current_sim_coord.lon:.4f} to destination.")

        distance_to_destination_this_leg = current_leg_parsed['total_distance_km']
        
        # Calculate energy needed to reach destination from current point with buffer
        kwh_needed_to_destination_buffered = (distance_to_destination_this_leg * consumption_wh_km) / 1000.0
        # Convert needed KWh to SOC percentage
        soc_needed_to_destination_buffered = (kwh_needed_to_destination_buffered / battery_capacity_kwh) * 100.0
        
        # Check if a charge is needed for this leg
        charge_needed = False
        if current_soc_percent <= charge_threshold_for_ev:
            charge_needed = True
            print(f"Charge needed: SOC {current_soc_percent:.1f}% <= Threshold {charge_threshold_for_ev}%.")
        elif (current_soc_percent - soc_needed_to_destination_buffered) < min_charge_at_destination_for_ev:
            charge_needed = True
            print(f"Charge needed: SOC {current_soc_percent:.1f}% - Needed {soc_needed_to_destination_buffered:.1f}% ({current_soc_percent - soc_needed_to_destination_buffered:.1f}%) < Min Dest {min_charge_at_destination_for_ev}%.")
        elif current_soc_percent < (soc_needed_to_destination_buffered + (battery_capacity_kwh * 0.1 / battery_capacity_kwh * 100)): # 10% buffer
            charge_needed = True
            print(f"Charge needed: SOC {current_soc_percent:.1f}% insufficient for destination with 10% buffer.")

        # --- Handle Charging Stop if Needed ---
        if charge_needed:
            print(f"Attempting to find charging station near {current_sim_coord.lat:.4f}, {current_sim_coord.lon:.4f}...")
            nearby_chargers = await find_charging_stations( # Corrected function call
                latitude=current_sim_coord.lat,
                longitude=current_sim_coord.lon,
                distance_km=25, # Search radius for chargers
                max_results=10,
                min_power_kw=min_charger_power
            )

            # Sort by distance and then by power (higher power preferred)
            nearby_chargers.sort(key=lambda x: (x.distance_km if x.distance_km is not None else float('inf'), -(x.power_kw if x.power_kw is not None else 0)))

            suitable_charger: Optional[ChargingStation] = None
            # Find the best suitable charger
            for charger in nearby_chargers:
                if charger.power_kw and charger.power_kw >= min_charger_power:
                    suitable_charger = charger
                    break
            
            if not suitable_charger:
                raise UnfeasibleRouteError(
                    f"No suitable charging station found near {current_sim_coord.lat:.4f}, "
                    f"{current_sim_coord.lon:.4f} with min power {min_charger_power}kW. "
                    f"Current SOC: {current_soc_percent:.1f}%. Route cannot be completed."
                )
            
            # --- Route to Charging Station ---
            print(f"Routing to charging station: {suitable_charger.title} at {suitable_charger.coordinates.lat:.4f}, {suitable_charger.coordinates.lon:.4f}")
            gh_response_to_charger = await get_detailed_route_from_graphhopper(current_sim_coord, suitable_charger.coordinates)
            to_charger_parsed = parse_graphhopper_response(gh_response_to_charger)

            if not to_charger_parsed or not to_charger_parsed.get('route_geometry'):
                raise RuntimeError(f"Could not route to charging station {suitable_charger.title}.")

            # Simulate driving to charger
            drive_to_charger_distance_km = to_charger_parsed['total_distance_km']
            drive_to_charger_duration_s = to_charger_parsed['total_duration_s']
            energy_consumed_to_charger_kwh = (drive_to_charger_distance_km * consumption_wh_km) / 1000.0

            soc_before_driving_to_charger = current_soc_percent
            current_soc_percent -= (energy_consumed_to_charger_kwh / battery_capacity_kwh) * 100.0
            total_energy_consumed_kwh += energy_consumed_to_charger_kwh

            # Add this driving segment to overall route
            # Ensure not to duplicate last point if it's the start of the new segment
            if all_route_geometry and to_charger_parsed['route_geometry'] and all_route_geometry[-1] == to_charger_parsed['route_geometry'][0]:
                all_route_geometry.extend(to_charger_parsed['route_geometry'][1:])
            else:
                all_route_geometry.extend(to_charger_parsed['route_geometry'])
            all_route_segments_parsed.extend(to_charger_parsed['route_segments'])
            
            total_optimized_distance_km += drive_to_charger_distance_km
            total_optimized_duration_s += drive_to_charger_duration_s

            current_sim_coord = suitable_charger.coordinates # Now at the charger location

            # --- Simulate Charging at Station ---
            target_soc_kwh = (target_charge_for_ev / 100.0) * battery_capacity_kwh
            current_soc_kwh = (current_soc_percent / 100.0) * battery_capacity_kwh
            charge_needed_kwh = target_soc_kwh - current_soc_kwh

            if charge_needed_kwh < 0.1: # Don't charge if almost full
                charge_needed_kwh = 0.0 # Set to 0 if negligible
                print(f"Negligible charge needed ({charge_needed_kwh:.2f} kWh). Skipping charge.")

            if charge_needed_kwh > 0:
                ev_max_power = get_charging_power_for_soc(ev_info, current_soc_percent)
                effective_charger_power = suitable_charger.power_kw if suitable_charger.power_kw else 0.0
                effective_charging_rate_kw = min(ev_max_power, effective_charger_power)

                if effective_charging_rate_kw == 0:
                    raise UnfeasibleRouteError(f"Effective charging power at {suitable_charger.title} is 0kW. Cannot charge.")
                
                charge_time_hours = charge_needed_kwh / effective_charging_rate_kw
                charge_time_minutes = round(charge_time_hours * 60)

                current_soc_before_charge = current_soc_percent
                current_soc_percent = (target_soc_kwh / battery_capacity_kwh) * 100.0
                total_charging_duration_minutes += charge_time_minutes
                total_energy_consumed_kwh -= charge_needed_kwh # Energy is added back

                # Add charging segment
                charging_segment_step = RouteStep( # Using RouteStep for charging "segments"
                    distance_km=0.0,
                    duration_s=float(charge_time_minutes * 60), # Convert minutes to seconds
                    geometry=[current_sim_coord, current_sim_coord], # No movement
                    instruction=f"Charge at {suitable_charger.title} for {charge_time_minutes} minutes"
                )
                all_route_segments_parsed.append(charging_segment_step)

                suitable_charger.recommended_charge_minutes = charge_time_minutes
                suitable_charger.estimated_charge_added_kwh = charge_needed_kwh
                charging_locations.append(suitable_charger)
                print(f"Charged at {suitable_charger.title} for {charge_time_minutes} min. SOC: {current_soc_before_charge:.1f}% -> {current_soc_percent:.1f}%.")
            else:
                print(f"No significant charge needed at {suitable_charger.title}. Proceeding.")
            
            # After charging, we are at the charger. The loop will then calculate route from this new current_sim_coord.
            # Continue the loop to recalculate the path to destination from the new point.
            continue 
        
        # --- If No Charge Needed, Drive the Remaining Leg to Destination ---
        # We already have the 'current_leg_parsed' data.
        print(f"No charge needed. Driving remaining leg of {distance_to_destination_this_leg:.2f} km.")
        
        drive_distance_km = current_leg_parsed['total_distance_km']
        drive_duration_s = current_leg_parsed['total_duration_s']
        energy_consumed_drive_kwh = (drive_distance_km * consumption_wh_km) / 1000.0

        soc_before_driving = current_soc_percent
        current_soc_percent -= (energy_consumed_drive_kwh / battery_capacity_kwh) * 100.0
        total_energy_consumed_kwh += energy_consumed_drive_kwh

        # Add this final driving segment to overall route
        if all_route_geometry and current_leg_parsed['route_geometry'] and all_route_geometry[-1] == current_leg_parsed['route_geometry'][0]:
            all_route_geometry.extend(current_leg_parsed['route_geometry'][1:])
        else:
            all_route_geometry.extend(current_leg_parsed['route_geometry'])
        all_route_segments_parsed.extend(current_leg_parsed['route_segments'])

        total_optimized_distance_km += drive_distance_km
        total_optimized_duration_s += drive_duration_s
        
        current_sim_coord = end_coord # Reached destination if no charge was needed in this leg

    # Final checks
    if current_sim_coord != end_coord:
        raise UnfeasibleRouteError("Could not reach destination within maximum iterations. Route might be too complex or unfeasible.")

    if current_soc_percent < min_charge_at_destination_for_ev:
        # This check should ideally be caught by the loop, but as a safeguard.
        print(f"Warning: Arrived at destination with {current_soc_percent:.1f}% SOC, which is below minimum {min_charge_at_destination_for_ev}%.")

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