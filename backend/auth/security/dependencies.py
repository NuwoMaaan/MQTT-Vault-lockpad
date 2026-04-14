from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.security.jwt_handler import verify_token
from auth.models.permissions import Scope


security = HTTPBearer()

def require_scope(required_scope: Scope):
    required_scope = str(required_scope)

    def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        token = credentials.credentials
        payload = verify_token(token)

        scopes = payload.get("scope", [])
        token_type = payload.get("token_type")

        if token_type != "service":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type"
            )

        if required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return payload

    return dependency