"""
Core ReAct Agent — the main execution engine.

Implements the strict loop:
  THOUGHT → ACTION → OBSERVATION → GENERATE FIX → SELF-REVIEW → TEST
with up to max_steps iterations.
"""

from __future__ import annotations

import re
import os
from typing import Any

from app.llm import query, query_with_context
from app.reviewer import review_code, revise_code
from app.state import AgentState
from tools.search import search_code
from tools.file_ops import read_file, write_file, list_files
from tools.test_runner import run_tests, lint_code
from utils.logger import AgentLogger


# ── Prompt templates (kept SHORT for phi3:mini) ─────────────────────────────

THOUGHT_PROMPT = """\
You are a coding agent. Your task:
{task}

Project root: {project_root}
Current step: {step}/{max_steps}
Previous attempts: {attempts}

{history_summary}

Decide the SINGLE next action. Choose ONE:
- search_code: <keyword>  (example: search_code: divide   -- use a SHORT keyword, NOT a file path)
- read_file: <relative_path>  (example: read_file: calculator.py)
- write_file: <relative_path>  (example: write_file: calculator.py)
- run_tests  (no argument needed)

IMPORTANT: For search_code, use a SHORT keyword like "divide" or "def add", NOT a file path.
IMPORTANT: For read_file, use a RELATIVE path like "calculator.py", NOT an absolute path.

Reply in this EXACT format (two lines only):
THOUGHT: <your brief reasoning>
ACTION: <tool_name>: <argument>
"""

FIX_PROMPT = """\
TASK: {task}

FILE: {file_path}
CURRENT CODE:
{file_content}

{error_context}

RULES:
1. Output the COMPLETE corrected file content
2. ONLY fix what is needed — do NOT add new functions, classes, or imports
3. Keep the SAME file structure and function signatures
4. If a test expects a specific error message, use EXACTLY that message
5. Output ONLY Python code — no markdown fences, no explanations, no comments about the fix
"""

EXTRACT_ACTION_PATTERN = re.compile(
    r"ACTION:\s*(search_code|read_file|write_file|run_tests)\s*:?\s*(.*)",
    re.IGNORECASE,
)


class Agent:
    """ReAct agent with self-review loop."""

    def __init__(self, task: str, project_root: str = ".", max_steps: int = 3):
        self.state = AgentState(
            task=task,
            project_root=os.path.abspath(project_root),
            max_steps=max_steps,
        )
        self.logger = AgentLogger(log_dir=os.path.join(project_root, "logs"))

    # ── Public entry point ───────────────────────────────────────────────

    def run(self) -> AgentState:
        """Execute the full agent loop. Returns final state."""
        self.state.status = "running"
        self.logger.log_event("agent_start", {"task": self.state.task})

        print("\n" + "=" * 60)
        print("  DEVELOPER CODE INTELLIGENCE AGENT")
        print(f"  Task: {self.state.task}")
        print(f"  Project: {self.state.project_root}")
        print(f"  Max iterations: {self.state.max_steps}")
        print("=" * 60)

        for step in range(1, self.state.max_steps + 1):
            self.state.current_step = step
            self.state.attempts += 1

            print(f"\n{'-' * 40}")
            print(f"  ITERATION {step}/{self.state.max_steps}")
            print(f"{'-' * 40}")

            step_result = self._run_iteration(step)

            if step_result == "success":
                self.state.status = "success"
                self.logger.log_event("agent_complete", {"status": "success", "steps": step})
                print("\n[OK]  AGENT COMPLETED SUCCESSFULLY")
                return self.state

        # exhausted all iterations
        self.state.status = "fail"
        self.logger.log_event("agent_complete", {"status": "fail", "steps": self.state.max_steps})
        print("\n[FAIL]  AGENT FAILED -- max iterations reached")
        return self.state

    # ── Single iteration ─────────────────────────────────────────────────

    def _run_iteration(self, step: int) -> str:
        """Run one full ReAct iteration. Returns 'success' or 'continue'."""

        # STEP 1 — THOUGHT + ACTION (combined LLM call)
        thought, action_name, action_arg = self._think(step)
        self.state.last_thought = thought
        self.state.last_action = f"{action_name}: {action_arg}"

        # STEP 2 — EXECUTE ACTION → OBSERVATION
        observation = self._execute_action(action_name, action_arg)
        self.state.last_observation = observation

        # STEP 3 — GENERATE FIX (if we have a file in context)
        code_fix = ""
        review_text = ""
        if self.state.current_file and action_name in ("read_file", "search_code"):
            code_fix = self._generate_fix()
            self.state.last_code_fix = code_fix

            # STEP 4 — SELF-REVIEW
            if code_fix:
                code_fix, review_text = self._self_review(code_fix)
                self.state.last_review = review_text

                # Write the approved fix
                write_result = write_file(self.state.current_file, code_fix)
                observation += f"\n{write_result}"

        # STEP 5 — RUN TESTS
        test_exit, test_output = run_tests(self.state.project_root)
        self.state.test_exit_code = test_exit
        self.state.test_output = test_output

        status = "success" if test_exit == 0 else "fail"

        # Log this step
        self.logger.log_step(
            step=step,
            thought=thought,
            action=f"{action_name}: {action_arg}",
            observation=observation,
            review=review_text,
            test_result=test_output,
            status=status,
        )

        # Store in history
        self.state.history.append({
            "step": step,
            "thought": thought,
            "action": action_name,
            "action_arg": action_arg,
            "observation": observation[:500],
            "review": review_text,
            "test_status": status,
        })

        return status

    # ── THOUGHT phase ────────────────────────────────────────────────────

    def _think(self, step: int) -> tuple[str, str, str]:
        """Ask the LLM to decide the next action.

        Returns (thought, action_name, action_arg).
        """
        history_summary = self._format_history()

        prompt = THOUGHT_PROMPT.format(
            task=self.state.task,
            project_root=self.state.project_root,
            step=step,
            max_steps=self.state.max_steps,
            attempts=self.state.attempts,
            history_summary=history_summary,
        )

        response = query(prompt)
        thought, action_name, action_arg = self._parse_thought_response(response)

        # Fallback logic
        if not action_name:
            if not self.state.current_file:
                # Try to extract a filename from the task
                file_hint = self._extract_filename_from_task()
                if file_hint and step > 1:
                    action_name = "read_file"
                    action_arg = file_hint
                    thought = f"Falling back to reading {file_hint} directly."
                else:
                    action_name = "search_code"
                    # Extract a keyword from the task, not the whole thing
                    action_arg = self._extract_search_keyword()
                    thought = "Falling back to keyword search."
            else:
                action_name = "run_tests"
                action_arg = ""
                thought = "Falling back to run_tests."

        # Sanitize: strip quotes from action_arg
        action_arg = action_arg.strip('"').strip("'")

        # Smart retry: if we searched with same query before, switch to read_file
        if action_name == "search_code" and self._already_tried(action_name, action_arg):
            file_hint = self._extract_filename_from_task()
            if file_hint:
                action_name = "read_file"
                action_arg = file_hint
                thought = f"Search already tried. Reading {file_hint} directly."

        return thought, action_name, action_arg

    def _parse_thought_response(self, response: str) -> tuple[str, str, str]:
        """Extract thought and action from LLM response."""
        thought = ""
        action_name = ""
        action_arg = ""

        # Extract THOUGHT line
        for line in response.splitlines():
            if line.strip().upper().startswith("THOUGHT:"):
                thought = line.split(":", 1)[1].strip()
                break

        # Extract ACTION line
        match = EXTRACT_ACTION_PATTERN.search(response)
        if match:
            action_name = match.group(1).lower().strip()
            action_arg = match.group(2).strip()

        return thought, action_name, action_arg

    # ── ACTION execution ─────────────────────────────────────────────────

    def _execute_action(self, action_name: str, action_arg: str) -> str:
        """Execute a tool and return the observation string."""
        print(f"  [TOOL] Executing: {action_name}({action_arg})")

        if action_name == "search_code":
            result = search_code(action_arg, self.state.project_root)
            # Try to extract a file path from search results
            self._extract_file_from_search(result)
            return result

        elif action_name == "read_file":
            path = self._resolve_path(action_arg)
            content = read_file(path)
            if not content.startswith("[ERROR]"):
                self.state.current_file = path
                self.state.current_file_content = content
            return content

        elif action_name == "write_file":
            # write_file via action is handled in the fix+review pipeline
            # If called directly, we just note it
            return "write_file called — use generate_fix pipeline instead."

        elif action_name == "run_tests":
            exit_code, output = run_tests(self.state.project_root)
            self.state.test_exit_code = exit_code
            self.state.test_output = output
            return output

        else:
            return f"[ERROR] Unknown action: {action_name}"

    # ── FIX generation ───────────────────────────────────────────────────

    def _generate_fix(self) -> str:
        """Ask the LLM to generate a code fix for the current file."""
        error_context = ""
        if self.state.test_output and self.state.test_exit_code != 0:
            error_context = f"TEST ERRORS:\n{self.state.test_output[:1000]}"

        prompt = FIX_PROMPT.format(
            task=self.state.task,
            file_path=self.state.current_file,
            file_content=self.state.current_file_content[:2000],
            error_context=error_context,
        )

        fix = query(prompt)

        # Strip markdown code fences if the LLM wrapped them
        fix = self._strip_code_fences(fix)
        return fix

    # ── SELF-REVIEW loop ─────────────────────────────────────────────────

    def _self_review(self, code_fix: str, max_revisions: int = 2) -> tuple[str, str]:
        """Self-review loop: critique → revise until APPROVED.

        Returns (final_code, review_text).
        """
        for revision in range(max_revisions):
            approved, review_text = review_code(
                self.state.current_file_content,
                code_fix,
                self.state.task,
            )
            print(f"  [REVIEW] #{revision + 1}: {review_text[:100]}")

            if approved:
                return code_fix, review_text

            # REVISE
            print(f"  [REVISE] Revising code (attempt {revision + 1})...")
            code_fix = revise_code(code_fix, review_text, self.state.task)
            code_fix = self._strip_code_fences(code_fix)

        # If we exhausted revisions, use the last version
        return code_fix, f"Auto-approved after {max_revisions} revisions"

    # ── Helpers ───────────────────────────────────────────────────────────

    def _format_history(self) -> str:
        """Format recent history for the prompt."""
        if not self.state.history:
            return "No previous actions."

        lines = ["PREVIOUS ACTIONS:"]
        for h in self.state.history[-3:]:  # last 3 steps
            lines.append(
                f"  Step {h['step']}: {h['action']}({h.get('action_arg', '')}) "
                f"-> {h['test_status']}"
            )
        if self.state.test_output and self.state.test_exit_code != 0:
            lines.append(f"LAST TEST ERROR:\n{self.state.test_output[:500]}")

        return "\n".join(lines)

    def _extract_file_from_search(self, search_output: str) -> None:
        """Try to find a file path in search output and set it as current."""
        for line in search_output.splitlines():
            # ripgrep format: path:line:content
            if ":" in line:
                candidate = line.split(":")[0].strip()
                if candidate.endswith(".py") and os.path.isfile(
                    os.path.join(self.state.project_root, candidate)
                ):
                    full = os.path.join(self.state.project_root, candidate)
                    self.state.current_file = full
                    self.state.current_file_content = read_file(full)
                    return
                # Also try as absolute path
                if os.path.isfile(candidate):
                    self.state.current_file = candidate
                    self.state.current_file_content = read_file(candidate)
                    return

    def _resolve_path(self, path: str) -> str:
        """Resolve a relative path against the project root."""
        if os.path.isabs(path):
            return path
        return os.path.join(self.state.project_root, path)

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove markdown code fences from LLM output."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            # Remove first line (```python or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text

    def _extract_filename_from_task(self) -> str:
        """Extract a .py filename mentioned in the task description."""
        import re as _re
        match = _re.search(r"(\w+\.py)", self.state.task)
        if match:
            return match.group(1)
        return ""

    def _extract_search_keyword(self) -> str:
        """Extract a short, meaningful keyword from the task for searching."""
        task = self.state.task.lower()
        # Common code-related keywords to look for
        for keyword in ["divide", "add", "subtract", "multiply", "error",
                        "bug", "fix", "test", "function", "class", "import"]:
            if keyword in task:
                return keyword
        # Fallback: use first significant word
        words = [w for w in task.split() if len(w) > 3 and w not in
                 ("the", "that", "this", "with", "from", "should", "when")]
        return words[0] if words else "def"

    def _already_tried(self, action_name: str, action_arg: str) -> bool:
        """Check if we already tried this exact action in a previous step."""
        for h in self.state.history:
            if h.get("action") == action_name and h.get("action_arg") == action_arg:
                return True
        return False

