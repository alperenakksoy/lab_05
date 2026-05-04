from datetime import datetime
from sqlalchemy import ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.entitiy.Vehicle import Vehicle


class Position():
 __tablename__ = "positions"

 id: Mapped[int] = mapped_column(primary_key=True, index=True)
 vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
 latitude: Mapped[float] = mapped_column(Float, nullable=False)
 longitude: Mapped[float] = mapped_column(Float, nullable=False)
 speed_kmh: Mapped[float] = mapped_column(Float, default=0.0)
 recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

 vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="positions")
