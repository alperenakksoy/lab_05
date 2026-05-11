from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository import VehicleRepository
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut, VehicleOutV2


def _404(vehicle_id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
        "error":     "NOT_FOUND",
        "message":   f"Vehicle {vehicle_id} not found",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[VehicleOut]:
    vehicles = VehicleRepository.get_all(db, skip, limit)
    return [VehicleOut.model_validate(v) for v in vehicles]


def get_by_id(db: Session, vehicle_id: int) -> VehicleOut:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v:
        _404(vehicle_id)
    return VehicleOut.model_validate(v)


def create(db: Session, data: VehicleCreate) -> VehicleOut:
    if VehicleRepository.get_by_plate(db, data.plate):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "error":     "CONFLICT",
            "message":   f"Plate '{data.plate}' already exists",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    v = VehicleRepository.create(db, data)
    return VehicleOut.model_validate(v)

def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> VehicleOut:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        _404(vehicle_id)
    v = VehicleRepository.update(db, vehicle_id, data)
    return VehicleOut.model_validate(v)


def delete(db: Session, vehicle_id: int) -> None:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        _404(vehicle_id)
    VehicleRepository.delete(db, vehicle_id)


def get_all_v2(db: Session, skip: int = 0, limit: int = 100) -> list[VehicleOutV2]:
    vehicles = VehicleRepository.get_all(db, skip, limit)
    return [VehicleOutV2.model_validate(v) for v in vehicles]


def get_by_id_v2(db: Session, vehicle_id: int) -> VehicleOutV2:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v:
        _404(vehicle_id)
    return VehicleOutV2.model_validate(v)