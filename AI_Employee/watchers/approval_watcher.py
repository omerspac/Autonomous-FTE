import time
import logging
import shutil
import yaml
import re
import json
import subprocess
from pathlib import Path
from .base_watcher import BaseWatcher

from AI_Employee.utils.audit_logger import log_ai_action

logger = logging.getLogger(__name__)

class ApprovalWatcher(BaseWatcher):
    """
    Human-in-the-loop Approval Watcher.
    Monitors the /Approved folder for plans moved there by the user.
    Executes the approved plans using the MCP Server.
    """

    def __init__(self, vault_path: Path, check_interval_seconds: int = 10):
        super().__init__(vault_path, check_interval_seconds)
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
        self.rejected_dir = self.vault_path / "Rejected"
        self.logs_dir = self.vault_path / "Logs"
        
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)

    def _parse_plan(self, file_path: Path):
        content = file_path.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if match:
            metadata = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            return metadata, body
        return None, content

    def execute_action(self, metadata: dict, body: str):
        """
        Interprets the plan and calls the MCP server.
        """
        action_type = metadata.get("type", "unknown")
        target = metadata.get("mcp_target", "unknown")
        
        logger.info(f"Executing approved action: {action_type} via {target}")
        
        result = {
            "status": "SUCCESS",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action": action_type,
            "details": f"Executed action based on plan for {metadata.get('source_file')}"
        }

        if target == "social-mcp":
            content = self._extract_social_content(body)
            repo_root = Path(__file__).resolve().parents[2]
            social_mcp_dir = repo_root / "mcp_servers" / "social-mcp"

            cmd = ["node", "post_twitter_cli.js", content]
            proc = subprocess.run(
                cmd,
                cwd=social_mcp_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            if proc.returncode != 0:
                error_text = (proc.stderr or proc.stdout or "Unknown X execution error").strip()
                result = {
                    "status": "FAILED",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": action_type,
                    "details": error_text,
                }
            else:
                cli_out = (proc.stdout or "").strip()
                try:
                    payload = json.loads(cli_out) if cli_out else {}
                except json.JSONDecodeError:
                    payload = {"raw": cli_out}

                result = {
                    "status": "SUCCESS",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": action_type,
                    "details": payload,
                }
        
        # Comprehensive Audit Logging
        log_ai_action(
            action_type=action_type,
            actor="ApprovalWatcher",
            target=target,
            parameters=metadata,
            result=result,
            approval_status="APPROVED"
        )
            
        return result

    def _extract_social_content(self, body: str) -> str:
        """Extracts best-effort content text from a generated plan body."""
        objective_match = re.search(r"# Objective\s*(.*?)\s*(#|$)", body, re.DOTALL | re.IGNORECASE)
        if objective_match:
            text = objective_match.group(1).strip()
        else:
            text = body.strip()

        # Keep the content concise for X posting limits.
        return text[:260]

    def check_for_updates(self) -> bool:
        approved_plans = list(self.approved_dir.glob("*.md"))
        if not approved_plans:
            return False

        new_processed = False
        for plan_file in approved_plans:
            try:
                logger.info(f"Detected approved plan: {plan_file.name}")
                
                # 1. Parse
                metadata, body = self._parse_plan(plan_file)
                
                # 2. Execute
                execution_result = self.execute_action(metadata, body)
                logger.info(f"Execution result: {execution_result['status']}")
                
                # 3. Move to Done
                shutil.move(str(plan_file), str(self.done_dir / plan_file.name))
                logger.info(f"Moved {plan_file.name} to Done.")
                
                new_processed = True
                
            except Exception as e:
                logger.error(f"Failed to execute approved plan {plan_file.name}: {e}", exc_info=True)

        return new_processed
