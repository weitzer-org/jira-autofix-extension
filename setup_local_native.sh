#!/bin/bash
set -e

# setup_local_native.sh
# Installs the Jira Autofix Extension using native Python (via uv) to bypass Docker networking issues.
# Requires: uv (Santa-approved version), Python 3.10+ (Santa-approved version)
# Usage: ./setup_local_native.sh

# 1. Check for required tools
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found. Please install uv and ensure it is in your PATH."
    exit 1
fi

# 2. Check for required environment variables (or prompt)
if [ -z "$JIRA_URL" ]; then read -p "Enter JIRA_URL (e.g., https://your-domain.atlassian.net): " JIRA_URL; fi
if [ -z "$JIRA_EMAIL" ]; then read -p "Enter JIRA_EMAIL (e.g., user@example.com): " JIRA_EMAIL; fi
if [ -z "$JIRA_API_TOKEN" ]; then read -s -p "Enter JIRA_API_TOKEN: " JIRA_API_TOKEN; echo ""; fi

if [ -z "$JIRA_URL" ] || [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Missing required credentials. Please set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN."
    exit 1
fi

echo "🧹 Uninstalling existing extension..."
gemini extensions uninstall jira-autofix || true
rm -rf .venv

echo "🐍 Setting up Python environment via uv..."
# Install Python 3.12 managed by uv
uv python install 3.12
# Create venv
uv venv --python 3.12
# Activate venv
source .venv/bin/activate
# Install mcp-atlassian from PyPI (public index)
echo "📦 Installing mcp-atlassian..."
uv pip install mcp-atlassian --index-url https://pypi.org/simple

# Get absolute path to the venv python executable
# We use the python binary directly to avoid shebang issues and ensure we control arguments
VENV_PYTHON="$(pwd)/.venv/bin/python3"
MCP_SCRIPT="$(pwd)/.venv/bin/mcp-atlassian"

if [ ! -f "$MCP_SCRIPT" ]; then
    echo "❌ Failed to find mcp-atlassian script at $MCP_SCRIPT"
    exit 1
fi

echo "📝 Backing up manifest..."
cp gemini-extension.json gemini-extension.json.bak

echo "🔧 Configuring Manifest for Native Execution..."
# Node script to rewrite manifest configuration
# Uses explicit CLI flags for robustness
export JIRA_URL
export JIRA_EMAIL
export JIRA_API_TOKEN
export VENV_PYTHON
export MCP_SCRIPT

node -e '
const fs = require("fs");
const manifest = JSON.parse(fs.readFileSync("gemini-extension.json", "utf8"));

const JIRA_URL = process.env.JIRA_URL;
const JIRA_EMAIL = process.env.JIRA_EMAIL;
const JIRA_TOKEN = process.env.JIRA_API_TOKEN;
const PYTHON = process.env.VENV_PYTHON;
const SCRIPT = process.env.MCP_SCRIPT;

// Construct command: python script -v --flags ...
// We use "sh -c" to wrap the command string execution
const cmd = `"${PYTHON}" "${SCRIPT}" -v --jira-url "${JIRA_URL}" --jira-username "${JIRA_EMAIL}" --jira-token "${JIRA_TOKEN}"`;

manifest.mcpServers.atlassian.command = "/bin/sh";
manifest.mcpServers.atlassian.args = ["-c", cmd];
manifest.mcpServers.atlassian.env = {}; 

// Remove settings to prevent interactive prompts during verify
manifest.settings = [];

fs.writeFileSync("gemini-extension.json", JSON.stringify(manifest, null, 2));
'

echo "📦 Installing extension..."
# Pipe 'y' to auto-confirm installation
printf "y\n" | gemini extensions install .

echo "♻️  Restoring original manifest..."
mv gemini-extension.json.bak gemini-extension.json

echo "✅ Setup Complete!"
echo "To verify: gemini run --debug \"Fetch details for SCRUM-1 using jira_get_issue\""
