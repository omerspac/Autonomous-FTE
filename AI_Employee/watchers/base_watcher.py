import abc
import time
import logging
import json
from pathlib import Path
from typing import Optional, Set, Any

logger = logging.getLogger(__name__)

class BaseWatcher(abc.ABC):
    """
    Production-ready base class for watchers.
    Handles:
    - Interval-based execution
    - Duplicate prevention via state persistence
    - Graceful error handling and logging
    - Abstract methods for update detection and action creation
    """

    def __init__(self, vault_path: Path, check_interval_seconds: int = 60):
        if check_interval_seconds <= 0:
            raise ValueError("check_interval_seconds must be a positive integer.")
        
        self.vault_path = Path(vault_path).resolve()
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        
        self.check_interval_seconds = check_interval_seconds
        self.running = False
        
        # State management to prevent duplicates
        self.state_file = self.vault_path / "Logs" / f"{self.__class__.__name__}_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_ids: Set[str] = self._load_state()

    def _load_state(self) -> Set[str]:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get("processed_ids", []))
            except Exception as e:
                logger.error(f"Failed to load state for {self.__class__.__name__}: {e}")
        return set()

    def _save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"processed_ids": list(self.processed_ids)}, f)
        except Exception as e:
            logger.error(f"Failed to save state for {self.__class__.__name__}: {e}")

    def is_processed(self, item_id: str) -> bool:
        return item_id in self.processed_ids

    def mark_as_processed(self, item_id: str):
        self.processed_ids.add(item_id)
        # Keep state file size manageable (optional: truncate old IDs)
        if len(self.processed_ids) > 1000:
            # Simple truncation: convert to list, take last 500
            self.processed_ids = set(list(self.processed_ids)[-500:])
        self._save_state()

    @abc.abstractmethod
    def check_for_updates(self) -> bool:
        """Checks for updates. Returns True if any new items were processed."""
        pass

    def create_action_file(self, metadata: dict, content: str, filename_prefix: str) -> Path:
        """
        Creates a markdown action file in Needs_Action.
        """
        timestamp = int(time.time())
        filename = f"{filename_prefix}_{timestamp}.md"
        filepath = self.needs_action_dir / filename
        
        # Format as Markdown with Frontmatter
        frontmatter = "---\n"
        for key, value in metadata.items():
            frontmatter += f"{key}: {value}\n"
        frontmatter += "---\n\n"
        
        full_content = frontmatter + content
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        logger.info(f"Created action file: {filepath}")
        return filepath

    def run(self) -> None:
        self.running = True
        logger.info(f"{self.__class__.__name__} started (Interval: {self.check_interval_seconds}s).")
        while self.running:
            try:
                self.check_for_updates()
            except Exception as e:
                logger.error(f"Error in {self.__class__.__name__} loop: {e}", exc_info=True)
                # Exponential backoff or simple retry delay could be added here
            
            # Sleep in small increments to allow for faster shutdown
            for _ in range(self.check_interval_seconds):
                if not self.running:
                    break
                time.sleep(1)

    def stop(self) -> None:
        self.running = False
        logger.info(f"{self.__class__.__name__} stopping.")
