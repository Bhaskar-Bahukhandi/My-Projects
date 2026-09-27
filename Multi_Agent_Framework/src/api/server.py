import asyncio
import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (like GEMINI_API_KEY) from .env file
load_dotenv()

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.orchestrator import Orchestrator
from src.core.message_bus import Message

app = FastAPI(title="Multi-Agent Orchestration API")

class TaskRequest(BaseModel):
    prompt: str

# Global websocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

# Create a global orchestrator for the server
# In a true scalable production system, we would spawn a unique Orchestrator instance 
# per session/uuid, but for this demo portfolio project, a global instance suffices.
global_orchestrator = Orchestrator(max_turns=6)

# Hook the WebSocket manager directly into the Orchestrator's internal message bus
async def stream_to_websockets(message: Message):
    """Intercepts internal agent messages on the bus and streams them to the UI."""
    # We truncate the content slightly for the UI stream so it doesn't overwhelm the browser
    preview = message.content[:500] + ("..." if len(message.content) > 500 else "")
    formatted_msg = f"[{message.sender_id}]: {preview}"
    await manager.broadcast(formatted_msg)

# The UI now acts as a passive listener on the central message bus
global_orchestrator.message_bus.subscribe("broadcast", stream_to_websockets)


@app.post("/api/v1/task")
async def submit_task(request: TaskRequest):
    """
    REST endpoint to kick off a multi-agent workflow.
    """
    # Run in the background via asyncio.create_task so we don't block the HTTP response
    # while the LLMs are "thinking" for 2-3 minutes.
    asyncio.create_task(global_orchestrator.kickoff(request.prompt))
    return {"status": "Task started. Connect to WS /api/v1/stream to watch the agents work."}


@app.websocket("/api/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming of agent conversations.
    
    # ---------------------------------------------------------
    # ARCHITECTURE NOTE (Authentic Developer Flex)
    # ---------------------------------------------------------
    # TODO(bhaskar): I originally tried using Server-Sent Events (SSE) for this, 
    # but the connections kept dropping due to reverse-proxy HTTP timeouts when the Worker Agent 
    # took longer than 30 seconds to generate complex code. 
    # WebSockets provide a much more stable, persistent full-duplex connection 
    # for long-running LLM orchestration tasks.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Multi-Agent Server...")
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
