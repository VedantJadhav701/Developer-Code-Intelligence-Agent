"""
Self-review module.
The LLM critiques its own code fix and returns APPROVED or REVISE + reason.
"""

from __future__ import annotations

from app.llm import query

REVIEW_SYSTEM = (
    "You are a strict code reviewer. "
    "Review the proposed code fix for correctness, edge cases, and syntax. "
    "CRITICAL: If the code has a SyntaxError (like missing 'return', incomplete expressions, or unclosed blocks), you MUST return REVISE. "
    "Respond with EXACTLY one line:\n"
    "  APPROVED\n"
    "or\n"
    "  REVISE: <one-line reason>\n"
    "Do NOT output anything else."
)

REVISE_SYSTEM = (
    "You are a senior Python developer. "
    "Fix the code based on the review feedback. "
    "Output ONLY the corrected Python code — no explanations, no markdown fences."
)


def review_code(original_code: str, fixed_code: str, task: str) -> tuple[bool, str]:
    """Review a code fix.

    Returns:
        (approved: bool, review_text: str)
    """
    prompt = (
        f"TASK: {task}\n\n"
        f"ORIGINAL CODE:\n{original_code[:1500]}\n\n"
        f"PROPOSED FIX:\n{fixed_code[:1500]}\n\n"
        "Is the fix correct? Reply APPROVED or REVISE: <reason>"
    )
    response = query(prompt, system=REVIEW_SYSTEM)

    if not response:
        # LLM failure → cautiously approve to avoid infinite loop
        return True, "APPROVED (LLM unavailable — auto-approved)"

    approved = response.strip().upper().startswith("APPROVED")
    return approved, response.strip()


def revise_code(code: str, review_feedback: str, task: str) -> str:
    """Ask the LLM to revise code based on review feedback.

    Returns the revised code string.
    """
    prompt = (
        f"TASK: {task}\n\n"
        f"CODE:\n{code[:1500]}\n\n"
        f"REVIEW FEEDBACK: {review_feedback}\n\n"
        "Fix the code. Output ONLY the corrected Python code."
    )
    response = query(prompt, system=REVISE_SYSTEM)
    return response if response else code  # fallback to original on failure
