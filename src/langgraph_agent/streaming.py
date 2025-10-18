"""
Streaming support for LangGraph agent.
Simple, efficient token-by-token streaming.
"""

from typing import AsyncIterator, Dict, Any
from .state import AgentState
from .memory import get_memory


async def stream_agent_response(
    agent,
    initial_state: AgentState,
    session_id: str = None
) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream agent execution with real-time updates.
    
    Yields events:
    - node_start: When a node begins
    - node_end: When a node completes
    - token: Individual tokens from LLM
    - complete: Final result
    - error: If something fails
    """
    try:
        # Get config for session
        config = None
        if session_id:
            memory = get_memory()
            config = memory.get_config(session_id)
        
        final_state = None
        
        # Stream events from graph - this already executes the graph!
        async for event in agent.astream_events(initial_state, config=config, version="v2"):
            event_type = event.get("event")
            
            # Capture final output
            if event_type == "on_chain_end":
                node_name = event.get("name", "")
                # Capture the final state from the last chain end
                if "output" in event.get("data", {}):
                    output = event["data"]["output"]
                    if isinstance(output, dict) and "response" in output:
                        final_state = output
                
                if node_name in ["router", "planning", "execution", "reflection", "output"]:
                    yield {
                        "type": "node_end",
                        "node": node_name,
                        "data": event.get("data", {})
                    }
            
            # Node execution events
            elif event_type == "on_chain_start":
                node_name = event.get("name", "")
                if node_name in ["router", "planning", "execution", "reflection", "output"]:
                    yield {
                        "type": "node_start",
                        "node": node_name,
                        "data": {}
                    }
            
            # LLM token streaming
            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content"):
                    content = chunk.content
                    if content:
                        yield {
                            "type": "token",
                            "content": content
                        }
            
            # Tool execution
            elif event_type == "on_tool_start":
                tool_name = event.get("name", "")
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "inputs": event.get("data", {}).get("input", {})
                }
            
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "")
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": event.get("data", {}).get("output")
                }
        
        # Yield completion with captured state
        yield {
            "type": "complete",
            "state": final_state
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


async def stream_simple(
    agent,
    user_input: str,
    session_id: str = None
) -> AsyncIterator[str]:
    """
    Simple streaming - just yields text tokens.
    
    For CLI display where you just want the text output.
    """
    # Only set NEW values - checkpointer will restore previous state (like messages)
    initial_state = {
        "user_input": user_input,
        "session_id": session_id or "default",
        "response": "",
        "plan": [],
        "execution_results": [],
        "files_modified": [],
        "next_action": "",
        "tool_call_count": 0,
        "retry_count": 0,
        "reflection_notes": []
        # Note: "messages" is NOT reset - checkpointer restores it
    }
    
    current_node = None
    
    async for event in stream_agent_response(agent, initial_state, session_id):
        event_type = event.get("type")
        
        if event_type == "node_start":
            node = event.get("node")
            current_node = node
            # Emit node markers
            if node == "planning":
                yield "\n🎯 Planning..."
            elif node == "execution":
                yield "\n⚡ Executing..."
            elif node == "reflection":
                yield "\n🔄 Reflecting on errors..."
            elif node == "output":
                yield "\n\n📋 "
        
        elif event_type == "token":
            # Stream LLM tokens
            yield event.get("content", "")
        
        elif event_type == "tool_start":
            tool = event.get("tool")
            yield f"\n🛠️  {tool}"
        
        elif event_type == "complete":
            # Final response
            state = event.get("state", {})
            response = state.get("response", "")
            if response and current_node != "output":
                yield f"\n\n{response}"
        
        elif event_type == "error":
            yield f"\n❌ Error: {event.get('error')}"

