
"""
Ticket management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.api.dependencies import get_db, get_current_user, require_engineer
from app.schemas.ticket import (
    Ticket, TicketCreate, TicketUpdate, TicketList, TicketStats, TicketFilters
)
from app.models.ticket import (
    Ticket as TicketModel, TicketStatus, TicketPriority, TicketCategory,
    TicketAttachment, TicketActivity, Tag
)
from app.models.user import User as UserModel
from app.services.ai_service import AIService
from app.services.file_service import FileService

router = APIRouter(prefix="/tickets", tags=["tickets"])


def generate_ticket_id() -> str:
    """Generate unique ticket ID in format INC-YYYYMMDD-NNNNN"""
    today = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4().int)[:5]
    return f"INC-{today}-{random_suffix}"


def calculate_sla_deadline(priority: TicketPriority, category: TicketCategory) -> datetime:
    """Calculate SLA deadline based on priority and category"""
    base_hours = {
        TicketPriority.CRITICAL: 2,
        TicketPriority.HIGH: 8,
        TicketPriority.MEDIUM: 24,
        TicketPriority.LOW: 72
    }
    
    hours = base_hours.get(priority, 24)
    
    # Adjust for category
    if category == TicketCategory.INCIDENT:
        hours = hours * 0.8  # Faster for incidents
    elif category == TicketCategory.CHANGE:
        hours = hours * 2    # Longer for changes
    
    return datetime.utcnow() + timedelta(hours=hours)


@router.post("/json", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket_json(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    # FIXME: This is a temporary solution for the ADK agent.
    # In a real-world scenario, you would want to have a secure way
    # for the agent to authenticate and get the current user.
    # For now, we will hardcode the user id.
):
    """
    Create a new ticket from a JSON payload.
    """
    # Hardcoded user for now
    user_id = 1 # Assuming user with id 1 exists (admin)

    # Generate ticket ID and calculate SLA
    ticket_id = generate_ticket_id()
    sla_deadline = calculate_sla_deadline(ticket_in.priority, ticket_in.category)
    
    # Use user's department if not specified, and validate that we have one.
    final_department_id = ticket_in.department_id
    if final_department_id is None:
        # Get department from user
        user = await db.get(UserModel, user_id)
        if user:
            final_department_id = user.department_id
    
    if final_department_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A department ID is required. Please provide one or ensure the user is assigned to a department."
        )
    
    # Create ticket
    db_ticket = TicketModel(
        id=ticket_id,
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        category=ticket_in.category,
        reported_by_id=user_id,
        department_id=final_department_id,
        sla_deadline=sla_deadline
    )
    
    db.add(db_ticket)
    await db.commit()
    
    # Add tags if provided
    if ticket_in.tags:
        from sqlalchemy import select
        for tag_name in ticket_in.tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            # Manually insert into association table to avoid lazy loading issues
            from app.models.ticket import ticket_tag_association
            stmt = ticket_tag_association.insert().values(ticket_id=db_ticket.id, tag_id=tag.id)
            await db.execute(stmt)
        await db.commit()

    # Log activity
    activity = TicketActivity(
        ticket_id=ticket_id,
        user_id=user_id,
        activity_type="created",
        details={"message": "Ticket created"}
    )
    db.add(activity)
    await db.commit()

    # Re-fetch the ticket with all relationships eagerly loaded for the response
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    result = await db.execute(
        select(TicketModel)
        .options(
            selectinload(TicketModel.reporter),
            selectinload(TicketModel.assignee),
            selectinload(TicketModel.department),
            selectinload(TicketModel.tags),
            selectinload(TicketModel.attachments),
            selectinload(TicketModel.activities)
        )
        .where(TicketModel.id == db_ticket.id)
    )
    return result.scalar_one()


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(),
    title: str = Form(...),
    description: str = Form(...),
    category: TicketCategory = Form(...),
    priority: TicketPriority = Form(TicketPriority.MEDIUM),
    department_id: Optional[int] = Form(None),
    tags: Optional[List[str]] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Create a new ticket, optionally including attachments in the same request.
    """
    # Generate ticket ID and calculate SLA
    ticket_id = generate_ticket_id()
    sla_deadline = calculate_sla_deadline(priority, category)
    
    # Use user's department if not specified, and validate that we have one.
    final_department_id = department_id or current_user.department_id
    if final_department_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A department ID is required. Please provide one or ensure the user is assigned to a department."
        )
    
    # Create ticket
    db_ticket = TicketModel(
        id=ticket_id,
        title=title,
        description=description,
        priority=priority,
        category=category,
        reported_by_id=current_user.id,
        department_id=final_department_id,
        sla_deadline=sla_deadline
    )
    
    db.add(db_ticket)
    await db.commit()
    
    # Add tags if provided
    if tags:
        from sqlalchemy import select
        for tag_name in tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            # Manually insert into association table to avoid lazy loading issues
            from app.models.ticket import ticket_tag_association
            stmt = ticket_tag_association.insert().values(ticket_id=db_ticket.id, tag_id=tag.id)
            await db.execute(stmt)
        await db.commit()

    # Handle file uploads if provided
    if files:
        for file in files:
            folder = f"ticket_attachments/{db_ticket.id}"
            file_info = await file_service.save_file(file=file, subfolder=folder)
            attachment = TicketAttachment(
                file_name=file.filename,
                file_path=file_info["file_path"],
                file_type=file_info["mime_type"],
                file_size=file_info["file_size"],
                ticket_id=db_ticket.id,
                uploaded_by_id=current_user.id
            )
            db.add(attachment)
        await db.commit()

    # Log activity
    activity = TicketActivity(
        ticket_id=ticket_id,
        user_id=current_user.id,
        activity_type="created",
        details={"message": "Ticket created"}
    )
    db.add(activity)
    await db.commit()

    # Re-fetch the ticket with all relationships eagerly loaded for the response
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    result = await db.execute(
        select(TicketModel)
        .options(
            selectinload(TicketModel.reporter),
            selectinload(TicketModel.assignee),
            selectinload(TicketModel.department),
            selectinload(TicketModel.tags),
            selectinload(TicketModel.attachments),
            selectinload(TicketModel.activities)
        )
        .where(TicketModel.id == db_ticket.id)
    )
    return result.scalar_one()


@router.get("/", response_model=TicketList)
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[List[TicketStatus]] = Query(None),
    priority: Optional[List[TicketPriority]] = Query(None),
    category: Optional[List[TicketCategory]] = Query(None),
    assigned_to_me: bool = Query(False),
    reported_by_me: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get tickets with filtering and pagination
    """
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select

    query = select(TicketModel).options(
        selectinload(TicketModel.reporter),
        selectinload(TicketModel.assignee),
        selectinload(TicketModel.department),
        selectinload(TicketModel.tags),
        selectinload(TicketModel.attachments),
        selectinload(TicketModel.activities)
    )
    
    # Apply filters based on user role
    if current_user.role.value == "end-user":
        # End users can only see their own tickets
        query = query.where(TicketModel.reported_by_id == current_user.id)
    elif assigned_to_me:
        query = query.where(TicketModel.assigned_to_id == current_user.id)
    elif reported_by_me:
        query = query.where(TicketModel.reported_by_id == current_user.id)
    
    # Apply other filters
    if status:
        query = query.where(TicketModel.status.in_(status))
    if priority:
        query = query.where(TicketModel.priority.in_(priority))
    if category:
        query = query.where(TicketModel.category.in_(category))
    if search:
        query = query.where(
            or_(
                TicketModel.title.ilike(f"%{search}%"),
                TicketModel.description.ilike(f"%{search}%"),
                TicketModel.id.ilike(f"%{search}%")
            )
        )
    
    # Order by priority and creation date
    query = query.order_by(
        TicketModel.priority.desc(),
        TicketModel.created_at.desc()
    )
    
    total_query = await db.execute(query)
    total = len(total_query.fetchall())
    
    result = await db.execute(query.offset(skip).limit(limit))
    tickets = result.scalars().all()
    
    return {
        "tickets": tickets,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get ticket by ID
    """
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select

    result = await db.execute(
        select(TicketModel)
        .options(
            selectinload(TicketModel.reporter),
            selectinload(TicketModel.assignee),
            selectinload(TicketModel.department),
            selectinload(TicketModel.tags),
            selectinload(TicketModel.attachments),
            selectinload(TicketModel.activities)
        )
        .where(TicketModel.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if (current_user.role.value == "end-user" and 
        ticket.reported_by_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update ticket
    """
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    can_update = (
        current_user.role.value in ["l1-engineer", "l2-engineer", "ops-manager", "admin"] or
        (current_user.role.value == "end-user" and ticket.reported_by_id == current_user.id)
    )
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Track changes for activity log
    changes = {}
    update_data = ticket_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        old_value = getattr(ticket, field)
        if old_value != value:
            changes[field] = {"old": old_value, "new": value}
            await db.execute(TicketModel.__table__.update().where(TicketModel.id == ticket_id).values(**{field: value}))
    
    # Set resolved timestamp if status changed to resolved
    if ticket_update.status == TicketStatus.RESOLVED and ticket.status != TicketStatus.RESOLVED:
        await db.execute(TicketModel.__table__.update().where(TicketModel.id == ticket_id).values(resolved_at=datetime.utcnow()))
    
    await db.commit()
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    
    # Log activity if there were changes
    if changes:
        activity = TicketActivity(
            ticket_id=ticket_id,
            user_id=current_user.id,
            activity_type="updated",
            details={"changes": changes}
        )
        db.add(activity)
        await db.commit()
    
    return ticket


@router.post("/{ticket_id}/attachments", response_model=Ticket)
async def upload_attachment(
    ticket_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends()
):
    """
    Upload one or more attachments to an existing ticket.
    """
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Permission check: User can only upload to their own tickets, unless they are staff
    is_reporter = ticket.reported_by_id == current_user.id
    is_staff = current_user.role.value in ["l1-engineer", "l2-engineer", "ops-manager", "admin"]
    if not is_reporter and not is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload attachments to this ticket."
        )

    for file in files:
        # Upload file using the file service
        folder = f"ticket_attachments/{ticket.id}"
        file_info = await file_service.save_file(file=file, subfolder=folder)

        # Create a new TicketAttachment record
        attachment = TicketAttachment(
            file_name=file.filename,
            file_path=file_info["file_path"],
            file_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            ticket_id=ticket.id,
            uploaded_by_id=current_user.id
        )
        db.add(attachment)

    await db.commit()
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()

    return ticket





@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    assignee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_engineer)
):
    """
    Assign ticket to an engineer
    """
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Verify assignee exists and is an engineer
    assignee_query = await db.execute(UserModel.__table__.select().where(UserModel.id == assignee_id))
    assignee = assignee_query.first()
    if not assignee or assignee.role.value not in ["l1-engineer", "l2-engineer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assignee"
        )
    
    old_assignee_id = ticket.assigned_to_id
    await db.execute(TicketModel.__table__.update().where(TicketModel.id == ticket_id).values(assigned_to_id=assignee_id, status=TicketStatus.IN_PROGRESS))
    
    await db.commit()
    
    # Log activity
    activity = TicketActivity(
        ticket_id=ticket_id,
        user_id=current_user.id,
        activity_type="assigned",
        details={
            "old_assignee_id": old_assignee_id,
            "new_assignee_id": assignee_id,
            "assignee_name": assignee.name
        }
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Ticket assigned successfully"}


@router.post("/{ticket_id}/escalate")
async def escalate_ticket(
    ticket_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Escalate ticket to L2 or management
    """
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await db.execute(TicketModel.__table__.update().where(TicketModel.id == ticket_id).values(status=TicketStatus.ESCALATED, escalation_reason=reason, is_escalated=True, assigned_to_id=None))
    
    await db.commit()
    
    # Log activity
    activity = TicketActivity(
        ticket_id=ticket_id,
        user_id=current_user.id,
        activity_type="escalated",
        details={"reason": reason}
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Ticket escalated successfully"}


@router.get("/stats/overview", response_model=TicketStats)
async def get_ticket_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get ticket statistics overview
    """
    query = TicketModel.__table__.select()
    
    # Filter by user role
    if current_user.role.value == "end-user":
        query = query.where(TicketModel.reported_by_id == current_user.id)
    elif current_user.role.value in ["l1-engineer", "l2-engineer"]:
        query = query.where(TicketModel.assigned_to_id == current_user.id)
    
    total_tickets_query = await db.execute(query)
    total_tickets = len(total_tickets_query.fetchall())
    open_tickets_query = await db.execute(query.where(TicketModel.status == TicketStatus.OPEN))
    open_tickets = len(open_tickets_query.fetchall())
    in_progress_tickets_query = await db.execute(query.where(TicketModel.status == TicketStatus.IN_PROGRESS))
    in_progress_tickets = len(in_progress_tickets_query.fetchall())
    resolved_tickets_query = await db.execute(query.where(TicketModel.status == TicketStatus.RESOLVED))
    resolved_tickets = len(resolved_tickets_query.fetchall())
    closed_tickets_query = await db.execute(query.where(TicketModel.status == TicketStatus.CLOSED))
    closed_tickets = len(closed_tickets_query.fetchall())
    escalated_tickets_query = await db.execute(query.where(TicketModel.status == TicketStatus.ESCALATED))
    escalated_tickets = len(escalated_tickets_query.fetchall())
    
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "escalated_tickets": escalated_tickets,
        "avg_resolution_time": 2.5,  # Mock data - calculate from actual data
        "sla_compliance_rate": 94.5   # Mock data - calculate from actual data
    }


@router.post("/{ticket_id}/analyze")
async def analyze_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_engineer)
):
    """
    Get AI analysis for a ticket
    """
    ticket_query = await db.execute(TicketModel.__table__.select().where(TicketModel.id == ticket_id))
    ticket = ticket_query.first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ai_service = AIService()
    analysis = await ai_service.analyze_ticket(ticket_id, db)
    
    return analysis
