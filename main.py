import os
from typing import Annotated
from fastapi import FastAPI, Request, Depends, HTTPException, Header, status, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from datetime import datetime, timezone

from app.database import get_db
from app.service import VehicleService, PositionService, FuelLogService
from app.dto.VehicleDto import VehicleCreate, VehicleUpdate, VehicleOut, VehicleOutV2
from app.dto.PositionDto import PositionCreate, PositionOut
from app.dto.FuelLogDto import FuelLogCreate, FuelLogOut

# ==========================================
# 1. SECURITY SETUP (Task 1 Requirement)
# ==========================================
VALID_API_KEY = os.getenv("API_KEY", "dev-secret-key")
VALID_TOKEN   = os.getenv("BEARER_TOKEN", "dev-bearer-token")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme  = HTTPBearer(auto_error=False)

def require_api_key(key: str = Security(api_key_header)):
    if key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key

def require_bearer(creds: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if not creds or creds.credentials != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    return creds.credentials


# ==========================================
# 2. APP & RATE LIMITER SETUP
# ==========================================
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Vehicle Tracking API")
app.state.limiter = limiter

# FIX: Let SlowAPI handle X-RateLimit headers dynamically!
app.add_middleware(SlowAPIMiddleware)

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


# ==========================================
# 3. META ENDPOINTS (Unsecured)
# ==========================================
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/versions")
@limiter.limit("100/minute")
def get_versions(request: Request):
    return {
        "versions": [
            {"version": "v1", "deprecated": False, "sunset_date": None, "base_url": "/api/v1"},
            {"version": "v2", "deprecated": False, "sunset_date": "2026-12-31", "base_url": "/api/v2",
             "migration_guide": "/docs/v1-to-v2"}
        ]
    }


# ==========================================
# 4. V1 ENDPOINTS (Requires API Key)
# ==========================================
@app.get("/api/v1/vehicles", response_model=list[VehicleOut])
@limiter.limit("100/minute")
def list_vehicles_v1(request: Request, db: DbSession, header: RequireJson, skip: int = 0, limit: int = 100, api_key: str = Depends(require_api_key)):
    return VehicleService.get_all(db, skip=skip, limit=limit)

@app.post("/api/v1/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle_v1(request: Request, data: VehicleCreate, db: DbSession, header: RequireJson, api_key: str = Depends(require_api_key)):
    return VehicleService.create(db, data)

@app.get("/api/v1/vehicles/{id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def get_vehicle_v1(request: Request, id: int, db: DbSession, header: RequireJson, api_key: str = Depends(require_api_key)):
    return VehicleService.get_by_id(db, id)

@app.put("/api/v1/vehicles/{id}", response_model=VehicleOut)
@limiter.limit("100/minute")
def update_vehicle_v1(request: Request, id: int, data: VehicleUpdate, db: DbSession, header: RequireJson, api_key: str = Depends(require_api_key)):
    return VehicleService.update(db, id, data)

@app.delete("/api/v1/vehicles/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle_v1(request: Request, id: int, db: DbSession, api_key: str = Depends(require_api_key)):
    VehicleService.delete(db, id)
    return None

@app.post("/api/v1/vehicles/{id}/positions", response_model=PositionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_position(request: Request, id: int, data: PositionCreate, db: DbSession, api_key: str = Depends(require_api_key)):
    return PositionService.log_position(db, id, data)

@app.get("/api/v1/vehicles/{id}/positions/latest", response_model=PositionOut)
@limiter.limit("100/minute")
def get_latest_position(request: Request, id: int, db: DbSession, api_key: str = Depends(require_api_key)):
    return PositionService.get_latest(db, id)

@app.post("/api/v1/vehicles/{id}/fuel", response_model=FuelLogOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def log_fuel(request: Request, id: int, data: FuelLogCreate, db: DbSession, api_key: str = Depends(require_api_key)):
    return FuelLogService.log_fuel(db, id, data)

@app.get("/api/v1/vehicles/{id}/fuel", response_model=list[FuelLogOut])
@limiter.limit("100/minute")
def get_fuel_history(request: Request, id: int, db: DbSession, api_key: str = Depends(require_api_key)):
    return FuelLogService.get_history(db, id)


# ==========================================
# 5. V2 ENDPOINTS (Requires Bearer Token)
# ==========================================
@app.get("/api/v2/vehicles", response_model=list[VehicleOutV2])
@limiter.limit("100/minute")
def list_vehicles_v2(request: Request, db: DbSession, header: RequireJson, skip: int = 0, limit: int = 100, token: str = Depends(require_bearer)):
    return VehicleService.get_all_v2(db, skip=skip, limit=limit)

@app.get("/api/v2/vehicles/{id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def get_vehicle_v2(request: Request, id: int, db: DbSession, header: RequireJson, token: str = Depends(require_bearer)):
    return VehicleService.get_by_id_v2(db, id)

@app.post("/api/v2/vehicles", response_model=VehicleOutV2, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def create_vehicle_v2(request: Request, data: VehicleCreate, db: DbSession, token: str = Depends(require_bearer)):
    v = VehicleService.create(db, data)
    return VehicleService.get_by_id_v2(db, v.id)

@app.put("/api/v2/vehicles/{id}", response_model=VehicleOutV2)
@limiter.limit("100/minute")
def update_vehicle_v2(request: Request, id: int, data: VehicleUpdate, db: DbSession, token: str = Depends(require_bearer)):
    VehicleService.update(db, id, data)
    return VehicleService.get_by_id_v2(db, id)

@app.delete("/api/v2/vehicles/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
def delete_vehicle_v2(request: Request, id: int, db: DbSession, token: str = Depends(require_bearer)):
    VehicleService.delete(db, id)
    return None