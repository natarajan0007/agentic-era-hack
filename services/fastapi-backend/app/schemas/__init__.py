"""
Pydantic schemas for request/response models
"""
from .user import User, UserCreate, UserUpdate, Token
from .ticket import Ticket, TicketCreate, TicketUpdate
from .chat import ChatMessage, ChatMessageCreate
from .knowledge import KnowledgeArticleResponse as KnowledgeArticle, KnowledgeArticleCreate
from .analytics import AnalyticsData, SystemMetrics

__all__ = [
    "User",
    "UserCreate", 
    "UserUpdate",
    "Token",
    "Ticket",
    "TicketCreate",
    "TicketUpdate",
    "ChatMessage",
    "ChatMessageCreate",
    "KnowledgeArticle",
    "KnowledgeArticleCreate",
    "AnalyticsData",
    "SystemMetrics"
]
