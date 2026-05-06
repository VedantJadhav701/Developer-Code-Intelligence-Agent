"""
Developer Code Intelligence Agent — CLI Entry Point.

A lightweight local open-source coding agent inspired by Claude Code CLI.
Runs fully offline via Ollama on low-end hardware.

Usage:
    python main.py --task "Fix the divide-by-zero bug" --root ./demo_project
    python main.py --task "Add input validation" --root ./project --sandbox
    python main.py --benchmark
"""

from __future__ import annotations

import argparse
import sys
import os
import time

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from app.agent import Agent
from app.sandbox import SandboxManager
from tools.git_tools import is_git_repo, git_commit, git_push, git_diff
from utils.config import AgentConfig, MODELS
from utils.metrics import RunMetrics


BANNER = r"""
 ____              _                    _
|  _ \  _____   __/ \   __ _  ___ _ __ | |_
| | | |/ _ \ \ / / _ \ / _` |/ _ \ '_ \| __|
| |_| |  __/\ V / ___ \ (_| |  __/ | | | |_
|____/ \___| \_/_/   \_\__, |\___|_| |_|\__|
                       |___/
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DevAgent — A production-grade local coding agent powered by Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python main.py --task "Fix the failing test" --root ./project
  python main.py --task "Add error handling" --root ./backend --model qwen2.5-coder:3b
  python main.py --benchmark
  python main.py --task "Fix bug" --root ./project --sandbox --auto-commit
        """,
    )

    # Core flags
    parser.add_argument("--task", "-t", default="", help="The coding task for the agent.")
    parser.add_argument("--root", "-r", default=".", help="Project root directory (default: cwd).")
    parser.add_argument("--model", default=MODELS["primary"], help=f"Ollama model (default: {MODELS['primary']}).")
    parser.add_argument("--max-steps", "-m", type=int, default=5, help="Maximum ReAct iterations (default: 5).")

    # Feature flags
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark suite instead of a task.")
    parser.add_argument("--sandbox", action="store_true", help="Run in sandbox mode (copy project first).")
    parser.add_argument("--auto-commit", action="store_true", help="Auto-commit on success.")
    parser.add_argument("--auto-push", action="store_true", help="Auto-push after commit (disabled by default).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()
    config = AgentConfig.from_cli(args)

    # ── Benchmark mode ────────────────────────────────────────────────
    if config.benchmark:
        return _run_benchmark(config)

    # ── Task mode ─────────────────────────────────────────────────────
    if not config.task:
        parser.error("--task is required (or use --benchmark)")
        return 1

    root = os.path.abspath(config.project_root)
    if not os.path.isdir(root):
        print(f"[ERROR] Project root not found: {root}")
        return 1

    # Set model
    import app.llm as llm_module
    llm_module.set_model(config.model)

    # Print banner
    print(BANNER)
    print("+" + "=" * 58 + "+")
    print("|" + "  DEVELOPER CODE INTELLIGENCE AGENT".center(58) + "|")
    print("|" + f"  Model: {config.model}".center(58) + "|")
    print("|" + f"  Sandbox: {'ON' if config.sandbox else 'OFF'}".center(58) + "|")
    print("+" + "=" * 58 + "+")

    # ── Sandbox setup ─────────────────────────────────────────────────
    sandbox = None
    working_root = root
    if config.sandbox:
        sandbox = SandboxManager(root)
        working_root = sandbox.create()

    # ── Run agent ─────────────────────────────────────────────────────
    agent = Agent(
        task=config.task,
        project_root=working_root,
        max_steps=config.max_steps,
    )

    start_time = time.time()
    final_state = agent.run()
    elapsed = time.time() - start_time

    # ── Save metrics ──────────────────────────────────────────────────
    metrics_path = agent.metrics.save(os.path.join(root, "logs"))

    # ── Print summary ─────────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("  FINAL SUMMARY")
    print("-" * 60)
    print(f"  Status:     {final_state.status}")
    print(f"  Steps used: {final_state.current_step}/{final_state.max_steps}")
    print(f"  Attempts:   {final_state.attempts}")
    print(f"  Time:       {elapsed:.1f}s")
    if final_state.current_file:
        print(f"  Last file:  {final_state.current_file}")
    if final_state.patches_applied:
        print(f"  Patches:    {len(final_state.patches_applied)}")
    print(f"  Log file:   {os.path.join(root, 'logs', 'run.json')}")
    if metrics_path:
        print(f"  Metrics:    {metrics_path}")
    print("-" * 60)

    # ── Sandbox apply ─────────────────────────────────────────────────
    if sandbox and sandbox.is_active:
        if final_state.status == "success":
            print("\n[SANDBOX] Applying changes to real project...")
            result = sandbox.apply_to_project()
            if result["applied"]:
                print(f"[SANDBOX] Applied {len(result['applied'])} file(s):")
                for f in result["applied"]:
                    print(f"  - {f}")
            else:
                print("[SANDBOX] No changes to apply.")
        sandbox.destroy()

    # ── Git operations ────────────────────────────────────────────────
    if final_state.status == "success" and config.auto_commit:
        _handle_git(root, config)

    return 0 if final_state.status == "success" else 1


def _run_benchmark(config: AgentConfig) -> int:
    """Run the benchmark suite."""
    from tools.benchmark_runner import run_benchmarks

    agent_dir = os.path.dirname(os.path.abspath(__file__))
    benchmarks_dir = os.path.join(agent_dir, "benchmarks")

    print(BANNER)
    print("+" + "=" * 58 + "+")
    print("|" + "  BENCHMARK MODE".center(58) + "|")
    print("|" + f"  Model: {config.model}".center(58) + "|")
    print("+" + "=" * 58 + "+")

    import app.llm as llm_module
    llm_module.set_model(config.model)

    report = run_benchmarks(benchmarks_dir, model=config.model, max_steps=config.max_steps)
    report.print_report()
    report_path = report.save(os.path.join(agent_dir, "logs"))
    print(f"\n[BENCHMARK] Report saved to: {report_path}")

    return 0 if report.pass_rate >= 80 else 1


def _handle_git(root: str, config: AgentConfig) -> None:
    """Handle git commit and optional push."""
    if not is_git_repo(root):
        print("[GIT] Not a git repository. Skipping.")
        return

    print("\n[GIT] Staging and committing changes...")
    commit_msg = f"agent: {config.task[:50]}"
    result = git_commit(root, commit_msg)
    print(f"  {result}")

    if config.auto_push:
        print("[GIT] Pushing to remote...")
        push_result = git_push(root)
        print(f"  {push_result}")
    else:
        print("[GIT] Auto-push disabled. Use --auto-push to enable.")


if __name__ == "__main__":
    sys.exit(main())
