from fastapi import APIRouter, HTTPException, status, Header
from auth.models.token import Token
from auth.security.token_service import issue_service_token
from auth.security.auth_api import verify_api_key
from auth.config import settings

API_KEY = settings.API_KEY
router = APIRouter()

@router.post("/token", response_model=Token)
def create_token(
    x_api_key: str = Header(..., alias="X-API-Key"),
    service: str = Header(..., alias="X-Service-Name")
    ):
    if not verify_api_key(x_api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    jwt_token = issue_service_token(service)
    return Token(access_token=jwt_token)