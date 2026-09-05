from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.model import Users
from app.schemas import UserRoles
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from uuid import UUID

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

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

        user_id = UUID(user_id)
        

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.scalar(select(Users).where(Users.user_id == user_id))

    if not user:
        raise credentials_exception

    return user

def requires_admin(current_user: Users = Depends(get_current_user)):

    if current_user.role is not UserRoles.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user
    