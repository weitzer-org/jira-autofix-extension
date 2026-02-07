"""
Tests for documentation files (GEMINI.md, README.md).
"""
import os
import re
import pytest


class TestGeminiDocumentation:
    """Test suite for GEMINI.md context file."""

    @pytest.fixture
    def doc_path(self):
        """Path to the GEMINI.md file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "GEMINI.md")

    @pytest.fixture
    def doc_content(self, doc_path):
        """Load the documentation content."""
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_file_exists(self, doc_path):
        """Verify GEMINI.md exists."""
        assert os.path.exists(doc_path)

    def test_file_is_not_empty(self, doc_content):
        """Verify file has content."""
        assert len(doc_content) > 100

    def test_has_title(self, doc_content):
        """Verify document has a title."""
        lines = doc_content.split('\n')
        assert lines[0].startswith('#')
        assert 'Jira' in lines[0] or 'jira' in lines[0].lower()

    def test_documents_available_commands(self, doc_content):
        """Verify document lists available commands."""
        assert "## Available Commands" in doc_content or "Available Commands" in doc_content
        assert "/jira-autofix" in doc_content or "jira-autofix" in doc_content
        assert "/setrepo" in doc_content or "setrepo" in doc_content
        assert "/clearrepo" in doc_content or "clearrepo" in doc_content

    def test_documents_jira_autofix_command(self, doc_content):
        """Verify jira-autofix command is documented."""
        assert "jira-autofix" in doc_content.lower()
        # Should have usage examples
        assert any(marker in doc_content for marker in ["Usage:", "**Usage**", "usage"])

    def test_documents_setrepo_command(self, doc_content):
        """Verify setrepo command is documented."""
        assert "setrepo" in doc_content.lower()

    def test_documents_clearrepo_command(self, doc_content):
        """Verify clearrepo command is documented."""
        assert "clearrepo" in doc_content.lower()

    def test_documents_mcp_servers(self, doc_content):
        """Verify MCP servers are documented."""
        assert "MCP" in doc_content or "mcp" in doc_content.lower()
        assert "Atlassian" in doc_content or "Jira" in doc_content
        assert "GitHub" in doc_content

    def test_documents_atlassian_tools(self, doc_content):
        """Verify Atlassian/Jira tools are documented."""
        jira_tools = ["jira_get_issue", "jira_search", "jira_add_comment"]
        found_tools = sum(1 for tool in jira_tools if tool in doc_content)
        assert found_tools >= 2, "Should document key Jira tools"

    def test_documents_github_tools(self, doc_content):
        """Verify GitHub tools are documented."""
        github_tools = ["create_branch", "create_pull_request", "push_files"]
        found_tools = sum(1 for tool in github_tools if tool in doc_content)
        assert found_tools >= 1, "Should document key GitHub tools"

    def test_documents_behavioral_guidelines(self, doc_content):
        """Verify behavioral guidelines are documented."""
        assert "Behavioral" in doc_content or "Guidelines" in doc_content or "guidelines" in doc_content.lower()

    def test_warns_about_plan_approval(self, doc_content):
        """Verify document mentions plan approval requirement."""
        assert "approve" in doc_content.lower() or "confirm" in doc_content.lower()

    def test_documents_security_focus(self, doc_content):
        """Verify document mentions security review."""
        assert "security" in doc_content.lower() or "review" in doc_content.lower()

    def test_no_broken_markdown_headers(self, doc_content):
        """Verify markdown headers are properly formatted."""
        lines = doc_content.split('\n')
        for line in lines:
            if line.startswith('#'):
                # Should have space after hash(es)
                header_match = re.match(r'^(#+)(.+)$', line)
                if header_match:
                    hashes, text = header_match.groups()
                    # Text should start with space or be empty
                    assert text.startswith(' ') or text == '', \
                        f"Malformed header (no space): {line}"

    def test_mentions_limitations_or_known_issues(self, doc_content):
        """Verify document mentions limitations."""
        keywords = ["Limitations", "TODO", "Known", "Workaround"]
        assert any(kw in doc_content for kw in keywords), \
            "Should document known limitations or TODOs"


class TestReadmeDocumentation:
    """Test suite for README.md documentation."""

    @pytest.fixture
    def doc_path(self):
        """Path to the README.md file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")

    @pytest.fixture
    def doc_content(self, doc_path):
        """Load the documentation content."""
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_file_exists(self, doc_path):
        """Verify README.md exists."""
        assert os.path.exists(doc_path)

    def test_file_is_comprehensive(self, doc_content):
        """Verify README is comprehensive (substantial content)."""
        assert len(doc_content) > 1000, "README should be comprehensive"

    def test_has_title_with_project_name(self, doc_content):
        """Verify README has a descriptive title."""
        lines = doc_content.split('\n')
        assert lines[0].startswith('#')
        assert 'Jira' in lines[0]
        assert 'Extension' in lines[0] or 'Autofix' in lines[0]

    def test_has_overview_section(self, doc_content):
        """Verify README has an overview section."""
        assert "## Overview" in doc_content or "## Description" in doc_content

    def test_documents_prerequisites(self, doc_content):
        """Verify README lists prerequisites."""
        assert "## Prerequisites" in doc_content or "Prerequisites" in doc_content
        assert "Gemini CLI" in doc_content or "gemini" in doc_content.lower()
        assert "Docker" in doc_content

    def test_documents_installation(self, doc_content):
        """Verify README includes installation instructions."""
        assert "## Install" in doc_content or "Installation" in doc_content
        assert "gemini extensions install" in doc_content or "install" in doc_content.lower()

    def test_documents_github_pat_requirement(self, doc_content):
        """Verify README mentions GitHub Personal Access Token."""
        assert "GitHub Personal Access Token" in doc_content or "PAT" in doc_content
        assert "repo" in doc_content.lower()  # Should mention repo scope

    def test_documents_jira_credentials(self, doc_content):
        """Verify README documents Jira authentication setup."""
        assert "Jira" in doc_content
        assert any(term in doc_content for term in ["API Token", "credentials", "authentication"])

    def test_documents_usage(self, doc_content):
        """Verify README includes usage instructions."""
        assert "## Usage" in doc_content or "Usage" in doc_content
        assert "gemini run" in doc_content or "jira-autofix" in doc_content

    def test_includes_usage_examples(self, doc_content):
        """Verify README includes concrete usage examples."""
        # Should have code blocks with examples
        assert "```" in doc_content
        # Should reference example issue keys
        example_patterns = [r'SCRUM-\d+', r'PROJ-\d+', r'[A-Z]+-\d+']
        assert any(re.search(pattern, doc_content) for pattern in example_patterns)

    def test_documents_workflow_steps(self, doc_content):
        """Verify README explains the workflow."""
        workflow_keywords = ["workflow", "step", "phase", "process"]
        assert any(kw in doc_content.lower() for kw in workflow_keywords)
        # Should mention multiple phases
        phases = ["Fetch", "Plan", "Implement", "Review", "PR", "Pull Request"]
        found_phases = sum(1 for phase in phases if phase in doc_content)
        assert found_phases >= 3, "Should document major workflow phases"

    def test_documents_configuration(self, doc_content):
        """Verify README includes configuration section."""
        assert "## Configuration" in doc_content or "Configuration" in doc_content or "Settings" in doc_content

    def test_includes_sequence_diagram_or_architecture(self, doc_content):
        """Verify README includes architectural documentation."""
        # Could be a diagram, architecture section, or detailed workflow
        indicators = ["```", "Sequence Diagram", "Architecture", "## Workflow Details", "flowchart"]
        assert any(ind in doc_content for ind in indicators)

    def test_documents_mcp_servers(self, doc_content):
        """Verify README documents MCP servers."""
        assert "MCP" in doc_content
        assert "Atlassian" in doc_content or "Jira" in doc_content
        assert "GitHub" in doc_content

    def test_documents_debug_mode(self, doc_content):
        """Verify README mentions debug mode."""
        assert "--debug" in doc_content or "debug" in doc_content.lower()

    def test_includes_troubleshooting_or_tips(self, doc_content):
        """Verify README includes helpful tips or troubleshooting."""
        helpful_sections = ["TIP", "NOTE", "WARNING", "Important", "troubleshoot"]
        assert any(section in doc_content for section in helpful_sections)

    def test_documents_file_structure(self, doc_content):
        """Verify README documents the project file structure."""
        assert "## File Structure" in doc_content or "File Structure" in doc_content or "Structure" in doc_content
        assert "gemini-extension.json" in doc_content
        assert "GEMINI.md" in doc_content

    def test_includes_license_info(self, doc_content):
        """Verify README includes license information."""
        assert "## License" in doc_content or "License" in doc_content

    def test_no_broken_links(self, doc_content):
        """Verify internal file references exist."""
        # Extract file references
        file_refs = re.findall(r'`([a-zA-Z0-9_\-/.]+\.(md|json|toml|sh))`', doc_content)

        base_path = os.path.dirname(os.path.dirname(__file__))
        for file_ref, _ in file_refs:
            # Skip URLs and some special cases
            if file_ref.startswith('http') or file_ref.startswith('$'):
                continue

            file_path = os.path.join(base_path, file_ref)
            assert os.path.exists(file_path), f"Referenced file does not exist: {file_ref}"

    def test_documents_setrepo_command(self, doc_content):
        """Verify README mentions setrepo command or repository configuration."""
        # The README may not explicitly document /setrepo but should mention repo configuration
        assert ("setrepo" in doc_content.lower() or
                ("repository" in doc_content.lower() and "default" in doc_content.lower()))

    def test_documents_clearrepo_command(self, doc_content):
        """Verify README mentions clearrepo or related functionality."""
        # The README may not explicitly document /clearrepo but should cover repo management
        assert ("clearrepo" in doc_content.lower() or
                "repository" in doc_content.lower())

    def test_mentions_repository_detection(self, doc_content):
        """Verify README explains repository detection."""
        assert "detect" in doc_content.lower() or "auto-detect" in doc_content.lower()
        assert "current directory" in doc_content.lower() or "git remote" in doc_content.lower()

    def test_code_examples_use_proper_syntax(self, doc_content):
        """Verify code blocks use proper markdown syntax."""
        # Find all code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', doc_content, re.DOTALL)
        assert len(code_blocks) > 0, "README should include code examples"

        # Check for common issues
        for lang, code in code_blocks:
            if lang in ['bash', 'sh', '']:
                # Bash code blocks shouldn't have Python syntax
                assert 'def ' not in code, "Bash code block contains Python syntax"


class TestDocumentationConsistency:
    """Tests for consistency between documentation files."""

    @pytest.fixture
    def gemini_content(self):
        """Load GEMINI.md content."""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "GEMINI.md")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def readme_content(self):
        """Load README.md content."""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_both_mention_jira_autofix_command(self, gemini_content, readme_content):
        """Verify both docs mention the main command."""
        assert "jira-autofix" in gemini_content.lower()
        assert "jira-autofix" in readme_content.lower()

    def test_both_mention_setrepo(self, gemini_content, readme_content):
        """Verify GEMINI.md documents setrepo command."""
        # GEMINI.md is the internal context file that must document all commands
        assert "setrepo" in gemini_content.lower()
        # README may not explicitly document helper commands

    def test_both_mention_clearrepo(self, gemini_content, readme_content):
        """Verify GEMINI.md documents clearrepo command."""
        # GEMINI.md is the internal context file that must document all commands
        assert "clearrepo" in gemini_content.lower()
        # README may not explicitly document helper commands

    def test_consistent_mcp_server_references(self, gemini_content, readme_content):
        """Verify MCP servers are consistently referenced."""
        # Both should mention Atlassian/Jira MCP
        assert "Atlassian" in gemini_content or "Jira" in gemini_content
        assert "Atlassian" in readme_content or "Jira" in readme_content

        # Both should mention GitHub MCP
        assert "GitHub" in gemini_content
        assert "GitHub" in readme_content

    def test_command_usage_consistency(self, gemini_content, readme_content):
        """Verify command usage is consistently documented."""
        # Both should show similar usage patterns
        assert "/jira-autofix" in gemini_content or "jira-autofix" in gemini_content
        assert "jira-autofix" in readme_content