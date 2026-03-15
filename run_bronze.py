import os
import sys
import time
import threading
import signal
import logging # Import logging for direct use by run_bronze.py

from pathlib import Path

# Clear console logs (this remains outside logging as it's a console specific action)
if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')

# Add AI_Employee to sys.path to allow importing modules
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "AI_Employee"))

# Centralized logging setup
from AI_Employee.logging_config import setup_logging
log_file_path = script_dir / "AI_Employee" / "logs" / "bronze.log"
setup_logging(log_file_path)
logger = logging.getLogger(__name__) # Get logger for run_bronze.py itself

from AI_Employee.orchestrator.orchestrator import Orchestrator
from AI_Employee.watchers.filesystem_watcher import FileSystemWatcher
from AI_Employee.utils.dashboard_manager import update_dashboard # Import dashboard updater

# Global flag for graceful shutdown
_running = True
watcher_thread = None
file_system_watcher_instance = None
orchestrator_instance = None

def signal_handler(signum, frame):
    global _running
    logger.info("Ctrl+C detected. Initiating graceful shutdown...")
    _running = False

def main():
    global watcher_thread, file_system_watcher_instance, orchestrator_instance

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler) # Also handle SIGTERM

    # Define the vault path
    # For now, we'll assume the vault is located at AI_Employee/vault relative to the script.
    # In a production environment, this should be configurable (e.g., via environment variable).
    vault_path = script_dir / "AI_Employee" / "vault"
    vault_path.mkdir(parents=True, exist_ok=True) # Ensure vault directory exists

    logger.info(f"Using vault path: {vault_path}") # Changed from print to logger.info
    update_dashboard(vault_path) # Initial dashboard update

    # Initialize FileSystemWatcher
    file_system_watcher_instance = FileSystemWatcher(vault_path=vault_path) # Removed log_file parameter
    watcher_thread = threading.Thread(target=file_system_watcher_instance.run, daemon=True)
    watcher_thread.start()
    # "FileSystemWatcher started in background thread." will be logged by watcher itself

    # Initialize Orchestrator
    orchestrator_instance = Orchestrator(vault_path=vault_path) # Removed log_file parameter
    # "Orchestrator initialized." will be logged by orchestrator itself

    logger.info("Starting orchestrator loop (Ctrl+C to stop)...") # Changed from print to logger.info
    while _running:
        orchestrator_instance.scan_and_process_files()
        update_dashboard(vault_path) # Update dashboard after processing
        for i in range(30):
            if not _running:
                break
            time.sleep(1)
        if not _running:
            break

    logger.info("Orchestrator loop stopped.") # Changed from print to logger.info

    # Stop the FileSystemWatcher gracefully
    if file_system_watcher_instance:
        file_system_watcher_instance.stop()
        if watcher_thread and watcher_thread.is_alive():
            logger.info("Waiting for FileSystemWatcher thread to finish...") # Changed from print to logger.info
            watcher_thread.join(timeout=5) # Give it some time to stop
            if watcher_thread.is_alive():
                logger.warning("FileSystemWatcher thread did not terminate gracefully.") # Changed from print to logger.warning
            else:
                logger.info("FileSystemWatcher thread stopped.") # Changed from print to logger.info
        else:
            logger.info("FileSystemWatcher was not running or thread already finished.") # Changed from print to logger.info


    logger.info("Shutdown complete.") # Changed from print to logger.info

if __name__ == "__main__":
    main()

