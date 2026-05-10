from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.dependencies import limiter
from app.controller import VehicleV1Controller, VehicleV2Controller, PositionController, FuelLogController

app = FastAPI(title="Vehicle Tracking API")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: Exception):
    return _rate_limit_exceeded_handler(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_content = exc.detail if isinstance(exc.detail, dict) else {
        "error":     "Client Error",
        "message":   exc.detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=exc.status_code, content=error_content)

@app.get("/health", tags=["Meta"])
def health_check():
    return {"status": "healthy"}


@app.get("/api/versions", tags=["Meta"])
@limiter.limit("100/minute")
def get_versions(request: Request):
    return {
        "versions": [
            {
                "version":    "v1",
                "deprecated": False,
                "sunset_date": None,
                "base_url":   "/api/v1",
            },
            {
                "version":     "v2",
                "deprecated":  False,
                "sunset_date": "2026-12-31",
                "base_url":    "/api/v2",
                "migration_guide": "/docs/v1-to-v2",
            },
        ]
    }

app.include_router(VehicleV1Controller.router)
app.include_router(VehicleV2Controller.router)
app.include_router(PositionController.router)
app.include_router(FuelLogController.router)