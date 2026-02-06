# Jira Autofix Extension

This extension automates the end-to-end workflow of resolving Jira issues by analyzing tickets, planning fixes, implementing code changes, reviewing them, and opening pull requests.

## Available Commands

### /jira-autofix

The primary command. Orchestrates the full fix lifecycle for a Jira issue.

When a user wants to fix a Jira issue, resolve a bug, or implement a task from Jira, this command should be the preferred way to do so.

## MCP Servers Available

### Atlassian (Jira)
Use the Atlassian MCP server tools to:
- Fetch Jira issue details (`jira_get_issue`)
- Search for related issues (`jira_search`)
- Get remote links on issues (`jira_get_issue_link_types`)
- Add comments to issues (`jira_add_comment`)

### GitHub
Use the GitHub MCP server tools to:
- Create branches (`create_branch`)
- Push file changes (`push_files`, `create_or_update_file`)
- Create pull requests (`create_pull_request`)
- Read repository contents (`get_file_contents`)

## Behavioral Guidelines

- Always confirm the fix plan with the developer before making code changes.
- When reviewing code, focus on correctness, security, and maintainability.
- If a security or code review finds CRITICAL issues, pause and present them to the developer before proceeding to create a PR.
- When posting a comment back to Jira, include a link to the PR and a brief summary of the changes made.
- Do not transition Jira ticket status — only add comments.
- If the developer is already inside the target repository, skip the clone step.
