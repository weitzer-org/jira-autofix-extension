#!/bin/bash
set -e

# Configuration
REPO_DIR="logo-maker-weitzer"
VENV_DIR="async_auto_fix/venv"
FLASK_PORT=5000
TEST_SCRIPT="async_auto_fix/tests/test_full_workflow.py"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Backend E2E Test Runner${NC}"

# 1. Cleanup previous run artifacts
if [ -d "$REPO_DIR" ]; then
    echo "🗑️  Cleaning up previous clone of $REPO_DIR..."
    rm -rf "$REPO_DIR"
fi

# 2. Check and free port 5000
if lsof -Pi :$FLASK_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port $FLASK_PORT is in use. Attempting to free it...${NC}"
    lsof -ti:$FLASK_PORT | xargs kill -9
    sleep 1
fi

# 3. Activate Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_DIR${NC}"
    exit 1
fi
source "$VENV_DIR/bin/activate"

# 4. Start Flask Server
echo "🌐 Starting Flask server..."
python -u -m async_auto_fix.ui.app > flask_e2e.log 2>&1 &
FLASK_PID=$!

# Implement cleanup trap
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if ps -p $FLASK_PID > /dev/null; then
        echo "Stopping Flask server (PID $FLASK_PID)..."
        kill $FLASK_PID || true
    fi
}
trap cleanup EXIT

# 5. Wait for Server
echo "⏳ Waiting for server to be ready..."
MAX_RETRIES=30
count=0
while ! curl -s http://localhost:$FLASK_PORT > /dev/null; do
    sleep 1
    count=$((count+1))
    if [ $count -ge $MAX_RETRIES ]; then
        echo -e "${RED}❌ Server failed to start in time. Check flask_e2e.log${NC}"
        cat flask_e2e.log
        exit 1
    fi
done
echo -e "${GREEN}✓ Server is up!${NC}"

# 6. Run the Test
echo -e "${YELLOW}🧪 Running E2E Test: $TEST_SCRIPT${NC}"
echo "----------------------------------------"

if python "$TEST_SCRIPT"; then
    echo "----------------------------------------"
    echo -e "${GREEN}✅ BACKEND E2E TEST PASSED${NC}"
    exit 0
else
    echo "----------------------------------------"
    echo -e "${RED}❌ BACKEND E2E TEST FAILED${NC}"
    exit 1
fi
