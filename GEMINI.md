# Jira Autofix Extension

This extension automates the end-to-end workflow of resolving Jira issues by analyzing tickets, planning fixes, implementing code changes, reviewing them, and opening pull requests.

## Repository Structure

- **Root** — Gemini CLI extension (slash commands, MCP servers, extension config)
- **`async_auto_fix/`** — Standalone Python/Flask agent using Google ADK with Split View UI

## Available Commands

### /jira-autofix
The primary command. Orchestrates the full fix lifecycle for a Jira issue.

**Usage:**
- `jira-autofix SCRUM-1` — Use saved repo, auto-detect, or current directory
- `jira-autofix "SCRUM-1 https://github.com/owner/repo"` — Specify repo explicitly

### /setrepo
Set the default GitHub repository: `/setrepo https://github.com/owner/repo`

### /clearrepo
Clear the saved default repository.

## MCP Servers

### Atlassian (Jira)
- `jira_get_issue` — Fetch issue details
- `jira_search` — Search issues with JQL
- `jira_add_comment` — Add comment to issue

### GitHub
- `create_branch` — Create a new branch
- `create_pull_request` — Create a PR
- `get_file_contents` — Read file from GitHub
- `push_files` / `create_or_update_file` — Push file changes

## Environment Variables
| Variable | Purpose |
|----------|---------|
| `JIRA_URL` | Jira instance URL |
| `JIRA_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | Jira API token |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub PAT with `repo` scope |

## Behavioral Guidelines
- Always confirm the fix plan before making code changes
- Focus on correctness, security, and maintainability during reviews
- If a security review finds CRITICAL issues, pause and present them before creating a PR
- When commenting on Jira, include a PR link and brief summary
- Do not transition Jira ticket status — only add comments
- If already inside the target repo, skip the clone step

## Security Rules
- **Never commit** `.env` files, API keys, or tokens
- Use `.env.example` with placeholders only
- All secrets go in `.env` (gitignored)
