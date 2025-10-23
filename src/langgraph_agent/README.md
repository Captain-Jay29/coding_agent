# LangGraph Agent

A sophisticated 2-agent coding assistant built with LangGraph for advanced orchestration, planning, and execution.

## Architecture Overview

### Graph Structure
```
Router → Planning → Execution → Reflection → Output → END
```

**Flow Control:**
- **Router**: Entry point that routes to planning or direct execution
- **Planning**: Generates structured execution plans
- **Execution**: Executes planned steps using tools
- **Reflection**: Analyzes failures and determines retry strategy
- **Output**: Formats final response

### Agent Hierarchy

#### 1. Planning Agent (`agents/planning_agent.py`)
- **Purpose**: Breaks down user requests into atomic, executable steps
- **Input**: User request + context (messages, retry info, previous errors)
- **Output**: Structured plan with steps, actions, and arguments
- **LLM**: ChatOpenAI with specialized planning prompts

#### 2. Execution Agent (`agents/execution_agent.py`)
- **Purpose**: Executes planned steps using LangChain tools
- **Input**: Structured plan from Planning Agent
- **Output**: Execution results with success/failure status
- **Tools**: File operations, shell commands, Git operations
- **LLM**: ChatOpenAI with AgentExecutor for tool calling

### State Management

#### AgentState (`state.py`)
```python
class AgentState(TypedDict):
    # User Input/Output
    user_input: str
    response: str
    
    # Planning
    plan: List[PlanStep]
    
    # Execution
    execution_results: List[ExecutionResult]
    files_modified: List[str]
    
    # Context
    messages: List[BaseMessage]
    session_id: str
    
    # Control Flow
    next_action: str  # "plan", "execute", "reflect", "replan", "complete"
    
    # Retry & Reflection
    retry_count: int
    reflection_notes: List[str]
    
    # Metadata
    tool_call_count: int
```

### Memory System

#### LangGraph Memory (`memory.py`)
- **Checkpointing**: Uses LangGraph's built-in `MemorySaver`
- **Session Management**: Thread-based session isolation
- **Persistence**: In-memory checkpointing with configurable storage
- **Integration**: Seamless integration with LangGraph's state management

### Routing Logic

#### Conditional Edges
1. **`route_after_router()`**: Routes to planning or execution based on complexity
2. **`route_after_execution()`**: Routes to reflection on errors, output on success
3. **`route_after_reflection()`**: Routes to replanning, execution, or completion

#### Routing Decisions
- **Router → Planning**: Always (for consistency)
- **Planning → Execution**: Always (execute generated plan)
- **Execution → Reflection**: On errors with retry count < max
- **Execution → Output**: On success or max retries exceeded
- **Reflection → Planning**: On replan decision
- **Reflection → Execution**: On retry decision
- **Reflection → Output**: On completion decision

### Streaming Support

#### Real-time Events (`streaming.py`)
- **Node Events**: `node_start`, `node_end` for each graph node
- **Token Streaming**: Real-time LLM token output
- **Tool Events**: `tool_start`, `tool_end` for tool execution
- **Error Handling**: Graceful error reporting

#### Event Types
```python
# Node execution
{"type": "node_start", "node": "planning"}
{"type": "node_end", "node": "execution"}

# Token streaming
{"type": "token", "content": "Hello"}

# Tool execution
{"type": "tool_start", "tool": "write_file"}
{"type": "tool_end", "tool": "write_file", "output": "Success"}

# Completion
{"type": "complete", "state": {...}}
```

## Usage

### Basic Usage
```python
from src.langgraph_agent import create_langgraph_agent, stream_simple

# Create agent with memory
agent = create_langgraph_agent(with_memory=True)

# Stream response
async for token in stream_simple(agent, "Create a calculator", "session-1"):
    print(token, end="")
```

### Advanced Usage
```python
from src.langgraph_agent import stream_agent_response

# Full event streaming
async for event in stream_agent_response(agent, initial_state, "session-1"):
    if event["type"] == "node_start":
        print(f"Starting {event['node']}")
    elif event["type"] == "token":
        print(event["content"], end="")
```

## Key Features

### 1. **Intelligent Planning**
- Breaks complex tasks into atomic steps
- Handles error context for re-planning
- Structured plan format with tool arguments

### 2. **Robust Execution**
- Tool-based execution with error handling
- File modification tracking
- Success/failure result tracking

### 3. **Reflection & Retry**
- Automatic error analysis
- Intelligent retry strategies
- Context-aware re-planning

### 4. **Memory & Persistence**
- Session-based state management
- Automatic checkpointing
- Conversation history preservation

### 5. **Real-time Streaming**
- Token-by-token LLM output
- Node execution progress
- Tool execution feedback

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your-api-key
DEFAULT_MODEL=gpt-4o-mini
MODEL_TEMPERATURE=0.0
MEMORY_STORAGE_DIR=.agent_memory
```

### Graph Compilation
```python
# With memory (default)
agent = create_langgraph_agent(with_memory=True)

# Without memory
agent = create_langgraph_agent(with_memory=False)

# Custom storage
agent = create_langgraph_agent(storage_dir="/custom/path")
```

## Comparison with Single Agent

| Feature | Single Agent | LangGraph Agent |
|---------|-------------|-----------------|
| **Architecture** | Monolithic | Multi-agent orchestration |
| **Planning** | Implicit | Explicit planning phase |
| **Error Handling** | Retry loop | Reflection + re-planning |
| **Memory** | Custom JSON | LangGraph checkpointing |
| **Streaming** | Token-only | Node + token + tool events |
| **State Management** | Manual | Automatic via LangGraph |
| **Complexity** | Simple | Advanced orchestration |

## Benefits

1. **Separation of Concerns**: Planning and execution are distinct phases
2. **Better Error Recovery**: Reflection phase enables intelligent retry strategies
3. **Structured Execution**: Plans provide clear step-by-step execution
4. **Advanced Memory**: LangGraph's built-in checkpointing and state management
5. **Rich Streaming**: Multiple event types for better user experience
6. **Scalability**: Easy to add new nodes and routing logic

## File Structure

```
langgraph_agent/
├── __init__.py              # Main exports
├── graph.py                 # Graph definition and routing
├── state.py                 # State schema
├── memory.py                # Memory management
├── streaming.py             # Streaming support
├── agents/
│   ├── planning_agent.py    # Planning Agent implementation
│   └── execution_agent.py   # Execution Agent implementation
└── nodes/
    ├── router.py            # Router node
    ├── planning.py          # Planning node
    ├── execution.py         # Execution node
    ├── reflection.py        # Reflection node
    └── output.py            # Output node
```

This LangGraph agent represents a significant advancement over the single-agent approach, providing better structure, error handling, and user experience through intelligent orchestration.