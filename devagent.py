"""
DevAgent Global CLI Wrapper.

Allows running DevAgent from any directory on the system:
    devagent --task "Fix the bug" --root /path/to/project

This script finds the main.py entry point relative to its own location
and forwards all arguments.
"""

import os
import sys
import subprocess


def main():
    # The directory where THIS script is located
    agent_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the main.py entry point
    main_py = os.path.join(agent_dir, "main.py")

    # Use the current Python executable (conda/venv aware)
    python_exe = sys.executable

    # Run the command, forwarding all arguments
    cmd = [python_exe, main_py] + sys.argv[1:]

    try:
        # Set PYTHONPATH so 'app', 'tools', etc. can be found
        env = os.environ.copy()
        env["PYTHONPATH"] = agent_dir + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[DevAgent] Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"[DevAgent] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
