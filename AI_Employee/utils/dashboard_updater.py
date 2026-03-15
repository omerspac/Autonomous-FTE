import logging
from pathlib import Path
from datetime import datetime

# Configure logging for the dashboard updates
logger = logging.getLogger(__name__)

def update_dashboard(vault_path: str) -> None:
    """
    Counts the number of files in 'Needs_Action', 'Plans', and 'Done' folders
    within the specified Obsidian vault and updates 'Dashboard.md' with the counts
    and a last updated timestamp.

    Args:
        vault_path: The absolute path to the Obsidian vault as a string.
    """
    try:
        vault_path_obj = Path(vault_path).resolve()

        needs_action_path = vault_path_obj / "Needs_Action"
        plans_path = vault_path_obj / "Plans"
        done_path = vault_path_obj / "Done"
        dashboard_file = vault_path_obj / "Dashboard.md"

        # Ensure directories exist, though they should be created by other components
        needs_action_path.mkdir(parents=True, exist_ok=True)
        plans_path.mkdir(parents=True, exist_ok=True)
        done_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Updating dashboard for vault: {vault_path_obj}")

        # Count files in each directory
        pending_tasks_count = len([f for f in needs_action_path.iterdir() if f.is_file()])
        active_plans_count = len([f for f in plans_path.iterdir() if f.is_file()])
        completed_tasks_count = len([f for f in done_path.iterdir() if f.is_file()])

        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dashboard_content = f"""# AI Employee Dashboard

## Status
Pending Tasks: {pending_tasks_count}
Active Plans: {active_plans_count}
Completed Tasks: {completed_tasks_count}

## Last Updated:
{current_timestamp}
"""

        # Overwrite Dashboard.md safely
        dashboard_file.write_text(dashboard_content, encoding='utf-8')
        logger.info(f"Dashboard.md updated successfully at {dashboard_file}")

    except FileNotFoundError as e:
        logger.error(f"One of the required vault directories or files was not found: {e}", exc_info=True)
    except IOError as e:
        logger.error(f"An I/O error occurred while updating the dashboard: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred in update_dashboard: {e}", exc_info=True)


if __name__ == "__main__":
    # Example usage:
    # Assuming a test vault structure for demonstration
    test_vault_path = Path("./test_vault_for_dashboard")
    test_vault_path.mkdir(exist_ok=True)
    (test_vault_path / "Needs_Action").mkdir(exist_ok=True)
    (test_vault_path / "Plans").mkdir(exist_ok=True)
    (test_vault_path / "Done").mkdir(exist_ok=True)

    # Create some dummy files for testing counts
    (test_vault_path / "Needs_Action" / "file1.md").touch()
    (test_vault_path / "Needs_Action" / "file2.md").touch()
    (test_vault_path / "Plans" / "plan_a.md").touch()
    (test_vault_path / "Done" / "task_x.md").touch()
    (test_vault_path / "Done" / "task_y.md").touch()
    (test_vault_path / "Done" / "task_z.md").touch()

    update_dashboard(str(test_vault_path))

    # Verify content (optional)
    print(f"\nContent of {test_vault_path / 'Dashboard.md'}:\n")
    print((test_vault_path / "Dashboard.md").read_text())

    # Clean up test files (optional)
    import shutil
    # shutil.rmtree(test_vault_path)
