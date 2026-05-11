from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, computed_field
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
    model_config = ConfigDict(from_attributes=True)

    id:         int
    plate:      str
    model:      str
    driver:     str | None
    status:     VehicleStatus
    created_at: datetime

    @computed_field
    @property
    def _links(self) -> dict:
        base = f"/api/v1/vehicles/{self.id}"
        return {
            "self":       {"href": base},
            "collection": {"href": "/api/v1/vehicles"},
            "positions":  {"href": f"{base}/positions"},
            "fuel":       {"href": f"{base}/fuel"},
        }


class VehicleOutV2(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id:           int
    registration: str = Field(validation_alias='plate')
    model:        str
    driver:       str | None
    status:       VehicleStatus
    created_at:   datetime

    @computed_field
    @property
    def _links(self) -> dict:
        base = f"/api/v2/vehicles/{self.id}"
        return {
            "self":       {"href": base},
            "collection": {"href": "/api/v2/vehicles"},
        }