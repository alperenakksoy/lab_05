from sqlalchemy.orm import Session
from app.entity.Vehicle import Vehicle
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[type[Vehicle]]:
    return db.query(Vehicle).offset(skip).limit(limit).all()


def get_by_id(db: Session, vehicle_id: int) -> type[Vehicle] | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def get_by_plate(db: Session, plate: str) -> type[Vehicle] | None:
    return db.query(Vehicle).filter(Vehicle.plate == plate).first()


def create(db: Session, data: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> type[Vehicle] | None:
    vehicle = get_by_id(db, vehicle_id)
    if not vehicle:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete(db: Session, vehicle_id: int) -> bool:
    vehicle = get_by_id(db, vehicle_id)
    if not vehicle:
        return False
    db.delete(vehicle)
    db.commit()
    return True