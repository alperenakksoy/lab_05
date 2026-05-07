from sqlalchemy.orm import Session
from app.entity.FuelLog import FuelLog
from app.dto.FuelLogDto import FuelLogCreate


def create(db: Session, vehicle_id: int, data: FuelLogCreate) -> FuelLog:
    log = FuelLog(**data.model_dump(), vehicle_id=vehicle_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_all(db: Session, vehicle_id: int) -> list[FuelLog]:
    return (
        db.query(FuelLog)
        .filter(FuelLog.vehicle_id == vehicle_id)
        .order_by(FuelLog.logged_at.desc())
        .all()
    )