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

