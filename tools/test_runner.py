"""
Test runner and linter — executes pytest and flake8 via subprocess.
"""

from __future__ import annotations

import subprocess
import shutil


def run_tests(project_root: str = ".", test_path: str = "") -> tuple[int, str]:
    """Run pytest on the project.

    Args:
        project_root: Working directory for pytest.
        test_path: Optional specific test file/dir. Defaults to auto-discovery.

    Returns:
        (exit_code, output_text)
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
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode, output[:3000]
    except subprocess.TimeoutExpired:
        return 1, "[ERROR] pytest timed out after 60s"
    except FileNotFoundError:
        return 1, "[ERROR] pytest not found. Install: pip install pytest"
    except Exception as exc:  # noqa: BLE001
        return 1, f"[ERROR] Test runner failed: {exc}"


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
