"""
API dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token, check_permissions
from app.models.user import User
from app.schemas.user import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def require_roles(allowed_roles: list):
    """
    Dependency factory for role-based access control
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if not check_permissions(current_user.role.value, allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Common role dependencies
require_engineer = require_roles(["l1-engineer", "l2-engineer", "ops-manager", "admin"])
require_l2_or_above = require_roles(["l2-engineer", "ops-manager", "admin"])
require_manager = require_roles(["ops-manager", "transition-manager", "admin"])
require_admin = require_roles(["admin"])
