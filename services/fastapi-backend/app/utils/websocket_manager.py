"""
WebSocket connection manager for real-time features
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        # Store active connections by ticket_id
        self.ticket_connections: Dict[str, List[WebSocket]] = {}
        # Store user connections for direct messaging
        self.user_connections: Dict[int, List[WebSocket]] = {}
        # Map websockets to their associated ticket and user
        self.connection_map: Dict[WebSocket, Dict[str, any]] = {}
    
    async def connect(self, websocket: WebSocket, ticket_id: str, user_id: int):
        """
        Add a new WebSocket connection
        """
        await websocket.accept()
        
        # Add to ticket connections
        if ticket_id not in self.ticket_connections:
            self.ticket_connections[ticket_id] = []
        self.ticket_connections[ticket_id].append(websocket)
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        # Store connection mapping
        self.connection_map[websocket] = {
            "ticket_id": ticket_id,
            "user_id": user_id
        }
        
        logger.info(f"WebSocket connected: user {user_id} to ticket {ticket_id}")
    
    def disconnect(self, websocket: WebSocket, ticket_id: str):
        """
        Remove a WebSocket connection
        """
        # Remove from connection map
        connection_info = self.connection_map.pop(websocket, {})
        user_id = connection_info.get("user_id")
        
        # Remove from ticket connections
        if ticket_id in self.ticket_connections:
            if websocket in self.ticket_connections[ticket_id]:
                self.ticket_connections[ticket_id].remove(websocket)
            if not self.ticket_connections[ticket_id]:
                del self.ticket_connections[ticket_id]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user {user_id} from ticket {ticket_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            # Connection might be closed, remove it
            self._cleanup_connection(websocket)
    
    async def broadcast_to_ticket(self, ticket_id: str, message: dict, exclude_user: int = None):
        """
        Broadcast a message to all connections for a specific ticket
        """
        if ticket_id not in self.ticket_connections:
            return
        
        connections_to_remove = []
        for websocket in self.ticket_connections[ticket_id]:
            try:
                # Skip if this is the user who sent the message
                connection_info = self.connection_map.get(websocket, {})
                if exclude_user and connection_info.get("user_id") == exclude_user:
                    continue
                
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to ticket {ticket_id}: {str(e)}")
                connections_to_remove.append(websocket)
        
        # Clean up failed connections
        for websocket in connections_to_remove:
            self._cleanup_connection(websocket)
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """
        Broadcast a message to all connections for a specific user
        """
        if user_id not in self.user_connections:
            return
        
        connections_to_remove = []
        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                connections_to_remove.append(websocket)
        
        # Clean up failed connections
        for websocket in connections_to_remove:
            self._cleanup_connection(websocket)
    
    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all connected users
        """
        all_connections = set()
        for connections in self.ticket_connections.values():
            all_connections.update(connections)
        
        connections_to_remove = []
        for websocket in all_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to all: {str(e)}")
                connections_to_remove.append(websocket)
        
        # Clean up failed connections
        for websocket in connections_to_remove:
            self._cleanup_connection(websocket)
    
    def _cleanup_connection(self, websocket: WebSocket):
        """
        Clean up a failed connection from all tracking structures
        """
        connection_info = self.connection_map.pop(websocket, {})
        ticket_id = connection_info.get("ticket_id")
        user_id = connection_info.get("user_id")
        
        # Remove from ticket connections
        if ticket_id and ticket_id in self.ticket_connections:
            if websocket in self.ticket_connections[ticket_id]:
                self.ticket_connections[ticket_id].remove(websocket)
            if not self.ticket_connections[ticket_id]:
                del self.ticket_connections[ticket_id]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    def get_ticket_connection_count(self, ticket_id: str) -> int:
        """
        Get the number of active connections for a ticket
        """
        return len(self.ticket_connections.get(ticket_id, []))
    
    def get_user_connection_count(self, user_id: int) -> int:
        """
        Get the number of active connections for a user
        """
        return len(self.user_connections.get(user_id, []))
    
    def get_total_connections(self) -> int:
        """
        Get the total number of active connections
        """
        return len(self.connection_map)
    
    def get_active_tickets(self) -> List[str]:
        """
        Get list of tickets with active connections
        """
        return list(self.ticket_connections.keys())
    
    def get_active_users(self) -> List[int]:
        """
        Get list of users with active connections
        """
        return list(self.user_connections.keys())
