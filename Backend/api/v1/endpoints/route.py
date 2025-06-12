# ev-route-optimizer-backend/api/v1/endpoints/route.py
from fastapi import APIRouter, HTTPException, status
from api.v1.models.route_request import RouteRequest
from api.v1.models.route_response import RouteResponse
from services.ev_optimizer import optimize_ev_route # Import the core optimization logic

router = APIRouter()

@router.post("/optimize-route", response_model=RouteResponse, status_code=status.HTTP_200_OK)
async def get_optimized_ev_route(request: RouteRequest):
    """
    Optimizes an EV route based on start/end locations and EV type,
    calculating and inserting necessary charging stops for efficient travel.
    """
    try:
        optimized_route = await optimize_ev_route(request)
        return optimized_route
    except ValueError as e:
        # Handle client-side errors (e.g., invalid EV type, ungeocodeable address)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        # Handle errors from external services (e.g., ORS API failure)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Backend service error: {e}")
    except Exception as e:
        # Catch any other unexpected errors and return a generic 500 error
        print(f"Unhandled exception: {e}") # Log unexpected errors for debugging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected internal error occurred.")