from fastapi import APIRouter, HTTPException, status
from api.v1.models.route_request import RouteRequest
from api.v1.models.route_response import RouteResponse
from services.ev_optimizer import optimize_ev_route 
router = APIRouter()

@router.post("/optimize-route", response_model=RouteResponse)
async def optimize_route(request: RouteRequest):
    try:
        response = await optimize_ev_route(
            start_location=request.start_location,
            end_location=request.end_location,
            ev_type=request.ev_type,
            current_charge_percent=request.current_charge_percent, 
        )
        return response
    except ValueError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Input Error: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc() # Log the full traceback for unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected server error occurred: {e}")