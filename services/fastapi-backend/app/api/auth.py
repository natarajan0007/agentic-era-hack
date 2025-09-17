"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Any

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import User, Token, UserCreate
from app.models.user import User as UserModel
import logging
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",  # This should match your login endpoint URL
    scheme_name="JWT"
)

router = APIRouter(prefix="/auth", tags=["authentication"])



@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    logging.info(f"Attempting login for user: {form_data.username}")
    user_query = await db.execute(UserModel.__table__.select().where(UserModel.email == form_data.username))
    user = user_query.first()
    if user:
        print(f"User found: {user.email}")
        print(f"Hashed password from DB: {user.hashed_password}")
        print(f"Type of hashed password: {type(user.hashed_password)}")
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    await db.execute(UserModel.__table__.update().where(UserModel.id == user.id).values(last_login=datetime.utcnow()))
    await db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
    await db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Register a new user.
    """
    # Check if user with this email already exists
    user = await db.execute(UserModel.__table__.select().where(UserModel.email == user_in.email))
    user = user.first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    # Validate department_id if provided
    department_id = user_in.department_id
    if department_id is not None:
        from app.models.user import Department
        department = await db.execute(Department.__table__.select().where(Department.id == department_id))
        department = department.first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with id {department_id} does not exist"
            )
    
    # Create new user
    db_user = UserModel(
        email=user_in.email,
        name=user_in.name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        avatar=user_in.avatar,
        phone=user_in.phone,
        department_id=department_id,
        manager_id=user_in.manager_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserModel = Depends(get_current_user)):
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(current_user.id), "role": current_user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": current_user
    }


@router.post("/logout")
async def logout(current_user: UserModel = Depends(get_current_user)):
    """
    Logout user (client should discard token)
    """
    return {"message": "Successfully logged out"}
