"""
Memory Layer — Short-term runtime state + Long-term FAISS-backed semantic retrieval.

Implements:
  - Semantic code chunking
  - Sentence-transformer embeddings
  - FAISS vector index for Top-K retrieval
  - Compressed memory summaries
  - Context pruning for low-VRAM operation

Falls back gracefully if sentence-transformers or faiss are not installed.
"""

from __future__ import annotations

import os
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from utils.config import (
    SUPPORTED_EXTENSIONS, IGNORE_DIRS, MAX_FILE_SIZE_BYTES,
    MAX_CHUNK_CHARS, TOP_K_RETRIEVAL,
)

# ── Lazy imports for optional heavy deps ──────────────────────────────────────

_FAISS_AVAILABLE = False
_TRANSFORMERS_AVAILABLE = False
_np = None
_faiss = None
_SentenceTransformer = None


def _load_deps() -> None:
    """Lazy-load heavy dependencies only when needed."""
    global _FAISS_AVAILABLE, _TRANSFORMERS_AVAILABLE, _np, _faiss, _SentenceTransformer
    try:
        import numpy as np
        _np = np
    except ImportError:
        return

    try:
        import faiss
        _faiss = faiss
        _FAISS_AVAILABLE = True
    except ImportError:
        pass

    try:
        from sentence_transformers import SentenceTransformer
        _SentenceTransformer = SentenceTransformer
        _TRANSFORMERS_AVAILABLE = True
    except ImportError:
        pass


# ── Code Chunking ─────────────────────────────────────────────────────────────

@dataclass
class CodeChunk:
    """A chunk of source code with metadata."""
    file_path: str
    start_line: int
    end_line: int
    content: str
    language: str = "python"
    chunk_hash: str = ""

    def __post_init__(self) -> None:
        if not self.chunk_hash:
            self.chunk_hash = hashlib.md5(
                self.content.encode("utf-8", errors="replace")
            ).hexdigest()[:12]


def chunk_file(file_path: str, max_chars: int = MAX_CHUNK_CHARS) -> list[CodeChunk]:
    """Split a source file into semantic chunks.

    Chunks on function/class boundaries when possible, falls back to
    fixed-size splitting.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    if len(content) > MAX_FILE_SIZE_BYTES:
        return []  # Skip very large files

    ext = Path(file_path).suffix
    lines = content.splitlines(keepends=True)
    chunks: list[CodeChunk] = []
    current_lines: list[str] = []
    current_start = 1

    def _flush(end: int) -> None:
        text = "".join(current_lines).strip()
        if text:
            chunks.append(CodeChunk(
                file_path=file_path,
                start_line=current_start,
                end_line=end,
                content=text[:max_chars],
                language=ext.lstrip("."),
            ))

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Split on function/class boundaries (Python-aware)
        is_boundary = (
            stripped.startswith("def ") or
            stripped.startswith("class ") or
            stripped.startswith("async def ")
        )

        if is_boundary and current_lines:
            _flush(i - 1)
            current_lines = [line]
            current_start = i
        else:
            current_lines.append(line)

        # Force split if chunk gets too large
        if len("".join(current_lines)) > max_chars:
            _flush(i)
            current_lines = []
            current_start = i + 1

    # Flush remaining
    if current_lines:
        _flush(len(lines))

    return chunks


def chunk_project(project_root: str) -> list[CodeChunk]:
    """Recursively chunk all source files in a project."""
    all_chunks: list[CodeChunk] = []
    for root, dirs, files in os.walk(project_root):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if Path(f).suffix in SUPPORTED_EXTENSIONS:
                full_path = os.path.join(root, f)
                all_chunks.extend(chunk_file(full_path))
    return all_chunks


# ── FAISS Vector Store ────────────────────────────────────────────────────────

class SemanticIndex:
    """FAISS-backed semantic search index for code chunks.

    Falls back to keyword matching if FAISS or sentence-transformers
    are not available.
    """

    EMBED_MODEL = "all-MiniLM-L6-v2"  # 80 MB, fast, good quality

    def __init__(self) -> None:
        _load_deps()
        self.chunks: list[CodeChunk] = []
        self._index = None
        self._embedder = None
        self._dimension = 0
        self._ready = False

    def build(self, chunks: list[CodeChunk]) -> bool:
        """Build the FAISS index from code chunks.

        Returns True if semantic index was built, False if falling back.
        """
        self.chunks = chunks
        if not chunks:
            return False

        if not (_FAISS_AVAILABLE and _TRANSFORMERS_AVAILABLE):
            print("[MEMORY] FAISS/sentence-transformers not available — using keyword fallback")
            return False

        try:
            print(f"[MEMORY] Building semantic index over {len(chunks)} chunks...")
            self._embedder = _SentenceTransformer(self.EMBED_MODEL)
            texts = [c.content for c in chunks]
            embeddings = self._embedder.encode(texts, show_progress_bar=False)
            embeddings = _np.array(embeddings, dtype="float32")

            self._dimension = embeddings.shape[1]
            self._index = _faiss.IndexFlatIP(self._dimension)  # Inner product
            _faiss.normalize_L2(embeddings)
            self._index.add(embeddings)

            self._ready = True
            print(f"[MEMORY] Semantic index ready ({self._dimension}d, {len(chunks)} chunks)")
            return True
        except Exception as exc:
            print(f"[MEMORY] Index build failed: {exc}")
            self._ready = False
            return False

    def search(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> list[CodeChunk]:
        """Retrieve the most relevant chunks for a query."""
        if not self.chunks:
            return []

        if self._ready and self._embedder and self._index:
            return self._semantic_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)

    def _semantic_search(self, query: str, top_k: int) -> list[CodeChunk]:
        """FAISS-powered semantic search."""
        try:
            q_embed = self._embedder.encode([query])
            q_embed = _np.array(q_embed, dtype="float32")
            _faiss.normalize_L2(q_embed)

            k = min(top_k, len(self.chunks))
            scores, indices = self._index.search(q_embed, k)

            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.chunks):
                    results.append(self.chunks[idx])
            return results
        except Exception as exc:
            print(f"[MEMORY] Semantic search failed: {exc}")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> list[CodeChunk]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        scored = []
        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            score = content_lower.count(query_lower)
            # Boost exact matches in function/class names
            for line in chunk.content.splitlines()[:3]:
                if query_lower in line.lower():
                    score += 5
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]


# ── Working Memory (Short-Term) ──────────────────────────────────────────────

@dataclass
class WorkingMemory:
    """Short-term memory for the current agent run.

    Stores retrieved chunks, compressed summaries, and recent
    observations for context assembly.
    """

    retrieved_chunks: list[CodeChunk] = field(default_factory=list)
    summaries: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    thoughts: list[str] = field(default_factory=list)

    def add_retrieval(self, chunks: list[CodeChunk]) -> None:
        """Add retrieved chunks, deduplicating by hash."""
        seen = {c.chunk_hash for c in self.retrieved_chunks}
        for c in chunks:
            if c.chunk_hash not in seen:
                self.retrieved_chunks.append(c)
                seen.add(c.chunk_hash)

    def get_context(self, max_chars: int = 3000) -> str:
        """Assemble compressed context from retrieved chunks."""
        parts: list[str] = []
        total = 0

        for chunk in self.retrieved_chunks:
            header = f"# {chunk.file_path} (L{chunk.start_line}-{chunk.end_line})"
            block = f"{header}\n{chunk.content}\n"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)

        return "\n".join(parts)

    def add_summary(self, summary: str) -> None:
        """Store a compressed summary."""
        self.summaries.append(summary[:500])
        # Keep only last 10 summaries
        if len(self.summaries) > 10:
            self.summaries = self.summaries[-10:]

    def clear(self) -> None:
        """Reset working memory."""
        self.retrieved_chunks.clear()
        self.summaries.clear()
        self.observations.clear()
        self.thoughts.clear()
