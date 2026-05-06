"""
Metrics collector — tracks latency, retries, token estimates, and benchmark results.

All metrics are stored in-memory and flushed to disk on demand.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StepMetrics:
    """Metrics for a single agent step."""
    step: int = 0
    action: str = ""
    latency_s: float = 0.0
    prompt_chars: int = 0
    response_chars: int = 0
    estimated_tokens: int = 0  # rough: chars / 4
    status: str = ""


@dataclass
class RunMetrics:
    """Aggregated metrics for an entire agent run."""

    model: str = ""
    task: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    total_steps: int = 0
    retries: int = 0
    patch_rejections: int = 0
    successes: int = 0
    failures: int = 0
    total_latency_s: float = 0.0
    total_estimated_tokens: int = 0
    steps: list[StepMetrics] = field(default_factory=list)

    # ── Recording ─────────────────────────────────────────────────────────

    def record_step(
        self,
        step: int,
        action: str,
        latency_s: float,
        prompt_chars: int,
        response_chars: int,
        status: str,
    ) -> StepMetrics:
        """Record metrics for a single step."""
        estimated_tokens = (prompt_chars + response_chars) // 4
        sm = StepMetrics(
            step=step,
            action=action,
            latency_s=round(latency_s, 3),
            prompt_chars=prompt_chars,
            response_chars=response_chars,
            estimated_tokens=estimated_tokens,
            status=status,
        )
        self.steps.append(sm)
        self.total_steps += 1
        self.total_latency_s += latency_s
        self.total_estimated_tokens += estimated_tokens
        if status == "success":
            self.successes += 1
        elif status == "fail":
            self.failures += 1
        return sm

    def finalize(self) -> None:
        """Mark the run as complete."""
        self.end_time = time.time()

    # ── Reporting ─────────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Return a JSON-serialisable summary."""
        elapsed = (self.end_time or time.time()) - self.start_time
        return {
            "model": self.model,
            "task": self.task[:100],
            "total_steps": self.total_steps,
            "retries": self.retries,
            "patch_rejections": self.patch_rejections,
            "successes": self.successes,
            "failures": self.failures,
            "total_latency_s": round(self.total_latency_s, 2),
            "wall_time_s": round(elapsed, 2),
            "total_estimated_tokens": self.total_estimated_tokens,
            "avg_step_latency_s": round(
                self.total_latency_s / max(self.total_steps, 1), 2
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def save(self, log_dir: str) -> str:
        """Save metrics to disk."""
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
        out_file = path / "metrics.json"
        try:
            out_file.write_text(
                json.dumps(self.summary(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return str(out_file)
        except Exception as exc:
            print(f"[METRICS ERROR] {exc}")
            return ""


class Timer:
    """Simple context-manager timer."""

    def __init__(self) -> None:
        self.start = 0.0
        self.elapsed = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.time()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed = time.time() - self.start
