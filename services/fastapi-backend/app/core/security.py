"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def check_permissions(user_role: str, required_roles: list) -> bool:
    """
    Check if user has required permissions
    """
    role_hierarchy = {
        "end-user": 1,
        "l1-engineer": 2,
        "l2-engineer": 3,
        "ops-manager": 4,
        "transition-manager": 4,
        "admin": 5
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = min([role_hierarchy.get(role, 5) for role in required_roles])
    
    return user_level >= required_level
