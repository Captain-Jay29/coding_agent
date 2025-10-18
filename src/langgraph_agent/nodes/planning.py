"""
Planning Node - Calls Planning Agent to generate execution plan.
"""

from ..state import AgentState
from ..agents.planning_agent import PlanningAgent


# Global instance to avoid recreating
_planning_agent = None

def get_planning_agent():
    global _planning_agent
    if _planning_agent is None:
        _planning_agent = PlanningAgent()
    return _planning_agent


def planning_node(state: AgentState) -> AgentState:
    """Generate execution plan using Planning Agent."""
    agent = get_planning_agent()
    
    # Build context including error information if re-planning
    context = {
        "messages": state.get("messages", []),
        "retry_count": state.get("retry_count", 0),
        "previous_errors": None
    }
    
    # If re-planning, include error information
    if state.get("retry_count", 0) > 0:
        execution_results = state.get("execution_results", [])
        failed_steps = [r for r in execution_results if not r.get("success")]
        if failed_steps:
            context["previous_errors"] = [
                f"Step {r['step']}: {r.get('error', 'Unknown error')}"
                for r in failed_steps
            ]
    
    # Create plan from user input
    user_input = state["user_input"]
    if context["previous_errors"]:
        # Add error context to input for re-planning
        user_input = f"{user_input}\n\nPrevious attempt failed with errors:\n" + \
                     "\n".join(context["previous_errors"][:3])
    
    plan = agent.create_plan(user_input, context=context)
    
    return {
        **state,
        "plan": plan,
        "next_action": "execute"
    }

