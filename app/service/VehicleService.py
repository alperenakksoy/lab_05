from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository import VehicleRepository
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut, VehicleOutV2

def _links(vehicle_id: int, version: str = "v1") -> dict:
    base = f"/api/{version}/vehicles"
    return {
        "self":       {"href": f"{base}/{vehicle_id}"},
        "collection": {"href": base},
        "positions":  {"href": f"/api/v1/vehicles/{vehicle_id}/positions"},
        "fuel":       {"href": f"/api/v1/vehicles/{vehicle_id}/fuel"},
    }

def _404(vehicle_id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
        "error": "NOT_FOUND",
        "message": f"Vehicle {vehicle_id} not found",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[VehicleOut]:
    return [VehicleOut.model_validate(v) for v in VehicleRepository.get_all(db, skip, limit)]

def get_by_id(db: Session, vehicle_id: int) -> VehicleOut:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v: _404(vehicle_id)
    return VehicleOut.model_validate(v)

def create(db: Session, data: VehicleCreate) -> VehicleOut:
    if VehicleRepository.get_by_plate(db, data.plate):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "error": "CONFLICT",
            "message": f"Plate '{data.plate}' already exists",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    return VehicleOut.model_validate(VehicleRepository.create(db, data))

def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> VehicleOut:
    if not VehicleRepository.get_by_id(db, vehicle_id): _404(vehicle_id)
    return VehicleOut.model_validate(VehicleRepository.update(db, vehicle_id, data))

def delete(db: Session, vehicle_id: int) -> None:
    if not VehicleRepository.get_by_id(db, vehicle_id): _404(vehicle_id)
    VehicleRepository.delete(db, vehicle_id)

def get_all_v2(db: Session, skip: int = 0, limit: int = 100) -> list[VehicleOutV2]:
    return [VehicleOutV2.model_validate(v) for v in VehicleRepository.get_all(db, skip, limit)]

def get_by_id_v2(db: Session, vehicle_id: int) -> VehicleOutV2:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v: _404(vehicle_id)
    return VehicleOutV2.model_validate(v)