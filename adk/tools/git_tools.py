"""Local Git operations tools for ADK agent."""
import os
import shutil
import subprocess
from typing import Any


def clone_repo(repo_url: str, target_dir: str, token: str = None) -> dict[str, Any]:
    """
    Clone a Git repository to a local directory.
    
    Args:
        repo_url: Repository URL (e.g., "https://github.com/owner/repo")
        target_dir: Local directory to clone into
        token: Optional GitHub token for private repos
        
    Returns:
        Dictionary with clone status and directory path
    """
    # Clean up existing directory if present
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    # Construct authenticated URL if token provided
    if token and "github.com" in repo_url:
        if not repo_url.endswith(".git"):
            repo_url = f"{repo_url}.git"
        repo_url = repo_url.replace("https://", f"https://{token}@")
    
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "success": True,
            "directory": target_dir,
            "message": f"Cloned to {target_dir}",
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": e.stderr,
            "directory": target_dir,
        }


def checkout_branch(repo_dir: str, branch: str, create: bool = False) -> dict[str, Any]:
    """
    Checkout or create a Git branch.
    
    Args:
        repo_dir: Local repository directory
        branch: Branch name to checkout
        create: Whether to create a new branch
        
    Returns:
        Dictionary with checkout status
    """
    try:
        cmd = ["git", "checkout"]
        if create:
            cmd.append("-b")
        cmd.append(branch)
        
        result = subprocess.run(
            cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "success": True,
            "branch": branch,
            "created": create,
        }
    except subprocess.CalledProcessError as e:
        # Branch might already exist
        if create and "already exists" in e.stderr:
            return checkout_branch(repo_dir, branch, create=False)
        return {
            "success": False,
            "error": e.stderr,
            "branch": branch,
        }


def commit_and_push(
    repo_dir: str,
    message: str,
    files: list[str] = None,
    push: bool = True,
) -> dict[str, Any]:
    """
    Stage, commit, and optionally push changes.
    
    Args:
        repo_dir: Local repository directory
        message: Commit message
        files: Specific files to stage (None = all changes)
        push: Whether to push after committing
        
    Returns:
        Dictionary with commit status and SHA
    """
    try:
        # Stage files
        if files:
            for f in files:
                subprocess.run(
                    ["git", "add", f],
                    cwd=repo_dir,
                    capture_output=True,
                    check=True,
                )
        else:
            subprocess.run(
                ["git", "add", "-A"],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        
        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_sha = sha_result.stdout.strip()
        
        # Push if requested
        if push:
            subprocess.run(
                ["git", "push", "-u", "origin", "HEAD"],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )
        
        return {
            "success": True,
            "commit_sha": commit_sha,
            "pushed": push,
            "message": message,
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": e.stderr if e.stderr else str(e),
        }


def get_current_branch(repo_dir: str) -> str:
    """Get the current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_default_branch(repo_dir: str) -> str:
    """Get the default branch name from remote."""
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        # Output is like "refs/remotes/origin/main"
        return result.stdout.strip().split("/")[-1]
    except subprocess.CalledProcessError:
        # Fallback to common defaults
        return "main"


def pull_latest(repo_dir: str) -> dict[str, Any]:
    """Pull latest changes from remote."""
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}
