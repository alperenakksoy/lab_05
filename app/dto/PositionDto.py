from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PositionCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_kmh: float = Field(0.0, ge=0)


class PositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    recorded_at: datetime