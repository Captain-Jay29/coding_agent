"""
Simple memory management for conversation persistence.
Using InMemorySaver initially, can be upgraded to Redis later.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from .state import AgentState
from .config import config


class SimpleMemoryManager:
    """Simple memory manager for agent state persistence."""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or config.get_memory_storage_dir()
        self.memory_saver = MemorySaver()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _serialize_message(self, msg: BaseMessage) -> Dict[str, Any]:
        """Serialize a message object to JSON-compatible dict."""
        return {
            "type": msg.__class__.__name__,
            "content": msg.content,
            "additional_kwargs": msg.additional_kwargs,
            "response_metadata": getattr(msg, 'response_metadata', {})
        }
    
    def _deserialize_message(self, msg_dict: Dict[str, Any]) -> BaseMessage:
        """Deserialize a message dict back to message object."""
        msg_type = msg_dict.get("type", "HumanMessage")
        content = msg_dict.get("content", "")
        
        if msg_type == "AIMessage":
            return AIMessage(content=content)
        else:
            return HumanMessage(content=content)
    
    def save_state(self, session_id: str, state: AgentState) -> bool:
        """Save agent state to memory."""
        try:
            # Serialize messages properly
            serialized_state = {
                "messages": [self._serialize_message(msg) for msg in state.get("messages", [])],
                "current_files": state.get("current_files", {}),
                "last_command_output": state.get("last_command_output"),
                "last_error": state.get("last_error"),
                "session_id": state.get("session_id"),
                "created_at": str(state.get("created_at")),
                "last_updated": str(state.get("last_updated"))
            }
            
            # Save to local file
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            with open(file_path, 'w') as f:
                json.dump(serialized_state, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, session_id: str) -> Optional[AgentState]:
        """Load agent state from memory."""
        try:
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Deserialize messages back to proper objects
                messages = []
                for msg_data in data.get("messages", []):
                    if isinstance(msg_data, dict):
                        messages.append(self._deserialize_message(msg_data))
                    # Skip old string-format messages
                
                # Reconstruct state with proper message objects
                return {
                    "messages": messages,
                    "current_files": data.get("current_files", {}),
                    "last_command_output": data.get("last_command_output"),
                    "last_error": data.get("last_error"),
                    "session_id": data.get("session_id"),
                    "created_at": data.get("created_at"),
                    "last_updated": data.get("last_updated")
                }
            return None
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        try:
            files = os.listdir(self.storage_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception:
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from memory."""
        try:
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


# Global memory manager instance
memory_manager = SimpleMemoryManager()
