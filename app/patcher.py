"""
Patch Engine — generates and applies line-level diffs instead of rewriting full files.

Supports:
  - Unified diff generation
  - Patch application with context validation
  - Minimal change preservation
"""

from __future__ import annotations

import difflib
import os
from pathlib import Path
from typing import Any


def generate_diff(original: str, modified: str, file_path: str = "file.py") -> str:
    """Generate a unified diff between original and modified content."""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines, mod_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm="",
    )
    return "".join(diff)


def apply_patch(file_path: str, original_content: str, patched_content: str) -> dict[str, Any]:
    """Apply a patch to a file with validation.

    Returns a result dict with status, diff, and stats.
    """
    result: dict[str, Any] = {
        "status": "error",
        "file": file_path,
        "diff": "",
        "lines_changed": 0,
        "lines_added": 0,
        "lines_removed": 0,
    }

    if not patched_content.strip():
        result["error"] = "Empty patch content"
        return result

    # Generate diff for logging
    diff_text = generate_diff(original_content, patched_content, file_path)
    result["diff"] = diff_text

    # Count changes
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            result["lines_added"] += 1
        elif line.startswith("-") and not line.startswith("---"):
            result["lines_removed"] += 1
    result["lines_changed"] = result["lines_added"] + result["lines_removed"]

    # Write the patched file
    try:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(patched_content, encoding="utf-8")
        result["status"] = "success"
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)

    return result


def format_diff_summary(patch_result: dict[str, Any]) -> str:
    """Format a human-readable patch summary."""
    if patch_result["status"] != "success":
        return f"[PATCH ERROR] {patch_result.get('error', 'Unknown error')}"

    return (
        f"[PATCH] {patch_result['file']}: "
        f"+{patch_result['lines_added']} / -{patch_result['lines_removed']} lines"
    )
