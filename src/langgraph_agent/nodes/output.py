"""
Output Node - Format final response to user.
"""

from langchain_core.messages import HumanMessage, AIMessage
from ..state import AgentState


def output_node(state: AgentState) -> AgentState:
    """Format execution results into user-friendly response."""
    plan = state.get("plan", [])
    execution_results = state.get("execution_results", [])
    files_modified = state.get("files_modified", [])
    
    response_parts = []
    
    # Summary
    success_count = sum(1 for r in execution_results if r["success"])
    total_count = len(execution_results)
    
    if success_count == total_count and total_count > 0:
        response_parts.append(f"✅ Completed all {total_count} steps successfully!")
    elif success_count > 0:
        response_parts.append(f"⚠️  Completed {success_count}/{total_count} steps")
    else:
        response_parts.append("❌ Execution failed")
    
    # Show plan steps with results
    response_parts.append("\n📋 Execution Details:")
    for i, (step_plan, result) in enumerate(zip(plan, execution_results), 1):
        status = "✅" if result["success"] else "❌"
        desc = step_plan.get("description", step_plan["action"])
        response_parts.append(f"{status} Step {i}: {desc}")
        
        # Show result or error
        if result["success"] and result.get("result"):
            # Truncate long results
            result_text = str(result["result"])
            if len(result_text) > 200:
                result_text = result_text[:200] + "..."
            response_parts.append(f"   → {result_text}")
        elif not result["success"] and result.get("error"):
            response_parts.append(f"   → Error: {result['error']}")
    
    # Files modified
    if files_modified:
        response_parts.append(f"\n📁 Files modified: {', '.join(files_modified)}")
    
    response = "\n".join(response_parts)
    
    # Update conversation history
    messages = list(state.get("messages", []))
    
    # Add user input to history
    user_input = state.get("user_input", "")
    if user_input:
        messages.append(HumanMessage(content=user_input))
    
    # Add assistant response to history (concise version)
    summary = f"Completed {success_count}/{total_count} steps."
    if files_modified:
        summary += f" Modified: {', '.join(files_modified)}"
    messages.append(AIMessage(content=summary))
    
    # Keep only last 10 messages (5 turns) to avoid context bloat
    if len(messages) > 10:
        messages = messages[-10:]
    
    return {
        **state,
        "response": response,
        "messages": messages,
        "next_action": "complete"
    }

