from fastapi import APIRouter, Request, status

from app.dependencies import DbSession, ApiKey, limiter
from app.service import FuelLogService
from app.dto.FuelLogDto import FuelLogCreate, FuelLogOut

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["Fuel Logs"],
)

@router.post("/{vehicle_id}/fuel", response_model=FuelLogOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_fuel(
    request: Request,
    vehicle_id: int,
    data: FuelLogCreate,
    db: DbSession,
    api_key: ApiKey,
):
    return FuelLogService.log_fuel(db, vehicle_id, data)

@router.get("/{vehicle_id}/fuel", response_model=list[FuelLogOut])
@limiter.limit("100/minute")
def get_fuel_history(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    api_key: ApiKey,
):
    return FuelLogService.get_history(db, vehicle_id)