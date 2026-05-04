from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import repository, dto, entitiy


def build_vehicle_links(vehicle_id: int, version: str = "v1") -> dict:
    base = f"/api/{version}/vehicles"
    return {
        "self": {"href": f"{base}/{vehicle_id}"},
        "collection": {"href": base},
        "positions": {"href": f"{base}/{vehicle_id}/positions"},
        "fuel": {"href": f"{base}/{vehicle_id}/fuel"},
    }

def list_vehicles(db: Session, skip: int, limit: int) -> list[models.Vehicle]:
    """Return all vehicles — no extra logic needed here yet."""
    return crud.get_vehicles(db, skip=skip, limit=limit)


def get_vehicle_or_404(db: Session, vehicle_id: int) -> models.Vehicle:
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Vehicle {vehicle_id} not found"}
        )
    return vehicle


def create_vehicle(db: Session, data: schemas.VehicleCreate) -> models.Vehicle:
    existing = crud.get_vehicle_by_plate(db, data.plate)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "CONFLICT",
                "message": f"Vehicle with plate '{data.plate}' already exists"
            }
        )
    return crud.create_vehicle(db, data)


def update_vehicle(
        db: Session,
        vehicle_id: int,
        updates: schemas.VehicleUpdate
) -> models.Vehicle:
    get_vehicle_or_404(db, vehicle_id)  # raises 404 if missing
    return crud.update_vehicle(db, vehicle_id, updates)


def delete_vehicle(db: Session, vehicle_id: int) -> None:
    get_vehicle_or_404(db, vehicle_id)
    crud.delete_vehicle(db, vehicle_id)
