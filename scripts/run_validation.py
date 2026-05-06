"""
DevAgent Empirical Validation Script — Automates testing on real-world repositories.
"""

import os
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
        
    def run_test(self, repo_url: str, task: str, category: str):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        test_dir = self.root / "validation" / "repos" / category / repo_name
        
        console.print(f"\n[bold blue][VALIDATION][/bold blue] Testing: [cyan]{repo_name}[/cyan] in [yellow]{category}[/yellow]")
        
        # 1. Clone
        if not test_dir.exists():
            console.print(f"  [STEP] Cloning {repo_url}...")
            subprocess.run(["git", "clone", repo_url, str(test_dir)], check=True, capture_output=True)
        
        # 2. Run DevAgent
        console.print(f"  [STEP] Running DevAgent task: '{task}'")
        start_time = time.time()
        
        # We run the devagent command directly using the installed CLI
        cmd = [
            "devagent", "run",
            "--task", task,
            "--root", str(test_dir),
            "--max-steps", "10"
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        latency = int(time.time() - start_time)
        
        # 3. Collect Metrics
        # Try to find the metrics.json created by the agent
        metrics_file = test_dir / "logs" / "metrics.json"
        agent_metrics = {}
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                agent_metrics = json.load(f)
        
        result = {
            "repo": repo_name,
            "category": category,
            "task": task,
            "success": process.returncode == 0,
            "latency": latency,
            "confidence": agent_metrics.get("confidence", 0),
            "steps": agent_metrics.get("total_steps", 0),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        self._save_result(result)
        self._update_summary()
        
        status_color = "green" if result["success"] else "red"
        console.print(f"  [DONE] Status: [{status_color}]{'SUCCESS' if result['success'] else 'FAIL'}[/{status_color}] | Latency: {latency}s")

    def _save_result(self, result: dict):
        results = []
        if self.results_file.exists():
            with open(self.results_file, "r") as f:
                results = json.load(f)
        
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
            "avg_latency": f"{sum(r['latency'] for r in results) / total:.1f}s" if total > 0 else "0s",
            "avg_confidence": f"{sum(float(r['confidence'].strip('%')) if isinstance(r['confidence'], str) else r['confidence'] for r in results) / total:.1f}%" if total > 0 else "0%",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        with open(self.summary_file, "w") as f:
            json.dump(summary, f, indent=2)
            
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
    
    # EXAMPLE TARGETS (Small repos)
    targets = [
        ("https://github.com/realpython/flask-todo-api", "Fix any ZeroDivisionError in routes", "flask"),
        ("https://github.com/tiangolo/fastapi", "Fix input validation in basic examples", "fastapi"), # Note: FastAPI is huge, but we can point to subfolders
    ]
    
    # For now, we just initialize the dashboard
    runner.print_dashboard()
