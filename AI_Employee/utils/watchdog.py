import subprocess
import time
import logging
import signal
import sys
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SystemWatchdog:
    """
    Process Watchdog and Crash Recovery System.
    Restarts Watchers, Orchestrator, and MCP Servers on failure.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.processes: Dict[str, Any] = {}
        self.running = False

    def start_component(self, name: str, command: List[str], cwd: Path):
        """
        Starts a component and tracks its process.
        """
        logger.info(f"Starting {name}...")
        try:
            p = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True if sys.platform == "win32" else False
            )
            self.processes[name] = {
                "process": p,
                "command": command,
                "cwd": cwd,
                "start_time": time.time(),
                "restarts": 0
            }
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")

    def monitor_and_recover(self):
        """
        Continuous health check and auto-restart loop.
        """
        self.running = True
        logger.info("System Watchdog is active.")
        
        while self.running:
            for name, info in list(self.processes.items()):
                p = info["process"]
                
                # Check if process died
                if p.poll() is not None:
                    error_msg = f"CRITICAL: {name} crashed! Restarting..."
                    logger.critical(error_msg)
                    
                    # Log to system_errors.json (via HealthMonitor helper if available)
                    # For now, just attempt restart
                    info["restarts"] += 1
                    self.start_component(name, info["command"], info["cwd"])
            
            time.sleep(10) # Check every 10 seconds

    def stop_all(self):
        self.running = False
        logger.info("Stopping all components...")
        for name, info in self.processes.items():
            p = info["process"]
            p.terminate()
            logger.info(f"Stopped {name}")

if __name__ == "__main__":
    # Test stub
    # root = Path(__file__).resolve().parent.parent.parent
    # watchdog = SystemWatchdog(root)
    # watchdog.start_component("Silver_Orchestrator", ["python", "run_silver.py"], root)
    # watchdog.monitor_and_recover()
    pass
