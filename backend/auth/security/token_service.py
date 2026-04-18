from auth.security.jwt_handler import create_access_token, create_refresh_token
from auth.config import settings
from auth.models.token import AccessToken, RefreshToken, Token, TokenResponse

def issue_service_token(service_name: str, scopes: list[str]) -> TokenResponse:
    data = {
        "sub": service_name,
        "token_type": None,
        "scope": scopes,
    }
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    # access_expires_in = settings.EXPIRE * 24 * 60 * 60
    # refresh_expires_in = settings.REFRESH_EXPIRE * 24 * 60 * 60
    access_expires_in = 60
    refresh_expires_in = 300
    
    return TokenResponse(
        access_token=access_token,
        access_token_expires_in=access_expires_in,
        refresh_token=refresh_token,
        refresh_token_expires_in=refresh_expires_in,
    )

def token(token_response: TokenResponse) -> Token:
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