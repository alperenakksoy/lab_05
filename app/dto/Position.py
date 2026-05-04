from datetime import datetime
from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_kmh: float = Field(0.0, ge=0)


class PositionOut(BaseModel):
    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    recorded_at: datetime

    class Config:
        from_attributes = True