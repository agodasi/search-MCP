from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bridge")

class Event(BaseModel):
    type: str
    data: Dict[str, Any]

# Persistence of state
class GlobalState:
    def __init__(self):
        self.last_query: Optional[Dict[str, Any]] = None
        self.last_results: Optional[Dict[str, Any]] = None
        self.last_content: Optional[Dict[str, Any]] = None

state = GlobalState()
connected_clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"New WebSocket connection: {websocket.client}")
    connected_clients.append(websocket)
    
    # Sync initial state on connect
    try:
        if state.last_query:
            await websocket.send_json({"type": "search_query", "data": state.last_query})
        if state.last_results:
            await websocket.send_json({"type": "search_results", "data": state.last_results})
        if state.last_content:
            await websocket.send_json({"type": "content_extracted", "data": state.last_content})
    except Exception as e:
        logger.error(f"Error during initial sync: {e}")

    try:
        while True:
            # We don't expect data FROM clients usually, but we keep the connection alive
            data = await websocket.receive_text()
            # If we wanted to handle bidirectional commands, we'd do it here
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {websocket.client}")
        connected_clients.remove(websocket)

@app.post("/event")
async def post_event(event: Event):
    logger.info(f"Received event: {event.type}")
    
    # Update global state based on event type
    if event.type == "search_query":
        state.last_query = event.data
        state.last_content = None # Reset content for new query
    elif event.type == "search_results":
        state.last_results = event.data
    elif event.type == "content_extracted":
        state.last_content = event.data
        
    # Broadcast to all connected clients
    message = event.dict()
    logger.info(f"Broadcasting: {message}")
    
    # Create list of tasks for broadcasting
    tasks = []
    for client in connected_clients:
        tasks.append(client.send_json(message))
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
        
    return {"status": "ok", "delivered_to": len(connected_clients)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)