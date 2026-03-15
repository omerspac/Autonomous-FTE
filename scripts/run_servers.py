import subprocess
import time
import os
import signal
import sys
from pathlib import Path

SERVERS = [
    {"name": "email-mcp", "path": "mcp_servers/email-mcp"},
    {"name": "social-mcp", "path": "mcp_servers/social-mcp"},
    {"name": "accounting-mcp", "path": "mcp_servers/accounting-mcp"},
    {"name": "browser-mcp", "path": "mcp_servers/browser-mcp"}
]

processes = []

def start_servers():
    root = Path(__file__).resolve().parent.parent
    for srv in SERVERS:
        full_path = root / srv["path"]
        print(f"Starting {srv['name']}...")
        
        # Check if npm install is needed (simplistic check)
        if not (full_path / "node_modules").exists():
            print(f"Installing dependencies for {srv['name']}...")
            subprocess.run(["npm", "install"], cwd=full_path, shell=True, check=True)

        p = subprocess.Popen(
            ["npm", "start"], 
            cwd=full_path, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append((srv["name"], p))

def cleanup(signum, frame):
    print("\nStopping all MCP servers...")
    for name, p in processes:
        p.terminate()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    start_servers()
    
    print("All servers started. Press Ctrl+C to stop.")
    
    # Watchdog loop
    while True:
        for name, p in processes:
            if p.poll() is not None:
                print(f"CRITICAL: {name} died! Restarting...")
                # In production, implement restart logic here
        time.sleep(5)
