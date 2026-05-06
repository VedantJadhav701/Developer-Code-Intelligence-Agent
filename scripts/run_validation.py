"""
DevAgent Empirical Validation Script — Automates testing on real-world repositories.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

class ValidationRunner:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).absolute()
        self.reports_dir = self.root / "validation" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.reports_dir / "results.json"
        self.summary_file = self.reports_dir / "benchmark_summary.json"
        self.tasks_dir = self.root / "validation" / "tasks"
        self.repos_root = self.root / "validation" / "repos"
        
    def run_benchmark(self):
        """Main entry point to run all tasks in the library."""
        if not self.tasks_dir.exists():
            console.print("[bold red][ERROR][/bold red] Tasks directory not found.")
            return

        task_files = list(self.tasks_dir.glob("*.json"))
        if not task_files:
            console.print("[bold yellow][WARN][/bold yellow] No task files found in validation/tasks/")
            return

        console.print(f"[bold blue]Starting Benchmark Run: {len(task_files)} task groups found.[/bold blue]")

        for task_file in task_files:
            target_name = task_file.stem
            with open(task_file, "r") as f:
                tasks = json.load(f)

            # Find the repo path (search through categories)
            repo_path = self._find_repo(target_name)
            if not repo_path:
                console.print(f"[bold red]SKIPPING:[/bold red] Repo for {target_name} not found in validation/repos/")
                continue

            for t_data in tasks:
                self.run_task(repo_path, target_name, t_data)

        self.print_dashboard()

    def _find_repo(self, name: str) -> Path:
        """Search for repo by name in the validation/repos subfolders."""
        mapping = {
            "todoism": "flask/todoism",
            "azure-auth": "fastapi/azure-auth",
            "doit": "cli_tools/doit",
            "student-projects": "student_projects/placement-cell"
        }
        
        rel_path = mapping.get(name, name)
        full_path = self.repos_root / rel_path
        if full_path.exists():
            return full_path
        
        for p in self.repos_root.rglob(name):
            if p.is_dir():
                return p
        return None

    def run_task(self, repo_path: Path, target_name: str, task_data: dict):
        task_str = task_data["task"]
        difficulty = task_data.get("difficulty", "medium")
        
        console.print(f"\n[bold blue][TASK][/bold blue] [cyan]{target_name}[/cyan] ({difficulty}): {task_str}")
        
        start_time = time.time()
        cmd = [
            sys.executable, "-m", "devagent.cli", "run",
            "--task", task_str,
            "--root", str(repo_path),
            "--max-steps", "10",
            "--sandbox"
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        latency = int(time.time() - start_time)
        
        metrics_file = repo_path / "logs" / "metrics.json"
        agent_metrics = {}
        if metrics_file.exists():
            try:
                with open(metrics_file, "r") as f:
                    agent_metrics = json.load(f)
            except: pass
        
        failure_type = None
        if process.returncode != 0:
            if "Timeout" in process.stdout or "Timeout" in process.stderr:
                failure_type = "timeout"
            elif "Patch failed" in process.stdout:
                failure_type = "patch_parse_failure"
            elif "Iteration limit" in process.stdout:
                failure_type = "iteration_limit"
            else:
                failure_type = "logic_error"

        result = {
            "repo": target_name,
            "task": task_str,
            "difficulty": difficulty,
            "success": process.returncode == 0,
            "latency_seconds": latency,
            "confidence": agent_metrics.get("confidence", 0),
            "retries": agent_metrics.get("patch_rejections", 0),
            "steps": agent_metrics.get("total_steps", 0),
            "rollback_used": False,
            "corruption": False,
            "failure_type": failure_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        self._save_result(result)
        self._update_summary()
        
        status_color = "green" if result["success"] else "red"
        console.print(f"  [DONE] Status: [{status_color}]{'SUCCESS' if result['success'] else 'FAIL'}[/{status_color}] | Latency: {latency}s")

    def _save_result(self, result: dict):
        results = []
        if self.results_file.exists():
            try:
                with open(self.results_file, "r") as f:
                    results = json.load(f)
            except: pass
        
        results.append(result)
        with open(self.results_file, "w") as f:
            json.dump(results, f, indent=2)

    def _update_summary(self):
        if not self.results_file.exists():
            return
            
        with open(self.results_file, "r") as f:
            results = json.load(f)
            
        total = len(results)
        successes = sum(1 for r in results if r["success"])
        
        summary = {
            "total_runs": total,
            "success_rate": f"{(successes / total) * 100:.1f}%" if total > 0 else "0%",
            "avg_latency": f"{sum(r['latency_seconds'] for r in results) / total:.1f}s" if total > 0 else "0s",
            "avg_confidence": f"{sum(self._parse_confidence(r['confidence']) for r in results) / total:.1f}%" if total > 0 else "0%",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        with open(self.summary_file, "w") as f:
            json.dump(summary, f, indent=2)

    def _parse_confidence(self, val) -> float:
        if isinstance(val, str):
            return float(val.strip('%'))
        return float(val)

    def print_dashboard(self):
        if not self.summary_file.exists():
            console.print("[yellow]No validation results yet.[/yellow]")
            return
            
        with open(self.summary_file, "r") as f:
            summary = json.load(f)
            
        table = Table(title="DevAgent Empirical Validation Dashboard", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")
        
        table.add_row("Total Runs", str(summary["total_runs"]))
        table.add_row("Overall Success Rate", summary["success_rate"])
        table.add_row("Avg Latency", summary["avg_latency"])
        table.add_row("Avg Agent Confidence", summary["avg_confidence"])
        
        console.print(table)

if __name__ == "__main__":
    runner = ValidationRunner(".")
    runner.run_benchmark()
