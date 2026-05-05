"""
Shared state object for the agent.
Single source of truth passed through every step of the ReAct loop.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """Mutable state shared across all agent components."""

    # --- task definition ---
    task: str = ""
    project_root: str = "."

    # --- iteration tracking ---
    current_step: int = 0
    max_steps: int = 3
    status: str = "pending"  # pending | running | success | fail

    # --- file context ---
    current_file: str = ""
    current_file_content: str = ""

    # --- execution results ---
    test_output: str = ""
    test_exit_code: int = -1
    lint_output: str = ""

    # --- history ---
    history: list[dict[str, Any]] = field(default_factory=list)

    # --- last LLM outputs ---
    last_thought: str = ""
    last_action: str = ""
    last_observation: str = ""
    last_code_fix: str = ""
    last_review: str = ""

    # --- attempts counter ---
    attempts: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serialisable snapshot of the current state."""
        return {
            "task": self.task,
            "project_root": self.project_root,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "status": self.status,
            "current_file": self.current_file,
            "test_output": self.test_output[:500] if self.test_output else "",
            "test_exit_code": self.test_exit_code,
            "attempts": self.attempts,
            "history_length": len(self.history),
        }

    def clone(self) -> "AgentState":
        """Deep-copy for safe rollback."""
        return copy.deepcopy(self)
