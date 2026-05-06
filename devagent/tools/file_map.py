"""
File Map Tool — Provides a structural overview of a file using AST.
"""

from __future__ import annotations
import os
from devagent.utils.ast_utils import get_file_structure, format_structure_summary

def get_file_map(file_path: str, root_dir: str = ".") -> str:
    """Return a hierarchical map of functions and classes in the file."""
    full_path = os.path.join(root_dir, file_path)
    if not os.path.exists(full_path):
        return f"Error: File {file_path} not found."
    
    symbols = get_file_structure(full_path)
    if not symbols:
        return f"Could not parse structure for {file_path} (possibly empty or non-python)."
    
    summary = format_structure_summary(symbols)
    header = f"### Structure of {file_path} ###\n"
    return header + summary + "\n\nUse read_file with specific line ranges to see the implementation."
