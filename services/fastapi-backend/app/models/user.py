"""
User and Department models
"""
from sqlalchemy import Column, String, Integer, Boolean, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    END_USER = "end-user"
    L1_ENGINEER = "l1-engineer"
    L2_ENGINEER = "l2-engineer"
    OPS_MANAGER = "ops-manager"
    TRANSITION_MANAGER = "transition-manager"
    ADMIN = "admin"


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="department")
    tickets = relationship("Ticket", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    avatar = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    department = relationship("Department", back_populates="users")
    manager = relationship("User", remote_side=[id], back_populates="reports")
    reports = relationship("User", back_populates="manager")
    
    reported_tickets = relationship(
        "Ticket", 
        back_populates="reporter", 
        foreign_keys="Ticket.reported_by_id"
    )
    assigned_tickets = relationship(
        "Ticket", 
        back_populates="assignee", 
        foreign_keys="Ticket.assigned_to_id"
    )
    knowledge_articles = relationship("KnowledgeArticle", back_populates="author")
    chat_messages = relationship("ChatMessage", back_populates="sender")
    ticket_activities = relationship("TicketActivity", back_populates="user")
