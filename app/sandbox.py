"""
Sandbox Layer — copies project to isolated workspace before agent modifies anything.

Flow:
  Real Project → Sandbox Copy → Agent Modifies Sandbox → Run Tests → Show Diff → Optional Apply

Safety features:
  - Path validation (no escaping sandbox)
  - Restricted to supported file types
  - Diff preview before applying back
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from utils.config import IGNORE_DIRS, SUPPORTED_EXTENSIONS


class SandboxManager:
    """Manages an isolated sandbox workspace for safe agent operations."""

    def __init__(self, project_root: str, sandbox_dir: str | None = None):
        self.project_root = os.path.abspath(project_root)
        self.sandbox_dir = sandbox_dir or os.path.join(self.project_root, "sandbox_workspace")
        self._active = False

    def create(self) -> str:
        """Create a sandbox copy of the project. Returns sandbox path."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)

        def _ignore(directory: str, contents: list[str]) -> list[str]:
            ignored = []
            for item in contents:
                if item in IGNORE_DIRS or item == "sandbox_workspace":
                    ignored.append(item)
            return ignored

        shutil.copytree(self.project_root, self.sandbox_dir, ignore=_ignore)
        self._active = True
        print(f"[SANDBOX] Created at: {self.sandbox_dir}")
        return self.sandbox_dir

    def destroy(self) -> None:
        """Remove the sandbox."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
            self._active = False
            print("[SANDBOX] Destroyed.")

    def validate_path(self, path: str) -> bool:
        """Ensure a path is within the sandbox (no directory traversal)."""
        abs_path = os.path.abspath(path)
        return abs_path.startswith(os.path.abspath(self.sandbox_dir))

    def get_sandbox_path(self, relative_path: str) -> str:
        """Convert a relative path to its sandbox equivalent."""
        return os.path.join(self.sandbox_dir, relative_path)

    def apply_to_project(self) -> dict[str, Any]:
        """Copy sandbox changes back to the real project.

        Returns a summary of what was applied.
        """
        if not self._active:
            return {"status": "error", "message": "No active sandbox"}

        applied: list[str] = []
        errors: list[str] = []

        for root, dirs, files in os.walk(self.sandbox_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for f in files:
                sandbox_file = os.path.join(root, f)
                rel_path = os.path.relpath(sandbox_file, self.sandbox_dir)
                real_file = os.path.join(self.project_root, rel_path)

                try:
                    # Only apply supported file types
                    if Path(f).suffix in SUPPORTED_EXTENSIONS or f in {"conftest.py"}:
                        sandbox_content = Path(sandbox_file).read_text(encoding="utf-8", errors="replace")
                        real_content = ""
                        if os.path.exists(real_file):
                            real_content = Path(real_file).read_text(encoding="utf-8", errors="replace")

                        if sandbox_content != real_content:
                            Path(real_file).parent.mkdir(parents=True, exist_ok=True)
                            Path(real_file).write_text(sandbox_content, encoding="utf-8")
                            applied.append(rel_path)
                except Exception as exc:
                    errors.append(f"{rel_path}: {exc}")

        return {
            "status": "success" if not errors else "partial",
            "applied": applied,
            "errors": errors,
        }

    @property
    def is_active(self) -> bool:
        return self._active and os.path.isdir(self.sandbox_dir)
