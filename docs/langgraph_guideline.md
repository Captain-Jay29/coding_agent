# LangGraph Migration Guide

## Overview

This document outlines the migration from LangChain AgentExecutor to LangGraph with a two-agent architecture: **Planning Agent** and **Execution Agent**. The goal is to achieve better control flow, intelligent retry logic, validation, and extensibility.

---

## Current vs Future Architecture

### Current (AgentExecutor)
```
User Input → Single Agent → Tools → Response
                ↑              ↓
                └─ Manual Retry ┘
```

**Limitations:**
- Manual retry logic outside agent loop
- No validation or reflection
- Linear execution flow
- Single monolithic agent
- State management via JSON serialization

### Future (LangGraph)
```
User Input → Planning Agent → Execution Agent → Validation → Response
                  ↓               ↓                ↓
               [Plan]         [Execute]       [Validate]
                                ↓ (error)
                            Reflection → Re-plan → Re-execute
```

**Benefits:**
- Explicit state graph with checkpointing
- Built-in validation and reflection loops
- Separation of concerns (planning vs execution)
- Parallel execution capability
- Human-in-the-loop at any node
- Better observability via LangSmith

---

## System Architecture

### Two-Agent Design

#### **1. Planning Agent**
**Role:** Understands user intent, breaks down tasks, creates execution plan

**Responsibilities:**
- Parse user request and conversation context
- Identify required tools and dependencies
- Generate step-by-step execution plan
- Estimate complexity and risks
- Handle re-planning on failures

**Output:** Structured plan with steps, tools, and order

#### **2. Execution Agent**
**Role:** Executes planned steps, handles tool calls, reports results

**Responsibilities:**
- Execute each step from plan sequentially
- Call appropriate tools (file ops, git, shell)
- Track execution progress and results
- Handle tool errors gracefully
- Report back to validation layer

**Output:** Execution results and any errors encountered

---

## State Schema

### Core State Structure

```python
class AgentState(TypedDict):
    # Input/Output
    user_input: str
    response: str
    
    # Planning
    plan: List[PlanStep]  # [{"step": 1, "action": "create_file", "args": {...}}]
    current_step: int
    
    # Execution
    execution_results: List[ExecutionResult]
    tool_call_count: int
    files_modified: List[str]
    
    # Error Handling & Reflection
    errors: List[ErrorInfo]
    retry_count: int
    reflection_notes: List[str]
    
    # Conversation Context
    messages: List[BaseMessage]
    session_id: str
    
    # Validation
    validation_status: str  # "pending", "passed", "failed"
    validation_results: Dict[str, Any]
    
    # Control Flow
    next_action: str  # "execute", "reflect", "replan", "complete", "interrupt"
    needs_human_approval: bool
```

### State Management Best Practices

1. **Checkpointing:** Save state after each node (automatic with LangGraph)
2. **Immutability:** Nodes return state updates, don't mutate in place
3. **Versioning:** Track state version for debugging and replay
4. **Persistence:** Use LangGraph's built-in SQLite/Postgres persistence

---

## Graph Structure

### Nodes

#### **1. Router Node**
**Purpose:** Entry point, analyzes request and determines flow

**Logic:**
- Check if request is simple (direct execution) or complex (needs planning)
- Route to Planning Agent or skip to Execution Agent
- Check for dangerous operations (git push, file deletion) → flag for human approval

**Output:** `next_action = "plan" | "execute" | "interrupt"`

---

#### **2. Planning Node**
**Purpose:** Planning Agent generates execution plan

**Logic:**
- Analyze user input and conversation history
- Break down task into atomic steps
- Identify required tools for each step
- Check for dependencies (e.g., install before run)
- Estimate risk level (safe, cautious, dangerous)

**Output:** 
```python
state.plan = [
    {"step": 1, "action": "write_file", "args": {"path": "app.py", "content": "..."}},
    {"step": 2, "action": "run_command", "args": {"command": "pytest app.py"}}
]
state.next_action = "execute"
```

**Enhancement:** Can call research tools (search docs, check file existence) to inform plan

---

#### **3. Execution Node**
**Purpose:** Execution Agent runs planned steps

**Logic:**
- Iterate through `state.plan` steps
- For each step:
  - Call appropriate tool with args
  - Capture result and errors
  - Update `execution_results`
- If error occurs: populate `state.errors` and set `next_action = "reflect"`
- If all succeed: set `next_action = "validate"`

**Output:**
```python
state.execution_results = [
    {"step": 1, "success": True, "result": "File created"},
    {"step": 2, "success": False, "error": "ModuleNotFoundError: pytest"}
]
state.next_action = "reflect" | "validate"
```

**Enhancement:** Support parallel execution for independent steps

---

#### **4. Reflection Node**
**Purpose:** Analyze failures and determine recovery strategy

**Logic:**
- Examine `state.errors` to identify root cause
- Check `state.retry_count` against max retries
- Generate reflection notes (what went wrong, what to try)
- Decide: Re-plan, Re-execute specific step, or Give up

**Output:**
```python
state.reflection_notes = [
    "Step 2 failed due to missing pytest dependency",
    "Should add install step before running tests"
]
state.next_action = "replan" | "execute" | "complete"
state.retry_count += 1
```

**Intelligence:** Can call diagnostic tools (check installed packages, file existence, syntax validation)

---

#### **5. Validation Node**
**Purpose:** Verify execution results meet quality standards

**Logic:**
- Run linting on created/modified files
- Execute tests if applicable
- Check git status (no uncommitted files if git workflow)
- Verify file contents match plan intent

**Output:**
```python
state.validation_results = {
    "linting": "passed",
    "tests": "passed",
    "git_clean": True
}
state.validation_status = "passed" | "failed"
state.next_action = "complete" | "reflect"
```

**Enhancement:** Configurable validation rules per project type

---

#### **6. Human Approval Node**
**Purpose:** Interrupt for dangerous operations

**Logic:**
- Check `state.needs_human_approval` flag
- Present context to user (what will happen, preview changes)
- Wait for human response (approve/reject/modify)
- Resume execution or abort

**Triggers:**
- Git push to protected branches
- File deletions
- Running unknown/unsafe commands
- Expensive operations (cloud deployments)

**Output:**
```python
state.next_action = "execute" | "complete"  # Based on human decision
```

---

#### **7. Output Node**
**Purpose:** Format final response to user

**Logic:**
- Summarize what was accomplished
- Include relevant file paths, command outputs
- Report validation results
- Add retry information if retries occurred
- Update conversation messages

**Output:** Final `state.response` for user

---

### Edges (Control Flow)

```
START
  ↓
Router
  ├─→ Planning → Execution → Validation → Output → END
  ├─→ Execution → Validation → Output → END (skip planning)
  └─→ Human Approval → (resume flow)

Execution (on error) → Reflection
                           ↓
                      ├─→ Re-planning → Execution
                      ├─→ Re-execution (same plan)
                      └─→ Output (give up)

Validation (failed) → Reflection → Re-execution
```

**Conditional Edges:**
- `next_action == "reflect"` → Go to Reflection Node
- `next_action == "replan"` → Go back to Planning Node
- `next_action == "execute"` → Go to Execution Node
- `next_action == "validate"` → Go to Validation Node
- `next_action == "interrupt"` → Go to Human Approval Node
- `next_action == "complete"` → Go to Output Node

---

## Implementation Approach

### Phase 1: Basic Graph Setup

1. **Define State Schema** (`state.py`)
   - Create `AgentState` TypedDict
   - Add state update helpers

2. **Create Core Nodes** (`nodes/`)
   - `router.py` - Entry point logic
   - `planning.py` - Planning Agent with LLM
   - `execution.py` - Execution Agent with tool calls
   - `output.py` - Response formatting

3. **Build Graph** (`graph.py`)
   ```python
   from langgraph.graph import StateGraph
   
   workflow = StateGraph(AgentState)
   workflow.add_node("router", router_node)
   workflow.add_node("planning", planning_node)
   workflow.add_node("execution", execution_node)
   workflow.add_node("output", output_node)
   
   workflow.set_entry_point("router")
   workflow.add_conditional_edges("router", route_decision)
   workflow.add_edge("planning", "execution")
   workflow.add_edge("execution", "output")
   workflow.add_edge("output", END)
   
   app = workflow.compile()
   ```

4. **Test Basic Flow**
   - Simple file creation → execution → output
   - Verify state persistence
   - Check LangSmith traces

### Phase 2: Add Reflection & Retry

1. **Add Reflection Node** (`nodes/reflection.py`)
   - Error analysis logic
   - Retry decision logic

2. **Update Graph with Loops**
   ```python
   workflow.add_node("reflection", reflection_node)
   workflow.add_conditional_edges("execution", check_execution_status)
   # If error: route to reflection
   # If success: route to validation
   ```

3. **Implement Re-planning**
   - Reflection can route back to Planning
   - Pass error context to Planning Agent

### Phase 3: Add Validation

1. **Add Validation Node** (`nodes/validation.py`)
   - Linting checks
   - Test execution
   - Git status verification

2. **Connect Validation to Reflection**
   - Failed validation → Reflection → Re-execution

### Phase 4: Add Human-in-the-Loop

1. **Add Human Approval Node** (`nodes/human_approval.py`)
   - Interrupt execution
   - Present preview to user
   - Wait for input

2. **Add Interrupt Points**
   - Git push detection
   - Dangerous command detection
   - User can override with `--auto-approve` flag

---

## Features to Implement

### Core Features (Must-Have)

- [ ] **Two-Agent Architecture**: Planning + Execution agents
- [ ] **Intelligent Retry**: Reflection node with error analysis
- [ ] **Validation Loop**: Automatic linting and testing after execution
- [ ] **Checkpointing**: Save state after each node for crash recovery
- [ ] **Better Observability**: Graph visualization in LangSmith
- [ ] **Human-in-the-Loop**: Interrupt for dangerous operations (git push)
- [ ] **Re-planning**: Failed executions can trigger plan revision

### Enhanced Features (Nice-to-Have)

- [ ] **Parallel Execution**: Execute independent steps simultaneously
- [ ] **Plan Preview**: Show plan to user before execution (optional)
- [ ] **Step-by-Step Mode**: Execute one step at a time with user confirmation
- [ ] **Validation Rules**: Configurable quality checks per project type
- [ ] **Smart Tool Selection**: Only expose relevant tools to each agent
- [ ] **Execution Rollback**: Undo changes if validation fails
- [ ] **Cost Estimation**: Predict token usage and time before execution

### Advanced Features (Future)

- [ ] **Multi-Step Debugging**: Interactive debugging loop for test failures
- [ ] **Iterative Refinement**: Auto-fix linting/test errors until passing
- [ ] **Branch Comparison**: Show diff before git operations
- [ ] **Execution Replay**: Re-run from any checkpoint with different parameters
- [ ] **A/B Testing**: Try multiple plans and pick best result

---

## Migration Strategy

### Step 1: Parallel Implementation
- Keep existing AgentExecutor in `src/agent.py`
- Build LangGraph version in `src/langgraph_agent.py`
- Toggle between implementations via config flag

### Step 2: Feature Parity
- Ensure LangGraph version supports all current features
- Migrate session management
- Update CLI and Web UI to support new flow

### Step 3: Evaluation
- Run eval suite against both implementations
- Compare performance, reliability, token usage
- Test retry logic improvements

### Step 4: Gradual Rollout
- Default to AgentExecutor, opt-in to LangGraph
- Monitor for regressions
- Gather user feedback

### Step 5: Deprecation
- Switch default to LangGraph
- Keep AgentExecutor as fallback for 1-2 releases
- Remove old implementation

---

## Future Extensions

### Additional Agents

#### **Research Agent**
**Purpose:** Search documentation, Stack Overflow, existing codebase

**Use Cases:**
- "How do I use pandas DataFrame?"
- "Find examples of pytest fixtures in our code"
- "What's the latest syntax for FastAPI routes?"

**Integration:** Called by Planning Agent to inform plan

---

#### **Test Agent**
**Purpose:** Dedicated to testing, debugging, and fixing test failures

**Use Cases:**
- Execution fails tests → Test Agent analyzes failures
- Write tests for existing code
- Debug why tests are failing

**Integration:** Called by Reflection Node when tests fail

---

#### **Code Review Agent**
**Purpose:** Review generated code for quality, security, best practices

**Use Cases:**
- Check for security vulnerabilities
- Suggest performance improvements
- Enforce style guidelines

**Integration:** Runs as part of Validation Node

---

#### **Git Agent**
**Purpose:** Specialized in version control workflows

**Use Cases:**
- Manage branches and merges
- Resolve merge conflicts
- Generate commit messages from diffs

**Integration:** Separate branch in graph for git-heavy operations

---

### Additional Nodes

#### **Parallel Execution Node**
Execute independent steps simultaneously for speed

#### **Monitoring Node**
Track long-running operations, provide progress updates

#### **Cache Node**
Store and reuse results from previous executions (e.g., "install dependencies" step)

#### **User Preference Node**
Learn from user feedback and adjust behavior (e.g., always skip plan preview)

#### **Cost Optimization Node**
Choose cheapest model for each step (GPT-4 for planning, GPT-3.5 for execution)

---

### Multi-Agent Orchestration

#### **Hierarchical Approach**
```
              Manager Agent
                    |
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Planning Agent  Execution Agent  Test Agent
```

**Manager** decides which agents to invoke and in what order

#### **Collaborative Approach**
```
Planning Agent → Execution Agent → Review Agent
      ↑               ↓                  ↓
      └───────── Feedback Loop ─────────┘
```

**Review Agent** can request changes from Planning/Execution

#### **Sequential Pipeline**
```
Research → Plan → Execute → Test → Review → Git Commit
```

Each agent perfects one aspect of the workflow

---

## Key Design Decisions

### 1. State Management
**Decision:** Use LangGraph's built-in checkpointing with SQLite/Postgres  
**Rationale:** Better durability, replay capability, no manual JSON serialization

### 2. Agent Separation
**Decision:** Planning and Execution as separate agents (not nodes)  
**Rationale:** Different prompts, tools, and concerns; easier to optimize independently

### 3. Validation Timing
**Decision:** Validate after execution, not during  
**Rationale:** Faster execution; validation failures route to reflection for fixes

### 4. Retry Logic
**Decision:** Reflection node decides retry strategy (not automatic loop)  
**Rationale:** Intelligence in deciding what to retry and how; avoids infinite loops

### 5. Human-in-the-Loop
**Decision:** Interrupt points at graph level (not tool level)  
**Rationale:** Better UX; user sees full context before approval

### 6. Tool Access
**Decision:** All tools available to both agents initially  
**Rationale:** Simplicity; can restrict later if needed for performance

---

## Success Metrics

### Performance
- **Latency:** Should match or improve vs. AgentExecutor
- **Token Usage:** Planning overhead should be < 20% increase
- **Success Rate:** Retry logic should improve task completion by 30%+

### Quality
- **Validation Pass Rate:** 90%+ of executions pass validation
- **Manual Fixes:** Reduce human intervention by 50%
- **Error Recovery:** 80%+ of errors auto-recovered via reflection

### Observability
- **Trace Clarity:** Graph visualization shows clear execution path
- **Debug Time:** Cut debugging time by 50% with checkpointing
- **Replay Usage:** Enable replay for 100% of failed executions

---

## Example Workflow

### User Request: "Create a calculator package with tests and commit it"

#### Step 1: Router
- Analyzes request → Complex, needs planning
- Routes to Planning Agent

#### Step 2: Planning
```python
plan = [
    {"step": 1, "action": "create_directory", "args": {"path": "calculator"}},
    {"step": 2, "action": "write_file", "args": {"path": "calculator/__init__.py", "content": "..."}},
    {"step": 3, "action": "write_file", "args": {"path": "calculator/calculator.py", "content": "..."}},
    {"step": 4, "action": "write_file", "args": {"path": "calculator/tests.py", "content": "..."}},
    {"step": 5, "action": "run_command", "args": {"command": "pytest calculator/tests.py"}},
    {"step": 6, "action": "git_create_branch", "args": {"name": "calculator"}},
    {"step": 7, "action": "git_stage_files", "args": {"files": ["calculator/"]}},
    {"step": 8, "action": "git_commit", "args": {"message": "Add calculator package"}},
    {"step": 9, "action": "git_push", "args": {}}
]
```

#### Step 3: Execution
- Executes steps 1-5 successfully
- Step 5 fails: "ModuleNotFoundError: pytest"
- Routes to Reflection

#### Step 4: Reflection
```python
reflection = "Tests failed due to missing pytest. Need to install dependencies."
retry_strategy = "Add installation step before tests"
next_action = "replan"
```

#### Step 5: Re-planning
```python
updated_plan = [
    # ... existing steps 1-4 ...
    {"step": 5, "action": "run_command", "args": {"command": "pip install pytest"}},
    {"step": 6, "action": "run_command", "args": {"command": "pytest calculator/tests.py"}},
    # ... git steps renumbered ...
]
```

#### Step 6: Re-execution
- All steps succeed
- Routes to Validation

#### Step 7: Validation
- Linting: Pass
- Tests: Pass
- Git status: Clean
- Routes to Output

#### Step 8: Human Approval (Git Push)
- Interrupt before step 9 (git_push)
- Show user: "Ready to push branch 'calculator' with 1 commit"
- User approves
- Resume execution

#### Step 9: Output
```
✅ Created calculator package with tests
✅ All tests passing (3/3)
✅ Committed to branch 'agent/calculator'
✅ Pushed to remote

Files created:
- calculator/__init__.py
- calculator/calculator.py
- calculator/tests.py
```

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Tracing](https://docs.smith.langchain.com/)
- Current: `src/agent.py` (AgentExecutor implementation)
- Current: `docs/streaming_guidelines.md` (Streaming patterns)
- Current: `docs/langsmith_metrics.md` (Observability setup)

---

## Next Steps

1. Review this guideline with team
2. Prototype basic graph (Router → Planning → Execution → Output)
3. Test with simple file operations
4. Iterate and add reflection/validation
5. Run evaluation suite to compare with AgentExecutor
6. Update documentation and examples

