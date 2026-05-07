from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums.vehicle_enum import VehicleStatus

if TYPE_CHECKING:
    from app.entity.Position import Position
    from app.entity.FuelLog import FuelLog

class Vehicle(Base):
    __tablename__ = "vehicles"

    id:         Mapped[int]           = mapped_column(primary_key=True, index=True)
    plate:      Mapped[str]           = mapped_column(String(20), unique=True, nullable=False)
    model:      Mapped[str]           = mapped_column(String(100), nullable=False)
    driver:     Mapped[str | None]    = mapped_column(String(100), nullable=True)
    status:     Mapped[VehicleStatus] = mapped_column(
                    SAEnum(VehicleStatus, name="vehicle_status",
                           values_callable=lambda e: [x.value for x in e]),
                    default=VehicleStatus.ACTIVE, nullable=False)
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    # String references only — never import Position/FuelLog directly here
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="vehicle", cascade="all, delete-orphan"
    )
    fuel_logs: Mapped[list["FuelLog"]] = relationship(
        "FuelLog", back_populates="vehicle", cascade="all, delete-orphan"
    )