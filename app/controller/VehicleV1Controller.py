from fastapi import APIRouter, Request, status

from app.dependencies import DbSession, RequireJson, ApiKey, limiter
from app.service import VehicleService
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["Vehicles V1"],
)

@router.get("", response_model=list[VehicleOut])
@limiter.limit("100/minute")
def list_vehicles(
    request: Request,
    db: DbSession,
    _: RequireJson,
    api_key: ApiKey,
    skip: int = 0,
    limit: int = 100,
):
    return VehicleService.get_all(db, skip=skip, limit=limit)

@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle(
    request: Request,
    data: VehicleCreate,
    db: DbSession,
    _: RequireJson,
    api_key: ApiKey,
):
    return VehicleService.create(db, data)

@router.get("/{vehicle_id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def get_vehicle(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    _: RequireJson,
    api_key: ApiKey,
):
    return VehicleService.get_by_id(db, vehicle_id)

@router.put("/{vehicle_id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def update_vehicle(
    request: Request,
    vehicle_id: int,
    data: VehicleUpdate,
    db: DbSession,
    _: RequireJson,
    api_key: ApiKey,
):
    return VehicleService.update(db, vehicle_id, data)

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    api_key: ApiKey,
):
    VehicleService.delete(db, vehicle_id)