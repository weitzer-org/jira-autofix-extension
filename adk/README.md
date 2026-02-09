# ADK Jira Autofix Agent

This is the ADK (Agent Development Kit) version of the Jira Autofix agent.

## Setup

```bash
cd adk/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

```bash
export JIRA_URL="https://your-org.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-jira-token"
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."
```

## Running Locally

### With ADK Dev UI
```bash
adk web --port 8000
```

### With Flask UI
```bash
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
