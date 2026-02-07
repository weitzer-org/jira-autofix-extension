"""
Tests for TOML command files (jira-autofix.toml, setrepo.toml, clearrepo.toml).
"""
import os
import pytest
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python versions


class TestJiraAutofixCommand:
    """Test suite for commands/jira-autofix.toml."""

    @pytest.fixture
    def command_path(self):
        """Path to the jira-autofix command file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands", "jira-autofix.toml")

    @pytest.fixture
    def command_config(self, command_path):
        """Load the command configuration."""
        with open(command_path, 'rb') as f:
            return tomllib.load(f)

    def test_toml_is_valid(self, command_path):
        """Verify the TOML file is valid and parseable."""
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)
        assert isinstance(config, dict)

    def test_required_fields_exist(self, command_config):
        """Verify required fields are present."""
        assert "description" in command_config
        assert "prompt" in command_config

    def test_description_is_meaningful(self, command_config):
        """Verify description is meaningful."""
        description = command_config["description"]
        assert len(description) > 20
        assert "Jira" in description
        assert any(word in description.lower() for word in ["fix", "resolve", "implement"])

    def test_prompt_contains_persona(self, command_config):
        """Verify prompt includes PERSONA section."""
        prompt = command_config["prompt"]
        assert "<PERSONA>" in prompt
        assert "</PERSONA>" in prompt
        assert "Senior Software Engineer" in prompt or "engineer" in prompt.lower()

    def test_prompt_contains_instructions(self, command_config):
        """Verify prompt includes INSTRUCTIONS section."""
        prompt = command_config["prompt"]
        assert "<INSTRUCTIONS>" in prompt
        assert "</INSTRUCTIONS>" in prompt

    def test_prompt_contains_all_phases(self, command_config):
        """Verify prompt includes all execution phases."""
        prompt = command_config["prompt"]
        phases = [
            "Phase 1: Gather Jira Context",
            "Phase 2: Set Up the Repository",
            "Phase 3: Plan the Fix",
            "Phase 4: Implement the Fix",
            "Phase 5: Security & Code Review",
            "Phase 6: Create Pull Request",
            "Phase 7: Update Jira Ticket"
        ]
        for phase in phases:
            assert phase in prompt, f"Missing phase: {phase}"

    def test_prompt_mentions_mcp_tools(self, command_config):
        """Verify prompt references MCP tools."""
        prompt = command_config["prompt"]
        # Check for Atlassian MCP tools
        assert "jira_get_issue" in prompt
        assert "jira_add_comment" in prompt

        # Check for GitHub MCP tools
        assert "create_pull_request" in prompt or "GitHub MCP" in prompt

    def test_prompt_includes_debug_mode(self, command_config):
        """Verify prompt includes debug mode instructions."""
        prompt = command_config["prompt"]
        assert "--debug" in prompt
        assert "Debug Mode" in prompt or "DEBUG" in prompt

    def test_prompt_includes_security_review(self, command_config):
        """Verify prompt includes security review instructions."""
        prompt = command_config["prompt"]
        assert "security" in prompt.lower()
        assert any(vuln in prompt.lower() for vuln in ["injection", "xss", "sql injection", "vulnerabilities"])

    def test_prompt_includes_constraints(self, command_config):
        """Verify prompt includes CONSTRAINTS section."""
        prompt = command_config["prompt"]
        assert "<CONSTRAINTS>" in prompt
        assert "</CONSTRAINTS>" in prompt
        assert "Never" in prompt or "never" in prompt

    def test_prompt_forbids_main_branch_push(self, command_config):
        """Verify prompt forbids pushing directly to main/master."""
        prompt = command_config["prompt"]
        assert "main" in prompt.lower() or "master" in prompt.lower()
        assert "Never" in prompt and ("push to" in prompt.lower() or "feature branch" in prompt.lower())

    def test_prompt_requires_plan_approval(self, command_config):
        """Verify prompt requires developer approval before implementation."""
        prompt = command_config["prompt"]
        assert "approve" in prompt.lower()
        assert "Wait for the developer" in prompt or "wait for" in prompt.lower()

    def test_prompt_includes_git_operations(self, command_config):
        """Verify prompt includes git operation instructions."""
        prompt = command_config["prompt"]
        git_ops = ["git clone", "git checkout", "git push"]
        for op in git_ops:
            assert op in prompt, f"Missing git operation: {op}"
        # "Commit with a message" is used instead of "git commit"
        assert "Commit" in prompt and "message" in prompt

    def test_prompt_handles_repo_detection(self, command_config):
        """Verify prompt includes repository detection logic."""
        prompt = command_config["prompt"]
        assert "~/.jira-autofix-repo" in prompt
        assert "git remote" in prompt
        assert "Priority 1" in prompt or "priority" in prompt.lower()

    def test_prompt_includes_test_execution(self, command_config):
        """Verify prompt includes test execution instructions."""
        prompt = command_config["prompt"]
        assert "test" in prompt.lower()
        assert "pytest" in prompt or "package.json" in prompt or "test runner" in prompt.lower()

    def test_prompt_includes_jira_comment(self, command_config):
        """Verify prompt includes Jira comment posting."""
        prompt = command_config["prompt"]
        assert "jira_add_comment" in prompt
        assert "comment" in prompt.lower()

    def test_prompt_includes_meta_instructions(self, command_config):
        """Verify prompt includes META_INSTRUCTIONS section."""
        prompt = command_config["prompt"]
        assert "<META_INSTRUCTIONS>" in prompt
        assert "</META_INSTRUCTIONS>" in prompt
        assert "Do NOT attempt to call" in prompt or "execute the logic" in prompt

    def test_prompt_warns_against_invented_tools(self, command_config):
        """Verify prompt warns against inventing non-existent tools."""
        prompt = command_config["prompt"]
        assert "Do NOT invent tools" in prompt or "CRITICAL: Do NOT invent" in prompt


class TestSetrepoCommand:
    """Test suite for commands/setrepo.toml."""

    @pytest.fixture
    def command_path(self):
        """Path to the setrepo command file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands", "setrepo.toml")

    @pytest.fixture
    def command_config(self, command_path):
        """Load the command configuration."""
        with open(command_path, 'rb') as f:
            return tomllib.load(f)

    def test_toml_is_valid(self, command_path):
        """Verify the TOML file is valid and parseable."""
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)
        assert isinstance(config, dict)

    def test_required_fields_exist(self, command_config):
        """Verify required fields are present."""
        assert "description" in command_config
        assert "prompt" in command_config

    def test_description_mentions_setrepo(self, command_config):
        """Verify description mentions setting repository."""
        description = command_config["description"]
        assert "repository" in description.lower()
        assert "default" in description.lower() or "set" in description.lower()

    def test_prompt_contains_persona(self, command_config):
        """Verify prompt includes PERSONA section."""
        prompt = command_config["prompt"]
        assert "<PERSONA>" in prompt
        assert "</PERSONA>" in prompt

    def test_prompt_contains_instructions(self, command_config):
        """Verify prompt includes INSTRUCTIONS section."""
        prompt = command_config["prompt"]
        assert "<INSTRUCTIONS>" in prompt
        assert "</INSTRUCTIONS>" in prompt

    def test_prompt_handles_config_file(self, command_config):
        """Verify prompt mentions the config file location."""
        prompt = command_config["prompt"]
        assert "~/.jira-autofix-repo" in prompt

    def test_prompt_handles_github_urls(self, command_config):
        """Verify prompt handles various GitHub URL formats."""
        prompt = command_config["prompt"]
        assert "github.com" in prompt.lower()
        assert "owner/repo" in prompt

    def test_prompt_provides_usage_examples(self, command_config):
        """Verify prompt includes usage examples or format info."""
        prompt = command_config["prompt"]
        formats = [
            "https://github.com/owner/repo",
            "owner/repo",
            "git@github.com"
        ]
        # At least one format should be mentioned
        assert any(fmt in prompt for fmt in formats)

    def test_prompt_confirms_action(self, command_config):
        """Verify prompt includes confirmation message."""
        prompt = command_config["prompt"]
        assert "Confirm to the user" in prompt or "Print:" in prompt
        assert "✅" in prompt or "set to" in prompt.lower()

    def test_prompt_handles_no_argument(self, command_config):
        """Verify prompt handles case when no argument is provided."""
        prompt = command_config["prompt"]
        assert "If no argument" in prompt or "no argument is provided" in prompt.lower()


class TestClearrepoCommand:
    """Test suite for commands/clearrepo.toml."""

    @pytest.fixture
    def command_path(self):
        """Path to the clearrepo command file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands", "clearrepo.toml")

    @pytest.fixture
    def command_config(self, command_path):
        """Load the command configuration."""
        with open(command_path, 'rb') as f:
            return tomllib.load(f)

    def test_toml_is_valid(self, command_path):
        """Verify the TOML file is valid and parseable."""
        with open(command_path, 'rb') as f:
            config = tomllib.load(f)
        assert isinstance(config, dict)

    def test_required_fields_exist(self, command_config):
        """Verify required fields are present."""
        assert "description" in command_config
        assert "prompt" in command_config

    def test_description_mentions_clear(self, command_config):
        """Verify description mentions clearing repository."""
        description = command_config["description"]
        assert "clear" in description.lower() or "remove" in description.lower()
        assert "repository" in description.lower()

    def test_prompt_contains_persona(self, command_config):
        """Verify prompt includes PERSONA section."""
        prompt = command_config["prompt"]
        assert "<PERSONA>" in prompt
        assert "</PERSONA>" in prompt

    def test_prompt_contains_instructions(self, command_config):
        """Verify prompt includes INSTRUCTIONS section."""
        prompt = command_config["prompt"]
        assert "<INSTRUCTIONS>" in prompt
        assert "</INSTRUCTIONS>" in prompt

    def test_prompt_deletes_config_file(self, command_config):
        """Verify prompt includes instruction to delete config file."""
        prompt = command_config["prompt"]
        assert "~/.jira-autofix-repo" in prompt
        assert "rm" in prompt or "Delete" in prompt

    def test_prompt_confirms_action(self, command_config):
        """Verify prompt includes confirmation message."""
        prompt = command_config["prompt"]
        assert "Confirm to the user" in prompt or "Print:" in prompt
        assert "✅" in prompt or "cleared" in prompt.lower()

    def test_prompt_explains_next_behavior(self, command_config):
        """Verify prompt explains what happens after clearing."""
        prompt = command_config["prompt"]
        assert "auto-detect" in prompt.lower() or "current directory" in prompt.lower()


class TestCommandsIntegration:
    """Integration tests across all command files."""

    def test_all_commands_use_consistent_structure(self):
        """Verify all command files follow consistent structure."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")
        command_files = ["jira-autofix.toml", "setrepo.toml", "clearrepo.toml"]

        for filename in command_files:
            filepath = os.path.join(commands_dir, filename)
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)

            # All should have description and prompt
            assert "description" in config, f"{filename} missing description"
            assert "prompt" in config, f"{filename} missing prompt"

            # All should have PERSONA and INSTRUCTIONS
            prompt = config["prompt"]
            assert "<PERSONA>" in prompt, f"{filename} missing PERSONA"
            assert "<INSTRUCTIONS>" in prompt, f"{filename} missing INSTRUCTIONS"

    def test_config_file_path_consistency(self):
        """Verify all commands use the same config file path."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")
        config_path = "~/.jira-autofix-repo"

        for filename in ["jira-autofix.toml", "setrepo.toml", "clearrepo.toml"]:
            filepath = os.path.join(commands_dir, filename)
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)

            if filename != "jira-autofix.toml":  # clearrepo and setrepo definitely reference it
                assert config_path in config["prompt"], \
                    f"{filename} does not reference {config_path}"

    def test_all_toml_files_parseable(self):
        """Verify all TOML files in commands directory are parseable."""
        commands_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands")

        for filename in os.listdir(commands_dir):
            if filename.endswith(".toml"):
                filepath = os.path.join(commands_dir, filename)
                with open(filepath, 'rb') as f:
                    config = tomllib.load(f)
                assert isinstance(config, dict), f"{filename} did not parse to a dictionary"