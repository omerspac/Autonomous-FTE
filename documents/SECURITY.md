# AI Employee - Security Design

The AI Employee is designed with a "Secure by Default" posture, focusing on credential protection, human-in-the-loop gating, and comprehensive auditing.

## 🔐 1. Credential Management
- **Environment Variables**: All API keys, database passwords, and OAuth tokens are stored in `.env` files. These files are never committed to source control.
- **`credentials.json`**: For the Gmail API, the system uses a localized credential file that is excluded from the Git repository.
- **Token Caching**: Sensitive tokens are cached in the `vault/Logs/` directory and protected by the operating system's file permissions.

## 👥 2. Human-in-the-Loop (HITL)
The most critical security feature is the folder-based gating system:
1.  **Sensitive Actions**: Any task involving `email`, `social`, `payment`, or `accounting` is automatically marked for approval.
2.  **No Direct Execution**: The Action Layer (MCP) cannot be triggered directly by the AI. It only responds to files placed in the `Approved/` folder.
3.  **Physical Boundary**: The "Decision" requires a human to move a file from `Pending_Approval` to `Approved`.

## 📜 3. Audit Logging
Every significant AI event is logged in a daily, immutable JSON format:
- **Timestamp**: ISO format.
- **Actor**: The component that initiated the action (e.g., `Orchestrator`).
- **Target**: The MCP server or external platform (e.g., `LinkedIn`).
- **Approval Status**: Explicitly recorded (e.g., `APPROVED`, `N/A`).
- **Result**: The final output or error message.

## 🛠️ 4. Dry Run Mode
- For development and testing, all MCP servers support a `DRY_RUN=true` environment variable.
- In this mode, the AI can "execute" actions, but no actual API calls are made to external services. All logs will reflect the simulated status.

## 🚨 5. Vulnerability Reporting
If you discover a security vulnerability, please do not open an issue. Send a private report to the system administrator.
