# Frontend - Coding Agent UI

## Quick Start

### 1. Install Dependencies

```bash
cd web_ui/frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Or use the start script:
```bash
./start.sh
```

The app will be available at **http://localhost:3000**

## Prerequisites

- **Backend must be running** on http://localhost:8000
- Node.js 18+ installed
- npm or yarn

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Main page (two-column layout)
│   └── globals.css      # Global styles
├── components/
│   ├── ChatPanel.tsx    # Streaming chat interface
│   ├── FileTree.tsx     # Workspace file browser
│   └── MetricsPanel.tsx # Session metrics display
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Features

### Two-Column Layout
Modern card-based design with centralized content, rounded corners, and gradient styling.

### Left Column: Chat Interface
- ✅ Real-time streaming responses (SSE)
- ✅ Token-by-token display with smooth updates
- ✅ Auto-scroll to latest message
- ✅ Clean gradient message bubbles (user/assistant)
- ✅ Session management controls (new session button)
- ✅ Session ID display
- ✅ Loading states and error handling

### Right Column Top: File Tree
- ✅ Workspace directory structure
- ✅ Auto-refresh every 3 seconds
- ✅ Expandable/collapsible folders
- ✅ File sizes displayed
- ✅ Graceful offline handling

### Right Column Bottom: Metrics Panel
**2x2 Grid Display:**
- ✅ **Turn Number** - Current conversation turn
- ✅ **Messages** - Total message count
- ✅ **Files** - Files in context
- ✅ **Latency** - Running average response time (last 10 messages)
- ✅ Session ID reference
- ✅ Auto-refresh every 2 seconds

## Development

### Run Dev Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Lint
```bash
npm run lint
```

## Configuration

Backend API endpoint is hardcoded to `http://localhost:8000`

To change it, update the fetch URLs in:
- `components/ChatPanel.tsx`
- `components/FileTree.tsx`
- `components/MetricsPanel.tsx`

## Troubleshooting

### CORS Errors
Make sure backend is running with CORS enabled for http://localhost:3000

### Streaming Not Working
1. Check backend is running on port 8000
2. Open browser console for errors
3. Verify `/api/chat` endpoint is accessible

### File Tree Empty
1. Verify workspace path in backend config
2. Check `/api/workspace/tree` endpoint response

### Metrics Not Updating
1. Make sure you've sent at least one message
2. Verify session ID is being passed correctly
3. Check `/api/metrics/{session_id}` endpoint

## Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Server-Sent Events** - Real-time streaming

## Next Steps

Once running:
1. Send a message to the agent
2. Watch it stream token-by-token
3. See files appear in the tree as agent creates them
4. Monitor metrics update in real-time

