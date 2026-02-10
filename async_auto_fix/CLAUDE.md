# Async Auto-Fix Agent (ADK)

Standalone Python/Flask agent that automates Jira issue resolution using Google's Agent Development Kit (ADK).

## Architecture

```
async_auto_fix/
├── agent.py              # ADK agent definition + system instructions
├── tools/                # Tool implementations
│   ├── jira_tools.py     # get_jira_issue, search_jira, add_jira_comment
│   ├── github_tools.py   # create_branch, create_pull_request, get_file_contents, update_file
│   └── git_tools.py      # clone_repo, checkout_branch, commit_and_push
├── workflow/
│   └── phases.py         # 7 workflow phases + WorkflowState management
├── ui/
│   ├── app.py            # Flask routes (/api/start, /api/run, /api/approve)
│   ├── templates/        # Jinja2 HTML (Split View dashboard)
│   └── static/           # CSS (dark theme) + JS (dynamic updates)
├── tests/                # Playwright + API E2E tests
├── start.sh              # Entry point script
└── requirements.txt      # google-adk, flask, etc.
```

## Workflow Phases

| # | Phase | Approval Required |
|---|-------|:-:|
| 1 | Gather Jira Context | No |
| 2 | Set Up Repository | No |
| 3 | Plan the Fix | **Yes** |
| 4 | Implement the Fix | No |
| 5 | Security & Code Review | **Yes** |
| 6 | Create Pull Request | No |
| 7 | Update Jira Ticket | No |

## Key Patterns
- Phases 3 and 5 require human approval (modal dialog in UI)
- Backend returns `status: "awaiting_approval"` for approval phases, `status: "success"` otherwise
- Flask sessions stored server-side (`flask-session` package)
- ADK agent runs async via `asyncio.run()` in sync Flask routes

## Running
```bash
./async_auto_fix/start.sh          # Flask UI on port 5000
./async_auto_fix/start.sh --adk    # ADK Dev UI on port 8000
```

## Testing
```bash
./run_ui_e2e.sh          # Full Playwright UI test
./run_backend_e2e.sh     # Backend API test
```
