import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Comprehensive Audit Logging for AI Employee.
    Stores logs in /Logs/YYYY-MM-DD.json as a JSON list.
    """
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).resolve()
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.logs_dir / f"{today}.json"

    def log_action(self, 
                   action_type: str, 
                   actor: str, 
                   target: str, 
                   parameters: Dict[str, Any], 
                   result: Any, 
                   approval_status: str = "N/A"):
        """
        Records a single AI action to the daily log file.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "result": result
        }

        log_file = self._get_log_file()
        
        try:
            # Read existing logs or start new list
            if log_file.exists():
                with open(log_file, "r+", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
                    
                    data.append(entry)
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
            else:
                with open(log_file, "w", encoding="utf-8") as f:
                    json.dump([entry], f, indent=4)
            
            logger.debug(f"Audit log entry created for {action_type}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

# Global helper for easy access
_instance: Optional[AuditLogger] = None

def setup_audit_logger(vault_path: Path):
    global _instance
    _instance = AuditLogger(vault_path)

def log_ai_action(action_type: str, actor: str, target: str, parameters: Dict[str, Any], result: Any, approval_status: str = "N/A"):
    if _instance:
        _instance.log_action(action_type, actor, target, parameters, result, approval_status)
    else:
        # Fallback to standard logging if audit logger not initialized
        logging.getLogger(__name__).warning(f"Audit Logger not initialized. Action: {action_type} - {result}")
