from datetime import datetime
from sqlalchemy import DateTime,String,Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.vehicle_enum import VehicleStatus
from app.entitiy.Position import Position
from app.entitiy.FuelLog import FuelLog

class Vehicle(object):
    __tablename__ = 'vehicles'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    driver: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[VehicleStatus] = mapped_column(
        SAEnum(VehicleStatus), default=VehicleStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="vehicle", cascade="all, delete-orphan"
    )
    fuel_logs: Mapped[list["FuelLog"]] = relationship(
        "FuelLog", back_populates="vehicle", cascade="all, delete-orphan"
    )