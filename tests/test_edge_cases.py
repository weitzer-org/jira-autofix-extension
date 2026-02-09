"""
Edge case and regression tests for the jira-autofix extension.
These tests strengthen confidence by covering boundary conditions and potential failure modes.
"""
import json
import os
import pytest
try:
    import tomllib
except ImportError:
    import tomli as tomllib


class TestJSONEdgeCases:
    """Edge case tests for JSON configuration."""

    @pytest.fixture
    def extension_config_path(self):
        """Path to the extension configuration file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")

    def test_json_no_trailing_commas(self, extension_config_path):
        """Verify JSON doesn't have trailing commas (which would be invalid)."""
        with open(extension_config_path, 'r') as f:
            content = f.read()
        # JSON with trailing commas will fail to parse
        config = json.loads(content)
        assert config is not None

    def test_all_strings_properly_escaped(self, extension_config_path):
        """Verify all strings in JSON are properly escaped."""
        with open(extension_config_path, 'r') as f:
            config = json.load(f)

        def check_strings(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    check_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_strings(item)
            elif isinstance(obj, str):
                # If we got here, the string was properly parsed
                assert isinstance(obj, str)

        check_strings(config)

    def test_env_var_names_no_typos(self, extension_config_path):
        """Verify environment variable names are consistent and without typos."""
        with open(extension_config_path, 'r') as f:
            config = json.load(f)

        env_vars = set()
        for setting in config["settings"]:
            env_var = setting["envVar"]
            # Check for common typos - these should NOT be present
            assert "TOEKN" not in env_var, f"Typo 'TOEKN' found in {env_var}"
            assert "GITHBU" not in env_var, f"Typo 'GITHBU' found in {env_var}"
            assert "JRIA" not in env_var, f"Typo 'JRIA' found in {env_var}"

            # Check for duplicate env vars
            assert env_var not in env_vars, f"Duplicate env var: {env_var}"
            env_vars.add(env_var)

    def test_mcp_server_commands_are_valid(self, extension_config_path):
        """Verify MCP server commands use valid docker syntax."""
        with open(extension_config_path, 'r') as f:
            config = json.load(f)

        for server_name, server_config in config["mcpServers"].items():
            assert server_config["command"] == "docker", \
                f"Server {server_name} should use docker command"
            assert isinstance(server_config["args"], list), \
                f"Server {server_name} args should be a list"
            # Check that "run" is the first arg
            assert server_config["args"][0] == "run", \
                f"Server {server_name} should start with 'run' arg"


class TestTOMLEdgeCases:
    """Edge case tests for TOML command files."""

    def test_toml_multiline_strings_valid(self):
        """Verify TOML multiline strings are properly formatted."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")

        for filename in ["jira-autofix.toml", "setrepo.toml", "clearrepo.toml"]:
            filepath = os.path.join(commands_dir, filename)
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)
            # If parsing succeeded, multiline strings are valid
            assert "prompt" in config

    def test_prompts_no_unescaped_quotes(self):
        """Verify prompts don't have unescaped quotes that could break parsing."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")

        for filename in ["jira-autofix.toml", "setrepo.toml", "clearrepo.toml"]:
            filepath = os.path.join(commands_dir, filename)
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)

            prompt = config["prompt"]
            # If we got here, the prompt was parsed successfully
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_prompts_have_balanced_xml_tags(self):
        """Verify XML-like tags in prompts are balanced."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")

        for filename in ["jira-autofix.toml", "setrepo.toml", "clearrepo.toml"]:
            filepath = os.path.join(commands_dir, filename)
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)

            prompt = config["prompt"]

            # Check common tag pairs
            tag_pairs = [
                ("<PERSONA>", "</PERSONA>"),
                ("<INSTRUCTIONS>", "</INSTRUCTIONS>"),
                ("<CONSTRAINTS>", "</CONSTRAINTS>"),
            ]

            for open_tag, close_tag in tag_pairs:
                if open_tag in prompt:
                    assert close_tag in prompt, \
                        f"{filename}: {open_tag} without matching {close_tag}"
                    # Check they appear in the right order
                    assert prompt.index(open_tag) < prompt.index(close_tag), \
                        f"{filename}: {close_tag} appears before {open_tag}"


class TestDocumentationEdgeCases:
    """Edge case tests for documentation files."""

    def test_no_broken_internal_references(self):
        """Verify internal section references exist."""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        with open(readme_path, 'r') as f:
            content = f.read()

        # Check that section headers exist for common reference patterns
        if "[Prerequisites]" in content:
            assert "## Prerequisites" in content or "### Prerequisites" in content

    def test_markdown_code_blocks_closed(self):
        """Verify all markdown code blocks are properly closed."""
        for doc_file in ["README.md", "GEMINI.md"]:
            doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), doc_file)
            with open(doc_path, 'r') as f:
                content = f.read()

            # Count opening and closing code blocks
            opening_count = content.count("```")
            # Should be even (each opening has a closing)
            assert opening_count % 2 == 0, \
                f"{doc_file} has unmatched code blocks (count: {opening_count})"

    def test_no_placeholder_text(self):
        """Verify documentation doesn't contain placeholder text."""
        for doc_file in ["README.md", "GEMINI.md"]:
            doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), doc_file)
            with open(doc_path, 'r') as f:
                content = f.read().lower()

            placeholders = ["todo:", "fixme:", "xxx", "placeholder", "[insert", "tbd"]
            for placeholder in placeholders:
                if placeholder in content:
                    # Allow "todo" in specific contexts like "TODO list" or section titled "TODO"
                    if placeholder == "todo:" and "## known limitations / todo" in content.lower():
                        continue
                    assert False, f"{doc_file} contains placeholder text: {placeholder}"


class TestRegressionTests:
    """Regression tests to prevent previously fixed issues."""

    def test_github_mcp_server_uses_correct_image(self):
        """Regression: Ensure GitHub MCP server uses official image."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")
        with open(config_path, 'r') as f:
            config = json.load(f)

        github_args = config["mcpServers"]["github"]["args"]
        github_image = [arg for arg in github_args if "github" in arg.lower() and "/" in arg][0]

        # Should use official GitHub image
        assert "ghcr.io/github/" in github_image, \
            "Should use official GitHub MCP server image"

    def test_atlassian_server_uses_working_image(self):
        """Regression: Ensure Atlassian server uses the working sooperset image."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")
        with open(config_path, 'r') as f:
            config = json.load(f)

        atlassian_args = config["mcpServers"]["atlassian"]["args"]
        atlassian_image = [arg for arg in atlassian_args if "mcp-atlassian" in arg][0]

        # Should use sooperset image (documented as working in Design Decisions)
        assert "sooperset/mcp-atlassian" in atlassian_image

    def test_jira_autofix_prevents_direct_push_to_main(self):
        """Regression: Ensure the prompt forbids pushing to main/master."""
        command_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "commands", "jira-autofix.toml")
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)

        prompt = config["prompt"]
        # Should have constraint about never pushing to main
        assert "Never" in prompt and "main" in prompt.lower()

    def test_debug_mode_documented(self):
        """Regression: Ensure debug mode is properly documented."""
        command_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "commands", "jira-autofix.toml")
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)

        prompt = config["prompt"]
        assert "--debug" in prompt
        assert "Debug Mode" in prompt or "DEBUG" in prompt


class TestSecurityChecks:
    """Security-related validation tests."""

    def test_no_hardcoded_secrets(self):
        """Verify no hardcoded secrets in configuration files."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")
        with open(config_path, 'r') as f:
            content = f.read()

        # Check for patterns that look like hardcoded secrets
        suspicious_patterns = [
            "ghp_",  # GitHub personal access token
            "github_pat_",  # GitHub PAT
            "sk-",  # OpenAI API key pattern
            "AKIA",  # AWS access key
        ]

        for pattern in suspicious_patterns:
            assert pattern not in content, \
                f"Found suspicious pattern that looks like a hardcoded secret: {pattern}"

    def test_env_vars_used_for_credentials(self):
        """Verify credentials are loaded from environment variables."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini-extension.json")
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check that credential settings use envVar
        for setting in config["settings"]:
            if any(word in setting["name"].lower() for word in ["token", "password", "secret", "key"]):
                assert "envVar" in setting, \
                    f"Credential setting '{setting['name']}' should use envVar"

    def test_git_operations_avoid_add_all(self):
        """Verify prompt advises against 'git add -A' to prevent sensitive file leaks."""
        command_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "commands", "jira-autofix.toml")
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)

        prompt = config["prompt"]
        # Should warn against using git add -A
        assert "git add -A" in prompt or "git add ." in prompt
        # And should have a warning context
        assert "Do NOT use" in prompt or "avoid" in prompt.lower()