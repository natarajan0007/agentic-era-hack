"""
Chat and messaging endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from app.api.dependencies import get_db, get_current_user
from app.schemas.chat import ChatMessage, ChatMessageCreate, ChatHistory, AIResponse
from app.models.chat import ChatMessage as ChatMessageModel
from app.models.ticket import Ticket as TicketModel
from app.models.user import User as UserModel
from app.services.ai_service import AIService
from app.utils.websocket_manager import WebSocketManager

router = APIRouter(prefix="/chat", tags=["chat"])
websocket_manager = WebSocketManager()


@router.post("/", response_model=ChatMessage, status_code=status.HTTP_201_CREATED)
def send_message(
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Send a chat message
    """
    # Verify ticket exists and user has access
    ticket = db.query(TicketModel).filter(TicketModel.id == message_in.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    can_chat = (
        current_user.role.value in ["l1-engineer", "l2-engineer", "ops-manager", "admin"] or
        ticket.reported_by_id == current_user.id or
        ticket.assigned_to_id == current_user.id
    )
    
    if not can_chat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create message
    db_message = ChatMessageModel(
        ticket_id=message_in.ticket_id,
        sender_id=current_user.id,
        message=message_in.message,
        message_type=message_in.message_type,
        is_internal=message_in.is_internal,
        metadata=message_in.metadata
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Broadcast to WebSocket connections
    websocket_manager.broadcast_to_ticket(
        message_in.ticket_id,
        {
            "type": "new_message",
            "message": {
                "id": db_message.id,
                "message": db_message.message,
                "sender": {"id": current_user.id, "name": current_user.name},
                "created_at": db_message.created_at.isoformat(),
                "is_internal": db_message.is_internal
            }
        }
    )
    
    return db_message


@router.get("/{ticket_id}/history", response_model=ChatHistory)
def get_chat_history(
    ticket_id: str,
    skip: int = 0,
    limit: int = 50,
    include_internal: bool = False,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get chat history for a ticket
    """
    # Verify ticket exists and user has access
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    can_view = (
        current_user.role.value in ["l1-engineer", "l2-engineer", "ops-manager", "admin"] or
        ticket.reported_by_id == current_user.id or
        ticket.assigned_to_id == current_user.id
    )
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Build query
    query = db.query(ChatMessageModel).filter(ChatMessageModel.ticket_id == ticket_id)
    
    # Filter internal messages for end users
    if current_user.role.value == "end-user" or not include_internal:
        query = query.filter(ChatMessageModel.is_internal == False)
    
    # Order by creation time
    query = query.order_by(ChatMessageModel.created_at.desc())
    
    total = query.count()
    messages = query.offset(skip).limit(limit).all()
    
    # Reverse to show oldest first
    messages.reverse()
    
    return {
        "messages": messages,
        "total": total
    }


@router.post("/{ticket_id}/ai-chat", response_model=AIResponse)
async def chat_with_ai(
    ticket_id: str,
    message: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Chat with AI assistant about a ticket
    """
    # Verify ticket exists and user has access
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Get recent chat history for context
    recent_messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.ticket_id == ticket_id
    ).order_by(ChatMessageModel.created_at.desc()).limit(10).all()
    
    # Format chat history for AI
    chat_history = []
    for msg in reversed(recent_messages):
        sender = "ai" if msg.is_ai_message else "user"
        chat_history.append({
            "sender": sender,
            "message": msg.message
        })
    
    # Get AI response
    ai_service = AIService()
    ai_response = await ai_service.generate_chat_response(
        user_message=message,
        chat_history=chat_history,
        user_role=current_user.role.value,
        ticket_id=ticket_id,
        db=db
    )
    
    # Save user message
    user_message = ChatMessageModel(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        message=message,
        message_type="text"
    )
    db.add(user_message)
    
    # Save AI response
    ai_message = ChatMessageModel(
        ticket_id=ticket_id,
        sender_id=None,
        message=ai_response,
        is_ai_message=True,
        message_type="text"
    )
    db.add(ai_message)
    
    db.commit()
    
    return {
        "message": ai_response,
        "suggestions": ["Check system logs", "Restart service", "Contact L2 support"],
        "confidence": 0.85
    }


@router.websocket("/ws/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat
    """
    try:
        # Verify token and get user
        from app.core.security import verify_token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008)
            return
        
        user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
        if not user:
            await websocket.close(code=1008)
            return
        
        # Verify ticket access
        ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
        if not ticket:
            await websocket.close(code=1008)
            return
        
        can_access = (
            user.role.value in ["l1-engineer", "l2-engineer", "ops-manager", "admin"] or
            ticket.reported_by_id == user.id or
            ticket.assigned_to_id == user.id
        )
        
        if not can_access:
            await websocket.close(code=1008)
            return
        
        # Accept connection and add to manager
        await websocket.accept()
        websocket_manager.connect(websocket, ticket_id, user.id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data.get("type") == "chat_message":
                    # Save message to database
                    db_message = ChatMessageModel(
                        ticket_id=ticket_id,
                        sender_id=user.id,
                        message=message_data["message"],
                        message_type="text"
                    )
                    db.add(db_message)
                    db.commit()
                    db.refresh(db_message)
                    
                    # Broadcast to other connections
                    websocket_manager.broadcast_to_ticket(
                        ticket_id,
                        {
                            "type": "new_message",
                            "message": {
                                "id": db_message.id,
                                "message": db_message.message,
                                "sender": {"id": user.id, "name": user.name},
                                "created_at": db_message.created_at.isoformat()
                            }
                        },
                        exclude_user=user.id
                    )
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, ticket_id)
            
    except Exception as e:
        await websocket.close(code=1011)