import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

def setup_logging(log_path: Path):
    """
    Sets up centralized logging for the AI Employee system.

    Logs to a rotating file handler and to the console.

    Args:
        log_path: The full path to the log file (e.g., AI_Employee/logs/bronze.log).
    """
    # Ensure the log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear any existing handlers to prevent duplicate output
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Define a formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    # File Handler (Rotating)
    # Max 5 MB per file, keep 5 backup files
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Initial log message to confirm setup
    logger = logging.getLogger(__name__)
    logger.info(f"Centralized logging setup complete. Logging to: {log_path}")