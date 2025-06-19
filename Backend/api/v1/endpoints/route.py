from fastapi import APIRouter, HTTPException, status
from api.v1.models.route_request import RouteRequest
from api.v1.models.route_response import RouteResponse
from services.ev_optimizer import optimize_ev_route, UnfeasibleRouteError # Import the custom exception

router = APIRouter()

@router.post("/optimize-route", response_model=RouteResponse)
async def optimize_route(request: RouteRequest):
    try:
        response = await optimize_ev_route(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except UnfeasibleRouteError as e:
        # Catch the specific error for unfeasible routes due to no charging stations
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")