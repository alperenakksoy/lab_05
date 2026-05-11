from fastapi import APIRouter, Request, status

from app.dependencies import DbSession, RequireJson, BearerToken, limiter
from app.service import VehicleService
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOutV2

router = APIRouter(
    prefix="/api/v2/vehicles",
    tags=["Vehicles V2"],
)

@router.get("", response_model=list[VehicleOutV2])
@limiter.limit("100/minute")
def list_vehicles(
    request: Request,
    db: DbSession,
    _: RequireJson,
    token: BearerToken,
    skip: int = 0,
    limit: int = 100,
):
    return VehicleService.get_all_v2(db, skip=skip, limit=limit)

@router.get("/{vehicle_id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def get_vehicle(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    _: RequireJson,
    token: BearerToken,
):
    return VehicleService.get_by_id_v2(db, vehicle_id)

@router.post("", response_model=VehicleOutV2, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle(
    request: Request,
    data: VehicleCreate,
    db: DbSession,
    token: BearerToken,
):
    v = VehicleService.create(db, data)
    return VehicleService.get_by_id_v2(db, v.id)

@router.put("/{vehicle_id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def update_vehicle(
    request: Request,
    vehicle_id: int,
    data: VehicleUpdate,
    db: DbSession,
    token: BearerToken,
):
    VehicleService.update(db, vehicle_id, data)
    return VehicleService.get_by_id_v2(db, vehicle_id)

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle(
    request: Request,
    vehicle_id: int,
    db: DbSession,
    token: BearerToken,
):
    VehicleService.delete(db, vehicle_id)