# 🚀 UI Implementation Guide (< 1 Day MVP)

## 🎯 Goal
Build a minimal working UI with streaming chat, file tree, and basic metrics in **under 8 hours**.

---

## 📋 Core Features Only

### ✅ Must Have (Priority 1)
1. **Streaming chat interface** - Main column with agent responses
2. **File tree viewer** - Show workspace directory structure
3. **Basic session metrics** - Current session stats only
4. **Session management** - Create/switch sessions

### ❌ Skip for MVP
- Historical metrics/charts
- File editing in UI
- Dark mode
- Authentication
- Deployment optimizations

---

## 🏗️ Architecture (Simplified)

```
Frontend (Next.js)  ←→  Backend (FastAPI)  ←→  Agent (existing)
    Port 3000              Port 8000
```

**Communication:** Server-Sent Events (SSE) for streaming

---

## 🔧 Backend Setup (1-2 hours)

### Step 1: Create FastAPI Server

**File:** `backend/server.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import os
from pathlib import Path

# Import your existing agent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
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
    session_id: str = None

# 1. STREAMING CHAT ENDPOINT
@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Stream agent responses via SSE."""
    agent = get_agent()
    
    # Use existing session or create new one
    if request.session_id:
        agent.load_session(request.session_id)
    elif not agent.current_session_id:
        agent.start_session()
    
    async def event_generator():
        try:
            # Stream events from agent
            async for event in agent.astream_response(request.message):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
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
            error = {
                "event": "error",
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
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
```

### Step 2: Install Backend Dependencies

**File:** `backend/requirements.txt`

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic==2.5.0
```

### Step 3: Run Backend

```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Test:** Visit `http://localhost:8000/api/health`

---

## 💻 Frontend Setup (2-3 hours)

### Step 1: Create Next.js App

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npm install ai @ai-sdk/openai
```

### Step 2: Main Layout Component

**File:** `frontend/app/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import ChatPanel from '@/components/ChatPanel';
import FileTree from '@/components/FileTree';
import MetricsPanel from '@/components/MetricsPanel';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Column: Chat */}
      <div className="flex-1 flex flex-col border-r border-gray-200">
        <header className="bg-white border-b border-gray-200 p-4">
          <h1 className="text-xl font-bold">Coding Agent</h1>
        </header>
        <ChatPanel sessionId={sessionId} onSessionChange={setSessionId} />
      </div>

      {/* Right Column: File Tree + Metrics */}
      <div className="w-96 flex flex-col">
        {/* File Tree (top half) */}
        <div className="flex-1 border-b border-gray-200 overflow-auto">
          <FileTree />
        </div>

        {/* Metrics (bottom half) */}
        <div className="h-64 overflow-auto">
          <MetricsPanel sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
```

### Step 3: Chat Panel Component

**File:** `frontend/components/ChatPanel.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: any;
}

interface ChatPanelProps {
  sessionId: string | null;
  onSessionChange: (id: string) => void;
}

export default function ChatPanel({ sessionId, onSessionChange }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          session_id: sessionId
        })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.event === 'on_chat_model_stream') {
              const token = data.data?.chunk?.content || '';
              assistantMessage += token;
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1].content = assistantMessage;
                return updated;
              });
            } else if (data.event === 'done') {
              if (data.data?.session_id) {
                onSessionChange(data.data.session_id);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Error: Failed to get response' }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white border border-gray-200'
              }`}
            >
              <div className="text-sm font-medium mb-1">
                {msg.role === 'user' ? 'You' : 'Agent'}
              </div>
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isStreaming ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

### Step 4: File Tree Component

**File:** `frontend/components/FileTree.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
}

export default function FileTree() {
  const [tree, setTree] = useState<FileNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchTree();
    const interval = setInterval(fetchTree, 3000); // Refresh every 3s
    return () => clearInterval(interval);
  }, []);

  const fetchTree = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/workspace/tree');
      const data = await res.json();
      setTree(data.children || []);
    } catch (error) {
      console.error('Failed to fetch tree:', error);
    }
  };

  const toggleExpand = (path: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderNode = (node: FileNode, depth = 0) => {
    const isExpanded = expanded.has(node.path);
    const isDir = node.type === 'directory';

    return (
      <div key={node.path}>
        <div
          className="flex items-center gap-2 px-2 py-1 hover:bg-gray-100 cursor-pointer"
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => isDir && toggleExpand(node.path)}
        >
          {isDir && <span>{isExpanded ? '▼' : '▶'}</span>}
          <span>{isDir ? '📂' : '📄'}</span>
          <span className="text-sm">{node.name}</span>
          {node.size && (
            <span className="text-xs text-gray-400 ml-auto">
              {(node.size / 1024).toFixed(1)}KB
            </span>
          )}
        </div>
        {isDir && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white h-full">
      <div className="border-b border-gray-200 p-3 font-semibold">
        📁 Workspace Files
      </div>
      <div className="overflow-auto">
        {tree.map(node => renderNode(node))}
      </div>
    </div>
  );
}
```

### Step 5: Metrics Panel Component

**File:** `frontend/components/MetricsPanel.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';

interface MetricsPanelProps {
  sessionId: string | null;
}

export default function MetricsPanel({ sessionId }: MetricsPanelProps) {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    if (!sessionId) return;

    const fetchMetrics = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/metrics/${sessionId}`);
        const data = await res.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, [sessionId]);

  if (!metrics) {
    return (
      <div className="bg-white h-full p-4">
        <div className="font-semibold mb-2">📊 Session Metrics</div>
        <p className="text-sm text-gray-500">No active session</p>
      </div>
    );
  }

  return (
    <div className="bg-white h-full p-4">
      <div className="font-semibold mb-3">📊 Session Metrics</div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Turn:</span>
          <span className="font-medium">{metrics.turn_number}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Messages:</span>
          <span className="font-medium">{metrics.message_count}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Files:</span>
          <span className="font-medium">{metrics.files_in_context}</span>
        </div>
        <div className="text-xs text-gray-400 mt-4">
          Session: {metrics.session_id.slice(0, 8)}...
        </div>
      </div>
    </div>
  );
}
```

### Step 6: Run Frontend

```bash
cd frontend
npm run dev
```

**Visit:** `http://localhost:3000`

---

## ⚡ Quick Start Commands

```bash
# Terminal 1: Backend
cd backend
python server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## ✅ Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Chat streaming works
- [ ] File tree displays
- [ ] Metrics update in real-time
- [ ] Can create new sessions

---

## 🎯 Time Estimate

| Task | Time |
|------|------|
| Backend setup | 1h |
| Frontend setup | 1h |
| Chat component | 1.5h |
| File tree | 1h |
| Metrics panel | 30m |
| Testing & fixes | 1h |
| **Total** | **6 hours** |

---

## 🚨 Common Issues

**CORS errors:** Make sure FastAPI CORS is configured correctly  
**SSE not working:** Check browser console for network errors  
**File tree empty:** Verify workspace path in backend  
**Metrics not updating:** Check sessionId is being passed correctly

---

## 🚀 Deploy Later (Optional)

**Backend:** Railway, Render, or Fly.io  
**Frontend:** Vercel (one-click deploy)

---

**That's it! Keep it simple, get it working, iterate later.** 🎉

