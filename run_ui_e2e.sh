#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/benw307/logo-maker-weitzer"
REPO_DIR="logo-maker-weitzer"
VENV_DIR="adk/venv"

echo "🚀 Starting UI E2E Test Runner"

# 1. Cleanup Previous Run
if [ -d "$REPO_DIR" ]; then
    echo "🗑️  Cleaning up previous clone of $REPO_DIR..."
    rm -rf "$REPO_DIR"
fi

# Kill any existing Flask process on port 5000
if lsof -i :5000 > /dev/null; then
    echo "⚠️  Port 5000 is in use. Attempting to free it..."
    lsof -ti :5000 | xargs kill -9 || true
    sleep 2
fi

# 2. Activate Virtual Environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment not found at $VENV_DIR"
    exit 1
fi

# 3. Check for dependencies
if ! pip show pytest-playwright > /dev/null; then
    echo "⚠️  pytest-playwright not installed. Installing..."
    pip install pytest-playwright
    playwright install chromium
fi

# 4. Start Flask Server
echo "🌐 Starting Flask server..."
# We use python -u for unbuffered output to catch startup errors/logs
python -u -m adk.ui.app > flask_ui_e2e.log 2>&1 &
FLASK_PID=$!

# Implement cleanup trap
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    if [ -n "$FLASK_PID" ]; then
        echo "Stopping Flask server (PID $FLASK_PID)..."
        kill $FLASK_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# 5. Wait for Server
echo "⏳ Waiting for server to be ready..."
MAX_RETRIES=30
for ((i=1; i<=MAX_RETRIES; i++)); do
    if curl -s http://localhost:5000 > /dev/null; then
        echo "✓ Server is up!"
        SERVER_READY=true
        break
    fi
    sleep 1
done

if [ "$SERVER_READY" != "true" ]; then
    echo "❌ Server failed to start. Check logs:"
    cat flask_ui_e2e.log
    exit 1
fi

# 6. Run UI Test
echo "🧪 Running UI Test: adk/tests/test_ui_e2e.py"
echo "----------------------------------------"

# Run pytest on the UI test file (default browser: chromium)
pytest adk/tests/test_ui_e2e.py

TEST_EXIT_CODE=$?

echo "----------------------------------------"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ UI E2E TEST PASSED"
else
    echo "❌ UI E2E TEST FAILED"
    echo "Check flask_ui_e2e.log for server errors:"
    tail -n 50 flask_ui_e2e.log
fi

exit $TEST_EXIT_CODE
