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
        session_id=session_id,
        created_at=now,
        last_updated=now
    )


def update_state_timestamp(state: AgentState) -> AgentState:
    """Update the last_updated timestamp in the state."""
    state["last_updated"] = datetime.now()
    return state
