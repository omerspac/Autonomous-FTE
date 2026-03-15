import logging
import subprocess
from pathlib import Path
from typing import Optional
from subprocess import TimeoutExpired # Import TimeoutExpired

from AI_Employee.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

class PlanGenerationSkill(BaseSkill):
    """
    A skill responsible for generating structured plans using the Claude CLI
    configured for a Gemini backend.
    """

    @property
    def name(self) -> str:
        return "PlanGenerationSkill" # Now uses Claude CLI for plan generation

    def execute(self, input_text: str, context: Optional[dict] = None) -> Optional[str]:
        """
        Executes the plan generation skill using the Gemini CLI.

        Args:
            input_text: The content of the file to be summarized and planned.
            context: An optional dictionary. Can contain 'stricter_prompt_mode' (bool)
                     to use a more explicit prompt for plan structure.

        Returns:
            The structured plan as a string, or None if generation failed.
        """
        stricter_prompt_mode = context.get("stricter_prompt_mode", False) if context else False

        if stricter_prompt_mode:
            llm_prompt = (
                "The previous attempt to generate a plan did not follow the exact Markdown structure. "
                "Please regenerate the plan, ensuring it STRICTLY adheres to the following format:\n\n"
                "---\n"
                "created: <ISO timestamp>\n"
                "status: <pending|in_progress|completed|failed>\n"
                "---\n\n"
                "## Objective\n"
                "<brief objective>\n"
                "## Analysis\n"
                "<detailed analysis>\n"
                "## Action Plan\n"
                "<numbered list of actions with checkboxes>\n\n"
                f"Here is the original request: '''{input_text}'''"
            )
        else:
            llm_prompt = f"Summarize the following request and create a structured Plan with checkboxes for implementation: '''{input_text}'''"

        command = ["claude", "-p", llm_prompt]
        logger.info(f"Invoking Claude CLI (Gemini backend) for plan generation. Command: {' '.join(command[:2])} ...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', timeout=120)
            logger.debug(f"Gemini CLI stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"Gemini CLI stderr: {result.stderr.strip()}")
            return result.stdout.strip()
        except FileNotFoundError:
            logger.error("'claude' command not found. Please ensure the Claude CLI is installed and in your PATH.")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Claude CLI command failed with exit code {e.returncode}: {e.stderr.strip()}")
            return None
        except TimeoutExpired:
            logger.error(f"Claude CLI command timed out after 120 seconds.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling Claude CLI: {e}", exc_info=True)
            return None
