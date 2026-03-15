import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)

class FileSystemWatcher(BaseWatcher, FileSystemEventHandler):
    def __init__(self, vault_path: Path, check_interval_seconds: int = 60):
        # We call BaseWatcher init first
        super().__init__(vault_path, check_interval_seconds)
        self.inbox_path = self.vault_path / "Inbox"
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        self.observer = Observer()
        self.observer.schedule(self, str(self.inbox_path), recursive=False)

    def check_for_updates(self) -> bool:
        """
        The heavy lifting is done by on_created, but we can use this 
        for periodic health checks of the observer.
        """
        if not self.observer.is_alive():
            logger.warning("Observer was dead, restarting...")
            self.observer.start()
        return False

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if self.is_processed(str(file_path)):
            return

        logger.info(f"New file detected in Inbox: {file_path.name}")
        
        # Give it a moment to finish writing
        time.sleep(1)
        
        try:
            # Metadata for the task
            metadata = {
                "type": "file",
                "original_name": file_path.name,
                "path": str(file_path.absolute()),
                "extension": file_path.suffix,
                "detected_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            content = f"# New File Received: {file_path.name}\n\n**Detected:** {metadata['detected_at']}\n**Original Path:** {metadata['path']}\n\n---"
            
            # Create action file (MD)
            self.create_action_file(metadata, content, "file_drop")
            
            # Copy original file to Needs_Action as well
            shutil.copy(file_path, self.needs_action_dir / file_path.name)
            
            self.mark_as_processed(str(file_path))
            
            # Optional: Move to Inbox/Processed or delete
            # file_path.unlink()

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")

    def run(self) -> None:
        self.observer.start()
        super().run()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join()
        super().stop()
