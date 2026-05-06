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

from rich.progress import Progress, SpinnerColumn, TextColumn

def verify_ollama(model_name: str) -> bool:
    """Verify Ollama is running and model is available."""
    import subprocess
    import requests
    
    # 1. Check if server is reachable
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            console.print("[bold red][ERROR][/bold red] Ollama server returned error.")
            return False
    except:
        console.print("[bold red][ERROR][/bold red] Could not connect to Ollama server.")
        console.print("Run: [bold cyan]ollama serve[/bold cyan] in a separate terminal.")
        return False

    # 2. Check if model is pulled
    try:
        tags = response.json().get("models", [])
        model_names = [m["name"] for m in tags]
        # Handle both "name" and "name:latest"
        if model_name not in model_names and f"{model_name}:latest" not in model_names:
            console.print(f"[bold red][ERROR][/bold red] Model [bold cyan]{model_name}[/bold cyan] not found.")
            console.print(f"Run: [bold cyan]ollama pull {model_name}[/bold cyan]")
            return False
    except Exception as e:
        console.print(f"[bold yellow][WARN][/bold yellow] Could not verify model: {e}")
    
    return True

def cmd_run(args):
    """Implementation of 'devagent run' command."""
    if not verify_ollama(args.model):
        return 1

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
    if config.sandbox or config.dry_run:
        if config.dry_run:
            console.print("[bold yellow][DRY RUN][/bold yellow] Agent will work in an isolated sandbox. No changes will be applied.")
        sandbox = SandboxManager(root)
        working_root = sandbox.create()

    # Safety Snapshot
    if not config.dry_run:
        from devagent.utils.safety import SafetyManager
        safety = SafetyManager(root)
        safety.create_snapshot(task_id=config.task[:10].replace(" ", "_"))

    # Run agent
    agent = Agent(
        task=config.task,
        project_root=working_root,
        max_steps=config.max_steps,
        dry_run=config.dry_run
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
    
    # Confidence Score with color coding
    conf_color = "green" if final_state.confidence_score > 0.8 else "yellow" if final_state.confidence_score > 0.5 else "red"
    table.add_row("Confidence", f"[{conf_color}]{final_state.confidence_score * 100:.0f}%[/{conf_color}]")
    
    if final_state.current_file:
        table.add_row("Last File", final_state.current_file)
    table.add_row("Patches", str(len(final_state.patches_applied)))
    
    console.print("\n", table)

    # Show confidence reasons
    if final_state.confidence_reasons:
        console.print("\n[bold]Confidence Breakdown:[/bold]")
        for reason in final_state.confidence_reasons:
            console.print(f"  [green]✓[/green] {reason}")

    # Explain Mode
    if config.explain and final_state.explanations:
        console.print("\n" + "=" * 60)
        console.print("  [bold cyan]TRACEABILITY REPORT (EXPLAIN MODE)[/bold cyan]")
        console.print("=" * 60)
        for exp in final_state.explanations:
            if exp["type"] == "action":
                console.print(f"\n[bold yellow]Selection:[/bold yellow] {exp['action']}")
                console.print(f"  [dim]Why:[/dim] {exp['reason']}")
            elif exp["type"] == "review":
                status_color = "green" if exp["status"] == "APPROVED" else "red"
                console.print(f"\n[bold {status_color}]Review:[/bold {status_color}] {exp['file']} ({exp['status']})")
                console.print(f"  [dim]Logic:[/dim] {exp['reason']}")

    # Sandbox apply / Dry Run
    if sandbox and sandbox.is_active:
        if config.dry_run:
            console.print("\n[bold yellow][DRY RUN][/bold yellow] Completed. No changes applied.")
            # Show diffs anyway to show what would have happened
            for i, patch in enumerate(final_state.patches_applied):
                console.print(f"\n[bold]Proposed Patch #{i+1}[/bold] for [cyan]{patch.get('file', 'unknown')}[/cyan]:")
                console.print(f"[dim]{patch.get('diff', 'No diff available')}[/dim]")
            sandbox.destroy()
            return 0

        if final_state.status == "success":
            if config.interactive:
                console.print("\n[bold yellow][INTERACTIVE][/bold yellow] Reviewing changes...")
                # Show diff for each applied patch
                for i, patch in enumerate(final_state.patches_applied):
                    console.print(f"\n[bold]Patch #{i+1}[/bold] for [cyan]{patch.get('file', 'unknown')}[/cyan]:")
                    console.print(f"[dim]{patch.get('diff', 'No diff available')}[/dim]")
                
                choice = console.input("\nApply these changes to the real project? [y/N]: ").lower()
                if choice != 'y':
                    console.print("[bold red]Changes rejected.[/bold red] Sandbox will be destroyed.")
                    sandbox.destroy()
                    return 1

            console.print("\n[bold yellow][SANDBOX][/bold yellow] Applying changes to real project...")
            result = sandbox.apply_to_project()
            if result["applied"]:
                for f in result["applied"]:
                    console.print(f"  [green]✓[/green] {f}")
        sandbox.destroy()

    # Git operations
    if final_state.status == "success" and config.auto_commit and not config.dry_run:
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

def cmd_rollback(args):
    """Implementation of 'devagent rollback' command."""
    from devagent.utils.safety import SafetyManager
    root = os.path.abspath(getattr(args, "root", "."))
    safety = SafetyManager(root)
    return 0 if safety.rollback() else 1

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
    run_parser.add_argument("--interactive", "-i", action="store_true", help="Review changes before applying")
    run_parser.add_argument("--dry-run", action="store_true", help="Run without applying any changes")
    run_parser.add_argument("--explain", action="store_true", help="Explain why files were chosen and patches applied")
    run_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmark suite")
    bench_parser.add_argument("--model", default=MODELS["primary"], help="Ollama model")
    bench_parser.add_argument("--max-steps", "-m", type=int, default=5, help="Max iterations")

    # Command: doctor
    subparsers.add_parser("doctor", help="Check system health")

    # Command: models
    subparsers.add_parser("models", help="List installed Ollama models")

    # Command: rollback
    roll_parser = subparsers.add_parser("rollback", help="Revert the last agent changes")
    roll_parser.add_argument("--root", "-r", default=".", help="Project root")

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
    elif args.command == "rollback":
        sys.exit(cmd_rollback(args))
    elif args.command == "version":
        console.print(f"DevAgent CLI v{__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
