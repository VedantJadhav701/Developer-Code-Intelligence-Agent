"""
Test runner and linter — executes pytest and flake8 via subprocess.
"""

from __future__ import annotations

import subprocess
import shutil
import re

def extract_failing_functions(output: str) -> list[str]:
    """Extract names of failing tests or functions from pytest output."""
    failures = []
    # Pattern for "FAILED path/to/test.py::test_function"
    pattern = re.compile(r"FAILED\s+[\w\/\.\\-]+\.py::(\w+)")
    for match in pattern.finditer(output):
        failures.append(match.group(1))
    
    # Pattern for "____ test_function ____"
    pattern2 = re.compile(r"____\s+(\w+)\s+____")
    for match in pattern2.finditer(output):
        failures.append(match.group(1))
        
    return list(set(failures))


def run_tests(project_root: str = ".", test_path: str = "") -> tuple[int, str]:
    """Run pytest on the project.

    Args:
        project_root: Working directory for pytest.
        test_path: Optional specific test file/dir. Defaults to auto-discovery.

    Returns:
        (exit_code, output_text, failing_functions)
        exit_code 0 = all tests passed.
    """
    cmd = ["python", "-m", "pytest", "-v", "--tb=short"]
    if test_path:
        cmd.append(test_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_root,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = (stdout + "\n" + stderr).strip()

        failing_funcs = extract_failing_functions(output)

        if len(output) > 2000:
            # Try to extract the interesting parts: failures and short summary
            parts = []
            if "FAILURES" in output:
                # Extract from "FAILURES" to the end
                idx = output.find("FAILURES")
                parts.append("... [OMITTED PASSING TESTS] ...")
                parts.append(output[idx:idx + 2500])
            elif "short test summary info" in output:
                idx = output.find("short test summary info")
                parts.append("... [OMITTED] ...")
                parts.append(output[idx:idx + 1000])
            else:
                parts.append(output[:1000])
                parts.append("... [TRUNCATED] ...")
                parts.append(output[-1000:])
            output = "\n".join(parts)

        return result.returncode, output, failing_funcs
    except subprocess.TimeoutExpired:
        return 1, "[ERROR] pytest timed out after 60s", []
    except FileNotFoundError:
        return 1, "[ERROR] pytest not found. Install: pip install pytest", []
    except Exception as exc:  # noqa: BLE001
        return 1, f"[ERROR] Test runner failed: {exc}", []


def lint_code(file_path: str) -> tuple[int, str]:
    """Run flake8 on a single file.

    Returns:
        (exit_code, output_text)
    """
    flake8_bin = shutil.which("flake8")
    if not flake8_bin:
        return 0, "[SKIP] flake8 not installed — skipping lint"

    try:
        result = subprocess.run(
            [flake8_bin, "--max-line-length=120", file_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip()
        if not output:
            return 0, "No lint issues found."
        return result.returncode, output[:2000]
    except Exception as exc:  # noqa: BLE001
        return 0, f"[WARN] Lint failed: {exc}"
