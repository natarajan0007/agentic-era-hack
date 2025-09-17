"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.dependencies import get_db, get_current_user, require_manager, require_admin
from app.schemas.user import User, UserCreate, UserUpdate, UserList, UserWithStats, Department as DepartmentSchema, DepartmentBase
from app.models.user import User as UserModel, Department as DepartmentModel
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get list of users with filtering and pagination
    """
    query = db.query(UserModel)
    
    if role:
        query = query.filter(UserModel.role == role)
    if department_id:
        query = query.filter(UserModel.department_id == department_id)
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "users": users,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user by ID
    """
    # Users can only view their own profile unless they're a manager
    if user_id != current_user.id and current_user.role.value not in ["ops-manager", "transition-manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update user information
    """
    # Users can only update their own profile unless they're a manager
    if user_id != current_user.id and current_user.role.value not in ["ops-manager", "transition-manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/stats", response_model=UserWithStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get user performance statistics
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate stats (simplified - in production use proper analytics)
    from app.models.ticket import Ticket, TicketStatus
    
    assigned_tickets = db.query(Ticket).filter(Ticket.assigned_to_id == user_id).count()
    resolved_tickets = db.query(Ticket).filter(
        Ticket.assigned_to_id == user_id,
        Ticket.status == TicketStatus.RESOLVED
    ).count()
    
    # Convert user to dict and add stats
    user_dict = {
        **user.__dict__,
        "tickets_assigned_count": assigned_tickets,
        "tickets_resolved_count": resolved_tickets,
        "avg_resolution_time": 2.5,  # Mock data
        "sla_compliance_rate": 95.0   # Mock data
    }
    
    return user_dict


@router.get("/departments/", response_model=List[DepartmentSchema])
def get_departments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of departments
    """
    departments = db.query(DepartmentModel).all()
    return departments


@router.post("/departments/", response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
def create_department(
    department_in: DepartmentBase,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Create a new department. Only accessible by admin users.
    """
    existing_department = db.query(DepartmentModel).filter(DepartmentModel.name == department_in.name).first()
    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with name '{department_in.name}' already exists."
        )
    db_department = DepartmentModel(**department_in.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department