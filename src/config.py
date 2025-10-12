"""
Configuration management for the coding agent.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuration manager for the coding agent."""
    
    def __init__(self):
        """Initialize configuration by loading .env file and environment variables."""
        # Load .env file if it exists
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
        
        # Core settings
        self.workspace_path = self._get_workspace_path()
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        self.model_temperature = float(os.getenv("MODEL_TEMPERATURE", "0.0"))
        
        # Ensure workspace directory exists
        self._ensure_workspace_exists()
    
    def _get_workspace_path(self) -> Path:
        """Get the workspace path from environment or use current directory."""
        workspace = os.getenv("WORKSPACE_PATH")
        if workspace:
            return Path(workspace)
        else:
            # Default to current directory if not specified
            return Path.cwd()
    
    def _ensure_workspace_exists(self):
        """Create workspace directory if it doesn't exist."""
        if not self.workspace_path.exists():
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            print(f"Created workspace directory: {self.workspace_path}")
    
    def get_workspace_path(self) -> Path:
        """Get the workspace path as a Path object."""
        return self.workspace_path
    
    def get_model_config(self) -> dict:
        """Get model configuration dictionary."""
        return {
            "model_name": self.default_model,
            "temperature": self.model_temperature
        }
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY")
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        errors = []
        
        # Check OpenAI API key
        if not self.get_openai_api_key():
            errors.append("OPENAI_API_KEY environment variable not set")
        
        # Check workspace permissions
        if not os.access(self.workspace_path, os.W_OK):
            errors.append(f"Workspace directory not writable: {self.workspace_path}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def print_config(self):
        """Print current configuration for debugging."""
        print("Current Configuration:")
        print(f"  Workspace Path: {self.workspace_path}")
        print(f"  Default Model: {self.default_model}")
        print(f"  Model Temperature: {self.model_temperature}")
        print(f"  OpenAI API Key: {'Set' if self.get_openai_api_key() else 'Not set'}")


# Global configuration instance
config = Config()
