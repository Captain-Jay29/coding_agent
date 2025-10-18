"""
Execution Node - Calls Execution Agent to execute planned steps.
"""

from ..state import AgentState
from ..agents.execution_agent import ExecutionAgent


# Global instance
_execution_agent = None

def get_execution_agent():
    global _execution_agent
    if _execution_agent is None:
        _execution_agent = ExecutionAgent()
    return _execution_agent


def execution_node(state: AgentState) -> AgentState:
    """Execute planned steps using Execution Agent."""
    agent = get_execution_agent()
    
    # Execute the plan
    plan = state.get("plan", [])
    execution_results, files_modified = agent.execute_plan(plan)
    
    # Count tool calls
    tool_call_count = len(execution_results)
    
    # Check for errors - only consider it an error if success is explicitly False
    has_errors = any(r.get("success") is False for r in execution_results)
    
    # Only reflect if there are actual errors AND we haven't exceeded retry count
    retry_count = state.get("retry_count", 0)
    next_action = "reflect" if has_errors else "complete"
    
    return {
        **state,
        "execution_results": execution_results,
        "files_modified": files_modified,
        "tool_call_count": tool_call_count,
        "next_action": next_action
    }

