# Jira Autofix Extension

This project automates resolving Jira issues end-to-end: reading tickets, planning fixes, implementing code changes, reviewing, and opening pull requests.

## Repository Structure

- **Root** — Gemini CLI extension config, slash commands (`commands/`), MCP server definitions
- **`async_auto_fix/`** — Standalone Python/Flask agent using Google ADK with Split View UI

## How to Run

```bash
# Start the standalone agent UI
./async_auto_fix/start.sh
# Opens at http://localhost:5000

# Run E2E tests
./run_ui_e2e.sh          # Playwright UI test
./run_backend_e2e.sh     # Backend API test
```

## Environment Setup

1. Copy `async_auto_fix/.env.example` to `async_auto_fix/.env`
2. Fill in: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `GOOGLE_API_KEY`
3. Virtual environment is in `async_auto_fix/venv/`

## Tech Stack
- **Python 3.12**, Flask, Google ADK (`google-adk`)
- **Playwright** for E2E testing
- **Jinja2** templates, vanilla CSS/JS frontend

## Code Conventions
- Python imports use `from async_auto_fix.xxx import yyy`
- Module entry point: `python -m async_auto_fix.ui.app`
- All tools are in `async_auto_fix/tools/` (Jira, GitHub, Git)
- Workflow phases defined in `async_auto_fix/workflow/phases.py`

## Security Rules
- **Never commit** `.env` files, API keys, or tokens
- Use `.env.example` with placeholders only
- All secrets go in `.env` (gitignored)
