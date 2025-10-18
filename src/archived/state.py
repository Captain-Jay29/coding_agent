"""
State management for the coding agent.
Defines the minimal agent state structure.
"""

from typing import TypedDict, List, Dict, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Minimal agent state for conversation and context management."""
    
    # Core conversation
    messages: List[BaseMessage]
    
    # File context
    current_files: Dict[str, str]  # filename -> content
    
    # Last operation results
    last_command_output: Optional[str]
    last_error: Optional[Dict[str, str]]  # error details
    
    # Retry tracking
    retry_count: int  # Current retry attempt for this turn
    retry_history: List[Dict[str, str]]  # History of retry attempts with errors
    
    # Session metadata
    session_id: str
    created_at: datetime
    last_updated: datetime


class ToolResult(TypedDict):
    """Standardized result structure for all tools."""
    
    success: bool
    data: Optional[any]
    error: Optional[str]
    error_type: Optional[str]
    suggestions: Optional[List[str]]
    metadata: Optional[Dict[str, any]]


def create_initial_state(session_id: str) -> AgentState:
    """Create a new agent state for a session."""
    now = datetime.now()
    
    return AgentState(
        messages=[],
        current_files={},
        last_command_output=None,
        last_error=None,
        retry_count=0,
        retry_history=[],
        session_id=session_id,
        created_at=now,
        last_updated=now
    )


def update_state_timestamp(state: AgentState) -> AgentState:
    """Update the last_updated timestamp in the state."""
    state["last_updated"] = datetime.now()
    return state


def reset_retry_state(state: AgentState) -> AgentState:
    """Reset retry counter and history for a new user message."""
    state["retry_count"] = 0
    state["retry_history"] = []
    return state


def increment_retry_count(state: AgentState, error_info: Dict[str, str]) -> AgentState:
    """Increment retry count and add error to history."""
    state["retry_count"] += 1
    state["retry_history"].append({
        "attempt": state["retry_count"],
        "error": error_info.get("error", "Unknown error"),
        "error_type": error_info.get("error_type", "Unknown"),
        "timestamp": datetime.now().isoformat()
    })
    return state
