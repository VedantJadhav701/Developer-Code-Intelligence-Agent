"""
LLM integration layer — talks to Ollama via the Python SDK.
All prompts are kept SHORT to respect low-VRAM constraints.
"""

from __future__ import annotations

import ollama

# ── Configuration ────────────────────────────────────────────────────────────
MODEL = "qwen2.5:3b"
DEFAULT_OPTIONS = {
    "temperature": 0.2,
    "num_predict": 1024,
    "num_ctx": 2048,       # CRITICAL: limits KV cache to fit in low-RAM systems
    "top_p": 0.9,
}


def query(prompt: str, *, system: str = "", model: str = MODEL) -> str:
    """Send a prompt to Ollama and return the response text.

    Uses the ollama Python SDK (no subprocess).
    Falls back to empty string on error so the agent loop can continue.
    """
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options=DEFAULT_OPTIONS,
        )
        return response["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        print(f"[LLM ERROR] {exc}")
        return ""


def query_with_context(prompt: str, context: str, *, model: str = MODEL) -> str:
    """Query with additional context injected into the system message."""
    system = (
        "You are a senior Python developer. "
        "Be concise. Output ONLY what is asked — no markdown fences unless requested.\n\n"
        f"CONTEXT:\n{context[:2000]}"
    )
    return query(prompt, system=system, model=model)
