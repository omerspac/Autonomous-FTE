import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Health Monitoring and Error Reporting for Autonomous FTE.
    """
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.error_log = vault_path / "Logs" / "system_errors.json"
        self.error_log.parent.mkdir(parents=True, exist_ok=True)
        if not self.error_log.exists():
            self.error_log.write_text("[]")

    def log_failure(self, component: str, error: str, severity: str = "ERROR"):
        """
        Logs a failure to a structured JSON file.
        """
        failure_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error,
            "severity": severity
        }
        
        try:
            with open(self.error_log, "r+") as f:
                data = json.load(f)
                data.append(failure_entry)
                
                # Keep log size manageable (last 100 errors)
                if len(data) > 100:
                    data = data[-100:]
                
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            
            logger.info(f"Logged failure for {component}: {error}")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to write to system_errors.json: {e}")

    def check_disk_space(self) -> bool:
        """
        Graceful Degradation: Check if we have space to work.
        """
        # Basic check: vault path exists and has space
        import shutil
        total, used, free = shutil.disk_usage(self.vault_path)
        if free < 100 * 1024 * 1024: # Less than 100MB
            self.log_failure("System", "Disk space critically low (<100MB)", "CRITICAL")
            return False
        return True

    def get_summary(self) -> Dict[str, Any]:
        """
        Summary for the CEO Briefing.
        """
        try:
            with open(self.error_log, "r") as f:
                data = json.load(f)
                return {
                    "total_errors": len(data),
                    "last_error": data[-1] if data else None
                }
        except:
            return {"total_errors": 0}
