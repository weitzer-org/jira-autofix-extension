
import pytest
import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5000"
ISSUE_KEY = "SCRUM-1"
REPO_URL = "https://github.com/benw307/logo-maker-weitzer"

def test_jira_autofix_workflow(page: Page):
    # Capture console logs
    page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"BROWSER ERROR: {exc}"))

    # 1. Open the app
    print(f"\n🚀 Navigating to {BASE_URL}")
    page.goto(BASE_URL)
    expect(page).to_have_title("Jira Autofix Agent")

    # 2. Start Workflow (Setup View)
    print("📝 Entering issue details...")
    page.fill("#issue-key", ISSUE_KEY)
    page.fill("#repo-url", REPO_URL)
    page.click("#start-btn")

    # 3. Wait for Workflow View (Sidebar & Content)
    print("⏳ Waiting for workflow view...")
    # Increase timeout to 30s as backend clone might take time
    expect(page.locator("#phase-content-view")).to_be_visible(timeout=30000)
    expect(page.locator(".sidebar")).to_be_visible()
    
    # Function to run a phase
    def run_phase(phase_num, phase_name, requires_approval=False):
        print(f"\n🔄 Running Phase {phase_num}: {phase_name}")
        
        # Verify Sidebar Activation (Optimistic check)
        # The frontend updates sidebar based on currentPhase state
        # Click Run
        run_btn = page.locator("#run-btn")
        expect(run_btn).to_be_visible()
        expect(run_btn).to_be_enabled()
        run_btn.click()
        
        # Wait for completion or approval
        if requires_approval:
            print("   ⏳ Waiting for approval modal...")
            modal = page.locator("#approval-modal")
            expect(modal).to_have_class(re.compile(r"active"), timeout=60000)
            
            print("   ✅ Approving phase...")
            # Click "Approve & Proceed"
            page.click("text=Approve & Proceed")
            expect(modal).not_to_have_class(re.compile(r"active"))
            
            # After approval, wait for the run button to finish 'Running...'
            print("   ⏳ Waiting for post-approval completion...")
            expect(run_btn).not_to_contain_text("Running", timeout=120000)
        else:
            print("   ⏳ Waiting for completion...")
            # Wait for button to be enabled again OR for final completion
            expect(run_btn).not_to_contain_text("Running", timeout=120000)

    # Phase 1: Gather Context
    run_phase(1, "Gather Jira Context")
    
    # Phase 2: Set Up Repository
    run_phase(2, "Set Up Repository")
    
    # Phase 3: Plan the Fix (Requires Approval)
    run_phase(3, "Plan the Fix", requires_approval=True)
    
    # Phase 4: Implement the Fix
    run_phase(4, "Implement the Fix")
    
    # Phase 5: Security Review (Requires Approval)
    run_phase(5, "Security & Code Review", requires_approval=True)
    
    # Phase 6: Create PR
    run_phase(6, "Create Pull Request")
    
    # Phase 7: Update Jira
    run_phase(7, "Update Jira Ticket")
    
    # 4. Verify Final Success
    print("\n🎉 Verifying final success state...")
    # New UI check: Run button says "Workflow Complete"
    expect(page.locator("#run-btn")).to_contain_text("Workflow Complete")
    
    print("✅ UI Test Passed!")
