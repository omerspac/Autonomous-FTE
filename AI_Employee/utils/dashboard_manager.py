import logging
from pathlib import Path
from datetime import datetime
from typing import NoReturn

# Configure logging for the dashboard manager
logger = logging.getLogger(__name__)

# Ensure a default handler is present if this module is run standalone
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def _count_files_in_directory(directory_path: Path) -> int:
    """
    Counts the number of files directly within a given directory.
    """
    if not directory_path.is_dir():
        logger.warning(f"Directory not found or is not a directory: {directory_path}")
        return 0
    return sum(1 for item in directory_path.iterdir() if item.is_file())

def update_dashboard(vault_path: Path) -> None:
    """
    Updates the AI Employee Dashboard.md file within the vault root.

    Counts files in Needs_Action, Plans, and Done directories and generates
    a Dashboard.md with these counts and a last updated timestamp.

    Args:
        vault_path: The absolute path to the Obsidian vault.
    """
    try:
        vault_path = vault_path.resolve()
        logger.info(f"Updating dashboard for vault: {vault_path}")

        # Define paths for relevant directories
        needs_action_path = vault_path / "Needs_Action"
        plans_path = vault_path / "Plans"
        done_path = vault_path / "Done"
        dashboard_file_path = vault_path / "Dashboard.md"

        # Count files
        pending_tasks_count = _count_files_in_directory(needs_action_path)
        active_plans_count = _count_files_in_directory(plans_path)
        completed_tasks_count = _count_files_in_directory(done_path)

        # Generate dashboard content
        current_timestamp = datetime.now().isoformat()
        dashboard_content = f"""# AI Employee Dashboard

## Status
Pending Tasks: {pending_tasks_count}
Active Plans: {active_plans_count}
Completed Tasks: {completed_tasks_count}

## Last Updated:
{current_timestamp}
"""

        # Overwrite Dashboard.md safely
        dashboard_file_path.write_text(dashboard_content, encoding='utf-8')
        logger.info(f"Dashboard.md successfully updated at {dashboard_file_path}")

    except Exception as e:
        logger.error(f"Error updating dashboard for vault '{vault_path}': {e}", exc_info=True)
        # Re-raise the exception to indicate failure to the caller
        raise

if __name__ == "__main__":
    # Example usage:
    # This assumes a 'test_vault' directory exists one level up from 'utils'
    # For a real application, vault_path would be passed dynamically.
    example_vault_path = Path(__file__).resolve().parent.parent.parent / "AI_Employee" / "vault"
    example_vault_path.mkdir(parents=True, exist_ok=True) # Ensure vault exists

    # Create dummy directories for testing counts
    (example_vault_path / "Needs_Action").mkdir(exist_ok=True)
    (example_vault_path / "Plans").mkdir(exist_ok=True)
    (example_vault_path / "Done").mkdir(exist_ok=True)

    # Create dummy files
    (example_vault_path / "Needs_Action" / "task1.txt").touch()
    (example_vault_path / "Needs_Action" / "task2.txt").touch()
    (example_vault_path / "Plans" / "plan_a.md").touch()
    (example_vault_path / "Done" / "completed_item.log").touch()

    print(f"Running example dashboard update for: {example_vault_path}")
    update_dashboard(example_vault_path)
    print(f"Check {example_vault_path / 'Dashboard.md'} for output.")

    # Clean up dummy files
    (example_vault_path / "Needs_Action" / "task1.txt").unlink()
    (example_vault_path / "Needs_Action" / "task2.txt").unlink()
    (example_vault_path / "Plans" / "plan_a.md").unlink()
    (example_vault_path / "Done" / "completed_item.log").unlink()
    print("Example dummy files cleaned up.")
