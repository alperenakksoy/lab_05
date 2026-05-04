"""
crud.py
-------
Equivalent to @Repository / JpaRepository in Spring Boot.

In Spring Boot:
  vehicleRepository.findAll()
  vehicleRepository.findById(id)
  vehicleRepository.save(vehicle)
  vehicleRepository.deleteById(id)

Here we write plain functions that accept a SQLAlchemy Session
and perform the same operations manually.
"""

from sqlalchemy.orm import Session
from app import models, schemas


# ══════════════════════════════════════════════════════
#  VEHICLE  CRUD
# ══════════════════════════════════════════════════════

def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> list[models.Vehicle]:
    """Equivalent to vehicleRepository.findAll(Pageable pageable)"""
    return db.query(models.Vehicle).offset(skip).limit(limit).all()


def get_vehicle(db: Session, vehicle_id: int) -> models.Vehicle | None:
    """Equivalent to vehicleRepository.findById(id)"""
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()


def get_vehicle_by_plate(db: Session, plate: str) -> models.Vehicle | None:
    """Equivalent to vehicleRepository.findByPlate(plate)"""
    return db.query(models.Vehicle).filter(models.Vehicle.plate == plate).first()


def create_vehicle(db: Session, vehicle: schemas.VehicleCreate) -> models.Vehicle:
    """
    Equivalent to vehicleRepository.save(new Vehicle(...))
    model_dump() converts the Pydantic schema into a plain dict,
    then ** unpacks it as constructor arguments.
    """
    db_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)   # loads the auto-generated id back into the object
    return db_vehicle


def update_vehicle(
    db: Session,
    vehicle_id: int,
    updates: schemas.VehicleUpdate
) -> models.Vehicle | None:
    """Equivalent to vehicleRepository.save(existingVehicle) after setting fields"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None

    # Only apply fields that were actually sent (exclude_unset = patch semantics)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    """Equivalent to vehicleRepository.deleteById(id)"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    db.delete(db_vehicle)
    db.commit()
    return True


# ══════════════════════════════════════════════════════
#  POSITION  CRUD
# ══════════════════════════════════════════════════════

def create_position(
    db: Session,
    vehicle_id: int,
    position: schemas.PositionCreate
) -> models.Position:
    db_pos = models.Position(**position.model_dump(), vehicle_id=vehicle_id)
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos


def get_latest_position(db: Session, vehicle_id: int) -> models.Position | None:
    return (
        db.query(models.Position)
        .filter(models.Position.vehicle_id == vehicle_id)
        .order_by(models.Position.recorded_at.desc())
        .first()
    )


# ══════════════════════════════════════════════════════
#  FUEL LOG  CRUD
# ══════════════════════════════════════════════════════

def create_fuel_log(
    db: Session,
    vehicle_id: int,
    log: schemas.FuelLogCreate
) -> models.FuelLog:
    db_log = models.FuelLog(**log.model_dump(), vehicle_id=vehicle_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_fuel_logs(db: Session, vehicle_id: int) -> list[models.FuelLog]:
    return (
        db.query(models.FuelLog)
        .filter(models.FuelLog.vehicle_id == vehicle_id)
        .order_by(models.FuelLog.logged_at.desc())
        .all()
    )