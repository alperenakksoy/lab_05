from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository import VehicleRepository, PositionRepository
from app.dto.PositionDto import PositionCreate, PositionOut


def log_position(db: Session, vehicle_id: int, data: PositionCreate) -> PositionOut:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":     "NOT_FOUND",
                "message":   f"Vehicle {vehicle_id} not found",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    pos = PositionRepository.create(db, vehicle_id, data)
    return PositionOut.model_validate(pos)


def get_latest(db: Session, vehicle_id: int) -> PositionOut:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":     "NOT_FOUND",
                "message":   f"Vehicle {vehicle_id} not found",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    pos = PositionRepository.get_latest(db, vehicle_id)
    if not pos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":     "NOT_FOUND",
                "message":   f"No positions found for vehicle {vehicle_id}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return PositionOut.model_validate(pos)