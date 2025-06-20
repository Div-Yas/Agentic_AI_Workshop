from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

# Store active connections
active_connections: List[WebSocket] = []

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Echo back for now - can be extended for specific commands
            await websocket.send_text(f"Message received: {data}")
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_message(message: Dict):
    """Broadcast message to all connected clients"""
    if not active_connections:
        return
    
    message_json = json.dumps(message)
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_text(message_json)
        except Exception:
            disconnected.append(connection)
    
    # Remove disconnected connections
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)

async def send_workflow_update(request_id: str, status: str, progress: int, message: str = ""):
    """Send workflow update to connected clients"""
    update_message = {
        "type": "workflow_update",
        "request_id": request_id,
        "status": status,
        "progress": progress,
        "message": message,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await broadcast_message(update_message) 