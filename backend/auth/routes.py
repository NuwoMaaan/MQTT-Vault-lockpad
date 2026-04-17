from fastapi import APIRouter, HTTPException, status, Header, Depends
from auth.models.token import Token, AccessToken, RefreshToken
from auth.models.token_response import TokenResponse
from auth.security.token_service import issue_service_token
from auth.security.dependencies import require_refresh_token
from auth.security.auth_api import verify_api_key
from auth.config import settings
from auth.models.permissions import BleScopes

API_KEY = settings.API_KEY
router = APIRouter()

@router.post("/ble/token", response_model=Token)
def create_token(
    x_api_key: str = Header(..., alias="X-API-Key"),
    service: str = Header(..., alias="X-Service-Name")
    ):
    if not verify_api_key(x_api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    token_response: TokenResponse = issue_service_token(service, scopes=[BleScopes.READ, BleScopes.WRITE])
    
    return Token(
        access_token=AccessToken(
            token=token_response.access_token,
            expires_in=token_response.access_token_expires_in
        ),
        refresh_token=RefreshToken(
            token=token_response.refresh_token,
            expires_in=token_response.refresh_token_expires_in
        )
    )

@router.post("/token/refresh", response_model=Token)
def refresh_token(
    payload: dict = Depends(require_refresh_token)
    ):
    service_name = payload.get("sub")
    scopes = payload.get("scope", [])
    
    token_response = issue_service_token(service_name, scopes=scopes)
    
    return Token(
        access_token=AccessToken(
            token=token_response.access_token,
            expires_in=token_response.access_token_expires_in
        ),
        refresh_token=RefreshToken(
            token=token_response.refresh_token,
            expires_in=token_response.refresh_token_expires_in
        )
    )