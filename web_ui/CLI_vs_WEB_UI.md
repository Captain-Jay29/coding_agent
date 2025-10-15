# CLI vs Web UI - Key Differences

## 🎯 Overview

The **CLI** (`interface/cli.py`) and **Web UI** (`web_ui/`) use the same agent but have different interfaces.

---

## 📋 Feature Comparison

| Feature | CLI | Web UI | Status |
|---------|-----|--------|--------|
| **Chat with agent** | ✅ | ✅ | Both work |
| **Streaming responses** | ✅ | ✅ | Both work |
| **File creation** | ✅ | ✅ | Both work |
| **Command execution** | ✅ | ✅ | Both work |
| **Session management** | ✅ Special commands | ✅ UI Button | Different UX |
| **File tree view** | ❌ | ✅ | Web UI only |
| **Metrics display** | ❌ | ✅ | Web UI only |
| **Multi-line input** | ✅ | ❌ | CLI only |
| **Command history** | ✅ | ❌ | CLI only |

---

## 🔧 CLI Special Commands

These work **ONLY in CLI**, not in Web UI:

```bash
help         # Show help message
sessions     # List all sessions
clear        # Clear current session
info         # Show session info
config       # Show configuration
quit / exit  # Exit CLI
```

**Why?** These are handled by `interface/cli.py` before the agent sees them.

---

## 🌐 Web UI Controls

These are **UI buttons/features**, not chat commands:

- **New Session** button - Creates fresh session
- **File Tree** - Auto-refreshes workspace files
- **Metrics Panel** - Shows session stats
- **Session ID** - Displayed in header

**Why?** Web UIs use buttons/panels instead of text commands.

---

## ⚠️ Important Limitations

### **Interactive Scripts Don't Work**

Scripts using `input()` will **freeze** in both CLI and Web UI:

```python
# ❌ This will hang:
n = int(input("Enter n: "))

# ✅ Use this instead:
import sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
```

**Solution:** The agent now knows to avoid `input()` and use arguments instead.

### **No Multi-line in Web UI**

CLI supports `"""` for multi-line:
```
You: """
Create a function
that does X
"""
```

Web UI: Use Shift+Enter or just type naturally (agent understands context).

---

## 🎨 Web UI Exclusive Features

### 1. File Tree Browser
- See all workspace files
- Auto-refreshes every 3 seconds
- Expandable folders
- File sizes shown

### 2. Real-time Metrics
- Turn number
- Message count
- Files in context
- Auto-refreshes every 2 seconds

### 3. Visual Session Management
- See current session ID in header
- "New Session" button
- Persistent across page refreshes (via session ID)

---

## 💡 Best Practices

### **For CLI Users:**
- Use special commands (`help`, `sessions`, `clear`)
- Multi-line input with `"""`
- Command history with ↑/↓ arrows

### **For Web UI Users:**
- Use "New Session" button to start fresh
- Check file tree to see created files
- Watch metrics for conversation stats
- Ask agent to modify scripts to avoid `input()`

---

## 🔄 Migrating Between Interfaces

### **CLI → Web UI:**
Sessions are compatible! Use the session ID:

```bash
# In CLI
You: info
Session ID: abc-123-def

# In Web UI
# Send a message, it creates new session
# Or use the API to load: POST /api/chat with session_id: "abc-123-def"
```

### **Web UI → CLI:**
```bash
# Start CLI
python main.py

# Load session
sessions                    # List all sessions
# Use the agent (it auto-continues the session)
```

---

## 🚀 Quick Reference

### **Start CLI:**
```bash
python main.py
```

### **Start Web UI:**
```bash
# Terminal 1: Backend
./web_ui/backend/start.sh

# Terminal 2: Frontend
cd web_ui/frontend && npm run dev

# Browser: http://localhost:3000
```

### **Which to Use?**

**Use CLI when:**
- ✅ You want command history
- ✅ You need multi-line input
- ✅ You prefer keyboard-only interaction
- ✅ You want to quickly switch sessions

**Use Web UI when:**
- ✅ You want visual file tree
- ✅ You want to see metrics
- ✅ You prefer graphical interface
- ✅ You want to share your screen
- ✅ You're working remotely

---

## 🐛 Common Issues

### **"help doesn't work in Web UI"**
✅ **Expected:** `help` is a CLI command, not available in Web UI.  
💡 **Solution:** Just ask the agent "What can you do?" or "Help me understand your capabilities"

### **"Script hangs when running"**
✅ **Cause:** Script uses `input()` which waits for stdin.  
💡 **Solution:** Ask agent to modify script to use command-line arguments instead.

### **"Session commands don't work"**
✅ **Expected:** `sessions`, `clear`, `info` are CLI-only.  
💡 **Solution:** Use the "New Session" button or ask agent for session info.

---

## 📈 Future Enhancements

Planned Web UI features:
- [ ] Session browser with search
- [ ] File preview/edit in UI
- [ ] Download chat history
- [ ] Upload files to workspace
- [ ] Settings panel
- [ ] Dark mode
- [ ] Multi-line text area

---

**Both interfaces use the same powerful agent - choose what works best for you!** 🎉

