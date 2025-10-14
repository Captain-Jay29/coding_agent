"""
Git operations tools for version control.
Enables the agent to create branches, commit changes, and push to remote.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError
from langchain_core.tools import tool
from .config import config


def _get_repo() -> Repo:
    """Get the Git repository object for the main project."""
    try:
        # Get the project root (parent of workspace)
        repo_path = config.get_workspace_path().parent
        repo = Repo(repo_path)
        return repo
    except InvalidGitRepositoryError:
        raise RuntimeError(
            f"Not a git repository: {repo_path}. "
            "Please ensure you're working in a git repository."
        )


def _format_commit(commit) -> str:
    """Format a commit object for display."""
    return f"{commit.hexsha[:7]} - {commit.author.name}: {commit.message.strip()}"


def _is_protected_branch(branch_name: str) -> bool:
    """Check if a branch is protected (main, master, develop)."""
    protected = ["main", "master", "develop"]
    return branch_name in protected


@tool
def git_status() -> str:
    """Check the current git status of the workspace.
    
    Shows:
    - Current branch
    - Modified files
    - Untracked files
    - Staged files
    
    Returns:
        Status summary as a string
    """
    repo = _get_repo()
    
    status_lines = [f"📍 Current branch: {repo.active_branch.name}"]
    
    # Check for uncommitted changes
    if repo.is_dirty(untracked_files=True):
        # Modified files
        modified = [item.a_path for item in repo.index.diff(None)]
        if modified:
            status_lines.append(f"\n📝 Modified files ({len(modified)}):")
            status_lines.extend([f"  - {f}" for f in modified[:10]])
            if len(modified) > 10:
                status_lines.append(f"  ... and {len(modified) - 10} more")
        
        # Staged files
        staged = [item.a_path for item in repo.index.diff("HEAD")]
        if staged:
            status_lines.append(f"\n✅ Staged files ({len(staged)}):")
            status_lines.extend([f"  - {f}" for f in staged[:10]])
            if len(staged) > 10:
                status_lines.append(f"  ... and {len(staged) - 10} more")
        
        # Untracked files
        untracked = repo.untracked_files
        if untracked:
            status_lines.append(f"\n❓ Untracked files ({len(untracked)}):")
            status_lines.extend([f"  - {f}" for f in untracked[:10]])
            if len(untracked) > 10:
                status_lines.append(f"  ... and {len(untracked) - 10} more")
    else:
        status_lines.append("\n✨ Working tree clean - no changes to commit")
    
    return "\n".join(status_lines)


@tool
def git_create_branch(feature_name: str) -> str:
    """Create a new branch following the agent/feature naming convention.
    
    The branch name will be prefixed with 'agent/' automatically.
    This creates a new branch from the current HEAD and switches to it.
    
    Args:
        feature_name: Descriptive name for the feature (e.g., 'calculator', 'data-pipeline')
    
    Returns:
        Success message with branch name
    """
    repo = _get_repo()
    
    # Format branch name
    branch_name = f"agent/{feature_name}"
    
    # Check if branch already exists
    if branch_name in [b.name for b in repo.branches]:
        return f"⚠️  Branch '{branch_name}' already exists. Use git_checkout_branch to switch to it."
    
    try:
        # Create and checkout new branch
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        
        return f"✅ Created and switched to branch: {branch_name}"
    except GitCommandError as e:
        raise RuntimeError(f"Failed to create branch: {e}")


@tool
def git_checkout_branch(branch_name: str) -> str:
    """Switch to an existing branch.
    
    Args:
        branch_name: Name of the branch to checkout
    
    Returns:
        Success message
    """
    repo = _get_repo()
    
    try:
        # Check if branch exists
        if branch_name not in [b.name for b in repo.branches]:
            available = [b.name for b in repo.branches]
            return f"❌ Branch '{branch_name}' not found. Available branches: {', '.join(available)}"
        
        # Checkout the branch
        repo.git.checkout(branch_name)
        
        return f"✅ Switched to branch: {branch_name}"
    except GitCommandError as e:
        raise RuntimeError(f"Failed to checkout branch: {e}")


@tool
def git_list_branches() -> str:
    """List all local branches.
    
    Shows current branch with an asterisk (*).
    
    Returns:
        List of branches
    """
    repo = _get_repo()
    
    current = repo.active_branch.name
    branches = []
    
    for branch in repo.branches:
        prefix = "* " if branch.name == current else "  "
        branches.append(f"{prefix}{branch.name}")
    
    return "📋 Local branches:\n" + "\n".join(branches)


@tool
def git_diff(file_path: Optional[str] = None) -> str:
    """Show changes in the working directory.
    
    Args:
        file_path: Optional path to show diff for specific file only
    
    Returns:
        Diff output showing changes
    """
    repo = _get_repo()
    
    try:
        if file_path:
            # Show diff for specific file
            diff = repo.git.diff(file_path)
            if not diff:
                return f"No changes in {file_path}"
        else:
            # Show all changes
            diff = repo.git.diff()
            if not diff:
                return "No changes in working directory"
        
        return f"📊 Changes:\n\n{diff}"
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get diff: {e}")


@tool
def git_stage_files(file_patterns: List[str] = None) -> str:
    """Stage files for commit.
    
    Args:
        file_patterns: List of file patterns to stage (e.g., ['agent_runs/*', 'README.md']).
                      If None or empty, stages all changes.
    
    Returns:
        Success message with staged files
    """
    repo = _get_repo()
    
    try:
        if not file_patterns:
            # Stage all changes
            repo.git.add(A=True)
            staged_count = len([item.a_path for item in repo.index.diff("HEAD")])
            return f"✅ Staged all changes ({staged_count} files)"
        else:
            # Stage specific patterns
            for pattern in file_patterns:
                repo.git.add(pattern)
            
            staged = [item.a_path for item in repo.index.diff("HEAD")]
            return f"✅ Staged {len(staged)} files:\n" + "\n".join([f"  - {f}" for f in staged[:10]])
    except GitCommandError as e:
        raise RuntimeError(f"Failed to stage files: {e}")


@tool
def git_commit(message: str) -> str:
    """Commit staged changes with a message.
    
    IMPORTANT: This commits changes locally. Use git_push to push to remote.
    
    Args:
        message: Commit message describing the changes
    
    Returns:
        Success message with commit hash
    """
    repo = _get_repo()
    
    # Check if there are staged changes
    if not repo.index.diff("HEAD"):
        return "⚠️  No staged changes to commit. Use git_stage_files first."
    
    try:
        # Create commit
        commit = repo.index.commit(message)
        
        return f"✅ Committed changes: {commit.hexsha[:7]} - {message}"
    except GitCommandError as e:
        raise RuntimeError(f"Failed to commit: {e}")


@tool
def git_push(branch_name: Optional[str] = None, force: bool = False) -> str:
    """Push commits to remote repository.
    
    IMPORTANT: This requires user confirmation. The agent should:
    1. Show what will be pushed (use git_log)
    2. Ask user for permission
    3. Only then call this function
    
    Args:
        branch_name: Branch to push (defaults to current branch)
        force: Whether to force push (NOT RECOMMENDED for agent use)
    
    Returns:
        Success message
    """
    repo = _get_repo()
    
    if branch_name is None:
        branch_name = repo.active_branch.name
    
    # Safety check: prevent force push to protected branches
    if force and _is_protected_branch(branch_name):
        raise RuntimeError(
            f"❌ Force push to protected branch '{branch_name}' is not allowed. "
            "This is a safety feature to prevent data loss."
        )
    
    # Check if branch is protected
    if _is_protected_branch(branch_name):
        return (
            f"⚠️  WARNING: You're about to push to protected branch '{branch_name}'. "
            "Consider creating a feature branch instead using git_create_branch."
        )
    
    try:
        # Get remote
        origin = repo.remote(name='origin')
        
        # Push
        if force:
            origin.push(branch_name, force=True)
            return f"✅ Force pushed to origin/{branch_name}"
        else:
            # Set upstream and push
            origin.push(branch_name, set_upstream=True)
            return f"✅ Pushed branch '{branch_name}' to remote (origin/{branch_name})"
    
    except GitCommandError as e:
        raise RuntimeError(f"Failed to push: {e}")


@tool
def git_pull(branch_name: Optional[str] = None) -> str:
    """Pull latest changes from remote repository.
    
    Args:
        branch_name: Branch to pull (defaults to current branch)
    
    Returns:
        Success message with update info
    """
    repo = _get_repo()
    
    if branch_name is None:
        branch_name = repo.active_branch.name
    
    try:
        # Get remote
        origin = repo.remote(name='origin')
        
        # Fetch first
        origin.fetch()
        
        # Pull
        pull_info = origin.pull(branch_name)
        
        return f"✅ Pulled latest changes from origin/{branch_name}"
    
    except GitCommandError as e:
        raise RuntimeError(f"Failed to pull: {e}")


@tool
def git_log(limit: int = 10, branch_name: Optional[str] = None) -> str:
    """Show recent commit history.
    
    Args:
        limit: Number of commits to show (default: 10)
        branch_name: Branch to show log for (defaults to current branch)
    
    Returns:
        Formatted commit history
    """
    repo = _get_repo()
    
    try:
        if branch_name:
            commits = list(repo.iter_commits(branch_name, max_count=limit))
        else:
            commits = list(repo.iter_commits(max_count=limit))
        
        if not commits:
            return "No commits yet"
        
        log_lines = [f"📜 Recent commits ({len(commits)}):"]
        for commit in commits:
            log_lines.append(f"  {_format_commit(commit)}")
        
        return "\n".join(log_lines)
    
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get log: {e}")


@tool
def git_show_commit(commit_hash: str) -> str:
    """Show details of a specific commit.
    
    Args:
        commit_hash: Full or short commit hash
    
    Returns:
        Commit details including changes
    """
    repo = _get_repo()
    
    try:
        commit = repo.commit(commit_hash)
        
        details = [
            f"📝 Commit: {commit.hexsha}",
            f"👤 Author: {commit.author.name} <{commit.author.email}>",
            f"📅 Date: {commit.authored_datetime}",
            f"💬 Message: {commit.message.strip()}",
            f"\n📊 Changed files ({len(commit.stats.files)}):"
        ]
        
        for file, stats in commit.stats.files.items():
            details.append(f"  {file}: +{stats['insertions']} -{stats['deletions']}")
        
        return "\n".join(details)
    
    except GitCommandError as e:
        raise RuntimeError(f"Failed to show commit: {e}")


@tool
def git_branch_summary() -> str:
    """Get a summary of the current branch and its status relative to remote.
    
    Shows:
    - Current branch name
    - Commits ahead/behind remote
    - Last commit info
    
    Returns:
        Branch summary
    """
    repo = _get_repo()
    
    try:
        current_branch = repo.active_branch
        branch_name = current_branch.name
        
        summary = [f"🌿 Current branch: {branch_name}"]
        
        # Get last commit
        if current_branch.commit:
            summary.append(f"📍 Last commit: {_format_commit(current_branch.commit)}")
        
        # Check tracking branch
        try:
            tracking_branch = current_branch.tracking_branch()
            if tracking_branch:
                # Compare with remote
                ahead = repo.iter_commits(f'{tracking_branch.name}..{branch_name}')
                behind = repo.iter_commits(f'{branch_name}..{tracking_branch.name}')
                
                ahead_count = sum(1 for _ in ahead)
                behind_count = sum(1 for _ in behind)
                
                if ahead_count > 0:
                    summary.append(f"⬆️  Ahead of {tracking_branch.name} by {ahead_count} commit(s)")
                if behind_count > 0:
                    summary.append(f"⬇️  Behind {tracking_branch.name} by {behind_count} commit(s)")
                if ahead_count == 0 and behind_count == 0:
                    summary.append(f"✅ Up to date with {tracking_branch.name}")
            else:
                summary.append("📌 No remote tracking branch set")
        except Exception:
            summary.append("📌 No remote tracking branch")
        
        return "\n".join(summary)
    
    except Exception as e:
        raise RuntimeError(f"Failed to get branch summary: {e}")


# Export all git tools
GIT_TOOLS = [
    git_status,
    git_create_branch,
    git_checkout_branch,
    git_list_branches,
    git_diff,
    git_stage_files,
    git_commit,
    git_push,
    git_pull,
    git_log,
    git_show_commit,
    git_branch_summary,
]

