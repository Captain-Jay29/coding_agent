# LangGraph Coding Agent - Simplified Implementation Plan

## 🎯 Core Philosophy
**Build Small, Ship Fast, Iterate Often**

The goal is to create a **single, efficient agent** that can perform CRUD operations on a codebase through natural conversation. We'll start with the absolute minimum and add complexity only when needed.

## 🏗️ Simplified Architecture

```
User Input → Single ReAct Agent → Tools → File System
                ↑                    ↓
                └──── Memory ────────┘
```

No multi-agent complexity initially. Just one smart agent with good tools and memory.

## 📁 Minimal Project Structure

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
│   ├── test_suite.py      # LangSmith evaluation suite
│   └── datasets/          # Test cases & expected outputs
├── main.py                # Entry point
├── requirements.txt       
└── README.md
```

### File Specifications

#### `src/agent.py`
**Purpose**: Core agent using LangGraph's create_react_agent
**Input**: User messages, conversation history
**Output**: Agent responses with executed actions
```python
# Key responsibilities:
# - Initialize ReAct agent with tools
# - Handle conversation flow
# - Manage state transitions
# - Error recovery
```

#### `src/tools.py`
**Purpose**: Simple, safe file and shell operations
**Input**: Operation requests (read, write, execute)
**Output**: Operation results or error messages
```python
# Core tools only:
# - read_file(path) → content
# - write_file(path, content) → success/error
# - edit_file(path, old, new) → success/error
# - run_command(cmd) → output
# - list_files(pattern) → file_list
```

#### `src/state.py`
**Purpose**: Define minimal agent state
**Input**: Current state, new events
**Output**: Updated state
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]  # Conversation history
    current_files: Dict[str, str]  # Files being worked on
    last_command_output: Optional[str]  # Last shell output
```

#### `src/memory.py`
**Purpose**: Simple persistence for conversations
**Input**: Thread ID, state
**Output**: Saved/loaded state
```python
# Using InMemorySaver initially, upgrade to Redis later
# Simple thread-based persistence
```

#### `interface/cli.py`
**Purpose**: Minimal interactive CLI
**Input**: User commands
**Output**: Formatted agent responses
```python
# Simple REPL loop with:
# - Colored output
# - File change previews
# - Confirmation prompts for destructive ops
```

## 🚀 Incremental Build Strategy

### Phase 1: MVP (2 hours)
**Goal**: Agent that can read/write single files

1. **Setup** (30 min)
   - Project structure
   - Dependencies (langgraph, langchain, click)
   - Basic configuration

2. **Core Agent** (1 hour)
   ```python
   # Minimal working agent
   from langgraph.prebuilt import create_react_agent
   
   agent = create_react_agent(
       model=ChatOpenAI(temperature=0),
       tools=[read_file, write_file],
       checkpointer=MemorySaver()
   )
   ```

3. **Basic CLI** (30 min)
   - Simple input/output loop
   - Display file changes
   - Basic error handling

**Success Criteria**: Can create a "Hello World" Python file through conversation

### Phase 2: Enhanced Operations (1 hour)
**Goal**: Multi-file editing and shell commands

1. Add more tools:
   - `edit_file` (partial file updates)
   - `run_command` (with safety checks)
   - `search_files` (grep-like functionality)

2. Improve state management:
   - Track multiple files in context
   - Remember command outputs
   - Add undo capability

**Success Criteria**: Can create a simple web app (HTML/CSS/JS) and run a local server

### Phase 3: Smart Context (30 mins)
**Goal**: Intelligent file selection and error recovery

1. Context-aware file loading:
   ```python
   def smart_context(query: str, project_root: str):
       # Only load relevant files based on query
       # Use simple heuristics (file extensions, imports)
   ```

2. Error recovery:
   ```python
   def handle_error(error: Exception, context: State):
       # Try to fix syntax errors
       # Suggest missing imports
       # Retry with modifications
   ```

**Success Criteria**: Can debug and fix a broken Python script

### Phase 4: Production Features (30 mins)
**Goal**: Safety and persistence

1. Add safety features:
   - Confirmation for destructive operations
   - Rollback capability
   - Git integration (optional)

2. Improve memory:
   - Persist across sessions
   - User preferences
   - Project-specific context

**Success Criteria**: Safe for use on real projects

## 🧪 Evaluation Strategy with LangSmith

### Setup
```python
from langsmith import Client
from langsmith.evaluation import evaluate

client = Client()

# Create dataset
dataset = client.create_dataset(
    "coding-agent-tasks",
    description="CRUD operations for coding agent"
)
```

### Test Cases

#### Level 1: Basic Operations
```python
test_cases = [
    {
        "input": "Create a file called hello.py with a main function",
        "expected": {
            "file_created": True,
            "has_main_function": True,
            "syntax_valid": True
        }
    },
    {
        "input": "Read the contents of hello.py",
        "expected": {
            "file_read": True,
            "content_returned": True
        }
    }
]
```

#### Level 2: Multi-file Operations
```python
test_cases = [
    {
        "input": "Create a Flask app with routes for user CRUD",
        "expected": {
            "files_created": ["app.py", "models.py", "routes.py"],
            "imports_correct": True,
            "routes_defined": ["GET", "POST", "PUT", "DELETE"]
        }
    }
]
```

#### Level 3: Debugging & Fixes
```python
test_cases = [
    {
        "input": "Fix the syntax error in broken.py",
        "context": {"broken.py": "def hello(\n    print('unclosed"},
        "expected": {
            "syntax_fixed": True,
            "file_runnable": True
        }
    }
]
```

### Evaluation Metrics

```python
def evaluate_agent():
    results = evaluate(
        agent.invoke,
        data=dataset_name,
        evaluators=[
            accuracy,  # Did it complete the task?
            relevance,  # Were actions relevant?
            safety,    # No destructive unintended ops
            efficiency # Minimal tool calls
        ]
    )
    
    # Custom metrics
    metrics = {
        "task_completion_rate": sum(r.success for r in results) / len(results),
        "average_tool_calls": np.mean([r.tool_calls for r in results]),
        "error_recovery_rate": sum(r.recovered for r in results) / sum(r.had_error for r in results)
    }
```

### Continuous Improvement
```python
# Log all interactions to LangSmith
@trace
async def agent_interaction(user_input: str):
    result = await agent.ainvoke(user_input)
    
    # Auto-log to LangSmith for analysis
    log_feedback(
        run_id=result.run_id,
        score=calculate_score(result),
        comment=auto_review(result)
    )
```

## 💡 Key Design Principles

### 1. **Simplicity First**
- Single agent, not multi-agent system
- Minimal state management
- Clear tool boundaries
- No premature optimization

### 2. **Safe by Default**
```python
SAFE_OPERATIONS = ["read", "list", "search"]
CONFIRM_OPERATIONS = ["write", "delete", "execute"]

async def execute_tool(tool_name, args):
    if tool_name in CONFIRM_OPERATIONS and not auto_approve:
        if not await get_user_confirmation():
            return "Operation cancelled by user"
    return await tool.invoke(args)
```



### 3. **Efficient Context Management**
```python
# Don't load entire codebase
MAX_FILES_IN_CONTEXT = 5
MAX_FILE_SIZE = 10000  # characters

def load_context(files: List[str]):
    # Only load what's needed
    context = {}
    for file in files[:MAX_FILES_IN_CONTEXT]:
        content = read_file(file)
        if len(content) > MAX_FILE_SIZE:
            content = content[:MAX_FILE_SIZE] + "... (truncated)"
        context[file] = content
    return context
```

### 4. **Clear Feedback**
```python
def format_operation_result(operation, result):
    if operation == "write_file":
        return f"✅ Created: {result.filename}\n📝 Preview:\n{result.preview[:200]}"
    elif operation == "run_command":
        return f"⚡ Executed: {result.command}\n📤 Output:\n{result.output}"
```

## 🏁 Getting Started Guide

### Week 1: MVP
1. **Day 1-2**: Implement basic agent with read/write
2. **Day 3**: Add CLI interface
3. **Day 4**: Add edit and execute tools
4. **Day 5**: Setup LangSmith evaluation

### Week 2: Polish
1. **Day 1-2**: Add safety features
2. **Day 3**: Implement smart context
3. **Day 4**: Add memory persistence
4. **Day 5**: Run full evaluation suite

### Success Metrics
- ✅ Can perform all CRUD operations
- ✅ Maintains conversation context
- ✅ Handles errors gracefully
- ✅ 90%+ task completion rate on test suite
- ✅ Average < 5 tool calls per task
- ✅ Zero destructive operations without confirmation

## 🎁 Optional Enhancements (Only After MVP)

1. **Streaming Response**: Show real-time progress
2. **Diff Preview**: Show changes before applying
3. **Project Templates**: Quick scaffolding
4. **Auto-complete**: Suggest completions
5. **Web UI**: Simple FastAPI interface

## 📝 Example Interaction

You: Create a simple todo app in Python

Agent: I'll create a simple todo app in Python with basic CRUD operations.

[Planning] Creating app.py with Todo class and main functions...

✅ Created: app.py
📝 Preview:
```python
class Todo:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append({"id": len(self.tasks) + 1, "task": task, "done": False})
```

Would you like me to add more features like task completion or persistence?

You: Yes, add persistence to a JSON file

Agent: I'll add JSON persistence to save and load tasks.

[Modifying] Updating app.py with save/load functionality...

✅ Modified: app.py
📝 Changes:
+ import json
+ def save_to_file(self, filename="todos.json"):
+ def load_from_file(self, filename="todos.json"):

Would you like me to test the app?

## Key Takeaway

**Start with one agent that does a few things really well, rather than multiple agents that add complexity.** We can always add more sophisticated patterns later, but a simple, reliable agent that ships quickly is better than a complex system that takes forever to build.

## ⚠️ Error Handling & Recovery Strategy

### 🧩 Phase 1–2 (MVP)
In the initial version, the focus is **stability and observability**, not auto-repair.  
The agent will:
- Catch and log all tool execution errors (file, shell, memory, etc.)
- Report human-readable errors in the CLI
- Persist error context (tool name, message, traceback) in the conversation state
- Continue operation gracefully without crashing

This ensures clear visibility into what failed and why, while keeping the core simple and reliable.

```python
def safe_execute(tool, *args, **kwargs):
    try:
        return tool(*args, **kwargs)
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
```

### 🧠 Phase 3+ (Enhanced Recovery)

Once the base agent is stable, intelligent recovery will be added:

- Auto-detection of common issues (syntax errors, missing imports, bad commands)
- LLM-guided fixes using context from previous steps
- Retry policies for transient failures (timeouts, dependency installs)
- Optional user approval before automated repairs

This staged approach keeps early iterations predictable while setting up a clear path toward self-correcting, resilient agent behavior.
