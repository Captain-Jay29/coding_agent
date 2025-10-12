"""
Main agent logic using LangChain's basic tools.
Simplified version without LangGraph for MVP testing.
"""

import os
import uuid
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

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
            - write_file: Create or overwrite files (paths are relative to workspace)
            - read_file: Read file contents (paths are relative to workspace)
            - edit_file: Modify existing files (paths are relative to workspace)
            - run_command: Execute shell commands (runs IN the workspace directory)
            - list_files: List files matching a pattern
            - file_exists: Check if a file exists
            - get_file_info: Get file metadata
            
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
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process a user message and return agent response."""
        if not self.current_session_id:
            self.start_session()
        
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
                    "timestamp": self.current_state["last_updated"].isoformat() if hasattr(self.current_state["last_updated"], 'isoformat') else str(self.current_state["last_updated"])
                }
            }
            
        except Exception as e:
            # Handle errors gracefully
            error_response = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "session_id": self.current_session_id
            }
            
            # Update state with error
            if self.current_state:
                self.current_state["last_error"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            
            return error_response
    
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
