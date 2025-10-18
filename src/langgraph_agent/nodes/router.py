"""
Router Node - Entry point that routes to planning or execution.
Simple routing logic.
"""

from ..state import AgentState


def router_node(state: AgentState) -> AgentState:
    """
    Route to planning for complex tasks, direct execution for simple ones.
    
    Simple heuristic: Always route to planning for consistency.
    Planning agent will create even single-step plans.
    """
    user_input = state["user_input"]
    
    # For now, always plan (keeps it simple)
    # Planning agent handles both simple and complex tasks
    next_action = "plan"
    
    return {
        **state,
        "next_action": next_action
    }

