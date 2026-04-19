import os
import sys
import time
import threading
import signal
import logging
from pathlib import Path

from dotenv import load_dotenv

# Clear console logs
if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')

# Add AI_Employee to sys.path
script_dir = Path(__file__).resolve().parent
load_dotenv(script_dir / ".env")
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "AI_Employee"))

# Centralized logging setup
from AI_Employee.logging_config import setup_logging
log_file_path = script_dir / "AI_Employee" / "vault" / "Logs" / "silver.log"
log_file_path.parent.mkdir(parents=True, exist_ok=True)
setup_logging(log_file_path)
logger = logging.getLogger(__name__)

from AI_Employee.orchestrator.orchestrator import Orchestrator
from AI_Employee.watchers.filesystem_watcher import FileSystemWatcher
from AI_Employee.watchers.gmail_watcher import GmailWatcher
from AI_Employee.watchers.whatsapp_watcher import WhatsAppWatcher
from AI_Employee.watchers.linkedin_watcher import LinkedInWatcher
from AI_Employee.watchers.approval_watcher import ApprovalWatcher
from AI_Employee.utils.dashboard_manager import update_dashboard

# Global flag for graceful shutdown
_running = True
watchers = []
watcher_threads = []
orchestrator_instance = None

def signal_handler(signum, frame):
    global _running
    logger.info("Ctrl+C detected. Initiating graceful shutdown...")
    _running = False

def start_watcher(watcher_class, vault_path, name):
    try:
        watcher = watcher_class(vault_path=vault_path)
        thread = threading.Thread(target=watcher.run, daemon=True, name=name)
        thread.start()
        watchers.append(watcher)
        watcher_threads.append(thread)
        logger.info(f"{name} started.")
    except Exception as e:
        logger.exception(f"{name} failed to start and will be skipped: {e}")

def main():
    global orchestrator_instance

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    vault_path = script_dir / "AI_Employee" / "vault"
    vault_path.mkdir(parents=True, exist_ok=True)

    # Initialize Audit Logger
    from AI_Employee.utils.audit_logger import setup_audit_logger
    setup_audit_logger(vault_path)

    logger.info(f"Using vault path: {vault_path}")
    update_dashboard(vault_path)

    # Initialize Watchers
    start_watcher(FileSystemWatcher, vault_path, "FileSystemWatcher")
    start_watcher(GmailWatcher, vault_path, "GmailWatcher")
    start_watcher(LinkedInWatcher, vault_path, "LinkedInWatcher")
    start_watcher(ApprovalWatcher, vault_path, "ApprovalWatcher")

    # Initialize Orchestrator
    orchestrator_instance = Orchestrator(vault_path=vault_path)

    # Start WhatsApp watcher last so other services are already initialized.
    start_watcher(WhatsAppWatcher, vault_path, "WhatsAppWatcher")

    logger.info("Starting orchestrator loop (Ctrl+C to stop)...")
    while _running:
        orchestrator_instance.process_tasks()
        
        update_dashboard(vault_path)
        
        # Sleep with check for shutdown
        for _ in range(5): # Check every second for 5 seconds
            if not _running:
                break
            time.sleep(1)

    logger.info("Orchestrator loop stopped.")

    # Stop Watchers
    for watcher in watchers:
        watcher.stop()
    
    for thread in watcher_threads:
        if thread.is_alive():
            logger.info(f"Waiting for {thread.name} to finish...")
            thread.join(timeout=2)
    
    logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
