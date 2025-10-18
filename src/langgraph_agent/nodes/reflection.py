"""
Reflection Node - Analyzes errors and determines retry strategy.
Simple, efficient error analysis and recovery.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import config
from ..state import AgentState


def reflection_node(state: AgentState) -> AgentState:
    """
    Analyze execution failures and decide next action.
    
    Strategies:
    1. Re-plan: If error suggests wrong approach
    2. Retry: If error is transient (network, etc.)
    3. Give up: If max retries exceeded
    """
    execution_results = state.get("execution_results", [])
    retry_count = state.get("retry_count", 0)
    max_retries = config.get_max_retry()
    
    # Find failed steps
    failed_steps = [r for r in execution_results if not r.get("success")]
    
    if not failed_steps:
        # No failures, shouldn't be here
        return {**state, "next_action": "complete"}
    
    # Check retry limit
    if retry_count >= max_retries:
        return {
            **state,
            "next_action": "complete",
            "response": f"❌ Max retries ({max_retries}) exceeded. Last errors:\n" + 
                       "\n".join([f"- {r['error']}" for r in failed_steps[:3]])
        }
    
    # Analyze errors to decide strategy
    errors = [r.get("error", "") for r in failed_steps]
    error_text = " ".join(errors).lower()
    
    # Determine if we should re-plan or retry
    replan_keywords = [
        "no such file",
        "not found",
        "module",
        "import",
        "syntax error",
        "command not found"
    ]
    
    should_replan = any(keyword in error_text for keyword in replan_keywords)
    
    if should_replan:
        # Re-plan with error context
        return {
            **state,
            "next_action": "replan",
            "retry_count": retry_count + 1,
            "reflection_notes": [
                f"Retry {retry_count + 1}/{max_retries}",
                f"Errors detected: {', '.join(errors[:2])}",
                "Strategy: Re-planning with error context"
            ]
        }
    else:
        # Retry same plan (transient error)
        return {
            **state,
            "next_action": "execute",
            "retry_count": retry_count + 1,
            "reflection_notes": [
                f"Retry {retry_count + 1}/{max_retries}",
                "Strategy: Retrying same plan (transient error)"
            ]
        }

