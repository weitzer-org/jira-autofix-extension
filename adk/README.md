# ADK Jira Autofix Agent

This is the ADK (Agent Development Kit) version of the Jira Autofix agent.

## Quick Start

The easiest way to get started is using the startup script:

```bash
./adk/start.sh
```

This automatically sets up the virtual environment, installs dependencies, and launches the Flask UI at http://localhost:5000.

### Startup Script Options

| Option | Description |
|--------|-------------|
| `--adk` | Use ADK Dev UI instead of Flask UI |
| `--port N` | Specify custom port (default: 5000 for Flask, 8000 for ADK) |
| `--help` | Show help message |

**Examples:**
```bash
./adk/start.sh              # Flask UI on port 5000
./adk/start.sh --adk        # ADK Dev UI on port 8000
./adk/start.sh --port 3000  # Flask UI on port 3000
```

## Manual Setup

If you prefer manual setup:

```bash
cd adk/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt --index-url https://pypi.org/simple/
```

## Environment Variables

Create a `.env` file in the `adk/` directory (copy from `.env.example`):

```bash
JIRA_URL="https://your-org.atlassian.net"
JIRA_EMAIL="your-email@example.com"
JIRA_API_TOKEN="your-jira-token"
GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."
```

## Running Locally (Manual)

### With ADK Dev UI
```bash
adk web --port 8000
```

### With Flask UI
```bash
cd /path/to/jira-autofix-extension
source adk/venv/bin/activate
python -m adk.ui.app
# Open http://localhost:5000
```

## Project Structure

```
adk/
├── agent.py          # Main ADK agent
├── tools/            # Tool functions
│   ├── jira_tools.py
│   ├── github_tools.py
│   └── git_tools.py
├── workflow/         # Workflow logic
│   └── phases.py
└── ui/               # Web interface
    └── app.py
```
