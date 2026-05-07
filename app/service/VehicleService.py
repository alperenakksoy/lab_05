from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository import VehicleRepository
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut, VehicleOutV2


def _build_links(vehicle_id: int, version: str = "v1") -> dict:
    base = f"/api/{version}/vehicles"
    return {
        "self":       {"href": f"{base}/{vehicle_id}"},
        "collection": {"href": base},
        "positions":  {"href": f"/api/v1/vehicles/{vehicle_id}/positions"},
        "fuel":       {"href": f"/api/v1/vehicles/{vehicle_id}/fuel"},
    }


def _not_found(vehicle_id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error":     "NOT_FOUND",
            "message":   f"Vehicle {vehicle_id} not found",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


# ── v1 ────────────────────────────────────────────────────────────────────────

def get_all(db: Session, skip: int, limit: int) -> list[VehicleOut]:
    vehicles = VehicleRepository.get_all(db, skip, limit)
    result = []
    for v in vehicles:
        out = VehicleOut.model_validate(v)
        object.__setattr__(out, "_links", _build_links(v.id))
        result.append(out)
    return result


def get_by_id(db: Session, vehicle_id: int) -> VehicleOut:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v:
        _not_found(vehicle_id)
    out = VehicleOut.model_validate(v)
    object.__setattr__(out, "_links", _build_links(v.id))
    return out


def create(db: Session, data: VehicleCreate) -> VehicleOut:
    if VehicleRepository.get_by_plate(db, data.plate):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error":     "CONFLICT",
                "message":   f"Plate '{data.plate}' already exists",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    v = VehicleRepository.create(db, data)
    out = VehicleOut.model_validate(v)
    object.__setattr__(out, "_links", _build_links(v.id))
    return out


def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> VehicleOut:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        _not_found(vehicle_id)
    v = VehicleRepository.update(db, vehicle_id, data)
    out = VehicleOut.model_validate(v)
    object.__setattr__(out, "_links", _build_links(v.id))
    return out


def delete(db: Session, vehicle_id: int) -> None:
    if not VehicleRepository.get_by_id(db, vehicle_id):
        _not_found(vehicle_id)
    VehicleRepository.delete(db, vehicle_id)



def get_all_v2(db: Session, skip: int, limit: int) -> list[VehicleOutV2]:
    vehicles = VehicleRepository.get_all(db, skip, limit)
    result = []
    for v in vehicles:
        out = VehicleOutV2.model_validate(v)
        object.__setattr__(out, "_links", _build_links(v.id, "v2"))
        result.append(out)
    return result


def get_by_id_v2(db: Session, vehicle_id: int) -> VehicleOutV2:
    v = VehicleRepository.get_by_id(db, vehicle_id)
    if not v:
        _not_found(vehicle_id)

    out = VehicleOutV2.model_validate(v)
    object.__setattr__(out, "_links", _build_links(v.id, "v2"))
    return out