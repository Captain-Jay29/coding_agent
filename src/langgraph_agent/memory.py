"""
Memory management for LangGraph agent.
Uses LangGraph's built-in checkpointing - simple and efficient.
"""

import sys
from pathlib import Path
from typing import Optional
from langgraph.checkpoint.memory import MemorySaver

# Import config
sys.path.append(str(Path(__file__).parent.parent))
from src.config import config as app_config


class LangGraphMemory:
    """Simple wrapper for LangGraph's built-in checkpointing."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize memory with in-memory checkpointing.
        
        Args:
            storage_dir: Directory for storage (uses config default if not provided)
        """
        # Use config default if not provided
        if storage_dir is None:
            storage_dir = app_config.get_memory_storage_dir()
        
        # Ensure storage directory exists (for future use)
        Path(storage_dir).mkdir(parents=True, exist_ok=True)
        
        # Use MemorySaver (in-memory checkpointing)
        # This maintains state across the session
        self.checkpointer = MemorySaver()
    
    def get_config(self, session_id: str) -> dict:
        """
        Get configuration for a session.
        
        Args:
            session_id: Session identifier (used as thread_id)
            
        Returns:
            Config dict for LangGraph invocation
        """
        return {
            "configurable": {
                "thread_id": session_id
            }
        }
    
    def list_sessions(self) -> list:
        """
        List all available sessions.
        
        Note: LangGraph stores thread_ids in its internal storage.
        This is a simplified implementation.
        """
        # For now, return empty list
        # Can be enhanced by querying the checkpointer's storage
        return []


# Global instance
_memory_instance: Optional[LangGraphMemory] = None


def get_memory(storage_dir: str = None) -> LangGraphMemory:
    """Get or create the global memory instance (uses config default)."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LangGraphMemory(storage_dir)
    return _memory_instance

