"""
Ticket-related models
"""
from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey, Text, Table, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# Association table for ticket tags
ticket_tag_association = Table(
    "ticket_tag_association",
    Base.metadata,
    Column("ticket_id", String, ForeignKey("tickets.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"
    ON_HOLD = "on-hold"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, enum.Enum):
    INCIDENT = "incident"
    SERVICE_REQUEST = "service-request"
    PROBLEM = "problem"
    CHANGE = "change"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    SECURITY = "security"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True)  # Custom ID format: INC-YYYYMMDD-NNNNN
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    sla_deadline = Column(DateTime(timezone=True), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    resolution = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    melt_data = Column(JSON, nullable=True)  # Metrics, Events, Logs, Traces data
    customer_satisfaction = Column(Integer, nullable=True)  # 1-5 rating
    is_escalated = Column(Boolean, default=False)

    # Relationships
    reporter = relationship("User", back_populates="reported_tickets", foreign_keys=[reported_by_id])
    assignee = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_to_id])
    department = relationship("Department", back_populates="tickets")
    tags = relationship("Tag", secondary=ticket_tag_association, back_populates="tickets")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="ticket", cascade="all, delete-orphan")
    activities = relationship("TicketActivity", back_populates="ticket", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=True)  # Hex color code
    
    # Relationships
    tickets = relationship("Ticket", secondary=ticket_tag_association, back_populates="tags")


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    uploaded_by = relationship("User")


class TicketActivity(Base):
    __tablename__ = "ticket_activities"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # e.g., "status_change", "comment", "assignment"
    details = Column(JSON, nullable=False)  # Store activity details as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="activities")
    user = relationship("User", back_populates="ticket_activities")
