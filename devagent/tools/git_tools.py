"""
Git tools — git diff, status, commit, and push operations.

All operations are safe subprocess calls with error handling.
"""

from __future__ import annotations

import subprocess
import os


def git_diff(project_root: str = ".", staged: bool = False) -> str:
    """Show git diff of current changes."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--staged")
    cmd.append("--stat")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15, cwd=project_root,
        )
        output = result.stdout.strip()
        if not output:
            return "[GIT] No changes detected."

        # Also get the full diff (capped)
        full = subprocess.run(
            ["git", "diff"] + (["--staged"] if staged else []),
            capture_output=True, text=True, timeout=15, cwd=project_root,
        )
        return f"STAT:\n{output}\n\nDIFF:\n{full.stdout[:3000]}"
    except FileNotFoundError:
        return "[ERROR] git not found on PATH"
    except subprocess.TimeoutExpired:
        return "[ERROR] git diff timed out"
    except Exception as exc:
        return f"[ERROR] git diff failed: {exc}"


def git_status(project_root: str = ".") -> str:
    """Show git status."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=10, cwd=project_root,
        )
        return result.stdout.strip() or "[GIT] Working tree clean."
    except Exception as exc:
        return f"[ERROR] git status failed: {exc}"


def git_commit(project_root: str, message: str) -> str:
    """Stage all and commit."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=project_root, capture_output=True, timeout=10)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True, timeout=15, cwd=project_root,
        )
        if result.returncode == 0:
            return f"[GIT] Committed: {message}"
        return f"[GIT] Commit failed: {result.stderr.strip()}"
    except Exception as exc:
        return f"[ERROR] git commit failed: {exc}"


def git_push(project_root: str = ".") -> str:
    """Push to remote origin."""
    try:
        result = subprocess.run(
            ["git", "push"], capture_output=True, text=True, timeout=30, cwd=project_root,
        )
        if result.returncode == 0:
            return "[GIT] Pushed successfully."
        return f"[GIT] Push failed: {result.stderr.strip()}"
    except Exception as exc:
        return f"[ERROR] git push failed: {exc}"


def is_git_repo(project_root: str = ".") -> bool:
    """Check if directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, cwd=project_root,
        )
        return result.returncode == 0
    except Exception:
        return False
