"""Jira API tools for ADK agent."""
import os
from typing import Any
from atlassian import Jira


def _get_jira_client() -> Jira:
    """Get authenticated Jira client."""
    return Jira(
        url=os.environ["JIRA_URL"],
        username=os.environ["JIRA_EMAIL"],
        password=os.environ["JIRA_API_TOKEN"],
        cloud=True,
    )


def get_jira_issue(issue_key: str) -> dict[str, Any]:
    """
    Fetch a Jira issue by its key.
    
    Args:
        issue_key: The Jira issue key (e.g., "SCRUM-1")
        
    Returns:
        Dictionary containing issue details including:
        - key: Issue key
        - summary: Issue title
        - description: Full description
        - status: Current status
        - priority: Priority level
        - assignee: Assigned user
        - labels: List of labels
        - components: List of components
    """
    jira = _get_jira_client()
    issue = jira.issue(issue_key, fields="*all")
    
    fields = issue.get("fields", {})
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": fields.get("status", {}).get("name") if fields.get("status") else None,
        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
        "labels": fields.get("labels", []),
        "components": [c.get("name") for c in fields.get("components", [])],
        "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
        "created": fields.get("created"),
        "updated": fields.get("updated"),
    }


def search_jira(jql: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search Jira issues using JQL.
    
    Args:
        jql: JQL query string (e.g., 'project = SCRUM AND status = "In Progress"')
        max_results: Maximum number of results to return
        
    Returns:
        List of matching issues with key, summary, and status
    """
    jira = _get_jira_client()
    results = jira.jql(jql, limit=max_results)
    
    issues = []
    for issue in results.get("issues", []):
        fields = issue.get("fields", {})
        issues.append({
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name") if fields.get("status") else None,
            "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
        })
    return issues


def add_jira_comment(issue_key: str, comment: str) -> dict[str, Any]:
    """
    Add a comment to a Jira issue.
    
    Args:
        issue_key: The Jira issue key
        comment: Comment text (supports Jira markdown)
        
    Returns:
        Dictionary with comment ID and creation timestamp
    """
    jira = _get_jira_client()
    result = jira.issue_add_comment(issue_key, comment)
    
    return {
        "id": result.get("id"),
        "created": result.get("created"),
        "body": result.get("body"),
    }
