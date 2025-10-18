"""
State schema for LangGraph 2-agent orchestration.
Clean, minimal structure following guideline.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class PlanStep(TypedDict):
    """Single step in execution plan."""
    step: int
    action: str  # Tool name: write_file, run_command, etc.
    args: Dict[str, Any]  # Tool arguments
    description: str  # Human-readable description


class ExecutionResult(TypedDict):
    """Result of executing a step."""
    step: int
    success: bool
    result: Optional[str]
    error: Optional[str]


class AgentState(TypedDict):
    """State for 2-agent LangGraph system."""
    # User Input/Output
    user_input: str
    response: str
    
    # Planning (from Planning Agent)
    plan: List[PlanStep]
    
    # Execution (from Execution Agent)
    execution_results: List[ExecutionResult]
    files_modified: List[str]
    
    # Conversation Context
    messages: List[BaseMessage]
    session_id: str
    
    # Control Flow
    next_action: str  # "plan", "execute", "reflect", "replan", "complete"
    
    # Retry & Reflection
    retry_count: int
    reflection_notes: List[str]
    
    # Metadata
    tool_call_count: int

