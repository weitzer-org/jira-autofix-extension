"""
Workflow phases for the Jira Autofix agent.

This module defines the 7-phase workflow with approval checkpoints.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class PhaseStatus(Enum):
    """Status of a workflow phase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Phase:
    """Represents a workflow phase."""
    name: str
    description: str
    requires_approval: bool = False
    status: PhaseStatus = PhaseStatus.PENDING
    result: Optional[dict[str, Any]] = None
    approval_message: Optional[str] = None


class WorkflowState:
    """
    Manages the state of the Jira Autofix workflow.
    
    This is a stateless implementation where state is passed through
    the UI/API layer. For stateful persistence, this would be backed
    by a database.
    """
    
    PHASES = [
        Phase(
            name="gather_context",
            description="Gather Jira Context",
            requires_approval=False,
        ),
        Phase(
            name="setup_repo",
            description="Set Up Repository",
            requires_approval=False,
        ),
        Phase(
            name="plan_fix",
            description="Plan the Fix",
            requires_approval=True,
            approval_message="Please review the proposed fix plan before implementation.",
        ),
        Phase(
            name="implement_fix",
            description="Implement the Fix",
            requires_approval=False,
        ),
        Phase(
            name="security_review",
            description="Security & Code Review",
            requires_approval=True,
            approval_message="Please review the security findings before creating a PR.",
        ),
        Phase(
            name="create_pr",
            description="Create Pull Request",
            requires_approval=False,
        ),
        Phase(
            name="update_jira",
            description="Update Jira Ticket",
            requires_approval=False,
        ),
    ]
    
    def __init__(self):
        """Initialize a new workflow state."""
        self.issue_key: Optional[str] = None
        self.repo_url: Optional[str] = None
        self.current_phase_index: int = 0
        self.phases: list[Phase] = [
            Phase(
                name=p.name,
                description=p.description,
                requires_approval=p.requires_approval,
                approval_message=p.approval_message,
            )
            for p in self.PHASES
        ]
    
    @property
    def current_phase(self) -> Optional[Phase]:
        """Get the current phase."""
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None
    
    def advance_phase(self) -> bool:
        """Move to the next phase. Returns False if at end."""
        if self.current_phase_index < len(self.phases) - 1:
            self.current_phase_index += 1
            return True
        return False
    
    def set_phase_status(self, status: PhaseStatus, result: dict = None):
        """Update the current phase status."""
        if self.current_phase:
            self.current_phase.status = status
            if result:
                self.current_phase.result = result
    
    def is_awaiting_approval(self) -> bool:
        """Check if currently waiting for human approval."""
        return (
            self.current_phase is not None
            and self.current_phase.status == PhaseStatus.AWAITING_APPROVAL
        )
    
    def approve_current_phase(self):
        """Approve the current phase (human-in-the-loop)."""
        if self.current_phase and self.is_awaiting_approval():
            self.current_phase.status = PhaseStatus.APPROVED
    
    def reject_current_phase(self, reason: str = None):
        """Reject the current phase."""
        if self.current_phase:
            self.current_phase.status = PhaseStatus.REJECTED
            if reason:
                self.current_phase.result = {"rejection_reason": reason}
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize state to dictionary (for API/UI)."""
        return {
            "issue_key": self.issue_key,
            "repo_url": self.repo_url,
            "current_phase_index": self.current_phase_index,
            "phases": [
                {
                    "name": p.name,
                    "description": p.description,
                    "status": p.status.value,
                    "requires_approval": p.requires_approval,
                    "result": p.result,
                }
                for p in self.phases
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowState":
        """Deserialize state from dictionary."""
        state = cls()
        state.issue_key = data.get("issue_key")
        state.repo_url = data.get("repo_url")
        state.current_phase_index = data.get("current_phase_index", 0)
        
        for i, phase_data in enumerate(data.get("phases", [])):
            if i < len(state.phases):
                state.phases[i].status = PhaseStatus(phase_data.get("status", "pending"))
                state.phases[i].result = phase_data.get("result")
        
        return state
