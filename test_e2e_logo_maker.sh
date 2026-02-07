#!/bin/bash

# Configuration
REPO_URL="https://github.com/benw307/logo-maker-weitzer"
REPO_DIR="logo-maker-weitzer"
ISSUE_KEY="SCRUM-1"
# Use --prompt for non-interactive mode (bypasses some prompts)
COMMAND="gemini run jira-autofix \"$ISSUE_KEY --debug\""

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Robust End-to-End Test for $ISSUE_KEY on $REPO_URL${NC}"

# Check dependencies
if ! command -v expect &> /dev/null; then
    echo "Error: 'expect' is required."
    exit 1
fi

# 1. Clean and Setup Repo
echo "cleaning up old repo..."
rm -rf "$REPO_DIR"
echo "Cloning $REPO_URL..."
git clone "$REPO_URL" "$REPO_DIR" || { echo "Clone failed"; exit 1; }

cd "$REPO_DIR" || exit 1

# 2. Run with Expect
# - Timeout extended to 10 minutes for slow operations
# - Spawns command inside the repo dir
# - Matches partial strings carefully

# Disable colors to simplifying expect matching
export NO_COLOR=1

/usr/bin/expect <<EOF
set timeout 600
spawn $COMMAND

# Enable debug logging
exp_internal 1
match_max 100000

expect {
    # 1. Antigravity Prompt
    "Do you want to connect Antigravity*" {
        send "3\r"
        exp_continue
    }

    # 2. MCP Permission Prompts
    # Match "Action Required" header or "Allow execution" loosely
    # -re enables regex matching
    -re "Action Required" {
        send "3\r"
        exp_continue
    }
    -re "Allow execution of MCP tool" {
        send "3\r"
        exp_continue
    }
    
    # 3. Repository Confirmation
    -re "Should I work in this repository" {
        sleep 1
        send "Yes\r"
        exp_continue
    }

    # 4. Plan Approval / Execution
    # --yolo handles tool calls, but sometimes it asks for overall plan approval
    "Do you want to proceed*" {
        send "Yes\r"
        exp_continue
    }

    # 4. Plan Approval / Execution
    # --yolo handles tool calls, but sometimes it asks for overall plan approval
    "Do you want to proceed*" {
        send "Yes\r"
        exp_continue
    }
    
    # 5. Success / Completion
    "Pull Request created*" {
        puts "\n✅ PR Created Successfully!"
        exit 0
    }
    
    # 6. Timeout
    timeout {
        puts "\n❌ Timeout waiting for prompt or completion."
        exit 1
    }
    
    # 7. EOF (Process exited)
    eof {
        puts "\nℹ️ Process exited."
        # Check exit status?
    }
}
EOF
