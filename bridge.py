from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
import json
from typing import List

app = FastAPI()

class Event(BaseModel):
    type: str  # "log", "search_query", "search_results", "content_extracted"
    data: dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        print(f"Broadcasting: {message}")
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, the connection might be dead
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"New WebSocket connection: {websocket.client}")
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {websocket.client}")
        manager.disconnect(websocket)

@app.post("/event")
async def post_event(event: Event):
    print(f"Received event: {event.model_dump()}")
    await manager.broadcast(event.model_dump())
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)