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
from .state import AgentState, create_initial_state, update_state_timestamp, reset_retry_state, increment_retry_count
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
              * By default, captures output for return value and error handling
              * Use show_output=True for interactive/monitoring tools (dashboards, monitors, live displays)
                to stream output directly to terminal in real-time
              * Examples: run_command("python monitor.py", show_output=True) for dashboards
                         run_command("pytest tests.py") for normal commands (captures output)
              WARNING: Scripts with input() will hang! Modify them to accept arguments instead.
              Example: Instead of input("Enter n:"), use sys.argv or provide test values.
            - list_files: List files matching a pattern
            - file_exists: Check if a file exists
            - get_file_info: Get file metadata
            
            Directory Navigation:
            - get_current_directory: Show current workspace path (like pwd)
            - list_directory: List contents of a directory with details (like ls)
            - change_workspace_context: Explore a different directory and see its contents
            
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
    
    def _format_retry_feedback(self, error_info: Dict[str, str], user_input: str) -> str:
        """Format error information as feedback for the agent to retry.
        
        This creates a clear, structured message that helps the agent understand:
        - What went wrong
        - What has been tried before
        - How to approach the fix
        """
        retry_count = self.current_state.get("retry_count", 0)
        max_retries = config.get_max_retry()
        retry_history = self.current_state.get("retry_history", [])
        
        feedback = f"""🔄 RETRY ATTEMPT {retry_count} of {max_retries}

Your previous action encountered an error. Please analyze the error carefully and try a different approach.

ORIGINAL USER REQUEST:
{user_input}

ERROR DETAILS:
- Error Type: {error_info.get('error_type', 'Unknown')}
- Error Message: {error_info.get('error', 'Unknown error')}
"""
        
        # Add previous retry attempts to avoid repeating mistakes
        if len(retry_history) > 1:
            feedback += "\nPREVIOUS ATTEMPTS THAT FAILED:\n"
            for attempt in retry_history[:-1]:  # Exclude current attempt
                feedback += f"  Attempt {attempt['attempt']}: {attempt['error_type']} - {attempt['error'][:100]}\n"
            feedback += "\n⚠️  Do NOT repeat the same approach. Try something different.\n"
        
        feedback += """
INSTRUCTIONS:
1. Carefully read the error message above
2. Identify the root cause of the failure
3. Consider what might need to be fixed or done differently
4. Try a different approach or fix the underlying issue
5. Then retry the operation

Examples of what to check:
- Missing dependencies (install them first)
- File paths (check if files exist, use correct paths)
- Syntax errors (fix the code)
- Missing permissions (check file/directory permissions)
- Wrong tool usage (use the correct tool or parameters)

Please proceed with your fix and retry.
"""
        
        return feedback
    
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
            
            # Retry tags
            retry_count = self.current_state.get("retry_count", 0) if self.current_state else 0
            if retry_count > 0:
                tags.append("auto-retry")
                tags.append(f"retry-count-{retry_count}")
                if success:
                    tags.append("retry-recovered")
                else:
                    tags.append("retry-exhausted")
            
            # Add all tags
            for tag in tags:
                run.add_tags([tag])
            
            # Add custom metadata
            message_count = len(self.current_state["messages"]) if self.current_state else 0
            files_in_context = len(self.current_state.get("current_files", {})) if self.current_state else 0
            
            retry_count = self.current_state.get("retry_count", 0) if self.current_state else 0
            
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
                "response_length": len(response),
                "retry_count": retry_count,
                "had_retries": retry_count > 0,
                "auto_retry_enabled": config.get_auto_retry_enabled()
            }
            
            if error_type:
                metadata["error_type"] = error_type
            
            run.add_metadata(metadata)
            
        except Exception as e:
            # Silently fail if tagging doesn't work - don't break the main flow
            pass
    
    @traceable(run_type="chain", name="process_message")
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process a user message and return agent response with automatic retry on errors."""
        if not self.current_session_id:
            self.start_session()
        
        # Track start time for latency metrics
        start_time = datetime.now()
        
        # Reset retry state for new user message
        self.current_state = reset_retry_state(self.current_state)
        
        # Store original user input for retry context
        original_user_input = user_input
        
        # Add user message to state (only once, before any retries)
        self.current_state["messages"].append(HumanMessage(content=user_input))
        
        # Get max retry settings
        max_retries = config.get_max_retry()
        auto_retry_enabled = config.get_auto_retry_enabled()
        
        # Retry loop
        last_error = None
        while True:
            try:
                # Get chat history with sliding window to prevent token overflow
                # Exclude the current message we just added (and any retry messages)
                max_history = config.get_max_history_messages()
                all_messages = self.current_state["messages"][:-1]
                
                # Apply sliding window - take only recent messages
                if len(all_messages) > max_history:
                    chat_history = all_messages[-max_history:]
                else:
                    chat_history = all_messages
                
                # Process with the agent executor, passing chat history
                response = self.agent_executor.invoke({
                    "input": user_input,  # Use current input (original or retry feedback)
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
                retry_count = self.current_state.get("retry_count", 0)
                self._add_trace_tags_and_metadata(original_user_input, response_text, latency_seconds, success=True, tool_call_count=tool_call_count)
                
                # Add AI message to state
                self.current_state["messages"].append(AIMessage(content=response_text))
                
                # Update state timestamp
                self.current_state = update_state_timestamp(self.current_state)
                
                # Save state
                memory_manager.save_state(self.current_session_id, self.current_state)
                
                # Success response with retry info if retries occurred
                result = {
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
                        "retry_count": retry_count,
                        "timestamp": self.current_state["last_updated"].isoformat() if hasattr(self.current_state["last_updated"], 'isoformat') else str(self.current_state["last_updated"])
                    }
                }
                
                # Add retry history to metadata if retries occurred
                if retry_count > 0:
                    result["metadata"]["retry_history"] = self.current_state.get("retry_history", [])
                    result["metadata"]["recovered_from_error"] = True
                
                return result
                
            except Exception as e:
                # Store error info
                error_info = {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                last_error = error_info
                
                # Increment retry count and add to history
                self.current_state = increment_retry_count(self.current_state, error_info)
                current_retry = self.current_state.get("retry_count", 0)
                
                # Check if we should retry
                should_retry = (
                    auto_retry_enabled and 
                    current_retry <= max_retries
                )
                
                if should_retry:
                    print(f"\n⚠️  Error encountered on attempt {current_retry}/{max_retries + 1}")
                    print(f"   Error: {error_info['error_type']}: {error_info['error'][:200]}")
                    print(f"   🔄 Retrying automatically...\n")
                    
                    # Format retry feedback for the agent
                    retry_feedback = self._format_retry_feedback(error_info, original_user_input)
                    
                    # Update user_input to include error context for retry
                    user_input = retry_feedback
                    
                    # Add retry feedback as a new message for context
                    self.current_state["messages"].append(HumanMessage(content=retry_feedback))
                    
                    # Continue to next iteration of retry loop
                    continue
                else:
                    # No more retries - return error
                    end_time = datetime.now()
                    latency_seconds = (end_time - start_time).total_seconds()
                    
                    # Add tags for error tracking
                    self._add_trace_tags_and_metadata(original_user_input, str(e), latency_seconds, success=False, error_type=type(e).__name__, tool_call_count=0)
                    
                    # Prepare error response
                    error_response = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "session_id": self.current_session_id,
                        "metadata": {
                            "latency_seconds": latency_seconds,
                            "tool_call_count": 0,
                            "retry_count": current_retry - 1 if current_retry > 0 else 0,
                            "max_retries_exceeded": current_retry > max_retries,
                            "retry_history": self.current_state.get("retry_history", [])
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
