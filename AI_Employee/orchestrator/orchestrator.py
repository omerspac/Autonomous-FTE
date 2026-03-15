import os
import time
import shutil
import logging
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from AI_Employee.skills.plan_generation_skill import PlanGenerationSkill
except ImportError:
    PlanGenerationSkill = None

from AI_Employee.utils.dashboard_manager import update_dashboard

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Gold Tier Orchestrator:
    - Multi-domain reasoning (Finance, Social, Business)
    - Ralph Wiggum Loop: "I'm helping!" (Continuous retry/verification)
    """

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).resolve()
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.plans_path = self.vault_path / "Plans"
        self.done_path = self.vault_path / "Done"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        
        # Ensure directory structure
        for p in [self.needs_action_path, self.plans_path, self.done_path, self.pending_approval_path]:
            p.mkdir(parents=True, exist_ok=True)

        self.ai_skill = PlanGenerationSkill() if PlanGenerationSkill else None
        logger.info(f"Gold Tier Orchestrator initialized at {self.vault_path}")

    def _parse_markdown_task(self, file_path: Path) -> Dict[str, Any]:
        """
        Parses YAML frontmatter and content from a markdown file.
        """
        content = file_path.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if match:
            try:
                metadata = yaml.safe_load(match.group(1))
                body = match.group(2).strip()
                return {"metadata": metadata, "body": body}
            except Exception as e:
                logger.error(f"Failed to parse YAML in {file_path.name}: {e}")
        
        return {"metadata": {}, "body": content.strip()}

    def _determine_approval_required(self, metadata: dict, body: str) -> bool:
        """
        Gold Tier Rules:
        - Financial transactions > $0 require approval (Odoo)
        - Public Social Media posts require approval
        - Email sending requires approval
        """
        task_type = metadata.get("type", "").lower()
        content = (body + str(metadata)).lower()
        
        # Rule 1: Type-based
        if task_type in ["email", "linkedin", "payment", "social", "accounting"]:
            return True
            
        # Rule 2: Keyword-based
        keywords = ["send email", "payment", "invoice", "post to", "transfer", "pay", "tweet", "publish"]
        if any(kw in content for kw in keywords):
            return True
            
        return False

    def generate_plan(self, task_info: dict, source_file: str) -> str:
        """
        Generates a structured plan aware of Gold Tier MCP capabilities.
        """
        metadata = task_info["metadata"]
        body = task_info["body"]
        approval_needed = self._determine_approval_required(metadata, body)
        
        task_type = metadata.get("type", "unknown")
        
        # Map task to MCP server
        mcp_target = "unknown"
        if task_type in ["email", "calendar"]: mcp_target = "email-mcp"
        elif task_type in ["linkedin", "social", "twitter", "facebook"]: mcp_target = "social-mcp"
        elif task_type in ["payment", "invoice", "accounting"]: mcp_target = "accounting-mcp"
        elif task_type in ["research", "browser"]: mcp_target = "browser-mcp"

        # Plan Frontmatter
        plan_header = f"""---
created: {datetime.now().isoformat()}
status: pending
source_file: {source_file}
approval_required: {"Yes" if approval_needed else "No"}
mcp_target: {mcp_target}
---

"""
        
        if self.ai_skill:
            ai_output = self.ai_skill.execute(f"Metadata: {metadata}\n\nContent: {body}\n\nTarget MCP: {mcp_target}")
            if ai_output:
                return plan_header + ai_output

        # Template Fallback
        objective = metadata.get("subject", metadata.get("original_name", "Process incoming task"))
        
        steps = [
            f"- [ ] Analyze context from {metadata.get('from', 'source')}",
            f"- [ ] Select tool from {mcp_target} (e.g., {task_type}_action)",
            "- [ ] Verify data integrity"
        ]
        
        if approval_needed:
            steps.insert(1, "- [ ] Wait for human approval in /Pending_Approval")
            steps.append(f"- [ ] Execute {task_type} via {mcp_target}")

        plan_body = f"""# Objective
{objective}

# Analysis
Task type identified as **{task_type}**. Routing to **{mcp_target}**.

# Steps
{chr(10).join(steps)}

# Approval Required
{"Yes" if approval_needed else "No"}
"""
        return plan_header + plan_body

    def process_tasks(self):
        """
        Ralph Wiggum Loop: "I'm helping!"
        Ensures tasks are processed until the <promise>TASK_COMPLETE</promise> tag is found.
        """
        from AI_Employee.orchestrator.ralph_loop import RalphLoop
        ralph = RalphLoop(self.vault_path, max_iterations=3)

        tasks = list(self.needs_action_path.glob("*.md")) + list(self.needs_action_path.glob("*.json"))
        if not tasks:
            return

        logger.info(f"Processing {len(tasks)} tasks...")
        
        for task_file in tasks:
            def run_processing():
                # Internal helper for RalphLoop execution
                try:
                    logger.info(f"Ralph is processing: {task_file.name}")
                    if task_file.suffix == '.json':
                         task_info = {"metadata": {"type": "api_event"}, "body": task_file.read_text()}
                    else:
                        task_info = self._parse_markdown_task(task_file)
                    
                    plan_content = self.generate_plan(task_info, task_file.name)
                    
                    approval_needed = "approval_required: Yes" in plan_content
                    dest_dir = self.pending_approval_path if approval_needed else self.plans_path
                    
                    plan_file_name = f"PLAN_{task_file.stem}.md"
                    plan_path = dest_dir / plan_file_name
                    
                    plan_path.write_text(plan_content, encoding='utf-8')
                    logger.info(f"Created plan: {plan_path.name}")
                    
                    # Move only if complete
                    shutil.move(str(task_file), str(self.done_path / task_file.name))
                    update_dashboard(self.vault_path)
                    
                    # For Gold Tier: We signal completion after initial planning
                    return "<promise>TASK_COMPLETE</promise>"
                except Exception as e:
                    logger.error(f"Error in Ralph processing: {e}")
                    raise

            # Use RalphLoop to handle the task
            success = ralph.run_until_complete(task_file.stem, run_processing)
            
            if not success:
                logger.critical(f"Ralph failed to process {task_file.name}. Moving to Rejected.")
                shutil.move(str(task_file), str(self.vault_path / "Rejected" / task_file.name))

    def run_loop(self, interval: int = 10):
        logger.info("Starting Gold Tier Reasoning Loop...")
        try:
            while True:
                self.process_tasks()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Reasoning Loop stopped by user.")

if __name__ == "__main__":
    pass
