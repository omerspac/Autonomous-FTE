const PYTHON_PATH = "C:\\Users\\omera\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\python.exe";

module.exports = {
  apps: [
    // --- WATCHERS ---
    {
      name: "gmail-watcher",
      script: "AI_Employee/watchers/gmail_watcher.py",
      interpreter: PYTHON_PATH,
      restart_delay: 5000,
      env: {
        NODE_ENV: "production",
      }
    },
    {
      name: "whatsapp-watcher",
      script: "AI_Employee/watchers/whatsapp_watcher.py",
      interpreter: PYTHON_PATH,
      restart_delay: 10000, // WhatsApp might need more time between restarts
    },
    {
      name: "fs-watcher",
      script: "AI_Employee/watchers/filesystem_watcher.py",
      interpreter: PYTHON_PATH,
    },

    // --- REASONING ---
    {
      name: "orchestrator",
      script: "run_silver.py",
      interpreter: PYTHON_PATH,
    },

    // --- MCP SERVERS ---
    {
      name: "accounting-mcp",
      script: "mcp_servers/accounting-mcp/accounting_mcp_server.js",
      cwd: "mcp_servers/accounting-mcp",
    },
    {
      name: "browser-mcp",
      script: "mcp_servers/browser-mcp/index.js",
      cwd: "mcp_servers/browser-mcp",
    },
    {
      name: "email-mcp",
      script: "mcp_servers/email-mcp/index.js",
      cwd: "mcp_servers/email-mcp",
    },
    {
      name: "social-mcp",
      script: "mcp_servers/social-mcp/social_mcp_server.js",
      cwd: "mcp_servers/social-mcp",
    },
  ],
};
