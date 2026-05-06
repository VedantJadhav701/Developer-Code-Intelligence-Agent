"""
Structured JSON logger — writes every agent step to logs/run.json.

Tracks: thoughts, actions, observations, reviews, test results,
latency, model info, and benchmark performance.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AgentLogger:
    """Append-only JSON logger that writes each step as an object in an array."""

    def __init__(self, log_dir: str = "logs"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._log_dir / "run.json"
        self._entries: list[dict[str, Any]] = []

    def log_step(
        self,
        step: int,
        thought: str,
        action: str,
        observation: str,
        review: str,
        test_result: str,
        status: str,
        *,
        latency: float = 0.0,
        model: str = "",
        patch_summary: str = "",
    ) -> None:
        """Log a complete agent iteration step."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "thought": thought,
            "action": action,
            "observation": observation[:2000],
            "review": review,
            "test_result": test_result[:2000],
            "latency": f"{latency:.2f}s" if latency else "",
            "model": model,
            "patch": patch_summary,
            "status": status,
        }
        self._entries.append(entry)
        self._flush()
        self._print_step(entry)

    def log_event(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Log a freeform event (startup, shutdown, error, etc.)."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **(data or {}),
        }
        self._entries.append(entry)
        self._flush()

    def _flush(self) -> None:
        """Write the full log array to disk."""
        try:
            self._log_file.write_text(
                json.dumps(self._entries, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[LOGGER ERROR] {exc}")

    @staticmethod
    def _print_step(entry: dict[str, Any]) -> None:
        """Pretty-print a step to the console."""
        print("\n" + "=" * 60)
        print(f"  STEP {entry['step']}  |  STATUS: {entry['status']}")
        print("=" * 60)
        print(f"  THOUGHT:     {entry['thought']}")
        print(f"  ACTION:      {entry['action']}")
        print(f"  OBSERVATION: {entry['observation'][:1500]}")
        if entry.get("review"):
            print(f"  REVIEW:      {entry['review']}")
        if entry.get("patch"):
            print(f"  PATCH:       {entry['patch'][:200]}")
        if entry.get("latency"):
            print(f"  LATENCY:     {entry['latency']}")
        print(f"  TEST RESULT: {entry['test_result'][:1500]}")
        print("=" * 60)
