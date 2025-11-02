"""
WebSocket Routes for Real-time Communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/ws/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Connected to RAG-ENTERPRISE",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message (integrate with RAG pipeline)
            # TODO: Call RAG pipeline here
            
            # Echo response for now
            response = {
                "type": "message",
                "content": f"Received: {message_data.get('content')}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.send_personal_message(
                json.dumps(response),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            
            notification = {
                "type": "notification",
                "message": "System update",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.send_personal_message(
                json.dumps(notification),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
