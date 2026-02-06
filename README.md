# Jira Autofix Extension for Gemini CLI

An extension for [Gemini CLI](https://github.com/google-gemini/gemini-cli) that automates the workflow of resolving Jira issues — from reading the ticket to opening a pull request with the fix.

## Overview

The Jira Autofix extension provides a single, guided command (`/jira-autofix`) that orchestrates the full lifecycle of fixing a Jira issue: fetching context from Jira, cloning the relevant repo, planning a fix, implementing it, reviewing the code, and opening a PR on GitHub.

---

## Customer Workflow

### Step 1: Provide Jira Ticket
The developer invokes the command and provides a link (or key) to a Jira ticket:
```
/jira-autofix https://myorg.atlassian.net/browse/PROJ-1234
```

### Step 2: Fetch Jira Issue Context
The extension uses the **Jira MCP server** to:
- Retrieve the issue summary, description, acceptance criteria, and comments
- Fetch linked/related issues (parent epics, blockers, subtasks) for additional context
- Identify relevant labels, components, and priority

### Step 3: Provide GitHub Repository
The developer specifies the GitHub repository associated with the issue:
- Can be provided as a command argument, or
- The extension prompts the developer to provide the repo URL
- Example: `https://github.com/myorg/my-service`

### Step 4: Clone Repository Locally
The extension:
- Clones the GitHub repo into a local working directory
- Checks out the default branch (e.g., `main`)
- Ensures the workspace is clean and ready for changes

### Step 5: Create & Approve Fix Plan
The Gemini model:
- Analyzes the Jira issue context alongside the codebase
- Produces a structured plan detailing which files to change, what logic to add/modify, and why
- Presents the plan to the developer for review
- The developer **approves** the plan or **provides feedback** to revise it
- This loop repeats until the developer is satisfied

### Step 6: Implement the Fix
After plan approval, the Gemini model:
- Makes the code changes described in the approved plan
- Runs any available test suites to validate the fix
- Reports results back to the developer

### Step 7: Run Security & Code Review
The extension leverages the **security** and **code-review** extensions (or equivalent built-in analysis) to:
- Scan the diff for security vulnerabilities (injection, secrets, weak crypto, etc.)
- Review the code changes for bugs, performance issues, and maintainability concerns
- Present findings to the developer; critical issues block progression

### Step 8: Create Branch & Pull Request
Using the **GitHub MCP server**, the extension:
- Creates a new feature branch (e.g., `fix/PROJ-1234-short-description`)
- Commits all changes with a descriptive message referencing the Jira ticket
- Pushes the branch to the remote
- Opens a pull request with:
  - Title referencing the Jira issue key
  - Body containing the fix summary, link to the Jira ticket, and review notes

### Step 9: Update Jira Ticket
Using the **Jira MCP server**, the extension posts a comment back to the original Jira issue containing:
- A summary of what was fixed
- A link to the GitHub pull request
- The review results (security + code review status)

---

## Requirements

### External Dependencies (MCP Servers)

| MCP Server | Purpose | Used In |
|---|---|---|
| **Jira MCP Server** | Fetch issue details, linked issues, post comments | Steps 2, 9 |
| **GitHub MCP Server** | Create branches, push commits, open PRs | Step 8 |

### Extension Dependencies

| Extension | Purpose | Used In |
|---|---|---|
| **security** (`gemini-cli-extensions/security`) | Vulnerability scanning of code changes | Step 7 |
| **code-review** (`gemini-cli-extensions/code-review`) | Code quality review of changes | Step 7 |

### Extension Components

| Component | Description |
|---|---|
| `gemini-extension.json` | Manifest declaring MCP servers and context file |
| `GEMINI.md` | Context instructions for the model during sessions |
| `commands/jira-autofix.toml` | Main command defining the orchestration prompt |
| `mcp-server/` | (If needed) Custom MCP tools for cloning repos, running tests, etc. |

---

## Architecture

```
jira-autofix-extension/
├── gemini-extension.json        # Extension manifest
├── GEMINI.md                    # Model context & instructions
├── README.md                    # This file
├── commands/
│   └── jira-autofix.toml        # Main orchestration command
└── mcp-server/                  # Optional: custom tooling
    ├── package.json
    ├── tsconfig.json
    └── src/
        └── index.ts
```

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

## Decisions Made

1. **Jira MCP Server** — Official Atlassian remote MCP server (`atlassian/atlassian-mcp-server`) via `npx mcp-remote`. Uses OAuth 2.1 browser flow — no API tokens to manage.
2. **GitHub MCP Server** — Official `github/github-mcp-server` via Docker. PAT-based auth stored securely via Gemini CLI extension settings (`sensitive: true` → OS keychain).
3. **Authentication** — Jira: zero-config OAuth. GitHub: single PAT prompted at install time, stored in system keychain.

## Open Questions

1. **Repo cloning** — Should we use a built-in shell tool (`git clone`) or a custom MCP tool for cloning?
2. **Test execution** — Should the extension automatically detect and run tests, or leave that to the developer?
3. **Security/Code Review** — Should we depend on the existing extensions, or bundle equivalent prompts inline?
4. **Scope** — Should the command support providing both the Jira ticket and repo URL as arguments, or always prompt interactively?
