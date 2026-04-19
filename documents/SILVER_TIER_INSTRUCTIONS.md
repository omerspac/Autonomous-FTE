# Silver Tier Autonomous FTE - Setup Instructions

## 1. Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for MCP Server)
- **Obsidian** (Optional, for viewing the Vault)

## 2. Installation

1.  **Install Python Dependencies:**
    ```bash
    pip install watchdog
    ```
    *(Note: If you use a virtual environment, activate it first.)*

2.  **Install MCP Server Dependencies:**
    Navigate to the MCP server directory you need (example: email server):
    ```bash
    cd mcp_servers/email-mcp
    npm install
    ```
    This installs `@modelcontextprotocol/sdk`.

## 3. Directory Structure

The system uses the following structure:

```
AI_Employee/
├── vault/                  # The "Brain" of the FTE
│   ├── Needs_Action/       # Incoming tasks (from Watchers)
│   ├── Plans/              # Generated plans (History)
│   ├── Pending_Approval/   # Plans waiting for human review
│   ├── Approved/           # Plans approved for execution
│   ├── Done/               # Completed tasks
│   ├── Rejected/           # Rejected plans
│   ├── Logs/               # System logs
│   ├── Skills/             # Skill definitions (if used)
│   ├── Dashboard.md        # Status dashboard
│   ├── Company_Handbook.md # Context
│   └── Business_Goals.md   # Context
├── watchers/               # Sensors (Gmail, WhatsApp, LinkedIn, FileSystem)
├── orchestrator/           # Logic (Reasoning & Execution)
├── skills/                 # AI Capabilities
└── utils/                  # Helpers
mcp_servers/                # Node.js MCP action servers (email/social/accounting/browser)
run_silver.py               # Main entry point
```

## 4. Running the System

1.  **Start the Silver Tier Agent:**
    Run the main script from the root directory:
    ```bash
    python run_silver.py
    ```

2.  **Workflow:**
    - **Input:** Drop a file into `AI_Employee/vault/Inbox` or wait for mock watchers to generate tasks in `Needs_Action`.
    - **Planning:** The Orchestrator picks up tasks from `Needs_Action`, generates a plan, and saves it to `Pending_Approval`.
    - **Approval:**
        - Open `AI_Employee/vault/Pending_Approval`.
        - Review the generated `PLAN_*.md`.
        - If satisfied, move the file to `AI_Employee/vault/Approved`.
    - **Execution:** The Orchestrator detects the file in `Approved`, executes it (currently logs execution), and moves it to `Done`.

## 5. Customization

- **Watchers:** Edit `AI_Employee/watchers/*.py` to implement real API calls (Gmail, WhatsApp, LinkedIn).
- **MCP Server:** Edit the target server entrypoint (for example, `mcp_servers/email-mcp/index.js`) to add real tools.
- **Orchestrator:** Edit `AI_Employee/orchestrator/orchestrator.py` to change the logic or integrate with a real LLM (currently uses a mock/fallback if `claude` CLI is missing).

## 6. Logs

Check `AI_Employee/vault/Logs/silver.log` for system logs and `AI_Employee/vault/Logs/execution.log` for plan execution records.
