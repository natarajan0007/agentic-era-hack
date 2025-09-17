"""
Chat message models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for AI messages
    message = Column(Text, nullable=False)
    is_ai_message = Column(Boolean, default=False)
    message_type = Column(String, default="text")  # text, image, file, system
    metainfo = Column(String, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_internal = Column(Boolean, default=False)  # Internal notes vs customer-facing

    # Relationships
    ticket = relationship("Ticket", back_populates="chat_messages")
    sender = relationship("User", back_populates="chat_messages")
