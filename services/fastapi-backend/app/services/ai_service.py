"""
AI integration service for intelligent assistance using a provider-based model.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import KnowledgeArticle
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)

# --- Helper functions for fallback logic ---

def _get_fallback_chat_response(user_message: str, user_role: str) -> str:
    """Generate a fallback chat response when an AI service is not available."""
    message_lower = user_message.lower()
    if "password" in message_lower:
        return "For password issues, please try resetting your password through the self-service portal."
    if "login" in message_lower:
        return "For login problems, please check your credentials and clear your browser cache."
    if "printer" in message_lower:
        return "For printer issues, please ensure the printer is on and connected to the network."
    if user_role in ["l1-engineer", "l2-engineer"]:
        return "I can help with ticket analysis. Please provide more details about the issue."
    return "I'm here to help! Please describe your IT issue in detail."

def _get_fallback_suggestions(ticket: Ticket) -> List[Dict[str, Any]]:
    """Generate fallback resolution suggestions based on ticket category."""
    if "login" in ticket.title.lower() or "password" in ticket.title.lower():
        return [{"title": "Password Reset", "description": "Reset user password via Active Directory.", "confidence": 85}]
    if "network" in ticket.title.lower() or "internet" in ticket.title.lower():
        return [{"title": "Network Connectivity Test", "description": "Run ping and traceroute tests.", "confidence": 85}]
    return [{"title": "Basic Troubleshooting", "description": "Restart the affected application or service.", "confidence": 60}]


# --- AI Provider Interface (Abstract Base Class) ---

class AIProvider(ABC):
    """Abstract interface for an AI provider."""
    @abstractmethod
    async def generate_chat_response(self, messages: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    async def generate_resolution_suggestions(self, ticket: Ticket) -> List[Dict[str, Any]]:
        pass


# --- Concrete Provider Implementations ---

class GeminiProvider(AIProvider):
    """AI Provider implementation for Google Gemini."""
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini AI Provider initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Provider: {e}")
            raise

    async def generate_chat_response(self, messages: List[Dict[str, Any]]) -> str:
        # Gemini uses a different format than OpenAI, this adapts it.
        # It prefers a simple list of strings for history in this context.
        prompt = "\n".join([msg['content'] for msg in messages])
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat response error: {e}")
            return "Error communicating with the AI service."

    async def generate_resolution_suggestions(self, ticket: Ticket) -> List[Dict[str, Any]]:
        # For now, the Gemini provider will use the fallback for structured suggestions
        # as parsing LLM responses for structured data is complex and error-prone without more robust logic.
        return _get_fallback_suggestions(ticket)


class FallbackProvider(AIProvider):
    """Provider that gives static, rule-based responses when no AI service is configured."""
    def __init__(self):
        logger.info("Fallback AI Provider initialized.")

    async def generate_chat_response(self, messages: List[Dict[str, Any]]) -> str:
        user_message = messages[-1]['content'] if messages else ""
        # A simple way to get user_role, though not perfectly clean
        system_prompt = messages[0]['content'] if messages and messages[0]['role'] == 'system' else ""
        user_role = "end-user" # default
        if "L1 support" in system_prompt:
            user_role = "l1-engineer"
        return _get_fallback_chat_response(user_message, user_role)

    async def generate_resolution_suggestions(self, ticket: Ticket) -> List[Dict[str, Any]]:
        return _get_fallback_suggestions(ticket)


# --- Main AIService Class (Factory) ---

class AIService:
    """A factory class that selects and uses an AI provider based on configuration."""
    def __init__(self):
        self.provider: AIProvider
        if settings.GEMINI_API_KEY:
            self.provider = GeminiProvider()
        else:
            self.provider = FallbackProvider()

    async def generate_chat_response(self, user_message: str, chat_history: List[Dict[str, Any]], user_role: str, ticket_id: Optional[str] = None, db: Optional[Session] = None) -> str:
        system_prompt = self._get_system_prompt_by_role(user_role)
        if ticket_id and db:
            ticket_context = self._get_ticket_context(ticket_id, db)
            system_prompt += f"\n\nTicket Context: {ticket_context}"
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history:
            role = "assistant" if msg["sender"] == "ai" else "user"
            messages.append({"role": role, "content": msg["message"]})
        messages.append({"role": "user", "content": user_message})
        
        return await self.provider.generate_chat_response(messages)

    async def analyze_ticket(self, ticket_id: str, db: Session) -> Dict[str, Any]:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}
        
        resolution_suggestions = await self.provider.generate_resolution_suggestions(ticket)
        
        return {
            "similar_tickets": self._find_similar_tickets(ticket, db),
            "relevant_articles": self._find_relevant_knowledge(ticket, db),
            "resolution_suggestions": resolution_suggestions,
            "estimated_resolution_time": self._estimate_resolution_time(ticket),
            "escalation_recommendation": self._should_escalate(ticket)
        }

    # The helper methods below are independent of the AI provider
    def _get_system_prompt_by_role(self, user_role: str) -> str:
        prompts = {
            "end-user": "You are an AI assistant for the Intellica IT support platform. Help users report IT issues clearly and provide basic troubleshooting guidance.",
            "l1-engineer": "You are an AI assistant for L1 support engineers. Help with ticket analysis, finding similar issues, and suggesting solutions.",
            "l2-engineer": "You are an AI assistant for L2 technical specialists. Help with complex troubleshooting and root cause analysis.",
            "ops-manager": "You are an AI assistant for IT operations managers. Help with team performance analysis, SLA monitoring, and operational insights."
        }
        return prompts.get(user_role, "You are a helpful IT support assistant.")

    def _get_ticket_context(self, ticket_id: str, db: Session) -> str:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket: return "No ticket information available."
        context = f"Ticket ID: {ticket.id}\nTitle: {ticket.title}\nDescription: {ticket.description}\nStatus: {ticket.status}\nPriority: {ticket.priority}"
        return context

    def _find_similar_tickets(self, ticket: Ticket, db: Session) -> List[Dict[str, Any]]:
        # This is a placeholder for a real vector search implementation
        return []

    def _extract_keywords(self, text: str) -> List[str]:
        words = text.lower().split()
        stopwords = {"the", "a", "an", "in", "on", "is", "are", "and"}
        return [w for w in words if w not in stopwords and len(w) > 3]

    def _find_relevant_knowledge(self, ticket: Ticket, db: Session) -> List[Dict[str, Any]]:
        # This is a placeholder for a real vector search implementation
        return []

    def _estimate_resolution_time(self, ticket: Ticket) -> Dict[str, Any]:
        base_times = {TicketPriority.CRITICAL: 2, TicketPriority.HIGH: 4, TicketPriority.MEDIUM: 8, TicketPriority.LOW: 24}
        estimated_hours = base_times.get(ticket.priority, 8)
        return {"estimated_hours": round(estimated_hours, 1), "confidence": 75}

    def _should_escalate(self, ticket: Ticket) -> Dict[str, Any]:
        escalation_score = 0
        if ticket.priority == TicketPriority.CRITICAL: escalation_score += 40
        return {"should_escalate": escalation_score >= 50, "escalation_score": escalation_score}