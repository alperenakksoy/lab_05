from typing import Annotated
from fastapi import FastAPI, Request, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timezone

from app.database import get_db
from app.service import VehicleService, PositionService, FuelLogService
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut, VehicleOutV2
from app.dto.PositionDto import PositionCreate, PositionOut
from app.dto.FuelLogDto import FuelLogCreate, FuelLogOut

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Vehicle Tracking API")
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: Exception):
    return _rate_limit_exceeded_handler(request, exc)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    error_content = exc.detail if isinstance(exc.detail, dict) else {
        "error": "Client Error",
        "message": exc.detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return JSONResponse(status_code=exc.status_code, content=error_content)

DbSession = Annotated[Session, Depends(get_db)]

def verify_content_type(accept: str = Header(default="*/*")):
    if "application/json" not in accept and "*/*" not in accept:
        raise HTTPException(status_code=406, detail="Accept header must allow application/json")

RequireJson = Annotated[None, Depends(verify_content_type)]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/versions")
@limiter.limit("100/minute")
def get_versions(request: Request):
    return {
        "versions": [
            {"version": "v1", "deprecated": False, "base_url": "/api/v1"},
            {"version": "v2", "deprecated": False, "sunset_date": "2026-12-31", "base_url": "/api/v2"}
        ]
    }

@app.get("/api/v1/vehicles", response_model=list[VehicleOut])
@limiter.limit("100/minute")
def list_vehicles_v1(request: Request, db: DbSession, header: RequireJson, skip: int = 0, limit: int = 100):
    return VehicleService.get_all(db, skip=skip, limit=limit)

@app.post("/api/v1/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle_v1(request: Request, data: VehicleCreate, db: DbSession, header: RequireJson):
    return VehicleService.create(db, data)

@app.get("/api/v1/vehicles/{id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def get_vehicle_v1(request: Request, id: int, db: DbSession, header: RequireJson):
    return VehicleService.get_by_id(db, id)

@app.put("/api/v1/vehicles/{id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def update_vehicle_v1(request: Request, id: int, data: VehicleUpdate, db: DbSession, header: RequireJson):
    return VehicleService.update(db, id, data)

@app.delete("/api/v1/vehicles/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle_v1(request: Request, id: int, db: DbSession):
    VehicleService.delete(db, id)
    return None

@app.post("/api/v1/vehicles/{id}/positions", response_model=PositionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_position(request: Request, id: int, data: PositionCreate, db: DbSession):
    return PositionService.log_position(db, id, data)

@app.get("/api/v1/vehicles/{id}/positions/latest", response_model=PositionOut)
@limiter.limit("100/minute")
def get_latest_position(request: Request, id: int, db: DbSession):
    return PositionService.get_latest(db, id)

@app.post("/api/v1/vehicles/{id}/fuel", response_model=FuelLogOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_fuel(request: Request, id: int, data: FuelLogCreate, db: DbSession):
    return FuelLogService.log_fuel(db, id, data)

@app.get("/api/v1/vehicles/{id}/fuel", response_model=list[FuelLogOut])
@limiter.limit("100/minute")
def get_fuel_history(request: Request, id: int, db: DbSession):
    return FuelLogService.get_history(db, id)

@app.get("/api/v2/vehicles", response_model=list[VehicleOutV2])
@limiter.limit("100/minute")
def list_vehicles_v2(request: Request, db: DbSession, header: RequireJson, skip: int = 0, limit: int = 100):
    return VehicleService.get_all_v2(db, skip=skip, limit=limit)

@app.get("/api/v2/vehicles/{id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def get_vehicle_v2(request: Request, id: int, db: DbSession, header: RequireJson):
    return VehicleService.get_by_id_v2(db, id)

@app.post("/api/v2/vehicles", response_model=VehicleOutV2, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle_v2(request: Request, data: VehicleCreate, db: DbSession):
    v = VehicleService.create(db, data)
    return VehicleService.get_by_id_v2(db, v.id)

@app.put("/api/v2/vehicles/{id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def update_vehicle_v2(request: Request, id: int, data: VehicleUpdate, db: DbSession):
    VehicleService.update(db, id, data)
    return VehicleService.get_by_id_v2(db, id)

@app.delete("/api/v2/vehicles/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle_v2(request: Request, id: int, db: DbSession):
    VehicleService.delete(db, id)
    return None