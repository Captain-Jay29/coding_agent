# Debugging SSE Streaming

## Changes Made

### Backend (server.py)
- Added console logging for each SSE event sent: `[SSE] Sending event: {type}`

### Frontend (ChatPanel.tsx)
- Added `console.log()` for each received event
- Added try/catch for better error handling
- Added handler for `on_complete` event

## How to Debug

### 1. Restart Both Servers

**Backend:**
```bash
# Stop with Ctrl+C, then:
cd /Users/jay/Desktop/coding_agent
./web_ui/backend/start.sh
```

**Frontend:**
```bash
# If needed, stop with Ctrl+C, then:
cd /Users/jay/Desktop/coding_agent/web_ui/frontend
npm run dev
```

### 2. Open Browser Console

1. Open http://localhost:3000
2. Press F12 (or Cmd+Option+I on Mac)
3. Go to "Console" tab

### 3. Send a Message

Type something like: "Hello, create a test file"

### 4. Check Logs

**Backend Terminal** should show:
```
[SSE] Sending event: on_chat_model_stream
[SSE] Sending event: on_chat_model_stream
[SSE] Sending event: on_tool_start
...
[SSE] Sending event: on_complete
```

**Browser Console** should show:
```
Received event: on_chat_model_stream {event: 'on_chat_model_stream', data: {...}}
Received event: on_chat_model_stream {event: 'on_chat_model_stream', data: {...}}
...
Stream complete
```

## Common Issues

### Issue: Events logged in backend but not in browser
**Cause:** CORS or network issue
**Fix:** Check browser Network tab for failed requests

### Issue: Events received but content not showing
**Cause:** Wrong event structure
**Fix:** Check `data.data.chunk.content` path in console

### Issue: "Failed to parse SSE line" errors
**Cause:** Malformed JSON in SSE stream
**Fix:** Check backend event formatting

## Expected Event Structure

Backend sends:
```json
{
  "event": "on_chat_model_stream",
  "data": {
    "chunk": {
      "content": "Hello"
    }
  }
}
```

Frontend extracts:
```javascript
const token = data.data?.chunk?.content || '';
```

## Quick Test

Run this in browser console while streaming:
```javascript
// Monitor all fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('Fetch:', args);
  return originalFetch.apply(this, args);
};
```

This will show all API calls being made.

