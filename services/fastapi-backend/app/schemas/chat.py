"""
Chat-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    message: str
    message_type: str = "text"
    is_internal: bool = False
    metadata: Optional[str] = None


class ChatMessageCreate(ChatMessageBase):
    ticket_id: str


class ChatMessageInDB(ChatMessageBase):
    id: int
    ticket_id: str
    sender_id: Optional[int] = None
    is_ai_message: bool = False
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class ChatMessage(ChatMessageInDB):
    sender: Optional[Dict[str, Any]] = None


class ChatHistory(BaseModel):
    messages: List[ChatMessage]
    total: int


class AIResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = None
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None
