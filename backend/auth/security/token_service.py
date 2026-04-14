from auth.security.jwt_handler import create_access_token

def issue_service_token(service_name: str, scopes: list[str]) -> str:
    data = {
        "sub": service_name,
        "token_type": "service",
        "scope": scopes,
    }
    return create_access_token(data)