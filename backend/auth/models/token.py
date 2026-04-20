from pydantic import BaseModel

class AccessToken(BaseModel):
    token: str
    expires_in: int

class RefreshToken(BaseModel):
    token: str
    expires_in: int

class Token(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken
    token_type: str = "bearer"

class TokenResponse(BaseModel):
    access_token: str
    access_token_expires_in: int
    refresh_token: str
    refresh_token_expires_in: int