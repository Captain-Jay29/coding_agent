# Backend API for Coding Agent

FastAPI server that powers the web UI, providing streaming agent responses, workspace management, and session tracking.

## Quick Start

### 1. Install Dependencies
```bash
cd web_ui/backend
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure your main `.env` file is set up (at project root):
```bash
OPENAI_API_KEY=your-key-here
WORKSPACE_PATH=/path/to/agent_runs
DEFAULT_MODEL=gpt-4o-mini
MODEL_TEMPERATURE=0.0
```

### 3. Run the Server
```bash
python server.py
```

Or use the start script:
```bash
./start.sh
```

The server will run on **http://localhost:8000**

## API Endpoints

### 1. Chat (Streaming)
**`POST /api/chat`** - Stream agent responses via Server-Sent Events (SSE)

**Request:**
```json
{
  "message": "Create a hello world Python file",
  "session_id": "optional-session-id"
}
```

**Response:** SSE stream with events:
- `on_chat_model_stream` - LLM tokens
- `on_tool_start` - Tool execution begins
- `on_tool_end` - Tool execution completes
- `on_complete` - Response finished (includes metadata with latency)
- `done` - Stream complete (includes session_id)
- `error` - Error occurred

### 2. File System
**`GET /api/workspace/tree`** - Get workspace directory structure

**Response:**
```json
{
  "name": "agent_runs",
  "type": "directory",
  "children": [...]
}
```

### 3. Metrics
**`GET /api/metrics/{session_id}`** - Get real-time session metrics

**Response:**
```json
{
  "session_id": "abc123...",
  "turn_number": 3,
  "message_count": 6,
  "files_in_context": 2
}
```

### 4. Sessions
**`GET /api/sessions`** - List all available sessions

**`POST /api/sessions`** - Create a new session

**Response:**
```json
{
  "session_id": "newly-created-id"
}
```

### 5. Health Check
**`GET /api/health`** - Server health and status

**Response:**
```json
{
  "status": "healthy",
  "agent_ready": true
}
```

## Features

### Streaming Architecture
- ✅ Server-Sent Events (SSE) for real-time updates
- ✅ Token-by-token LLM streaming
- ✅ Tool execution progress tracking
- ✅ Latency measurement for each response

### CORS Configuration
- ✅ Configured for `http://localhost:3000` (frontend)
- ✅ Credentials support enabled
- ✅ All methods and headers allowed

### Session Management
- ✅ Persistent session storage (JSON files)
- ✅ Session creation and listing
- ✅ Automatic session initialization if not provided

### Error Handling
- ✅ Graceful error responses in SSE stream
- ✅ Detailed error messages with tracebacks
- ✅ Safe JSON serialization for complex objects

## Testing

### Test with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Get file tree
curl http://localhost:8000/api/workspace/tree

# Create new session
curl -X POST http://localhost:8000/api/sessions

# Stream chat (replace session_id)
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a Python calculator", "session_id": "your-session-id"}'

# Get session metrics
curl http://localhost:8000/api/metrics/your-session-id
```

### Test Script
Run the automated test suite:
```bash
python test_server.py
```

## Troubleshooting

### Server won't start
- Verify main `.env` file has `OPENAI_API_KEY`
- Check port 8000 is not already in use
- Ensure all dependencies are installed

### CORS errors
- Backend must be running on port 8000
- Frontend must be on port 3000
- Check browser console for specific CORS error details

### SSE streaming not working
- Use `-N` flag with curl for streaming
- Check browser network tab shows `text/event-stream`
- Verify `Connection: keep-alive` header is present

### Metrics returning empty
- Ensure at least one message has been sent in the session
- Verify session_id is valid and exists
- Check `sessions/` directory for session files

## Tech Stack

- **FastAPI** - Modern async Python web framework
- **Pydantic** - Request/response validation
- **Server-Sent Events** - Real-time streaming protocol
- **LangChain** - Agent orchestration integration
- **Uvicorn** - ASGI server

## Integration

This backend integrates with:
- **Main Agent** (`src/agent.py`) - Core coding agent logic
- **Config** (`src/config.py`) - Environment variables
- **Memory** (`src/memory.py`) - Session persistence
- **Frontend** (`web_ui/frontend/`) - Next.js UI

