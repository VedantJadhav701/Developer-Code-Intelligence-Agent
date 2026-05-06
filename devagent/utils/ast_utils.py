"""
AST Utilities for DevAgent — Hierarchical mapping and structural analysis.

Helps the agent understand file structure without reading the whole file.
"""

import ast
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CodeSymbol:
    name: str
    type: str  # 'function', 'class', 'method'
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    children: List['CodeSymbol'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

def get_file_structure(file_path: str) -> List[CodeSymbol]:
    """Parse a Python file and return a hierarchical list of symbols."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        tree = ast.parse(content)
        symbols = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbol = _parse_node(node)
                if symbol:
                    symbols.append(symbol)
        
        return symbols
    except Exception:
        return []

def _parse_node(node: ast.AST) -> Optional[CodeSymbol]:
    """Recursively parse an AST node into a CodeSymbol."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        symbol = CodeSymbol(
            name=node.name,
            type="function",
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring=ast.get_docstring(node)
        )
        return symbol
    
    elif isinstance(node, ast.ClassDef):
        symbol = CodeSymbol(
            name=node.name,
            type="class",
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring=ast.get_docstring(node)
        )
        # Parse methods
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = _parse_node(child)
                if method:
                    method.type = "method"
                    symbol.children.append(method)
        return symbol
    
    return None

def format_structure_summary(symbols: List[CodeSymbol], indent: int = 0) -> str:
    """Format symbols into a readable tree summary."""
    lines = []
    for s in symbols:
        prefix = "  " * indent
        line = f"{prefix}- {s.type.capitalize()}: {s.name} (L{s.start_line}-{s.end_line})"
        lines.append(line)
        if s.children:
            lines.append(format_structure_summary(s.children, indent + 1))
    return "\n".join(lines)
