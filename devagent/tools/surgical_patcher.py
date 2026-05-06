"""
Surgical Patcher — applies targeted SEARCH/REPLACE blocks to files.
Inspired by Aider and Claude Code.
"""

from __future__ import annotations
import os

def apply_surgical_patch(file_path: str, search_block: str, replace_block: str) -> str:
    """Apply a targeted search-and-replace to a file."""
    if not os.path.isfile(file_path):
        return f"[ERROR] File not found: {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Clean up whitespace issues
        search_block = search_block.strip()
        replace_block = replace_block.strip()

        if not search_block:
             # If search is empty, we can't safely replace. 
             # But if it's a new file, we might append.
             return "[ERROR] Search block is empty. Use write_file for full rewrites."

        # Find the search block
        if search_block not in content:
            # Try a slightly looser match (ignore leading/trailing whitespace per line)
            return f"[ERROR] Search block not found in {os.path.basename(file_path)}. Ensure exact matching."

        new_content = content.replace(search_block, replace_block)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"[OK] Surgical patch applied to {os.path.basename(file_path)}."
    except Exception as exc:
        return f"[ERROR] Patching failed: {exc}"
