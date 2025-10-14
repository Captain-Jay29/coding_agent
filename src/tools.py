"""
Core tools for file and shell operations.
Simple, safe operations with error handling.
"""

import os
import subprocess
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool
from .state import ToolResult
from .config import config
from .git_tools import GIT_TOOLS


def _resolve_path(file_path: str) -> str:
    """Resolve file path relative to workspace directory."""
    path = Path(file_path)
    if path.is_absolute():
        return str(path)
    else:
        # Make path relative to workspace
        workspace_path = config.get_workspace_path()
        return str(workspace_path / path)


def safe_execute(tool_func, *args, **kwargs) -> ToolResult:
    """Safely execute a tool function with error handling."""
    try:
        result = tool_func(*args, **kwargs)
        return ToolResult(
            success=True,
            data=result,
            error=None,
            error_type=None,
            suggestions=None,
            metadata={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        return ToolResult(
            success=False,
            data=None,
            error=str(e),
            error_type=type(e).__name__,
            suggestions=None,
            metadata={
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
        )


@tool
def read_file(file_path: str) -> str:
    """Read contents of a file.
    
    Args:
        file_path: Path to the file to read
    """
    resolved_path = _resolve_path(file_path)
    with open(resolved_path, 'r', encoding='utf-8') as f:
        return f.read()


@tool
def write_file(file_path: str, content: str) -> bool:
    """Write content to a file.
    
    Args:
        file_path: Path where to write the file
        content: Content to write to the file
    """
    resolved_path = _resolve_path(file_path)
    
    # Create directory if it doesn't exist (only if there's a directory part)
    dir_path = os.path.dirname(resolved_path)
    if dir_path:  # Only create directory if there's actually a directory part
        os.makedirs(dir_path, exist_ok=True)
    
    with open(resolved_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


@tool
def edit_file(file_path: str, old_content: str, new_content: str) -> bool:
    """Edit a file by replacing old_content with new_content.
    
    Args:
        file_path: Path to the file to edit
        old_content: The content to replace
        new_content: The new content to replace with
    """
    resolved_path = _resolve_path(file_path)
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"File not found: {resolved_path}")
    
    with open(resolved_path, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    if old_content not in current_content:
        raise ValueError(f"Old content not found in file: {resolved_path}")
    
    updated_content = current_content.replace(old_content, new_content)
    
    with open(resolved_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True


@tool
def run_command(command: str, timeout: int = None, working_dir: str = None) -> str:
    """Run a shell command and return the output.
    
    Commands execute in the workspace directory by default, making it easy to work with
    files you've created. You can optionally specify a different working directory.
    
    Args:
        command: The shell command to execute
        timeout: Timeout in seconds (uses config default if not provided)
        working_dir: Working directory for command execution (defaults to workspace path)
    """
    if timeout is None:
        timeout = config.get_command_timeout()
    
    # Default to workspace directory for command execution
    if working_dir is None:
        working_dir = str(config.get_workspace_path())
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=working_dir
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {result.stderr}")
    
    return result.stdout


@tool
def list_files(pattern: str = "*") -> List[str]:
    """List files matching a pattern.
    
    Args:
        pattern: Glob pattern to match files (default: "*")
    """
    import glob
    return glob.glob(pattern)


@tool
def file_exists(file_path: str) -> bool:
    """Check if a file exists.
    
    Args:
        file_path: Path to check
    """
    resolved_path = _resolve_path(file_path)
    return os.path.exists(resolved_path)


@tool
def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information (size, modified time, etc.).
    
    Args:
        file_path: Path to the file
    """
    resolved_path = _resolve_path(file_path)
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"File not found: {resolved_path}")
    
    stat = os.stat(resolved_path)
    return {
        "path": resolved_path,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": os.path.isfile(resolved_path),
        "is_dir": os.path.isdir(resolved_path)
    }


# Tool registry for the agent
TOOLS = [
    # File operations
    read_file,
    write_file,
    edit_file,
    run_command,
    list_files,
    file_exists,
    get_file_info,
    # Git operations
    *GIT_TOOLS,
]
