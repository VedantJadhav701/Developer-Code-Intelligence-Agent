"""
File operations — read and write with safety guards.
"""

from __future__ import annotations

import os
from pathlib import Path


def read_file(path: str) -> str:
    """Read a file and return its contents.
    
    Supports range: path/to/file.py:L10-L50
    Returns an error string on failure (never raises).
    """
    try:
        # Check for line range
        line_range = None
        if ":L" in path:
            parts = path.split(":L")
            path = parts[0]
            line_range = parts[1]

        p = Path(path)
        if not p.exists():
            return f"[ERROR] File not found: {path}"
        if not p.is_file():
            return f"[ERROR] Not a file: {path}"
        
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        
        if line_range:
            try:
                start, end = map(int, line_range.split("-"))
                lines = lines[start-1:end]
                header = f"### {path} (Lines {start}-{end}) ###\n"
                return header + "\n".join(lines)
            except ValueError:
                return f"[ERROR] Invalid line range: {line_range}"

        content = "\n".join(lines)
        return content[:10000]  # cap to protect LLM context
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] Could not read {path}: {exc}"


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed.

    Returns a status message.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[OK] Written {len(content)} chars to {path}"
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] Could not write {path}: {exc}"


def list_files(directory: str, extension: str = ".py") -> list[str]:
    """List files with given extension under a directory."""
    results = []
    try:
        for root, _dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(extension):
                    results.append(os.path.join(root, f))
    except Exception:  # noqa: BLE001
        pass
    return results
