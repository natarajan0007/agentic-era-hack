"""
Ticket-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority, TicketCategory
from app.schemas.user import User, Department


class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class Tag(TagBase):
    id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class TicketAttachmentBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int


class TicketAttachment(TicketAttachmentBase):
    id: int
    file_path: str
    uploaded_at: datetime
    uploaded_by_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class TicketActivityBase(BaseModel):
    activity_type: str
    details: Dict[str, Any]


class TicketActivity(TicketActivityBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    priority: TicketPriority = TicketPriority.MEDIUM
    category: TicketCategory


class TicketCreate(TicketBase):
    department_id: Optional[int] = None
    tags: Optional[List[str]] = []
    melt_data: Optional[Dict[str, Any]] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[int] = None
    resolution: Optional[str] = None
    escalation_reason: Optional[str] = None
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)


class TicketInDB(TicketBase):
    id: str
    status: TicketStatus
    reported_by_id: int
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    sla_deadline: datetime
    department_id: int
    resolution: Optional[str] = None
    escalation_reason: Optional[str] = None
    melt_data: Optional[Dict[str, Any]] = None
    customer_satisfaction: Optional[int] = None
    is_escalated: bool = False

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class Ticket(TicketInDB):
    reporter: Optional[User] = None
    assignee: Optional[User] = None
    department: Optional[Department] = None
    tags: List[Tag] = []
    attachments: List[TicketAttachment] = []
    activities: List[TicketActivity] = []


class TicketList(BaseModel):
    tickets: List[Ticket]
    total: int
    page: int
    size: int


class TicketStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    escalated_tickets: int
    avg_resolution_time: Optional[float] = None
    sla_compliance_rate: Optional[float] = None


class TicketFilters(BaseModel):
    status: Optional[List[TicketStatus]] = None
    priority: Optional[List[TicketPriority]] = None
    category: Optional[List[TicketCategory]] = None
    assigned_to_id: Optional[int] = None
    reported_by_id: Optional[int] = None
    department_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
