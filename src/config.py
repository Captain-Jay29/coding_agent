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
        
        # Tool settings
        self.command_timeout = int(os.getenv("COMMAND_TIMEOUT", "30"))
        self.memory_storage_dir = os.getenv("MEMORY_STORAGE_DIR", ".agent_memory")
        
        # Agent settings
        self.max_history_messages = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
        
        # Retry settings
        self.max_retry = int(os.getenv("MAX_RETRY", "3"))
        self.auto_retry = os.getenv("AUTO_RETRY", "true").lower() == "true"
        
        # Git settings
        self.git_enabled = os.getenv("GIT_ENABLED", "true").lower() == "true"
        self.git_auto_push = os.getenv("GIT_AUTO_PUSH", "false").lower() == "true"
        self.git_main_branch = os.getenv("GIT_MAIN_BRANCH", "main")
        
        # LangSmith settings for tracing and evaluation
        # Note: Use LANGCHAIN_* prefix (official LangSmith env vars)
        self.langsmith_tracing = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.langsmith_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGCHAIN_PROJECT", "coding-agent")
        self.langsmith_endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        
        # Set LangSmith environment variables if not already set
        # This ensures LangChain automatically traces all operations
        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project
            os.environ["LANGCHAIN_ENDPOINT"] = self.langsmith_endpoint
        
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
    
    def get_command_timeout(self) -> int:
        """Get command timeout in seconds."""
        return self.command_timeout
    
    def get_memory_storage_dir(self) -> str:
        """Get memory storage directory path."""
        return self.memory_storage_dir
    
    def get_max_history_messages(self) -> int:
        """Get maximum number of history messages to pass to agent."""
        return self.max_history_messages
    
    def get_max_retry(self) -> int:
        """Get maximum number of retry attempts for failed operations."""
        return self.max_retry
    
    def get_auto_retry_enabled(self) -> bool:
        """Check if automatic retry is enabled."""
        return self.auto_retry
    
    def get_git_enabled(self) -> bool:
        """Check if Git operations are enabled."""
        return self.git_enabled
    
    def get_git_auto_push(self) -> bool:
        """Check if automatic push is enabled (not recommended)."""
        return self.git_auto_push
    
    def get_git_main_branch(self) -> str:
        """Get the main branch name (protected from direct pushes)."""
        return self.git_main_branch
    
    def get_langsmith_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return self.langsmith_tracing
    
    def get_langsmith_api_key(self) -> Optional[str]:
        """Get LangSmith API key."""
        return self.langsmith_api_key
    
    def get_langsmith_project(self) -> str:
        """Get LangSmith project name."""
        return self.langsmith_project
    
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
        print(f"  Command Timeout: {self.command_timeout}s")
        print(f"  Memory Storage: {self.memory_storage_dir}")
        print(f"  Max History Messages: {self.max_history_messages}")
        print(f"  Max Retry Attempts: {self.max_retry}")
        print(f"  Auto Retry Enabled: {self.auto_retry}")
        print(f"  Git Enabled: {self.git_enabled}")
        print(f"  Git Auto-Push: {self.git_auto_push}")
        print(f"  Git Main Branch: {self.git_main_branch}")
        print(f"  LangSmith Tracing: {self.langsmith_tracing}")
        print(f"  LangSmith Project: {self.langsmith_project}")
        print(f"  LangSmith API Key: {'Set' if self.langsmith_api_key else 'Not set'}")
        print(f"  OpenAI API Key: {'Set' if self.get_openai_api_key() else 'Not set'}")


# Global configuration instance
config = Config()
