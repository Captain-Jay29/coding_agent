# Coding Agent

A powerful coding agent built with LangChain that can perform CRUD operations on codebases through natural conversation with contextual awareness and workspace management.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Configure your workspace (optional):**
   Create a `.env` file:
   ```bash
   WORKSPACE_PATH=/path/to/your/workspace
   DEFAULT_MODEL=gpt-4o-mini
   MODEL_TEMPERATURE=0.0
   MAX_HISTORY_MESSAGES=20
   COMMAND_TIMEOUT=30
   MEMORY_STORAGE_DIR=.agent_memory
   ```

4. **Run the agent:**
   ```bash
   python main.py
   ```

## Features

### 🎯 **Core Capabilities**
- **File Operations**: Read, write, edit files with workspace awareness
- **Shell Commands**: Execute commands safely in workspace context
- **Multi-file Projects**: Create complete packages and applications
- **Code Testing**: Run tests, linting, and validation

### 🧠 **Intelligence Features**
- **Contextual Awareness**: Remembers conversation history and file context
- **Smart Path Resolution**: Automatically handles file paths and workspace navigation
- **Multi-line Input**: Support for complex, multi-line requests
- **Session Management**: Persistent conversation history across sessions

### 🛠 **Developer Experience**
- **Workspace Isolation**: All work happens in a dedicated workspace directory
- **Configuration Management**: Flexible settings via environment variables
- **Error Handling**: Graceful error recovery with detailed feedback
- **Rich CLI**: Clean, colored interface with helpful commands

## Usage Examples

### **Simple File Operations**
```
You: Create a simple Python script that prints "Hello World"

Agent: I'll create a simple Python script for you.

✅ Created: hello.py
📝 Preview:
print("Hello World")

You: Run the script to test it

Agent: I'll run the script to test it.

⚡ Executed: python hello.py
📤 Output:
Hello World
```

### **Multi-file Project Creation**
```
You: Create a Python package called "calculator" with:
- __init__.py file
- calculator.py with Calculator class
- operations.py with basic math operations
- tests.py with unit tests
- requirements.txt

Agent: I'll create a complete calculator package for you.

✅ Created: calculator/__init__.py
✅ Created: calculator/calculator.py
✅ Created: calculator/operations.py
✅ Created: calculator/tests.py
✅ Created: calculator/requirements.txt

You: Add a modulo operation to it

Agent: I'll add the modulo operation to your calculator package.

✅ Updated: calculator/operations.py (added modulo function)
✅ Updated: calculator/calculator.py (added modulo method)
✅ Updated: calculator/tests.py (added modulo tests)

You: Test the package

Agent: I'll run the tests to verify everything works.

⚡ Executed: pytest calculator/tests.py
📤 Output: 7 tests passed!
```

### **Advanced Features**
```
You: multiline
Multi-line input mode activated!
Enter your request (press Ctrl+D or type 'END' on a new line when done):
Create a Flask web application with:
- app.py (main Flask app)
- templates/index.html
- static/style.css
- requirements.txt
END

Agent: I'll create a complete Flask web application for you.

✅ Created: app.py
✅ Created: templates/index.html
✅ Created: static/style.css
✅ Created: requirements.txt
```

## Available Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `sessions` | List available sessions |
| `session <id>` | Switch to a specific session |
| `info` | Show current session information |
| `config` | Show current configuration |
| `multiline` | Enter multi-line input mode |
| `clear` | Clear current session |
| `quit/exit` | Exit the agent |

## Configuration Options

All settings can be configured via `.env` file or environment variables:

| Setting | Default | Description |
|---------|---------|-------------|
| `WORKSPACE_PATH` | `./agent_runs` | Directory for all agent work |
| `DEFAULT_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `MODEL_TEMPERATURE` | `0.0` | Model temperature (0-1) |
| `MAX_HISTORY_MESSAGES` | `20` | Conversation history limit |
| `COMMAND_TIMEOUT` | `30` | Command execution timeout (seconds) |
| `MEMORY_STORAGE_DIR` | `.agent_memory` | Session storage directory |

## Project Structure

```
coding-agent/
├── src/
│   ├── agent.py          # Main agent logic with contextual awareness
│   ├── tools.py           # File/shell operations with workspace support
│   ├── state.py           # State management & conversation types
│   ├── memory.py          # Session persistence & management
│   └── config.py          # Configuration management
├── interface/
│   └── cli.py             # Rich CLI interface with multi-line support
├── agent_runs/            # Default workspace directory
├── .agent_memory/         # Session storage
├── main.py                # Entry point
├── requirements.txt       
├── .env                   # Configuration file (optional)
└── README.md
```

## Key Improvements

### **Contextual Awareness**
- Agent remembers conversation history and file context
- Understands references like "that file" or "operations.py"
- Maintains context across multi-turn conversations

### **Workspace Management**
- All files created in dedicated workspace directory
- Commands execute in workspace context automatically
- Clean separation between agent work and project files

### **Enhanced CLI**
- Multi-line input mode for complex requests
- Session management with persistent history
- Rich formatting and helpful commands
- Configuration display and management

### **Robust Error Handling**
- Graceful handling of file operations
- Detailed error reporting with suggestions
- Session state preservation on errors
- Timeout protection for long-running commands

## Development

This implementation follows the "Build Small, Ship Fast" philosophy with incremental enhancements:

- **Phase 1**: Basic CRUD operations ✅
- **Phase 2**: Contextual awareness ✅
- **Phase 3**: Workspace management ✅
- **Phase 4**: Enhanced CLI ✅
- **Phase 5**: Advanced features (in progress)

See `coding-agent-design.md` for the full design document and roadmap.

## Troubleshooting

### **Common Issues**

**Command not found errors:**
- Commands execute in workspace directory by default
- Use relative paths from workspace (e.g., `pytest tests.py` not `pytest agent_runs/tests.py`)

**Interactive output not showing:**
- Progress bars and animations appear in your terminal, not in agent UI
- This is expected behavior for interactive terminal features

**Session context lost:**
- Use `sessions` command to list available sessions
- Use `session <id>` to switch to a specific session
- Each session maintains its own conversation history

**Configuration not loading:**
- Ensure `.env` file is in project root
- Check that environment variables are properly set
- Use `config` command to verify current settings
