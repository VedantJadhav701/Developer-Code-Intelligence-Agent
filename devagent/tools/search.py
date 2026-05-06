"""
Code search tool — uses ripgrep (rg) with fallback to findstr on Windows.
"""

from __future__ import annotations

import os
import shutil
import subprocess


def search_code(query: str, search_path: str = ".") -> str:
    """Search codebase for a pattern using ripgrep.

    Falls back to findstr on Windows if rg is not installed.
    Returns the raw output string (capped at 3000 chars).
    """
    rg_bin = shutil.which("rg")

    if rg_bin:
        cmd = [
            rg_bin,
            "--no-heading",
            "--line-number",
            "--max-count", "20",
            "--type", "py",
            query,
            search_path,
        ]
    elif os.name == "nt":
        # Windows fallback
        cmd = [
            "findstr",
            "/S", "/N", "/I",
            query,
            os.path.join(search_path, "*.py"),
        ]
    else:
        cmd = [
            "grep",
            "-rn",
            "--include=*.py",
            "-m", "20",
            query,
            search_path,
        ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=search_path if rg_bin else None,
        )
        output = result.stdout.strip()
        if not output:
            return f"No results found for: {query}"
        return output[:3000]
    except FileNotFoundError:
        return f"[ERROR] Search tool not found. Install ripgrep: https://github.com/BurntSushi/ripgrep"
    except subprocess.TimeoutExpired:
        return f"[ERROR] Search timed out for query: {query}"
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] Search failed: {exc}"
