import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db

# rate limiter
limiter = Limiter(key_func=get_remote_address)

# credentials
VALID_API_KEY = os.getenv("API_KEY", "dev-secret-key")
VALID_TOKEN   = os.getenv("BEARER_TOKEN", "dev-bearer-token")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme  = HTTPBearer(auto_error=False)


def require_api_key(key: str = Security(api_key_header)) -> str:
    if key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


def require_bearer(creds: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> str:
    if not creds or creds.credentials != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    return creds.credentials


def verify_content_type(accept: str = Header(default="*/*")) -> None:
    if "application/json" not in accept and "*/*" not in accept:
        raise HTTPException(status_code=406, detail="Accept header must allow application/json")


DbSession   = Annotated[Session, Depends(get_db)]
RequireJson = Annotated[None, Depends(verify_content_type)]
ApiKey      = Annotated[str, Depends(require_api_key)]
BearerToken = Annotated[str, Depends(require_bearer)]