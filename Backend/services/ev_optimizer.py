# Backend/services/ev_optimizer.py

import httpx
import asyncio
from typing import List, Dict, Any, Optional
import math
import traceback
from .geocoding import get_coordinates
from .routing import get_detailed_route_from_google, parse_google_directions_response
from .charging_stations import find_charging_stations

from api.v1.models.route_response import (
    RouteResponse,
    RouteSummary,
    RouteDetails,
    Coordinate,
    RouteStep
)
from pydantic import ValidationError

# Define your EV models data here
EV_MODELS = {
    "Tesla Model 3 Long Range": {
        "battery_capacity_kwh": 75.0,
        "consumption_wh_km": 150.0,
        "charging_speed_kw_standard": 11.0,
        "charging_speed_kw_fast": 250.0
    },
    "Tata Nexon EV": {
        "battery_capacity_kwh": 40.0,
        "consumption_wh_km": 135.0,
        "charging_speed_kw_standard": 7.2,
        "charging_speed_kw_fast": 50.0
    },
    "Nissan Leaf (40 kWh)": {
        "battery_capacity_kwh": 40.0,
        "consumption_wh_km": 170.0,
        "charging_speed_kw_standard": 6.6,
        "charging_speed_kw_fast": 50.0
    },
    "Hyundai Kona Electric (64 kWh)": {
        "battery_capacity_kwh": 64.0,
        "consumption_wh_km": 160.0,
        "charging_speed_kw_standard": 7.2,
        "charging_speed_kw_fast": 77.0
    }
}

# Custom Exception for unfeasible routes
class UnfeasibleRouteError(Exception):
    """Custom exception for when a route is not feasible due to low SOC."""
    pass

# Helper function: Calculate Haversine distance between two Coordinates
def _calculate_haversine_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    """
    Calculates the Haversine distance between two Coordinate objects in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = math.radians(coord1.lat)
    lon1_rad = math.radians(coord1.lon)
    lat2_rad = math.radians(coord2.lat)
    lon2_rad = math.radians(coord2.lon)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# Helper function to find a point along a polyline at a given distance
def _find_point_along_polyline(
    start_coord: Coordinate,
    polyline_coords: List[Coordinate],
    target_distance_km: float
) -> Optional[Coordinate]:
    """
    Finds a Coordinate along a given polyline at approximately the target_distance_km
    from the start_coord. Assumes polyline_coords represents a path starting near start_coord.
    Returns None if target_distance_km exceeds polyline length.
    """
    if not polyline_coords:
        return None

    current_distance_traversed = 0.0
    
    # Find the starting point in the polyline_coords that is closest to start_coord
    best_start_index = 0
    min_dist = float('inf')
    for i, coord in enumerate(polyline_coords):
        dist_to_coord = _calculate_haversine_distance(start_coord, coord)
        if dist_to_coord < min_dist:
            min_dist = dist_to_coord
            best_start_index = i
    
    previous_point = polyline_coords[best_start_index]

    for i in range(best_start_index + 1, len(polyline_coords)):
        current_point = polyline_coords[i]
        segment_length = _calculate_haversine_distance(previous_point, current_point)

        if current_distance_traversed + segment_length >= target_distance_km:
            remaining_dist_in_segment = target_distance_km - current_distance_traversed
            interpolation_factor = remaining_dist_in_segment / segment_length if segment_length > 0 else 0
            
            interpolated_lat = previous_point.lat + (current_point.lat - previous_point.lat) * interpolation_factor
            interpolated_lon = previous_point.lon + (current_point.lon - previous_point.lon) * interpolation_factor
            
            return Coordinate(lat=interpolated_lat, lon=interpolated_lon)
        
        current_distance_traversed += segment_length
        previous_point = current_point
    
    return None

async def optimize_ev_route(
    start_location: str,
    end_location: str,
    ev_type: str,
    current_charge_percent: int,
    min_soc_percent: float = 10.0, # Minimum SOC to maintain (e.g., at end of segment)
    target_soc_percent: float = 90.0, # Target SOC when charging as per new algo step 9
    charging_preference: str = "standard", # "standard" or "fast"
    max_iterations: int = 20, # Increased iterations for complex routes
    highway_factor: float = 1.2, # Factor for increased consumption on highways
    segment_planning_length_km: float = 100.0 # Your new segment length (Step 4)
) -> RouteResponse:
    try:
        # --- Step 1: Take the start and end location ---
        # Handled by function parameters.

        # --- 1. Look up EV specific data ---
        ev_data = EV_MODELS.get(ev_type)
        if not ev_data:
            raise ValueError(f"EV type '{ev_type}' not found in supported models. Please provide valid EV type.")

        battery_capacity_kwh = ev_data["battery_capacity_kwh"]
        consumption_wh_km = ev_data["consumption_wh_km"]
        
        # Determine charging speed based on preference
        if charging_preference.lower() == "fast":
            charging_speed_kw = ev_data["charging_speed_kw_fast"]
        else: # Default to standard
            charging_speed_kw = ev_data["charging_speed_kw_standard"]

        # --- 2. Geocode Start and End Addresses ---
        start_coord = await get_coordinates(start_location)
        end_coord = await get_coordinates(end_location)

        if not start_coord:
            return RouteResponse(success=False, message=f"Could not geocode start address: {start_location}")
        if not end_coord:
            return RouteResponse(success=False, message=f"Could not geocode end address: {end_location}")

        #print(f"DEBUG: Using EV: {ev_type} (Battery: {battery_capacity_kwh} kWh, Consumption: {consumption_wh_km} Wh/km)")
        #print(f"DEBUG: Charging preference: {charging_preference}, Speed: {charging_speed_kw} kW")
        effective_consumption_kwh_km = (consumption_wh_km * highway_factor) / 1000 # Convert Wh/km to kWh/km
        #print(f"DEBUG: Effective consumption: {effective_consumption_kwh_km:.3f} kWh/km (with highway factor {highway_factor})")

        current_soc_kwh = (current_charge_percent / 100.0) * battery_capacity_kwh
        current_soc_percent = float(current_charge_percent)

        total_optimized_distance_km = 0.0
        total_optimized_duration_s = 0
        total_energy_consumed_kwh = 0.0
        total_charging_duration_minutes = 0.0
        charging_locations_coords: List[Coordinate] = [] # Stores coordinates of charging stops
        all_route_segments_parsed: List[RouteStep] = []
        full_route_geometry_coords: List[Coordinate] = [] # Accumulates geometry for entire optimized path

        current_position = start_coord

        # --- Step 2: Get the complete route from the start to end without any ev optimisation ---
        full_route_google_response = await get_detailed_route_from_google(start_coord, end_coord)
        if not full_route_google_response:
            raise Exception("Failed to get initial full route from Google Maps. Cannot plan route.")
        
        parsed_full_route = parse_google_directions_response(full_route_google_response)
        if not parsed_full_route or not parsed_full_route.route_geometry:
            raise Exception("Failed to parse initial full route geometry. Cannot plan route.")
        
        main_route_polyline = parsed_full_route.route_geometry
        total_route_distance_km = parsed_full_route.total_distance_km
        total_route_energy_needed_kwh = total_route_distance_km * effective_consumption_kwh_km
        
        # --- Step 3: if the route can be completed with the available charge, plan it and tell no charging required ---
        energy_remaining_at_dest_kwh = current_soc_kwh - total_route_energy_needed_kwh
        soc_remaining_at_dest_percent = (energy_remaining_at_dest_kwh / battery_capacity_kwh) * 100

        if soc_remaining_at_dest_percent >= min_soc_percent:
            #print(f"DEBUG: Route can be completed without charging. Final SOC: {soc_remaining_at_dest_percent:.1f}%")
            return RouteResponse(
                success=True,
                message="Route planned successfully! No charging stops required.",
                route_summary=RouteSummary(
                    totalDistanceKm=total_route_distance_km,
                    totalDurationMinutes=parsed_full_route.total_duration_s / 60.0,
                    totalDrivingMinutes=parsed_full_route.total_duration_s / 60.0,
                    totalChargingMinutes=0.0,
                    estimatedChargingStops=0,
                    totalEnergyConsumptionKwh=total_route_energy_needed_kwh,
                    finalChargePercent=soc_remaining_at_dest_percent
                ),
                route_details=parsed_full_route # Return the full parsed route
            )

        # --- Step 4: if it doesn't work then break the whole route into segments of 100kms ---
        #print(f"DEBUG: Route cannot be completed without charging. Initiating segment-based optimization (segments of {segment_planning_length_km}km).")

        # Initializing for iterative planning
        current_polyline_index = 0
        # Find the closest index in the main_route_polyline to start_coord
        min_dist_to_start_polyline = float('inf')
        for i, coord in enumerate(main_route_polyline):
            dist = _calculate_haversine_distance(start_coord, coord)
            if dist < min_dist_to_start_polyline:
                min_dist_to_start_polyline = dist
                current_polyline_index = i
        
        iteration = 0
        # Loop until current_position is very close to the end destination
        while _calculate_haversine_distance(current_position, end_coord) > 0.01 and iteration < max_iterations:
            iteration += 1
            #print(f"\n--- Optimization Iteration {iteration} --- Current Pos: {current_position.lat:.4f},{current_position.lon:.4f} SOC: {current_soc_percent:.1f}% ---")

            # Determine the end point of the *current planning segment*
            # This is either 100km from current_position along the polyline, or the final destination.
            segment_end_point_candidate = _find_point_along_polyline(
                current_position,
                main_route_polyline[current_polyline_index:],
                segment_planning_length_km
            )

            # If the remaining path is shorter than segment_planning_length_km, or _find_point_along_polyline
            # returns None, the next target is the final destination.
            if segment_end_point_candidate is None or _calculate_haversine_distance(segment_end_point_candidate, end_coord) < 0.01:
                next_target_coord = end_coord
                #print(f"DEBUG: Next planning target is final destination: {next_target_coord.lat:.4f},{next_target_coord.lon:.4f}")
            else:
                next_target_coord = segment_end_point_candidate
                #print(f"DEBUG: Next planning target is ~{segment_planning_length_km}km mark: {next_target_coord.lat:.4f},{next_target_coord.lon:.4f}")
            
            # Get the actual route for this segment from current_position to next_target_coord
            actual_segment_route_response = await get_detailed_route_from_google(current_position, next_target_coord)
            if not actual_segment_route_response:
                raise Exception(f"Failed to get route for segment from {current_position} to {next_target_coord}")
            
            parsed_actual_segment_route = parse_google_directions_response(actual_segment_route_response)
            if not parsed_actual_segment_route or not parsed_actual_segment_route.route_segments:
                raise Exception(f"Failed to parse route details for segment from {current_position} to {next_target_coord}")

            actual_segment_distance_km = parsed_actual_segment_route.total_distance_km
            actual_segment_energy_needed_kwh = actual_segment_distance_km * effective_consumption_kwh_km
            
            # --- Step 5: if the vehicle can travel the first 100km segment then continue to step 7 else go to step 6 ---
            # (This check now applies to ANY segment, not just the "first" for generality)
            soc_after_driving_segment_kwh = current_soc_kwh - actual_segment_energy_needed_kwh
            soc_after_driving_segment_percent = (soc_after_driving_segment_kwh / battery_capacity_kwh) * 100

            charging_stop_required_now = False

            if soc_after_driving_segment_percent < min_soc_percent:
                #print(f"DEBUG: SOC ({soc_after_driving_segment_percent:.1f}%) after driving planned segment ({actual_segment_distance_km:.2f}km) is below min_soc_percent ({min_soc_percent:.1f}%). Charging required.")
                charging_stop_required_now = True

                # Calculate max drivable distance based on current SOC down to min_soc_percent
                energy_usable_for_drive = current_soc_kwh - (min_soc_percent / 100.0) * battery_capacity_kwh
                max_drivable_km_before_critical = energy_usable_for_drive / effective_consumption_kwh_km if energy_usable_for_drive > 0 else 0.0

                # Search radius for chargers: slightly beyond critical range, with a minimum.
                search_radius_for_chargers_km = max(max_drivable_km_before_critical + 20, 50) # Buffer of 20km (from step 8) + minimum 50km
                
                # Find charging stations, prioritizing fast chargers if that's the preference
                min_power_for_search = ev_data["charging_speed_kw_fast"] if charging_preference.lower() == "fast" else ev_data["charging_speed_kw_standard"]

                found_stations = await find_charging_stations(
                    latitude=current_position.lat,
                    longitude=current_position.lon,
                    distance_km=int(search_radius_for_chargers_km), # OCM API expects int
                    max_results=5,
                    min_power_kw=min_power_for_search
                )
                
                best_reachable_charger_coord: Optional[Coordinate] = None
                best_charger_route_distance = float('inf')

                if found_stations:
                    for station in found_stations:
                        route_to_charger_response = await get_detailed_route_from_google(current_position, station.coordinates)
                        if route_to_charger_response:
                            parsed_route_to_charger = parse_google_directions_response(route_to_charger_response)
                            if parsed_route_to_charger:
                                energy_to_charger_kwh = parsed_route_to_charger.total_distance_km * effective_consumption_kwh_km
                                if current_soc_kwh - energy_to_charger_kwh >= (min_soc_percent / 100.0) * battery_capacity_kwh:
                                    if parsed_route_to_charger.total_distance_km < best_charger_route_distance:
                                        best_reachable_charger_coord = station.coordinates
                                        best_charger_route_distance = parsed_route_to_charger.total_distance_km
                                        #print(f"DEBUG: Found reachable charger candidate: {station.name} at {station.coordinates.lat:.4f},{station.coordinates.lon:.4f} (Dist: {parsed_route_to_charger.total_distance_km:.1f} km)")
                
                if best_reachable_charger_coord:
                    next_actual_waypoint = best_reachable_charger_coord
                    #print(f"DEBUG: Routing to best reachable charging station at {next_actual_waypoint.lat:.4f},{next_actual_waypoint.lon:.4f}")
                else:
                    # --- Step 6: find the required charging to travel and return a message stating "Charge the vehicle to that much and continue else route wont finish" ---
                    # If no reachable charger found, calculate what's needed at current spot
                    # This happens if it cannot even reach the next potential charger.
                    energy_needed_to_reach_next_safe_point = actual_segment_energy_needed_kwh # Or energy needed to reach _any_ point (e.g., 100km mark) safely
                    
                    # Calculate charge required to safely reach the next logical segment end or first charger.
                    # This requires enough energy to drive the segment PLUS end with min_soc_percent
                    required_soc_kwh_for_segment = (actual_segment_energy_needed_kwh + (min_soc_percent / 100.0) * battery_capacity_kwh)
                    charge_needed_kwh_to_proceed = required_soc_kwh_for_segment - current_soc_kwh
                    
                    if charge_needed_kwh_to_proceed <= 0: # Should not happen if charging_stop_required_now is true, but safety check
                        charge_needed_kwh_to_proceed = 0.1 # Minimum to trigger message
                    
                    charge_percent_needed = (charge_needed_kwh_to_proceed / battery_capacity_kwh) * 100
                    
                    # Create a RouteSummary with zero values for error state
                    error_summary = RouteSummary(
                        totalDistanceKm=0.0, totalDurationMinutes=0.0, totalDrivingMinutes=0.0,
                        totalChargingMinutes=0.0, estimatedChargingStops=0, totalEnergyConsumptionKwh=0.0, finalChargePercent=current_soc_percent
                    )
                    return RouteResponse(
                        success=False,
                        message=f"Charge the vehicle by at least {charge_percent_needed:.1f}% ({charge_needed_kwh_to_proceed:.2f} kWh) at current location ({current_position.lat:.4f},{current_position.lon:.4f}) to continue, else route may not be feasible.",
                        route_summary=error_summary,
                        route_details=None
                    )
            else:
                # Vehicle can complete the segment without dropping below min_soc_percent
                next_actual_waypoint = next_target_coord # Drive to the end of the planned segment
                #print(f"DEBUG: Vehicle can drive planned segment. Routing to {next_actual_waypoint.lat:.4f},{next_actual_waypoint.lon:.4f}.")

            # --- Step 10: Continue to complete the 100 km segment (or to the determined charging stop) ---
            # Drive the actual calculated segment (to segment_end_point or found_charger)
            final_driving_segment_response = await get_detailed_route_from_google(current_position, next_actual_waypoint)
            if not final_driving_segment_response:
                raise Exception(f"Failed to get final driving route from {current_position} to {next_actual_waypoint}")
            
            parsed_final_driving_segment = parse_google_directions_response(final_driving_segment_response)
            if not parsed_final_driving_segment or not parsed_final_driving_segment.route_segments:
                raise Exception(f"Failed to parse final driving route details for segment from {current_position} to {next_actual_waypoint}")

            distance_driven_in_this_step_km = parsed_final_driving_segment.total_distance_km
            duration_driven_in_this_step_s = parsed_final_driving_segment.total_duration_s
            energy_consumed_in_this_step_kwh = distance_driven_in_this_step_km * effective_consumption_kwh_km

            # Update overall route metrics
            total_optimized_distance_km += distance_driven_in_this_step_km
            total_optimized_duration_s += duration_driven_in_this_step_s
            total_energy_consumed_kwh += energy_consumed_in_this_step_kwh

            # Update SOC after driving
            current_soc_kwh -= energy_consumed_in_this_step_kwh
            current_soc_percent = (current_soc_kwh / battery_capacity_kwh) * 100
            
            all_route_segments_parsed.extend(parsed_final_driving_segment.route_segments)
            
            # Append geometry
            if full_route_geometry_coords and parsed_final_driving_segment.route_geometry and \
               _calculate_haversine_distance(full_route_geometry_coords[-1], parsed_final_driving_segment.route_geometry[0]) < 0.01:
                full_route_geometry_coords.extend(parsed_final_driving_segment.route_geometry[1:])
            else:
                full_route_geometry_coords.extend(parsed_final_driving_segment.route_geometry)
            
            # Move current position to the end of the segment just driven
            current_position = next_actual_waypoint
            
            # Advance current_polyline_index to ensure _find_point_along_polyline starts from the correct place
            min_dist_to_current_pos_on_main_polyline = float('inf')
            temp_idx_on_main = current_polyline_index # Start search from current_polyline_index onwards
            for i in range(current_polyline_index, len(main_route_polyline)):
                dist = _calculate_haversine_distance(current_position, main_route_polyline[i])
                if dist < min_dist_to_current_pos_on_main_polyline:
                    min_dist_to_current_pos_on_main_polyline = dist
                    temp_idx_on_main = i
            current_polyline_index = temp_idx_on_main


            #print(f"DEBUG: Drove {distance_driven_in_this_step_km:.2f} km. New SOC: {current_soc_percent:.1f}%")

            # --- Step 9: if not able to travel the distance then find a charging station to charge upto 90% ---
            # This logic is integrated as part of the `charging_stop_required_now` check.
            # If `next_actual_waypoint` was a charger, perform charging now.
            # Also, if we've reached the final destination and SOC is low, charge.
            is_at_final_destination = _calculate_haversine_distance(current_position, end_coord) < 0.01

            if charging_stop_required_now or (is_at_final_destination and current_soc_percent < min_soc_percent):
                # If a charging stop was made or at the end with low SOC, charge to target_soc_percent (90%)
                charge_target_percent_for_stop = 90.0 # As per Step 9's specific instruction
                
                charge_amount_kwh = ((charge_target_percent_for_stop / 100.0) * battery_capacity_kwh) - current_soc_kwh
                
                # Cap charge at full capacity
                if current_soc_kwh + charge_amount_kwh > battery_capacity_kwh:
                    charge_amount_kwh = battery_capacity_kwh - current_soc_kwh

                if charge_amount_kwh > 0.01: # Only charge if a meaningful amount
                    charge_duration_hours = charge_amount_kwh / charging_speed_kw
                    charge_duration_minutes = charge_duration_hours * 60

                    total_charging_duration_minutes += charge_duration_minutes
                    current_soc_kwh += charge_amount_kwh
                    current_soc_percent = (current_soc_kwh / battery_capacity_kwh) * 100
                    
                    if charge_amount_kwh > 0.01:
                        charging_locations_coords.append(current_position)
                        #print(f"DEBUG: Charging stop added at {current_position.lat:.4f},{current_position.lon:.4f}")
                    #print(f"DEBUG: Charged {charge_amount_kwh:.2f} kWh in {charge_duration_minutes:.1f} minutes. New SOC: {current_soc_percent:.1f}% (Target {charge_target_percent_for_stop:.1f}%)")
                else:
                    print("DEBUG: No meaningful charge needed at this point.")
            
        # Final check if the loop terminated because max_iterations was reached, but not at destination
        if _calculate_haversine_distance(current_position, end_coord) > 0.01 and iteration >= max_iterations:
             # --- Step 6 (part of): All options exhausted ---
             raise UnfeasibleRouteError(f"Max iterations ({max_iterations}) reached. Could not find a feasible route to {end_location}.")


        final_soc_percent = (current_soc_kwh / battery_capacity_kwh) * 100

        charge_coords_for_json = [
        {"lat": coord.lat, "lon": coord.lon} for coord in charging_locations_coords
        ]
        print(charging_locations_coords)

        # --- Step 12: return the data in the form required ---
        summary = RouteSummary(
            totalDistanceKm=total_optimized_distance_km,
            totalDurationMinutes=(total_optimized_duration_s / 60.0) + total_charging_duration_minutes,
            totalDrivingMinutes=total_optimized_duration_s / 60.0,
            totalChargingMinutes=total_charging_duration_minutes,
            estimatedChargingStops=len(charging_locations_coords),
            totalEnergyConsumptionKwh=total_energy_consumed_kwh,
            finalChargePercent=final_soc_percent
        )

        details = RouteDetails(
            total_distance_km=total_optimized_distance_km,
            total_duration_s=int(total_optimized_duration_s + (total_charging_duration_minutes * 60)),
            route_segments=all_route_segments_parsed,
            route_geometry=full_route_geometry_coords,
            charging_locations_coords=charge_coords_for_json 
        )

        print("Optimization complete. Returning result.")
        return RouteResponse(
            success=True,
            message="Route optimized successfully!",
            route_summary=summary,
            route_details=details
        )

    except UnfeasibleRouteError as e:
        print(f"UnfeasibleRouteError: {e}")
        traceback.print_exc()
        error_summary = RouteSummary(
            totalDistanceKm=0.0, totalDurationMinutes=0.0, totalDrivingMinutes=0.0,
            totalChargingMinutes=0.0, estimatedChargingStops=0, totalEnergyConsumptionKwh=0.0, finalChargePercent=0.0
        )
        return RouteResponse(
            success=False, message=f"Route optimization failed: {str(e)}",
            route_summary=error_summary, route_details=None
        )
    except ValidationError as e:
        print(f"Validation error during optimization: {e.errors()}")
        traceback.print_exc()
        error_summary = RouteSummary(
            totalDistanceKm=0.0, totalDurationMinutes=0.0, totalDrivingMinutes=0.0,
            totalChargingMinutes=0.0, estimatedChargingStops=0, totalEnergyConsumptionKwh=0.0, finalChargePercent=0.0
        )
        return RouteResponse(
            success=False, message=f"Invalid input data or internal model mismatch: {e.errors()}",
            route_summary=error_summary, route_details=None
        )
    except Exception as e:
        print(f"An unexpected error occurred during optimization: {e}")
        traceback.print_exc()
        error_summary = RouteSummary(
            totalDistanceKm=0.0, totalDurationMinutes=0.0, totalDrivingMinutes=0.0,
            totalChargingMinutes=0.0, estimatedChargingStops=0, totalEnergyConsumptionKwh=0.0, finalChargePercent=0.0
        )
        return RouteResponse(
            success=False, message=f"An internal server error occurred: {str(e)}",
            route_summary=error_summary, route_details=None
        )