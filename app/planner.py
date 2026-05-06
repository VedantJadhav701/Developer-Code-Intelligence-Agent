"""
Planner Layer — interprets the task and generates a short action plan.

The planner is NOT the coder. It decides:
  1. Which files are likely relevant
  2. Which tools to use first
  3. A short execution strategy
"""

from __future__ import annotations

import re
from typing import Any

from app.llm import query


PLAN_PROMPT = """\
You are a coding task planner. Given a task and project files, create a SHORT plan.

TASK: {task}

PROJECT FILES:
{file_list}

Create a plan with exactly 3-5 steps. Each step should be ONE action.
Available actions: search_code, semantic_search, read_file, write_patch, run_tests, lint_code, git_diff

Reply in this EXACT format:
LIKELY_FILES: file1.py, file2.py
PLAN:
1. <action>: <target>
2. <action>: <target>
3. <action>: <target>
"""


def generate_plan(task: str, file_list: list[str]) -> dict[str, Any]:
    """Generate an execution plan for the given task."""
    files_str = "\n".join(f"  - {f}" for f in file_list[:30])
    prompt = PLAN_PROMPT.format(task=task, file_list=files_str)
    response = query(prompt)

    if not response:
        return _fallback_plan(task, file_list)
    return _parse_plan(response, task, file_list)


def _parse_plan(response: str, task: str, file_list: list[str]) -> dict[str, Any]:
    """Parse the LLM's plan response."""
    result: dict[str, Any] = {"likely_files": [], "steps": [], "raw_plan": response}

    files_match = re.search(r"LIKELY_FILES:\s*(.+)", response, re.IGNORECASE)
    if files_match:
        result["likely_files"] = [f.strip() for f in files_match.group(1).split(",") if f.strip()]

    step_pattern = re.compile(r"\d+\.\s*(\w+):\s*(.+)")
    for match in step_pattern.finditer(response):
        result["steps"].append((match.group(1).strip().lower(), match.group(2).strip()))

    if not result["steps"]:
        return _fallback_plan(task, file_list)
    return result


def _fallback_plan(task: str, file_list: list[str]) -> dict[str, Any]:
    """Generate a sensible fallback plan from the task description."""
    likely_files = [m.group(1) for m in re.finditer(r"(\w+\.py)", task)]
    steps = []
    if likely_files:
        steps.append(("read_file", likely_files[0]))
    else:
        keywords = [w for w in task.lower().split() if len(w) > 3 and w not in {"the", "that", "this", "with", "from"}]
        steps.append(("search_code", keywords[0] if keywords else "def"))
    steps.append(("run_tests", "."))
    return {"likely_files": likely_files, "steps": steps, "raw_plan": "Fallback plan."}
