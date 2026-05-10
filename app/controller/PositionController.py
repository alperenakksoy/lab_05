from fastapi import APIRouter, Request, status

from app.dependencies import DbSession, ApiKey, limiter
from app.service import PositionService
from app.dto.PositionDto import PositionCreate, PositionOut

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["Positions"],
)


@router.post("/{vehicle_id}/positions", response_model=PositionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_position(
    request: Request,
    vehicle_id: int,
    data: PositionCreate,
    db: DbSession,
    api_key: ApiKey,
):
    return PositionService.log_position(db, vehicle_id, data)


@router.get("/{vehicle_id}/positions/latest", response_model=PositionOut)
@limiter.limit("100/minute")
def get_latest_position(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    api_key: ApiKey,
):
    return PositionService.get_latest(db, vehicle_id)