"""
Shared state object for the agent.
Single source of truth passed through every step of the ReAct loop.

Implements both short-term memory (runtime state) and slots for
long-term memory integration.
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
    max_steps: int = 5
    status: str = "pending"  # pending | running | success | fail

    # --- file context ---
    current_file: str = ""
    current_file_content: str = ""

    # --- execution results ---
    test_output: str = ""
    test_exit_code: int = -1
    lint_output: str = ""

    # --- history (short-term memory) ---
    history: list[dict[str, Any]] = field(default_factory=list)

    # --- last LLM outputs ---
    last_thought: str = ""
    last_action: str = ""
    last_observation: str = ""
    last_code_fix: str = ""
    last_review: str = ""

    # --- attempts counter ---
    attempts: int = 0

    # --- retrieval context ---
    retrieved_chunks: list[Any] = field(default_factory=list)

    # --- planner output ---
    plan: dict[str, Any] = field(default_factory=dict)

    # --- patch tracking ---
    patches_applied: list[dict[str, Any]] = field(default_factory=list)

    # --- sandbox ---
    sandbox_active: bool = False
    working_root: str = ""  # actual root being modified (sandbox or real)

    # --- thoughts / observations for memory ---
    thoughts: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

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
            "patches_applied": len(self.patches_applied),
            "sandbox_active": self.sandbox_active,
        }

    def clone(self) -> "AgentState":
        """Deep-copy for safe rollback."""
        return copy.deepcopy(self)
