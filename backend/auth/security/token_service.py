from auth.security.jwt_handler import create_access_token

def issue_service_token(service_name: str):
    data = {
        "service": service_name,
        "role": "service"
    }

    return create_access_token(data)