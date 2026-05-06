"""
Semantic search tool — uses FAISS + sentence-transformers for code retrieval.

Falls back to keyword search if dependencies aren't installed.
"""

from __future__ import annotations

from devagent.app.memory import SemanticIndex, CodeChunk, chunk_project


# Module-level singleton index
_index: SemanticIndex | None = None


def build_index(project_root: str) -> bool:
    """Build or rebuild the semantic index for a project.

    Returns True if semantic search is available.
    """
    global _index
    _index = SemanticIndex()
    chunks = chunk_project(project_root)
    return _index.build(chunks)


def semantic_search(query: str, project_root: str = ".", top_k: int = 5) -> str:
    """Search code semantically using embeddings.

    Falls back to keyword search if FAISS is not available.
    Returns formatted results string.
    """
    global _index

    # Auto-build index if not ready
    if _index is None:
        build_index(project_root)

    if _index is None:
        return "[ERROR] Could not build semantic index"

    results = _index.search(query, top_k=top_k)

    if not results:
        return f"No semantic matches found for: {query}"

    output_lines = [f"Found {len(results)} semantic matches for '{query}':\n"]
    for i, chunk in enumerate(results, 1):
        header = f"--- [{i}] {chunk.file_path} (L{chunk.start_line}-{chunk.end_line}) ---"
        content = chunk.content[:500]
        output_lines.append(f"{header}\n{content}\n")

    return "\n".join(output_lines)[:3000]


def get_relevant_chunks(query: str, top_k: int = 5) -> list[CodeChunk]:
    """Get raw chunk objects for internal use."""
    if _index is None:
        return []
    return _index.search(query, top_k=top_k)
