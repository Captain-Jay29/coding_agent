# Coding Agent

A simple coding agent built with LangGraph that can perform CRUD operations on codebases through natural conversation.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

## Features

- **File Operations**: Read, write, edit files
- **Shell Commands**: Execute commands safely
- **Session Management**: Persistent conversation history
- **Error Handling**: Graceful error recovery
- **Simple CLI**: Clean, colored interface

## Usage Examples

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

## Project Structure

```
coding-agent/
├── src/
│   ├── agent.py          # Main agent logic (ReAct pattern)
│   ├── tools.py           # File/shell operations 
│   ├── state.py           # State management & types
│   └── memory.py          # Conversation persistence
├── interface/
│   └── cli.py             # Simple CLI interface
├── evals/
│   └── datasets/          # Test cases & expected outputs
├── main.py                # Entry point
├── requirements.txt       
└── README.md
```

## Development

This is an MVP implementation following the "Build Small, Ship Fast" philosophy. The agent starts simple and can be enhanced incrementally.

See `coding-agent-design.md` for the full design document and roadmap.
