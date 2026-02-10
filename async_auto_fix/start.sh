#!/bin/bash

# ADK Jira Autofix Agent - Startup Script
# This script sets up and runs the Jira Autofix agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🚀 Starting ADK Jira Autofix Agent..."

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        echo "   Copy .env.example to .env and configure your credentials:"
        echo "   cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
    fi
    echo ""
    read -p "Continue without .env? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r "$SCRIPT_DIR/requirements.txt" --index-url https://pypi.org/simple/

# Parse command line arguments
UI_MODE="flask"  # default
PORT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --adk)
            UI_MODE="adk"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --adk       Use ADK Dev UI instead of Flask UI"
            echo "  --port N    Specify port number (default: 5000 for Flask, 8000 for ADK)"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root for module imports
cd "$PROJECT_ROOT"

# Start the UI
if [ "$UI_MODE" = "adk" ]; then
    PORT="${PORT:-8000}"
    echo "🌐 Starting ADK Dev UI on http://localhost:$PORT"
    adk web --port "$PORT"
else
    PORT="${PORT:-5000}"
    echo "🌐 Starting Flask UI on http://localhost:$PORT"
    export FLASK_RUN_PORT="$PORT"
    python -m async_auto_fix.ui.app
fi
