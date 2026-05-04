from datetime import datetime

from sqlalchemy import ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entitiy.Vehicle import Vehicle

class FuelLog():
    __tablename__ = "fuel_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    fuel_level: Mapped[float] = mapped_column(Float, nullable=False)  # percentage 0-100
    fuel_litres: Mapped[float] = mapped_column(Float, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="fuel_logs")

    