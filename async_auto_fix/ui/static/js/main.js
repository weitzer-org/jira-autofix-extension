
let currentPhase = 0;
let isRunning = false;
let pollingInterval = null;

// DOM Elements
const phaseList = document.getElementById('phase-list');
const activePhaseTitle = document.getElementById('active-phase-title');
const workflowStatus = document.getElementById('workflow-status');
const setupView = document.getElementById('setup-view');
const phaseContentView = document.getElementById('phase-content-view');
const summaryView = document.getElementById('summary-view');
const approvalModal = document.getElementById('approval-modal');
const runBtn = document.getElementById('run-btn');

async function startWorkflow() {
    const issueKey = document.getElementById('issue-key').value;
    const repoUrl = document.getElementById('repo-url').value;

    if (!issueKey) return alert('Please enter a Jira Issue Key');

    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ issue_key: issueKey, repo_url: repoUrl })
        });

        const data = await response.json();
        console.log('Start response:', data); // DEBUG
        if (data.status === 'success' || data.status === 'started') {
            console.log('Switching views...'); // DEBUG
            // Hide setup, show workflow
            setupView.classList.add('hidden');
            phaseContentView.classList.remove('hidden');
            console.log('phaseContentView classes:', phaseContentView.classList); // DEBUG

            // Activate first phase
            updateSidebar(1);
            runBtn.disabled = false;
            runBtn.innerText = "Run Phase 1";
        } else {
            console.error('Start failed:', data); // DEBUG
        }
    } catch (error) {
        console.error('Error starting workflow:', error);
        alert('Failed to start workflow');
    }
}

async function runPhase() {
    if (isRunning) return;

    isRunning = true;
    runBtn.disabled = true;
    runBtn.innerText = "Running...";

    // Optimistic update of sidebar
    updateSidebar(currentPhase + 1);

    try {
        const response = await fetch('/api/run', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'awaiting_approval') {
            showApprovalModal(data.state.current_phase_index, data.message, data.state);
        } else if (data.status === 'success') {
            currentPhase++;
            updateUI(data.state);
            runBtn.innerText = `Run Phase ${currentPhase + 1}`;
            runBtn.disabled = false;

            if (currentPhase >= 7) {
                runBtn.innerText = "Workflow Complete";
                runBtn.disabled = true;
                workflowStatus.innerText = "Completed";
                workflowStatus.style.color = "var(--success-color)";
            }
        } else {
            alert(`Error: ${data.error}`);
            runBtn.disabled = false;
            runBtn.innerText = "Retry";
        }
    } catch (error) {
        console.error('Error running phase:', error);
        runBtn.disabled = false;
        runBtn.innerText = "Retry";
    } finally {
        isRunning = false;
    }
}

function updateSidebar(activeIndex) {
    const items = phaseList.getElementsByTagName('li');
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('active');
        if (i < activeIndex) {
            items[i].classList.add('completed');
            // Add checkmark if not present
            if (!items[i].querySelector('.check-icon')) {
                const statusDiv = items[i].querySelector('.step-status');
                statusDiv.innerHTML = '<span class="check-icon">✓</span>';
            }
        }
    }

    if (activePhaseTitle) {
        const activeItem = items[activeIndex];
        if (activeItem) {
            activeItem.classList.add('active');
            activePhaseTitle.innerText = activeItem.querySelector('.step-text').innerText;
        }
    }
}

function updateUI(state) {
    // Update main content output
    const outputDiv = document.getElementById('phase-output');
    // For now, just show the last result. Ideally, we append to a log.
    const phases = state.phases;
    const lastResult = phases[currentPhase - 1]?.result;

    if (lastResult) {
        outputDiv.innerText = typeof lastResult === 'object' ? JSON.stringify(lastResult, null, 2) : lastResult;
    }
    updateSidebar(state.current_phase_index);
}

function showApprovalModal(phaseIndex, message, state) {
    approvalModal.classList.add('active');
    const planText = document.getElementById('approval-plan-text');

    // Try to find the plan content from the previous phase result or current state
    const phaseData = state.phases[phaseIndex];
    planText.innerText = phaseData.result || "No specific plan details provided.";
}

async function handleApproval(action) {
    approvalModal.classList.remove('active');

    if (action === 'approve') {
        try {
            const response = await fetch('/api/approve', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                currentPhase++; // Advance after approval
                updateUI(data.state);
                runBtn.innerText = `Run Phase ${currentPhase + 1}`;
                runBtn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            alert("Approval failed");
        }
    } else {
        alert("Rejection/Amendment logic not yet implemented in backend.");
        runBtn.disabled = false;
        runBtn.innerText = "Retry / Amend";
    }
}
