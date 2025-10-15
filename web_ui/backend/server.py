from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import os
from pathlib import Path
from typing import Optional

# Import your existing agent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.agent import get_agent
from src.config import config
from src.memory import memory_manager

app = FastAPI()

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# 1. STREAMING CHAT ENDPOINT
@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Stream agent responses via SSE."""
    agent = get_agent()
    
    # Use existing session or create new one
    if request.session_id:
        agent.start_session(request.session_id)  # This loads existing or creates new
    elif not agent.current_session_id:
        agent.start_session()
    
    async def event_generator():
        try:
            # Stream events from agent
            async for event in agent.astream_response(request.message):
                event_type = event.get('event')
                # Debug: print event type
                print(f"[SSE] Sending event: {event_type}")
                
                # Create a JSON-serializable version of the event
                try:
                    # Try to serialize the whole event
                    json.dumps(event)
                    # If successful, send as-is
                    yield f"data: {json.dumps(event)}\n\n"
                except (TypeError, ValueError) as e:
                    # If not serializable, send a simplified version
                    simplified_event = {
                        "event": event_type,
                        "name": event.get("name", ""),
                        "run_id": event.get("run_id", "")
                    }
                    # For chat model streams, extract the content
                    if event_type == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk", {})
                        if hasattr(chunk, 'content'):
                            simplified_event["data"] = {"chunk": {"content": chunk.content}}
                        else:
                            simplified_event["data"] = {"chunk": {"content": str(chunk)}}
                    
                    yield f"data: {json.dumps(simplified_event)}\n\n"
                
                await asyncio.sleep(0)  # Yield control
            
            # Send completion with session info
            completion = {
                "event": "done",
                "data": {
                    "session_id": agent.current_session_id
                }
            }
            yield f"data: {json.dumps(completion)}\n\n"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR] Exception in event_generator: {str(e)}")
            print(error_details)
            error = {
                "event": "error",
                "data": {
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": error_details
                }
            }
            yield f"data: {json.dumps(error)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# 2. FILE TREE ENDPOINT
@app.get("/api/workspace/tree")
async def get_file_tree():
    """Get workspace directory structure."""
    workspace = config.get_workspace_path()
    
    def build_tree(path: Path, max_depth=3, current_depth=0):
        """Recursively build directory tree."""
        if current_depth >= max_depth:
            return None
        
        try:
            items = []
            for item in sorted(path.iterdir()):
                # Skip hidden files and __pycache__
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                
                node = {
                    "name": item.name,
                    "path": str(item.relative_to(workspace)),
                    "type": "directory" if item.is_dir() else "file"
                }
                
                if item.is_file():
                    node["size"] = item.stat().st_size
                elif item.is_dir():
                    children = build_tree(item, max_depth, current_depth + 1)
                    if children:
                        node["children"] = children
                
                items.append(node)
            
            return items
        except PermissionError:
            return []
    
    tree = build_tree(workspace)
    return {"root": str(workspace), "children": tree or []}

# 3. SESSION METRICS ENDPOINT
@app.get("/api/metrics/{session_id}")
async def get_session_metrics(session_id: str):
    """Get current session metrics."""
    agent = get_agent()
    
    if session_id != agent.current_session_id:
        agent.load_session(session_id)
    
    info = agent.get_session_info()
    
    return {
        "session_id": session_id,
        "turn_number": info.get("message_count", 0) // 2,
        "message_count": info.get("message_count", 0),
        "files_in_context": info.get("files_in_context", 0),
        "created_at": info.get("created_at"),
        "last_updated": info.get("last_updated")
    }

# 4. SESSION MANAGEMENT
@app.get("/api/sessions")
async def list_sessions():
    """List all available sessions."""
    sessions = memory_manager.list_sessions()
    return {"sessions": sessions}

@app.post("/api/sessions")
async def create_session():
    """Create a new session."""
    agent = get_agent()
    session_id = agent.start_session()
    return {"session_id": session_id}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workspace": str(config.get_workspace_path()),
        "model": config.get_model_config()["model_name"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)