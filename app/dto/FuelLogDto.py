from datetime import datetime
from pydantic import BaseModel, Field


class FuelLogCreate(BaseModel):
    fuel_level: float = Field(..., ge=0, le=100)
    fuel_litres: float | None = None


class FuelLogOut(BaseModel):
    id: int
    vehicle_id: int
    fuel_level: float
    fuel_litres: float | None
    logged_at: datetime

    class Config:
        from_attributes = True