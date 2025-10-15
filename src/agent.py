"""
Main agent logic using LangChain's basic tools.
Simplified version without LangGraph for MVP testing.
"""

import os
import uuid
from typing import Dict, Any, List, AsyncIterator
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

from .tools import TOOLS
from .state import AgentState, create_initial_state, update_state_timestamp
from .memory import memory_manager
from .config import config


class CodingAgent:
    """Main coding agent using LangChain tools."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        """Initialize the coding agent."""
        # Use config values if not provided
        model_config = config.get_model_config()
        model_name = model_name or model_config["model_name"]
        temperature = temperature if temperature is not None else model_config["temperature"]
        
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=config.get_openai_api_key()
        )
        
        # Create a simple prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful coding assistant. You can create, read, edit, and execute files.
            
            WORKSPACE CONTEXT:
            - You are working in a dedicated workspace directory
            - All files you create are stored in this workspace
            - Commands (like pytest, python, etc.) execute FROM the workspace directory
            - When running commands, use relative paths from the workspace (e.g., "pytest calculator/tests.py")
            
            AVAILABLE TOOLS:
            
            File Operations:
            - write_file: Create or overwrite files (paths are relative to workspace)
            - read_file: Read file contents (paths are relative to workspace)
            - edit_file: Modify existing files (paths are relative to workspace)
            - run_command: Execute shell commands (runs IN the workspace directory)
              WARNING: Scripts with input() will hang! Modify them to accept arguments instead.
              Example: Instead of input("Enter n:"), use sys.argv or provide test values.
            - list_files: List files matching a pattern
            - file_exists: Check if a file exists
            - get_file_info: Get file metadata
            
            Git Operations:
            - git_status: Check current git status and see modified/untracked files
            - git_create_branch: Create a new branch with 'agent/' prefix (e.g., agent/calculator)
            - git_checkout_branch: Switch to an existing branch
            - git_list_branches: List all local branches
            - git_diff: Show changes in working directory
            - git_stage_files: Stage files for commit (or stage all with no args)
            - git_commit: Commit staged changes with a message
            - git_push: Push branch to remote (REQUIRES USER CONFIRMATION - show changes first!)
            - git_pull: Pull latest changes from remote
            - git_log: Show recent commit history
            - git_show_commit: Show details of a specific commit
            - git_branch_summary: Get current branch status and remote tracking info
            
            GIT WORKFLOW:
            When making code changes that should be committed:
            1. Check status: git_status()
            2. Create feature branch: git_create_branch("descriptive-name")
            3. Make your file changes (write_file, edit_file, etc.)
            4. Stage changes: git_stage_files() or git_stage_files(["specific/file.py"])
            5. Show diff: git_diff() - review what will be committed
            6. Commit: git_commit("Clear description of changes")
            7. Show what will be pushed: git_log(limit=5)
            8. Ask user for permission to push
            9. If approved: git_push()
            
            IMPORTANT GIT RULES:
            - NEVER commit directly to main/master/develop branches
            - ALWAYS create a feature branch first (agent/feature-name)
            - ALWAYS show git_diff() before committing
            - ALWAYS show git_log() before pushing
            - NEVER auto-push without user confirmation
            - Branch names should be descriptive: agent/calculator, agent/data-pipeline, etc.
            
            CONVERSATION CONTEXT:
            - When users reference files from previous messages (like "that file" or "operations.py"), 
              look at the conversation history to find the exact file path you used before
            - Remember what files you've created and where they are
            
            Always provide clear feedback about what you're doing."""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create the agent
        agent = create_tool_calling_agent(self.model, TOOLS, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)
        
        self.current_session_id = None
        self.current_state = None
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new conversation session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.current_session_id = session_id
        
        # Try to load existing state, or create new one
        self.current_state = memory_manager.load_state(session_id)
        if self.current_state is None:
            self.current_state = create_initial_state(session_id)
        
        return session_id
    
    def _add_trace_tags_and_metadata(self, user_input: str, response: str, latency: float, success: bool, error_type: str = None, tool_call_count: int = 0):
        """Add intelligent tags and metadata to LangSmith trace for filtering and analysis."""
        try:
            from langsmith import get_current_run_tree
            
            run = get_current_run_tree()
            if not run:
                return
            
            tags = []
            user_lower = user_input.lower()
            response_lower = response.lower()
            
            # Task type tags
            if any(word in user_lower for word in ["git", "commit", "push", "branch", "pull"]):
                tags.append("git-operation")
            
            if any(word in user_lower for word in ["create", "write", "make", "generate"]):
                tags.append("file-creation")
            
            if any(word in user_lower for word in ["read", "show", "display", "view", "check"]):
                tags.append("file-reading")
            
            if any(word in user_lower for word in ["edit", "modify", "update", "change", "fix"]):
                tags.append("file-editing")
            
            if any(word in user_lower for word in ["run", "execute", "test", "pytest"]):
                tags.append("command-execution")
            
            if any(word in user_lower for word in ["install", "pip", "package", "dependency"]):
                tags.append("package-management")
            
            # Complexity tags
            if len(user_input.split()) > 30 or "multi" in user_lower:
                tags.append("complex-query")
            else:
                tags.append("simple-query")
            
            # Success/Error tags
            if success:
                tags.append("success")
            else:
                tags.append("error")
                if error_type:
                    tags.append(f"error-{error_type}")
            
            # Performance tags
            if latency > 10:
                tags.append("slow")
            elif latency < 3:
                tags.append("fast")
            
            # Multi-turn conversation tag
            if self.current_state and len(self.current_state["messages"]) > 2:
                tags.append("multi-turn")
            else:
                tags.append("single-turn")
            
            # Tool usage tags
            if tool_call_count == 0:
                tags.append("no-tools")
            elif tool_call_count == 1:
                tags.append("single-tool")
            else:
                tags.append("multi-tool")
            
            # Add all tags
            for tag in tags:
                run.add_tags([tag])
            
            # Add custom metadata
            message_count = len(self.current_state["messages"]) if self.current_state else 0
            files_in_context = len(self.current_state.get("current_files", {})) if self.current_state else 0
            
            metadata = {
                "session_id": self.current_session_id,
                "turn_number": message_count // 2,
                "message_count": message_count,
                "has_conversation_history": message_count > 2,  # More than just current exchange
                "files_in_context": files_in_context,
                "has_file_context": files_in_context > 0,
                "tool_call_count": tool_call_count,
                "latency_seconds": latency,
                "success": success,
                "model": self.model.model_name,
                "temperature": self.model.temperature,
                "input_length": len(user_input),
                "response_length": len(response)
            }
            
            if error_type:
                metadata["error_type"] = error_type
            
            run.add_metadata(metadata)
            
        except Exception as e:
            # Silently fail if tagging doesn't work - don't break the main flow
            pass
    
    @traceable(run_type="chain", name="process_message")
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process a user message and return agent response."""
        if not self.current_session_id:
            self.start_session()
        
        # Track start time for latency metrics
        start_time = datetime.now()
        
        try:
            # Add user message to state
            self.current_state["messages"].append(HumanMessage(content=user_input))
            
            # Get chat history with sliding window to prevent token overflow
            # Exclude the current message we just added
            max_history = config.get_max_history_messages()
            all_messages = self.current_state["messages"][:-1]
            
            # Apply sliding window - take only recent messages
            if len(all_messages) > max_history:
                chat_history = all_messages[-max_history:]
            else:
                chat_history = all_messages
            
            # Process with the agent executor, passing chat history
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            # Extract the response
            response_text = response.get("output", "No response generated")
            
            # Count tool calls from intermediate steps
            tool_call_count = 0
            if "intermediate_steps" in response:
                tool_call_count = len(response["intermediate_steps"])
            
            # Calculate latency
            end_time = datetime.now()
            latency_seconds = (end_time - start_time).total_seconds()
            
            # Add tags and metadata for LangSmith filtering
            self._add_trace_tags_and_metadata(user_input, response_text, latency_seconds, success=True, tool_call_count=tool_call_count)
            
            # Add AI message to state
            self.current_state["messages"].append(AIMessage(content=response_text))
            
            # Update state timestamp
            self.current_state = update_state_timestamp(self.current_state)
            
            # Save state
            memory_manager.save_state(self.current_session_id, self.current_state)
            
            return {
                "success": True,
                "response": response_text,
                "session_id": self.current_session_id,
                "metadata": {
                    "model": self.model.model_name,
                    "temperature": self.model.temperature,
                    "latency_seconds": latency_seconds,
                    "tool_call_count": tool_call_count,
                    "turn_number": len(self.current_state["messages"]) // 2,
                    "session_message_count": len(self.current_state["messages"]),
                    "timestamp": self.current_state["last_updated"].isoformat() if hasattr(self.current_state["last_updated"], 'isoformat') else str(self.current_state["last_updated"])
                }
            }
            
        except Exception as e:
            # Calculate latency even for errors
            end_time = datetime.now()
            latency_seconds = (end_time - start_time).total_seconds()
            
            # Add tags for error tracking (no tool count available on error)
            self._add_trace_tags_and_metadata(user_input, str(e), latency_seconds, success=False, error_type=type(e).__name__, tool_call_count=0)
            
            # Handle errors gracefully
            error_response = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "session_id": self.current_session_id,
                "metadata": {
                    "latency_seconds": latency_seconds,
                    "tool_call_count": 0
                }
            }
            
            # Update state with error
            if self.current_state:
                self.current_state["last_error"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            
            return error_response
    
    async def astream_response(self, user_input: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream agent response with events for real-time feedback.
        
        Yields events including:
        - on_chat_model_stream: Token-by-token LLM output
        - on_tool_start: Tool invocation begins
        - on_tool_end: Tool execution completes
        - on_chain_start/end: Agent reasoning steps
        
        Note: LangSmith tracing happens automatically via astream_events.
        The @traceable decorator doesn't work with async generators.
        """
        if not self.current_session_id:
            self.start_session()
        
        # Track start time for latency metrics
        start_time = datetime.now()
        
        try:
            # Add user message to state
            self.current_state["messages"].append(HumanMessage(content=user_input))
            
            # Get chat history with sliding window
            max_history = config.get_max_history_messages()
            all_messages = self.current_state["messages"][:-1]
            
            if len(all_messages) > max_history:
                chat_history = all_messages[-max_history:]
            else:
                chat_history = all_messages
            
            # Track response content and tool calls
            response_content = ""
            tool_call_count = 0
            
            # Stream events from agent executor
            async for event in self.agent_executor.astream_events(
                {
                    "input": user_input,
                    "chat_history": chat_history
                },
                version="v1"
            ):
                # Yield the event to the caller
                yield event
                
                # Collect response content from chat model streams
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        response_content += content
                
                # Count tool calls
                elif event["event"] == "on_tool_start":
                    tool_call_count += 1
            
            # After streaming completes, update state
            if response_content:
                self.current_state["messages"].append(AIMessage(content=response_content))
            
            # Calculate latency
            end_time = datetime.now()
            latency_seconds = (end_time - start_time).total_seconds()
            
            # Add tags and metadata for LangSmith filtering
            self._add_trace_tags_and_metadata(user_input, response_content, latency_seconds, success=True, tool_call_count=tool_call_count)
            
            # Update state timestamp
            self.current_state = update_state_timestamp(self.current_state)
            
            # Save state
            memory_manager.save_state(self.current_session_id, self.current_state)
            
            # Yield completion event with metadata
            yield {
                "event": "on_complete",
                "data": {
                    "success": True,
                    "session_id": self.current_session_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "latency_seconds": latency_seconds,
                        "turn_number": len(self.current_state["messages"]) // 2,
                        "session_message_count": len(self.current_state["messages"]),
                        "tool_call_count": tool_call_count
                    }
                }
            }
            
        except Exception as e:
            # Calculate latency even for errors
            end_time = datetime.now()
            latency_seconds = (end_time - start_time).total_seconds()
            
            # Add tags for error tracking (tool_call_count not available on error)
            self._add_trace_tags_and_metadata(user_input, str(e), latency_seconds, success=False, error_type=type(e).__name__, tool_call_count=0)
            
            # Yield error event
            yield {
                "event": "on_error",
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "session_id": self.current_session_id,
                    "metadata": {
                        "latency_seconds": latency_seconds,
                        "tool_call_count": 0
                    }
                }
            }
            
            # Update state with error
            if self.current_state:
                self.current_state["last_error"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        if not self.current_state:
            return {"error": "No active session"}
        
        # Handle datetime objects that might be strings after JSON serialization
        created_at = self.current_state["created_at"]
        last_updated = self.current_state["last_updated"]
        
        # Convert to string if it's a datetime object, otherwise use as-is
        created_at_str = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
        last_updated_str = last_updated.isoformat() if hasattr(last_updated, 'isoformat') else str(last_updated)
        
        return {
            "session_id": self.current_session_id,
            "message_count": len(self.current_state["messages"]),
            "files_in_context": len(self.current_state["current_files"]),
            "created_at": created_at_str,
            "last_updated": last_updated_str,
            "last_error": self.current_state["last_error"]
        }
    
    def list_available_sessions(self) -> List[str]:
        """List all available session IDs."""
        return memory_manager.list_sessions()


# Global agent instance - will be initialized when needed
agent = None

def get_agent(model_name: str = None, temperature: float = None) -> CodingAgent:
    """Get or create the global agent instance."""
    global agent
    if agent is None:
        agent = CodingAgent(model_name, temperature)
    return agent
