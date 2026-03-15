# AI Employee - Architecture Overview

The system follows a Three-Layer Architecture: Perception, Reasoning, and Action. All layers are decoupled and communicate via the central Markdown database (The Vault).

## 🏗 System Diagram (ASCII)

```text
    +-----------------------------------------------------------+
    |                    Perception Layer                       |
    |  [Gmail API]      [Playwright]      [Watchdog (FS)]       |
    |  (EmailWatcher)   (WhatsAppWatcher) (FileWatcher)         |
    +-----------------------------+-----------------------------+
                                  |
                                  v
    +-----------------------------+-----------------------------+
    |                      THE VAULT (Brain)                    |
    |  /Needs_Action  /Plans  /Approved  /Done  /Rejected       |
    +-----------------------------+-----------------------------+
                                  |
                                  v
    +-----------------------------+-----------------------------+
    |                      Reasoning Layer                      |
    |  [Orchestrator] <---> [Agent Skills] <---> [Ralph Loop]   |
    |  (Task Planning)      (Business context)   (Auto-Retries) |
    +-----------------------------+-----------------------------+
                                  |
                                  v
    +-----------------------------+-----------------------------+
    |                        Action Layer                       |
    |  [Email MCP]   [Social MCP]   [Accounting MCP]  [Browser] |
    |  (Actions/Tools) (FB/X/Insta)  (Odoo ERP)       (Puppet.) |
    +-----------------------------+-----------------------------+
                                  |
                                  v
    +-----------------------------------------------------------+
    |                    Governance & Audit                     |
    |  [Human Approval] [Daily JSON Audit] [System Error Log]   |
    +-----------------------------------------------------------+
```

## 🧠 Component Descriptions

### 1. Perception Layer (Watchers)
- **Watchers** are long-running Python threads that monitor external triggers.
- They transform raw data (Emails, Chats, Files) into standardized Markdown/JSON files and place them in `vault/Needs_Action`.
- **Duplicate Prevention**: Each watcher maintains a state file to ensure it doesn't process the same item twice.

### 2. Reasoning Layer (Orchestrator)
- **The Orchestrator** is the "Thinking Loop". It reads inputs from `Needs_Action` and generates a structured `Plan.md`.
- **Ralph Wiggum Loop**: An iterative processing model that ensures tasks aren't marked complete until the system confirms success or hits a retry limit.
- **Routing Logic**: Determines if a plan needs human approval (e.g., payments) or can be executed directly.

### 3. Action Layer (MCP Servers)
- Built on the **Model Context Protocol (MCP)** by Anthropic.
- Modular Node.js servers that expose specific capabilities (Tools) to the agent.
- **`accounting-mcp`**: Connects directly to Odoo ERP for live financial management.
- **`social-mcp`**: Handles multi-platform engagement (FB, IG, Twitter).

### 4. Human-in-the-loop (HITL)
- **Mandatory Gating**: Any action involving money, public-facing content, or formal communication is sent to `vault/Pending_Approval`.
- **Execution**: Only when the user moves the file to `vault/Approved` does the `ApprovalWatcher` trigger the actual Action Layer.
