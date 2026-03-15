# Autonomous AI Employee (Gold Tier)

An advanced, multi-domain AI workforce automation system designed to handle perception, reasoning, and action layers autonomously with human-in-the-loop oversight.

## What This Project Is About

Autonomous FTE is a personal AI operations manager focused on social media, communications, and business workflows. You can think of it as an always-on digital teammate that monitors incoming activity, generates execution plans, and helps run repeatable work across channels from one control flow.

The system is organized into three layers: Perception (watchers), Reasoning (orchestrator + planning skill), and Action (MCP servers). Watchers collect signals from sources like Gmail, WhatsApp Web, LinkedIn (scaffolded), and the local Inbox, then convert them into structured tasks in the Vault. The orchestrator analyzes each task, builds a plan, maps it to the right MCP target, and decides whether approval is required before execution.

For sensitive work, the project enforces human-in-the-loop governance. Items involving public posting, payments, invoices, or formal outbound communication are routed to Pending_Approval first. After approval, actions are executed and logged to the Vault for traceability and audits.

### Current Focus Areas

- Personal social media manager flows (drafting/routing posts and social actions through MCP tools)
- Email and calendar automation flows
- Finance and accounting workflows via Odoo-oriented MCP tooling
- Browser automation helpers for web tasks
- Scheduled executive reporting (daily summaries, weekly audits, CEO briefing)

## 🚀 Quick Start

1. **Clone & Install**:
   ```bash
   git clone <repo-url>
   pip install -r requirements.txt
   ```

2. **Setup MCP Servers**:
   Navigate to each directory in `mcp_servers/` and run `npm install`.

3. **Configure Environment**:
   Copy `.env.example` to `.env` in the root and in each MCP server directory. Fill in your API keys (Gmail, Odoo, etc.).

4. **Launch Infrastructure**:
   ```bash
   # Start the MCP Action Layer & Watchdog
   python scripts/run_servers.py
   ```

5. **Launch the Agent**:
   ```bash
   # Start the Perception & Reasoning Layer
   python run_silver.py
   ```

## 📂 Project Structure

- `AI_Employee/`: Core Python logic (Watchers, Orchestrator, Utils).
- `mcp_servers/`: Action layer (Node.js servers for Email, Social, Odoo, Browser).
- `vault/`: The "Brain" (Obsidian-compatible Markdown database).
- `scripts/`: Operational tools and scheduled tasks.
- `Logs/`: Daily audit trails and system health logs.

## 🛠 Features

- **Multi-Channel Perception**: Gmail, WhatsApp, and Filesystem monitoring.
- **Iterative Reasoning**: Ralph Wiggum Loop ensures task completion with retries.
- **Financial Integration**: Full Odoo ERP connectivity for invoicing and P&L.
- **Social Presence**: Automated posting to LinkedIn, Facebook, X, and Instagram.
- **Human-in-the-loop**: Mandatory approval for sensitive actions (payments, public posts).
- **CEO Briefing**: Automated Monday morning strategic reports.

---
*See [ARCHITECTURE.md](./ARCHITECTURE.md) for deep technical details.*
