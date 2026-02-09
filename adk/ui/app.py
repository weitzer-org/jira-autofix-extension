"""
Flask web UI for the Jira Autofix ADK agent.

Provides a simple interface for:
- Entering Jira issue key
- Viewing agent progress
- Approving/rejecting at checkpoints
- Viewing final PR link
"""
import os
import json
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from adk.agent import root_agent
from adk.workflow.phases import WorkflowState, PhaseStatus

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Session service for ADK
session_service = InMemorySessionService()


@app.route("/")
def index():
    """Main page with issue input form."""
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_workflow():
    """Start a new workflow for a Jira issue."""
    data = request.json
    issue_key = data.get("issue_key")
    repo_url = data.get("repo_url")
    
    if not issue_key:
        return jsonify({"error": "Issue key is required"}), 400
    
    # Initialize workflow state
    state = WorkflowState()
    state.issue_key = issue_key
    state.repo_url = repo_url
    
    # Store in session
    session["workflow_state"] = state.to_dict()
    
    return jsonify({
        "status": "started",
        "issue_key": issue_key,
        "state": state.to_dict(),
    })


@app.route("/api/run", methods=["POST"])
def run_phase():
    """Run the current phase of the workflow."""
    state_data = session.get("workflow_state")
    if not state_data:
        return jsonify({"error": "No active workflow"}), 400
    
    state = WorkflowState.from_dict(state_data)
    
    if state.is_awaiting_approval():
        return jsonify({
            "status": "awaiting_approval",
            "phase": state.current_phase.name,
            "message": state.current_phase.approval_message,
            "state": state.to_dict(),
        })
    
    # Create runner for ADK agent
    runner = Runner(
        agent=root_agent,
        app_name="jira_autofix_ui",
        session_service=session_service,
    )
    
    # Construct prompt based on current phase
    phase = state.current_phase
    if phase.name == "gather_context":
        prompt = f"Fetch the Jira issue details for {state.issue_key}"
    elif phase.name == "setup_repo":
        prompt = f"Clone and set up the repository: {state.repo_url or 'auto-detect from issue'}"
    elif phase.name == "plan_fix":
        prompt = "Analyze the codebase and create a fix plan"
    elif phase.name == "implement_fix":
        prompt = "Implement the approved fix plan"
    elif phase.name == "security_review":
        prompt = "Perform a security and code review of the changes"
    elif phase.name == "create_pr":
        prompt = "Create a pull request with the changes"
    elif phase.name == "update_jira":
        prompt = f"Add a comment to {state.issue_key} with the PR link"
    else:
        prompt = "Continue with the workflow"
    
    # Run the agent
    try:
        # Get or create session
        session_id = session.get("adk_session_id", f"session_{state.issue_key}")
        adk_session = session_service.get_or_create_session(
            app_name="jira_autofix_ui",
            user_id="web_user",
            session_id=session_id,
        )
        session["adk_session_id"] = adk_session.id
        
        # Execute agent
        response = runner.run(
            user_id="web_user",
            session_id=adk_session.id,
            new_message=prompt,
        )
        
        # Collect response
        result_text = ""
        for event in response:
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        result_text += part.text
        
        # Update phase status
        if phase.requires_approval:
            state.set_phase_status(PhaseStatus.AWAITING_APPROVAL, {"result": result_text})
        else:
            state.set_phase_status(PhaseStatus.COMPLETED, {"result": result_text})
            state.advance_phase()
        
        session["workflow_state"] = state.to_dict()
        
        return jsonify({
            "status": "success",
            "phase": phase.name,
            "result": result_text,
            "state": state.to_dict(),
        })
        
    except Exception as e:
        state.set_phase_status(PhaseStatus.FAILED, {"error": str(e)})
        session["workflow_state"] = state.to_dict()
        return jsonify({
            "status": "error",
            "error": str(e),
            "state": state.to_dict(),
        }), 500


@app.route("/api/approve", methods=["POST"])
def approve_phase():
    """Approve the current phase (human-in-the-loop)."""
    state_data = session.get("workflow_state")
    if not state_data:
        return jsonify({"error": "No active workflow"}), 400
    
    state = WorkflowState.from_dict(state_data)
    
    if not state.is_awaiting_approval():
        return jsonify({"error": "Not awaiting approval"}), 400
    
    state.approve_current_phase()
    state.advance_phase()
    session["workflow_state"] = state.to_dict()
    
    return jsonify({
        "status": "approved",
        "next_phase": state.current_phase.name if state.current_phase else None,
        "state": state.to_dict(),
    })


@app.route("/api/reject", methods=["POST"])
def reject_phase():
    """Reject the current phase."""
    data = request.json
    reason = data.get("reason", "Rejected by user")
    
    state_data = session.get("workflow_state")
    if not state_data:
        return jsonify({"error": "No active workflow"}), 400
    
    state = WorkflowState.from_dict(state_data)
    state.reject_current_phase(reason)
    session["workflow_state"] = state.to_dict()
    
    return jsonify({
        "status": "rejected",
        "reason": reason,
        "state": state.to_dict(),
    })


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current workflow status."""
    state_data = session.get("workflow_state")
    if not state_data:
        return jsonify({"status": "no_workflow"})
    
    state = WorkflowState.from_dict(state_data)
    return jsonify({
        "status": "active",
        "state": state.to_dict(),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
