import json
import logging
import time
from pathlib import Path
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)

class RalphLoop:
    """
    Ralph Wiggum Autonomous Loop: "I'm helping!"
    Ensures a task is processed iteratively until a completion promise is found.
    """
    def __init__(self, vault_path: Path, max_iterations: int = 5):
        self.vault_path = vault_path
        self.max_iterations = max_iterations
        self.state_file = vault_path / "Logs" / "ralph_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {}

    def _save_state(self, task_id: str, iteration: int, status: str):
        state = self._load_state()
        state[task_id] = {
            "iteration": iteration,
            "status": status,
            "last_run": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.state_file.write_text(json.dumps(state, indent=2))

    def run_until_complete(self, task_id: str, process_func: Callable[..., str], *args, **kwargs) -> bool:
        """
        Runs the provided process_func until it returns the <promise>TASK_COMPLETE</promise> tag
        or reaches max_iterations.
        """
        iteration = 1
        logger.info(f"Starting Ralph Loop for task: {task_id}")

        while iteration <= self.max_iterations:
            try:
                logger.info(f"Iteration {iteration}/{self.max_iterations} for {task_id}")
                
                # Execute the task processing
                result_output = process_func(*args, **kwargs)
                
                # Check for the completion promise
                if "<promise>TASK_COMPLETE</promise>" in result_output:
                    logger.info(f"SUCCESS: Task {task_id} completed successfully.")
                    self._save_state(task_id, iteration, "COMPLETED")
                    return True
                
                logger.warning(f"Task {task_id} not yet complete. Retrying...")
                self._save_state(task_id, iteration, "IN_PROGRESS")
                
            except Exception as e:
                logger.error(f"Error in Ralph Loop iteration {iteration}: {e}")
                self._save_state(task_id, iteration, f"ERROR: {str(e)}")
            
            iteration += 1
            time.sleep(2) # Small cooldown between iterations

        logger.error(f"FAILURE: Task {task_id} failed to complete after {self.max_iterations} iterations.")
        return False
