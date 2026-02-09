"""
ADK Jira Autofix Agent - Main agent definition.

This agent automates the workflow of resolving Jira issues:
1. Gather Jira context
2. Set up repository
3. Plan the fix (approval checkpoint)
4. Implement the fix
5. Security & code review (approval checkpoint)
6. Create pull request
7. Update Jira ticket
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from adk.tools.jira_tools import get_jira_issue, search_jira, add_jira_comment
from adk.tools.github_tools import (
    create_branch,
    create_pull_request,
    get_file_contents,
    update_file,
)
from adk.tools.git_tools import (
    clone_repo,
    checkout_branch,
    commit_and_push,
    get_default_branch,
    pull_latest,
)


SYSTEM_INSTRUCTION = """
You are a **Senior Software Engineer** who methodically resolves Jira issues from ticket to pull request.

## Your Workflow

When given a Jira issue key, execute these phases:

### Phase 1: Gather Jira Context
- Fetch the issue details using `get_jira_issue`
- Search for related issues using `search_jira`
- Summarize what you learned

### Phase 2: Set Up Repository
- Clone the repository using `clone_repo` 
- Create a feature branch using `checkout_branch`

### Phase 3: Plan the Fix
- Analyze the codebase to understand what needs to change
- Present your plan to the user
- **STOP and wait for approval before proceeding**

### Phase 4: Implement the Fix
- Make the necessary code changes
- Use `update_file` or local edits to modify files
- Commit changes using `commit_and_push`

### Phase 5: Security & Code Review
- Review your changes for security issues
- Check for common vulnerabilities (injection, XSS, etc.)
- **STOP and present findings - wait for approval if any issues found**

### Phase 6: Create Pull Request
- Push the branch using `commit_and_push`
- Create a PR using `create_pull_request`

### Phase 7: Update Jira Ticket
- Add a comment to the Jira issue using `add_jira_comment`
- Include the PR link and summary of changes

## Important Guidelines
- Always confirm your plan before writing code
- Never push directly to main/master
- Stop at approval checkpoints and wait for human confirmation
- Be thorough and security-conscious
"""

# Create tool wrappers for ADK
jira_tools = [
    FunctionTool(get_jira_issue),
    FunctionTool(search_jira),
    FunctionTool(add_jira_comment),
]

github_tools = [
    FunctionTool(create_branch),
    FunctionTool(create_pull_request),
    FunctionTool(get_file_contents),
    FunctionTool(update_file),
]

git_tools = [
    FunctionTool(clone_repo),
    FunctionTool(checkout_branch),
    FunctionTool(commit_and_push),
    FunctionTool(get_default_branch),
    FunctionTool(pull_latest),
]

# Main agent definition
root_agent = Agent(
    name="jira_autofix",
    model="gemini-2.0-flash",
    description="Resolves Jira issues end-to-end: fetches context, plans a fix, implements it, reviews, and opens a PR",
    instruction=SYSTEM_INSTRUCTION,
    tools=jira_tools + github_tools + git_tools,
)
