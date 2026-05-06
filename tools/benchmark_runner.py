"""
Benchmark Runner — evaluates the agent against a suite of known bug scenarios.

Each benchmark is a self-contained project with:
  - buggy source code
  - test file
  - expected behavior

Measures: pass rate, retries, execution time, model performance.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str = ""
    task: str = ""
    passed: bool = False
    steps_used: int = 0
    max_steps: int = 5
    execution_time_s: float = 0.0
    model: str = ""
    error: str = ""


@dataclass
class BenchmarkReport:
    """Aggregated benchmark report."""
    results: list[BenchmarkResult] = field(default_factory=list)
    model: str = ""
    total_time_s: float = 0.0

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        return (self.passed / max(self.total, 1)) * 100

    def summary(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": f"{self.pass_rate:.1f}%",
            "total_time_s": round(self.total_time_s, 2),
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "steps": r.steps_used,
                    "time_s": round(r.execution_time_s, 2),
                    "error": r.error[:200] if r.error else "",
                }
                for r in self.results
            ],
        }

    def print_report(self) -> None:
        """Pretty-print the benchmark report."""
        print("\n" + "=" * 60)
        print("  BENCHMARK REPORT")
        print("=" * 60)
        print(f"  Model:     {self.model}")
        print(f"  Total:     {self.total}")
        print(f"  Passed:    {self.passed}")
        print(f"  Failed:    {self.failed}")
        print(f"  Pass Rate: {self.pass_rate:.1f}%")
        print(f"  Time:      {self.total_time_s:.1f}s")
        print("-" * 60)
        for r in self.results:
            icon = "PASS" if r.passed else "FAIL"
            print(f"  [{icon}] {r.name} ({r.steps_used} steps, {r.execution_time_s:.1f}s)")
        print("=" * 60)

    def save(self, output_dir: str) -> str:
        """Save report to JSON."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        out_file = path / "benchmark_report.json"
        out_file.write_text(
            json.dumps(self.summary(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(out_file)


def discover_benchmarks(benchmarks_dir: str) -> list[dict[str, str]]:
    """Discover all benchmark suites in the benchmarks directory."""
    benchmarks = []
    bench_path = Path(benchmarks_dir)

    if not bench_path.is_dir():
        return benchmarks

    for entry in sorted(bench_path.iterdir()):
        if entry.is_dir():
            task_file = entry / "task.txt"
            if task_file.exists():
                task = task_file.read_text(encoding="utf-8").strip()
                benchmarks.append({
                    "name": entry.name,
                    "path": str(entry),
                    "task": task,
                })

    return benchmarks


def run_benchmarks(benchmarks_dir: str, model: str = "qwen2.5-coder:3b",
                   max_steps: int = 5) -> BenchmarkReport:
    """Run all benchmarks and return a report."""
    # Import here to avoid circular imports
    from app.agent import Agent

    report = BenchmarkReport(model=model)
    suites = discover_benchmarks(benchmarks_dir)

    if not suites:
        print("[BENCHMARK] No benchmark suites found.")
        return report

    print(f"\n[BENCHMARK] Found {len(suites)} benchmark suites.")
    start_time = time.time()

    for suite in suites:
        print(f"\n[BENCHMARK] Running: {suite['name']}")
        result = BenchmarkResult(
            name=suite["name"],
            task=suite["task"],
            max_steps=max_steps,
            model=model,
        )

        # Create a temp copy to avoid modifying the benchmark
        tmp_dir = os.path.join(benchmarks_dir, f"_tmp_{suite['name']}")
        try:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            shutil.copytree(suite["path"], tmp_dir)

            t0 = time.time()
            agent = Agent(
                task=suite["task"],
                project_root=tmp_dir,
                max_steps=max_steps,
            )
            final_state = agent.run()
            result.execution_time_s = time.time() - t0
            result.steps_used = final_state.current_step
            result.passed = final_state.status == "success"

        except Exception as exc:
            result.error = str(exc)
            result.passed = False

        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

        report.results.append(result)

    report.total_time_s = time.time() - start_time
    return report
