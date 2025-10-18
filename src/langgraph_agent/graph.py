"""
Main LangGraph definition for 2-agent orchestration.

Flow: Router → Planning Agent → Execution Agent → Output
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.router import router_node
from .nodes.planning import planning_node
from .nodes.execution import execution_node
from .nodes.reflection import reflection_node
from .nodes.output import output_node
from .memory import get_memory


def route_after_router(state: AgentState) -> str:
    """Route based on router decision."""
    next_action = state.get("next_action", "plan")
    
    if next_action == "plan":
        return "planning"
    elif next_action == "execute":
        return "execution"
    else:
        return "planning"  # Default to planning


def route_after_execution(state: AgentState) -> str:
    """Route after execution based on success/failure."""
    next_action = state.get("next_action", "complete")
    
    if next_action == "reflect":
        return "reflection"
    else:
        return "output"


def route_after_reflection(state: AgentState) -> str:
    """Route after reflection based on retry strategy."""
    next_action = state.get("next_action", "complete")
    
    if next_action == "replan":
        return "planning"
    elif next_action == "execute":
        return "execution"
    else:
        return "output"


def create_langgraph_agent(with_memory: bool = True, storage_dir: str = None):
    """
    Create 2-agent LangGraph system with memory.
    
    Architecture:
    - Planning Agent: LLM-based plan generation
    - Execution Agent: LLM-based tool execution
    - Memory: Automatic checkpointing via LangGraph
    
    Flow: Router → Planning → Execution → Output → END
    
    Args:
        with_memory: Enable persistent memory (default: True)
        storage_dir: Directory for checkpoint storage (uses config default if None)
        
    Returns:
        Compiled LangGraph agent
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("output", output_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add edges
    workflow.add_conditional_edges("router", route_after_router)
    workflow.add_edge("planning", "execution")
    workflow.add_conditional_edges("execution", route_after_execution)
    workflow.add_conditional_edges("reflection", route_after_reflection)
    workflow.add_edge("output", END)
    
    # Compile with or without memory
    if with_memory:
        memory = get_memory(storage_dir)
        return workflow.compile(checkpointer=memory.checkpointer)
    else:
        return workflow.compile()



