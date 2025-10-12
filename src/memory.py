"""
Simple memory management for conversation persistence.
Using InMemorySaver initially, can be upgraded to Redis later.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .config import config


class SimpleMemoryManager:
    """Simple memory manager for agent state persistence."""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or config.get_memory_storage_dir()
        self.memory_saver = MemorySaver()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_state(self, session_id: str, state: AgentState) -> bool:
        """Save agent state to memory."""
        try:
            # Save to LangGraph's memory saver
            # Note: This is a simplified implementation
            # In practice, you'd use the proper LangGraph checkpointing
            
            # Also save to local file for backup
            file_path = os.path.join(self.storage_dir, f"{session_id}.json")
            with open(file_path, 'w') as f:
                json.dump(state, f, default=str, indent=2)
            
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
                    return json.load(f)
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
