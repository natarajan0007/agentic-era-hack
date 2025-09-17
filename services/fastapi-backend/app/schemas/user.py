"""
User-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class Department(DepartmentBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    avatar: Optional[str] = None
    phone: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    department_id: Optional[int] = None
    manager_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    department_id: Optional[int] = None
    department: Optional[Department] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class User(UserInDB):
    pass


class UserWithStats(User):
    tickets_assigned_count: int = 0
    tickets_resolved_count: int = 0
    avg_resolution_time: Optional[float] = None  # in hours
    sla_compliance_rate: Optional[float] = None  # percentage


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenPayload(BaseModel):
    sub: int  # user_id
    role: str
    exp: int  # expiration time


class UserList(BaseModel):
    users: List[User]
    total: int
    page: int
    size: int
