"""GitHub API tools for ADK agent."""
import os
from typing import Any, Optional
from github import Github, GithubException


def _get_github_client() -> Github:
    """Get authenticated GitHub client."""
    return Github(os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"])


def _parse_repo(repo: str) -> tuple[str, str]:
    """Parse repo string to owner/name tuple."""
    if "/" in repo:
        parts = repo.replace("https://github.com/", "").replace(".git", "").split("/")
        return parts[0], parts[1]
    raise ValueError(f"Invalid repo format: {repo}. Expected 'owner/repo'")


def get_file_contents(repo: str, path: str, ref: Optional[str] = None) -> dict[str, Any]:
    print(f"DEBUG: get_file_contents called with repo='{repo}', path='{path}', ref='{ref}'", flush=True)
    """
    Get contents of a file from a GitHub repository.
    
    Args:
        repo: Repository in "owner/repo" format
        path: Path to the file within the repository
        ref: Optional branch/tag/commit reference
        
    Returns:
        Dictionary with file content and metadata
    """
    gh = _get_github_client()
    owner, name = _parse_repo(repo)
    
    try:
        repository = gh.get_repo(f"{owner}/{name}")
        
        # Only pass ref if specified (None causes assertion error in PyGithub)
        if ref:
            content = repository.get_contents(path, ref=ref)
        else:
            content = repository.get_contents(path)
            
        # Handle directory listing
        if isinstance(content, list):
            files = []
            for file_content in content:
                files.append({
                    "name": file_content.name,
                    "path": file_content.path,
                    "type": file_content.type,
                    "size": file_content.size,
                    "sha": file_content.sha,
                })
            return {
                "type": "directory",
                "path": path,
                "files": files,
                "count": len(files)
            }
            
        # Handle single file
        return {
            "type": "file",
            "path": content.path,
            "content": content.decoded_content.decode("utf-8"),
            "sha": content.sha,
            "size": content.size,
        }
    except GithubException as e:
        error_msg = str(e)
        if e.status == 404:
            return {
                "error": "File or reference not found",
                "path": path,
                "ref": ref,
                "details": "The branch or file may not exist on the remote repository yet."
            }
        return {"error": error_msg, "path": path}


def create_branch(repo: str, branch_name: str, base_branch: Optional[str] = None) -> dict[str, Any]:
    print(f"DEBUG: create_branch called with repo='{repo}', branch_name='{branch_name}', base_branch='{base_branch}'")
    """
    Create a new branch in a GitHub repository.
    
    Args:
        repo: Repository in "owner/repo" format
        branch_name: Name for the new branch
        base_branch: Branch to create from (defaults to default branch)
        
    Returns:
        Dictionary with branch name and ref
    """
    gh = _get_github_client()
    owner, name = _parse_repo(repo)
    
    try:
        repository = gh.get_repo(f"{owner}/{name}")
        
        if base_branch is None:
            base_branch = repository.default_branch
        
        # Get the SHA of the base branch
        base_ref = repository.get_branch(base_branch)
        base_sha = base_ref.commit.sha
        
        # Create the new branch
        ref = repository.create_git_ref(f"refs/heads/{branch_name}", base_sha)
        return {
            "branch": branch_name,
            "ref": ref.ref,
            "sha": base_sha,
            "base_branch": base_branch,
        }
    except GithubException as e:
        if "Reference already exists" in str(e):
            return {"branch": branch_name, "already_exists": True}
        if e.status == 404:
            return {
                "error": "Base branch not found",
                "base_branch": base_branch,
                "details": "The base branch does not exist on the remote repository."
            }
        raise


def create_pull_request(
    repo: str,
    title: str,
    body: str,
    head: str,
    base: Optional[str] = None,
) -> dict[str, Any]:
    print(f"DEBUG: create_pull_request called with repo='{repo}', title='{title}', head='{head}', base='{base}'")
    """
    Create a pull request in a GitHub repository.
    
    Args:
        repo: Repository in "owner/repo" format
        title: PR title
        body: PR description (supports GitHub markdown)
        head: Source branch name
        base: Target branch (defaults to default branch)
        
    Returns:
        Dictionary with PR number, URL, and status
    """
    gh = _get_github_client()
    owner, name = _parse_repo(repo)
    
    try:
        repository = gh.get_repo(f"{owner}/{name}")
        
        if base is None:
            base = repository.default_branch
        
        pr = repository.create_pull(title=title, body=body, head=head, base=base)
        return {
            "number": pr.number,
            "url": pr.html_url,
            "state": pr.state,
            "title": pr.title,
        }
    except GithubException as e:
        if "A pull request already exists" in str(e):
            # Find existing PR
            prs = repository.get_pulls(state="open", head=f"{owner}:{head}")
            for existing_pr in prs:
                return {
                    "number": existing_pr.number,
                    "url": existing_pr.html_url,
                    "state": existing_pr.state,
                    "already_exists": True,
                }
        raise


def update_file(
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    sha: Optional[str] = None,
) -> dict[str, Any]:
    print(f"DEBUG: update_file called with repo='{repo}', path='{path}', message='{message}'", flush=True)
    """
    Create or update a file in a GitHub repository.
    
    Args:
        repo: Repository in "owner/repo" format
        path: Path to the file
        content: New file content
        message: Commit message
        branch: Branch to commit to
        sha: Current file SHA (required for updates, optional for new files)
        
    Returns:
        Dictionary with commit SHA and file info
    """
    gh = _get_github_client()
    owner, name = _parse_repo(repo)
    
    try:
        repository = gh.get_repo(f"{owner}/{name}")
        
        if sha:
            result = repository.update_file(path, message, content, sha, branch=branch)
        else:
            result = repository.create_file(path, message, content, branch=branch)
        
        return {
            "commit_sha": result["commit"].sha,
            "path": path,
            "branch": branch,
        }
    except GithubException as e:
        return {"error": str(e), "path": path}
