# Contributing

This guide explains how to set up your local development environment for the Jira Autofix extension.

## Prerequisites

You need the following tools installed on your machine:
- **Homebrew** (macOS package manager)
- **Node.js** (Runtime for Gemini CLI)
- **Docker Desktop** (Required for running MCP servers locally)
- **Gemini CLI** (To run and test the extension)

## Step-by-Step Setup

### 1. Install Homebrew
If you don't have Homebrew installed, run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Docker Desktop
Use Homebrew to install Docker:
```bash
brew install --cask docker
```
**Important**: After installation, open **Docker** from your Applications folder to initialize it. It will ask for permissions to install necessary networking tools.

### 3. Install Node.js
```bash
brew install node
```

### 4. Install Gemini CLI
Once Node.js is installed:
```bash
npm install -g @google/gemini-cli
```

## Running Locally

Once all tools are installed and Docker is running:

1.  **Clone the repo** (if you haven't already):
    ```bash
    git clone https://github.com/weitzer-org/jira-autofix-extension.git
    cd jira-autofix-extension
    ```

2.  **Install the extension**:
    ```bash
    gemini extensions install .
    ```

3.  **Run with Debug Mode**:
    ```bash
    /jira-autofix <ISSUE-KEY> --debug
    ```
