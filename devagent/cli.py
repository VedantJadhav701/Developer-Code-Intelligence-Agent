"""
DevAgent Professional CLI — The entry point for all agent operations.
"""

from __future__ import annotations

import argparse
import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add package root to sys.path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from devagent.app.agent import Agent
from devagent.app.sandbox import SandboxManager
from devagent.tools.git_tools import is_git_repo, git_commit, git_push
from devagent.utils.config import AgentConfig, MODELS
from devagent import __version__

console = Console()

BANNER = r"""
 ____              _                    _
|  _ \  _____   __/ \   __ _  ___ _ __ | |_
| | | |/ _ \ \ / / _ \ / _` |/ _ \ '_ \| __|
| |_| |  __/\ V / ___ \ (_| |  __/ | | | |_
|____/ \___| \_/_/   \_\__, |\___|_| |_|\__|
                       |___/
"""

def cmd_run(args):
    """Implementation of 'devagent run' command."""
    config = AgentConfig.from_cli(args)
    root = os.path.abspath(config.project_root)
    
    if not os.path.isdir(root):
        console.print(f"[bold red][ERROR][/bold red] Project root not found: {root}")
        return 1

    # Set model
    import devagent.app.llm as llm_module
    llm_module.set_model(config.model)

    console.print(BANNER, style="cyan")
    console.print(Panel.fit(
        f"[bold]DevAgent v{__version__}[/bold]\n"
        f"Model: [green]{config.model}[/green]\n"
        f"Sandbox: [yellow]{'ON' if config.sandbox else 'OFF'}[/yellow]",
        title="Session Info", border_style="blue"
    ))

    # Sandbox setup
    sandbox = None
    working_root = root
    if config.sandbox:
        sandbox = SandboxManager(root)
        working_root = sandbox.create()

    # Run agent
    agent = Agent(
        task=config.task,
        project_root=working_root,
        max_steps=config.max_steps,
    )

    start_time = time.time()
    final_state = agent.run()
    elapsed = time.time() - start_time

    # Save metrics
    metrics_path = agent.metrics.save(os.path.join(root, "logs"))

    # Print summary table
    table = Table(title="Execution Summary", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    
    table.add_row("Status", final_state.status.upper())
    table.add_row("Steps", f"{final_state.current_step}/{final_state.max_steps}")
    table.add_row("Time", f"{elapsed:.1f}s")
    if final_state.current_file:
        table.add_row("Last File", final_state.current_file)
    table.add_row("Patches", str(len(final_state.patches_applied)))
    
    console.print("\n", table)

    # Sandbox apply
    if sandbox and sandbox.is_active:
        if final_state.status == "success":
            console.print("\n[bold yellow][SANDBOX][/bold yellow] Applying changes to real project...")
            result = sandbox.apply_to_project()
            if result["applied"]:
                for f in result["applied"]:
                    console.print(f"  [green]✓[/green] {f}")
        sandbox.destroy()

    # Git operations
    if final_state.status == "success" and config.auto_commit:
        _handle_git(root, config)

    return 0 if final_state.status == "success" else 1

def _handle_git(root: str, config: AgentConfig) -> None:
    if not is_git_repo(root):
        return
    console.print("\n[bold blue][GIT][/bold blue] Committing changes...")
    commit_msg = f"agent: {config.task[:50]}"
    git_commit(root, commit_msg)
    if config.auto_push:
        git_push(root)

def cmd_benchmark(args):
    """Implementation of 'devagent benchmark' command."""
    from devagent.tools.benchmark_runner import run_benchmarks
    
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    benchmarks_dir = os.path.abspath(os.path.join(agent_dir, "..", "benchmarks"))
    
    import devagent.app.llm as llm_module
    llm_module.set_model(args.model)

    console.print(Panel(f"Running benchmarks with [bold cyan]{args.model}[/bold cyan]", title="Benchmark Suite"))
    
    report = run_benchmarks(benchmarks_dir, model=args.model, max_steps=args.max_steps)
    report.print_report()
    
    return 0 if report.pass_rate >= 80 else 1

def cmd_doctor(args):
    """Implementation of 'devagent doctor' command."""
    console.print("[bold cyan]DevAgent System Check[/bold cyan]\n")
    
    checks = []
    
    # Python Check
    checks.append(("[green]OK[/green]" if sys.version_info >= (3, 11) else "[red]FAIL[/red]", f"Python {sys.version_info.major}.{sys.version_info.minor}"))
    
    # Ollama Check
    import subprocess
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        checks.append(("[green]OK[/green]", "Ollama installed"))
    except:
        checks.append(("[red]FAIL[/red]", "Ollama NOT found (run: ollama serve)"))

    # FAISS Check
    try:
        import faiss
        checks.append(("[green]OK[/green]", "FAISS available"))
    except:
        checks.append(("[yellow]WARN[/yellow]", "FAISS not found (keyword search fallback active)"))

    for status, msg in checks:
        console.print(f" {status} {msg}")
    
    return 0

def cmd_models(args):
    """Implementation of 'devagent models' command."""
    import subprocess
    console.print("[bold cyan]Installed Ollama Models[/bold cyan]\n")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        console.print(result.stdout)
        console.print(f"\n[bold green]Recommended:[/bold green] {MODELS['primary']}")
    except:
        console.print("[red][ERROR][/red] Could not list Ollama models.")
    return 0

def main():
    parser = argparse.ArgumentParser(description="DevAgent CLI — Professional local coding agent.")
    parser.add_argument("--version", action="version", version=f"DevAgent v{__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run the agent on a coding task")
    run_parser.add_argument("--task", "-t", required=True, help="Task description")
    run_parser.add_argument("--root", "-r", default=".", help="Project root")
    run_parser.add_argument("--model", default=MODELS["primary"], help="Ollama model")
    run_parser.add_argument("--max-steps", "-m", type=int, default=5, help="Max iterations")
    run_parser.add_argument("--sandbox", action="store_true", help="Run in sandbox")
    run_parser.add_argument("--auto-commit", action="store_true", help="Auto-commit on success")
    run_parser.add_argument("--auto-push", action="store_true", help="Auto-push after commit")
    run_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmark suite")
    bench_parser.add_argument("--model", default=MODELS["primary"], help="Ollama model")
    bench_parser.add_argument("--max-steps", "-m", type=int, default=5, help="Max iterations")

    # Command: doctor
    subparsers.add_parser("doctor", help="Check system health")

    # Command: models
    subparsers.add_parser("models", help="List installed Ollama models")

    # Command: version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "run":
        sys.exit(cmd_run(args))
    elif args.command == "benchmark":
        sys.exit(cmd_benchmark(args))
    elif args.command == "doctor":
        sys.exit(cmd_doctor(args))
    elif args.command == "models":
        sys.exit(cmd_models(args))
    elif args.command == "version":
        console.print(f"DevAgent CLI v{__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
