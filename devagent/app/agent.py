"""
Core ReAct Agent — the main execution engine.

Implements the full production loop:
  PLAN → THOUGHT → ACTION → OBSERVATION → GENERATE FIX →
  SELF-REVIEW → PATCH → TEST → RETRY

Integrates:
  - Planner layer
  - Retrieval layer (semantic search + memory)
  - Tool execution layer
  - Self-review layer
  - Patch engine
  - Sandbox execution
  - Metrics tracking
"""

from __future__ import annotations

import re
import os
import time
from typing import Any
from rich.console import Console
from rich.panel import Panel

console = Console()

from devagent.app.llm import query, query_with_context
from devagent.app.reviewer import review_code, revise_code
from devagent.app.state import AgentState
from devagent.app.planner import generate_plan
from devagent.app.patcher import generate_diff, apply_patch, format_diff_summary
from devagent.app.memory import WorkingMemory, chunk_project, SemanticIndex
from devagent.tools.search import search_code
from devagent.tools.file_ops import read_file, write_file, list_files
from devagent.tools.file_map import get_file_map
from devagent.tools.env_detector import get_environment_info, repair_environment
from devagent.tools.test_runner import run_tests
from devagent.tools.linter import lint_code
from devagent.tools.git_tools import git_diff, git_status
from devagent.tools.semantic_search import semantic_search, build_index, get_relevant_chunks
from devagent.tools.surgical_patcher import apply_surgical_patch
from devagent.utils.logger import AgentLogger
from devagent.utils.metrics import RunMetrics, Timer


# ── Prompt templates (kept SHORT for small models) ───────────────────────────

THOUGHT_PROMPT = """\
You are a coding agent. Your task:
{task}

Project root: {project_root}
Current step: {step}/{max_steps}

{plan_context}

{history_summary}

{project_structure}

{retrieval_context}

Decide the SINGLE next action. Choose ONE:
- list_files: <relative_path>
- get_file_map: <relative_path>
- get_environment_info: <relative_path>
- repair_environment: <package_name>
- search_code: <keyword>
- semantic_search: <query>
- read_file: <relative_path>[:L<start>-<end>]
- write_file: <relative_path>
- surgical_patch: <file> | <SEARCH> | <REPLACE>
- run_tests: <optional_path>
- lint_code: <relative_path>
- git_diff

STRATEGY:
1. START by using 'get_environment_info' to understand the project runtime.
2. If tests fail with ModuleNotFoundError, use 'repair_environment' to fix the environment.
3. USE 'run_tests' to identify logic failures.
4. For large files (>50 lines), use 'get_file_map' FIRST to see the structure.
5. USE 'read_file' with line ranges (e.g. file.py:L10-L50) for targeted reading.
6. USE 'surgical_patch' for logic fixes. Format: file.py | <SEARCH> | <REPLACE>
7. ALWAYS use full relative paths.

Reply in this EXACT format (two lines only):
THOUGHT: <your reasoning>
ACTION: <tool_name>: <argument>
"""

FIX_PROMPT = """\
TASK: {task}

FILE: {file_path}
CURRENT CODE:
{file_content}

{error_context}

{retrieval_context}

Fix the bug. Output ONLY the COMPLETE Python code.
"""

EXTRACT_ACTION_PATTERN = re.compile(
    r"ACTION:\s*(get_file_map|get_environment_info|repair_environment|search_code|semantic_search|read_file|write_file|surgical_patch|run_tests|lint_code|list_files|git_diff)\s*:?\s*(.*)",
    re.IGNORECASE,
)


class Agent:
    """ReAct agent with planner, retrieval, self-review, and sandbox support."""

    def __init__(self, task: str, project_root: str = ".", max_steps: int = 5, dry_run: bool = False):
        self.state = AgentState(
            task=task,
            project_root=os.path.abspath(project_root),
            max_steps=max_steps,
            working_root=os.path.abspath(project_root),
        )
        self.dry_run = dry_run
        self.logger = AgentLogger(log_dir=os.path.join(project_root, "logs"))
        self.metrics = RunMetrics(task=task)
        self.memory = WorkingMemory()
        self._semantic_index: SemanticIndex | None = None

    # ── Public entry point ───────────────────────────────────────────────

    def run(self) -> AgentState:
        """Execute the full agent loop. Returns final state."""
        self.state.status = "running"
        self.metrics.model = self._get_model()
        self.logger.log_event("agent_start", {
            "task": self.state.task,
            "model": self.metrics.model,
        })

        # Phase 0: Initial scan + plan
        self._initial_scan()
        self._build_retrieval_index()
        self._run_planner()

        print("\n" + "=" * 60)
        print("  DEVELOPER CODE INTELLIGENCE AGENT")
        print(f"  Task: {self.state.task}")
        print(f"  Project: {self.state.project_root}")
        print(f"  Max iterations: {self.state.max_steps}")
        print("=" * 60)

        if self.state.plan:
            print(f"\n  [PLAN] {self.state.plan.get('raw_plan', '')[:200]}")

        for step in range(1, self.state.max_steps + 1):
            self.state.current_step = step
            self.state.attempts += 1

            print(f"\n{'-' * 40}")
            print(f"  ITERATION {step}/{self.state.max_steps}")
            print(f"{'-' * 40}")

            with Timer() as t:
                step_result = self._run_iteration(step)

            self.metrics.record_step(
                step=step,
                action=self.state.last_action,
                latency_s=t.elapsed,
                prompt_chars=getattr(query, '_last_prompt_chars', 0),
                response_chars=getattr(query, '_last_response_chars', 0),
                status=step_result,
            )

            if step_result == "success":
                self.state.status = "success"
                self._calculate_confidence()
                self.metrics.finalize()
                self.logger.log_event("agent_complete", {
                    "status": "success", "steps": step,
                    **self.metrics.summary(),
                })
                print("\n[OK]  AGENT COMPLETED SUCCESSFULLY")
                return self.state
        # Exhausted all iterations
        self.state.status = "fail"
        self._calculate_confidence()
        self.metrics.finalize()
        self.logger.log_event("agent_complete", {
            "status": "fail", "steps": self.state.max_steps,
            **self.metrics.summary(),
        })
        print("\n[FAIL]  AGENT FAILED -- max iterations reached")
        return self.state

    def _calculate_confidence(self) -> float:
        """Calculate a trust score (0.0 - 1.0) for the final result."""
        score = 0.0
        reasons = []

        # 1. Test Success (+0.50)
        if self.state.test_exit_code == 0 and "collected 0 items" not in self.state.test_output:
            score += 0.50
            reasons.append("Tests passed successfully")
        elif self.state.test_exit_code == 0:
             reasons.append("No tests found to validate")
        else:
            reasons.append("Tests failed or not fully resolved")

        # 2. Surgical Precision (+0.20)
        # Check if any patch was a surgical_patch (which is more precise)
        surgical_used = any("surgical_patch" in h.get("action", "") for h in self.state.history)
        if surgical_used:
            score += 0.20
            reasons.append("Used precise surgical patching")
        else:
            reasons.append("Used full-file replacement (less precise)")

        # 3. Self-Review Reliability (+0.15)
        # If last review was approved on first try
        if self.state.last_review and "APPROVED" in self.state.last_review.upper():
            score += 0.15
            reasons.append("Fix passed internal self-review")

        # 4. Step Efficiency (+0.15)
        # Fewer steps means higher confidence in the solution's clarity
        if self.state.current_step <= self.state.max_steps // 2:
            score += 0.15
            reasons.append("Solution reached efficiently")

        self.state.confidence_score = min(1.0, score)
        self.state.confidence_reasons = reasons
        return self.state.confidence_score

    # ── Phase 0: Initialization ──────────────────────────────────────────

    def _initial_scan(self) -> None:
        """Identify key files to give the agent immediate context."""
        files = list_files(self.state.project_root, extension=".py")
        if files:
            rel_files = [os.path.relpath(f, self.state.project_root) for f in files]
            self.state.history.append({
                "step": 0, "thought": "Initializing project scan.",
                "action": "system_scan",
                "observation": f"Found {len(rel_files)} Python files: {', '.join(rel_files[:15])}",
                "review": "", "test_result": "", "status": "info",
            })

    def _build_retrieval_index(self) -> None:
        """Build semantic retrieval index for the project."""
        try:
            build_index(self.state.project_root)
        except Exception as exc:
            print(f"[RETRIEVAL] Index build skipped: {exc}")

    def _run_planner(self) -> None:
        """Run the planner to generate an action plan."""
        files = list_files(self.state.project_root, extension=".py")
        rel_files = [os.path.relpath(f, self.state.project_root) for f in files[:30]]
        plan = generate_plan(self.state.task, rel_files)
        self.state.plan = plan

    # ── Single iteration ─────────────────────────────────────────────────

    def _run_iteration(self, step: int) -> str:
        """Run one full ReAct iteration. Returns 'success' or 'continue'."""

        # Retrieve relevant context for this step
        self._retrieve_context()

        # STEP 1 — THOUGHT + ACTION
        thought, action_name, action_arg = self._think(step)
        self.state.last_thought = thought
        self.state.last_action = f"{action_name}: {action_arg}"
        self.state.thoughts.append(thought)
        self.state.actions.append(f"{action_name}: {action_arg}")

        # STEP 2 — EXECUTE ACTION → OBSERVATION
        observation = self._execute_action(action_name, action_arg)
        self.state.last_observation = observation # Store and display result
        obs_text = str(observation) if isinstance(observation, dict) else observation
        self.state.observations.append(obs_text[:2000])
        console.print(Panel(obs_text[:1000], title="Observation", border_style="green"))
        
        self.state.explanations.append({
            "type": "action",
            "action": f"{action_name}: {action_arg}",
            "reason": thought
        })

        # STEP 3 — GENERATE FIX (if we have a file in context)
        code_fix = ""
        review_text = ""
        patch_summary = ""

        if self.state.current_file and action_name in ("read_file", "search_code", "semantic_search", "write_file"):
            code_fix = self._generate_fix()
            self.state.last_code_fix = code_fix

            # STEP 4 — SELF-REVIEW (with Synthetic Grounding)
            if code_fix:
                # Add a "Dry Run" lint check to the review context
                _, lint_output = lint_code(self.state.current_file)
                self.state.last_observation += f"\n[LINT] {lint_output}"

                code_fix, review_text = self._self_review(code_fix)
                self.state.last_review = review_text

                # STEP 5 — APPLY PATCH
                original = self.state.current_file_content or ""
                patch_result = apply_patch(self.state.current_file, original, code_fix)
                patch_summary = format_diff_summary(patch_result)
                self.state.patches_applied.append(patch_result)
                observation += f"\n{patch_summary}"

        # STEP 6 — RUN TESTS
        test_exit, test_output, failing = run_tests(self.state.working_root or self.state.project_root)
        self.state.test_exit_code = test_exit
        self.state.test_output = test_output
        self.state.failing_functions = failing

        # Determine success
        if test_exit == 0 and "collected 0 items" not in test_output:
            status = "success"
        else:
            status = "fail"

        # Log this step
        self.logger.log_step(
            step=step,
            thought=thought,
            action=f"{action_name}: {action_arg}",
            observation=observation,
            review=review_text,
            test_result=test_output,
            status=status,
            latency=getattr(query, '_last_latency', 0),
            model=self._get_model(),
            patch_summary=patch_summary,
        )

        # Store in history
        obs_text = str(observation) if isinstance(observation, dict) else observation
        self.state.history.append({
            "step": step, "thought": thought,
            "action": action_name, "action_arg": action_arg,
            "observation": obs_text[:500],
            "review": review_text, "test_status": status,
        })

        return status

    # ── Retrieval ────────────────────────────────────────────────────────

    def _retrieve_context(self) -> None:
        """Retrieve relevant code chunks for the current task, prioritizing failures."""
        query_text = self.state.task
        if self.state.failing_functions:
            query_text += " " + " ".join(self.state.failing_functions)
        
        chunks = get_relevant_chunks(query_text, top_k=5)
        
        # Prioritize chunks that mention failing functions explicitly
        if self.state.failing_functions:
            prioritized = []
            others = []
            for chunk in chunks:
                if any(func in chunk.content for func in self.state.failing_functions):
                    prioritized.append(chunk)
                else:
                    others.append(chunk)
            chunks = prioritized + others
            
        self.state.retrieved_chunks = chunks[:3]
        for chunk in chunks[:3]:
            self.memory.add_chunk(chunk)

    def _get_retrieval_context(self) -> str:
        """Format retrieved context for prompts."""
        ctx = self.memory.get_context(max_chars=1500)
        if ctx:
            return f"RETRIEVED CONTEXT:\n{ctx}"
        return ""

    # ── THOUGHT phase ────────────────────────────────────────────────────

    def _think(self, step: int) -> tuple[str, str, str]:
        """Ask the LLM to decide the next action."""
        history_summary = self._format_history()
        retrieval_context = self._get_retrieval_context()
        plan_context = ""
        if self.state.plan:
            plan_context = f"CURRENT PLAN:\n{self.state.plan.get('raw_plan', 'No plan available')}"

        # Get project structure summary
        structure = ""
        scan_step = next((h for h in self.state.history if h["action"] == "system_scan"), None)
        if scan_step:
            structure = f"FILE SYSTEM STRUCTURE:\n{scan_step['observation']}"

        prompt = THOUGHT_PROMPT.format(
            task=self.state.task,
            project_root=self.state.project_root,
            step=step,
            max_steps=self.state.max_steps,
            attempts=self.state.attempts,
            history_summary=history_summary,
            retrieval_context=retrieval_context,
            plan_context=plan_context,
            project_structure=structure,
        )

        response = query(prompt)
        thought, action_name, action_arg = self._parse_thought_response(response)

        # Fallback logic
        if not action_name:
            if not self.state.current_file:
                file_hint = self._extract_filename_from_task()
                if file_hint and step > 1:
                    action_name, action_arg = "read_file", file_hint
                    thought = f"Falling back to reading {file_hint} directly."
                else:
                    action_name = "search_code"
                    action_arg = self._extract_search_keyword()
                    thought = "Falling back to keyword search."
            else:
                action_name, action_arg = "run_tests", ""
                thought = "Falling back to run_tests."

        action_arg = action_arg.strip('"').strip("'")

        # Dedup: if same action tried before, try alternate
        if self._already_tried(action_name, action_arg):
            # If we keep trying run_tests/search_code, force read_file if possible
            if action_name in ("run_tests", "search_code", "semantic_search"):
                file_hint = self._extract_filename_from_task() or self._extract_file_from_plan()
                if file_hint:
                    action_name, action_arg = "read_file", file_hint
                    thought = f"Action {action_name} already tried. Forcing read_file on {file_hint}."
                elif self.state.current_file:
                    action_name, action_arg = "read_file", self.state.current_file
                    thought = f"Action {action_name} already tried. Reading current file again."
                else:
                    action_name, action_arg = "list_files", "."
                    thought = f"Action {action_name} already tried. Listing files to find something new."

        return thought, action_name, action_arg

    def _parse_thought_response(self, response: str) -> tuple[str, str, str]:
        """Extract thought and action from LLM response."""
        thought = ""
        for line in response.splitlines():
            if line.strip().upper().startswith("THOUGHT:"):
                thought = line.split(":", 1)[1].strip()
                break

        match = EXTRACT_ACTION_PATTERN.search(response)
        action_name = match.group(1).lower().strip() if match else ""
        action_arg = match.group(2).strip() if match else ""
        return thought, action_name, action_arg

    # ── ACTION execution ─────────────────────────────────────────────────

    def _execute_action(self, action_name: str, action_arg: str) -> str:
        """Execute a tool and return the observation string."""
        print(f"  [TOOL] Executing: {action_name}({action_arg})")
        root = self.state.working_root or self.state.project_root

        if action_name == "search_code":
            result = search_code(action_arg, root)
            self._extract_file_from_search(result)
            return result

        elif action_name == "get_file_map":
            return get_file_map(action_arg, root)

        elif action_name == "get_environment_info":
            return get_environment_info(root)

        elif action_name == "repair_environment":
            return repair_environment(action_arg, root)

        elif action_name == "semantic_search":
            result = semantic_search(action_arg, root)
            # Try to extract file from results
            self._extract_file_from_search(result)
            return result

        elif action_name == "read_file":
            path = self._resolve_path(action_arg)
            content = read_file(path)
            self.state.current_file = path
            self.state.current_file_content = "" if content.startswith("[ERROR]") else content
            return content

        elif action_name == "write_file":
            path = self._resolve_path(action_arg)
            self.state.current_file = path
            if not self.state.current_file_content:
                self.state.current_file_content = ""
            return f"[OK] Targeting {path} for writing."

        elif action_name == "run_tests":
            code, out, failing = run_tests(root, action_arg)
            self.state.test_output = out
            self.state.failing_functions = failing
            
            # Detect stagnation
            if out == self.state.last_test_output and out:
                self.state.stagnant_steps += 1
            else:
                self.state.stagnant_steps = 0
            self.state.last_test_output = out
            
            return out

        elif action_name == "surgical_patch":
            # Expected arg: "file.py | SEARCH_TEXT | REPLACE_TEXT"
            parts = action_arg.split("|")
            if len(parts) < 3:
                return "[ERROR] surgical_patch requires format: file | SEARCH | REPLACE"
            path = self._resolve_path(parts[0].strip())
            search = parts[1].strip()
            replace = parts[2].strip()
            return apply_surgical_patch(path, search, replace)

        elif action_name == "lint_code":
            path = self._resolve_path(action_arg)
            _, output = lint_code(path)
            return output

        elif action_name == "list_files":
            path = self._resolve_path(action_arg)
            files = list_files(path)
            if not files:
                return f"[INFO] No .py files found in {action_arg}"
            rel_files = [os.path.relpath(f, root) for f in files]
            return f"Found {len(rel_files)} files: " + ", ".join(rel_files[:20])

        elif action_name == "git_diff":
            return git_diff(root)

        else:
            return f"[ERROR] Unknown action: {action_name}"

    # ── FIX generation ───────────────────────────────────────────────────

    def _generate_fix(self) -> str:
        """Ask the LLM to generate a code fix for the current file."""
        error_context = ""
        if self.state.test_output and self.state.test_exit_code != 0:
            error_context = f"TEST ERRORS (FIX THESE):\n{self.state.test_output[:2000]}"

        retrieval_context = self._get_retrieval_context()

        prompt = FIX_PROMPT.format(
            task=self.state.task,
            file_path=self.state.current_file,
            file_content=self.state.current_file_content[:2000],
            error_context=error_context,
            retrieval_context=retrieval_context,
        )

        fix = query(prompt)
        return self._strip_code_fences(fix)

    # ── SELF-REVIEW loop ─────────────────────────────────────────────────

    def _self_review(self, code_fix: str, max_revisions: int = 2) -> tuple[str, str]:
        """Self-review loop: critique → revise until APPROVED."""
        for revision in range(max_revisions):
            approved, review_text = review_code(
                self.state.current_file_content, code_fix, self.state.task,
            )
            print(f"  [REVIEW] #{revision + 1}: {review_text[:100]}")

            if approved:
                self.state.explanations.append({
                    "type": "review",
                    "file": self.state.current_file,
                    "reason": review_text,
                    "status": "APPROVED"
                })
                return code_fix, review_text

            self.metrics.patch_rejections += 1
            self.state.explanations.append({
                "type": "review",
                "file": self.state.current_file,
                "reason": review_text,
                "status": "REJECTED"
            })
            print(f"  [REVISE] Revising code (attempt {revision + 1})...")
            code_fix = revise_code(code_fix, review_text, self.state.task)
            code_fix = self._strip_code_fences(code_fix)

        return code_fix, f"Auto-approved after {max_revisions} revisions"

    # ── Helpers ───────────────────────────────────────────────────────────

    def _format_history(self) -> str:
        """Format recent history for the prompt."""
        if not self.state.history:
            return "No previous actions."

        lines = ["PROJECT CONTEXT:"]
        scan_step = next((h for h in self.state.history if h["action"] == "system_scan"), None)
        if scan_step:
            lines.append(f"  {scan_step['observation']}")

        lines.append("\nPREVIOUS ACTIONS:")
        real_steps = [h for h in self.state.history if h["action"] != "system_scan"]
        for h in real_steps[-3:]:
            lines.append(
                f"  Step {h['step']}: {h['action']}({h.get('action_arg', '')}) "
                f"-> {h.get('status', h.get('test_status', 'info'))}"
            )

        if self.state.failing_functions:
            lines.append(f"\nFAILING FUNCTIONS DETECTED: {', '.join(self.state.failing_functions)}")
            lines.append("Look for these functions in the codebase. They are likely where the bug is.")

        if self.state.stagnant_steps >= 1:
            lines.append("\n[CRITICAL PIVOT] YOUR PREVIOUS FIXES ARE NOT WORKING.")
            if self.state.failing_functions:
                lines.append(f"STOP focusing on the original task name. FOCUS EXCLUSIVELY ON THESE FAILURES: {', '.join(self.state.failing_functions)}")
            lines.append("Read the code of the FAILING functions. The bug is there, not where you are currently looking.")

        if self.state.test_output:
            lines.append(f"\nLAST TEST ERROR:\n{self.state.test_output[:1500]}")

        return "\n".join(lines)

    def _extract_file_from_search(self, search_output: str) -> None:
        """Try to find a file path in search output and set it as current."""
        root = self.state.working_root or self.state.project_root
        for line in search_output.splitlines():
            if ":" in line:
                candidate = line.split(":")[0].strip()
                if candidate.endswith(".py"):
                    full = os.path.join(root, candidate) if not os.path.isabs(candidate) else candidate
                    if os.path.isfile(full):
                        self.state.current_file = full
                        self.state.current_file_content = read_file(full)
                        return

    def _resolve_path(self, path: str) -> str:
        """Resolve a relative path against the working root.
        
        Includes 'Path Anchoring' — if the file isn't at root, search for it
        in subdirectories to prevent hallucination errors.
        """
        root = self.state.working_root or self.state.project_root
        if os.path.isabs(path):
            return path
        
        target = os.path.join(root, path)
        if os.path.exists(target):
            return target
            
        # Path Anchoring: Look for the file elsewhere
        filename = os.path.basename(path)
        for r, _, files in os.walk(root):
            if filename in files:
                found_path = os.path.join(r, filename)
                print(f"  [PATH] Auto-anchored '{path}' to '{os.path.relpath(found_path, root)}'")
                return found_path
                
        return target

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Extract Python code from LLM response, stripping markdown and commentary."""
        if not text:
            return ""

        # 1. Look for ```python ... ```
        match = re.search(r"```python\s+(.*?)\s+```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 2. Look for ``` ... ```
        match = re.search(r"```\s+(.*?)\s+```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 3. Aggressive extraction: find first import/def/class and last line of code
        lines = text.splitlines()
        start_idx = 0
        found_start = False
        for i, line in enumerate(lines):
            if re.match(r"^\s*(import|from|def|class|#|@)", line):
                start_idx = i
                found_start = True
                break
        
        if not found_start:
            return text.strip()

        # Strip trailing non-code (explanations)
        end_idx = len(lines)
        for i in range(len(lines) - 1, start_idx, -1):
            line = lines[i].strip()
            # If line ends with typical code markers, it's likely code
            if line and (line.endswith(":") or line.endswith(")") or line.endswith("]") or 
                         line.endswith("}") or line.endswith("'") or line.endswith('"') or 
                         line in {"True", "False", "None"} or re.match(r"^\s*#", line)):
                end_idx = i + 1
                break
            
        return "\n".join(lines[start_idx:end_idx]).strip()

    def _extract_filename_from_task(self) -> str:
        """Extract a .py filename mentioned in the task description."""
        match = re.search(r"(\w+\.py)", self.state.task)
        return match.group(1) if match else ""

    def _extract_search_keyword(self) -> str:
        """Extract a short keyword from the task for searching."""
        task = self.state.task.lower()
        for keyword in ["divide", "add", "subtract", "multiply", "error",
                        "bug", "fix", "test", "function", "class", "import",
                        "validate", "parse", "process", "batch", "register"]:
            if keyword in task:
                return keyword
        words = [w for w in task.split() if len(w) > 3 and w not in
                 ("the", "that", "this", "with", "from", "should", "when")]
        return words[0] if words else "def"

    def _extract_file_from_plan(self) -> str:
        """Extract the first likely file from the plan."""
        if self.state.plan and self.state.plan.get("likely_files"):
            files = self.state.plan.get("likely_files")
            if isinstance(files, list) and files:
                return files[0]
            if isinstance(files, str):
                return files.split(",")[0].strip()
        return ""

    def _already_tried(self, action_name: str, action_arg: str) -> bool:
        """Check if we already tried this exact action in the last 2 steps."""
        # Look back at last 2 steps to avoid immediate loops
        for h in self.state.history[-2:]:
            if h.get("action") == action_name and h.get("action_arg") == action_arg:
                return True
        return False

    def _get_model(self) -> str:
        """Get the current model name."""
        from devagent.app.llm import MODEL
        return MODEL
