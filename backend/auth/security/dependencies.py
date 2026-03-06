from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.security.jwt_handler import verify_token

security = HTTPBearer()

def require_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    token = credentials.credentials
    payload = verify_token(token)
    return payload