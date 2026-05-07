from sqlalchemy.orm import Session
from app.entity.Position import Position
from app.dto.PositionDto import PositionCreate


def create(db: Session, vehicle_id: int, data: PositionCreate) -> Position:
    pos = Position(**data.model_dump(), vehicle_id=vehicle_id)
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return pos


def get_latest(db: Session, vehicle_id: int) -> Position | None:
    return (
        db.query(Position)
        .filter(Position.vehicle_id == vehicle_id)
        .order_by(Position.recorded_at.desc())
        .first()
    )