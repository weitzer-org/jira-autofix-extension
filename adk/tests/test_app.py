"""
Unit tests for the Jira Autofix ADK agent.

Run with: pytest adk/tests/ -v
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.phases import WorkflowState, PhaseStatus, Phase


class TestWorkflowState:
    """Tests for WorkflowState class."""
    
    def test_initial_state(self):
        """Test that initial state is properly configured."""
        state = WorkflowState()
        assert state.current_phase_index == 0
        assert len(state.phases) == 7
        assert state.issue_key is None
        assert state.repo_url is None
    
    def test_current_phase(self):
        """Test getting current phase."""
        state = WorkflowState()
        assert state.current_phase is not None
        assert state.current_phase.name == "gather_context"
    
    def test_advance_phase(self):
        """Test advancing to next phase."""
        state = WorkflowState()
        assert state.current_phase.name == "gather_context"
        
        result = state.advance_phase()
        assert result is True
        assert state.current_phase.name == "setup_repo"
        
        # Advance through all phases
        for _ in range(5):
            state.advance_phase()
        
        # Should be at last phase now
        assert state.current_phase.name == "update_jira"
        
        # Should return False when at end
        result = state.advance_phase()
        assert result is False
    
    def test_set_phase_status(self):
        """Test setting phase status."""
        state = WorkflowState()
        state.set_phase_status(PhaseStatus.IN_PROGRESS)
        assert state.current_phase.status == PhaseStatus.IN_PROGRESS
        
        state.set_phase_status(PhaseStatus.COMPLETED, {"result": "test"})
        assert state.current_phase.status == PhaseStatus.COMPLETED
        assert state.current_phase.result == {"result": "test"}
    
    def test_is_awaiting_approval(self):
        """Test awaiting approval check."""
        state = WorkflowState()
        assert state.is_awaiting_approval() is False
        
        state.set_phase_status(PhaseStatus.AWAITING_APPROVAL)
        assert state.is_awaiting_approval() is True
    
    def test_approve_current_phase(self):
        """Test approving a phase."""
        state = WorkflowState()
        state.set_phase_status(PhaseStatus.AWAITING_APPROVAL)
        state.approve_current_phase()
        assert state.current_phase.status == PhaseStatus.APPROVED
    
    def test_reject_current_phase(self):
        """Test rejecting a phase."""
        state = WorkflowState()
        state.reject_current_phase("Bad code")
        assert state.current_phase.status == PhaseStatus.REJECTED
        assert state.current_phase.result == {"rejection_reason": "Bad code"}
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        state = WorkflowState()
        state.issue_key = "TEST-123"
        state.repo_url = "https://github.com/test/repo"
        state.set_phase_status(PhaseStatus.COMPLETED)
        state.advance_phase()
        
        # Serialize
        data = state.to_dict()
        assert data["issue_key"] == "TEST-123"
        assert data["repo_url"] == "https://github.com/test/repo"
        assert data["current_phase_index"] == 1
        assert data["phases"][0]["status"] == "completed"
        
        # Deserialize
        new_state = WorkflowState.from_dict(data)
        assert new_state.issue_key == "TEST-123"
        assert new_state.repo_url == "https://github.com/test/repo"
        assert new_state.current_phase_index == 1
        assert new_state.phases[0].status == PhaseStatus.COMPLETED


class TestPhaseStatus:
    """Tests for PhaseStatus enum."""
    
    def test_all_statuses(self):
        """Test that all expected statuses exist."""
        expected = ["PENDING", "IN_PROGRESS", "AWAITING_APPROVAL", 
                    "APPROVED", "REJECTED", "COMPLETED", "FAILED"]
        for status in expected:
            assert hasattr(PhaseStatus, status)
    
    def test_status_values(self):
        """Test status string values."""
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.COMPLETED.value == "completed"


class TestFlaskApp:
    """Tests for Flask application endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from ui.app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_client() as client:
            yield client
    
    def test_index_page(self, client):
        """Test that index page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Jira Autofix Agent' in response.data
    
    def test_start_workflow_missing_issue(self, client):
        """Test starting workflow without issue key."""
        response = client.post('/api/start', 
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
        assert b'Issue key is required' in response.data
    
    def test_start_workflow_success(self, client):
        """Test starting workflow with valid data."""
        response = client.post('/api/start',
                               json={'issue_key': 'TEST-1'},
                               content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'started'
        assert data['issue_key'] == 'TEST-1'
        assert 'state' in data
    
    def test_run_phase_no_workflow(self, client):
        """Test running phase without active workflow."""
        response = client.post('/api/run',
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_get_status_no_workflow(self, client):
        """Test getting status without active workflow."""
        response = client.get('/api/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'no_workflow'


class TestJiraTools:
    """Tests for Jira tools (mocked)."""
    
    @patch.dict(os.environ, {
        'JIRA_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_API_TOKEN': 'test-token'
    })
    @patch('tools.jira_tools.Jira')
    def test_get_jira_issue(self, mock_jira_class):
        """Test fetching a Jira issue."""
        from tools.jira_tools import get_jira_issue
        
        mock_jira = Mock()
        mock_jira.issue.return_value = {
            'key': 'TEST-1',
            'fields': {
                'summary': 'Test Issue',
                'description': 'Test description',
                'status': {'name': 'Open'},
                'priority': {'name': 'High'},
                'assignee': {'displayName': 'Test User'},
                'labels': ['bug'],
                'components': [{'name': 'Backend'}],
                'issuetype': {'name': 'Bug'},
            }
        }
        mock_jira_class.return_value = mock_jira
        
        result = get_jira_issue('TEST-1')
        
        assert result['key'] == 'TEST-1'
        assert result['summary'] == 'Test Issue'
        assert result['status'] == 'Open'
        assert result['priority'] == 'High'
    
    @patch.dict(os.environ, {
        'JIRA_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_API_TOKEN': 'test-token'
    })
    @patch('tools.jira_tools.Jira')
    def test_search_jira(self, mock_jira_class):
        """Test searching Jira issues."""
        from tools.jira_tools import search_jira
        
        mock_jira = Mock()
        mock_jira.jql.return_value = {
            'issues': [
                {
                    'key': 'TEST-1',
                    'fields': {
                        'summary': 'Issue 1',
                        'status': {'name': 'Open'},
                        'issuetype': {'name': 'Bug'},
                    }
                }
            ]
        }
        mock_jira_class.return_value = mock_jira
        
        result = search_jira('project = TEST')
        
        assert len(result) == 1
        assert result[0]['key'] == 'TEST-1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
