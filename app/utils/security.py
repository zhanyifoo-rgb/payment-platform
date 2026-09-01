from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from jose import jwt
from app.config import settings

def hash_password(user_input_password: str) -> str:
    password_hash = PasswordHash.recommended()

    return password_hash.hash(user_input_password)


def verify_password(user_input_password: str, stored_password_hash:str):
    password_hash = PasswordHash.recommended()

    return password_hash.verify(user_input_password,stored_password_hash)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )