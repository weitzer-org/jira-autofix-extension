"""
Tests for gemini-extension.json configuration file.
"""
import json
import os
import pytest


class TestExtensionConfig:
    """Test suite for gemini-extension.json validation."""

    @pytest.fixture
    def extension_config_path(self):
        """Path to the extension configuration file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")

    @pytest.fixture
    def extension_config(self, extension_config_path):
        """Load the extension configuration."""
        with open(extension_config_path, 'r') as f:
            return json.load(f)

    def test_json_is_valid(self, extension_config_path):
        """Verify the JSON file is valid and parseable."""
        with open(extension_config_path, 'r') as f:
            config = json.load(f)
        assert isinstance(config, dict)

    def test_required_fields_exist(self, extension_config):
        """Verify all required top-level fields are present."""
        required_fields = ["name", "version", "description", "contextFileName", "mcpServers", "prompts", "settings"]
        for field in required_fields:
            assert field in extension_config, f"Required field '{field}' is missing"

    def test_name_is_jira_autofix(self, extension_config):
        """Verify the extension name is 'jira-autofix'."""
        assert extension_config["name"] == "jira-autofix"

    def test_version_format(self, extension_config):
        """Verify version follows semantic versioning."""
        version = extension_config["version"]
        assert isinstance(version, str)
        parts = version.split(".")
        assert len(parts) == 3, "Version should be in format X.Y.Z"
        for part in parts:
            assert part.isdigit(), "Each version part should be numeric"

    def test_context_file_exists(self, extension_config):
        """Verify the contextFileName points to an existing file."""
        context_file = extension_config["contextFileName"]
        assert context_file == "GEMINI.md"
        context_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), context_file)
        assert os.path.exists(context_path), f"Context file {context_file} does not exist"

    def test_mcp_servers_configuration(self, extension_config):
        """Verify MCP servers are properly configured."""
        mcp_servers = extension_config["mcpServers"]
        assert isinstance(mcp_servers, dict)

        # Check atlassian server
        assert "atlassian" in mcp_servers
        atlassian = mcp_servers["atlassian"]
        assert atlassian["command"] == "docker"
        assert "args" in atlassian
        assert isinstance(atlassian["args"], list)
        assert "env" in atlassian
        assert atlassian["env"]["JIRA_USERNAME"] == "$JIRA_EMAIL"

        # Check github server
        assert "github" in mcp_servers
        github = mcp_servers["github"]
        assert github["command"] == "docker"
        assert "args" in github
        assert isinstance(github["args"], list)
        assert "env" in github
        assert github["env"]["GITHUB_TOOLSETS"] == "repos,pull_requests,context"

    def test_docker_image_references(self, extension_config):
        """Verify Docker images are properly referenced."""
        atlassian_args = extension_config["mcpServers"]["atlassian"]["args"]
        assert "ghcr.io/sooperset/mcp-atlassian" in atlassian_args

        github_args = extension_config["mcpServers"]["github"]["args"]
        assert "ghcr.io/github/github-mcp-server" in github_args

    def test_prompts_configuration(self, extension_config):
        """Verify prompts are properly configured."""
        prompts = extension_config["prompts"]
        assert isinstance(prompts, dict)
        assert "jira-autofix" in prompts
        assert prompts["jira-autofix"] == "commands/jira-autofix.toml"

        # Verify the prompt file exists
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), prompts["jira-autofix"])
        assert os.path.exists(prompt_path), f"Prompt file {prompts['jira-autofix']} does not exist"

    def test_settings_configuration(self, extension_config):
        """Verify settings are properly configured."""
        settings = extension_config["settings"]
        assert isinstance(settings, list)
        assert len(settings) == 4, "Expected 4 settings (GitHub PAT, Jira URL, Jira Email, Jira API Token)"

        # Check each setting has required fields
        required_setting_fields = ["name", "description", "envVar", "sensitive"]
        for setting in settings:
            for field in required_setting_fields:
                assert field in setting, f"Setting missing required field: {field}"

    def test_github_token_setting(self, extension_config):
        """Verify GitHub Personal Access Token setting is correct."""
        settings = extension_config["settings"]
        github_token = next((s for s in settings if s["name"] == "GitHub Personal Access Token"), None)
        assert github_token is not None
        assert github_token["envVar"] == "GITHUB_PERSONAL_ACCESS_TOKEN"
        assert github_token["sensitive"] == True
        assert "repo" in github_token["description"]

    def test_jira_settings(self, extension_config):
        """Verify Jira settings are correctly configured."""
        settings = extension_config["settings"]

        # Check Jira URL
        jira_url = next((s for s in settings if s["name"] == "Jira URL"), None)
        assert jira_url is not None
        assert jira_url["envVar"] == "JIRA_URL"
        assert jira_url["sensitive"] == False

        # Check Jira Email
        jira_email = next((s for s in settings if s["name"] == "Jira Email"), None)
        assert jira_email is not None
        assert jira_email["envVar"] == "JIRA_EMAIL"
        assert jira_email["sensitive"] == False

        # Check Jira API Token
        jira_token = next((s for s in settings if s["name"] == "Jira API Token"), None)
        assert jira_token is not None
        assert jira_token["envVar"] == "JIRA_API_TOKEN"
        assert jira_token["sensitive"] == True

    def test_no_extra_top_level_fields(self, extension_config):
        """Verify there are no unexpected top-level fields."""
        expected_fields = {"name", "version", "description", "contextFileName", "mcpServers", "prompts", "settings"}
        actual_fields = set(extension_config.keys())
        assert actual_fields == expected_fields, f"Unexpected fields: {actual_fields - expected_fields}"

    def test_description_is_meaningful(self, extension_config):
        """Verify the description is meaningful and descriptive."""
        description = extension_config["description"]
        assert len(description) > 20, "Description should be meaningful"
        assert "Jira" in description
        assert "pull request" in description or "fix" in description

    def test_env_var_consistency(self, extension_config):
        """Verify environment variables in settings match MCP server references."""
        # Get all env vars from settings
        settings_env_vars = {s["envVar"] for s in extension_config["settings"]}

        # Check that MCP servers reference valid env vars
        atlassian_env = extension_config["mcpServers"]["atlassian"].get("env", {})
        for value in atlassian_env.values():
            if value.startswith("$"):
                env_var = value[1:]
                assert env_var in settings_env_vars or env_var == "JIRA_USERNAME", \
                    f"Environment variable {env_var} referenced but not in settings"