"""
Developer Code Intelligence Agent — CLI Entry Point.

Usage:
    python main.py --task "Fix the divide-by-zero bug in calculator.py"
    python main.py --task "Add input validation to user_service.py" --root ./my_project
    python main.py --task "Make all tests pass" --max-steps 5
"""

from __future__ import annotations

import argparse
import sys
import os

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from app.agent import Agent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Developer Code Intelligence Agent — autonomous coding agent powered by Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python main.py --task "Fix the failing test in test_math.py"
  python main.py --task "Add error handling to api.py" --root ./backend
  python main.py --task "Refactor utils.py to reduce duplication" --max-steps 5
        """,
    )
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="The coding task for the agent to complete.",
    )
    parser.add_argument(
        "--root", "-r",
        default=".",
        help="Project root directory (default: current directory).",
    )
    parser.add_argument(
        "--max-steps", "-m",
        type=int,
        default=3,
        help="Maximum ReAct iterations (default: 3).",
    )
    parser.add_argument(
        "--model",
        default="qwen2.5:3b",
        help="Ollama model to use (default: qwen2.5:3b).",
    )

    args = parser.parse_args()

    # Validate project root
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"[ERROR] Project root not found: {root}")
        return 1

    # Override model if specified
    if args.model != "qwen2.5:3b":
        import app.llm as llm_module
        llm_module.MODEL = args.model

    print("\n" + "+" + "=" * 58 + "+")
    print("|" + "  DEVELOPER CODE INTELLIGENCE AGENT".center(58) + "|")
    print("|" + f"  Model: {args.model}".center(58) + "|")
    print("+" + "=" * 58 + "+")

    # Run the agent
    agent = Agent(
        task=args.task,
        project_root=root,
        max_steps=args.max_steps,
    )

    final_state = agent.run()

    # Print summary
    print("\n" + "-" * 60)
    print("  FINAL SUMMARY")
    print("-" * 60)
    print(f"  Status:     {final_state.status}")
    print(f"  Steps used: {final_state.current_step}/{final_state.max_steps}")
    print(f"  Attempts:   {final_state.attempts}")
    if final_state.current_file:
        print(f"  Last file:  {final_state.current_file}")
    print(f"  Log file:   {os.path.join(root, 'logs', 'run.json')}")
    print("-" * 60)

    return 0 if final_state.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
