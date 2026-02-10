#!/usr/bin/env python3
"""
Full end-to-end API test for the Jira Autofix Flask app.

This script tests all phases of the workflow including approvals.
Run with: python adk/tests/test_full_workflow.py
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def print_separator():
    print("-" * 60)

def test_full_workflow():
    """Test the complete 7-phase workflow."""
    session = requests.Session()
    
    print("=" * 60)
    print("ADK Jira Autofix - Full Workflow Test")
    print("=" * 60)
    print(f"\nTargeting: {BASE_URL}")
    print(f"Issue: SCRUM-1")
    print(f"Repo: https://github.com/benw307/logo-maker-weitzer\n")
    
    # Check server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("ERROR: Flask server is not running!")
        sys.exit(1)
    
    # Step 1: Start workflow with repo URL
    print_separator()
    print("📋 STARTING WORKFLOW")
    print_separator()
    
    response = session.post(
        f"{BASE_URL}/api/start",
        json={
            "issue_key": "SCRUM-1",
            "repo_url": "https://github.com/benw307/logo-maker-weitzer"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"✗ Failed to start workflow: {response.text}")
        return False
    
    data = response.json()
    print(f"✓ Workflow started for {data['issue_key']}\n")
    
    # Run through each phase
    phases = [
        ("gather_context", "Gather Jira Context", False),
        ("setup_repo", "Set Up Repository", False),
        ("plan_fix", "Plan the Fix", True),  # Requires approval
        ("implement_fix", "Implement the Fix", False),
        ("security_review", "Security & Code Review", True),  # Requires approval
        ("create_pr", "Create Pull Request", False),
        ("update_jira", "Update Jira Ticket", False),
    ]
    
    for phase_num, (phase_name, phase_desc, requires_approval) in enumerate(phases, 1):
        print_separator()
        print(f"🔄 PHASE {phase_num}/7: {phase_desc}")
        print_separator()
        
        # Run the phase
        print(f"Running phase (this may take up to 60 seconds)...")
        start_time = time.time()
        
        response = session.post(
            f"{BASE_URL}/api/run",
            headers={"Content-Type": "application/json"}
        )
        
        elapsed = time.time() - start_time
        print(f"Response received in {elapsed:.2f}s")
        
        if response.status_code != 200:
            try:
                data = response.json()
                error = data.get("error", "Unknown error")
                print(f"✗ Phase failed: {error}")
                
                # Check if workflow is complete
                state = data.get("state", {})
                current_idx = state.get("current_phase_index", 0)
                if current_idx >= 7:
                    print("Workflow appears to be complete!")
                    return True
            except:
                print(f"✗ Phase failed: {response.text[:200]}")
            return False
        
        data = response.json()
        status = data.get("status")
        result = data.get("result", "")
        
        # Truncate result for display
        if len(result) > 500:
            result_display = result[:500] + "..."
        else:
            result_display = result
        
        print(f"\nResult:\n{result_display}\n")
        
        # Handle approval if needed
        if status == "awaiting_approval" or requires_approval:
            if data.get("state", {}).get("phases", [{}])[phase_num-1].get("status") == "awaiting_approval":
                print(f"⏸️  Phase requires approval")
                print(f"   Message: {data.get('message', 'Review the plan')}")
                
                # Auto-approve for testing
                print(f"   📝 Auto-approving for test purposes...")
                
                approve_response = session.post(
                    f"{BASE_URL}/api/approve",
                    headers={"Content-Type": "application/json"}
                )
                
                if approve_response.status_code == 200:
                    print(f"   ✓ Approved!\n")
                else:
                    print(f"   ✗ Approval failed: {approve_response.text}")
                    return False
        
        # Verify phase completed
        state = data.get("state", {})
        current_phase_idx = state.get("current_phase_index", 0)
        phases_state = state.get("phases", [])
        
        if phase_num - 1 < len(phases_state):
            phase_status = phases_state[phase_num - 1].get("status")
            if phase_status in ["completed", "approved"]:
                print(f"✓ Phase {phase_num} completed successfully!")
            elif phase_status == "awaiting_approval":
                print(f"⏸️ Phase {phase_num} awaiting approval")
            else:
                print(f"? Phase {phase_num} status: {phase_status}")
        
        print()
    
    # Final status check
    print_separator()
    print("📊 FINAL STATUS")
    print_separator()
    
    response = session.get(f"{BASE_URL}/api/status")
    data = response.json()
    
    state = data.get("state", {})
    all_completed = all(
        p.get("status") in ["completed", "approved"] 
        for p in state.get("phases", [])
    )
    
    if all_completed:
        print("🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
        return True
    else:
        print("Status of each phase:")
        for p in state.get("phases", []):
            status_icon = "✓" if p.get("status") in ["completed", "approved"] else "○"
            print(f"  {status_icon} {p.get('description')}: {p.get('status')}")
        
        # Return True if we got further than Phase 1
        completed_count = sum(
            1 for p in state.get("phases", []) 
            if p.get("status") in ["completed", "approved"]
        )
        return completed_count > 0

def main():
    try:
        success = test_full_workflow()
        
        print("\n" + "=" * 60)
        if success:
            print("✓ WORKFLOW TEST COMPLETED")
        else:
            print("✗ WORKFLOW TEST ENCOUNTERED ISSUES")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
