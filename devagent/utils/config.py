"""
Centralized configuration — single source of truth for all runtime settings.

Supports CLI overrides, model configuration, and path management.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


# ── Model Presets ─────────────────────────────────────────────────────────────

MODELS = {
    "primary": "qwen2.5-coder:3b",
    "fallback_1": "qwen2.5:3b",
    "fallback_2": "phi3:mini",
}

DEFAULT_INFERENCE_OPTIONS: dict[str, Any] = {
    "temperature": 0.1,
    "top_p": 0.9,
    "num_ctx": 4096,
    "num_predict": 2048,
}

# ── File / Path Constants ─────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".go", ".rs", ".java", ".rb"}
IGNORE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", "node_modules",
    ".venv", "venv", "env", ".mypy_cache", ".tox", "dist", "build",
    ".eggs", "*.egg-info", ".idea", ".vscode", "sandbox_workspace",
}
MAX_FILE_SIZE_BYTES = 100_000  # 100 KB — skip huge files
MAX_CHUNK_CHARS = 1500         # For retrieval chunks
TOP_K_RETRIEVAL = 5            # Number of retrieved chunks per query
MAX_CONTEXT_TOKENS = 3000      # Approximate token budget for context window


@dataclass
class AgentConfig:
    """Runtime configuration assembled from CLI args + defaults."""

    # ── Core settings ──
    task: str = ""
    project_root: str = "."
    model: str = MODELS["primary"]
    max_steps: int = 5
    verbose: bool = False

    # ── Feature flags ──
    sandbox: bool = True
    dry_run: bool = False
    auto_commit: bool = False
    auto_push: bool = False       # DISABLED by default — safety first
    benchmark: bool = False

    # ── Inference ──
    inference_options: dict[str, Any] = field(
        default_factory=lambda: DEFAULT_INFERENCE_OPTIONS.copy()
    )

    # ── Paths (derived) ──
    log_dir: str = ""
    sandbox_dir: str = ""

    def _load_global_config(self) -> None:
        """Load overrides from ~/.devagent/config.json"""
        import json
        config_path = os.path.expanduser("~/.devagent/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if hasattr(self, k):
                            setattr(self, k, v)
            except Exception:
                pass

    def __post_init__(self) -> None:
        self.project_root = os.path.abspath(self.project_root)
        self._load_global_config()
        if not self.log_dir:
            self.log_dir = os.path.join(self.project_root, "logs")
        if not self.sandbox_dir:
            self.sandbox_dir = os.path.join(self.project_root, "sandbox_workspace")

    @classmethod
    def from_cli(cls, args: Any) -> "AgentConfig":
        """Build config from argparse namespace."""
        cfg = cls(
            task=getattr(args, "task", ""),
            project_root=getattr(args, "root", "."),
            model=getattr(args, "model", MODELS["primary"]),
            max_steps=getattr(args, "max_steps", 5),
            verbose=getattr(args, "verbose", False),
            sandbox=getattr(args, "sandbox", True),
            dry_run=getattr(args, "dry_run", False),
            auto_commit=getattr(args, "auto_commit", False),
            auto_push=getattr(args, "auto_push", False),
            benchmark=getattr(args, "benchmark", False),
        )
        return cfg

    def snapshot(self) -> dict[str, Any]:
        """JSON-serialisable snapshot for logging."""
        return {
            "model": self.model,
            "max_steps": self.max_steps,
            "sandbox": self.sandbox,
            "auto_commit": self.auto_commit,
            "auto_push": self.auto_push,
            "inference_options": self.inference_options,
        }
