from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.enums.vehicle_enum import VehicleStatus


class VehicleCreate(BaseModel):
    plate:  str           = Field(..., min_length=2, max_length=20)
    model:  str           = Field(..., min_length=2, max_length=100)
    driver: str | None    = None
    status: VehicleStatus = VehicleStatus.ACTIVE


class VehicleUpdate(BaseModel):
    plate:  str | None           = None
    model:  str | None           = None
    driver: str | None           = None
    status: VehicleStatus | None = None


class VehicleOut(BaseModel):
    """v1 response — field is called 'plate'."""
    model_config = ConfigDict(from_attributes=True)

    id:         int
    plate:      str
    model:      str
    driver:     str | None
    status:     VehicleStatus
    created_at: datetime
    _links:     dict | None = None


class VehicleOutV2(BaseModel):
    """v2 response — BREAKING CHANGE: 'plate' renamed to 'registration'."""
    model_config = ConfigDict(from_attributes=True)

    id:           int
    registration: str          # renamed from plate
    model:        str
    driver:       str | None
    status:       VehicleStatus
    created_at:   datetime
    _links:       dict | None = None