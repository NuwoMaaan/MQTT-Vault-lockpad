from auth.config import settings
from fastapi import HTTPException, status
from datetime import datetime, UTC, timedelta
import jwt

SECRET_KEY = settings.JWT_SECRET_KEY
EXPIRE = settings.EXPIRE
REFRESH_EXPIRE = settings.REFRESH_EXPIRE
ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=EXPIRE)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    expire = datetime.now(UTC) + timedelta(days=REFRESH_EXPIRE)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expire")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
