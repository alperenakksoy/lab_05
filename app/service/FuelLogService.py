from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository import VehicleRepository, FuelLogRepository
from app.dto.FuelLogDto import FuelLogCreate, FuelLogOut


def log_fuel(db: Session, vehicle_id: int, data: FuelLogCreate) -> FuelLogOut:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":     "NOT_FOUND",
                "message":   f"Vehicle {vehicle_id} not found",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    log = FuelLogRepository.create(db, vehicle_id, data)
    return FuelLogOut.model_validate(log)


def get_history(db: Session, vehicle_id: int) -> list[FuelLogOut]:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":     "NOT_FOUND",
                "message":   f"Vehicle {vehicle_id} not found",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    logs = FuelLogRepository.get_all(db, vehicle_id)
    return [FuelLogOut.model_validate(l) for l in logs]