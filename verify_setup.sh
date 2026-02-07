#!/bin/bash
echo "🔍 Checking Gemini CLI Environment..."

echo "1. Gemini Version:"
gemini --version

echo "2. Docker Version:"
docker --version

echo "3. Extension List:"
gemini extensions list

echo "4. Running simple Docker test:"
docker run --rm hello-world

echo "5. Checking environment variables (masked):"
echo "JIRA_URL: ${JIRA_URL:0:4}..."
echo "JIRA_API_TOKEN: ${JIRA_API_TOKEN:0:4}..."
