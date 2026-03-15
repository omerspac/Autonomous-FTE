import abc
from pathlib import Path
from typing import Optional

class BaseSkill(abc.ABC):
    """
    Abstract base class for AI Agent Skills.
    All concrete skills must inherit from this class.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        A unique name for the skill.
        """
        pass

    @abc.abstractmethod
    def execute(self, input_text: str, context: Optional[dict] = None) -> Optional[str]:
        """
        Executes the skill's core logic.

        Args:
            input_text: The primary text input for the skill (e.g., a user request).
            context: An optional dictionary for additional context or parameters
                     needed by the skill (e.g., a stricter prompt flag).

        Returns:
            The string output of the skill, or None if the skill failed.
        """
        pass
