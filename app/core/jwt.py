from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "SECRET_KEY_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def _create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict):
    return _create_token(
        data,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(data: dict):
    return _create_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
