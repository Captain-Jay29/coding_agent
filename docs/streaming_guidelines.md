# ⚡ Implementing Streaming in the Coding Agent

This guide explains how to add **streaming output support** to your coding agent, allowing real-time feedback both in the CLI and in future UIs (like those built with the [Vercel AI SDK](https://ai-sdk.dev)).

---

## 🎯 Why Streaming?

Streaming enables the agent to send partial results (tokens, tool updates, or progress logs) as they happen — rather than waiting for a full response.  
This improves responsiveness and sets the foundation for building a modern, event-driven UI.

**Benefits:**
- Real-time token updates in CLI or GUI
- Smooth integration with frameworks like Vercel AI SDK
- Immediate visibility into tool actions and intermediate results
- Better user experience for long-running operations

---

## 🧱 Step 1: Add Streaming Support in CLI

Update your CLI to use the agent’s **asynchronous streaming interface**.

If your current call looks like this:
```python
result = agent.invoke(user_input)
print(result)
```
Change it to stream results progressively:

```python
import asyncio

async def run_agent_stream(user_input: str):
    async for chunk in agent.astream_events(user_input, version="v1"):
        event = chunk["event"]

        if event == "on_token":
            print(chunk["data"]["token"], end="", flush=True)

        elif event == "on_tool_start":
            print(f"\n🛠️ Running tool: {chunk['data']['name']}")

        elif event == "on_tool_end":
            print(f"\n✅ Tool finished: {chunk['data']['name']}")

        elif event == "on_error":
            print(f"\n❌ Error: {chunk['data']['error']}")

asyncio.run(run_agent_stream("Create a Flask app with CRUD routes"))
```
✅ Test this locally first — you should see responses stream token-by-token as the model generates them.

## 🌐 Step 2: Expose a Streaming API (Server-Sent Events)

Once streaming works in the CLI, expose it over HTTP so a frontend can consume it.

Create a small FastAPI server:

```python
# server.py
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from src.agent import agent  # your agent instance

app = FastAPI()

@app.post("/chat")
async def chat_stream(request: Request):
    body = await request.json()
    user_input = body["message"]

    async def event_generator():
        async for chunk in agent.astream_events(user_input, version="v1"):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

Run the server:
```bash
uvicorn server:app --reload
```

You can test this endpoint with:
```bash
curl -N -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Write a hello world script"}'
```

## 💬 Step 3: Connect the Stream to a UI (Optional Next Step)

Later, when you’re ready to build your GUI, you can directly consume this SSE stream using the Vercel AI SDK:

Example in a Next.js frontend:
```js
"use client";
import { useChat } from "ai/react";

export default function ChatUI() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: "/api/chat", // proxy to FastAPI backend
  });

  return (
    <div className="chat-ui">
      {messages.map(m => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

The useChat() hook automatically listens to the SSE stream and updates the UI in real time.

## 🧩 Step 4: Enrich the Stream (Optional Enhancements)

Once streaming is stable, you can add structured events to make the UI richer.

| Event Type      | Description           | Example UI                    |
|------------------|-----------------------|--------------------------------|
| on_tool_start    | Tool invocation started | Show spinner or “Working…”     |
| on_tool_end      | Tool completed         | Show ✅ confirmation            |
| on_diff_ready    | Diff generated         | Render code diff viewer        |
| on_error         | Error occurred         | Show error banner              |
| on_complete      | Response finished      | Finalize message block         |


This pattern lets your frontend render each event as a unique visual component (progress bar, code block, etc.).