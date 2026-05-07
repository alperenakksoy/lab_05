from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.entity.Vehicle import Vehicle

class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id:          Mapped[int]        = mapped_column(primary_key=True, index=True)
    vehicle_id:  Mapped[int]        = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    fuel_level:  Mapped[float]      = mapped_column(Float, nullable=False)
    fuel_litres: Mapped[float|None] = mapped_column(Float, nullable=True)
    logged_at:   Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="fuel_logs")