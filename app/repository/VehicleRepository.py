from sqlalchemy.orm import Session
from app.entitiy.Vehicle import Vehicle
from app import dto


def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> list[Vehicle]:
    return db.query(Vehicle).offset(skip).limit(limit).all()


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def get_vehicle_by_plate(db: Session, plate: str) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.plate == plate).first()


def create_vehicle(db: Session, vehicle: dto.VehicleCreate) -> Vehicle:
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(
    db: Session,
    vehicle_id: int,
    updates: dto.VehicleUpdate
) -> Vehicle | None:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False

    db.delete(db_vehicle)
    db.commit()
    return True