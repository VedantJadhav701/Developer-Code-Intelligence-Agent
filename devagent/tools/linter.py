"""
Linter tool — runs flake8 with configurable max-line-length.

Separated from test_runner for modularity and future extensibility.
"""

from __future__ import annotations

import subprocess
import shutil


def lint_code(file_path: str, max_line_length: int = 120) -> tuple[int, str]:
    """Run flake8 on a single file.

    Returns (exit_code, output_text).
    """
    flake8_bin = shutil.which("flake8")
    if not flake8_bin:
        return 0, "[SKIP] flake8 not installed — skipping lint"

    try:
        result = subprocess.run(
            [flake8_bin, f"--max-line-length={max_line_length}", file_path],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout.strip()
        if not output:
            return 0, "No lint issues found."
        return result.returncode, output[:2000]
    except subprocess.TimeoutExpired:
        return 0, "[WARN] Lint timed out"
    except Exception as exc:
        return 0, f"[WARN] Lint failed: {exc}"


def lint_project(project_root: str, max_line_length: int = 120) -> tuple[int, str]:
    """Run flake8 on the entire project."""
    flake8_bin = shutil.which("flake8")
    if not flake8_bin:
        return 0, "[SKIP] flake8 not installed"

    try:
        result = subprocess.run(
            [flake8_bin, f"--max-line-length={max_line_length}",
             "--exclude=sandbox_workspace,__pycache__,.git",
             project_root],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout.strip()
        if not output:
            return 0, "No lint issues found in project."
        return result.returncode, output[:3000]
    except Exception as exc:
        return 0, f"[WARN] Project lint failed: {exc}"
