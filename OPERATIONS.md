# AI Employee - Operations Guide

This guide describes how to run, monitor, and scale the AI Employee system in a production environment.

## 🏃 Running the System

1.  **Start Background Services**:
    The Action Layer (MCP Servers) must be running for the agent to execute any approved tasks.
    ```bash
    python scripts/run_servers.py
    ```

2.  **Start the Agent Loop**:
    The agent manages perception and reasoning. It can be started as a persistent daemon.
    ```bash
    python run_silver.py
    ```

## 📊 Monitoring

### 1. Health Checks
- **Watchdog Process**: Automatically restarts any component (Watcher, Orchestrator, MCP) that crashes.
- **System Error Logs**: Check `vault/Logs/system_errors.json` for high-level infrastructure failures.
- **Daily Audit Logs**: Check `vault/Logs/YYYY-MM-DD.json` for a history of all AI reasoning and actions.

### 2. Dashboard
Open `vault/Dashboard.md` in Obsidian for a real-time view of:
- **Pending Actions**: Tasks waiting in the queue.
- **Financial Status**: Real-time revenue/receivables.
- **System Uptime**: Status of all watchers.

## 🔄 Scaling Strategy

### 1. Adding New Skills
To extend the AI's intelligence:
1.  Create a new skill definition in `vault/Skills/`.
2.  Implement the logic in `AI_Employee/skills/`.
3.  The Orchestrator will automatically detect and utilize the new skill for relevant tasks.

### 2. Adding New Actions
To extend the AI's capabilities:
1.  Develop a new MCP server in `mcp_servers/`.
2.  Expose tools via the `@modelcontextprotocol/sdk`.
3.  Register the new server in `scripts/run_servers.py`.

### 3. Horizontal Scaling
- The **Action Layer** (MCP Servers) can be distributed across different machines or containers.
- The **Vault** can be shared via a network filesystem (NAS) or synced via cloud storage (Dropbox/Drive) for remote access to approvals.

## 🛠️ Maintenance

- **Log Rotation**: The system logs to daily files. Periodically archive or delete logs older than 30 days.
- **Odoo Backups**: Ensure the Odoo database is backed up regularly via standard Docker/PostgreSQL methods.
- **State Cleanup**: Truncate `*_state.json` files in `vault/Logs/` if they exceed 10,000 entries.
