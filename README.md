# Jira Autofix Extension for Gemini CLI

An extension for [Gemini CLI](https://github.com/google-gemini/gemini-cli) that automates the workflow of resolving Jira issues — from reading the ticket to opening a pull request with the fix.

## Overview

The Jira Autofix extension provides a single command (`/jira-autofix`) that orchestrates the full lifecycle of fixing a Jira issue: fetching context from Jira, cloning the relevant repo, planning a fix, implementing it, reviewing the code, opening a PR on GitHub, and posting the result back to Jira.

---

## Prerequisites

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) v0.4.0 or newer
- [Docker](https://docs.docker.com/get-docker/) (for the GitHub MCP server)
- [Node.js](https://nodejs.org/) v18+ and npm (optional, for development)
- A **GitHub Personal Access Token** with `repo` scope — [create one here](https://github.com/settings/tokens)
- A **Jira API Token** — [create one here](https://id.atlassian.com/manage-profile/security/api-tokens)

### How to generate a Jira API Token
1. Log in to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
2. Click **Create API token**.
3. Give it a label (e.g., "Gemini CLI").
4. Copy the token to your clipboard—you will need it for the installation prompt.

## Installing Gemini CLI

If you don't have Gemini CLI installed yet:

```bash
# Install via npm (requires Node.js 18+)
npm install -g @anthropic-ai/gemini-cli

# Or install via the official installer
curl -fsSL https://cli.gemini.google.dev/install.sh | bash
```

Verify the installation:

```bash
gemini --version
```

For detailed instructions, see the [Gemini CLI Getting Started guide](https://github.com/google-gemini/gemini-cli#getting-started).

## Installing This Extension

### Step 1: Install the extension

```bash
gemini extensions install https://github.com/weitzer-org/jira-autofix-extension
```

During installation you will be prompted for:

| Prompt | What to enter |
|---|---|
| **GitHub Personal Access Token** | A PAT with `repo` scope. **Warning**: Input is stored in plain text in your config file. |
| **Jira URL** | Your Jira instance URL (e.g., `https://myorg.atlassian.net`). |
| **Jira Email** | The email address you use to log in to Jira. |
| **Jira API Token** | A Jira API token. Create one at [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens). |

### Step 3: Verify the extension is installed

```bash
gemini extensions list
```

You should see `jira-autofix` in the list of installed extensions and it should be connected to both GitHub and Jira (via Docker).

### Debug Mode

If you encounter issues or want to see exactly what the extension is doing, you can run it with the `--debug` flag:

```bash
gemini run jira-autofix "<JIRA-URL> --debug"
```

This will print detailed logs (prefixed with `🐛 [DEBUG]:`) before every tool execution, helping you troubleshoot connection or logic issues.



### Managing the extension

```bash
# Update to the latest version
gemini extensions update jira-autofix

# Uninstall
gemini extensions uninstall jira-autofix

# Temporarily disable
gemini extensions disable jira-autofix

# Re-enable
gemini extensions enable jira-autofix
```

## Usage

### Basic Usage

**Important**: You must use `gemini run` to execute this command. Do NOT use `gemini /jira-autofix` (which sends it as a chat message).

```bash
gemini run jira-autofix "<ISSUE_KEY_OR_URL>"
```

Example:
```bash
gemini run jira-autofix "SCRUM-1"
```

### With Debug Mode

To see verbose logs, append the `--debug` flag **inside the quotes**:

```bash
gemini run jira-autofix "SCRUM-1 --debug"
```

> [!TIP]
> If you see an authentication error like `Cannot create property 'refresh_token'`, run this command to refresh your Cloud Shell credentials:
> ```bash
> gcloud auth application-default login
> ```

### Interactive Mode

Alternatively, start the interactive shell:

```bash
gemini
> /jira-autofix SCRUM-1 --debug
```

### From inside a repository

If you're already `cd`'d into the relevant repo, the extension will detect it and skip cloning:

```
cd ~/projects/my-service
gemini
> /jira-autofix PROJ-1234
```

If you're **not** inside the repo, the extension will ask you for the GitHub repo URL and clone it automatically.

## What Happens

When you run `/jira-autofix`, the extension walks through these steps:

| Step | What happens | Your input needed |
|---|---|---|
| 1. Fetch Jira context | Reads the issue, related issues, and comments from Jira | None |
| 2. Set up repository | Detects or clones the GitHub repo | Repo URL (if not detected) |
| 3. Plan the fix | Analyzes the codebase and presents a fix plan | Approve or revise the plan |
| 4. Implement the fix | Makes code changes and runs tests | None (reviews results) |
| 5. Review changes | Runs security and code quality review on the diff | Address critical findings (if any) |
| 6. Open pull request | Creates a branch, commits, pushes, and opens a PR | None |
| 7. Update Jira | Posts a comment on the Jira issue with the PR link | None |

### Developer Checkpoints

The extension pauses for your input at two key points:

1. **Plan approval** (Step 3) — You must approve the plan before any code is written. You can provide feedback to revise it.
2. **Critical findings** (Step 5) — If the security review finds CRITICAL issues, the extension stops and asks how you want to proceed.

## Configuration

### Extension Settings

Settings are managed via Gemini CLI:

```bash
# View current settings
gemini extensions list

# Update a setting
gemini extensions config jira-autofix "GitHub Personal Access Token"

# Update for a specific workspace
gemini extensions config jira-autofix "GitHub Personal Access Token" --scope workspace

# Update Jira settings
gemini extensions config jira-autofix "Jira URL"
gemini extensions config jira-autofix "Jira Email"
gemini extensions config jira-autofix "Jira API Token"
```

> [!WARNING]
> The **GitHub Personal Access Token** and **Jira API Token** are stored in plain text in your configuration file. Ensure this file is not shared.

### GitHub Token Scopes

The minimum required scope for your GitHub PAT is `repo`. This grants:
- Read access to repository contents
- Write access to create branches, push commits, and open PRs

### Atlassian Auth

The Atlassian MCP server uses **API Tokens** for authentication. This eliminates the need for interactive OAuth flows. Your credentials are securely passed to the Docker container via environment variables.

To connect to a different Atlassian tenant, simply update the extension configuration using `gemini extensions config`.



## Development

To develop this extension locally:

```bash
git clone https://github.com/weitzer-org/jira-autofix-extension
cd jira-autofix-extension
gemini extensions link .
```

Changes to `GEMINI.md`, `gemini-extension.json`, and `commands/jira-autofix.toml` are reflected immediately — no reinstall needed.

## File Structure

```
jira-autofix-extension/
├── gemini-extension.json        # Extension manifest (MCP servers, settings)
├── GEMINI.md                    # Model context loaded every session
├── README.md                    # This file
└── commands/
    └── jira-autofix.toml        # Main command prompt
```

---

## Workflow Details

### Step 1: Fetch Jira Issue Context
The extension uses the **Atlassian MCP server** to:
- Retrieve the issue summary, description, acceptance criteria, and comments
- Fetch linked/related issues (parent epics, blockers, subtasks) for additional context
- Identify relevant labels, components, and priority

### Step 2: Set Up Repository
The developer specifies the GitHub repository associated with the issue:
- If already inside the repo, the extension detects it and confirms
- Otherwise, the developer provides the repo URL
- The extension clones the repo and checks out the default branch

### Step 3: Plan the Fix
The Gemini model:
- Analyzes the Jira issue context alongside the codebase
- Produces a structured plan detailing which files to change, what logic to add/modify, and why
- Presents the plan to the developer for review
- The developer **approves** the plan or **provides feedback** to revise it

### Step 4: Implement the Fix
After plan approval, the Gemini model:
- Makes the code changes described in the approved plan
- Runs any available test suites to validate the fix
- Reports results back to the developer

### Step 5: Review Changes
The extension performs inline analysis of the diff to:
- Scan for security vulnerabilities (injection, secrets, weak crypto, etc.)
- Review code changes for bugs, performance issues, and maintainability
- Present findings classified as CRITICAL, HIGH, MEDIUM, or LOW
- Critical findings block progression until the developer responds

### Step 6: Open Pull Request
Using the **GitHub MCP server**, the extension:
- Creates a feature branch (e.g., `fix/PROJ-1234-short-description`)
- Commits all changes with a descriptive message referencing the Jira ticket
- Pushes the branch and opens a pull request with a structured body

### Step 7: Update Jira
Using the **Atlassian MCP server**, the extension posts a comment on the Jira issue with:
- A summary of what was fixed
- A link to the GitHub pull request
- The security and code review status

---

## Sequence Diagram

```
Developer          Gemini CLI           Jira MCP          GitHub MCP
    │                  │                    │                  │
    │  /jira-autofix   │                    │                  │
    │  + ticket URL    │                    │                  │
    │─────────────────>│                    │                  │
    │                  │  get issue details  │                  │
    │                  │───────────────────>│                  │
    │                  │  issue context     │                  │
    │                  │<───────────────────│                  │
    │  provide repo    │                    │                  │
    │─────────────────>│                    │                  │
    │                  │  clone repo (shell)│                  │
    │                  │──────────┐         │                  │
    │                  │<─────────┘         │                  │
    │  review plan     │                    │                  │
    │<─────────────────│                    │                  │
    │  approve/revise  │                    │                  │
    │─────────────────>│                    │                  │
    │                  │  implement fix     │                  │
    │                  │──────────┐         │                  │
    │                  │<─────────┘         │                  │
    │                  │  security + review │                  │
    │                  │──────────┐         │                  │
    │                  │<─────────┘         │                  │
    │  review results  │                    │                  │
    │<─────────────────│                    │                  │
    │                  │  create branch+PR  │                  │
    │                  │──────────────────────────────────────>│
    │                  │  PR link           │                  │
    │                  │<──────────────────────────────────────│
    │                  │  post comment      │                  │
    │                  │───────────────────>│                  │
    │                  │  confirmed         │                  │
    │                  │<───────────────────│                  │
    │  done + PR link  │                    │                  │
    │<─────────────────│                    │                  │
```

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Jira MCP server | Docker `ghcr.io/sooperset/mcp-atlassian` | Supports API token auth, no hang on startup |
| GitHub MCP server | Official (`github/github-mcp-server`) via Docker | Maintained by GitHub, broadest tool support |
| Jira auth | API Token (env vars) | Configuration-based, non-interactive |
| GitHub auth | PAT via extension settings (`sensitive: false`) | Stored in extension config (plain text) |
| Repo handling | Detect local repo or clone | Avoids unnecessary cloning |
| Test execution | Auto-detect and run | Reports results but does not block |
| Security/Code review | Bundled inline prompts | No extra extension dependencies |
| Branch naming | `fix/<issue-key>-<description>` | Consistent convention for all issue types |
| Jira updates | Comment only | Less risky than status transitions |
| PR reviewers | Not auto-assigned | Left to the developer |
| Failure handling | Pause and present | Developer decides how to proceed |
| Issue types | All types supported | Workflow is the same regardless |

## License

Apache-2.0
