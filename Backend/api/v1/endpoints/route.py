# Backend/api/v1/endpoints/route.py

from fastapi import APIRouter, HTTPException, status
from api.v1.models.route_request import RouteRequest
from api.v1.models.route_response import RouteResponse
from services.ev_optimizer import optimize_ev_route # Ensure this import is correct

router = APIRouter()

@router.post("/optimize-route", response_model=RouteResponse)
async def optimize_route(request: RouteRequest):
    try:
        # Pass fields from RouteRequest to optimize_ev_route using their new, matching names
        response = await optimize_ev_route(
            start_location=request.start_location,
            end_location=request.end_location,
            ev_type=request.ev_type,
            current_charge_percent=request.current_charge_percent, # This is an int, function expects int/float, so it's fine.
            # Optional parameters for optimize_ev_route are not in RouteRequest,
            # so optimize_ev_route will use its own defaults for them.
            # Parameters like charging_preference and range_full_charge are received from frontend
            # but are not directly passed to optimize_ev_route's current signature.
            # You can decide to pass them if you extend optimize_ev_route to use them later.
        )
        return response
    except ValueError as e: # Catch specific ValueErrors (like EV not found)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Input Error: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc() # Log the full traceback for unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected server error occurred: {e}")