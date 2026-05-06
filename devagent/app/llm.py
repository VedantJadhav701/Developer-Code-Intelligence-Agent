"""
LLM integration layer — talks to Ollama via the Python SDK.
All prompts are kept SHORT to respect low-VRAM constraints.

Supports:
  - Configurable model + inference options
  - Latency tracking
  - Graceful fallback on errors
"""

from __future__ import annotations

import time
import ollama

from devagent.utils.config import MODELS, DEFAULT_INFERENCE_OPTIONS

# ── Configuration (mutable at runtime via CLI) ───────────────────────────────
MODEL = MODELS["primary"]
OPTIONS = DEFAULT_INFERENCE_OPTIONS.copy()


def set_model(model: str) -> None:
    """Override the active model."""
    global MODEL
    MODEL = model


def set_options(options: dict) -> None:
    """Override inference options."""
    global OPTIONS
    OPTIONS = {**DEFAULT_INFERENCE_OPTIONS, **options}


def query(prompt: str, *, system: str = "", model: str | None = None) -> str:
    """Send a prompt to Ollama and return the response text.

    Falls back to empty string on error so the agent loop can continue.
    Returns the response text.
    """
    use_model = model or MODEL
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        t0 = time.time()
        response = ollama.chat(
            model=use_model,
            messages=messages,
            options=OPTIONS,
        )
        elapsed = time.time() - t0
        text = response["message"]["content"].strip()

        # Track latency for metrics (stored globally for metrics collector)
        query._last_latency = elapsed
        query._last_prompt_chars = len(prompt)
        query._last_response_chars = len(text)

        return text
    except Exception as exc:  # noqa: BLE001
        print(f"[LLM ERROR] {exc}")
        query._last_latency = 0
        query._last_prompt_chars = len(prompt)
        query._last_response_chars = 0
        return ""

# Initialize tracking attributes
query._last_latency = 0.0
query._last_prompt_chars = 0
query._last_response_chars = 0


def query_with_context(prompt: str, context: str, *, model: str | None = None) -> str:
    """Query with additional context injected into the system message."""
    system = (
        "You are a senior Python developer. "
        "Be concise. Output ONLY what is asked — no markdown fences unless requested.\n\n"
        f"CONTEXT:\n{context[:2000]}"
    )
    return query(prompt, system=system, model=model)
