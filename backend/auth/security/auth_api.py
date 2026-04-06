import secrets

def verify_api_key(api_key: str, API_KEY: str) -> bool:
    return secrets.compare_digest(api_key, API_KEY)